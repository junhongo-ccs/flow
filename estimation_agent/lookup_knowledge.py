import os
from typing import List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from promptflow.core import tool
from dotenv import load_dotenv

# .env ファイルの読み込み
load_dotenv()

@tool
def lookup_knowledge(user_input: Dict[str, Any], top_k: int = 3) -> str:
    """
    Azure AI Search から関連するナレッジを検索して返す
    
    Args:
        user_input: ユーザー入力
        top_k: 取得するドキュメント数
    
    Returns:
        結合された関連ドキュメントのテキスト
    """
    # ユーザーメッセージを優先し、なければ project_type を使用
    query = user_input.get("message") or user_input.get("project_type") or "software development"
    endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_AI_SEARCH_API_KEY")
    index_name = "estimation-rags"
    
    if not endpoint or not key:
        return "Warning: Azure AI Search connection info not found."

    try:
        client = SearchClient(endpoint, index_name, AzureKeyCredential(key))
        
        # 検索実行
        results = client.search(
            search_text=query,
            top=top_k,
            include_total_count=True
        )
        
        relevant_docs = []
        for result in results:
            content = result.get("content", "")
            source = result.get("source", "unknown")
            relevant_docs.append(f"--- Source: {source} ---\n{content}")
            
        if not relevant_docs:
            return "No relevant internal documents found."
            
        return "\n\n".join(relevant_docs)
        
    except Exception as e:
        return f"Error during search: {str(e)}"
