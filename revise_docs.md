# Documentation Structure for Context Rot Minimization

```
docs/
│
├── 00-meta/
│   ├── README.md
│   ├── documentation-guide.md
│   ├── changelog-architecture.md
│   └── last-audit.md
│
├── 01-product-scope/
│   ├── vision.md
│   ├── user-stories-active.md
│   ├── user-stories-completed.md
│   ├── requirements-functional.md
│   ├── requirements-non-functional.md
│   └── acceptance-criteria-templates.md
│
├── 02-architecture/
│   ├── 00-system-map.md
│   ├── 01-bounded-contexts.md
│   │
│   ├── contexts/
│   │   ├── auth/
│   │   │   ├── architecture.md
│   │   │   ├── data-models.md
│   │   │   ├── api-contracts.md
│   │   │   └── code-locations.md
│   │   │
│   │   ├── user-management/
│   │   │   ├── architecture.md
│   │   │   └── ...
│   │   │
│   │   └── [other-contexts]/
│   │
│   ├── cross-cutting/
│   │   ├── database-strategy.md
│   │   ├── api-conventions.md
│   │   ├── error-handling.md
│   │   ├── security-practices.md
│   │   └── performance-standards.md
│   │
│   ├── decisions/
│   │   ├── ADR-001-technology-stack.md
│   │   ├── ADR-002-state-management.md
│   │   ├── ADR-023-session-auth.md
│   │   └── adr-index.md
│   │
│   └── technical-debt.md
│
├── 03-project-plan/
│   ├── current-iteration.md
│   ├── backlog.md
│   ├── team-capacity.md
│   │
│   └── iterations/
│       ├── 2025-12-auth-system/
│       │   ├── 01-plan.md
│       │   ├── 02-do.md
│       │   ├── 03-check.md
│       │   └── 04-act.md
│       │
│       └── iteration-index.md
│
├── 04-pdca-prompts/
│   ├── meta-prompt.md
│   ├── plan-prompt.md
│   ├── do-prompt.md
│   ├── check-prompt.md
│   ├── act-prompt.md
│   └── prompt-changelog.md
│
└── 05-automation/
    ├── check-staleness.py
    ├── generate-context-summary.py
    ├── verify-code-links.py
    └── architecture-tests/
        ├── test_auth_constraints.py
        ├── test_api_conventions.py
        └── ...
```

---

## Folder & Document Goals Summary

### `00-meta/` - Documentation About Documentation
**Goal:** Centralized metadata and audit trails to prevent documentation from becoming an unmaintained afterthought.

- **`README.md`** - Entry point for all documentation. Quick links to most important docs, navigation guide, "start here" for new team members and LLMs.

- **`documentation-guide.md`** - How to write and maintain documentation. Style guide, when to update docs, who owns what, contribution workflow.

- **`changelog-architecture.md`** - Timeline of architectural changes. Tracks when major system changes occurred and which docs were affected. Critical for understanding when documentation might have diverged from reality.

- **`last-audit.md`** - Records last full documentation audit date, what was reviewed, what was fixed. Creates accountability and visibility into documentation health.

---

### `01-product-scope/` - The "What" and "Why"
**Goal:** Single source of truth for product requirements, decoupled from implementation details to prevent scope creep into technical docs.

- **`vision.md`** - High-level product vision, business goals, target users, value proposition. Changes rarely; provides context for all decisions. (~500 words)

- **`user-stories-active.md`** - Currently prioritized user stories waiting for implementation. Actively maintained, reviewed during meta-prompt analysis to identify next iteration.

- **`user-stories-completed.md`** - Archived user stories. Moved here after implementation. Useful for understanding product evolution but not actively consulted. Prevents active docs from bloating.

- **`requirements-functional.md`** - Specific functional requirements (features, behaviors, capabilities). Organized by feature area. Updated when product scope changes.

- **`requirements-non-functional.md`** - Performance, security, scalability, compliance requirements. These often drive architectural decisions and PDCA iterations focused on technical improvements.

- **`acceptance-criteria-templates.md`** - Reusable templates for defining "done" across different types of work. Ensures consistency in PLAN phase success criteria.

---

### `02-architecture/` - The "How It's Built"
**Goal:** Minimize context rot through bounded contexts, immutable decision records, and clear ownership.

#### Root Level

- **`00-system-map.md`** - Compressed 1000-word overview of entire system. High-level components, how they interact, technology choices. First doc an LLM reads during meta-prompt. **Critical for context window management.**

