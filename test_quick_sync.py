"""Test rápido sin esperar operaciones"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

ROOT = Path(__file__).resolve().parent
KB_DIR = ROOT / "kb"

load_dotenv(ROOT / ".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STORE_NAME = os.getenv("FILE_SEARCH_STORE_NAME", "").strip()
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# Listar documentos
print(f"📋 Store: {STORE_NAME}")
params = {"key": GEMINI_API_KEY, "pageSize": 50}
url = f"{BASE_URL}/{STORE_NAME}/documents"

try:
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    docs = data.get("documents", [])
    print(f"✅ Encontrados: {len(docs)} documentos")
    
    # Mostrar primero con su metadata
    if docs:
        doc = docs[0]
        print(f"\n📄 Primer doc:")
        print(f"  name: {doc.get('name')}")
        print(f"  displayName: {doc.get('displayName')}")
        print(f"  customMetadata: {doc.get('customMetadata')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Contar archivos locales
md_files = sorted(KB_DIR.rglob("*.md"))
md_files = [p for p in md_files if p.name.lower() != "template.md"]
print(f"\n📁 Archivos locales: {len(md_files)}")
