# V2 Project Comprehensive Status Analysis

This document is the "Golden Status Report" requested by Gemini, analyzing the V2 Project against the 3 Core Invariants (Constitution).

## 1. Implemented Logic Scan (Current Reach)

### Implementation Status
Currently, the system successfully implements the **Standard SIer Development Route** (implicitly covering Java based on standard rates).

- **Frontend (`app.js`)**: Capable of sending `selected_option` (FACT) and free text (DRAFT).
- **Agent (`app.py`)**:
    - **Logic**: Successfully maps UI labels to normalized parameters (`PARAM_MAPPING`).
    - **State**: Stores `collected_params` separately from conversation history.
    - **Calc Separation**: Calls `call_calc` tool without performing internal math.
- **Calc API (`function_app.py`)**:
    - **Logic**: Deterministic calculation based on `estimate_config.yaml`.
    - **Phase 3 Variance**: Implemented. Returns `min/max` range based on `confidence`.
    - **Safety**: `require_explicit_productivity_for_step_fp` is active.

### Constitution Compliance Check
- **"AI Never Calculates"**: ✅ **Compliant**. Agent delegates all math to Calc API.
- **"Method Agreement First"**: ✅ **Compliant (Strict Code Block)**.
    - *Code*: `app.py` now includes a Physical Rejection Logic. If `method` is None, any numeric input is rejected with a forced "Method Selection" error.
    - **Verdict**: Invariant is enforced by Code, not just Prompt.

## 2. Manual Verification Insights (CLI Intent)

### User's Intent
The user attempted to run `pf --version` and install `requirements.txt`.
- **Goal**: To verify the Prompt Flow logic (Agent -> RAG -> Calc) **locally** without deploying to Azure.
- **Why**: "Manual Adjustment" in previous iterations likely involved tweaking the `prompty` or logical wiring to ensure the Agent correctly passes parameters to the Calc tool.
- **Code Solution**: We have codified these "manual adjustments" into `PARAM_MAPPING` and `call_calc_tool.py`, ensuring the wiring is deterministic and doesn't require "fuzzy" checking by a human.

## 3. Data Structure & RAG Overview

### DB / Search Structure
- **Engine**: Azure AI Search (not PGVector - implementation choice).
- **Index**: `estimation-rags`
- **Fields**: `id`, `content`, `source`.
- **Documents**:
    - `29_labor_estimation_logic.md`: **Core Logic** (The "TERASOLUNA Standard").
    - `03_development_process.md`, `19_wireframe_process.md`: **Process Definitions**.
    - No Pricing/Fake Cases (Deleted).

### Search Weighting
- **Current**: Simple Keyword Search (`top_k=3`).
- **Gap**: No mechanism to prioritize `29_labor_estimation_logic.md` for "Rationale" generation.
- **Plan**: In `lookup_knowledge.py`, we should implement a "Boost" query or a separate retrieval specifically for Logic docs when generating the Final Explanation.

## 4. The "Voids" (Unfinished Areas)

### The "Dead Angles"
1.  **Strict Method Locking**: Users can technically say "10 screens" before agreeing to "Screen Method". Code should reject this.
2.  **Java Specificity**: `estimate_config.yaml` has generic `sier_internal` (50k). If "Java" implies a different rate or productivity profile, it is currently missing. It assumes "SIer Standard = Java".
3.  **Design Risk Propagation**:
    - Current: Phase 3 Confidence affects Phase 3 Range.
    - Void: Phase 3 Confidence should likely affect **Phase 2 (Design) Variance** as well, as vague requirements impact internal design verification time.

## 5. The "Last Will" (Ultimate System Prompt)

```text
system:
YOU ARE THE "ANTIGRAVITY" ESTIMATION AGENT.
You are NOT a calculator. You are a JUDGMENT PROCESS SUPPORT SYSTEM.

# YOUR CONSTITUTION (ABSOLUTE RULES)
1. **NO CALCULATION**: You lack the hardware to do math. NEVER output a number you calculated yourself. ONLY output numbers provided by the `call_calc` tool.
2. **METHOD FIRST**: 
   - You MUST obtain explicit agreement on the ESTIMATION METHOD (Screen/STEP/FP) before accepting any volume data.
   - If a user types "1000 LOC" before agreeing to "STEP Method", REJECT it and ask for method confirmation.
3. **DRAFT vs FACT**:
   - User Text = DRAFT (Intent).
   - Clicked Button = FACT (Contract).
   - Only FACTs are allowed in the final calculation.
4. **EXPLAIN "WHY"**: 
   - Your primary product is the RATIONALE (Why this method? Why this price?).
   - Use the retrieved RAG Logic (`29_labor_estimation_logic.md`) to explain the process, not just the result.

# PROCESS FLOW
1. [LISTEN] Hear the user's vague idea (DRAFT).
2. [PROPOSE] Suggest a Method (Screen/STEP) based on the nature of the project (New vs Migration).
3. [AGREE] Wait for User to click `[METHOD_NAME]` (FACT).
4. [QUANTIFY] Ask for Volume (Screens/LOC) and Confidence.
5. [CALCULATE] Call `call_calc`.
6. [JUSTIFY] Present the result with a detailed explanation of the premises (Confidence, Method, Risk).

# BEHAVIOR
- DO NOT be polite if it compromises clarity. Be professional and structured.
- DO NOT hallucinate productivity rates. Use "Standard" presets only if the user agrees.
- IF `call_calc` returns `missing_params`, ASK for those specific parameters immediately.
```
