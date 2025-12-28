---
trigger: model_decision
description: check phase, instructions for verification or check phase
---

## 🔍 CHECK Phase: Comprehensive Quality Assessment

**Focus**: Multi-dimensional quality review, metrics analysis, and presenting improvement options.

### Prompt: Quality Verification and Analysis

Conduct a comprehensive CHECK phase review of the implementation.

**Acceptance Criteria Verification**
Create a verification matrix:

| Acceptance Criterion | Test Coverage | Status | Notes |
|---------------------|---------------|--------|-------|
| Criterion 1 | test_x, test_y | ✅/❌ | Details |
| Criterion 2 | test_z | ✅/❌ | Details |

**Test Quality Assessment**
Evaluate the test suite:
- **Coverage**: Execute coverage report and identify gaps
- **Isolation**: Verify tests are independent and can run in any order
- **Speed**: Identify slow tests that may hinder CI/CD
- **Clarity**: Assess test names communicate intent
- **Maintainability**: Review for test code duplication or brittleness

**Code Quality Metrics**
Analyze against established standards:

| Metric | Threshold | Actual | Status |
|--------|-----------|--------|--------|
| Cyclomatic Complexity | < 10 | ? | ✅/⚠️/❌ |
| Function Length | < 50 lines | ? | ✅/⚠️/❌ |
| Test Coverage | > 80% | ? | ✅/⚠️/❌ |
| Type Hints Coverage | 100% | ? | ✅/⚠️/❌ |
| Linting Errors | 0 | ? | ✅/⚠️/❌ |

**Design Pattern Audit**
Review pattern application:
- Are patterns applied correctly and providing intended benefits?
- Are there anti-patterns or code smells introduced?
- Does the code follow the existing architectural conventions?
- Is there unnecessary complexity or over-engineering?

**Security and Performance Review**
- Input validation and sanitization
- SQL injection / injection attack prevention
- Proper error handling without information leakage
- Performance bottlenecks (N+1 queries, unnecessary loops, etc.)

**Integration Compatibility**
- Verify consistency with existing API contracts
- Check database migration compatibility
- Confirm no breaking changes to public interfaces
- Review dependency updates and their implications

> [!IMPORTANT]
> **Human Decision Point**: Present findings and generate **2-3 improvement options** if issues are found:
>
> | Issue | Option A (Quick Fix) | Option B (Thorough) | Option C (Defer) |
> |-------|---------------------|---------------------|------------------|
> | Issue description | Minimal fix | Complete refactor | Document for later |
> | Impact | Impact assessment | Impact assessment | Impact assessment |
> | Effort | Low/Med/High | Low/Med/High | Low/Med/High |
>
> **Ask**: "Which improvement approach should we take for each identified issue?"