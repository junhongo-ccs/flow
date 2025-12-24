from promptflow import tool
from typing import Dict, Any
import os
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def call_calc(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    calc APIを呼び出して計算結果を取得
    
    ローカル開発時はモックデータを返す
    本番環境では実際のAPIを呼び出す
    
    Args:
        user_input: ユーザー入力
            例: {
                "project_type": "web_app",
                "duration_months": 6,
                "team_size": 3
            }
    
    Returns:
        計算結果
            例: {
                "total": 10000000,
                "breakdown": {
                    "development": 7000000,
                    "design": 2000000,
                    "management": 1000000
                },
                "unit": "JPY"
            }
    """
    # 環境変数でモード切り替え
    use_mock = os.getenv("USE_MOCK_CALC", "true").lower() == "true"
    
    if use_mock:
        logger.info("Using mock calc API")
        return _mock_calc(user_input)
    else:
        logger.info("Calling real calc API")
        return _call_real_calc_api(user_input)

def _mock_calc(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """モック計算（開発用）"""
    # 簡易的な計算ロジック
    duration = user_input.get("duration_months", 6)
    team_size = user_input.get("team_size", 3)
    
    # 1人月100万円としての概算
    base_cost_per_month = 1000000
    total = base_cost_per_month * int(duration) * int(team_size)
    
    return {
        "total": total,
        "breakdown": {
            "development": int(total * 0.7),
            "design": int(total * 0.2),
            "management": int(total * 0.1)
        },
        "unit": "JPY",
        "is_mock": True
    }

def _call_real_calc_api(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """実際のcalc API呼び出し（本番用）"""
    import requests
    
    calc_api_url = os.getenv("CALC_API_URL")
    api_key = os.getenv("CALC_API_KEY")
    
    if not calc_api_url:
        logger.warning("CALC_API_URL is not set. Falling back to mock.")
        return _mock_calc(user_input)
    
    # Transform user input to Backend API format
    # Backend expects: {"screen_count": int, "complexity": "low"|"medium"|"high"}
    # User provides: {"project_type": str, "duration_months": int, "team_size": int}
    # OR: {"screen_count": int, "complexity": str}
    
    # Check if already in correct format
    if "screen_count" in user_input and "complexity" in user_input:
        api_request = user_input
    else:
        # Estimate screen_count from project parameters
        duration = user_input.get("duration_months", 6)
        team_size = user_input.get("team_size", 3)
        project_type = user_input.get("project_type", "web_app")
        
        # Simple heuristic: larger teams and longer projects = more screens
        estimated_screens = max(5, int(duration * team_size * 0.8))
        
        # Map project complexity
        complexity_map = {
            "simple": "low",
            "standard": "medium",
            "complex": "high",
            "web_app": "medium",
            "mobile_app": "high",
            "enterprise": "high"
        }
        complexity = complexity_map.get(project_type, "medium")
        
        api_request = {
            "screen_count": estimated_screens,
            "complexity": complexity
        }
        
        logger.info(f"Transformed input: {user_input} -> {api_request}")
    
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["X-API-Key"] = api_key
    
    try:
        response = requests.post(
            f"{calc_api_url}/calculate_estimate",
            json=api_request,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        api_response = response.json()
        
        # Transform Backend API response to expected format
        # Backend returns: {"status": "ok", "estimated_amount": int, "breakdown": {...}, ...}
        # Expected format: {"total": int, "breakdown": {...}, "unit": "JPY"}
        
        if api_response.get("status") == "ok":
            return {
                "total": api_response.get("estimated_amount"),
                "breakdown": api_response.get("breakdown", {}),
                "unit": api_response.get("currency", "JPY"),
                "screen_count": api_response.get("screen_count"),
                "complexity": api_response.get("complexity"),
                "config_version": api_response.get("config_version"),
                "is_mock": False
            }
        else:
            return {
                "error": True,
                "message": api_response.get("message", "Unknown error"),
                "calc_result": None
            }
            
    except Exception as e:
        logger.error(f"calc API error: {e}")
        return {
            "error": True,
            "message": str(e),
            "calc_result": None
        }