- **`01-bounded-contexts.md`** - Defines the bounded contexts used to partition the system. Lists each context, its responsibility, owner, and which code directories it covers. **Navigation document that prevents context overlap.**

#### `contexts/` - Bounded Context Documentation

**Goal:** Each subdirectory is a self-contained architectural unit that can be loaded independently into LLM context.

**Per-context structure:**

- **`architecture.md`** - How this bounded context works. Component diagram, data flow, key patterns, integration points. Should be understandable without reading other contexts. **Core technical reference.**

- **`data-models.md`** - Database schemas, data structures, validation rules for this context. Includes examples. Links to actual code locations.

- **`api-contracts.md`** - API endpoints, request/response formats, authentication requirements specific to this context. **Contract documentation that must stay synchronized with OpenAPI specs or actual code.**

- **`code-locations.md`** - Maps architectural concepts to actual files. "The UserSession class described above is in `backend/services/auth/session.py`". **Bridges documentation to code, critical for preventing drift.**

#### `cross-cutting/` - System-Wide Patterns

**Goal:** Document patterns that apply across all bounded contexts without repeating them everywhere.

- **`database-strategy.md`** - ORM choice, migration strategy, connection pooling, transaction patterns. Applied universally.

- **`api-conventions.md`** - REST patterns, versioning, pagination, filtering, sorting standards. Every new API endpoint should follow these.

- **`error-handling.md`** - Error response formats, logging strategies, exception handling patterns. Referenced by all contexts.

- **`security-practices.md`** - Authentication flow, authorization patterns, input validation, CORS policies, secret management.

- **`performance-standards.md`** - Response time targets, caching strategies, database query optimization guidelines, frontend bundle size limits.

#### `decisions/` - Architecture Decision Records (ADRs)

**Goal:** Immutable historical record of significant decisions. Prevents "why did we do this?" questions and documents context that would otherwise be lost.

- **`ADR-NNN-title.md`** - Individual ADRs following standard template (context, decision, consequences, alternatives considered, review date). Numbered sequentially, never edited after acceptance (only status changes).

- **`adr-index.md`** - Chronological list of all ADRs with current status (accepted, superseded, deprecated). Quick reference for finding relevant decisions.

#### Root Level (continued)

- **`technical-debt.md`** - Known shortcuts, hacky solutions, areas needing refactoring. Each item includes: description, why it exists, impact, estimated effort to fix. **Feeds into PDCA iteration planning.**

---

### `03-project-plan/` - The "What We're Doing Now"
**Goal:** Track current work and iteration history without mixing planning docs with permanent architecture docs.

- **`current-iteration.md`** - What's being worked on right now. Goals, timeline, who's involved, daily status. **Most frequently updated document.** Overwritten at start of each iteration.

- **`backlog.md`** - Prioritized list of next iterations. Each item: brief description, business value, effort estimate, prerequisites. **Input for meta-prompt analysis.**

- **`team-capacity.md`** - Current team composition, availability, skills, constraints. Used during PLAN phase to reality-check iteration scope.

#### `iterations/` - PDCA Iteration History

**Goal:** Preserve learnings from completed iterations without cluttering active planning docs.

**Per-iteration folder structure:**

- **`01-plan.md`** - Frozen snapshot of iteration plan. Problem statement, success criteria, scope, approach, risks, effort estimate. Created using `plan-prompt.md`.

- **`02-do.md`** - Daily implementation log. What was done, decisions made, deviations from plan, blockers. Updated throughout iteration using `do-prompt.md`. **Most valuable document for preventing repeated mistakes.**

- **`03-check.md`** - Evaluation against success criteria. Metrics, qualitative assessment, what worked/didn't work, root cause analysis. Created using `check-prompt.md`.

- **`04-act.md`** - Actions taken based on learnings. Documentation updated, standards changed, technical debt items created, process improvements. Created using `act-prompt.md`. **Ensures learnings feed back into architecture and product docs.**

- **`iteration-index.md`** - Chronological list of all iterations with one-sentence summaries. Quick navigation and pattern recognition tool.

---

### `04-pdca-prompts/` - Standardized LLM Interactions
**Goal:** Consistent, high-quality LLM collaboration through reusable, evolving prompts.

- **`meta-prompt.md`** - Orchestration prompt that analyzes all three documentation pillars to suggest next iteration. Reads product scope for gaps, architecture for technical debt, project plan for momentum. **The "what's next?" prompt that drives continuous improvement.**

