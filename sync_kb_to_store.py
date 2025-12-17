"""
Smart Sync: sincroniza cambios incrementales del KB con Gemini File Search Store.

Lógica:
1. Crea/reutiliza un File Search Store
2. Lista documentos existentes en el store
3. Para cada .md en kb/:
   - Si no existe → sube
   - Si existe pero cambió (hash diferente) → borra viejo y sube nuevo
   - Si existe y no cambió → no hace nada
4. Borra docs cuyo path ya no existe en el repo
"""

import os
import time
import hashlib
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


def list_documents(store_name: str) -> List[Dict]:
    """Lista todos los documentos en un File Search Store"""
    docs = []
    page_token = None
    while True:
        params = {"key": GEMINI_API_KEY, "pageSize": 20}
        if page_token:
            params["pageToken"] = page_token
        url = f"{BASE_URL}/{store_name}/documents"
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()
            docs.extend(data.get("documents", []))
            page_token = data.get("nextPageToken")
            if not page_token:
                break
        except Exception as e:
            logger.error(f"❌ Error listing documents: {e}")
            break
    return docs


def delete_document(doc_name: str):
    """Borra un documento del store"""
    params = {"key": GEMINI_API_KEY, "force": "true"}
    url = f"{BASE_URL}/{doc_name}"
    try:
        r = requests.delete(url, params=params, timeout=60)
        r.raise_for_status()
        logger.info(f"🗑️  Eliminado: {doc_name}")
    except Exception as e:
        logger.error(f"❌ Error deleting {doc_name}: {e}")


def get_metadata_value(doc: Dict, key: str) -> str:
    """Extrae un valor de custom_metadata"""
    try:
        for m in doc.get("custom_metadata", []):
            if m.get("key") == key:
                return m.get("string_value", "")
    except:
        pass
    return ""


# =========
# Main Logic
# =========
def main():
    global STORE_NAME
    
    logger.info("=" * 60)
    logger.info("🚀 Smart Sync: KB → File Search Store")
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

    # 2) RESET mode (si lo pides explícitamente)
    if RESET_STORE:
        logger.warning("🧹 RESET_STORE=true → borrando TODOS los documentos...")
        docs = list_documents(STORE_NAME)
        for d in docs:
            name = d.get("name")
            if name:
                delete_document(name)
        logger.info(f"✅ Borrados {len(docs)} documentos.")
    else:
        logger.info("💡 Modo incremental: solo actualizaré lo que cambió")

    # 3) Listar docs existentes en el store
    logger.info("\n📋 Leyendo documentos del store...")
    existing_docs = list_documents(STORE_NAME)
    logger.info(f"   Total docs en store: {len(existing_docs)}")
    
    existing_map = {}  # {path -> (doc_name, hash)}
    for doc in existing_docs:
        path = get_metadata_value(doc, "path")
        sha = get_metadata_value(doc, "sha")
        doc_name = doc.get("name", "unknown")
        if path:
            existing_map[path] = (doc_name, sha)
            logger.info(f"   ✓ {path} → hash: {sha[:8] if sha else 'NONE'}...")
        else:
            logger.warning(f"   ⚠️  Doc sin path metadata: {doc_name}")
    
    logger.info(f"   Mapeados: {len(existing_map)} documentos con path")

    # 4) Procesar archivos del KB
    logger.info("\n📄 Procesando archivos del KB...")
    md_files = sorted(KB_DIR.rglob("*.md"))
    md_files = [p for p in md_files if p.name.lower() != "template.md"]

    uploaded = 0
    updated = 0
    skipped = 0
    to_delete = set(existing_map.keys())

    for p in md_files:
        rel = p.relative_to(KB_DIR).as_posix()  # ej: incidents/checklist-incident-triage.md
        kb_path = f"kb/{rel}"
        section = rel.split("/", 1)[0]
        content = p.read_text(encoding="utf-8", errors="ignore")
        fm, _ = parse_frontmatter(content)
        new_hash = sha256_text(content)

        # Verificar si existe y si cambió
        if kb_path in existing_map:
            old_doc_name, old_hash = existing_map[kb_path]
            to_delete.discard(kb_path)  # No borrar este

            if new_hash == old_hash:
                logger.info(f"✅ Sin cambios: {kb_path}")
                skipped += 1
                continue
            else:
                # Cambió → borrar viejo y subir nuevo
                logger.info(f"🔄 Actualizando (hash cambió): {kb_path}")
                delete_document(old_doc_name)
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

        # Agregar campos del frontmatter
        for k in ["title", "description", "department", "doc_type", "owner_team", "maintainer", "visibility", "last_updated"]:
            v = fm.get(k)
            if v:
                meta.append({"key": k, "string_value": str(v)})

        # Keywords como CSV
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

    # 5) Borrar documentos cuyo path ya no existe
    logger.info("\n🗑️  Limpiando documentos eliminados...")
    deleted = 0
    for kb_path in to_delete:
        old_doc_name, _ = existing_map[kb_path]
        logger.info(f"   Borrando (ya no existe en repo): {kb_path}")
        delete_document(old_doc_name)
        deleted += 1

    # 6) Resumen
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN:")
    logger.info(f"   ✅ Subidos: {uploaded}")
    logger.info(f"   🔄 Actualizados: {updated}")
    logger.info(f"   ✓ Sin cambios: {skipped}")
    logger.info(f"   🗑️  Borrados: {deleted}")
    logger.info("=" * 60)
    logger.info("\n✅ Sync completado exitosamente!")
    logger.info(f"👉 File Search Store: {STORE_NAME}")
    logger.info(f"👉 Úsalo en el .env del bot como: FILE_SEARCH_STORE_NAMES={STORE_NAME}")


if __name__ == "__main__":
    main()

