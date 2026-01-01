# ADR Index

**Last Updated:** 2026-01-01

This index lists all Architecture Decision Records (ADRs) in chronological order.

---

## Active ADRs

### ADR-001: Technology Stack Selection

**Date:** 2025-12-27  
**Status:** ✅ Accepted  
**Summary:** Chose FastAPI, SQLAlchemy 2.0, PostgreSQL, Python 3.12  
**Link:** [ADR-001](ADR-001-technology-stack.md)

### ADR-002: Entity Versioning Pattern

**Date:** 2025-12-27  
**Status:** ⚠️ Superseded by ADR-005  
**Summary:** Original dual-table versioning pattern  
**Link:** [ADR-002](ADR-002-entity-versioning-pattern.md)

### ADR-005: Bitemporal Versioning Pattern

**Date:** 2026-01-01  
**Status:** ✅ Accepted  
**Summary:** Single-table bitemporal versioning with PostgreSQL TSTZRANGE, generic commands/services  
**Link:** [ADR-005](ADR-005-bitemporal-versioning.md)

### ADR-003: Command Pattern for Write Operations

**Date:** 2025-12-28  
**Status:** ✅ Accepted  
**Summary:** Implement Command pattern for Create/Update/Delete with undo support  
**Link:** [ADR-003](ADR-003-command-pattern.md)

### ADR-004: Code Quality Standards

**Date:** 2025-12-27  
**Status:** ✅ Accepted  
**Summary:** Strict MyPy mode, 80% test coverage minimum, Ruff linting  
**Link:** [ADR-004](ADR-004-quality-standards.md)

---

## Superseded ADRs

- **ADR-002:** Superseded by ADR-005 (2026-01-01) - Replaced dual-table pattern with bitemporal single-table

---

## Deprecated ADRs

_None yet_

---

## Creating New ADRs

### Template

Use this structure for new ADRs:

```markdown
# ADR-NNN: [Title]

## Status

[Proposed | Accepted | Superseded by ADR-XXX | Deprecated]

## Context

What is the issue we're facing that motivates this decision?

## Decision

What decision did we make?

## Consequences

What are the positive and negative consequences of this decision?

## Alternatives Considered

What other options were evaluated?

## Notes

Additional information, links, or future review dates
```

### Numbering

- Sequential: ADR-001, ADR-002, ADR-003...
- Never reuse numbers
- Gaps okay if ADRs deleted before acceptance

### Process

1. Draft ADR with "Proposed" status
2. Review with team
3. Update status to "Accepted" when consensus reached
4. Link from this index
