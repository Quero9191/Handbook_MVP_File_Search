# Handbook MVP - File Search Knowledge Base

## 🎯 Overview

Sistema automatizado para sincronizar documentos de Knowledge Base con Google Gemini File Search Store. El KB se actualiza automáticamente vía GitHub Actions cuando cambios se pushean a `main`.

**Características:**
- ✅ Sincronización automática por GitHub Actions
- ✅ Detección de cambios por hash SHA256
- ✅ Sin duplicados (mapeo local con `sync_state.json`)
- ✅ Control de versiones en Git
- ✅ Integración con Slack bot para consultas

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
python -m venv .venv
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
   ---
   ```
3. Escribe contenido con Markdown
4. Commit + push a `main`
5. GitHub Actions sincroniza automáticamente

## 🛠️ Scripts disponibles

### `sync_kb_to_store.py`
Sincroniza documentos con Gemini File Search Store.
```bash
python sync_kb_to_store.py
```

### `audit_kb.py`
Auditoría del Store: verifica estado, cuenta documentos, detecta duplicados.
```bash
python audit_kb.py
```

### `reset_kb.py`
Elimina TODOS los documentos del Store (uso con cuidado).
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
   ⬆️  Nuevos: 1
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
→ Ver logs en Actions tab, comprobar que secrets estén configurados

**Q: Audit muestra más de 14 documentos**
→ Hay duplicados, ejecutar `python reset_kb.py` y luego `python sync_kb_to_store.py`

**Q: Cambios no se reflejan en el bot**
→ Esperar 2 min a que GitHub Actions termine, luego probar consulta

## 📚 Recursos

- [Google Gemini File Search API](https://ai.google.dev/api/rest)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Last updated:** 2025-12-18
**Status:** ✅ Production ready

1. Copia [TEMPLATE.md](kb/TEMPLATE.md)
2. Llena el frontmatter (title, description, department, doc_type, etc.)
3. Escribe el contenido usando la estructura sugerida
4. Agrega links a docs relacionados
5. Actualiza [changelog.md](kb/changelog/changelog.md)

### Plantilla base:
```yaml
---
title: "Título claro"
description: "1 frase: qué es y para qué sirve"
department: "incidents | devrel | growth | handbook | organization | shared"
doc_type: "overview | process | playbook | checklist | guide | faq | policy"
owner_team: "Nombre del equipo"
maintainer: "Persona o equipo"
visibility: "internal"
keywords: ["term1", "term2"]
last_updated: "2025-12-17"
---
```

## 🤖 Integración con File Search Bot

1. Importa esta carpeta `kb/` a tu File Search Store
2. El bot podrá buscar y citar documentos específicos
3. Las palabras clave (keywords) mejorarán la búsqueda

**Ejemplo de búsqueda que debería funcionar:**
- "¿Cómo responder a un incidente?" → Encuentra playbook
- "Proceso de release" → Encuentra release notes
- "Contribuir en GitHub" → Encuentra contribution guide

## 🚀 Próximos pasos

1. Importar estos docs al File Search Store
2. Testear búsquedas del bot
3. Agregar más docs según necesidad
4. Recopilar feedback del equipo
5. Expandir a 50+ documentos

## 📞 Contacto & Mantenimiento

- **Owner**: Growth Team
- **Maintainer**: Communications
- **Última actualización**: 2025-12-17
- **Próxima revisión**: 2026-01-17

---

**¿Preguntas?** Revisa el [Glossary](kb/shared/glossary.md) o contacta al equipo de Communications.
