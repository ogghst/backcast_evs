# ADR-002: Entity Versioning Pattern

## Status
✅ Accepted (2025-12-27)

## Context

The Backcast EVS system requires Git-like versioning for entities, including:
- Complete history of all changes
- Time-travel queries to any past state
- Branch isolation for change orders
- Immutable audit trail

We needed to choose how to implement this versioning at the database level.

## Decision

Use **Composite Primary Key** pattern with separate head and version tables:

**Head Table Pattern:**
- `(id, branch)` composite primary key
- Stores stable identity and current state pointers
- Mutable (updated when new version created)

**Version Table Pattern:**
- `(head_id, valid_from)` composite primary key
- Stores complete immutable snapshots
- Temporal validity: `valid_from` to `valid_to`
- Parent version linking via `parent_version_id`

## Consequences

### Positive

- **Simple Time Travel:** Query version table with date range
- **Strong Isolation:** Composite PK naturally partitions by branch
- **Performance:** Index on `(head_id, branch, valid_from)` makes queries fast
- **No Row-Level Locks:** Head and version separate, reducing contention
- **Clear Semantics:** Head = identity, Version = historical state

### Negative

- **Join Overhead:** Combine head + version requires join (mitigated by repository pattern)
- **Storage:** Complete snapshots use more space than deltas (acceptable tradeoff)
- **Migration Complexity:** More complex than single-table design

## Alternatives Considered

### Alternative 1: Single Table with Version Column
```sql
CREATE TABLE entities (
    id UUID,
    version INT,
    ...fields,
    PRIMARY KEY (id, version)
);
```

- **Pros:** Simple, no joins needed
- **Cons:** Can't distinguish current vs historical, harder to query "latest"
- **Rejected:** Difficult to maintain current state pointer

### Alternative 2: Separate Versioning Table (Generic)
```sql
CREATE TABLE entity_versions (
    entity_type VARCHAR,
    entity_id UUID,
    version_data JSONB,
    PRIMARY KEY (entity_type, entity_id, version)
);
```

- **Pros:** One table for all entity types
- **Cons:** Loses type safety, JSONB querying slow, no FK constraints
- **Rejected:** Sacrifices too much type safety and queryability

### Alternative 3: Event Sourcing
Store events, rebuild state by replay.

- **Pros:** Perfect audit trail
- **Cons:** Slow reads, complex queries, difficult time-travel
- **Rejected:** Read performance critical for our use case

## Notes

This pattern is implemented via SQLAlchemy mixins (`VersionableHeadMixin`, `VersionSnapshotMixin`) for reuse across all versioned entities.

The versioning helpers in `app/core/versioning/` encapsulate the complexity, making it easy to add versioning to new entities.

