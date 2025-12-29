# Sprint 4: Time-Travel & History Queries

**Goal:** Enable historical queries and version navigation
**Status:** Planned
**Story Points:** 24

**Stories:**
- [ ] E03-U04: Entity history viewing
- [ ] E03-U05: Time-travel queries (query state at any past date)
- [ ] E03-U07: Automatic filtering to active/latest versions

**Tasks:**
- [ ] **S04-T01:** Implement Time-travel query support (`get_entity_at_date`)
- [ ] **S04-T02:** Create Version history endpoints
- [ ] **S04-T03:** Add Time machine date context in API
- [ ] **S04-T04:** Write Historical query tests

**Features:**
- Query entity state at any past timestamp
- Range queries on `valid_from` / `valid_to`
- Support for deleted entities in history
