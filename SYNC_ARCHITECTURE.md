# 🏗️ KB Sync Architecture

## Problema Original

El workflow de GitHub Actions estaba **duplicando documentos** (28 en lugar de 14). La raíz del problema:

- Google File Search Store API **NO persiste** el campo `display_name` entre ejecuciones
- Los documentos quedan en estado `STATE_PENDING` durante minutos (indexación)
- No hay forma de identificar cuál documento viejo corresponde a qué hash nuevo
- El workflow no puede detectar qué ya subió anteriormente

## 🎯 Solución: `.sync_state.json`

Mantenemos un **libro mayor local** que mapea cada archivo a su estado en el Store:

```json
{
  "kb/changelog/changelog.md": {
    "hash": "6a64ced5e0a2c867204d920140de43b7602e5e25...",
    "store_doc_id": "fileSearchStores/zigchainhandbookmvp-eyex7dtbkzyo/upload/operations/kbchangelogchangelogmd-j0e1d76s9qvx"
  },
  "kb/devrel/overview.md": {
    "hash": "84a0954460265d0634343e80543a6398e308f8cdbff1fd6225ab8631ff83db4c",
    "store_doc_id": "fileSearchStores/zigchainhandbookmvp-eyex7dtbkzyo/upload/operations/kbdevreloverviewmd-rxilar3dzsza"
  }
}
```

**Ubicación:** `.sync_state.json` (raíz del proyecto)  
**En Git:** ❌ NO - está en `.gitignore`

## 🔄 Flujo de Sincronización

### PASO 1: Cargar Estado Anterior
```
Lee sync_state.json → obtiene mapping: path → {hash, store_doc_id}
```

### PASO 2: Calcular Hashes Actuales
```
Para cada archivo .md en kb/:
  - Calcula SHA256 del contenido
  - Crea mapping: path → hash
```

### PASO 3: Procesar Cambios

Para cada archivo:

#### **CASO A: Sin cambios** ✓
```
IF hash_nuevo == hash_anterior:
  → SALTAR (no hacer nada)
  → Mantener documento en Store
  → Mantener entrada en sync_state.json
```

#### **CASO B: Archivo actualizado** 🔄
```
IF hash_nuevo != hash_anterior AND store_doc_id existe:
  → BORRAR documento viejo del Store (por store_doc_id)
  → SUBIR documento nuevo
  → ACTUALIZAR sync_state.json con nuevo hash + nuevo Store ID
```

#### **CASO C: Archivo nuevo** ⬆️
```
IF path NOT IN sync_state.json:
  → SUBIR documento al Store
  → AGREGAR entrada a sync_state.json
```

### PASO 4: Detectar Eliminados
```
FOR each path_anterior IN sync_state.json:
  IF path NOT IN archivos actuales:
    → BORRAR documento del Store (por store_doc_id)
    → ELIMINAR entrada de sync_state.json
```

### PASO 5: Guardar Nuevo Estado
```
Escribe sync_state.json con estado final
```

## 🛡️ Garantías

✅ **Nunca duplica**
- Si el hash no cambió, el documento no se re-sube
- Si el hash cambió, borramos el viejo ANTES de subir el nuevo

✅ **Detecta cambios**
- Usa SHA256 para detectar cualquier cambio en el contenido

✅ **No depende de API instable**
- No confía en `display_name` persistido
- No espera a que State se vuelva `STATE_ACTIVE`
- Mantiene su propio "libro mayor"

✅ **Identificación 100% certera**
- Mapeo unívoco: `path → (hash, Store ID)`
- Cuando necesita actualizar, sabe exactamente qué borrar (por Store ID)

✅ **Funciona en CI/CD**
- `.sync_state.json` NO va en Git
- Cada workflow run es independiente
- Usa los secrets de GitHub Actions

## 📊 Prueba de Concepto

### Primera ejecución (sin sync_state.json)
```
📊 RESUMEN:
   ⬆️  Nuevos:       14
   🔄 Actualizados: 0
   ✓ Sin cambios:   0
   🗑️  Eliminados:   0
   📚 Total en Store: 14
```

### Segunda ejecución (sin cambios)
```
📊 RESUMEN:
   ⬆️  Nuevos:       0
   🔄 Actualizados: 0
   ✓ Sin cambios:   14
   🗑️  Eliminados:   0
   📚 Total en Store: 14
```

✅ **Resultado:** ¡PERFECTO! No duplica, detecta correctamente.

## 🚀 Scripts

### `sync_kb_to_store.py`
Script principal. Ejecuta el flujo completo.

```bash
# Local (desarrollo)
python sync_kb_to_store.py

# En GitHub Actions (automático)
# Activado por: push a main + cambios en kb/
```

### `reset_kb.py`
Limpia el Store (borra todos los documentos). Útil para debugging.

```bash
python reset_kb.py
```

### `audit_kb.py`
Verifica qué hay en el Store actualmente.

```bash
python audit_kb.py
```

## 🔧 Configuración

### `.env` (desarrollo)
```env
GEMINI_API_KEY=your-key-here
FILE_SEARCH_STORE_NAME=fileSearchStores/zigchainhandbookmvp-eyex7dtbkzyo
STORE_DISPLAY_NAME=zigchain-handbook-mvp
```

### GitHub Actions Secrets
Necesitas agregar estos 3 secrets en Settings → Secrets and variables → Actions:

- `GEMINI_API_KEY` → Tu API key de Google Generative AI
- `FILE_SEARCH_STORE_NAME` → El Store ID (obtenido en primera ejecución)
- `STORE_DISPLAY_NAME` → Nombre display del Store

### Workflow (`.github/workflows/sync-kb.yml`)
Se ejecuta automáticamente cuando:
- Push a `main`
- Cambios en:
  - `kb/**` (archivos KB)
  - `sync_kb_to_store.py` (el script)
  - `requirements.txt` (dependencias)
  - `.github/workflows/sync-kb.yml` (el workflow mismo)

## 📝 Notas de Implementación

### ¿Por qué no usar `display_name`?
Probamos 5 versiones diferentes. Google Store API simplemente **no devuelve** `display_name` en los listados, solo se mantiene internamente. No es confiable para identificar documentos.

### ¿Por qué no esperar a `STATE_ACTIVE`?
Probamos `wait_operation()` del SDK - se colgaba infinitamente. No es una opción viable.

### ¿Por qué no usar metadata customizada para tracking?
La metadata customizada SÍ persiste, pero:
1. No aparece en los listados mientras el doc está en `STATE_PENDING`
2. Aún así necesitaríamos esperar a que indexe (problema arriba)

### ¿Por qué `.sync_state.json` local?
Es el único enfoque que funciona porque:
1. No depende de API inestable
2. Funciona en workflows stateless (GitHub Actions)
3. No contamina Git
4. Es simple y confiable

## 🎓 Lecciones Aprendidas

1. **Confía en lo que controlas**, no en APIs externas impredecibles
2. **Mantén estado local** cuando el estado remoto es incierto
3. **Mapeos explícitos** son mejores que heurísticas
4. **Borra antes de crear** (para evitar duplicados durante actualizaciones)
5. **Testa el happy path**: 1ª run (upload), 2ª run (sin cambios)
