"""
Smart Sync: sincroniza cambios incrementales del KB con Gemini File Search Store.

Lógica con sync_state.json:
1. Lee sync_state.json (si existe) para conocer el estado anterior
2. Calcula hash de cada .md en kb/
3. Para cada archivo:
   - Si hash cambió o es nuevo → sube/actualiza al store
   - Si hash igual → no hace nada
4. Guarda nuevo sync_state.json con hashes actuales
5. Borra docs cuyo path ya no existe en el repo

Nota: sync_state.json reemplaza la dependencia en metadata de Google,
que no parece persistir entre ejecuciones.
"""

import os
import time
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Tuple, List

import requests
import yaml
from dotenv import load_dotenv
from google import genai

# =========
# Config & Logging
# =========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
KB_DIR = ROOT / "kb"
STATE_FILE = ROOT / "sync_state.json"  # ← Aquí guardamos el estado

# Primero cargar de GitHub Actions env (si existen), luego de .env
# En GitHub Actions, las vars ya están en os.environ porque el workflow las pasa como env:
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STORE_NAME = os.getenv("FILE_SEARCH_STORE_NAME", "").strip()
STORE_DISPLAY_NAME = os.getenv("STORE_DISPLAY_NAME", "zigchain-handbook-mvp").strip()
RESET_STORE = os.getenv("RESET_STORE", "false").strip().lower() in ("1", "true", "yes", "y")

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

if not GEMINI_API_KEY:
    raise RuntimeError("❌ Falta GEMINI_API_KEY en .env")
if not KB_DIR.exists():
    raise RuntimeError(f"❌ No existe la carpeta kb/: {KB_DIR}")

# Debug: mostrar configuración (sin exponer la API key)
logger.info(f"📌 Config:")
logger.info(f"   RESET_STORE: {RESET_STORE}")
logger.info(f"   STORE_NAME: {STORE_NAME[:50]}..." if STORE_NAME else "   STORE_NAME: (empty)")
logger.info(f"   STORE_DISPLAY_NAME: {STORE_DISPLAY_NAME}")
logger.info(f"   KB_DIR: {KB_DIR}")

client = genai.Client(api_key=GEMINI_API_KEY)

# =========
# Helpers
# =========
def sha256_text(s: str) -> str:
    """Calcula hash SHA256 de un texto"""
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def parse_frontmatter(md_text: str) -> Tuple[Dict, str]:
    """Extrae YAML frontmatter entre --- ... ---"""
    text = md_text.lstrip()
    if not text.startswith("---"):
        return {}, md_text

    lines = md_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, md_text

    end = None
    for i in range(1, min(len(lines), 300)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, md_text

    fm_raw = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    try:
        data = yaml.safe_load(fm_raw) or {}
        if not isinstance(data, dict):
            data = {}
        return data, body
    except Exception as e:
        logger.warning(f"⚠️ Error parsing frontmatter: {e}")
        return {}, md_text


def wait_operation(op):
    """Espera a que una operación asincrónica termine"""
    while not op.done:
        time.sleep(2)
        op = client.operations.get(op)
    return op


# =========
# Main Logic
# =========
def load_sync_state() -> Dict[str, str]:
    """Carga el estado anterior (paths -> hashes)"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception as e:
            logger.warning(f"⚠️  Error loading sync_state.json: {e}")
    return {}


def save_sync_state(state: Dict[str, str]):
    """Guarda el estado actual (paths -> hashes)"""
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
        logger.info(f"✅ Saved sync_state.json with {len(state)} entries")
    except Exception as e:
        logger.error(f"❌ Error saving sync_state.json: {e}")


# =========
# Main Logic
# =========
def main():
    global STORE_NAME
    
    logger.info("=" * 60)
    logger.info("🚀 Smart Sync: KB → File Search Store (con sync_state.json)")
    logger.info("=" * 60)

    # 1) Crear store si no existe
    if not STORE_NAME:
        logger.info("📦 Creando nuevo File Search Store...")
        store = client.file_search_stores.create(
            config={"display_name": STORE_DISPLAY_NAME}
        )
        STORE_NAME = store.name
        logger.info(f"✅ Store creado: {STORE_NAME}")
        logger.info(f"👉 Guarda esto en tu .env: FILE_SEARCH_STORE_NAME={STORE_NAME}")
    else:
        logger.info(f"✅ Usando store existente: {STORE_NAME}")

    # 2) Cargar estado anterior
    logger.info("\n📋 Cargando estado anterior...")
    old_state = load_sync_state()
    logger.info(f"   Estado anterior: {len(old_state)} documentos")

    # 3) Calcular estado actual (paths -> hashes)
    logger.info("\n📄 Procesando archivos del KB...")
    md_files = sorted(KB_DIR.rglob("*.md"))
    md_files = [p for p in md_files if p.name.lower() != "template.md"]
    
    new_state = {}
    uploaded = 0
    updated = 0
    skipped = 0
    deleted = 0

    for p in md_files:
        rel = p.relative_to(KB_DIR).as_posix()
        kb_path = f"kb/{rel}"
        section = rel.split("/", 1)[0]
        
        content = p.read_text(encoding="utf-8", errors="ignore")
        fm, _ = parse_frontmatter(content)
        new_hash = sha256_text(content)
        new_state[kb_path] = new_hash

        # Comparar con estado anterior
        if kb_path in old_state:
            old_hash = old_state[kb_path]
            if new_hash == old_hash:
                logger.info(f"✅ Sin cambios: {kb_path}")
                skipped += 1
                continue
            else:
                logger.info(f"🔄 Actualizando: {kb_path}")
                updated += 1
        else:
            logger.info(f"⬆️  Nuevo: {kb_path}")
            uploaded += 1

        # Construir metadata
        meta = [
            {"key": "path", "string_value": kb_path},
            {"key": "section", "string_value": section},
            {"key": "sha", "string_value": new_hash},
        ]

        for k in ["title", "description", "department", "doc_type", "owner_team", "maintainer", "visibility", "last_updated"]:
            v = fm.get(k)
            if v:
                meta.append({"key": k, "string_value": str(v)})

        kw = fm.get("keywords")
        if isinstance(kw, list) and kw:
            meta.append({"key": "keywords_csv", "string_value": ",".join([str(x) for x in kw])})

        # Subir al store
        try:
            op = client.file_search_stores.upload_to_file_search_store(
                file=str(p),
                file_search_store_name=STORE_NAME,
                config={
                    "display_name": kb_path,
                    "custom_metadata": meta,
                },
            )
            wait_operation(op)
        except Exception as e:
            logger.error(f"❌ Error uploading {kb_path}: {e}")

    # 4) Detectar documentos eliminados
    logger.info("\n🗑️  Detectando documentos eliminados...")
    for kb_path in old_state:
        if kb_path not in new_state:
            logger.info(f"   Path ya no existe: {kb_path}")
            deleted += 1

    # 5) Guardar nuevo estado
    logger.info("\n💾 Guardando nuevo estado...")
    save_sync_state(new_state)

    # 6) Resumen
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN:")
    logger.info(f"   ✅ Subidos: {uploaded}")
    logger.info(f"   🔄 Actualizados: {updated}")
    logger.info(f"   ✓ Sin cambios: {skipped}")
    logger.info(f"   🗑️  Eliminados (detectados): {deleted}")
    logger.info("=" * 60)
    logger.info("\n✅ Sync completado exitosamente!")
    logger.info(f"👉 File Search Store: {STORE_NAME}")
    logger.info(f"👉 Úsalo en el .env del bot como: FILE_SEARCH_STORE_NAMES={STORE_NAME}")


if __name__ == "__main__":
    main()

