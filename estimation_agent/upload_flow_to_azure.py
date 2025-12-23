from promptflow.azure import PFClient
from azure.identity import DefaultAzureCredential
import argparse
import os

# Config defaults
SUBSCRIPTION_ID = "f477e584-821b-44b4-ad6b-51597eae05a6"
RESOURCE_GROUP = "rg-est-v2"
WORKSPACE_NAME = "est-agent-v2"
FLOW_DISPLAY_NAME = "estimation-agent"

def main():
    parser = argparse.ArgumentParser(description="Upload a prompt flow to Azure AI Foundry.")
    parser.add_argument("--flow-dir", type=str, default=".", help="Path to the flow directory")
    args = parser.parse_args()

    flow_dir = os.path.abspath(args.flow_dir)
    print(f"Connecting to workspace: {WORKSPACE_NAME}...")
    
    # Get credential
    credential = DefaultAzureCredential()
    
    # Initialize PFClient
    try:
        pf = PFClient(
            credential=credential,
            subscription_id=SUBSCRIPTION_ID,
            resource_group=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME
        )
    except Exception as e:
        print(f"Failed to initialize PFClient: {e}")
        return

    print(f"Uploading flow '{FLOW_DISPLAY_NAME}' from '{flow_dir}'...")
    
    try:
        # Create or update the flow
        flow = pf.flows.create_or_update(
            flow=flow_dir,
            display_name=FLOW_DISPLAY_NAME
        )
        print("Upload complete!")
        print(f"Flow ID: {flow.name}")
        print(f"Portal URL: https://ai.azure.com/project/flow/list?wsid=/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/{WORKSPACE_NAME}")
    except Exception as e:
        print(f"Failed to upload flow: {e}")

if __name__ == "__main__":
    main()
