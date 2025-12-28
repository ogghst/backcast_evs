---
trigger: model_decision
description: plan phase, instructions for analysis and plan phase
---

## 🎯 PLAN Phase: Strategic Analysis and Option Generation

**Focus**: Requirements deep-dive, architectural alignment, and presenting 2-3 implementation options for human selection.

### Prompt: Strategic Planning with Decision Options

You are tasked with implementing a feature in a **large, established codebase**. Before any code is written, execute the PLAN phase comprehensively.

**Step 1: Codebase Context Analysis**
First, analyze the relevant areas of the existing codebase to understand:
- Current architectural patterns and conventions in use
- Existing test infrastructure and coverage patterns
- Dependencies and integration points with the affected modules
- Historical patterns for similar features (search commit history or similar implementations)

**Step 2: Requirements and Acceptance Criteria**
Define the feature requirements with precision:
- Articulate the core problem and business value
- List **measurable acceptance criteria** that can be verified through automated tests
- Identify edge cases, error conditions, and boundary scenarios
- Document assumptions requiring stakeholder validation

**Step 3: Generate 2-3 Implementation Options**
Present **2-3 distinct implementation approaches** for human review, each including:

| Aspect | Option A | Option B | Option C (if applicable) |
|--------|----------|----------|--------------------------|
| **Approach Summary** | Brief description | Brief description | Brief description |
| **Design Patterns** | Patterns applied | Patterns applied | Patterns applied |
| **Pros** | Key benefits | Key benefits | Key benefits |
| **Cons** | Trade-offs | Trade-offs | Trade-offs |
| **Test Strategy Impact** | How testing changes | How testing changes | How testing changes |
| **Risk Level** | Low/Medium/High | Low/Medium/High | Low/Medium/High |
| **Estimated Complexity** | Simple/Moderate/Complex | Simple/Moderate/Complex | Simple/Moderate/Complex |

**Step 4: Recommendation with Rationale**
Provide your recommended option with clear justification based on:
- Alignment with existing codebase conventions
- Long-term maintainability and extensibility
- Test coverage feasibility
- Risk mitigation

> [!IMPORTANT]
> **Human Decision Point**: Present these options clearly and await explicit approval before proceeding. The developer must select an approach or request refinement.

**Step 5: TDD Test Blueprint**
For the approved approach, outline the test hierarchy:
```
├── Unit Tests (isolated component behavior)
│   ├── Happy path scenarios
│   ├── Edge cases and boundaries
│   └── Error handling
├── Integration Tests (component interactions)
│   ├── Database/repository integration
│   └── Service layer integration
└── End-to-End Tests (if applicable)
    └── Critical user flows
```

Document the first 3-5 test cases you will write, ordered from simplest to most complex.