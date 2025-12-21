---
---
title: "GitHub Contribution Guide"
description: "How to create branches, submit PRs, request reviews, and merge code following team standards"

doc_type: "guide"
owner: "@engineering"

last_review: "2025-12-21"
review_cycle_days: 90
---

## Purpose
This guide ensures consistent code quality, clear PR history, and smooth collaboration on GitHub. Everyone should follow this process.

## Scope
- Applies to: All code changes in main repos (backend, frontend, infra)
- Doesn't apply to: Documentation-only changes (can skip some steps), hotfixes (expedited review)

## Steps / Content

### 1. Create a Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/short-description
# or: bugfix/issue-number  |  refactor/component-name
```

**Naming convention**: `type/description` (lowercase, hyphens, <50 chars)

### 2. Make Commits
- Atomic commits: one logical change per commit
- Clear messages: `[component] short description` (72 chars max)
- Example: `[auth] add JWT token refresh logic`

```bash
git commit -m "[auth] add JWT token refresh logic"
```

### 3. Push & Open PR
```bash
git push origin feature/short-description
```

Then open PR on GitHub with:
- **Title**: Same as your last commit (clear + concise)
- **Description**: Use PR template (auto-filled):
  - What changed? Why?
  - Issue/ticket link (if applicable)
  - Tested on: (device/browser/environment)
  - Screenshots (if UI changes)

### 4. Request Reviews
- Tag reviewers: 1–2 team members (not yourself)
- Add labels: `bug`, `feature`, `documentation`, `needs-review`
- Request review from `@team-name` for visibility

### 5. Address Review Comments
- Reply to each comment (don't just commit without explanation)
- Update branch with changes
- Mark as "Resolved" after addressing
- Request re-review

### 6. Merge
- **Squash commits** if >3 commits (keep history clean)
- **Use PR title as commit message** when merging to main
- Delete branch after merge
- Link issue as closed: `Closes #123` in PR description

## Notes / Gotchas
- **Don't force-push to main**—ever
- **Don't merge your own PRs**—wait for 1+ approval
- **Draft PRs are OK**—mark as "Draft" if WIP
- **Rebase when main moves far ahead** (to avoid merge conflicts)

## Related
- [Handbook: Code Review Standards](handbook-document-types.md#code-review)
- [Tools: GitHub Setup](../shared/tools-and-links.md#github)
