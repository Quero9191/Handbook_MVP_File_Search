---
title: "Document Types & Standards"
description: "Guide to different document types we use and how to choose the right format"
department: "handbook"
doc_type: "guide"
owner_team: "Communications"
maintainer: "Communications"
visibility: "internal"
keywords: ["documentation", "standards", "guidelines", "document-types"]
last_updated: "2025-12-17"
---

## Purpose
Ensures consistency across the knowledge base and helps authors know what format fits their content.

## Scope
- Applies to: All new KB documents
- Doesn't apply to: Code comments, commit messages

## Document Types

### Overview
**When to use**: High-level summary of a topic, team, or department
**Structure**: 
- What is this?
- Who's responsible?
- Related docs/links

**Example**: [Organization Overview](../organization/overview.md)

### Playbook
**When to use**: Complex multi-step procedures (incidents, deployments)
**Structure**:
- Purpose & scope
- Step-by-step instructions
- Common mistakes/gotchas
- Related docs

**Example**: [Incident Management Framework](../incidents/playbook-incident-management-framework.md)

### Checklist
**When to use**: Quick reference to verify nothing was missed
**Structure**:
- Checkbox list
- 1–2 sentences per item
- Gotchas section

**Example**: [Incident Triage Checklist](../incidents/checklist-incident-triage.md)

### Guide
**When to use**: How-to instructions for specific tasks
**Structure**:
- Purpose
- Step-by-step (with examples/code)
- Common mistakes
- Related resources

**Example**: [GitHub Contribution Guide](guide-github-contribution.md)

### Process
**When to use**: Repeatable workflow or operational procedure
**Structure**:
- Purpose & scope
- Phases/stages with dates
- Success metrics
- Related docs

**Example**: [Release Notes Process](../devrel/processes/process-release-notes.md)

### Policy
**When to use**: Rules, compliance, or requirements
**Structure**:
- What's required?
- Who does it apply to?
- Consequences of non-compliance
- Exceptions process

**Example**: (Add when needed)

### FAQ
**When to use**: Common questions and quick answers
**Structure**:
- Question
- Answer (1–2 paragraphs max)
- Link to detailed guide if needed

**Example**: [Tools & Links](../shared/tools-and-links.md)

### Glossary
**When to use**: Definitions, acronyms, terminology
**Structure**:
- Term
- Definition (1–3 sentences)
- Context/usage

**Example**: [Company Glossary](../shared/glossary.md)

## Writing Standards

### Frontmatter (Required for All)
```yaml
---
title: "Clear, action-oriented title"
description: "1 sentence: what and why"
department: "incidents | devrel | growth | handbook | organization | shared"
doc_type: "overview | process | playbook | checklist | guide | faq | policy"
owner_team: "Team name"
maintainer: "Person/team name"
visibility: "internal"
keywords: ["term1", "term2"]
last_updated: "YYYY-MM-DD"
---
```

### Content Tips
- **Headings**: Use H2 for main sections, H3 for subsections
- **Lists**: Use bullets for unordered, numbers for sequential
- **Code**: Use markdown backticks for inline, triple backticks for blocks
- **Links**: Link to related docs using [Text](path/to/doc.md)
- **Length**: Keep docs focused—if >2000 words, split into multiple docs

## Related
- [TEMPLATE.md](../TEMPLATE.md) – Copy this for new documents
