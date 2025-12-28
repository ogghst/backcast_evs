---
trigger: model_decision
description: do phase,instructions for implement or execute phase
---

## 🔨 DO Phase: TDD Implementation with Incremental Verification

**Focus**: Red-Green-Refactor cycles, incremental complexity, and checkpoint-based progress with human review opportunities.

### Prompt: Test-Driven Implementation Cycle

Execute the approved implementation plan using strict TDD methodology. Work in small, verifiable increments.

**Red-Green-Refactor Cycle Protocol**

For each piece of functionality:

**🔴 RED: Write a Failing Test**
1. Write a single, well-named test capturing the **simplest** required behavior
2. Follow the Arrange-Act-Assert (AAA) pattern:
   ```python
   def test_[feature]_[scenario]_[expected_outcome](self):
       # Arrange: Set up preconditions
       # Act: Execute the behavior under test
       # Assert: Verify the expected outcome
   ```
3. Run the test to confirm it fails **for the expected reason**
4. Document why this test matters for the acceptance criteria

**🟢 GREEN: Minimal Passing Implementation**
1. Write the **minimum code** necessary to make the test pass
2. Resist adding functionality not required by current tests
3. Keep the implementation intentionally simple—even "ugly" code is acceptable at this stage
4. Run all tests to confirm the new test passes and no regressions occurred

**🔵 REFACTOR: Improve Design While Staying Green**
1. Examine the production code for improvement opportunities:
   - Extract methods for readability
   - Rename variables/functions for clarity
   - Apply appropriate design patterns (Strategy, Factory, Repository, etc.)
   - Ensure adherence to SOLID principles
2. Run tests after **each small change** to maintain green status
3. Document significant refactoring decisions

**Implementation Checkpoints**

After completing each logical component (3-5 test cycles):

> [!IMPORTANT]
> **Human Review Checkpoint**: Pause and present:
> - Tests written and their purpose
> - Code coverage of the current increment
> - Any design decisions or trade-offs made
> - Identified concerns or alternative approaches discovered
>
> **Ask**: "Should I continue with the current approach, or would you like to adjust direction?"

**Large Codebase Considerations**
- Maintain consistent patterns with existing code (naming, error handling, logging)
- Use existing utilities and helpers rather than creating duplicates
- Ensure new code integrates cleanly with dependency injection patterns
- Follow established module boundaries and layering

**Incremental Complexity Strategy**
1. Start with the core happy path
2. Add error handling and validation
3. Integrate with existing services/repositories
4. Add edge cases and boundary conditions
5. Implement cross-cutting concerns (logging, metrics, caching)