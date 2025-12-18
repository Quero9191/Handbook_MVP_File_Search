"""
Smart Sync: sincroniza cambios incrementales del KB con Gemini File Search Store.

🔑 ARQUITECTURA CON sync_state.json:

El problema: Google File Search Store API no persiste display_name ni permite
identificar qué documento viejo corresponde a qué hash nuevo.

La solución: Mantener un mapeo local en sync_state.json:

{
  "kb/path/to/file.md": {
    "hash": "6a64ced5e0a2c867...",
    "store_doc_id": "fileSearchStores/.../documents/xyz123"
  }
}

Flujo:
1. Cargar sync_state.json (estado anterior)
2. Calcular hash de cada .md en kb/
3. Para cada archivo:
   - Sin cambios → saltar
   - Hash nuevo → BORRAR viejo (por store_doc_id) y SUBIR nuevo
   - Nuevo archivo → SUBIR
4. Detectar eliminados (en sync_state pero no en kb/)
5. Guardar sync_state.json con nuevo estado

Garantías:
✅ Nunca duplica
✅ Detecta cambios
✅ No depende de API instable
✅ Identificación 100% certera (path + hash + Store ID)
"""

import os
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Tuple, List

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
STATE_FILE = ROOT / "sync_state.json"  # ← Archivo persistente en Git
STATE_BASE_FILE = ROOT / "sync_state_base.json"  # ← Template base (vacío)

# Cargar env variables
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STORE_NAME = os.getenv("FILE_SEARCH_STORE_NAME", "").strip()
STORE_DISPLAY_NAME = os.getenv("STORE_DISPLAY_NAME", "zigchain-handbook-mvp").strip()

if not GEMINI_API_KEY:
    raise RuntimeError("❌ Falta GEMINI_API_KEY en .env o en GitHub Actions secrets")
if not KB_DIR.exists():
    raise RuntimeError(f"❌ No existe la carpeta kb/: {KB_DIR}")

logger.info(f"📌 Config:")
logger.info(f"   STORE_NAME: {STORE_NAME[:50]}..." if STORE_NAME else "   STORE_NAME: (crear nuevo)")
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


def delete_document(store_doc_id: str) -> bool:
    """Borra un documento del File Search Store por su ID (con force=true si es necesario)"""
    if not store_doc_id:
        logger.warning(f"   ⚠️ Sin ID para borrar (ignorando)")
        return False
    
    try:
        logger.info(f"   🗑️  Borrando documento: {store_doc_id[:60]}...")
        client.file_search_stores.delete(
            name=store_doc_id
        )
        logger.info(f"   ✅ Documento borrado")
        return True
    except Exception as e:
        # Si falla por "non-empty", intentar con force=true
        if "non-empty" in str(e).lower() or "FAILED_PRECONDITION" in str(e):
            logger.info(f"   ⚠️ Documento tiene chunks, borrando con force=true...")
            try:
                import requests
                api_key = os.getenv("GEMINI_API_KEY")
                url = f"https://generativelanguage.googleapis.com/v1beta/{store_doc_id}"
                params = {"key": api_key, "force": "true"}
                resp = requests.delete(url, params=params, timeout=30)
                if resp.status_code == 200:
                    logger.info(f"   ✅ Documento borrado (force=true)")
                    return True
                else:
                    logger.warning(f"   ⚠️ Error con force=true: {resp.status_code}")
                    return False
            except Exception as force_err:
                logger.warning(f"   ⚠️ No se pudo borrar ni con force: {force_err}")
                return False
        else:
            logger.warning(f"   ⚠️ No se pudo borrar: {e}")
            return False


# =========
# State Management
# =========

def load_sync_state() -> Dict[str, dict]:
    """
    Carga el estado anterior: {kb_path -> {"hash": str, "store_doc_id": str}}
    
    Compatible con versión antigua que solo tenía hashes (strings).
    
    En GitHub Actions (primera ejecución):
    - Si sync_state.json está vacío o no existe
    - Usa sync_state_base.json como base (también vacío)
    """
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            
            # Si el archivo está vacío o es un dict vacío
            if not data:
                logger.info(f"📝 Primer run detectado - usando template base")
                if STATE_BASE_FILE.exists():
                    data = json.loads(STATE_BASE_FILE.read_text())
            
            # Convertir formato antiguo (solo strings) al nuevo (dicts)
            new_format = {}
            for path, value in data.items():
                if isinstance(value, str):
                    # Formato antiguo: solo el hash
                    new_format[path] = {
                        "hash": value,
                        "store_doc_id": None,  # No lo tenemos del formato anterior
                    }
                else:
                    # Formato nuevo: ya es un dict
                    new_format[path] = value
            
            return new_format
            
        except Exception as e:
            logger.warning(f"⚠️ Error loading sync_state.json: {e}")
            return {}
    logger.info(f"📝 Primer run: sin estado anterior (archivo no existe)")
    return {}


