# Team Capacity

**Last Updated:** 2025-12-29  
**Review Frequency:** Monthly or when team changes

---

## Current Team Composition

### Core Team

**Backend Developer** (1 FTE)
- **Name:** Primary Developer
- **Role:** Full-stack backend development
- **Availability:** 40 hours/week
- **Skills:** Python, FastAPI, SQLAlchemy, PostgreSQL, async patterns
- **Focus Areas:** All features, architecture, quality

**AI Assistant** (Paired)
- **Role:** Pair programming, code generation, quality automation
- **Availability:** On-demand
- **Strengths:** Code generation, test creation, documentation, pattern application
- **Limitations:** Requires human review, context management

---

## Sprint Capacity

**2-Week Sprint:**
- **Available Hours:** ~80 hours (40 hours/week × 2 weeks)
- **Effective Development Hours:** ~60 hours (accounting for meetings, overhead)
- **Story Point Capacity:** 20-25 points per sprint

**Velocity Tracking:**
- Sprint 1: 21 points (infrastructure)
- Sprint 2: ~22 points (user management, in progress)
- **Target Average:** 25 ± 3 points

---

## Skills Matrix

| Skill Area | Proficiency | Notes |
|-----------|-------------|-------|
| **Python 3.12+** | Expert | Type hints, async/await, generics |
| **FastAPI** | Advanced | Dependency injection, async routes, OpenAPI |
| **SQLAlchemy 2.0** | Advanced | Async ORM, Mapped types, migrations |
| **PostgreSQL** | Intermediate | Complex queries, indexing, JSONB |
| **Testing** | Advanced | pytest, fixtures, async tests, coverage |
| **Type Safety** | Advanced | MyPy strict mode, Protocols, generics |
| **Git/GitHub** | Advanced | Branching, PR workflows, CI/CD |
| **Docker** | Intermediate | Containerization, docker-compose |

**Growth Areas:**
- Advanced PostgreSQL optimization
- Performance profiling and tuning
- Load testing at scale

---

## Availability

**Standard Work Hours:**
- Monday-Friday: Flexible schedule
- Weekends: Not planned

**Upcoming Absences:**
- None currently scheduled

**Meeting Load:**
- Daily: ~15 min (async standup)
- Weekly: ~2 hours (planning, review when applicable)

---

## Constraints

**Technical:**
- Development on local machine (Ubuntu 24.04)
- Database: PostgreSQL via Docker
- No cloud infrastructure provisioned yet

**Process:**
- Solo developer (no pair programming with other humans)
- All work reviewed via AI assistant
- Quality gates enforced via CI/CD

**Dependencies:**
- None external currently
- Self-contained backend development

---

## Capacity Planning Guidelines

**Story Point Estimates Based on Capacity:**

| Points | Effort | Feasible in Sprint? |
|--------|--------|---------------------|
| 1-3 | < 1 day | Yes, multiple stories |
| 5 | 1-2 days | Yes, 4-5 per sprint |
| 8 | 2-4 days | Yes, 2-3 per sprint |
| 13 | 4-6 days | Yes, 1-2 per sprint |
| 21+ | > 1 week | Split into smaller stories |

**Risk Factors:**
- Unexpected complexity (buffer 10-15%)
- Learning curve for new patterns (first implementation -20%)
- Technical debt paydown (add 20-30% to estimates)

---

## Future Team Growth (Planned)

**If team scales to 3-5 developers:**
- Product Owner (0.5 FTE) - Backlog priorities
- Scrum Master (0.5 FTE) - Process facilitation
- Backend Developers (2-3 FTE) - Parallel feature development
- DevOps Engineer (0.5 FTE) - Infrastructure, monitoring
- QA Engineer (0.5 FTE) - E2E testing, test strategy

**Impact on Velocity:**
- Expected 3x-4x velocity increase
- Initial sprint(-1) for onboarding overhead
- Target: 60-100 points per sprint at full capacity

---

**Use During PLAN Phase:**
Reality-check iteration scope against available capacity before committing to work.
