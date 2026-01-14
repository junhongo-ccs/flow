# Architecture & Estimation Snapshot (2026-01-13)

> **Objective**: To inventory the current implementation status of Phase 1-3, ensuring the project can be expanded without breaking critical "Money" logic.
> **Source of Truth**: logic in `estimate-backend-calc` and strict UI state handling.

## 1. Architecture & Deployment Map

### Overview
The system consists of three decoupled components following the **Strict Separation of Concerns** principle.

| Component | Repository | Role | Deploy Target | Critical Env Vars |
| :--- | :--- | :--- | :--- | :--- |
| **UI** | `estimation-ui-app` | **Presentation**<br>Chat Interface, State Holding, user intent conversion to FACT. | Azure Static Web Apps | `VITE_API_ENDPOINT` (Url to Agent) |
| **Agent** | `flow` | **Reasoning**<br>Context understanding, Mapping ambiguous text to specific Options. | Azure Container Apps | `CALC_API_URL`, `CALC_API_KEY`<br>`AZURE_OPENAI_API_KEY` |
| **Calc API** | `estimate-backend-calc` | **Calculation**<br>Deterministic Money Logic. No guessing. | Azure Functions (Python) | None (Config via `estimate_config.yaml`) |

### Dependency Graph
```mermaid
graph LR
    User[User / Browsers] -- HTTPS --> UI[Static Web App (UI)]
    UI -- JSON (Chat) --> Agent[Container App (Agent)]
    Agent -- JSON (Calc Params) --> Calc[Azure Function (Calc API)]
    Calc -- JSON (Result) --> Agent
```

---

## 2. Contract Spec (Agent -> Calc API)

**Strict Rule**: The Agent **MUST** collect these parameters before calling the API. The API will **ERROR** (400) if mandatory fields are missing.

### Endpoint: `/calculate_estimate` (POST)

### Request Schema (Canonicalized Params)

| Field | Type | Required | Description / Constraints |
| :--- | :--- | :--- | :--- |
| `method` | String | **Yes** | `screen` (Default), `step`, `fp` |
| `screen_count` | Integer | **Yes** | Default: `10`. Base unit for 'screen' method. |
| `complexity` | String | **Yes** | `low`, `medium` (Default), `high` |
| `features` | Array[Str] | No | **Phase 1 Items**. See Feature Map below. |
| `phase2_items` | Array[Str] | No | **Phase 2 (Design)**. See Design Map below. |
| `phase3_items` | Array[Str] | No | **Phase 3 (Vendor)**. See Vendor Map below. |
| `confidence` | String | **Conditional** | **MANDATORY** if `phase3_items` exists. `low`, `medium`, `high`. |
| `loc` | Integer | **Conditional** | **MANDATORY** if `method=step`. |
| `fp_count` | Integer | **Conditional** | **MANDATORY** if `method=fp`. |
| `man_days_per_unit`| Float | **Conditional** | **MANDATORY** if `method=step` or `fp`. |

### Value Mappings (Source of Truth)

**Features (Phase 1)**
*Extracted from `FEATURE_LABEL_MAP`*
- `auth` (ユーザー認証)
- `list_search` (一覧表示・検索)
- `detail_view` (詳細表示)
- `crud` (CRUD操作)
- `payment` (決済機能)
- `push_notification` (プッシュ通知)
- `realtime` (リアルタイム機能)
- `external_api` (外部API連携)
- `admin_panel` (管理画面)
- `data_migration` (データ移行)

**Design (Phase 2 - Internal)**
*Extracted from `PHASE2_ITEMS`*
- `ia_design` (IA設計) - Fixed
- `wireframe` (WF作成) - Per Screen
- `figma` (Figma化) - Per Screen

**Vendor (Phase 3 - Outsource)**
*Extracted from `PHASE3_ITEMS`*
- `ui_design` (UIデザイン) - Per Screen
- `design_system` (デザインシステム) - Fixed
- `prototype` (プロトタイプ) - Fixed
- `logo_icon` (アイコン・ロゴ) - Fixed

---

## 3. State Machine Spec

The system ensures that **LLM Hallucinations** do not enter the Calculation logic by forcing a state transition from "Vague" to "Fact".

### Data States

| State | Definition | Owner | Persistence |
| :--- | :--- | :--- | :--- |
| **DRAFT** | User's free text input. "I want a travel app." | User | Ephemeral (Chat Log) |
| **CANDIDATE**| Agent's proposal options. "Did you mean [Mobile App]?" | Agent | Ephemeral (Chat Log) |
| **FACT** | Explicitly selected option. User clicked `[Mobile App]`. | System | **Session Memory** |
| **CALC** | Canonicalized JSON payload sent to Calc API. | System | Transient |
| **SNAPSHOT** | Final JSON response containing Inputs + Price. | System | **Permanent** (Artifact/Log) |

### Transition Logic
1.  **Selection**: User inputs text (DRAFT) -> Agent proposes Options (CANDIDATE).
2.  **Confirmation**: User clicks Option -> Button sends `value` to Agent -> stored as `selected_feature` (FACT).
3.  **Validation**: Before `call_calc` tool usage, Agent checks if all dependencies (e.g., `confidence` for Phase 3) are present in FACTs.
4.  **Calculation**: Agent constructs JSON from FACTs only -> Calls Calc API.

---

## 4. Do-Not-Break List (Invariant Zones)

> **Warning**: Modifying these areas requires explicit approval and rigorous regression testing.

### A. The "Money" Logic (Backend)
*   **File**: `estimate-backend-calc/function_app.py`
    *   **Logic**: `main_logic` function.
    *   **Reason**: Defines how money is calculated. Any change here changes the price.
*   **File**: `estimate-backend-calc/estimate_config.yaml`
    *   **Logic**: All `daily_rates`, `man_days`, and `policy` sections.
    *   **Reason**: This is the "Price List".

### B. User Confirmation Policy (Agent/Backend)
*   **Policy**: `require_explicit_vendor_confidence: true`
    *   **Constraint**: Never default the confidence level. The user must explicitly take responsibility for the vagueness level.
    *   **Constraint**: Never default Productivity for STEP/FP.

### C. UI State Integrity (Frontend)
*   **File**: `estimation-ui-app/app.js`
    *   **Logic**: `sendMessageToAPI` and `handleOptionClick`.
    *   **Reason**: Ensures that what the user *sees* (Button Click) is exactly what is *sent* (Value).

---

## 5. TERASOLUNA Embedding Points

To fully align with TERASOLUNA's "Agreement-based" architecture, the following hooks are identified for future enhancements:

| Concept | Current Implementation | Enhancement Point |
| :--- | :--- | :--- |
| **Method Selection** | Agent suggests `[STEP]` or `[Screen]` based on text. | **Hook**: Enforce a dedicated "Method Agreement" step before collecting detailed counts. |
| **Premise Agreement** | Implicit. User agrees by clicking options. | **Hook**: Start of Phase 3. Explicitly ask "Do you agree that Design is outsourced (Variable Cost)?" |
| **Evidence Preservation**| JSON is returned to User. | **Hook**: Save JSON Snapshot to Blob Storage with a timestamp/hash for non-repudiation. |

## 6. Unknowns & Pending Logic
*   **Unknown**: Handling of "Change Requests" after Snapshot generation (Version diffing logic).
*   **Unknown**: Deployment automated pipeline details (CI/CD specific triggers for Prod).
*   **Unknown**: Authentication layer for the UI (Currently Public/Anonymous).
