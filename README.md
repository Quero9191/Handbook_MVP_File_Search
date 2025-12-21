# 📚 Handbook MVP - File Search Knowledge Base

**Smart Gemini File Search synchronization system** that eliminates duplicates through SHA256-based change detection and persistent state mapping.

## 🎯 What It Does

Automatically syncs your Markdown knowledge base (`kb/` folder) to a Google Gemini File Search Store with **zero duplicates**, even with incremental updates. Uses GitHub Actions for automated synchronization.

**Key Features:**
- ✅ **Zero Duplicates** - SHA256 hash-based deduplication and store-ID tracking
- ✅ **Incremental Sync** - Only changed files are processed (no full reupload required)
- ✅ **Automated** - GitHub Actions triggers on `kb/` changes
- ✅ **Recoverable** - `sync_state.json` enables safe rollback and idempotent syncs
- ✅ **Integrated** - Works with the Slack bot which queries the File Search Store

## 📚 Estructura

```
kb/
├── organization/          # Estructura de la empresa
├── handbook/              # Procesos y guías operativas
├── incidents/             # Gestión de incidentes
├── devrel/                # Developer Relations & comunicación
├── growth/                # Marketing y growth
├── shared/                # Recursos compartidos (glosario, herramientas)
└── changelog/             # Historial de cambios
```

## 📄 Documentos incluidos (14 docs)

| Documento | Path | Tipo |
|-----------|------|------|
| Incident Management Playbook | `incidents/playbook-incident-management-framework.md` | Playbook |
| Incident Triage Checklist | `incidents/checklist-incident-triage.md` | Checklist |
| GitHub Contribution Guide | `handbook/guide-github-contribution.md` | Guía |
| Release Notes Process | `devrel/processes/process-release-notes.md` | Proceso |
| Campaign Launch Process | `growth/processes/process-campaign-launch.md` | Proceso |
| Company Glossary | `shared/glossary.md` | Glosario |
| Organization Overview | `organization/overview.md` | Overview |
| Handbook Overview | `handbook/overview.md` | Overview |
| Document Types | `handbook/handbook-document-types.md` | Referencia |
| DevRel Overview | `devrel/overview.md` | Overview |
| Growth Overview | `growth/overview.md` | Overview |
| UTM Tracking Guide | `growth/guides/guide-utm-tracking.md` | Guía |
| Tools & Links | `shared/tools-and-links.md` | Referencia |
| Changelog | `changelog/changelog.md` | Historial |

## ⚙️ Cómo funciona

### Sincronización automática

1. **Local**: Editas un archivo en `kb/` y haces commit + push a `main`
2. **GitHub Actions**: El workflow detecta cambios y ejecuta `sync_kb_to_store.py`
3. **Detección**: El script calcula hashes SHA256 para detectar qué cambió
4. **Store**: Borra documentos viejos y sube nuevos a Gemini File Search Store
5. **Estado**: Guarda el mapeo (path → Store ID) en `sync_state.json` y hace commit/push

### Archivo clave: `sync_state.json`

```json
{
  "kb/path/to/file.md": {
    "hash": "sha256_hash_value",
    "store_doc_id": "fileSearchStores/.../documents/id"
  }
}
```

Este archivo está en Git para que:
- El workflow sepa qué documentos ya existen en el Store
- Pueda identificar exactamente cuál Store ID corresponde a cada archivo
- Evite crear duplicados

## 🚀 Setup

### 1. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con:
```
GEMINI_API_KEY=your_api_key_here
FILE_SEARCH_STORE_NAME=fileSearchStores/your-store-id
STORE_DISPLAY_NAME=zigchain-handbook-mvp
```

### 2. Instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Para GitHub Actions

Agrega estos secrets en GitHub repo settings:
- `GEMINI_API_KEY`
- `FILE_SEARCH_STORE_NAME`
- `STORE_DISPLAY_NAME`

El workflow ejecutará automáticamente cuando haya cambios en:
- `kb/**` (archivos KB)
- `sync_kb_to_store.py` (script sync)
- `.github/workflows/sync-kb.yml` (workflow)

## 📝 Cómo agregar documentos

1. Crea archivo en `kb/{section}/documento.md`
2. Usa frontmatter YAML:
   ```yaml
   ---
   title: "Título del documento"
   description: "Descripción"
   department: "section"
   doc_type: "guía|proceso|checklist|playbook|referencia"
   owner_team: "Team responsable"
   maintainer: "Persona"
   visibility: "internal"
   keywords: ["keyword1", "keyword2"]
   last_updated: "YYYY-MM-DD"
    # OPTIONAL: additional metadata supported by the sync script
    # owner: "@person_or_team"
    # last_review: "YYYY-MM-DD"
    # review_cycle_days: 90
    ---
   ```
3. Escribe contenido con Markdown
4. Commit + push a `main`
5. GitHub Actions sincroniza automáticamente

## 🛠️ Scripts disponibles

### `sync_kb_to_store.py`
Sincroniza documentos con Gemini File Search Store. El script es incremental: sólo reemplaza documentos cuyo contenido (incluyendo frontmatter) cambió.
```bash
python3 sync_kb_to_store.py
```

### `audit_kb.py`
Auditoría del Store: verifica estado, lista documentos y ayuda a detectar inconsistencias.
```bash
python3 audit_kb.py
```

### `reset_kb.py`
Elimina TODOS los documentos del Store (uso con cuidado). Útil para empezar desde cero o cuando quieras crear un Store limpio.
```bash
python reset_kb.py
```

## 📊 Monitoreo

### Ver logs de GitHub Actions
https://github.com/Quero9191/Handbook_MVP_File_Search/actions

### Auditar Store localmente
```bash
python audit_kb.py
```

