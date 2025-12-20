from promptflow import tool
from typing import Dict, Any

@tool
def generate_response(calc_result: Dict[str, Any], user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    計算結果をもとにレスポンスを生成
    
    ローカル開発時はテンプレートベースのレスポンス
    Azure環境ではLLMを使用
    
    Args:
        calc_result: calc APIの結果
        user_input: ユーザー入力
    
    Returns:
        最終レスポンス
    """
    # エラーチェック
    if calc_result.get("error"):
        return {
            "success": False,
            "message": f"計算エラーが発生しました: {calc_result.get('message')}",
            "data": None
        }
    
    # 成功レスポンス生成
    total = calc_result.get("total", 0)
    breakdown = calc_result.get("breakdown", {})
    unit = calc_result.get("unit", "JPY")
    
    # テンプレートベースのレスポンス（Phase 4 で LLM に置き換え）
    message = f"""見積もり結果をお知らせします。

【総額】
{total:,} {unit}

【内訳】"""
    
    for key, value in breakdown.items():
        message += f"\n- {key}: {value:,} {unit}"
    
    if calc_result.get("is_mock"):
        message += "\n\n※ これはモックデータです（ローカル開発用）"
    
    return {
        "success": True,
        "message": message.strip(),
        "data": {
            "total": total,
            "breakdown": breakdown,
            "unit": unit
        }
    }
