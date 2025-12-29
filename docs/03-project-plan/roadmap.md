# Development Roadmap

**Last Updated:** 2025-12-29  
**Project Timeline:** 16 weeks (8 sprints × 2 weeks)  
**Methodology:** Scrum with PDCA cycle integration

---

## Overview

This roadmap defines the phased delivery approach for Backcast EVS backend, organizing work into 4 major phases across 8 epics.

**See Also:**
- [Project Backlog](backlog.md) - Detailed epic/story breakdown
- [Current Iteration](current-iteration.md) - Active sprint status

---

## Phase 1: Foundation (Sprints 1-2) ✅ COMPLETE

### Sprint 1: Infrastructure Setup ✅
**Goal:** Establish development environment and core infrastructure  
**Story Points:** 21

**Deliverables:**
- [x] Working dev environment with all tools configured (uv, ruff, mypy, pytest)
- [x] Database connection and Alembic migration system
- [x] Basic auth endpoints (/login, /register, JWT)
- [x] CI pipeline running on every PR (lint, type-check, test)

---

### Sprint 2: Core Infrastructure & User Management ✅
**Goal:** Complete foundation and implement user management  
**Story Points:** 23

**Deliverables:**
- [x] User management endpoints (/users/*)
- [x] Department management endpoints (/departments/*) - PLANNED
- [x] 80%+ test coverage
- [x] Interactive API docs at /docs

**Status:** Story 2.1 complete (User Management), Story 2.2 planned (Departments)

---

## Phase 2: Versioning System (Sprints 3-4) 📋 PLANNED

### Sprint 3: EVCS Core Implementation
**Goal:** Implement entity versioning system foundation  
**Story Points:** 26

**Deliverables:**
- [ ] Reusable versioning mixins (`VersionableHeadMixin`, `VersionSnapshotMixin`)
- [ ] Generic repository with MyPy validation
- [ ] Helper functions for all lifecycle operations
- [ ] Comprehensive versioning tests

**Technical Focus:**
- Composite PK pattern: `(id, branch)` for heads, `(head_id, valid_from)` for versions
- Type-safe generic repository
- Create/update/soft delete/restore/hard delete operations

---

### Sprint 4: Time-Travel & History Queries
**Goal:** Enable historical queries and version navigation  
**Story Points:** 24

**Deliverables:**
- [ ] Time-travel query support (`get_entity_at_date`)
- [ ] Version history endpoints
- [ ] Time machine date context in API
- [ ] Historical query tests

**Features:**
- Query entity state at any past timestamp
- Range queries on `valid_from` / `valid_to`
- Support for deleted entities in history

---

## Phase 3: Core Entities (Sprints 5-6) 📋 PLANNED

### Sprint 5: Project & WBE Management
**Goal:** Implement hierarchical project structure  
**Story Points:** 25

**Deliverables:**
- [ ] Project CRUD with versioning
- [ ] WBE CRUD with versioning
- [ ] Hierarchical relationship integrity
- [ ] API endpoints: /projects/*, /wbes/*

**Data Models:**
- Project (head + version, non-branching)
- WBE (head + version, branch-enabled)
- One-to-many: Project → WBEs

---

### Sprint 6: Cost Elements & Financial Structure
**Goal:** Complete project hierarchy and enable budget allocation  
**Story Points:** 26

**Deliverables:**
- [ ] Cost element CRUD with versioning
- [ ] Budget allocation endpoints
- [ ] Revenue allocation logic
- [ ] Budget validation rules

**Business Logic:**
- Total WBE budgets ≤ project budget
- Cost element budgets ≤ WBE allocation
- Revenue allocations reconcile to contract value

---

## Phase 4: Advanced Features (Sprints 7-8) 📋 PLANNED

### Sprint 7: Branching & Change Orders
**Goal:** Implement branch isolation and change order workflow  
**Story Points:** 28

**Deliverables:**
- [ ] Branch creation and management
- [ ] Change order workflow
- [ ] Branch comparison endpoints
- [ ] Merge functionality

**Features:**
- Deep copy on branch creation (`co-{short_id}`)
- Branch comparison with financial impact analysis
- Atomic merge operation
- Branch locking mechanism

---

### Sprint 8: EVM Calculations & Baselines
**Goal:** Enable EVM reporting and baseline management  
**Story Points:** 27

**Deliverables:**
- [ ] Baseline management endpoints
- [ ] EVM calculation service
- [ ] Schedule baseline logic
- [ ] Performance reports

**Calculations:**
- PV (Planned Value) using schedule baselines + progression types
- EV (Earned Value) from % complete
- AC (Actual Cost) from cost registrations
- CPI, SPI, TCPI, CV, SV, VAC

---

## Success Criteria

### End of Sprint 2 ✅ ACHIEVED
- [x] Foundation complete and stable
- [x] Team velocity established
- [x] CI/CD pipeline operational

### End of Sprint 4 (Target)
- [ ] Versioning system fully functional
- [ ] Time-travel queries working
- [ ] 80%+ test coverage achieved

### End of Sprint 6 (Target)
- [ ] Complete project hierarchy implemented
- [ ] Budget allocation working
- [ ] All core entities versioned

### End of Sprint 8 (Target)
- [ ] Branching and merging operational
- [ ] EVM calculations accurate
- [ ] System ready for production deployment

---

## Quality Gates

Each sprint must meet:
- **Code Quality:** MyPy strict mode passing, zero Ruff errors
- **Test Coverage:** ≥ 80% (unit + integration)
- **Documentation:** All endpoints in OpenAPI spec
- **Performance:** API response < 200ms (p95)
- **Review:** All PRs reviewed and approved

---

## Risk Mitigation

### Technical Risks

**Versioning complexity → performance issues**
- Mitigation: Proper indexes on `(head_id, branch, valid_from)`
- Use EXPLAIN ANALYZE for query optimization
- Add caching layer for frequently accessed data

**MyPy strict mode blocking development**
- Mitigation: Type hint training and templates
- Sparing use of `# type: ignore` with justification

**Branch merge conflicts**
- Mitigation: Pessimistic locking during merge
- Merge preview before commit
- Conflict detection logic

**Database migration failures**
- Mitigation: Test on staging first, maintain rollback scripts
- Database backups before migrations

### Process Risks

**Scope creep**
- Mitigation: Strict backlog prioritization, PO approval for new features

**Team velocity uncertainty**
- Mitigation: Track velocity over first 2 sprints, adjust commitments

**Testing debt accumulation**
- Mitigation: Tests required in Definition of Done, coverage gates in CI

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p95) | < 200ms | Application monitoring |
| Database Query Time (p95) | < 100ms | Query logging |
| Time-Travel Query (p95) | < 500ms | Performance tests |
| Branch Merge Time | < 5 seconds | Integration tests |
| Test Coverage | ≥ 85% | Automated coverage reports |
| MyPy Compliance | 100% strict | CI pipeline check |
| Build Success Rate | > 95% | CI pipeline analytics |

---

## Definition of Done

A user story is done when:
- [ ] Code is written and peer-reviewed
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests passing
- [ ] MyPy strict mode passing
- [ ] API documentation updated
- [ ] Code merged to main branch
- [ ] Deployed to staging environment
- [ ] Product owner acceptance obtained

---

## Sprint Ceremonies

**2-Week Sprint Cadence:**
- **Monday Week 1:** Sprint Planning (4 hours)
- **Daily:** Standup (15 minutes, 9:00 AM)
- **Wednesday Week 1:** Backlog Refinement (2 hours)
- **Friday Week 2:** Sprint Review/Demo (2 hours)
- **Friday Week 2:** Sprint Retrospective (1.5 hours)

**PDCA Integration:**
- **PLAN:** Sprint Planning + backlog refinement
- **DO:** Daily standup + implementation
- **CHECK:** Sprint Review + quality assessment
- **ACT:** Sprint Retrospective + process improvements

---

## Velocity Tracking

| Sprint | Committed Points | Completed Points | Velocity | Notes |
|--------|------------------|------------------|----------|-------|
| 1 | 21 | 21 | 21 | Infrastructure setup completed |
| 2 | 23 | 23 (estimated) | ~22 | User management (2.1 complete, 2.2 partial) |
| 3 | 26 | TBD | TBD | EVCS core |
| 4 | 24 | TBD | TBD | Time-travel queries |
| 5 | 25 | TBD | TBD | Projects & WBEs |
| 6 | 26 | TBD | TBD | Cost elements |
| 7 | 28 | TBD | TBD | Branching |
| 8 | 27 | TBD | TBD | EVM & baselines |

**Average Target Velocity:** 25 ± 3 story points

---

**Project Motto:** *"Type-safe, test-driven, incrementally delivered."*
