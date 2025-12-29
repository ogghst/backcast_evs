# Sprint 5: Project & WBE Management

**Goal:** Implement hierarchical project structure
**Status:** Planned
**Story Points:** 25

**Stories:**
- [ ] E04-U01: Create projects with metadata
- [ ] E04-U02: Create WBEs within projects (track individual machines)
- [ ] E04-U06: Maintain project-WBE-cost element hierarchy integrity
- [ ] E04-U07: Tree view of project structure

**Tasks:**
- [ ] **S05-T01:** Implement Project CRUD with versioning
- [ ] **S05-T02:** Implement WBE CRUD with versioning
- [ ] **S05-T03:** Implement Hierarchical relationship integrity logic
- [ ] **S05-T04:** Create API endpoints: /projects/*, /wbes/*

**Data Models:**
- Project (head + version, non-branching)
- WBE (head + version, branch-enabled)
- One-to-many: Project → WBEs
