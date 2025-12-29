# Sprint 7: Branching & Change Orders

**Goal:** Implement branch isolation and change order workflow
**Status:** Planned
**Story Points:** 28

**Stories:**
- [ ] E06-U01: Create change orders
- [ ] E06-U02: Automatic branch creation for change orders (`co-{id}`)
- [ ] E06-U03: Modify entities in branch (isolated from main)
- [ ] E06-U04: Compare branch to main (impact analysis)
- [ ] E06-U05: Merge approved change orders
- [ ] E06-U06: Lock/unlock branches
- [ ] E06-U07: Merged view showing main + branch changes
- [ ] E06-U08: Delete/archive branches

**Tasks:**
- [ ] **S07-T01:** Implement Branch creation and management
- [ ] **S07-T02:** Create Change order workflow
- [ ] **S07-T03:** Create Branch comparison endpoints
- [ ] **S07-T04:** Implement Merge functionality

**Features:**
- Deep copy on branch creation (`co-{short_id}`)
- Branch comparison with financial impact analysis
- Atomic merge operation
- Branch locking mechanism
