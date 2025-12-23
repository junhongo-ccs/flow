# AI Estimation System Implementation Plan - CI/CD & Deployment

## Goal
Automate the testing of the Prompt Flow using GitHub Actions and prepare for final deployment as an Azure AI Online Endpoint.

## Proposed Changes

### [Component] CI/CD (GitHub Actions)

#### [NEW] [pf-test.yml](file:///Users/hongoujun/Documents/GitHub/flow/.github/workflows/pf-test.yml)
Create a workflow to run `pf flow test` on every push to the `main` branch. This ensures that changes to the flow or RAG data don't break the agent.

### [Component] Deployment (Azure AI Online Endpoint)

#### [NEW] [deploy.sh](file:///Users/hongoujun/Documents/GitHub/flow/estimation_agent/deploy.sh)
A script to:
1.  **[NEW]** Create a Machine Learning Workspace (`mlw-estimation-agent`).
2.  Create an Azure AI Online Endpoint.
3.  Deploy the Prompt Flow to the endpoint.
4.  Configure Managed Identity and assign necessary roles (`Cognitive Services User`, `Search Index Data Reader`) so the endpoint can access OpenAI and Search.

## User Review Required
> [!IMPORTANT]
> To enable GitHub Actions, you will need to set the following **GitHub Secrets** in your repository:
> - `AZURE_OPENAI_ENDPOINT`
> - `AZURE_OPENAI_API_KEY`
> - `AZURE_AI_SEARCH_ENDPOINT`
> - `AZURE_AI_SEARCH_API_KEY`

## Verification Plan

### Automated Tests
- Trigger a GitHub Action by pushing a change.
- Verify that the `pf flow test` passes in the CI environment.

### Deployment Verification
- Verify that the Online Endpoint is reachable and returns a valid estimation response.
