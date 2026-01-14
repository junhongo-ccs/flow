# Repository Guidelines

## Constitution (Authoritative Rules)
This document is the binding constitution for the `flow` repository. When in doubt, treat `README_orchestration_minimum.md` and `ARCHITECTURE_ESTIMATION_SNAPSHOT.md` as the primary sources of truth.

## Runtime Clarification (CRITICAL)
- Antigravity is an IDE / agent-coding tool only. It is not a runtime AI and does not participate in execution.
- Runtime components are limited to:
  - Azure OpenAI (Agent / Reasoning)
  - Azure Functions (Calc API / deterministic calculation)
  - Chat UI (free text + option selection)

## TERASOLUNA Invariants (MUST NOT CHANGE)
- Estimation flow is: Judgment → Agreement → Calculation → Explanation → Evidence.
- Free text input is always DRAFT.
- Only UI-selected options (`selected_option`) are FACT.
- Calc API must never infer, guess, or default missing parameters.
- Missing required parameters must return a hard error (HTTP 400).
- All estimation results must be stored as immutable snapshots.

## Role Boundaries (NON-NEGOTIABLE)
- Agent (LLM): propose methods, map intent to options, request confirmation, explain results.
- Calc API: accept confirmed FACTs only and calculate deterministically.
- Codex: review and generate code/docs only; never assume runtime behavior.

## Codex Behavior Constraints
- Do not refactor, simplify, or optimize unless explicitly requested.
- Primary task is verifying consistency between documentation and implementation.

## Repository Scope & Structure
- This repo contains the Agent/Reasoning component (`estimation_agent/`) plus tests (`tests/`) and documentation (`docs/`).
- Related runtime components live in other repos (UI and Calc API); do not modify their behavior assumptions here.

## Implementation Ground Truth
- Runtime wiring, ports, and contract rules are defined in `README_orchestration_minimum.md`.
- Architecture, state machine, and snapshot definitions are defined in `ARCHITECTURE_ESTIMATION_SNAPSHOT.md`.
