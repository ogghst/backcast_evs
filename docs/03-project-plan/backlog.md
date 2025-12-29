# Project Backlog

**Last Updated:** 2025-12-29  
**Next Review:** 2025-01-15

---

## Current Sprint (Sprint 2)

**Goal:** Complete Story 2.1 quality improvements, prepare for Story 2.2  
**Duration:** 2025-12-27 to 2025-01-10

**Stories:**
- [x] Story 2.1: User Management - COMPLETED
- [ ] Story 2.2: Department Management - Planned (starts 2025-01-10)

---

## Epic Breakdown

### Epic 1: Foundation & Infrastructure ✅ COMPLETE
**Business Value:** Establish robust technical foundation  
**Status:** Complete  
**Duration:** Sprints 1-2

**Completed Stories:**
- [x] Development environment configuration
- [x] Database migrations (Alembic async)
- [x] Async database sessions (SQLAlchemy 2.0)
- [x] Authentication/authorization (JWT)
- [x] CI/CD pipeline (GitHub Actions)

---

### Epic 2: Core Entity Management (Non-Versioned) 🔵 IN PROGRESS
**Business Value:** Enable basic CRUD operations for foundational entities  
**Status:** Story 2.1 complete, Story 2.2 planned
**Duration:** Sprints 2-3

**Stories:**
- [x] **Story 2.1:** User CRUD with repository pattern, Pydantic schemas, comprehensive tests
- [ ] **Story 2.2:** Department CRUD
- [ ] User roles and permissions management
- [ ] Complete test coverage for all CRUD operations

**Acceptance Criteria:**
- All entities have CRUD endpoints
- 80%+ test coverage (unit + integration)
- MyPy strict mode passing
- OpenAPI documentation complete

---

### Epic 3: Entity Versioning System (EVCS Core) 📋 PLANNED
**Business Value:** Implement Git-like versioning for complete audit trails  
**Priority:** CRITICAL  
**Estimated Duration:** Sprints 3-5

**User Stories:**
1. Composite primary key support `(id, branch)`
2. Version tables with immutable snapshots
3. Versioning helper functions (create/update/delete)
4. Entity history viewing
5. Time-travel queries (query state at any past date)
6. Generic VersionedRepository for reusability
7. Automatic filtering to active/latest versions

**Technical Requirements:**
- `VersionableHeadMixin` and `VersionSnapshotMixin`
- Type-safe repository with generics
- Helpers: `create_entity_with_version`, `update_entity_with_version`, `soft_delete_entity`

---

### Epic 4: Project Structure Management 📋 PLANNED
**Business Value:** Enable hierarchical project organization  
**Priority:** HIGH  
**Estimated Duration:** Sprints 4-6

**User Stories:**
1. Create projects with metadata
2. Create WBEs within projects (track individual machines)
3. Create cost elements within WBEs (departmental budgets)
4. Allocate revenue across WBEs
5. Allocate budgets to cost elements
6. Maintain project-WBE-cost element hierarchy integrity
7. Tree view of project structure

**Data Model:**
- Project (head + version tables)
- WBE (head + version tables, branch-enabled)
- CostElement (head + version tables, branch-enabled)

---

### Epic 5: Financial Data Management 📋 PLANNED
**Business Value:** Track costs, forecasts, and earned value  
**Priority:** HIGH  
**Estimated Duration:** Sprints 5-7

**User Stories:**
1. Register actual costs against cost elements
2. Create/update forecasts (EAC)
3. Record earned value (% complete)
4. Define schedule baselines with progression types (linear/gaussian/logarithmic)
5. Validate cost registrations against budgets
6. View cost history and trends
7. Manage quality events (track rework costs)

**Features:**
- Cost registration with validation
- Forecast wizard (max 3 forecasts per cost element)
- Earned value recording
- Schedule baseline versioning

---

### Epic 6: Branching & Change Order Management 📋 PLANNED
**Business Value:** Enable isolated change order development  
**Priority:** CRITICAL  
**Estimated Duration:** Sprints 6-8

