# Development Roadmap

**Last Updated:** 2025-12-29
**Project Timeline:** 16 weeks (8 sprints × 2 weeks)
**Methodology:** Scrum with PDCA cycle integration

---

## Overview

This roadmap defines the phased delivery approach for Backcast EVS backend.
Detailed breakdown of stories and tasks are located in the individual Sprint files.

**See Also:**
- [Epics and User Stories](epics.md) - Detailed epic/story breakdown

---

## Phase 1: Foundation (Sprints 1-2) ✅ COMPLETE

- [Sprint 1: Infrastructure Setup](sprints/sprint-01.md)
- [Sprint 2: Core Infrastructure & User Management](sprints/sprint-02.md)

---

## Phase 2: Versioning System (Sprints 3-4) 📋 PLANNED

- [Sprint 3: EVCS Core Implementation](sprints/sprint-03.md)
- [Sprint 4: Time-Travel & History Queries](sprints/sprint-04.md)

---

## Phase 3: Core Entities (Sprints 5-6) 📋 PLANNED

- [Sprint 5: Project & WBE Management](sprints/sprint-05.md)
- [Sprint 6: Cost Elements & Financial Structure](sprints/sprint-06.md)

---

## Phase 4: Advanced Features (Sprints 7-8) 📋 PLANNED

- [Sprint 7: Branching & Change Orders](sprints/sprint-07.md)
- [Sprint 8: EVM Calculations & Baselines](sprints/sprint-08.md)

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

## Future Enhancements (Icebox)

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
