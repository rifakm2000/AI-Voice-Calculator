from flask import Flask, request, jsonify
from flask_cors import CORS
import numexpr as ne
import math
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/')
def home():
    return "AI Voice Calculator API is running."

@app.route('/calculate', methods=['POST'])
def calculate():
    """Receive an expression from frontend, process it, and return the result."""
    data = request.json
    expression = data.get("expression", "")
    
    # Process the expression for scientific calculations
    try:
        # Convert spoken words to mathematical symbols and functions
        expression = preprocess_expression(expression)
        
        # Create a safe environment with scientific functions
        safe_globals = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "log": math.log10,
            "ln": math.log,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
            "abs": abs,
            "pow": pow,
            "radians": math.radians,
            "degrees": math.degrees,
            "floor": math.floor,
            "ceil": math.ceil,
            "round": round,
            "np": np
        }
        
        # Evaluate the expression
        result = ne.evaluate(expression, local_dict=safe_globals)
        
        # Format the result (handle different numeric types)
        if isinstance(result, (np.ndarray, list)):
            result = str(result)
        else:
            # Format floating point numbers to be more readable
            try:
                if isinstance(result, (float, np.float64, np.float32)):
                    # If close to integer, convert to int
                    if abs(result - round(result)) < 1e-10:
                        result = int(round(result))
                    # Otherwise limit decimal places for readability
                    else:
                        result = float(f"{result:.10g}")
            except:
                pass
                
        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"error": f"Invalid expression: {str(e)}"}), 400

def preprocess_expression(expression):
    """Convert spoken words to mathematical notation and functions."""
    # Convert to lowercase for easier replacement
    expression = expression.lower()
    
    # Basic operators
    expression = expression.replace("plus", "+").replace("minus", "-") \
        .replace("times", "*").replace("into", "*").replace("multiplied by", "*") \
        .replace("divided by", "/").replace("divide by", "/").replace("over", "/")
    
    # Advanced mathematical functions
    replacements = {
        "square root": "sqrt",
        "square root of": "sqrt(",
        "cube root": "pow(x, 1/3)",
        "cube root of": "pow(",
        "sine": "sin",
        "sin": "sin",
        "cosine": "cos",
        "cos": "cos",
        "tangent": "tan",
        "tan": "tan",
        "logarithm": "log10",
        "log": "log10",
        "natural log": "ln",
        "ln": "ln",
        "exponential": "exp",
        "power": "pow",
        "raised to the power": "**",
        "to the power of": "**",
        "squared": "**2",
        "cubed": "**3",
        "factorial": "math.factorial",
        "absolute value": "abs"
    }
    
    for word, replacement in replacements.items():
        if word + " of" in expression:
            expression = expression.replace(word + " of", replacement + "(")
        else:
            expression = expression.replace(word, replacement)
    
    # Replace constants
    expression = expression.replace("pi", "pi").replace("e", "e")
    
    # Check for incomplete parentheses
    open_count = expression.count("(")
    close_count = expression.count(")")
    if open_count > close_count:
        expression += ")" * (open_count - close_count)
    
    return expression

if __name__ == '__main__':
    app.run(debug=True)