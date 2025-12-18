"""
Script de DEBUG: Ver exactamente qué hay en el Store
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STORE_NAME = os.getenv("FILE_SEARCH_STORE_NAME", "").strip()
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

print(f"\n📌 Store: {STORE_NAME}\n")

# Listar todos los documentos
docs = []
page_token = None
while True:
    params = {"key": GEMINI_API_KEY, "pageSize": 20}
    if page_token:
        params["pageToken"] = page_token
    url = f"{BASE_URL}/{STORE_NAME}/documents"
    
    r = requests.get(url, params=params, timeout=60)
    if r.status_code == 400:
        print("Store vacío o problema")
        break
    
    data = r.json()
    docs.extend(data.get("documents", []))
    page_token = data.get("nextPageToken")
    if not page_token:
        break

print(f"✅ Total: {len(docs)} documentos\n")
print("=" * 80)

# Mostrar cada documento
for i, doc in enumerate(docs, 1):
    name = doc.get("name", "").split("/")[-1]
    display = doc.get("display_name", "")
    print(f"{i:2d}. Name: {name}")
    print(f"    Display: {display}")
    print()

# Agrupar por display_name
from collections import Counter
displays = [doc.get("display_name", "") for doc in docs]
duplicates = {k: v for k, v in Counter(displays).items() if v > 1}

if duplicates:
    print("=" * 80)
    print("⚠️  DUPLICADOS DETECTADOS:")
    for display, count in duplicates.items():
        print(f"   {display} → {count} copias")
else:
    print("=" * 80)
    print("✅ Sin duplicados")