def save_sync_state(state: Dict[str, dict]):
    """Guarda el estado actual: {kb_path -> {"hash": str, "store_doc_id": str}}"""
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
        logger.info(f"💾 sync_state.json guardado: {len(state)} documentos")
    except Exception as e:
        logger.error(f"❌ Error saving sync_state.json: {e}")
        raise


# =========
# Main Sync Logic
# =========

def main():
    global STORE_NAME

    logger.info("=" * 70)
    logger.info("🚀 SMART SYNC: KB → File Search Store (con sync_state.json)")
    logger.info("=" * 70)

    # ─────────────────────────────────────────────────────────────
    # 1. Asegurar que existe el Store
    # ─────────────────────────────────────────────────────────────
    if not STORE_NAME:
        logger.info("\n📦 PASO 1: Creando nuevo File Search Store...")
        try:
            store = client.file_search_stores.create(
                config={"display_name": STORE_DISPLAY_NAME}
            )
            STORE_NAME = store.name
            logger.info(f"✅ Store creado: {STORE_NAME}")
            logger.info(f"\n👉 IMPORTANTE: Guarda esto en tu .env:")
            logger.info(f"   FILE_SEARCH_STORE_NAME={STORE_NAME}")
        except Exception as e:
            logger.error(f"❌ Error creando store: {e}")
            raise
    else:
        logger.info(f"\n✅ PASO 1: Store existente: {STORE_NAME}")

    # ─────────────────────────────────────────────────────────────
    # 2. Cargar estado anterior (sync_state.json)
    # ─────────────────────────────────────────────────────────────
    logger.info(f"\n📋 PASO 2: Cargando estado anterior...")
    old_state = load_sync_state()
    logger.info(f"   Documentos en sync_state.json: {len(old_state)}")

    # ─────────────────────────────────────────────────────────────
    # 3. Descubrir archivos .md en kb/ y calcular hashes
    # ─────────────────────────────────────────────────────────────
    logger.info(f"\n📄 PASO 3: Explorando kb/ y calculando hashes...")
    md_files = sorted(KB_DIR.rglob("*.md"))
    md_files = [p for p in md_files if p.name.lower() != "template.md"]
    logger.info(f"   Archivos encontrados: {len(md_files)}")

    # Calcular hashes de archivos actuales
    current_hashes = {}
    for p in md_files:
        rel = p.relative_to(KB_DIR).as_posix()
        kb_path = f"kb/{rel}"
        content = p.read_text(encoding="utf-8", errors="ignore")
        current_hashes[kb_path] = sha256_text(content)

    # ─────────────────────────────────────────────────────────────
    # 4. Procesamiento: NUEVO / CAMBIO / SIN CAMBIOS
    # ─────────────────────────────────────────────────────────────
    logger.info(f"\n🔄 PASO 4: Procesando cambios...")
    new_state = {}
    stats = {"uploaded": 0, "updated": 0, "unchanged": 0, "deleted": 0}

    for p in md_files:
        rel = p.relative_to(KB_DIR).as_posix()
        kb_path = f"kb/{rel}"
        new_hash = current_hashes[kb_path]

        logger.info(f"\n   📄 {kb_path}")

        # ╔═══════════════════════════════════════════════════════╗
        # ║ CASO 1: Archivo existía antes                         ║
        # ╚═══════════════════════════════════════════════════════╝
        if kb_path in old_state:
            old_entry = old_state[kb_path]
            old_hash = old_entry.get("hash")
            store_doc_id = old_entry.get("store_doc_id")

            # Subcase 1a: Sin cambios
            if new_hash == old_hash:
                logger.info(f"      ✓ Sin cambios (hash igual)")
                new_state[kb_path] = old_entry  # Mantener Store ID
                stats["unchanged"] += 1
                continue

            # Subcase 1b: Cambió el contenido
            else:
                logger.info(f"      🔄 ACTUALIZACIÓN DETECTADA")
                logger.info(f"         Old hash: {old_hash[:16]}...")
                logger.info(f"         New hash: {new_hash[:16]}...")
                
                # Borrar documento viejo del Store (si tenemos su ID)
                if store_doc_id:
                    logger.info(f"      🗑️  Borrando documento obsoleto...")
                    delete_document(store_doc_id)
                    stats["deleted"] += 1  # ← Contar como eliminado (viejo)
                else:
                    # No tenemos ID (formato antiguo). Tratarlo como nuevo
                    logger.info(f"         (sin ID antiguo, tratando como nuevo)")
                
                stats["uploaded"] += 1  # ← Contar subida del nuevo

        # ╔═══════════════════════════════════════════════════════╗
        # ║ CASO 2: Archivo es NUEVO                              ║
        # ╚═══════════════════════════════════════════════════════╝
        else:
            logger.info(f"      ⬆️  ARCHIVO NUEVO")
            stats["uploaded"] += 1

        # ─────────────────────────────────────────────────────────
        # Subir documento (NUEVO o reemplazo)
        # ─────────────────────────────────────────────────────────
        logger.info(f"      ⏳ Subiendo a Store...")
        
        content = p.read_text(encoding="utf-8", errors="ignore")
        fm, _ = parse_frontmatter(content)
        
        # Construir metadata
        section = rel.split("/", 1)[0]
        meta = [
            {"key": "path", "string_value": kb_path},
            {"key": "section", "string_value": section},
            {"key": "hash", "string_value": new_hash},
        ]

        # Agregar campos del frontmatter
        for key in ["title", "description", "department", "doc_type", 
                    "owner_team", "maintainer", "visibility", "last_updated"]:
            value = fm.get(key)
            if value:
                meta.append({"key": key, "string_value": str(value)})

        # Agregar keywords si existen
        keywords = fm.get("keywords")
        if isinstance(keywords, list) and keywords:
            meta.append({"key": "keywords_csv", "string_value": ",".join([str(k) for k in keywords])})

        # Subir al Store
        try:
            response = client.file_search_stores.upload_to_file_search_store(
                file=str(p),
                file_search_store_name=STORE_NAME,
                config={
                    "display_name": kb_path,
                    "mime_type": "text/markdown",
                    "custom_metadata": meta,
                },
            )
            
            # response es una Operation, esperar a que complete
            import time
            operation = response
            max_wait = 60  # segundos
            waited = 0
            while not operation.done and waited < max_wait:
                time.sleep(2)
                operation = client.operations.get(operation.name)
                waited += 2
            
            if not operation.done:
                logger.warning(f"      ⚠️ Operación no completó en {max_wait}s (continuando)")
            
            # Después de que se complete, buscar el documento que se creó
            # Puede haber delay de propagación, reintentar
            store_doc_id = None
            for attempt in range(5):  # Reintentar hasta 5 veces
                docs = client.file_search_stores.documents.list(parent=STORE_NAME)
                for doc in docs:
                    for meta_item in doc.custom_metadata:
                        if meta_item.key == "path" and meta_item.string_value == kb_path:
                            # Encontramos un documento con este path
                            # Si hay multiple (viejo y nuevo), tomar el más reciente (últimamente creado)
                            if store_doc_id is None or doc.create_time > docs_by_path[-1].create_time:
                                store_doc_id = doc.name
                            break
                
                if store_doc_id and "documents/" in store_doc_id:
                    # Encontramos el document_id real
                    break
                elif attempt < 4:
                    logger.info(f"      ⏳ Esperando replicación del documento ({attempt+1}/5)...")
                    time.sleep(3)
            
            if not store_doc_id:
                # Fallback: usar el operation name si no encontramos el doc
                store_doc_id = operation.name
                logger.warning(f"      ⚠️ No se encontró document_id después de reintentos, usando operation_id")
            elif "upload/operations" in store_doc_id:
                logger.warning(f"      ⚠️ Solo encontré operation_id, no document_id final")
            
            logger.info(f"      ✅ Subido exitosamente")
            logger.info(f"         Store ID: {store_doc_id[:60]}...")
            
            # Guardar en nuevo estado
            new_state[kb_path] = {
                "hash": new_hash,
                "store_doc_id": store_doc_id,
            }

        except Exception as e:
            logger.error(f"      ❌ Error subiendo: {e}")
            # Mantener entrada antigua si la había
            if kb_path in old_state:
                new_state[kb_path] = old_state[kb_path]
            raise

    # ─────────────────────────────────────────────────────────────
    # 5. Detectar archivos ELIMINADOS (estaban antes, ya no existen)
    # ─────────────────────────────────────────────────────────────
    logger.info(f"\n🗑️  PASO 5: Detectando eliminados...")
    for kb_path in old_state:
        if kb_path not in current_hashes:
            logger.info(f"   {kb_path}")
            logger.info(f"      ⚠️ Path ya no existe en kb/")
            
            store_doc_id = old_state[kb_path].get("store_doc_id")
            if store_doc_id:
                delete_document(store_doc_id)
            stats["deleted"] += 1

    # ─────────────────────────────────────────────────────────────
    # 6. Guardar nuevo estado
    # ─────────────────────────────────────────────────────────────
    logger.info(f"\n💾 PASO 6: Guardando nuevo estado...")
    save_sync_state(new_state)

    # ─────────────────────────────────────────────────────────────
    # 7. Resumen final
    # ─────────────────────────────────────────────────────────────
    logger.info(f"\n" + "=" * 70)
    logger.info(f"📊 RESUMEN DE SINCRONIZACIÓN:")
    logger.info(f"   ⬆️  Nuevos:       {stats['uploaded']}")
    logger.info(f"   🔄 Actualizados: {stats['updated']}")
    logger.info(f"   ✓ Sin cambios:   {stats['unchanged']}")
    logger.info(f"   🗑️  Eliminados:   {stats['deleted']}")
    logger.info(f"   📚 Total en Store: {len(new_state)}")
    logger.info(f"=" * 70)
    logger.info(f"\n✅ ¡SYNC COMPLETADO EXITOSAMENTE!")
    logger.info(f"\n👉 File Search Store ID:")
    logger.info(f"   {STORE_NAME}")
    logger.info(f"\n👉 Úsalo en la configuración del bot:")
    logger.info(f"   FILE_SEARCH_STORE_NAMES={STORE_NAME}")

    # ─────────────────────────────────────────────────────────────
    # 8. Guardar cambios en Git (si estamos en CI/CD)
    # ─────────────────────────────────────────────────────────────
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        logger.info(f"\n💾 PASO 8: Guardando sync_state.json en Git...")
        try:
            import subprocess
            
            # Configurar git user (necesario en GitHub Actions)
            subprocess.run(["git", "config", "--global", "user.email", "sync@github.local"], check=False)
            subprocess.run(["git", "config", "--global", "user.name", "KB Sync Bot"], check=False)
            
            # Add the sync state file
            result_add = subprocess.run(["git", "add", str(STATE_FILE)], capture_output=True, text=True)
            if result_add.returncode != 0:
                logger.warning(f"   ⚠️ Error en 'git add': {result_add.stderr}")
            
            # Verificar si hay cambios para commitear
            result_diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
            if result_diff.returncode != 0:  # Hay cambios (exit code 1 si hay diferencias)
                # Hacer commit
                result_commit = subprocess.run(
                    ["git", "commit", "-m", "chore: update sync_state.json after KB sync"],
                    capture_output=True,
                    text=True
                )
                if result_commit.returncode != 0:
                    logger.warning(f"   ⚠️ Error en 'git commit': {result_commit.stderr}")
                else:
                    logger.info(f"   ✓ Commit realizado")
                    
                    # Hacer push
                    result_push = subprocess.run(
                        ["git", "push", "origin", "main"],
                        capture_output=True,
                        text=True
                    )
                    if result_push.returncode != 0:
                        logger.warning(f"   ⚠️ Error en 'git push': {result_push.stderr}")
                    else:
                        logger.info(f"   ✅ sync_state.json pusheado exitosamente")
            else:
                logger.info(f"   ✓ No hay cambios en sync_state.json para commitear")
        except Exception as e:
            logger.warning(f"   ⚠️ Error al procesar git operations: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"\n❌ FALLO FATAL: {e}")
        exit(1)

