"""
Flask wrapper for Prompt Flow Agent
Provides REST API endpoints for the estimation agent
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from call_calc_tool import call_calc
from lookup_knowledge import lookup_knowledge
from jinja2 import Template

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Load the Jinja2 template
with open('generate_response.jinja2', 'r') as f:
    template_content = f.read()
    response_template = Template(template_content)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/score', methods=['POST'])
def score():
    """
    Main scoring endpoint
    Expects JSON: {"user_input": {...}}
    Returns JSON: {"response": "..."}
    """
    try:
        data = request.get_json()
        user_input = data.get('user_input', {})
        
        # Step 1: Call calc API
        calc_result = call_calc(user_input)
        
        # Step 2: Lookup knowledge
        knowledge = lookup_knowledge(user_input)
        
        # Step 3: Generate response using LLM
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # Render the prompt
        prompt = response_template.render(
            user_input=json.dumps(user_input),
            calc_result=json.dumps(calc_result),
            knowledge=knowledge
        )
        
        # Call Azure OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは親切で知識豊富なシステム開発の見積もりアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        agent_response = response.choices[0].message.content
        
        return jsonify({"response": agent_response}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
