from call_calc_tool import call_calc
import os

# Set mock mode
os.environ["USE_MOCK_CALC"] = "true"

def test_agent_tool():
    print("--- Testing Agent Tool (Design Readiness Detection) ---")
    
    cases = [
        {
            "name": "Option A (Full Design)",
            "input": {"message": "Option Aを選択しました"},
            "history": []
        },
        {
            "name": "Option C (Layout exists)",
            "input": {"message": "Option C"},
            "history": [{"role": "assistant", "content": "デザイン状況を教えてください [A] [B] [C] [D]"}]
        },
        {
            "name": "Figma Wireframe already exists",
            "input": {"message": "Figmaで作成済みなので不要です"},
            "history": [{"role": "assistant", "content": "設計フェーズの依頼範囲はどうしますか？"}]
        }
    ]
    
    for case in cases:
        print(f"\nCase: {case['name']}")
        # We need to look at what request is sent to the "API" 
        # Since call_calc calls _mock_calc, we can print the transformed request inside call_calc_tool.py
        # Or just trust the return from call_calc if we add some debug info 
        # However, call_calc doesn't return the flags. 
        # Let's modify call_calc_tool.py slightly to RETURN the flags in mock mode for verification.
        result = call_calc(case["input"], case["history"])
        print(f"Result (Total): {result['total']:,}")
        # Note: I'll update call_calc_tool.py to return include_phaseX flags for transparency.
        
if __name__ == "__main__":
    test_agent_tool()
