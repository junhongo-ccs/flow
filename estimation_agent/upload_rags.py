"""
RAG Documents Upload Script
Uploads markdown files to Azure AI Search index for RAG functionality
Uses REST API directly to avoid Python version compatibility issues
"""

import os
import json
import requests
import hashlib


def create_index(endpoint: str, api_key: str, index_name: str):
    """Create the search index"""
    url = f"{endpoint}/indexes/{index_name}?api-version=2023-11-01"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    # Define index schema
    index_definition = {
        "name": index_name,
        "fields": [
            {
                "name": "id",
                "type": "Edm.String",
                "key": True,
                "searchable": False,
                "filterable": False,
                "sortable": False,
                "facetable": False
            },
            {
                "name": "content",
                "type": "Edm.String",
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False
            },
            {
                "name": "filename",
                "type": "Edm.String",
                "searchable": True,
                "filterable": True,
                "sortable": True,
                "facetable": False
            },
            {
                "name": "filepath",
                "type": "Edm.String",
                "searchable": False,
                "filterable": False,
                "sortable": False,
                "facetable": False
            }
        ]
    }
    
    response = requests.put(url, headers=headers, json=index_definition)
    
    if response.status_code == 201:
        print(f"✅ Index '{index_name}' created successfully")
        return True
    elif response.status_code == 204:
        print(f"ℹ️  Index '{index_name}' already exists (updated)")
        return True
    else:
        print(f"❌ Failed to create index: {response.status_code}")
        print(f"   Response: {response.text}")
        return False


def upload_documents(endpoint: str, api_key: str, index_name: str, rags_dir: str):
    """Upload all markdown files from the rags directory"""
    url = f"{endpoint}/indexes/{index_name}/docs/index?api-version=2023-11-01"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    documents = []
    
    # Read all markdown files
    for filename in sorted(os.listdir(rags_dir)):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(rags_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a unique ID based on filename
        doc_id = hashlib.md5(filename.encode()).hexdigest()
        
        document = {
            "@search.action": "upload",
            "id": doc_id,
            "content": content,
            "filename": filename,
            "filepath": filepath,
        }
        
        documents.append(document)
        print(f"📄 Prepared: {filename}")
    
    # Upload documents in batch
    print(f"\n⬆️  Uploading {len(documents)} documents...")
    
    payload = {"value": documents}
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        succeeded = sum(1 for r in result.get('value', []) if r.get('status'))
        print(f"\n✅ Upload complete!")
        print(f"   Succeeded: {succeeded}/{len(documents)}")
        return succeeded, len(documents) - succeeded
    else:
        print(f"\n❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return 0, len(documents)


def main():
    # Configuration
    SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
    SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
    INDEX_NAME = "estimation-rags"
    RAGS_DIR = os.path.join(os.path.dirname(__file__), "rags")
    
    if not SEARCH_ENDPOINT or not SEARCH_API_KEY:
        print("❌ Error: Environment variables not set")
        print("   Please set AZURE_AI_SEARCH_ENDPOINT and AZURE_AI_SEARCH_API_KEY")
        return 1
    
    # Remove trailing slash from endpoint if present
    SEARCH_ENDPOINT = SEARCH_ENDPOINT.rstrip('/')
    
    print("=" * 60)
    print("RAG Documents Upload Script")
    print("=" * 60)
    print(f"Endpoint: {SEARCH_ENDPOINT}")
    print(f"Index: {INDEX_NAME}")
    print(f"Source: {RAGS_DIR}")
    print("=" * 60)
    print()
    
    # Create index
    if not create_index(SEARCH_ENDPOINT, SEARCH_API_KEY, INDEX_NAME):
        return 1
    
    print()
    
    # Upload documents
    succeeded, failed = upload_documents(SEARCH_ENDPOINT, SEARCH_API_KEY, INDEX_NAME, RAGS_DIR)
    
    if failed > 0:
        print(f"\n⚠️  Warning: {failed} documents failed to upload")
        return 1
    
    print("\n🎉 All documents uploaded successfully!")
    return 0


if __name__ == "__main__":
    exit(main())

