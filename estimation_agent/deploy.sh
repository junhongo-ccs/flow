#!/bin/bash
set -e

# Configuration
SUBSCRIPTION_ID="f477e584-821b-44b4-ad6b-51597eae05a6"
RESOURCE_GROUP="rg-estimation-agent"
WORKSPACE_NAME="mlw-estimation-agent"
LOCATION="eastus2" # Align with RAG/OpenAI where possible
ENDPOINT_NAME="estimation-agent-endpoint"
DEPLOYMENT_NAME="blue"

echo "Using Subscription: $SUBSCRIPTION_ID"
az account set --subscription "$SUBSCRIPTION_ID"

# 1. Create ML Workspace
echo "Creating ML Workspace: $WORKSPACE_NAME..."
az ml workspace create --name "$WORKSPACE_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" || echo "Workspace might already exist."

# 2. Create Online Endpoint
echo "Creating Online Endpoint: $ENDPOINT_NAME..."
az ml online-endpoint create --file deployment/endpoint.yaml --resource-group "$RESOURCE_GROUP" --workspace-name "$WORKSPACE_NAME"

# 3. Create Online Deployment
echo "Creating Online Deployment: $DEPLOYMENT_NAME..."
# Note: We use env vars from .env for the deployment yaml template in next step
az ml online-deployment create --file deployment/deployment.yaml --resource-group "$RESOURCE_GROUP" --workspace-name "$WORKSPACE_NAME" --all-traffic

echo "Deployment completed successfully!"
