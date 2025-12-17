# Handbook MVP - File Search Knowledge Base

## 📚 Estructura

Este es un Knowledge Base (KB) profesional con documentación consistente para tu bot.

### Carpetas por Departamento

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

## 📄 Documentos MVP (ya creados)

### Prioritarios (6 docs)
1. **Incident Management Playbook** (`incidents/playbook-incident-management-framework.md`)
   - Marco completo de respuesta a incidentes
   
2. **Incident Triage Checklist** (`incidents/checklist-incident-triage.md`)
   - Checklist rápido para primeros 5 minutos
   
3. **GitHub Contribution Guide** (`handbook/guide-github-contribution.md`)
   - Cómo hacer commit, PR, y merge
   
4. **Release Notes Process** (`devrel/processes/process-release-notes.md`)
   - Cómo documentar cambios para usuarios
   
5. **Campaign Launch Process** (`growth/processes/process-campaign-launch.md`)
   - Flujo para campañas de marketing
   
6. **Glossary** (`shared/glossary.md`)
   - Términos, acrónimos, definiciones

### Adicionales (8 docs)
- Organization Overview
- Handbook Overview & Document Types
- DevRel Overview
- Growth Overview
- UTM Tracking Guide
- Tools & Links
- Changelog

## 🎯 Características clave

✅ **Consistencia**: Todos los docs usan la misma plantilla (frontmatter + estructura)  
✅ **Navegación**: Links entre documentos relacionados  
✅ **Metadata**: Cada doc tiene `department`, `doc_type`, `owner_team`, `keywords`  
✅ **Profesional**: Contenido de calidad, listo para usar  

## 📝 Cómo usar

### Para agregar nuevos documentos:

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
