# Database Strategy

**Last Updated:** 2025-12-29

## ORM and Database Layer

### Technology Stack
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0 (async mode)
- **Driver:** asyncpg
- **Migration Tool:** Alembic (async template)

### Design Principles

**Async-First:**
All database operations use `AsyncSession` and `await` pattern for optimal concurrency.

**Type Safety:**
- SQLAlchemy 2.0 `Mapped[]` type hints for all columns
- Strict MyPy validation of all repository code
- Explicit return type annotations on all repository methods

---

## Connection Management

### Session Factory

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
```

### Session Lifecycle

**Dependency Injection Pattern:**
Sessions provided via FastAPI dependency, automatically committed/rolled back:

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

---

## Transaction Patterns

### Implicit Transactions
Most operations use implicit transactions via dependency injection.

### Explicit Transactions
For complex operations requiring atomicity:

```python
async with session.begin():
    # All operations in this block are atomic
    await repo.create_entity(data1)
    await repo.update_entity(data2)
    # Commits on context exit, rolls back on exception
```

---

## Migration Strategy

### Alembic Configuration

**Auto-generation:**
- Run `alembic revision --autogenerate -m "description"`
- Always review generated migration before applying
- Test on copy of production data when possible

**Versioning:**
- Sequential numbered migrations
- Never edit applied migrations (create new ones)
- Maintain both `upgrade()` and `downgrade()` paths

**Best Practices:**
- Use batch operations for large table changes
- Add indexes in separate migrations from table creation
- Test data migrations with prod-like data volumes

---

## Query Patterns

### Standard Queries

**Select with filters:**
```python
stmt = select(Model).where(Model.field == value)
result = await session.execute(stmt)
entities = result.scalars().all()
```

**Join queries:**
```python
stmt = (
    select(Parent)
    .join(Child)
    .where(Child.status == "active")
    .options(selectinload(Parent.children))
)
```

### Performance Optimization

**Eager Loading:**
Use `selectinload()` or `joinedload()` to avoid N+1 queries:
```python
stmt = select(User).options(
    selectinload(User.versions),
    selectinload(User.department),
)
```

**Pagination:**
Always limit queries that could return many rows:
```python
stmt = select(Model).limit(100).offset(skip)
```

---

## Indexing Strategy

### Required Indexes

**Version Tables:**
- `(head_id, valid_from)` - Time travel queries
- `(head_id, branch)` - Branch filtering
- `valid_to` - Active version filtering

**Standard Tables:**
- Primary keys (automatic)
- Foreign keys for joins
- Fields used in WHERE clauses frequently

### Index Monitoring
- Review slow query logs monthly
- Use `EXPLAIN ANALYZE` for query optimization
- Add indexes based on actual usage patterns

---

## Data Integrity

### Constraints

**Foreign Keys:**
- Always define FK relationships
- Use `ondelete` appropriately ("CASCADE", "SET NULL", "RESTRICT")

**Check Constraints:**
- Enforce business rules at DB level where possible
- Example: `CHECK (valid_from < valid_to OR valid_to IS NULL)`

**Unique Constraints:**
- Composite primary keys for versioned entities
- Unique indexes for natural keys (email, etc.)

---

## Backup and Recovery

### Backup Strategy
- Automated daily backups (PostgreSQL pg_dump)
- Point-in-time recovery enabled (WAL archiving)
- Test restore procedure quarterly

### Disaster Recovery
- RTO (Recovery Time Objective): < 1 hour
- RPO (Recovery Point Objective): < 15 minutes
- Documented restoration procedure in ops runbook

---

## Database Versioning (EVCS Pattern)

See [EVCS Architecture](../contexts/evcs-core/architecture.md) for details on:
- Composite primary key pattern
- Version table structure
- Time-travel query implementation
- Branch isolation mechanisms
