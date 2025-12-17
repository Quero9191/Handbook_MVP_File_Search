---
title: "Incident Triage Checklist"
description: "Quick reference checklist for Incident Commanders during initial incident response"
department: "incidents"
doc_type: "checklist"
owner_team: "Incident Response Team"
maintainer: "Engineering Lead"
visibility: "internal"
keywords: ["incident", "triage", "checklist", "response", "war-room"]
last_updated: "2025-12-17"
---

## Purpose
Quick reference to ensure no step is missed in the first 5 minutes of an incident. Use this alongside the Incident Management Framework.

## Scope
- Applies to: All SEV-1, SEV-2 incidents
- Doesn't apply to: SEV-3/4, security incidents (use security triage instead)

## Triage Checklist

- [ ] **Incident declared** with severity level and brief description
- [ ] **War room established** (Zoom link shared in Slack)
- [ ] **IC assigned** (on-call engineer or manager)
- [ ] **Initial participants joined**: IC, Lead Engineer, Communicator
- [ ] **Scribe assigned** (someone documenting in shared doc)
- [ ] **Symptoms confirmed**:
  - [ ] What service/component is down?
  - [ ] What's the user-facing impact?
  - [ ] How many users affected?
  - [ ] Started when? (exact time in UTC)
- [ ] **Monitoring/Logs checked**: Dashboards reviewed, error rates confirmed
- [ ] **Communication started**:
  - [ ] #incidents Slack thread active
  - [ ] StatusPage updated (if external incident)
  - [ ] Stakeholders notified
- [ ] **Runbooks consulted**: Have we seen this before?
- [ ] **Rollback/Mitigation plan identified**: What's our first move?
- [ ] **Timeline started**: Document every action with timestamp

## Notes / Gotchas
- **Don't spend >2 min investigating**—focus on quick fixes (rollback, feature flags) first
- **Communicate early, even with uncertainty**—silence causes panic
- **IC sets cadence**—if not heard from in 10 min, assume meeting is stale

## Related
- [Playbook: Incident Management Framework](playbook-incident-management-framework.md)
- [Tools: War Room Setup](../shared/tools-and-links.md#war-room-tools)
