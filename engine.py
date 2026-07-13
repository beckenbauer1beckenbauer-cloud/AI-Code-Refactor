import json
import re
import requests

def refactor_code_with_engine(name, code):
    """
    Refactors code using the engine specified in engine_state.json.
    Includes robust JSON sanitization to prevent crashes.
    """
    with open("engine_state.json", "r") as f:
        engine_state = json.load(f)

    # 1. Define strict prompt
    system_instruction = (
        "You are an expert Python engineer. "
        "Return ONLY a raw JSON object with keys: 'refactored_code' and 'explanation'. "
        "Do not include markdown, code blocks, or introductory text."
    )
    full_prompt = f"{system_instruction}\n\nTask: Refactor this function:\n{code}"

    raw_output = None

    # --- ENGINE: OLLAMA ---
    if engine_state['engine'] == "ollama":
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": engine_state.get("model_id", "llama3.2:3b"),
            "prompt": full_prompt,
            "stream": False,
            "format": "json"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                raw_output = response.json().get('response')
        except Exception as e:
            print(f"Engine failure (Ollama) for {name}: {e}")

    # --- ENGINE: NATIVE ---
    elif engine_state['engine'] == "native":
        try:
            from llama_cpp import Llama
            llm = Llama(model_path=engine_state['model_file'], verbose=False)
            output = llm.create_chat_completion(
                messages=[{"role": "user", "content": full_prompt}],
                response_format={"type": "json_object"}
            )
            raw_output = output['choices'][0]['message']['content']
        except Exception as e:
            print(f"Engine failure (Native) for {name}: {e}")

    # --- SANITIZATION (The part you were missing) ---
    if raw_output:
        try:
            # Strip whitespace and markdown blocks
            clean_output = raw_output.strip()
            clean_output = re.sub(r'^```json\s*', '', clean_output, flags=re.IGNORECASE)
            clean_output = re.sub(r'```$', '', clean_output).strip()
            
            return json.loads(clean_output)
        except json.JSONDecodeError:
            print(f"❌ JSON Parsing failed for {name}. Raw output was: {raw_output}")
            return None
            
    return None
