---
---
title: "Release Notes Process"
description: "How to document, write, and publish release notes for each sprint"

doc_type: "process"
owner: "@product"

last_review: "2025-12-21"
review_cycle_days: 90
---

## Purpose
Release notes inform customers (and internal teams) of what changed, why it matters, and how to adopt new features. This process ensures notes are accurate, timely, and customer-friendly.

## Scope
- Applies to: All releases (patch, minor, major versions)
- Doesn't apply to: Internal hotfixes, experimental features (not released yet)

## Steps / Content

### 1. Collection Phase (Throughout Sprint)
- **During sprint**: Product & Eng add items to GitHub Discussion "Release Notes - v[X.Y.Z]"
- **Format each item**:
  - Feature name
  - 1-line description
  - Why it matters (customer benefit)
  - Link to docs/issue

Example:
```
### Dark Mode Support
Users can now enable dark mode in Settings > Appearance.
Reduces eye strain and looks great at night. [Docs: Dark Mode](link)
```

### 2. Review Phase (3 days before release)
- DevRel lead reviews all items for clarity & customer impact
- Reorder by importance (features > fixes > improvements)
- Merge similar items
- Add "Breaking Changes" section if applicable

### 3. Writing Phase
- **Structure**:
  - Hero paragraph (1-2 sentences: headline)
  - Feature highlights (3–5 top items with images)
  - Full changelog (bulleted list of all changes)
  - Migration guide (if breaking changes)
  - Thanks (to contributors)
  
- **Tone**: Conversational, customer-focused, avoid jargon

### 4. Distribution
- Publish on website
- Email to subscribers (Mailchimp)
- Post on social media (Twitter, LinkedIn)
- Announce in Slack #announcements
- Update docs site versioning

## Notes / Gotchas
- **Don't ship without notes**—users need to know what changed
- **Don't oversell**—hype kills credibility if feature is small
- **User feedback matters**—link to feedback form in release notes

## Related
- [Changelog: Full History](../../changelog/changelog.md)
- [Tools: Release Workflow](../tools-and-links.md)
