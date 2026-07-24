import sys
import os

# Pinned base directory fix BEFORE imports
BASE_DIR = "/content" if os.path.exists("/content") else "/tmp"
os.chdir(BASE_DIR)
os.environ["OLLAMA_MODELS"] = os.path.expanduser("~/.ollama/models")

import shutil
import time
import subprocess
import urllib.request
from package_resolver import resolve_and_install_package
from extractor import extract_functions_deep
from refactor_and_validate import run_self_healing_pipeline
from plotting import generate_plot
from generate_analytics_report import run_comparative_analytics

def ensure_ollama_running():
    """Ensures Ollama service is active and pinned to BASE_DIR."""
    url = "http://127.0.0.1:11434/api/version"
    try:
        urllib.request.urlopen(url, timeout=3)
        return
    except Exception:
        pass

    if not shutil.which("ollama"):
        print("❌ Error: 'ollama' binary is not installed on this system.")
        print("👉 Please execute 'bash setup.sh' prior to running main.py.")
        sys.exit(1)

    print(f"⚡ Starting background Ollama process from {BASE_DIR}...")
    
    # Environment copy with absolute paths
    env = os.environ.copy()
    
    subprocess.Popen(
        ["ollama", "serve"],
        cwd=BASE_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    for _ in range(10):
        try:
            urllib.request.urlopen(url, timeout=2)
            print("✅ Ollama started successfully.")
            return
        except Exception:
            time.sleep(2)

    print("❌ Failed to start Ollama server.")
    sys.exit(1)

def ensure_model_installed(model_name):
    """Verifies model exists locally; downloads it dynamically if missing."""
    print(f"🔍 Checking if model '{model_name}' is downloaded...")
    try:
        res = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True, 
            check=True, 
            cwd=BASE_DIR
        )
        if model_name not in res.stdout:
            print(f"📥 Model '{model_name}' not found locally. Pulling '{model_name}' now...")
            subprocess.run(
                ["ollama", "pull", model_name], 
                check=True, 
                cwd=BASE_DIR
            )
            print(f"✅ Model '{model_name}' successfully downloaded!")
        else:
            print(f"✅ Model '{model_name}' is ready.")
    except Exception as e:
        print(f"⚠️ Warning during model check: {e}")

def select_model():
    print("\nSelect Ollama Model:")
    print("1. qwen2.5:7b")
    print("2. llama3.2:3b")
    print("3. deepseek-r1:7b")

    choice = input("Enter choice (1-3) [default: 1]: ").strip()
    models = {"1": "qwen2.5:7b", "2": "llama3.2:3b", "3": "deepseek-r1:7b"}
    selected = models.get(choice, "qwen2.5:7b")

    ensure_model_installed(selected)
    return selected

def main():
    # Make sure process is anchored in BASE_DIR
    os.chdir(BASE_DIR)
    ensure_ollama_running()

    print("=" * 60)
    print("🤖 Universal AI Refactoring Pipeline")
    print("=" * 60)

    target_input = input("Enter ANY Python library name (e.g., scikit-learn, httpx, django, scipy): ").strip()
    if not target_input:
        target_input = "scikit-learn"

    model_name = select_model()

    # Step 1: Resolve Package & Auto-Install
    module, pip_name, import_name = resolve_and_install_package(target_input, model_name=model_name)
    if not module:
        print(f"❌ Pipeline halted: Unable to process target '{target_input}'.")
        return

    # Reset directory after package installation to keep Ollama valid
    os.chdir(BASE_DIR)

    # Step 2: Extract Source Code
    print(f"\n⚙️ Extracting functions from '{import_name}'...")
    functions = extract_functions_deep(module, max_functions=10)

    if not functions:
        print(f"⚠️ No pure Python functions with source code found in '{import_name}'.")
        return

    print(f"✅ Extracted {len(functions)} functions from '{import_name}':")
    for fname, _ in functions:
        print(f"   • {fname}")

    # Step 3: Refactor & Validate
    validated_file = os.path.join(BASE_DIR, f"dataset_{import_name}_validated.json")
    run_self_healing_pipeline(functions, model_name=model_name, output_file=validated_file)

    # Step 4: Charts
    generate_plot(dataset_file=validated_file, library_name=import_name)

    # Step 5: Report
    report_file = os.path.join(BASE_DIR, f"report_{import_name}.md")
    run_comparative_analytics(model_name=model_name, input_file=validated_file, library_name=import_name, report_file=report_file)

    print(f"\n🎉 Pipeline completed successfully for '{import_name}'!")

if __name__ == "__main__":
    main()
