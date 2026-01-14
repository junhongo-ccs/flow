import os
import requests
import json
import logging
from typing import List, Dict, Any, Optional
from promptflow.core import tool

@tool
def call_calc(screen_count: int = None, features: List[str] = None, complexity: str = "medium", 
              phase2_items: List[str] = None, phase3_items: List[str] = None,
              method: str = "screen", loc: int = None, fp_count: int = None, man_days_per_unit: float = None,
              confidence: str = None) -> str:
    """
    Call the external Calculation API to get estimation details.
    
    Args:
        screen_count: Number of screens (Required for 'screen' method or if Design phases needed).
        features: List of feature keys (Required, e.g., ["auth", "payment"]).
        complexity: Complexity of the project ("low", "medium", "high").
        phase2_items: List of Phase 2 item keys.
        phase3_items: List of Phase 3 item keys.
        method: Estimation method ("screen", "step", "fp"). Default "screen".
        loc: Lines of Code (Required if method="step").
        fp_count: Function Points (Required if method="fp").
        man_days_per_unit: Productivity rate (Required if method="step" or "fp").
        confidence: Design Confidence ("low", "medium", "high"). Required if Phase 2/3 items are present.
    
    Returns:
        JSON string containing the calculation result.
    """
    # 1. Validation for REQUIRED fields
    missing_fields = []
    
    if method == "screen":
        if screen_count is None: missing_fields.append("screen_count")
        if features is None: missing_fields.append("features")
    
    elif method == "step":
        if loc is None: missing_fields.append("loc")
        if man_days_per_unit is None: missing_fields.append("man_days_per_unit")
        
    elif method == "fp":
        if fp_count is None: missing_fields.append("fp_count")
        if man_days_per_unit is None: missing_fields.append("man_days_per_unit")

    # Common
    if complexity is None: missing_fields.append("complexity")

    if missing_fields:
        return json.dumps({
            "status": "error",
            "error_type": "validation_error",
            "message": "Missing required parameters",
            "missing_fields": missing_fields
        }, ensure_ascii=False)

    # 2. Canonicalization
    # Deduplicate and sort lists to ensure deterministic API calls
    uniq_features = sorted(list(set(features))) if features else []
    uniq_phase2 = sorted(list(set(phase2_items))) if phase2_items else []
    uniq_phase3 = sorted(list(set(phase3_items))) if phase3_items else []

    # 3. Prepare Payload
    payload = {
        "api_version": "v1",
        "method": method,
        "screen_count": screen_count,
        "complexity": complexity,
        "features": uniq_features,
        "phase2_items": uniq_phase2,
        "phase3_items": uniq_phase3,
        "loc": loc,
        "fp_count": fp_count,
        "man_days_per_unit": man_days_per_unit,
        "confidence": confidence
    }
    
    endpoint = os.getenv("CALC_API_ENDPOINT")
    # Fallback to local func default if not set (mostly for dev/test)
    if not endpoint:
        endpoint = "http://localhost:7071/api/calculate_estimate"
        logging.warning(f"CALC_API_ENDPOINT not set. Using default: {endpoint}")

    try:
        # 4. Call API
        headers = {"Content-Type": "application/json"}
        logging.info(f"Calling Calc API at {endpoint} with payload: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return json.dumps(response.json(), ensure_ascii=False)
        else:
            return json.dumps({
                "status": "error", 
                "message": f"Calc API Error: {response.status_code}",
                "details": response.text
            }, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Connection Failed: {str(e)}"
        }, ensure_ascii=False)
