# Review Comments for TERASOLUNA-AI Estimation System V2

> **Source**: Architecture Review (2026-01-14)
> **Status**: Accepted & Invariant

## Overall Assessment
This V2 plan correctly treats the estimation system not as a calculator, but as a **Judgment Process Support System** aligned with the TERASOLUNA standard.
The design consistently enforces the TERASOLUNA core sequence:
`Judgment → Agreement → Calculation → Explanation → Evidence`

## Key Architectural Principles (Must Be Preserved)

### 1. Method First, Numbers Later (TERASOLUNA Core)
The system explicitly prevents users from entering quantitative values (Screen count / LOC / FP) before agreeing on the estimation method.
- **Rationale**: Estimation failure most often originates from method ambiguity, not calculation error.
- **Constraint**: If a user attempts to input numbers before method agreement, the system should **explicitly reject the input** and guide the user back to method selection.

### 2. Premise Agreement Is Not Optional (Vendor Mixed)
Vendor involvement is treated as a premise uncertainty, not merely a cost fluctuation.
- **Constraint**: Confidence is recorded in the Snapshot as an estimation premise. Cost variance is derived strictly from this agreed premise.

### 3. Explanation Responsibility Is a First-Class Output
Explanation is part of the deliverable, not a by-product.
The system must generate text explaining:
- "Why STEP was selected"
- "Why the estimate has a ±40% range"

### 4. Snapshot = Evidence, Not Just Storage
Snapshots are treated as non-repudiable evidence.
- Immutable parameter set (FACTs only)
- Deterministic calculation result
- Versioned schema (v1 / v2)

## Role Boundaries (Critical for AI Behavior)

### Agent (LLM / Azure OpenAI)
- **MUST**: Analyze context, Propose methods, Translate text to FACTs, Request confirmation.
- **MUST NOT**: Decide numeric values, Infer productivity, Calculate.

### Calc API (Code)
- **MUST**: Accept confirmed FACTs only, Apply formulas deterministically.
- **MUST NOT**: Interpret natural language, Guess missing parameters.

## Final Evaluation
**This system does not teach TERASOLUNA to AI. It forces AI to operate inside TERASOLUNA.**
As long as these invariants are preserved, future extensions will not compromise estimation integrity.
