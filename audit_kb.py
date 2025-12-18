"""
Script de auditoría del File Search Store.
Verifica:
- Total de documentos
- Documentos duplicados por path
- Documentos sin path
- Problemas de integridad

python audit_kb.py
"""

import os
import logging
from pathlib import Path
from collections import defaultdict
import requests
from dotenv import load_dotenv
from google import genai

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"

load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STORE_NAME = os.getenv("FILE_SEARCH_STORE_NAME", "").strip()
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

if not GEMINI_API_KEY:
    raise RuntimeError("❌ Falta GEMINI_API_KEY en .env")
if not STORE_NAME:
    raise RuntimeError("❌ Falta FILE_SEARCH_STORE_NAME en .env")

client = genai.Client(api_key=GEMINI_API_KEY)

def get_metadata_value(doc: dict, key: str) -> str:
    """Extrae un valor de custom_metadata"""
    try:
        for m in doc.get("custom_metadata", []):
            if m.get("key") == key:
                return m.get("string_value", "")
    except:
        pass
    return ""

def list_documents(store_name: str):
    """Lista todos los documentos en el store usando el SDK de Google"""
    try:
        docs_iterator = client.file_search_stores.documents.list(parent=store_name)
        docs = list(docs_iterator)
        return docs
    except Exception as e:
        logger.error(f"❌ Error listando documentos: {e}")
        return []

def main():
    logger.info("=" * 70)
    logger.info("📋 AUDITORÍA DEL KB - FILE SEARCH STORE")
    logger.info("=" * 70)
    logger.info(f"\n📌 Store: {STORE_NAME[:50]}...")
    
    # Listar todos los documentos
    logger.info("\n🔍 Escaneando documentos...")
    docs = list_documents(STORE_NAME)
    
    logger.info(f"\n✅ TOTAL DE DOCUMENTOS: {len(docs)}")
    
    if len(docs) == 0:
        logger.warning("⚠️  El Store está vacío.")
        return
    
    # Analizar estructura
    logger.info("\n" + "=" * 70)
    logger.info("📊 ANÁLISIS DETALLADO:")
    logger.info("=" * 70)
    
    # Por path
    paths = defaultdict(list)
    sections = defaultdict(int)
    no_path = []
    
    for doc in docs:
        path = get_metadata_value(doc, "path")
        section = get_metadata_value(doc, "section")
        
        if path:
            paths[path].append(doc)
            if section:
                sections[section] += 1
        else:
            no_path.append(doc)
    
    # Documentos por sección
    logger.info("\n📁 DOCUMENTOS POR SECCIÓN:")
    for section in sorted(sections.keys()):
        logger.info(f"   {section}: {sections[section]}")
    
    # Duplicados
    duplicates = {p: docs_list for p, docs_list in paths.items() if len(docs_list) > 1}
    
    if duplicates:
        logger.warning(f"\n⚠️  DUPLICADOS DETECTADOS: {len(duplicates)} paths repetidos")
        for path, docs_list in sorted(duplicates.items()):
            logger.warning(f"   {path}: {len(docs_list)} copias")
            for i, doc in enumerate(docs_list):
                doc_name = doc.get("name", "unknown").split("/")[-1]
                logger.warning(f"      [{i+1}] {doc_name}")
    else:
        logger.info("\n✅ Sin duplicados por path")
    
    # Documentos sin path
    if no_path:
        logger.warning(f"\n⚠️  DOCUMENTOS SIN PATH: {len(no_path)}")
        for doc in no_path:
            display_name = doc.get("display_name", "unknown")
            doc_name = doc.get("name", "unknown").split("/")[-1]
            logger.warning(f"   {display_name} ({doc_name})")
    else:
        logger.info("\n✅ Todos los documentos tienen path")
    
    # Resumen
    logger.info("\n" + "=" * 70)
    logger.info("📈 RESUMEN:")
    logger.info(f"   Total: {len(docs)} documentos")
    logger.info(f"   Únicos (por path): {len(paths)} paths")
    logger.info(f"   Sin path: {len(no_path)}")
    logger.info(f"   Duplicados: {len(duplicates)} paths con múltiples copias")
    logger.info("=" * 70)
    
    # Recomendaciones
    if len(docs) != 14:
        logger.warning(f"\n⚠️  PROBLEMA POTENCIAL:")
        logger.warning(f"   Esperados: 14 documentos")
        logger.warning(f"   Encontrados: {len(docs)}")
        if len(docs) > 14:
            logger.warning(f"   Hay {len(docs) - 14} documentos extra!")
            logger.warning(f"   Recomendación: Ejecutar python reset_kb.py para limpiar")
            logger.warning(f"                 Luego: python sync_kb_to_store.py")
    else:
        logger.info("\n✅ Estado correcto: 14 documentos únicos sin duplicados")

if __name__ == "__main__":
    main()
