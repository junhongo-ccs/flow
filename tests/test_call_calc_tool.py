import pytest
import sys
import os

# プロジェクトルートをパスに追加してインポート可能にする
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../estimation_agent')))

from call_calc_tool import call_calc, _mock_calc

def test_mock_calc_basic():
    """モック計算の基本動作"""
    user_input = {
        "project_type": "web_app",
        "duration_months": 6,
        "team_size": 3
    }
    
    result = _mock_calc(user_input)
    
    # 100万 * 6ヶ月 * 3人 = 1800万
    assert result["total"] == 18000000
    assert result["breakdown"]["development"] == 12600000
    assert result["is_mock"] is True

def test_call_calc_with_mock_mode(monkeypatch):
    """モックモードでのcall_calc"""
    monkeypatch.setenv("USE_MOCK_CALC", "true")
    
    user_input = {"duration_months": 3, "team_size": 2}
    result = call_calc(user_input)
    
    assert result["is_mock"] is True
    assert result["total"] == 6000000

def test_call_calc_missing_params():
    """パラメータ不足時のデフォルト値（デフォルト値 6ヶ月, 3人が使用されること）"""
    result = _mock_calc({})
    assert result["total"] == 18000000
