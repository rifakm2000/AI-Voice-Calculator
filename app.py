# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import re

app = Flask(__name__)
CORS(app)

def evaluate_expression(expr):
    # Clean the expression
    expr = re.sub(r'[^0-9+\-*/().%]', '', expr)
    
    # Handle percentage calculations
    expr = re.sub(r'(\d+(\.\d+)?)%', lambda m: str(float(m.group(1)) / 100), expr)
    
    # Safely evaluate the expression
    try:
        result = eval(expr)
        if isinstance(result, float):
            if result.is_integer():
                return int(result)
        return result
    except:
        raise ValueError("Invalid mathematical expression")

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression', '')
    
    try:
        result = evaluate_expression(expression)
        return jsonify({'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)