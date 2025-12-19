---
title: "E2E Test - New Document"
description: "Documento creado para probar E2E: subir nuevo archivo completo y verificar sincronización"
department: "shared"
doc_type: "guide"
owner_team: "Platform"
maintainer: "Quero"
visibility: "internal"
keywords: ["e2e", "test", "sync"]
last_updated: "2025-12-19 10:00 - E2E Test: New doc"
---

## E2E Test - New Document

Este documento se creó para probar la canalización de sincronización (KB → File Search Store).

Contenido de prueba:

- Paso 1: crear documento
- Paso 2: push a GitHub
- Paso 3: GitHub Actions ejecuta `sync_kb_to_store.py`
- Paso 4: Verificar `sync_state.json` actualizado y que el Store contiene el nuevo documento

Por favor, no borres este archivo hasta que confirmemos que el proceso funcionó.