Espera resultado como:
```
✅ TOTAL DE DOCUMENTOS: 14
✓ Sin cambios: 13
🔄 Actualizados: 0
🗑️ Eliminados: 0
⬆️ Nuevos: 1
📚 Total en Store: 14
```

## 🤖 Integración con Slack Bot

El bot consulta el Store con:
```
@bot [pregunta sobre KB]
```

El bot busca en File Search Store y responde con contexto del handbook.

## 📋 Checklist de cambios en KB

- [ ] Archivo está en carpeta correcta (`kb/{section}/`)
- [ ] Frontmatter tiene todos los campos requeridos
- [ ] Título, descripción y keywords son claros
- [ ] Contenido es profesional y actualizado
- [ ] Links internos a otros docs funcionan
- [ ] Commit message es descriptivo
- [ ] Push a `main` (no a rama)
- [ ] GitHub Actions ejecutó (ver en Actions tab)
- [ ] Audit muestra 14 documentos (sin duplicados)

## ❓ Troubleshooting

**Q: GitHub Actions falló**
→ Ver logs en Actions tab; comprobar que `GEMINI_API_KEY` y `FILE_SEARCH_STORE_NAME` estén configurados

**Q: Audit muestra más de 14 documentos**
→ Puede haber inconsistencias históricas. Opciones:
  - Ejecuta `python audit_kb.py` para inspeccionar listas y `store_doc_id`.
  - Si confirmas que quieres empezar desde cero: respalda `sync_state.json`, ejecuta `python reset_kb.py` y luego `python sync_kb_to_store.py`.
  - Alternativa segura: crea un nuevo Store y vuelve a sincronizar allí, luego cambia `FILE_SEARCH_STORE_NAME`.

**Q: Cambios en frontmatter (metadatos) → ¿tengo que re-subir todo?**
→ No. El script detecta cambios por SHA256 y sólo reemplaza los archivos modificados. No es necesario vaciar el Store por cambios de metadatos.

**Q: Cambios no se reflejan en el bot**
→ Espera a que GitHub Actions termine; luego prueba consulta al bot. Si el bot usa cache/TTL, espera el TTL o reinícialo.
## 🚀 Quick Start

### 1. Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure
Create `.env`:
```env
GEMINI_API_KEY=your_api_key_here
# After first sync:
FILE_SEARCH_STORE_NAME=fileSearchStores/...
```

### 3. Sync
```bash
python3 sync_kb_to_store.py
```

### 4. Verify
```bash
python3 audit_kb.py
```

Expected:
```
✅ TOTAL DE DOCUMENTOS: 14
✓ Sin cambios: 13
🔄 Actualizados: 0
🗑️ Eliminados: 0
⬆️ Nuevos: 1
📚 Total en Store: 14
```

## 📝 Files Overview

| File | Purpose |
|------|---------|
| `sync_kb_to_store.py` | Main sync engine |
| `audit_kb.py` | Verify Store integrity |
| `reset_kb.py` | Vacuum entire Store |
| `diagnose_api.py` | Debug API issues |
| `sync_state.json` | Source of truth (14 docs) |
| `.github/workflows/sync-kb.yml` | GitHub Actions automation |

## 🔄 How Sync Works

**The Problem:** Gemini creates new document IDs on every upload → **duplicates**

**The Solution:** Hash-based state mapping in Git
```json
{
  "kb/shared/glossary.md": {
    "hash": "78e29874...",
    "store_doc_id": "fileSearchStores/.../documents/xyz123"
  }
}
```

**6-Step Pipeline:**
1. Store Creation
2. Reconciliation (local vs Store)
3. Hash Calculation (SHA256)
4. Process Changes (upload new/updated, delete old)
5. Detect Deletions
6. Save State to Git

**Guarantees:**
- ✅ Zero duplicates (delete old before upload new)
- ✅ Idempotent (safe to retry)
- ✅ Change-aware (SHA256 based)
- ✅ Recoverable (Git history)

## 📋 Commands

```bash
# Sync (only changed files)
python sync_kb_to_store.py

# Audit Store health
python audit_kb.py

# Debug API
python diagnose_api.py

# ⚠️ Reset (delete all documents)
python reset_kb.py
```

## 📊 Current State

- **14 documentos** en 8 secciones
- **0 Duplicates** (verified)
- **Sync Time** ~30 seconds
- **State File** ~2KB (sync_state.json in Git)

## ✏️ Adding Documents

1. Copy `kb/TEMPLATE.md`
2. Fill YAML frontmatter:
   ```yaml
   ---
   title: "Clear Title"
   description: "One sentence: what and why"
   department: "incidents | devrel | growth | handbook | organization | shared"
   doc_type: "overview | process | playbook | checklist | guide"
   owner_team: "Team Name"
   keywords: ["term1", "term2"]
   ---
   ```
3. Write content
4. Commit & push to `main`
5. GitHub Actions auto-syncs ✅

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Duplicates detected | Run `reset_kb.py`, then `sync_kb_to_store.py` |
| Missing STORE_NAME | Complete first sync, copy ID to `.env` |
| Sync hangs | Check API key, network |
| API errors | Run `diagnose_api.py` |

## 🔐 Security

- `.env` is git-ignored (safe for secrets)
- `sync_state.json` tracked (essential for sync)
- Only manages this Store's documents

## 📚 Resources

- [Google Gemini File Search API](https://ai.google.dev/api/rest)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Related Slack Bot](../slack-bot-files-search-python-hugo)

---

**Version:** 2.0.0 (Production Ready)  
**Last Updated:** 2024-12-18  
**Status:** ✅ All 14 docs synced, zero duplicates, GitHub Actions enabled**¿Preguntas?** Revisa el [Glossary](kb/shared/glossary.md) o contacta al equipo de Communications.
