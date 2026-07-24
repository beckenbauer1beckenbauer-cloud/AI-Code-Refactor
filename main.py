import sys
import subprocess
import urllib.request
from package_resolver import resolve_and_install_package
from extractor import extract_functions_deep
from refactor_and_validate import run_self_healing_pipeline
from plotting import generate_plot
from generate_analytics_report import run_comparative_analytics
import shutil
import time

def ensure_ollama_running():
    """Checks if Ollama is active; attempts background launch if missing."""
    url = "http://127.0.0.1:11434/api/version"
    
    # Check if already running
    try:
        urllib.request.urlopen(url, timeout=3)
        return
    except Exception:
        pass

    # Verify executable exists before running Popen
    if not shutil.which("ollama"):
        print("❌ Error: 'ollama' binary is not installed on this system.")
        print("👉 Please execute 'bash setup.sh' prior to running main.py.")
        exit(1)

    print("⚡ Starting background Ollama process...")
    subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for service to come online
    for _ in range(10):
        try:
            urllib.request.urlopen(url, timeout=2)
            print("✅ Ollama started successfully.")
            return
        except Exception:
            time.sleep(2)
            
    print("❌ Failed to reach Ollama server after starting.")
    exit(1)

def select_model():
    print("\nSelect Ollama Model:")
    print("1. qwen2.5:7b")
    print("2. llama3.2:3b")
    print("3. deepseek-r1:7b")
    
    choice = input("Enter choice (1-3) [default: 1]: ").strip()
    models = {"1": "qwen2.5:7b", "2": "llama3.2:3b", "3": "deepseek-r1:7b"}
    return models.get(choice, "qwen2.5:7b")

def main():
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
    validated_file = f"dataset_{import_name}_validated.json"
    run_self_healing_pipeline(functions, model_name=model_name, output_file=validated_file)

    # Step 4: Charts
    generate_plot(dataset_file=validated_file, library_name=import_name)

    # Step 5: Report
    report_file = f"report_{import_name}.md"
    run_comparative_analytics(model_name=model_name, input_file=validated_file, library_name=import_name, report_file=report_file)

    print(f"\n🎉 Pipeline completed successfully for '{import_name}'!")

if __name__ == "__main__":
    main()
