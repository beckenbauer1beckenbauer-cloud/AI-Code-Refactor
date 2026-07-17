import requests
import json

def refactor_code(name, code, model_name="llama3.2:3b"):
    """
    Sends the raw function code to the local Ollama instance and
    returns the refactored code and explanation in JSON format.
    
    Args:
        name (str): Name of the function.
        code (str): The raw source code.
        model_name (str): The Ollama model to use (e.g., 'llama3.2:3b', 'qwen', 'gemma').
    """
    url = "http://localhost:11434/api/generate"

    system_prompt = (
        "You are an expert Python engineer. Refactor the provided function to: "
        "1. Add comprehensive type hints. "
        "2. Add Google-style docstrings (Parameters, Returns, Raises). "
        "3. Improve code structure if needed. "
        "Return ONLY a raw JSON object with two keys: 'refactored_code' and 'explanation'."
    )

    payload = {
        "model": model_name,
        "prompt": f"{system_prompt}\n\nFunction '{name}' code:\n{code}",
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            # Most Ollama models return the JSON in the 'response' field
            return json.loads(data.get('response', '{}'))
        else:
            print(f"❌ Error: Server returned {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Engine failure for {name} with model {model_name}: {e}")
        return None
