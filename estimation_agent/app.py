"""
Flask wrapper for Prompt Flow Agent - V2 Conversational Chat
Provides REST API endpoints for the estimation agent with conversation management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
from lookup_knowledge import lookup_knowledge
from jinja2 import Template
from openai import AzureOpenAI

app = Flask(__name__)
# Enable CORS for frontend - allow specific origins
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://zealous-river-0efdffa0f.1.azurestaticapps.net",
            "http://localhost:8000",
            "http://localhost:8001",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load the Jinja2 template
with open('generate_response.jinja2', 'r', encoding='utf-8') as f:
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
        self.collected_info = {}
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
    
    def update_info(self, key, value):
        """Update collected information"""
        self.collected_info[key] = value
    
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


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/score', methods=['POST'])
def score():
    """
    Main scoring endpoint for conversational chat
    
    Request JSON:
    {
        "user_input": {
            "message": "user message",
            "selected_option": "optional selected value"
        },
        "session_id": "optional session id",
        "conversation_history": []  # optional, for compatibility
    }
    
    Response JSON:
    {
        "message": "AI response",
        "options": [{"label": "...", "value": "..."}],  # optional
        "is_complete": false,
        "markdown": "...",  # only when is_complete=true
        "session_id": "session id"
    }
    """
    try:
        cleanup_expired_sessions()
        
        data = request.get_json()
        user_input = data.get('user_input', {})
        session_id = data.get('session_id')
        
        # Get or create session
        session = get_or_create_session(session_id)
        
        # Extract user message
        user_message = user_input.get('message', '')
        selected_option = user_input.get('selected_option')
        
        # Add user message to history
        if user_message or selected_option:
            message_content = selected_option if selected_option else user_message
            session.add_message('user', message_content)
        
        # Lookup knowledge from RAG
        knowledge = lookup_knowledge(user_input)
        
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # Render the prompt with conversation history
        prompt = response_template.render(
            user_input=json.dumps(user_input, ensure_ascii=False),
            knowledge=knowledge,
            conversation_history=json.dumps(session.history, ensure_ascii=False) if session.history else None
        )
        
        # Build messages for OpenAI
        messages = []
        
        # Add system message (from template)
        if 'system:' in prompt:
            parts = prompt.split('user:', 1)
            system_content = parts[0].replace('system:', '').strip()
            messages.append({"role": "system", "content": system_content})
            
            if len(parts) > 1:
                user_content = parts[1].strip()
                messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": prompt})
        
        # Call Azure OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=3000
        )
        
        agent_response = response.choices[0].message.content
        
        # Add AI response to history
        session.add_message('assistant', agent_response)
        
        # Parse response to check if conversation is complete
        # Simple heuristic: if response contains markdown header, it's the final output
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
            # Extract options if present (simple parsing)
            # Look for [option] patterns in the response
            import re
            options_pattern = r'\[([^\]]+)\]'
            found_options = re.findall(options_pattern, agent_response)
            
            if found_options:
                options = [{"label": opt, "value": opt} for opt in found_options]
                response_data["options"] = options
        
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
    """List active sessions (for debugging)"""
    return jsonify({
        "active_sessions": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "created_at": session.created_at.isoformat(),
                "message_count": len(session.history),
                "is_complete": session.is_complete
            }
            for sid, session in sessions.items()
        ]
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
