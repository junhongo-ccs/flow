import os
import glob
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
)
from dotenv import load_dotenv

# .env ファイルを明示的に指定して読み込む
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def recreate_index(endpoint, key, index_name):
    client = SearchIndexClient(endpoint, AzureKeyCredential(key))
    
    index = SearchIndex(
        name=index_name,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="ja.microsoft"),
            SimpleField(name="source", type=SearchFieldDataType.String),
        ]
    )
    
    try:
        # 既存のインデックスを削除（スキーマ変更を反映するため）
        print(f"Deleting existing index '{index_name}'...")
        client.delete_index(index_name)
    except Exception as e:
        print(f"Index '{index_name}' did not exist or could not be deleted: {e}")
        
    try:
        client.create_index(index)
        print(f"Index '{index_name}' created.")
    except Exception as e:
        raise e

def upload_documents(endpoint, key, index_name, rags_dir):
    client = SearchClient(endpoint, index_name, AzureKeyCredential(key))
    
    docs = []
    files = glob.glob(os.path.join(rags_dir, "*.md"))
    
    for i, file_path in enumerate(files):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            filename = os.path.basename(file_path)
            doc = {
                "id": str(i),
                "content": content,
                "source": filename
            }
            docs.append(doc)
    
    if docs:
        result = client.upload_documents(documents=docs)
        print(f"Uploaded {len(docs)} documents.")
    else:
        print("No documents found to upload.")

if __name__ == "__main__":
    endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_AI_SEARCH_API_KEY")
    index_name = "estimation-rags"
    rags_dir = os.path.join(os.path.dirname(__file__), "rags")
    
    if not endpoint or not key:
        print("Error: AZURE_AI_SEARCH_ENDPOINT or AZURE_AI_SEARCH_API_KEY not set in .env")
        print(f"DEBUG: ENDPOINT={endpoint}")
    else:
        recreate_index(endpoint, key, index_name)
        upload_documents(endpoint, key, index_name, rags_dir)
