"""
Script para VACIAR completamente el File Search Store.
Úsalo manualmente cuando necesites empezar desde cero.

python reset_kb.py
"""

import os
import logging
from pathlib import Path
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

if not GEMINI_API_KEY:
    raise RuntimeError("❌ Falta GEMINI_API_KEY en .env")
if not STORE_NAME:
    raise RuntimeError("❌ Falta FILE_SEARCH_STORE_NAME en .env")

client = genai.Client(api_key=GEMINI_API_KEY)

def list_documents(store_name: str):
    """Lista todos los documentos en el store usando el SDK de Google"""
    try:
        docs_iterator = client.file_search_stores.documents.list(parent=store_name)
        docs = list(docs_iterator)
        return docs
    except Exception as e:
        logger.error(f"❌ Error listando documentos: {e}")
        return []

def delete_document(doc_name: str):
    """Borra un documento usando el SDK con force=true"""
    try:
        client.file_search_stores.documents.delete(
            name=doc_name,
            config={"force": True}
        )
        logger.info(f"   ✓ Borrado: {doc_name.split('/')[-1]}")
    except Exception as e:
        logger.error(f"❌ Error borrando {doc_name}: {e}")

def main(auto_confirm=False):
    logger.info("=" * 60)
    logger.info("🧹 RESET DEL KB - VACIAR COMPLETAMENTE")
    logger.info("=" * 60)
    logger.info(f"\n📌 Store: {STORE_NAME[:50]}...")
    
    # Listar documentos
    logger.info("\n📋 Buscando documentos en el store...")
    docs = list_documents(STORE_NAME)
    
    if not docs:
        logger.warning("⚠️  No hay documentos para borrar. El store ya está vacío.")
        return
    
    logger.info(f"   Encontrados: {len(docs)} documentos")
    
    # Confirmación
    if not auto_confirm:
        logger.info("\n⚠️  ADVERTENCIA: Estás a punto de BORRAR TODOS los documentos.")
        confirm = input("¿Continuar? Escribe 'SI' para confirmar: ").strip().upper()
        
        if confirm != "SI":
            logger.info("❌ Operación cancelada.")
            return
    
    # Borrar todos
    logger.info("\n🗑️  Borrando documentos...")
    deleted = 0
    for doc in docs:
        doc_name = doc.name  # Document object has .name attribute, not .get()
        if doc_name:
            delete_document(doc_name)
            deleted += 1
    
    # Resumen
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ RESET COMPLETADO")
    logger.info(f"   Documentos borrados: {deleted}")
    logger.info("=" * 60)
    logger.info("\n👉 El Store está vacío. Listo para un nuevo upload.")

if __name__ == "__main__":
    main()
