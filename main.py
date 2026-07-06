import requests
import inspect
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os

# --- 1. UTILITY FUNCTIONS ---

def ensure_ollama_running():
    """Checks if Ollama is reachable; if not, attempts to restart it."""
    try:
        requests.get("http://localhost:11434", timeout=3)
        return True
    except:
        print("⚠️ Ollama offline. Attempting to start...")
        subprocess.Popen(["ollama", "serve"], stdout=open("ollama.log", "w"), stderr=subprocess.STDOUT)
        for i in range(15):
            time.sleep(2)
            try:
                requests.get("http://localhost:11434", timeout=3)
                return True
            except: continue
        return False

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
    payload = {
        "model": "llama3.2:3b",
        "prompt": f"Refactor Python code for '{name}'. Return ONLY JSON with 'refactored_code' and 'explanation'.\n\nCode:\n{code}",
        "stream": False,
        "format": "json"
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            return json.loads(response.json()['response'])
    except Exception as e:
        print(f"Engine failure for {name}: {e}")
    return None

# --- 2. PIPELINE FUNCTIONS ---

def process_and_save_dataset(functions_list, output_file):
    final_dataset = []
    print(f"🚀 Processing {len(functions_list)} functions...")
    for name, code in functions_list:
        result = refactor_code_with_ollama(name, code)
        if result:
            final_dataset.append({
                "function": name,
                "original_code": code,
                "refactored_code": result.get("refactored_code", code),
                "explanation": result.get("explanation", "")
            })
        time.sleep(1)
    with open(output_file, "w") as f:
        json.dump(final_dataset, f, indent=4)
    print(f"✅ Saved to {output_file}")

def refactor_and_validate(name, code):
    data = refactor_code_with_ollama(name, code)
    if not data or "refactored_code" not in data:
        return code, "Engine failed"
    new_code = data["refactored_code"]
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except SyntaxError:
        return new_code, "unfixed_error"

def run_self_healing_pipeline(functions_list, output_file):
    validated_dataset = []
    for name, code in functions_list:
        final_code, status = refactor_and_validate(name, code)
        validated_dataset.append({"function": name, "refactored_code": final_code, "status": status})
    with open(output_file, "w") as f:
        json.dump(validated_dataset, f, indent=4)
    print(f"✅ Validated dataset saved.")

def run_comparative_analytics(old_file, new_file):
    with open(old_file, "r") as f: old_data = json.load(f)
    with open(new_file, "r") as f: new_data = json.load(f)
    
    names = [e['function'] for e in old_data]
    orig_lens = [len(e.get('original_code', '')) for e in old_data]
    ref_lens = [len(e.get('refactored_code', '')) for e in new_data]

    plt.figure(figsize=(12, 6))
    plt.bar(names, orig_lens, label='Original')
    plt.bar(names, ref_lens, label='Refactored', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.savefig("comparative_analysis.png")
    print("📊 Plot saved: comparative_analysis.png")

# --- 3. EXECUTION GUARD ---

if __name__ == "__main__":
    if not ensure_ollama_running():
        print("❌ Ollama not reachable.")
        exit(1)

    try:
        functions = extract_functions_from_library(requests)
        process_and_save_dataset(functions, "final_dataset.json")
        run_self_healing_pipeline(functions, "final_dataset_validated.json")
        run_comparative_analytics("final_dataset.json", "final_dataset_validated.json")
        print("🏁 Pipeline finished.")
    except Exception as e:
        print(f"❌ Critical Failure: {e}")
