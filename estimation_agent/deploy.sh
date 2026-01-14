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
echo "Ensuring Online Endpoint: $ENDPOINT_NAME..."
az ml online-endpoint create --file deployment/endpoint.yaml --resource-group "$RESOURCE_GROUP" --workspace-name "$WORKSPACE_NAME" || echo "Endpoint might already exist."

# 3. Create or Update Online Deployment
echo "Preparing deployment configuration..."
# Export variables from .env for envsubst
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Create interpolated deployment file
envsubst '$AZURE_OPENAI_ENDPOINT,$AZURE_OPENAI_API_KEY,$AZURE_AI_SEARCH_ENDPOINT,$AZURE_AI_SEARCH_API_KEY' < deployment/deployment.yaml > deployment/deployment_ready.yaml

echo "Deploying Online Deployment: $DEPLOYMENT_NAME..."
# Check if deployment exists
if az ml online-deployment show --name production --endpoint-name "$ENDPOINT_NAME" --resource-group "$RESOURCE_GROUP" --workspace-name "$WORKSPACE_NAME" > /dev/null 2>&1; then
    echo "Deployment already exists. Updating..."
    az ml online-deployment update --file deployment/deployment_ready.yaml --resource-group "$RESOURCE_GROUP" --workspace-name "$WORKSPACE_NAME"
else
    echo "Deployment does not exist. Creating..."
    az ml online-deployment create --file deployment/deployment_ready.yaml --resource-group "$RESOURCE_GROUP" --workspace-name "$WORKSPACE_NAME" --all-traffic
fi

# Cleanup
rm deployment/deployment_ready.yaml

echo "Deployment completed successfully!"
