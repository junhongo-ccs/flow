import pytest
import os
from promptflow import PFClient

@pytest.fixture
def pf_client():
    return PFClient()

@pytest.fixture
def flow_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../estimation_agent'))

def test_flow_basic_execution(pf_client, flow_path):
    """Flow基本実行テスト"""
    result = pf_client.test(
        flow=flow_path,
        inputs={
            "user_input": {
                "project_type": "web_app",
                "duration_months": 6,
                "team_size": 3
            }
        }
    )
    
    assert result is not None
    assert "response" in result
    assert result["response"]["success"] is True
    assert result["response"]["data"]["total"] == 18000000

def test_flow_with_minimal_input(pf_client, flow_path):
    """最小限の入力（空辞書）でのテスト"""
    result = pf_client.test(
        flow=flow_path,
        inputs={
            "user_input": {}
        }
    )
    
    # デフォルト値 6ヶ月, 3人が使用される
    assert result["response"]["success"] is True
    assert result["response"]["data"]["total"] == 18000000
