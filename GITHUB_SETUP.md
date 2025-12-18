# 🔐 Configuración en GitHub - Pasos Requeridos

## Status Actual ✅

- ✅ Script `sync_kb_to_store.py` está listo
- ✅ `.sync_state.json` creado localmente y en `.gitignore`
- ✅ Workflow (`.github/workflows/sync-kb.yml`) está actualizado
- ⏳ **Pendiente:** Agregar secrets en GitHub

## 🎯 Lo Que Tienes Que Hacer en GitHub

### 1. Ir a Settings del Repositorio

1. Abre tu repo en GitHub: https://github.com/Quero9191/Handbook_MVP_File_Search
2. Click en **Settings** (arriba a la derecha)
3. En el menú izquierdo: **Security** → **Secrets and variables** → **Actions**

### 2. Agregar 3 Secrets

Click en **"New repository secret"** y crea estos 3:

#### Secret 1: `GEMINI_API_KEY`
- **Name:** `GEMINI_API_KEY`
- **Value:** Tu API key de Google Generative AI (la misma que está en tu `.env` local)

#### Secret 2: `FILE_SEARCH_STORE_NAME`
- **Name:** `FILE_SEARCH_STORE_NAME`
- **Value:** `fileSearchStores/zigchainhandbookmvp-eyex7dtbkzyo`
  - (Este es el Store que ya tienes, obtenido en la primera ejecución local)

#### Secret 3: `STORE_DISPLAY_NAME`
- **Name:** `STORE_DISPLAY_NAME`
- **Value:** `zigchain-handbook-mvp`

**Resultado esperado:**
```
✓ GEMINI_API_KEY          Last updated a few seconds ago
✓ FILE_SEARCH_STORE_NAME   Last updated a few seconds ago
✓ STORE_DISPLAY_NAME       Last updated a few seconds ago
```

### 3. Verificar el Workflow

En tu repo, ve a **Actions**:

1. Debería mostrar tu workflow en la lista: **"Sync KB to Store"**
2. Si hace push a `main` con cambios en `kb/`, se ejecutará automáticamente
3. El status mostrará ✅ o ❌

## 🧪 Prueba del Workflow (Opcional)

Si quieres testear el workflow sin hacer cambios de verdad:

### Opción A: Trigger manual (si lo implementas)
Agrega esto al workflow para poder ejecutarlo desde GitHub UI:
```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'kb/**'
      - 'sync_kb_to_store.py'
      - 'requirements.txt'
      - '.github/workflows/sync-kb.yml'
  workflow_dispatch:  # ← Esto permite trigger manual
```

### Opción B: Hacer un cambio pequeño
1. Edita cualquier archivo en `kb/` (o agrega un comentario)
2. Commit y push a `main`
3. Mira la ejecución en Actions

**Qué esperar:**
```
✅ Checkout repository
✅ Set up Python
✅ Install dependencies
✅ Run KB Sync to Store
   Output: "0 Sin cambios: 14"
✅ Log sync completion
```

## 📋 Checklist Final

- [ ] Accediste a Settings → Secrets and variables → Actions
- [ ] Agregaste `GEMINI_API_KEY` secret
- [ ] Agregaste `FILE_SEARCH_STORE_NAME` secret (zigchainhandbookmvp-eyex7dtbkzyo)
- [ ] Agregaste `STORE_DISPLAY_NAME` secret (zigchain-handbook-mvp)
- [ ] Los 3 secrets aparecen en la lista (no ves sus valores, solo que existen)
- [ ] El workflow está en `.github/workflows/sync-kb.yml`
- [ ] Hiciste push del código a `main`
- [ ] (Opcional) Ejecutaste el workflow y viste "Sin cambios: 14"

## ⚠️ Cosas Importantes

### No commits de `sync_state.json`
```bash
❌ NUNCA hagas: git add sync_state.json
✅ SIEMPRE está en: .gitignore
```

### No cambies los secrets después
- Una vez agregados, GitHub los encripta
- No puedes verlos de nuevo (solo si los editas)
- Si necesitas cambiar, edita el secret y reemplaza el valor

### El workflow se ejecuta automáticamente
- Cada push a `main` con cambios en `kb/` → sync automático
- No necesitas hacer nada manual
- El log se ve en Actions → workflow name

## 🚨 Si Algo Falla

### Error: "❌ Falta GEMINI_API_KEY"
→ Falta agregar el secret en GitHub

### Error: "❌ Store no encontrado"
→ El valor de `FILE_SEARCH_STORE_NAME` está mal

### El workflow no se ejecuta
→ Verifica que hayas hecho push a `main` (no otra rama)

### El workflow corre pero dice "0 Sin cambios"
→ ¡Perfecto! Significa que nada cambió (comportamiento esperado)

## 📞 Referencia Rápida

**Workflow location:** `.github/workflows/sync-kb.yml`

**What it does:**
1. Cuando pusheas a `main` con cambios en `kb/`
2. Ejecuta `python sync_kb_to_store.py`
3. El script usa los 3 secrets para conectar a Google
4. Sincroniza incrementalmente (no duplica)
5. Genera `.sync_state.json` (que no va a Git)

**Trigger manual (futuro):**
Si quieres poder disparar el workflow desde GitHub UI, agrega `workflow_dispatch:` en el `on:` del workflow.

---

**Done! Tu sistema está listo para producción.** ✅
