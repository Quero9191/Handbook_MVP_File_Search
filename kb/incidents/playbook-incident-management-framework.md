---
title: "Incident Management Framework"
description: "Complete playbook for identifying, declaring, and resolving production incidents with clear escalation paths"
department: "incidents"
doc_type: "playbook"
owner_team: "Incident Response Team"
maintainer: "Engineering Lead"
visibility: "internal"
keywords: ["incident", "escalation", "war-room", "postmortem", "severity-levels", "response"]
last_updated: "2025-12-17"
---

## Purpose
This playbook defines how we respond to production incidents, from detection through resolution and post-incident review. It ensures consistent communication, minimizes MTTR (Mean Time To Recovery), and helps teams learn from incidents.

## Scope
- Applies to: All production incidents affecting customer-facing systems, internal tools affecting 2+ teams
- Doesn't apply to: Local development issues, pre-production environments, security vulnerabilities (use security runbook instead)

## Steps / Content

### 1. Incident Classification
- **SEV-1 (Critical)**: Complete service outage, data loss risk, customer impact (many users affected)
- **SEV-2 (High)**: Degraded performance, partial feature unavailable, moderate customer impact
- **SEV-3 (Medium)**: Minor issues, workarounds available, limited impact
- **SEV-4 (Low)**: Non-urgent bugs, nice-to-have fixes

### 2. Detection & Declaration
- Anyone can declare an incident in `#incidents` Slack channel with format: `@incident SEV-X: brief description`
- On-call engineer gets paged automatically (Incident Commander role assigned)
- War room Zoom link auto-created and pinned in Slack thread

### 3. Incident Response Roles
- **Incident Commander (IC)**: Owns timeline, decisions, communication cadence
- **Lead Engineer**: Technical investigation and remediation
- **Communicator**: Updates stakeholders every 15 min (SEV-1/2), coordinates messaging
- **Scribe**: Documents decisions, times, actions in shared doc

### 4. Investigation & Mitigation
1. Establish war room and confirm participants
2. Define symptoms: What broke? Who's affected? When did it start?
3. Start root cause analysis (don't stop at first cause)
4. Attempt mitigation while investigating (rollback, feature flag flip, db failover)
5. Escalate to vendor support if needed
6. Communicate progress every 15 min

### 5. Resolution & All-Clear
- Once service restored, confirm with monitoring/metrics (no customer errors increasing)
- IC calls "all-clear" in Slack
- Schedule postmortem within 48 hours

## Notes / Gotchas
- **Don't blame individuals** in war room—focus on systems and processes
- **Don't end war room early**—confirm resolution with multiple people
- **Incident fatigue is real**—if incidents spike, escalate to leadership for process review

## Related
- [Checklist: Incident Triage](checklist-incident-triage.md)
- [Glossary: Severity Levels](../shared/glossary.md#severity-levels)
