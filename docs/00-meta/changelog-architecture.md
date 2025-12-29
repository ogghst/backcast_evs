# Architecture Changelog

**Purpose:** Track significant changes to the architecture over time.

---

## 2025-12-29: Documentation Restructuring

**Changes:**
- Migrated from monolithic docs to bounded-context structure
- Created separate folders for product scope, architecture, project plan
- Established cross-cutting concerns documentation
- Created context-specific architecture docs (auth, user-management)
- Unified PDCA prompts from two sources

**Rationale:**
- Combat context rot in growing codebase
- Enable AI-friendly documentation consumption
- Separate concerns clearly (what/why/how/when)

**Impact:**
- Easier to find relevant information
- Reduced cognitive load per document
- Better support for LLM context management

---

## 2025-12-28: Coding Standards Established

**Changes:**
- Created formal coding standards document
- Standardized schema mapping pattern (factory methods)
- Documented Ruff and MyPy configuration
- Established 80% test coverage minimum

**Rationale:**
- Prevent pattern divergence as team grows
- Reduce code review friction
- Make expectations explicit

**Impact:**
- Faster onboarding for new developers
- Consistent code style across codebase

---

## 2025-12-27: Technology Stack Finalized

**Changes:**
- Selected FastAPI + SQLAlchemy 2.0 + PostgreSQL
- Adopted Python 3.12 for advanced type hints
- Committed to Argon2 for password hashing
- Chose composite PK pattern for versioning

**Rationale:**
- See ADR-001 (Technology Stack)
- See ADR-002 (Versioning Pattern)

**Impact:**
- Foundation for all subsequent development
- Type safety enables refactoring confidence

---

## Template for Future Entries

### YYYY-MM-DD: [Change Description]

**Changes:**
- Bullet list of what changed

**Rationale:**
- Why this change was made

**Impact:**
- How it affects the system or team

---

## Review Schedule

Review this changelog quarterly to identify trends and patterns in architectural evolution.