**User Stories:**
1. Create change orders
2. Automatic branch creation for change orders (`co-{id}`)
3. Modify entities in branch (isolated from main)
4. Compare branch to main (impact analysis)
5. Merge approved change orders
6. Lock/unlock branches
7. Merged view showing main + branch changes
8. Delete/archive branches

**Operations:**
- Deep copy on branch creation
- Branch comparison with financial impact
- Atomic merge (all-or-nothing)
- Conflict detection

---

### Epic 7: Baseline Management 📋 PLANNED
**Business Value:** Capture project snapshots at key milestones  
**Priority:** MEDIUM  
**Estimated Duration:** Sprints 7-8

**User Stories:**
1. Create baselines at milestones (kickoff, BOM release, commissioning, etc.)
2. Snapshot all cost element data immutably
3. Compare current state to any baseline
4. Mark baselines as PMB (Performance Measurement Baseline)
5. Cancel baselines (corrections)
6. Preserve baseline schedule registrations

**Milestones:**
- Project kickoff, BOM release, engineering completion
- Procurement completion, manufacturing start, shipment
- Site arrival, commissioning start/completion, closeout

---

### Epic 8: EVM Calculations & Reporting 📋 PLANNED
**Business Value:** Standard EVM metrics and analytics  
**Priority:** HIGH  
**Estimated Duration:** Sprints 7-8

**User Stories:**
1. Calculate PV using schedule baselines
2. Calculate EV from % complete
3. Calculate AC from cost registrations
4. View performance indices (CPI/SPI/TCPI)
5. View variances (CV/SV/VAC)
6. Generate cost performance reports
7. Generate variance analysis reports
8. Time machine control for historical metrics

**Calculations:**
- Core metrics: PV, EV, AC, BAC, EAC, ETC
- Performance indices: CPI, SPI, TCPI
- Variances: CV, SV, VAC
- Compliance: ANSI/EIA-748 standards

---

## Completed Work

See `iterations/` folder for completed PDCA cycles and detailed history.

**Sprint 1:**
- ✅ Story 1.1: Infrastructure Setup
- ✅ Story 1.2: Database Architecture
- ✅ Story 1.3: Authentication System
- ✅ Story 1.4: CI/CD Pipeline

**Sprint 2:**
- ✅ Story 2.1: User Management

---

## Story Point Reference

| Points | Complexity | Time Estimate | Example |
|--------|------------|---------------|---------|
| 1 | Trivial | 1-2 hours | Add validation rule |
| 2 | Simple | 2-4 hours | Add new field |
| 3 | Easy | 4-8 hours | Simple CRUD endpoint |
| 5 | Medium | 1-2 days | Complex endpoint |
| 8 | Complex | 2-4 days | New entity with versioning |
| 13 | Very Complex | 4-6 days | Branch merge implementation |
| 21 | Epic | 1-2 weeks | Complete versioning system |

---

## Technical Debt

See [Technical Debt Register](../02-architecture/technical-debt.md)

**High Priority:**
- None currently

**Medium Priority:**
- Improve UserService test coverage (currently 74%)
- Add refresh token support for authentication

**Low Priority:**
- Consider connection pool optimization

---

## Future Enhancements

**Infrastructure:**
- [ ] Automated performance testing
- [ ] Load testing framework
- [ ] Observability (metrics, tracing)

**Security:**
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 integration (Google, GitHub)
- [ ] API key management

**Developer Experience:**
- [ ] Automated API client generation
- [ ] Development environment automation
- [ ] Enhanced CI/CD pipeline

**ERP Integration:**
- [ ] Automated cost data import
- [ ] Project scheduling tool integration
- [ ] Multi-currency support
- [ ] Resource management (labor hours, materials)
- [ ] Risk management integration
- [ ] Portfolio-level analytics

---

## Completed Work

See `iterations/` folder for completed PDCA cycles and detailed history.

**Sprint 1:**
- ✅ Story 1.1: Infrastructure Setup
- ✅ Story 1.2: Database Architecture
- ✅ Story 1.3: Authentication System
- ✅ Story 1.4: CI/CD Pipeline

**Sprint 2:**
- ✅ Story 2.1: User Management
