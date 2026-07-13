import json
import re
import requests

def refactor_code_with_engine(name, code):
    """
    Refactors code using the engine specified in engine_state.json.
    Includes context-window expansion and automated JSON repair.
    """
    with open("engine_state.json", "r") as f:
        engine_state = json.load(f)

    # Strict, token-efficient system instruction
    system_instruction = (
        "Output ONLY valid JSON. Structure: {'refactored_code': '...', 'explanation': '...'}. "
        "Do not include markdown or explanations outside JSON."
    )
    full_prompt = f"{system_instruction}\n\nTask: Refactor this function:\n{code}"

    raw_output = None

    # --- ENGINE: OLLAMA ---
    if engine_state.get('engine') == "ollama":
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": engine_state.get("model_id", "llama3.2:3b"),
            "prompt": full_prompt,
            "stream": False,
            "format": "json"
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                raw_output = response.json().get('response')
        except Exception as e:
            print(f"Engine failure (Ollama) for {name}: {e}")

    # --- ENGINE: NATIVE ---
    elif engine_state.get('engine') == "native":
        try:
            from llama_cpp import Llama
            # n_ctx=2048 solves the "token limit exceeded" error
            llm = Llama(
                model_path=engine_state['model_file'], 
                n_ctx=2048, 
                verbose=False
            )
            output = llm.create_chat_completion(
                messages=[{"role": "user", "content": full_prompt}],
                response_format={"type": "json_object"}
            )
            raw_output = output['choices'][0]['message']['content']
        except Exception as e:
            print(f"Engine failure (Native) for {name}: {e}")

    # --- ROBUST SANITIZATION & AUTO-REPAIR ---
    if raw_output:
       if raw_output:
        try:
            # 1. Clean markdown blocks
            clean_output = re.sub(r'^```json\s*', '', raw_output, flags=re.IGNORECASE)
            clean_output = re.sub(r'```$', '', clean_output).strip()
            
            # 2. FIX: Manual escape cleanup 
            # The model is adding double backslashes (\\*) that break JSON
            clean_output = clean_output.replace('\\\\', '\\')
            
            # 3. Repair truncated JSON (Auto-closing braces)
            if clean_output.count('{') > clean_output.count('}'):
                clean_output += '}'
            
            return json.loads(clean_output)
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parsing failed: {e}")
            print(f"Raw output was: {raw_output}")
            return None
            
    return None

def ai_debug_and_rewrite(script_path, error_log):
    with open(script_path, "r") as f:
        broken_code = f.read()
        
    prompt = f"File {script_path} crashed with error: {error_log}. Rewrite the code to fix this error. Output ONLY the fixed code."
    
    # Get fix from engine
    result = refactor_code_with_engine("DebugAgent", prompt)
    
    if result and 'refactored_code' in result:
        with open(script_path, "w") as f:
            f.write(result['refactored_code'])
        return True
    return False
