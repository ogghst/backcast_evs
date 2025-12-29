# Sprint 3: EVCS Core Implementation

**Goal:** Implement entity versioning system foundation
**Status:** Planned
**Story Points:** 26

**Stories:**
- [ ] E03-U01: Composite primary key support `(id, branch)`
- [ ] E03-U02: Version tables with immutable snapshots
- [ ] E03-U03: Versioning helper functions (create/update/delete)
- [ ] E03-U06: Generic VersionedRepository for reusability

**Tasks:**
- [ ] **S03-T01:** Implement `VersionableHeadMixin` and `VersionSnapshotMixin`
- [ ] **S03-T02:** Create Generic repository with MyPy validation
- [ ] **S03-T03:** Implement Helper functions for all lifecycle operations
- [ ] **S03-T04:** Write Comprehensive versioning tests

**Technical Focus:**
- Composite PK pattern: `(id, branch)` for heads, `(head_id, valid_from)` for versions
- Type-safe generic repository
- Create/update/soft delete/restore/hard delete operations
