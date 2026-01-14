"""
Flask wrapper for Prompt Flow Agent - V2 Conversational Chat
Provides REST API endpoints for the estimation agent with conversation management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid
import re
from datetime import datetime
from lookup_knowledge import lookup_knowledge
from jinja2 import Template
from openai import AzureOpenAI
from call_calc_tool import call_calc

app = Flask(__name__)
# Enable CORS for frontend - allow specific origins
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://zealous-river-0efdffa0f.1.azurestaticapps.net",
            "http://localhost:8000",
            "http://localhost:8080",
            "http://localhost:8001",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load the Jinja2 template
# Use absolute path relative to this file
template_path = os.path.join(os.path.dirname(__file__), 'generate_response.jinja2')
with open(template_path, 'r', encoding='utf-8') as f:
    template_content = f.read()
    response_template = Template(template_content)

# In-memory session storage (for simplicity)
# In production, use Redis or database
sessions = {}


class ConversationSession:
    """Manages a conversation session"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.history = []
        # Stores CONFIRMED parameters for calculation
        self.collected_params = {
            "method": None, # Must be explicitly selected (Constitution enforcement)
            "features": [],
            "phase2_items": [],
            "phase3_items": [],
            "screen_count": None,
            "complexity": None,
            "loc": None,
            "fp_count": None,
            "man_days_per_unit": None,
            "confidence": None # Phase 3: Design Confidence
        }
        # Immutable Estimation Snapshot (Params + Result + Timestamp)
        self.estimation_snapshot = None
        self.created_at = datetime.now()
        self.is_complete = False
        self.final_markdown = None
    
    def add_message(self, role, content):
        """Add a message to conversation history"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def update_param(self, key, value):
        """Update collected information (Explicit Confirmation Only)"""
        if key in ["features", "phase2_items", "phase3_items"]:
            if isinstance(value, list):
                for v in value:
                    if v not in self.collected_params[key]:
                        self.collected_params[key].append(v)
            else:
                 if value not in self.collected_params[key]:
                        self.collected_params[key].append(value)
        else:
            # Scalar values are overwritten
             self.collected_params[key] = value

    def is_expired(self):
        """Check if session is expired (1 hour)"""
        return (datetime.now() - self.created_at).seconds > 3600


def get_or_create_session(session_id=None):
    """Get existing session or create new one"""
    if session_id and session_id in sessions:
        session = sessions[session_id]
        if not session.is_expired():
            return session
        else:
            # Session expired, remove it
            del sessions[session_id]
    
    # Create new session
    new_session_id = session_id or str(uuid.uuid4())
    session = ConversationSession(new_session_id)
    sessions[new_session_id] = session
    return session


def cleanup_expired_sessions():
    """Remove expired sessions"""
    expired = [sid for sid, session in sessions.items() if session.is_expired()]
    for sid in expired:
        del sessions[sid]

# Mapping from Japanese labels to English keys (for UI options -> Param keys)
PARAM_MAPPING = {
    # Methods
    "STEP法": "step", "LOC法": "step", "Step": "step",
    "FP法": "fp", "Function Point": "fp",
    "画面数法": "screen", "Screen Count": "screen",

    # Features
    "ユーザー認証": "auth", "認証": "auth",
    "一覧表示・検索": "list_search", "検索": "list_search", "一覧": "list_search",
    "詳細表示": "detail_view", "詳細": "detail_view",
    "CRUD操作": "crud", "登録・編集": "crud",
    "決済機能": "payment", "決済": "payment",
    "プッシュ通知": "push_notification", "通知": "push_notification",
    "リアルタイム機能": "realtime", "チャット": "realtime",
    "外部API連携": "external_api", "API連携": "external_api",
    "データ移行": "data_migration",
    "管理画面": "admin_panel",
    
    # Complexity
    "簡易": "low", "シンプル": "low",
    "標準": "medium", "一般的": "medium",
    "高難度": "high", "複雑": "high",
    
    # Phase 2
    "IA設計": "ia_design",
    "WF作成": "wireframe",
    "Figma化": "figma",
    
    # Phase 3
    "UIデザイン": "ui_design",
    "デザインシステム": "design_system",
    "プロトタイプ": "prototype",
    "アイコン・ロゴ": "logo_icon",

    # Confidence (Design Readiness)
    "要件がまだ曖昧": "low", "Low Confidence": "low", "概算レベル": "low", "Vague": "low",
    "標準的": "medium", "Standard": "medium",
    "仕様確定済み": "high", "High Confidence": "high", "Concrete": "high", "詳細仕様あり": "high"
}

def extract_number(value_str):
    """Robustly extract first float/int from string value"""
    match = re.search(r'(\d+(\.\d+)?)', str(value_str))
    if match:
        return float(match.group(1))
    return None

@app.route('/', methods=['GET'])
def index():
    """Root endpoint for default health probe"""
    return jsonify({"service": "Estimation Agent V2", "status": "running"}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/score', methods=['POST'])
def score():
    """Main scoring endpoint"""
    try:
        cleanup_expired_sessions()
        
        data = request.get_json()
        user_input = data.get('user_input', {})
        session_id = data.get('session_id')
        
        session = get_or_create_session(session_id)
        
        client_history = data.get('conversation_history', [])
        if not session.history and client_history:
            session.history = client_history
        
        user_message = user_input.get('message', '')
        selected_option = user_input.get('selected_option') # This is the explicit intent
        method_only_ack = False
        
        # --- PHASE 2/3 LOGIC: Explicit Param Collection ---
        
        if selected_option:
            session.add_message('user', selected_option)
             
            # 1. Trigger
            if selected_option in ["CALCULATE_ESTIMATE", "見積もり作成", "計算する"]:
                pass 
            
            # 1.5 Method keys (direct)
            elif selected_option in ["screen", "step", "fp"]:
                session.update_param("method", selected_option)
                method_only_ack = True

            # 2. Map Params
            elif selected_option in PARAM_MAPPING:
                key = PARAM_MAPPING[selected_option]
                
                # Method Selection
                if key in ["step", "fp", "screen"]:
                    session.update_param("method", key)
                    method_only_ack = True
                
                # Complexity
                elif key in ["low", "medium", "high"]:
                    if "難度" in selected_option or "複雑" in selected_option or "簡易" in selected_option:
                        session.update_param("complexity", key)
                    elif "曖昧" in selected_option or "確定" in selected_option or "概算" in selected_option or "詳細仕様" in selected_option:
                        session.update_param("confidence", key)
                    else:
                        session.update_param("complexity", key)
                
                # Phase 2/3
                elif key in ["ia_design", "wireframe", "figma"]:
                    session.update_param("phase2_items", key)
                elif key in ["ui_design", "design_system", "prototype", "logo_icon"]:
                    session.update_param("phase3_items", key)
                
                # Default Features
                else: 
                     session.update_param("features", key)
            
            # 3. Numeric Extractions (Heuristics based on labels)
            else:
                 val = extract_number(selected_option)
                 if val is not None:
                     # --- CONSTITUTION ENFORCEMENT: METHOD FIRST ---
                     if session.collected_params["method"] is None:
                         # Physical Refusal of Input
                         warning_msg = (
                             "【システム警告】見積り手法が未決定です。\n\n"
                             "数値を入力する前に、まず採用する「見積り手法」を選択（確定）してください。\n"
                             "これはTERASOLUNAの合意形成プロセスに基づく必須手順です。"
                         )
                         return jsonify({
                             "message": warning_msg,
                             "options": [
                                 {"label": "画面数法 (Screen)", "value": "画面数法"},
                                 {"label": "STEP法 (LOC)", "value": "STEP法"},
                                 {"label": "FP法 (Function Point)", "value": "FP法"}
                             ],
                             "is_complete": False,
                             "session_id": session.session_id
                         }), 200

                     # Heuristics: Context needed? Or just check keywords in label
                     if "画面" in selected_option and "数" not in selected_option and "率" not in selected_option: 
                         # Assumes e.g. "20画面" but not "画面数法" or "生産性0.8"
                         session.update_param("screen_count", int(val))
                     elif "LOC" in selected_option or "step" in selected_option.lower():
                         session.update_param("loc", int(val))
                     elif "FP" in selected_option and "day" not in selected_option: # "100 FP"
                         session.update_param("fp_count", int(val))
                     elif "人日" in selected_option or "day" in selected_option.lower():
                         # Productivity (man_days_per_unit)
                         session.update_param("man_days_per_unit", val)
                     elif "screen_count" in session.collected_params.get("method", "screen"): 
                         # Fallback if just a number and method is screen (e.g. "[20]")
                         session.update_param("screen_count", int(val))

        elif user_message:
            session.add_message('user', user_message)

        # 4. Calculation
        calc_result_json = None
        should_calculate = (selected_option in ["CALCULATE_ESTIMATE", "見積もり作成", "計算する"])
        
        if method_only_ack and not should_calculate:
            response_data = {
                "message": "了解、手法を記録した。",
                "is_complete": False,
                "session_id": session.session_id
            }
            return jsonify(response_data), 200
        
        if should_calculate:
            params = session.collected_params
            result_str = call_calc(
                api_version="v2", # Phase 2 Version
                method=params["method"],
                screen_count=params["screen_count"],
                features=params["features"],
                complexity=params["complexity"],
                phase2_items=params["phase2_items"],
                phase3_items=params["phase3_items"],
                loc=params["loc"],
                fp_count=params["fp_count"],
                man_days_per_unit=params["man_days_per_unit"],
                confidence=params["confidence"]
            )
            result_json = json.loads(result_str)
            
            if result_json.get("status") == "error":
                if result_json.get("error_type") == "validation_error":
                    missing = result_json.get("missing_fields", [])
                    calc_result_json = {"error": "missing_params", "missing": missing}
                else:
                    calc_result_json = {"error": "api_error", "details": result_json.get("message")}
            else:
                # Success - PERSIST IMMUTABLE SNAPSHOT
                calc_result_json = result_json
                session.estimation_snapshot = {
                    "params": params.copy(),
                    "result": result_json,
                    "timestamp": datetime.now().isoformat(),
                    "schema_version": "v2"
                }

        knowledge = lookup_knowledge(user_input)
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        prompt = response_template.render(
            user_input=json.dumps(user_input, ensure_ascii=False),
            knowledge=knowledge,
            conversation_history=json.dumps(session.history, ensure_ascii=False),
            collected_params=json.dumps(session.collected_params, ensure_ascii=False),
            calc_result=json.dumps(calc_result_json, ensure_ascii=False) if calc_result_json else None
        )
        
        messages = []
        if 'system:' in prompt:
            parts = prompt.split('user:', 1)
            system_content = parts[0].replace('system:', '').strip()
            messages.append({"role": "system", "content": system_content})
            if len(parts) > 1:
                messages.append({"role": "user", "content": parts[1].strip()})
        else:
            messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=4000 
        )
        
        agent_response = response.choices[0].message.content
        session.add_message('assistant', agent_response)
        
        is_complete = '# プロジェクト見積もり・提案書' in agent_response
        
        response_data = {
            "message": agent_response,
            "is_complete": is_complete,
            "session_id": session.session_id
        }
        
        if is_complete:
            session.is_complete = True
            session.final_markdown = agent_response
            response_data["markdown"] = agent_response
        else:
            options_bracket = re.findall(r'\[([^\]\n]+)\](?!\()', agent_response)
            potential_list_items = re.findall(r'^\s*[-ー•*1-9][\.\)\s]+([^\n\[\]]+)', agent_response, re.MULTILINE)
            candidates = options_bracket + potential_list_items
            unique_options = []
            seen = set()
            for opt in candidates:
                clean_opt = re.sub(r'[\[\]\*]', '', opt).strip()
                if ': ' in clean_opt: clean_opt = clean_opt.split(': ')[0].strip()
                if clean_opt and clean_opt not in seen and len(clean_opt) < 40:
                    if not clean_opt.startswith(('#', 'http://', 'https://')):
                        unique_options.append({"label": clean_opt, "value": clean_opt})
                        seen.add(clean_opt)
            if unique_options:
                response_data["options"] = unique_options

        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]
        return jsonify({"message": "Session deleted"}), 200
    return jsonify({"error": "Session not found"}), 404

@app.route('/sessions', methods=['GET'])
def list_sessions():
    """List active sessions"""
    return jsonify({
        "active_sessions": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "created_at": session.created_at.isoformat(),
                "collected_params": session.collected_params
            }
            for sid, session in sessions.items()
        ]
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
