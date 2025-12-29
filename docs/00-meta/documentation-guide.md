# Documentation Guide

**Last Updated:** 2025-12-29

## Philosophy

Our documentation follows a **bounded context** approach to minimize context rot. Instead of one massive architecture document, we separate concerns into focused, self-contained documents.

**Guiding Principles:**
1. **Clear Boundaries:** Product scope, architecture, and project tracking are separate
2. **Findability:** Use this guide to locate information quickly
3. **Staleness Indicators:** Each doc shows last-updated date
4. **Immutable Decisions:** ADRs capture decisions at a point in time

---

## Finding Information

### "What should the system do?"
→ **Product Scope** (`docs/01-product-scope/`)
- High-level vision and business goals
- User requirements and acceptance criteria
- Functional specifications

### "How is it built?"
→ **Architecture** (`docs/02-architecture/`)
- System overview and technology choices
- Bounded context details (auth, user-management, etc.)
- Cross-cutting concerns (database, API, security)
- Architecture Decision Records (why we chose X over Y)

### "What's happening now?"
→ **Project Plan** (`docs/03-project-plan/`)
- Current iteration status and goals
- Project backlog and priorities
- Historical iteration records (PDCA cycles)

### "How do I work with AI?"
→ **PDCA Prompts** (`docs/04-pdca-prompts/`)
- Plan phase: Iteration planning, option generation
- Do phase: TDD implementation, daily tracking
- Check phase: Quality assessment
- Act phase: Standardization, learning capture

---

## Documentation Structure

```
docs/
├── 00-meta/               # This guide, changelog, maintenance records
├── 01-product-scope/      # Business requirements (the "what" and "why")
├── 02-architecture/       # Technical design (the "how")
│   ├── 00-system-map.md
│   ├── 01-bounded-contexts.md
│   ├── contexts/          # Per-context documentation
│   ├── cross-cutting/     # Shared concerns (DB, API, security)
│   └── decisions/         # ADRs
├── 03-project-plan/       # Execution tracking (the "when" and "now")
│   ├── current-iteration.md
│   ├── backlog.md
│   └── iterations/        # Historical PDCA records
└── 04-pdca-prompts/       # AI collaboration templates
```

---

## Maintenance Responsibilities

### Who Updates What?

**Product Owner:**
- `01-product-scope/` documents
- `current-iteration.md` goals

**Tech Lead:**
- `02-architecture/` documents
- ADRs for significant decisions

**Development Team:**
- Context-specific architecture docs
- PDCA iteration records during sprints
- Update docs when changing patterns

**All:**
- Keep `current-iteration.md` updated daily

---

## Update Workflow

### When Making Code Changes

1. **Before:** Check relevant architecture docs for current patterns
2. **During:** Note any pattern deviations in DO phase log
3. **After:** Update architecture docs if new pattern standardized (ACT phase)

### Quarterly Documentation Audit

Every 3 months, review all docs:
1. Update "Last Updated" dates
2. Remove or archive obsolete content
3. Identify gaps or missing context
4. Update `00-meta/changelog-architecture.md`

Record audit in `00-meta/last-audit.md`

---

## Writing Guidelines

### Document Title Format
```markdown
# Document Title

**Last Updated:** YYYY-MM-DD  
**Status:** Active | Deprecated | Superseded by [link]  
**Owner:** Team or role name
```

### Link to Code
Use file:// links for code references:
```markdown
See [`app/services/user.py`](file:///absolute/path/to/file.py)
```

### Keep It Concise
- One page per concern when possible
- Link to details rather than duplicating
- Use diagrams for complex relationships

### Date All Decisions
ADRs and significant changes must include dates to provide historical context.

---

## Documentation Debt

Like technical debt, documentation debt accumulates. Track it in:
- `02-architecture/technical-debt.md` (code-related)
- `00-meta/documentation-debt.md` (docs needing updates)

---

## Questions?

If you can't find what you need:
1. Check the [System Map](../02-architecture/00-system-map.md)
2. Search for keywords in all markdown files
3. Ask in team chat or create an issue

**Maintain this guide:** Update when you add new documentation patterns or structures.
