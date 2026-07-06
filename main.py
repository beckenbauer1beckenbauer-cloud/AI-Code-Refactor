import requests
import inspect
import json
import time
import matplotlib.pyplot as plt
import numpy as np

# --- FUNCTIONS ---

def extract_functions_from_library(library):
    extracted_data = []
    for name, obj in inspect.getmembers(library):
        if inspect.isfunction(obj):
            try:
                source = inspect.getsource(obj)
                extracted_data.append((name, source))
            except (TypeError, OSError):
                continue
    return extracted_data

def refactor_code_with_ollama(name, code):
    url = "http://localhost:11434/api/generate"
    system_prompt = (
        "You are an expert Python engineer. Refactor the provided function to: "
        "1. Add comprehensive type hints. "
        "2. Add Google-style docstrings. "
        "Return ONLY a raw JSON object with two keys: 'refactored_code' and 'explanation'."
    )
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
    except Exception as e:
        print(f"Engine failure for {name}: {e}")
    return None

def process_and_save_dataset(functions_list, output_file="final_dataset.json"):
    final_dataset = []
    for name, code in functions_list:
        print(f"Processing: {name}...")
        result = refactor_code_with_ollama(name, code)
        if result:
            final_dataset.append({
                "function": name,
                "original_code": code,
                "refactored_code": result.get("refactored_code", ""),
                "explanation": result.get("explanation", "")
            })
        time.sleep(1)
    with open(output_file, "w") as f:
        json.dump(final_dataset, f, indent=4)
    print(f"✅ Saved to {output_file}.")

def refactor_and_validate(name, code):
    refactored_data = refactor_code_with_ollama(name, code)
    if refactored_data is None:
        return code, "Engine failed"
    new_code = refactored_data.get("refactored_code", code)
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except SyntaxError:
        return new_code, "unfixed_error"

def run_self_healing_pipeline(functions_list, output_file="final_dataset_validated.json"):
    validated_dataset = []
    for name, code in functions_list:
        final_code, status = refactor_and_validate(name, code)
        validated_dataset.append({"function": name, "refactored_code": final_code, "status": status})
        with open(output_file, "w") as f:
            json.dump(validated_dataset, f, indent=4)
        time.sleep(1)

def run_comparative_analytics(old_file, new_file):
    with open(old_file, "r") as f: old_data = json.load(f)
    with open(new_file, "r") as f: new_data = json.load(f)
    
    def calculate_metrics(dataset):
        total = len(dataset)
        hints = sum(1 for e in dataset if '->' in e.get('refactored_code', ''))
        return {'type_hint_pct': round((hints/total)*100, 2) if total > 0 else 0}

    m_old = calculate_metrics(old_data)
    m_new = calculate_metrics(new_data)
    print(f"📊 Analytics: Legacy Type Hints {m_old['type_hint_pct']}% -> New {m_new['type_hint_pct']}%")

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    print("🚀 Starting Pipeline...")
    
    # 1. Extract
    functions = extract_functions_from_library(requests)
    
    # 2. Process
    process_and_save_dataset(functions, "final_dataset.json")
    run_self_healing_pipeline(functions, "final_dataset_validated.json")
    
    # 3. Analyze
    run_comparative_analytics("final_dataset.json", "final_dataset_validated.json")
    
    print("🏁 Pipeline Complete.")
