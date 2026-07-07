import requests
import json
import logging

logger = logging.getLogger(__name__)

def refactor_code_with_ollama(name, code, model="llama3.2:3b"):
    """
    Sends the raw function code to the local Ollama instance and 
    returns the refactored code and explanation in JSON format.
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
        "model": model,
        "prompt": f"{system_prompt}\n\nFunction '{name}' code:\n{code}",
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return json.loads(data['response'])
        else:
            logger.error(f"Server returned {response.status_code} for function {name}")
            return None
    except Exception as e:
        logger.error(f"Engine failure for {name}: {e}")
        return None
