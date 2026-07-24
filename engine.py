import requests
import json
import re

def sanitize_url(raw_url):
    """Strips brackets, parens, and markdown formatting from URL strings."""
    if not isinstance(raw_url, str):
        raw_url = str(raw_url)
    match = re.search(r"https?://[^\s\]\)\'\"]+", raw_url)
    if match:
        return match.group(0)
    return "http://127.0.0.1:11434/api/generate"

def clean_json_response(raw_text):
    """Extracts clean JSON from raw LLM output."""
    if not isinstance(raw_text, str):
        return {}
        
    raw_text = re.sub(r"^```json\s*", "", raw_text.strip(), flags=re.MULTILINE)
    raw_text = re.sub(r"^```python\s*", "", raw_text.strip(), flags=re.MULTILINE)
    raw_text = re.sub(r"^```\s*", "", raw_text.strip(), flags=re.MULTILINE)
    raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
    return {}

def refactor_code(name, code, model_name="qwen2.5:7b", target_url="[http://127.0.0.1:11434/api/generate](http://127.0.0.1:11434/api/generate)"):
    """Sends prompt to Ollama and returns sanitized JSON."""
    url = sanitize_url(target_url)

    system_prompt = (
        "You are an expert Python engineer. Refactor the provided function to: "
        "1. Add comprehensive type hints. "
        "2. Add Google-style docstrings (Parameters, Returns, Raises). "
        "3. Improve code structure if needed. "
        "Return ONLY a raw JSON object with two keys: 'refactored_code' and 'explanation'. "
        "Do NOT surround your response with markdown code blocks like ```json."
    )

    payload = {
        "model": model_name,
        "prompt": f"{system_prompt}\n\nFunction '{name}' code:\n{code}",
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            raw_response = data.get('response', '')
            parsed = clean_json_response(raw_response)
            
            if "refactored_code" in parsed and not isinstance(parsed["refactored_code"], str):
                parsed["refactored_code"] = str(parsed["refactored_code"])
                
            return parsed
        else:
            print(f"❌ Error: Server returned status code {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Engine failure for '{name}' using {model_name}: {e}")
        return None
