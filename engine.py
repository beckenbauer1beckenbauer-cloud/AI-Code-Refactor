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
    """Sends prompt to Ollama with token limit protection."""
    url = sanitize_url(target_url)

    # Truncate source code if it's excessively large to avoid Ollama CUDA OOM (500 error)
    lines = code.splitlines()
    if len(lines) > 100:
        code = "\n".join(lines[:100]) + "\n# ... [truncated for model memory context]"

    system_prompt = (
        "You are an expert Python engineer. Refactor the provided function to: "
        "1. Add type hints. "
        "2. Add Google-style docstrings. "
        "Return ONLY a raw JSON object with keys 'refactored_code' and 'explanation'. "
        "Do NOT include markdown formatting."
    )

    payload = {
        "model": model_name,
        "prompt": f"{system_prompt}\n\nFunction '{name}' code:\n{code}",
        "stream": False,
        "format": "json",
        "options": {
            "num_ctx": 2048  # Cap context size to prevent Colab GPU memory overload
        }
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
            print(f"❌ Ollama Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Engine failure for '{name}' using {model_name}: {e}")
        return None
