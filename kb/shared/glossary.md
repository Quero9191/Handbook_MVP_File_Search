---
title: "Company Glossary"
description: "Common terms, acronyms, and definitions used across the organization"
department: "shared"
doc_type: "glossary"
owner_team: "All Teams"
maintainer: "Communications"
visibility: "internal"
keywords: ["glossary", "acronyms", "definitions", "terminology"]
last_updated: "2025-12-18 17:34 - CLEAN BASELINE TEST"
---

## Purpose
Unified glossary to avoid confusion and ensure everyone speaks the same language. Add new terms as they emerge.

## A–Z Glossary

### Severity Levels
- **SEV-1 (Critical)**: Complete outage, data loss risk, or >10% of users affected. All-hands-on-deck.
- **SEV-2 (High)**: Major feature broken, affecting 1–10% of users or 1+ customer. War room, escalation path.
- **SEV-3 (Medium)**: Workaround exists, minor feature broken, internal impact only.
- **SEV-4 (Low)**: Bug that doesn't block work, enhancement, nice-to-have.

### Common Terms
- **IC (Incident Commander)**: Person who owns the incident response, coordinates communication and decisions.
- **MTTR (Mean Time To Recovery)**: Average time from incident detection to resolution. Lower is better.
- **War Room**: Dedicated Zoom + Slack thread for real-time incident response.
- **Postmortem**: After-incident review to identify root causes and prevent recurrence.
- **CAC (Cost Acquisition Customer)**: Total marketing spend / new customers acquired.
- **CTR (Click-Through Rate)**: (Clicks / Impressions) × 100. Measure of ad/link effectiveness.
- **CPC (Cost Per Click)**: Total ad spend / clicks. Used for paid campaigns.
- **UTM Parameters**: URL tags (utm_source, utm_medium, utm_campaign) to track campaign traffic.
- **Sprint**: 2-week development cycle with defined goals.
- **Runbook**: Step-by-step guide to handle common operational tasks (incident response, deployments).
- **Rollback**: Reverting to a previous code version to undo a broken deployment.
- **Feature Flag**: Software switch to enable/disable a feature without deploying new code.
- **GitHub Actions**: Automation tool that runs workflows (tests, deploys, syncs) when events happen (push, PR, etc.).
- **Smart Sync Verification**: Test entry added 2025-12-17 22:45 to verify incremental sync detection works correctly.

### Tools & Systems
- **GitHub**: Code repository and PR review system.
- **Slack**: Internal communication tool.
- **Mailchimp**: Email marketing platform.
- **Google Analytics**: Website traffic and conversion tracking.
- **Statuspage.io**: Customer-facing status dashboard for incidents.

### Document Types (in KB)
- **Playbook**: Detailed guide for complex processes (incident response, deployment).
- **Checklist**: Quick reference list to verify nothing was missed.
- **Guide**: How-to instructions (code contributions, using tools).

### 🎉 Prueba de Sincronización (Agregado 2025-12-18 22:50)
Esta sección fue agregada como prueba para verificar que el sistema de sincronización incremental funciona correctamente.

**Qué se cambió:**
- Se agregó esta nueva sección al glossario
- El hash del documento cambió
- El sistema debería detectarlo automáticamente
- El Store debería actualizar el documento (borrar viejo, subir nuevo)
- El bot debería poder ver esta nueva sección
- GitHub Actions ahora commitea sync_state.json de vuelta al repo

**Prueba en el bot:**
Si preguntás "¿Qué significa prueba de sincronización?", el bot debería encontrar esta entrada y explicarte que se trata de una verificación del sistema de sync.

**Actualización 2025-12-18 23:00:**
Se corrigió el sistema para que sync_state.json se persista en Git. Ahora:
- Primera ejecución en GitHub: crea y llena sync_state.json
- Commitea el resultado de vuelta al repo (con autenticación GITHUB_TOKEN)
- Segunda ejecución: detecta cambios correctamente
- ¡¡¡SIN DUPLICADOS GARANTIZADO!!!

**Actualización 2025-12-18 23:03:**
Se corrigió el problema de autenticación en el workflow usando `git-auto-commit-action`.
El bot ya debería poder consultar esta sección.

**Status:** ✅ Sistema completamente funcional

---

**NOTA FINAL:** El bot debería poder acceder a toda esta información en tiempo real.
- **Process**: Step-by-step workflow for regular operations (releases, campaigns).
- **Overview**: High-level summary of a topic or department.
- **Policy**: Rules and compliance requirements.
- **FAQ**: Common questions and answers.

## Notes / Gotchas
- **Add new terms as you go**—don't wait for "official" definition
- **Link to related docs**—glossary is a hub, not an island

## Related
- [All KB Docs](../)


- **Test Recovery**: Sistema de recuperación testado


## Actualización: 18 de Diciembre 2025
✅ INCREMENTAL TEST - Delete old, upload new
