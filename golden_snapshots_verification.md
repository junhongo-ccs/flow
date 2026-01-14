# Golden Snapshot Verification

## Golden Snapshot #1 : Screen Method (Phase 1)

### 1. FACT Input
```json
{
  "selected_option": ["Web App", "10画面", "ユーザー認証"],
  "collected_params": {
    "method": "screen",
    "screen_count": 10,
    "features": ["auth"],
    "complexity": "medium"
  }
}
```

### 2. Calc Payload
```json
{
  "method": "screen",
  "screen_count": 10,
  "complexity": "medium",
  "features": ["auth"],
  "phase2_items": [],
  "phase3_items": [],
  "confidence": null
}
```

### 3. Calc Response
```json
{
  "status": "ok",
  "estimated_amount": 1100000,
  "estimated_range": { "min": 1100000, "max": 1100000 },
  "currency": "JPY",
  "method": "screen",
  "breakdown": {
    "development": {
      "method": "screen",
      "base_days": 20.0,
      "total_days": 20.0,
      "cost": 1000000,
      "details": {
        "feature_days": 5,
        "screen_days": 15.0
      }
    },
    "phase2_design": { "total_days": 0, "cost": 0 },
    "phase3_visual": { "total_days": 0, "cost": 0, "range": { "min": 0, "max": 0 } },
    "final": 1100000
  }
}
```

### 4. Consistency Proof
- **MD**: `ARCHITECTURE_ESTIMATION_SNAPSHOT.md` #6.A Screen Count Method
    - "Formula: (Sum(Features) + (Screens * Rate)) * Complexity"
- **Code**: `estimate-backend-calc/function_app.py:L148-L150`
    - `dev_feature_days = sum(...)`
    - `dev_screen_days = screen_count * dev_screen_rate`
    - `dev_base_days = dev_feature_days + dev_screen_days`
- **Verdict**: Fully Consistent

---

## Golden Snapshot #2 : STEP / LOC Method (Phase 2)

### 1. FACT Input
```json
{
  "selected_option": ["STEP法", "10000 LOC", "0.05人日/step"],
  "collected_params": {
    "method": "step",
    "loc": 10000,
    "man_days_per_unit": 0.05,
    "complexity": "medium"
  }
}
```

### 2. Calc Payload
```json
{
  "method": "step",
  "loc": 10000,
  "man_days_per_unit": 0.05,
  "complexity": "medium",
  "features": [],
  "phase2_items": [],
  "phase3_items": []
}
```

### 3. Calc Response
```json
{
  "status": "ok",
  "estimated_amount": 27500000,
  "breakdown": {
    "development": {
      "method": "step",
      "base_days": 500.0,
      "total_days": 500.0,
      "cost": 25000000,
      "details": {
        "loc": 10000,
        "man_days_per_unit": 0.05
      }
    },
    "final": 27500000
  }
}
```

### 4. Consistency Proof
- **MD**: `ARCHITECTURE_ESTIMATION_SNAPSHOT.md` #6.B STEP Method
    - "Productivity must be explicitly chosen (not inferred)."
- **Code**: `estimate-backend-calc/estimate_config.yaml:L16`
    - `require_explicit_productivity_for_step_fp: true`
- **Code**: `estimate-backend-calc/function_app.py:L138`
    - `if require_explicit_prod and (loc is None or man_days_per_unit is None): return ... error`
- **Verdict**: Fully Consistent

---

## Golden Snapshot #3 : Vendor Mixed / Two-Layer (Phase 3)

### 1. FACT Input
```json
{
  "selected_option": ["UIデザイン", "Low Confidence"],
  "collected_params": {
    "phase3_items": ["ui_design"],
    "confidence": "low"
  }
}
```

### 2. Calc Payload
```json
{
  "method": "screen", // default
  "screen_count": 10, // default
  "phase3_items": ["ui_design"],
  "confidence": "low"
}
```

### 3. Calc Response
```json
{
  "status": "ok",
  "estimated_amount": 2112000,
  "estimated_range": {
    "min": 1707200,
    "max": 2516800
  },
  "breakdown": {
    "development": {
      "cost": 1000000,
      "total_days": 20.0
    },
    "phase3_visual": {
      "cost": 920000,
      "total_days": 10.0,
      "range": {
        "min": 552000,
        "max": 1288000
      }
    }
  }
}
```

### 4. Consistency Proof
- **MD**: `ARCHITECTURE_ESTIMATION_SNAPSHOT.md` #7 Vendor Mixed
    - "Variance determined by Confidence: Low (Vague): ±40%"
- **Code**: `estimate-backend-calc/estimate_config.yaml:L68`
    - `low: 0.4`
- **Code**: `estimate-backend-calc/function_app.py:L194`
    - `min`: `phase3_cost * (1 - variance)` -> `920000 * 0.6 = 552000`
    - `max`: `phase3_cost * (1 + variance)` -> `920000 * 1.4 = 1288000`
- **Verdict**: Fully Consistent
