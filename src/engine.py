import requests
import json

def refactor_code_with_ollama(name, code, system_prompt):
    """Sends code to the local Ollama instance."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2:3b",
        "prompt": f"{system_prompt}\n\nFunction '{name}' code:\n{code}",
        "stream": False,
        "format": "json"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return json.loads(response.json()['response'])
        return None
    except Exception as e:
        print(f"Engine failure for {name}: {e}")
        return None
