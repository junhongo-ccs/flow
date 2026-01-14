import os
import json
from unittest.mock import MagicMock, patch
# Import the function to test
from call_calc_tool import _call_real_calc_api

def test_transformation():
    print("--- Testing Agent Tool Transformation Logic ---")
    
    cases = [
        {
            "name": "Option A (Full Design)",
            "message": "Option Aを選択しました",
            "history": [],
            "expected_p2": True,
            "expected_p3": True
        },
        {
            "name": "Option C (Layout exists -> No Phase 2)",
            "message": "Option C",
            "history": [{"role": "assistant", "content": "デザイン状況を教えてください [A] [B] [C] [D]"}],
            "expected_p2": False,
            "expected_p3": True
        },
        {
            "name": "Option D (Design complete -> No P2, No P3)",
            "message": "Option D",
            "history": [{"role": "assistant", "content": "デザイン状況を教えてください [A] [B] [C] [D]"}],
            "expected_p2": False,
            "expected_p3": False
        },
        {
            "name": "Figma Wireframe already exists (No Phase 2)",
            "message": "不要（自社でFigma等を作成）",
            "history": [{"role": "assistant", "content": "設計フェーズの依頼範囲はどうしますか？"}],
            "expected_p2": False,
            "expected_p3": True
        }
    ]
    
    os.environ["CALC_API_URL"] = "http://mock-api"
    os.environ["CALC_API_KEY"] = "mock-key"
    
    for case in cases:
        print(f"\nCase: {case['name']}")
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "status": "ok", 
                "estimated_amount": 1000, 
                "currency": "JPY",
                "include_phase2": True,
                "include_phase3": True
            }
            
            _call_real_calc_api({"message": case["message"]}, case["history"])
            
            # Extract the json payload sent to requests.post
            args, kwargs = mock_post.call_args
            payload = kwargs.get('json', {})
            
            p2 = payload.get('include_phase2')
            p3 = payload.get('include_phase3')
            
            print(f"Sent to API: include_phase2={p2}, include_phase3={p3}")
            
            if p2 == case["expected_p2"] and p3 == case["expected_p3"]:
                print("✅ PASS")
            else:
                print(f"❌ FAIL: Expected P2={case['expected_p2']}, P3={case['expected_p3']}")

if __name__ == "__main__":
    test_transformation()
