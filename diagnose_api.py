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
logger.info(f"   Base URL: {BASE_URL}")

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

# Según la documentación:
# GET https://generativelanguage.googleapis.com/v1beta/{parent=fileSearchStores/*}/documents
# Parámetros: pageSize (int), pageToken (string), key (string)

url = f"{BASE_URL}/{STORE_NAME}/documents"
logger.info(f"   URL: {url}")
logger.info(f"   Parámetros: key=<API_KEY>, pageSize=50")

try:
    response = requests.get(
        url,
        params={
            "key": GEMINI_API_KEY,
            "pageSize": 50,
        },
        timeout=30,
        headers={
            "User-Agent": "GoogleGenAI/1.0",
        }
    )
    
    logger.info(f"\n   Status Code: {response.status_code}")
    logger.info(f"   Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        docs = data.get("documents", [])
        logger.info(f"\n✅ Respuesta exitosa:")
        logger.info(f"   Total documentos en respuesta: {len(docs)}")
        logger.info(f"   nextPageToken presente: {'nextPageToken' in data}")
        logger.info(f"   nextPageToken valor: {data.get('nextPageToken', 'N/A')[:20]}...")
        
        # Analizar estados
        if docs:
            logger.info(f"\n   Detalles de documentos:")
            states = {}
            for doc in docs:
                name = doc.get("name", "N/A")
                state = doc.get("state", "UNKNOWN")
                states[state] = states.get(state, 0) + 1
                logger.info(f"      - {name.split('/')[-1]}: state={state}")
            
            logger.info(f"\n   Resumen de estados:")
            for state, count in sorted(states.items()):
                logger.info(f"      {state}: {count}")
        else:
            logger.warning(f"⚠️  Sin documentos en esta página")
            
    elif response.status_code == 400:
        logger.warning(f"⚠️  Status 400 - Posible Store vacío o error en parámetros")
        logger.info(f"   Response: {response.text[:200]}")
    else:
        logger.error(f"❌ Error HTTP {response.status_code}")
        logger.info(f"   Response: {response.text[:200]}")
        
except Exception as e:
    logger.error(f"❌ Excepción en petición: {e}")

# ============================================================
# TEST 3: Paginar completamente
# ============================================================
logger.info("\n\n🧪 TEST 3: Paginar completamente a través de todos los documentos")
logger.info("-" * 70)

all_docs = []
page_token = None
page_count = 0

try:
    while True:
        page_count += 1
        logger.info(f"   Página {page_count}...")
        
        params = {
            "key": GEMINI_API_KEY,
            "pageSize": 50,
        }
        if page_token:
            params["pageToken"] = page_token
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        docs = data.get("documents", [])
        all_docs.extend(docs)
        
        logger.info(f"      → Documentos en esta página: {len(docs)}")
        logger.info(f"      → Total acumulado: {len(all_docs)}")
        
        page_token = data.get("nextPageToken")
        if not page_token:
            logger.info(f"      → Fin de paginas")
            break
            
        if page_count > 10:
            logger.warning(f"   ⚠️  Limite de 10 páginas alcanzado (previniendo bucle infinito)")
            break
            
except Exception as e:
    logger.error(f"❌ Error paginando: {e}")

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
