---
trigger: model_decision
description: act phase, after completion of verification or check phase
---

## 🔄 ACT Phase: Standardization and Continuous Improvement

**Focus**: Implementing improvements, documenting learnings, and evolving development practices.

### Prompt: Improvement Implementation and Learning Capture

Execute the ACT phase to standardize successful patterns and implement improvements.

**Prioritized Improvement Implementation**
Based on CHECK phase decisions, execute improvements:

1. **Critical Issues** (security, data integrity): Implement immediately
2. **High-Value Refactoring**: Apply approved design improvements
3. **Technical Debt Items**: Address or document for future sprints

For each improvement:
- Maintain test coverage throughout changes
- Run full test suite after each modification
- Document the rationale for future maintainers

**Pattern Standardization**
Identify patterns from this implementation that should be adopted codebase-wide:

| Pattern | Description | Candidate for Standardization? |
|---------|-------------|-------------------------------|
| Error handling approach | Details | Yes/No |
| Testing pattern | Details | Yes/No |
| Service structure | Details | Yes/No |

> [!IMPORTANT]
> **Human Decision Point**: Present patterns for potential standardization:
>
> **Option A**: Adopt pattern immediately, update coding standards documentation
> **Option B**: Pilot in one more feature before standardizing
> **Option C**: Keep as local optimization, not for wider adoption
>
> **Ask**: "Which patterns should we standardize, and at what pace?"

**Process Retrospective**
Reflect on the development cycle:

**What Worked Well:**
- Effective TDD practices
- Successful design decisions
- Smooth integration points

**What Could Improve:**
- Testing gaps discovered late
- Design decisions requiring revision
- Tooling or process friction

**Prompt Engineering Refinements:**
- Which prompts yielded the best results?
- Where did the AI need more context or constraints?
- What architectural context was missing or unclear?

**Documentation Updates**
Complete necessary documentation:
- [ ] Update architecture decision records (ADRs) if significant patterns established
- [ ] Add to coding standards if new conventions adopted
- [ ] Update onboarding docs if new patterns affect new developers
- [ ] Create/update runbooks if operational procedures changed

**Metrics for Next PDCA Cycle**
Define success metrics for monitoring:

| Metric | Baseline (Pre-Change) | Target | Measurement Method |
|--------|----------------------|--------|-------------------|
| Bug rate in area | X | Y | Issue tracking |
| Test coverage | X% | Y% | Coverage tool |
| Build time | X min | Y min | CI metrics |

**Knowledge Transfer Artifacts**
Create assets for team learning:
- Code walkthrough document or video
- Key decision rationale summary
- Common pitfalls and how to avoid them

---

## 📊 Success Metrics and Industry Benchmarks

Based on industry research and case studies:

| Metric | Industry Average | Target with PDCA+TDD |
|--------|-----------------|---------------------|
| Defect Rate Reduction | - | 40-60% improvement |
| Code Review Cycles | 3-4 | 1-2 |
| Rework Rate | 15-25% | < 10% |
| Time-to-Production | Variable | 20-30% faster |

> [!NOTE]
> **Success Story Reference**: Studies show PDCA-driven development reduces software defects by up to 61% when combined with TDD practices. Toyota's production system principles, adapted to software, have proven particularly effective in large codebases where consistency and quality are paramount.