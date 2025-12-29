# Backcast EVS Documentation

**Last Updated:** 2025-12-29  
**Status:** Active Development - Sprint 2

## Quick Start

- **New to the project?** Start with [Vision](../01-product-scope/vision.md)
- **Need architecture overview?** Read [System Map](../02-architecture/00-system-map.md)
- **Working on current iteration?** Check [Current Iteration](../03-project-plan/current-iteration.md)
- **Looking for specific context?** See [Bounded Contexts](../02-architecture/01-bounded-contexts.md)

## Documentation Structure

This documentation follows a structure designed to minimize context rot through three clear pillars:

### Product Scope (The "What" and "Why")
[01-product-scope/](../01-product-scope/)
- Vision and business goals
- User stories and requirements
- Acceptance criteria templates

### Architecture (The "How")
[02-architecture/](../02-architecture/)
- System overview and bounded contexts
- Per-context documentation (auth, user-management, etc.)
- Cross-cutting concerns (database, API conventions, security)
- Architecture Decision Records (ADRs)
- Technical debt tracking

### Project Plan (The "When" and "Now")
[03-project-plan/](../03-project-plan/)
- Current iteration status
- Backlog and team capacity
- Historical PDCA iteration records

### PDCA Prompts (Process Automation)
[04-pdca-prompts/](../04-pdca-prompts/)
- Standardized prompts for AI collaboration
- Meta-prompt for iteration planning
- Plan/Do/Check/Act templates

## Documentation Maintenance

-  **Before Each Iteration:** Update `current-iteration.md` with new plans
- **During Work:** Log decisions in `iterations/{name}/02-do.md`
- **After Completion:** Record learnings in CHECK and ACT documents
- **Quarterly:** Full documentation audit (see `last-audit.md`)

## Contact & Ownership

- **Product Owner:** [TBD]
- **Tech Lead:** [TBD]
- **Documentation Maintainer:** Development Team

## Recent Changes

See [changelog-architecture.md](changelog-architecture.md) for architectural evolution timeline.
