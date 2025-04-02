# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import re
import os

app = Flask(__name__)

# Enable CORS for all domains - this is crucial for cross-device access
# In production, you should restrict this to your specific domain
CORS(app, resources={r"/*": {"origins": "*"}})

def evaluate_expression(expr):
    # Clean the expression - only allow safe characters
    expr = re.sub(r'[^0-9+\-*/().%\s]', '', expr)
    
    # Security check - reject potentially harmful inputs
    if '__' in expr or 'import' in expr or 'eval' in expr or 'exec' in expr:
        raise ValueError("Invalid expression")
    
    # Handle percentage calculations
    expr = re.sub(r'(\d+(\.\d+)?)%', lambda m: str(float(m.group(1)) / 100), expr)
    
    # Safely evaluate the expression
    try:
        # Using eval with restricted globals/locals for better security
        result = eval(expr, {"__builtins__": {}}, {"math": math})
        if isinstance(result, float):
            if result.is_integer():
                return int(result)
        return result
    except Exception as e:
        raise ValueError(f"Invalid mathematical expression: {str(e)}")

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    
    if not data or 'expression' not in data:
        return jsonify({'error': 'Missing expression parameter'}), 400
        
    expression = data.get('expression', '')
    
    try:
        result = evaluate_expression(expression)
        return jsonify({'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/', methods=['GET'])
def home():
    return """
    <html>
        <head><title>Calculator API</title></head>
        <body>
            <h1>Calculator API is running</h1>
            <p>Use POST /calculate endpoint with JSON payload: {"expression": "your_expression"}</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    # Get port from environment variable
    app.run(debug=True)