- **`plan-prompt.md`** - Structures iteration planning. Ensures all necessary elements (problem statement, success criteria, risks) are defined before starting work. **Creates** `01-plan.md` for new iteration.

- **`do-prompt.md`** - Daily logging template. Prompts for decisions, deviations, blockers. **Updates** `02-do.md` throughout iteration.

- **`check-prompt.md`** - Evaluation framework. Systematic assessment of results vs. expectations. **Creates** `03-check.md` at iteration end.

- **`act-prompt.md`** - Decision framework for applying learnings. Identifies documentation updates, standards changes, next steps. **Creates** `04-act.md` and triggers updates to architecture/product docs.

- **`prompt-changelog.md`** - Tracks evolution of prompts themselves. When you discover a prompt isn't working well, you update it and log the change here. **Meta-documentation about your documentation process.**

---

### `05-automation/` - Scripts to Fight Context Rot
**Goal:** Automated detection of stale documentation and verification of architectural constraints.

- **`check-staleness.py`** - Compares file modification dates between code and docs. Flags bounded context docs that haven't been updated while their corresponding code changed significantly. Generates report of potentially stale docs. **Run weekly, creates GitHub issues.**

- **`generate-context-summary.py`** - Generates compressed summaries for LLM consumption. Reads all bounded context `_metadata.yml` files and creates lightweight index. Optionally generates different compression levels (200 words, 1000 words, full detail). **Enables efficient context window usage.**

- **`verify-code-links.py`** - Parses documentation for references to code files/paths. Verifies those files still exist. Reports broken links. **Catches docs referencing moved/deleted code.**

#### `architecture-tests/` - Executable Architecture Documentation

**Goal:** Tests that fail when implementation diverges from documented architectural constraints.

- **`test_auth_constraints.py`** - Verifies authentication implementation matches architecture docs (e.g., "we use sessions not JWT" per ADR-023).

- **`test_api_conventions.py`** - Checks that actual API endpoints follow documented conventions (error formats, versioning, pagination patterns).

- *Additional tests per bounded context as needed*

**Key principle:** These aren't unit tests of functionality—they're tests that architectural decisions are being followed. When they fail, either the code or the docs need updating.

---

## Document Lifecycle & Ownership

### High-Change Documents (Updated Weekly/Daily)
- `03-project-plan/current-iteration.md`
- `03-project-plan/iterations/CURRENT/02-do.md`
- `03-project-plan/backlog.md`

### Medium-Change Documents (Updated Per Iteration)
- `02-architecture/contexts/*/architecture.md` (when working in that context)
- `02-architecture/technical-debt.md`
- `01-product-scope/user-stories-active.md`

### Low-Change Documents (Updated Quarterly or As Needed)
- `02-architecture/00-system-map.md`
- `02-architecture/cross-cutting/*.md`
- `01-product-scope/vision.md`
- `01-product-scope/requirements-*.md`

### Append-Only Documents (Never Edited, Only Appended)
- `02-architecture/decisions/ADR-*.md` (status field can change)
- `00-meta/changelog-architecture.md`
- `03-project-plan/iterations/*/` (completed iterations are frozen)
- `04-pdca-prompts/prompt-changelog.md`

---

## Critical Success Factors

**1. Bounded Contexts Prevent Overwhelming LLMs**
Each context is small enough (~5-10 pages) to fit comfortably in an LLM context window with room for code and conversation.

**2. Metadata Enables Automation**
The `_metadata.yml` files in each context enable automated staleness detection without requiring AI to interpret prose.

**3. ADRs Preserve Historical Context**
Immutable decision records prevent "why did we do this?" questions that waste time and lead to repeated mistakes.

**4. Separation of Concerns Reduces Redundancy**
Product scope documents "what," architecture documents "how," project plan documents "when/now." Minimal overlap = less synchronization burden.

**5. Iteration History Captures Tacit Knowledge**
The DO phase logs capture decision-making process and context that never makes it into formal docs but is crucial for understanding the system.

**6. Prompts Create Consistent LLM Behavior**
Standardized prompts mean every developer gets similar quality assistance and documentation updates follow predictable patterns.

**7. Automation Scripts Provide Early Warning**
Staleness detection and broken link checking catch documentation drift before it becomes severe enough to mislead developers.

This structure balances completeness with maintainability, making documentation a useful tool rather than a maintenance burden.