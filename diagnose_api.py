"""
Script de diagnóstico para verificar la API de Google File Search correctamente.
Este script verifica EXACTAMENTE cómo deben hacerse las peticiones según la docs oficial.
"""

import os
import json
import logging
from pathlib import Path

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

if not GEMINI_API_KEY:
    raise RuntimeError("❌ Falta GEMINI_API_KEY en .env")
if not STORE_NAME:
    raise RuntimeError("❌ Falta FILE_SEARCH_STORE_NAME en .env")

# Endpoint base según documentación oficial
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

logger.info("=" * 70)
logger.info("🔍 DIAGNÓSTICO DE API - FILE SEARCH")
logger.info("=" * 70)
logger.info(f"\n📌 Configuración:")
logger.info(f"   API Key: {'✅ Presente' if GEMINI_API_KEY else '❌ Falta'}")
logger.info(f"   Store Name: {STORE_NAME}")
# ============================================================
# Helper Functions
# ============================================================

def fetch_documents_via_rest(url: str, api_key: str, page_size: int = 50) -> tuple[list, int]:
    """Fetch first page of documents via REST API"""
    try:
        response = requests.get(
            url,
            params={"key": api_key, "pageSize": page_size},
            timeout=30,
            headers={"User-Agent": "GoogleGenAI/1.0"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("documents", []), response.status_code
    except Exception as e:
        logger.error(f"❌ REST API Error: {e}")
        return [], 0


def fetch_all_documents_paginated(url: str, api_key: str, max_pages: int = 10) -> list:
    """Paginate through all documents"""
    all_docs = []
    page_token = None
    page_count = 0

    try:
        while page_count < max_pages:
            page_count += 1
            logger.info(f"   Página {page_count}...")
            
            params = {"key": api_key, "pageSize": 50}
            if page_token:
                params["pageToken"] = page_token
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            docs = data.get("documents", [])
            all_docs.extend(docs)
            
            logger.info(f"      → {len(docs)} en esta página, {len(all_docs)} total")
            
            page_token = data.get("nextPageToken")
            if not page_token:
                logger.info(f"      → Fin de páginas")
                break
    except Exception as e:
        logger.error(f"❌ Error paginando: {e}")

    return all_docs

# ============================================================
# TEST 1: Verificar Store usando SDK de Google
# ============================================================
logger.info("\n\n🧪 TEST 1: Verificar Store con SDK de Google")
logger.info("-" * 70)

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    store = client.file_search_stores.get(name=STORE_NAME)
    logger.info(f"✅ Store encontrado por SDK:")
    logger.info(f"   Name: {store.name}")
    logger.info(f"   Display: {getattr(store, 'display_name', 'N/A')}")
    logger.info(f"   CreateTime: {getattr(store, 'create_time', 'N/A')}")
except Exception as e:
    logger.error(f"❌ Error con SDK: {e}")

# ============================================================
# TEST 2: Petición HTTPS a documents.list (como dice la docs)
# ============================================================
logger.info("\n\n🧪 TEST 2: Petición HTTPS directa a documents.list")
logger.info("-" * 70)

url = f"{BASE_URL}/{STORE_NAME}/documents"
logger.info(f"   URL: {url}")

docs, status = fetch_documents_via_rest(url, GEMINI_API_KEY)

if status == 200:
    logger.info(f"✅ Respuesta exitosa (Status 200)")
    logger.info(f"   Total documentos: {len(docs)}")
    
    if docs:
        logger.info(f"\n   Primeros documentos:")
        states = {}
        for doc in docs[:5]:
            name = doc.get("name", "N/A")
            state = doc.get("state", "UNKNOWN")
            states[state] = states.get(state, 0) + 1
            logger.info(f"      - {name.split('/')[-1]}: {state}")
    else:
        logger.warning(f"⚠️  Sin documentos en esta página")
elif status == 400:
    logger.warning(f"⚠️  Status 400 - Posible Store vacío o error en parámetros")
else:
    logger.error(f"❌ Error HTTP {status}")

# ============================================================
# TEST 3: Paginar completamente
# ============================================================
logger.info("\n\n🧪 TEST 3: Paginar completamente a través de todos los documentos")
logger.info("-" * 70)

all_docs = fetch_all_documents_paginated(url, GEMINI_API_KEY)
logger.info(f"\n✅ TOTAL ACUMULADO: {len(all_docs)} documentos")

# ============================================================
# TEST 4: Contar por estado
# ============================================================
logger.info("\n\n🧪 TEST 4: Análisis de estados")
logger.info("-" * 70)

states = {}
for doc in all_docs:
    state = doc.get("state", "UNKNOWN")
    states[state] = states.get(state, 0) + 1

logger.info(f"   Distribución por estado:")
for state, count in sorted(states.items()):
    logger.info(f"      {state}: {count}")

# Documentación dice:
# STATE_UNSPECIFIED = valor default (no debería aparecer)
# STATE_PENDING = Se están procesando chunks (INVISIBLE A LISTADO)
# STATE_ACTIVE = Listos para queries
# STATE_FAILED = Error en procesamiento

logger.info(f"\n   🔔 Nota importante según docs:")
logger.info(f"      STATE_PENDING = En indexado (NO visible en listado)")
logger.info(f"      STATE_ACTIVE = Listo para búsquedas")
logger.info(f"      STATE_FAILED = Error en procesamiento")

# ============================================================
# TEST 5: Verificar Store por SDK también
# ============================================================
logger.info("\n\n🧪 TEST 5: Listar documentos por SDK (comparación)")
logger.info("-" * 70)

try:
    docs_sdk = client.file_search_stores.documents.list(parent=STORE_NAME)
    docs_list = list(docs_sdk)
    logger.info(f"✅ SDK Lista documentos: {len(docs_list)}")
    
    for doc in docs_list[:3]:
        logger.info(f"   - {doc.name}: state={doc.state}")
    if len(docs_list) > 3:
        logger.info(f"   ... y {len(docs_list) - 3} más")
        
except Exception as e:
    logger.error(f"❌ Error con SDK listing: {e}")

# ============================================================
# RESUMEN FINAL
# ============================================================
logger.info("\n\n" + "=" * 70)
logger.info("📊 RESUMEN DE DIAGNÓSTICO")
logger.info("=" * 70)
logger.info(f"\n   HTTPS directo (requests): {len(all_docs)} documentos")
logger.info(f"   SDK (genai.Client): {len(docs_list) if 'docs_list' in locals() else 'error'} documentos")
logger.info(f"\n   ❓ Si los números no coinciden, posible problema:")
logger.info(f"      • Documentos en STATE_PENDING no aparecen en listado")
logger.info(f"      • Documentos en STATE_FAILED no aparecen")
logger.info(f"      • Problema con autenticación")
logger.info(f"      • Problema con paginación")

logger.info("\n✅ Diagnóstico completado")
