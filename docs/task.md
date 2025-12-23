# AI Estimation System - Master Roadmap

> **Design Goal**: Azure AI Agent as the central orchestrator, using Calc API and RAG as tools to generate executive-level HTML estimates.

## 🏁 Phase 1: AI Agent Core (flow)
- [x] Azure Environment Setup (Foundry, OpenAI, Search)
- [x] RAG Knowledge Base Construction (18 docs indexed)
- [x] Local Flow Testing & Mock Integration
- [x] CI/CD Pipeline (Automated testing on push)
- [x] **Integration: Connect Agent to Calc API Tool** (URL: `estimate-api-cli.azurewebsites.net`)
    - [x] Update `.env` and `deployment.yaml` with live API URL
    - [x] Fix tool path (`/calculate` -> `/calculate_estimate`)
    - [x] Local verification successful (858,000 JPY for 5 screens, high complexity)
- [x] Upload & Configure Flow in Foundry (Project: `est-agent-v2`)
    - [x] Connection Configured (`jhong-mjha50n5-swedencentral`)
    - [x] Verification Passed (Compute Session)
- [/] **Deployment: Azure AI Online Endpoint**
    - [x] ML Workspace & Endpoint Creation
    - [!] **Deployment Failed (Liveness Probe) - NEXT SESSION**
        - **Issue**: `v2-deploy` failed with "Liveness probe failed"
        - **Fix needed**: Increase `initial_delay` from 300s to 600s in `deployment/deployment.yaml`
        - **Alternative**: Deploy via Azure AI Foundry Portal UI for better error visibility

## 🏗️ Phase 2: Outer Fortifications - Calculation (estimate-backend-calc)
- [x] Implement YAML-based calculation logic (No AI)
- [x] Create Azure Functions endpoint (Code ready)
- [x] Verify standalone calculation accuracy (Tests ready)
- [x] **Deployment: Deploy to Azure Functions** (URL: `https://estimate-api-cli.azurewebsites.net/api/calculate_estimate`)
    - [x] Fix 401 Unauthorized (OIDC authentication)
    - [x] Fix 404 Not Found (dependency packaging with `.python_packages`)
    - [x] API verification successful (200 OK, 1,320,000 JPY for 10 screens, medium complexity)
- [x] Expose endpoint for Agent's Tool Call

## 💻 Phase 3: Outer Fortifications - UI (estimation-ui-app)
- [x] Implement modern, premium single-page UI (v2.0.0)
- [ ] Connect UI to **Agent Endpoint only** (Waiting for Phase 1 deployment fix)
- [ ] Implement HTML rendering for `doc--8px` style responses (Done in v2.0.0)

## 🔗 Phase 4: Full System Integration & Verification
- [ ] End-to-end test: UI -> Agent -> Calc -> AI Generation -> UI
- [ ] Verify Agent-led orchestration (Agent makes the call to Calc)
- [ ] Final quality check: "Executive-ready" response verification

---

## 📝 Next Session TODO (2025-12-24)
1. **Fix Liveness Probe Issue**:
   - Edit `estimation_agent/deployment/deployment.yaml`:
     - Change `initial_delay: 300` to `initial_delay: 600` (lines 18, 23)
   - Retry deployment: `az ml online-deployment create --file deployment/deployment.yaml ...`
   
2. **Commit Pending Changes**:
   - Modified files: `call_calc_tool.py`, `flow.dag.yaml`, `.github/workflows/pf-test.yml`
   - New files: `deployment/`, `.env`, `deploy.sh`, etc.
   - Commit message: "feat: integrate live backend API and prepare Azure ML deployment"

3. **Verify Agent Deployment**:
   - Check deployment status in Azure Portal
   - Test endpoint with sample request
   - Proceed to Phase 3 (UI integration) if successful

---
*Last updated: 2025-12-24 01:33*
