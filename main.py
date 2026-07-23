import sys
import subprocess
import requests
import time
import os
import threading
import importlib

# Importing your modular components
from extractor import run_extraction
from processor import process_and_save_dataset
from plotting import generate_plot
from refactor_and_validate import run_self_healing_pipeline
from generate_analytics_report import run_comparative_analytics

def is_colab():
    """Reliably detects Google Colab environment."""
    if "COLAB_RELEASE_TAG" in os.environ or "COLAB_GPU" in os.environ:
        return True
    try:
        import google.colab
        return True
    except ImportError:
        return os.path.exists("/content")

def run_command(command):
    """Executes shell commands across Colab and local setups."""
    if is_colab():
        from IPython import get_ipython
        if get_ipython():
            get_ipython().system(command)
            return
    subprocess.run(command, shell=True, check=True)

def start_ollama_background():
    """Runs Ollama serve daemon in background."""
    ollama_path = "/usr/local/bin/ollama" if os.path.exists("/usr/local/bin/ollama") else "ollama"
    env = os.environ.copy()
    env["OLLAMA_HOST"] = "127.0.0.1:11434"
    subprocess.Popen([ollama_path, "serve"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def setup_environment():
    """Ensures dependencies and Ollama background service are ready."""
    print("--- 🚀 Initializing Refactoring Pipeline ---")
    
    in_colab = is_colab()
    
    try:
        if requests.get("http://127.0.0.1:11434").status_code == 200:
            print("✅ Ollama server is already active.")
            return
    except requests.exceptions.ConnectionError:
        pass

    print(f"🌍 Environment detected: {'Google Colab' if in_colab else 'Local/Server'}")
    
    if in_colab:
        print("🔧 Installing system dependencies (pciutils, zstd)...")
        subprocess.run("sudo apt-get update -qq && sudo apt-get install -y -qq pciutils zstd", shell=True, check=True)

    ollama_bin = "/usr/local/bin/ollama"
    if not os.path.exists(ollama_bin) and subprocess.run("which ollama", shell=True, capture_output=True).returncode != 0:
        print("📥 Installing Ollama binary...")
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)

    print("⚙️ Spawning background Ollama process...")
    thread = threading.Thread(target=start_ollama_background, daemon=True)
    thread.start()

    print("⏳ Waiting for Ollama server to respond...")
    for attempts in range(30):
        try:
            if requests.get("http://127.0.0.1:11434").status_code == 200:
                print("✅ Ollama server is reachable and ready.")
                return
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    print("❌ Error: Ollama server failed to launch.")
    sys.exit(1)

def setup_model(model_name):
    """Pulls requested model if missing."""
    print(f"\n🔍 Checking for model: {model_name}...")
    try:
        output = subprocess.check_output("ollama list", shell=True).decode()
        if model_name in output:
            print(f"✅ Model '{model_name}' is ready.")
        else:
            print(f"📥 Pulling model '{model_name}'... (this may take a few minutes)")
            run_command(f"ollama pull {model_name}")
    except Exception as e:
        print(f"⚠️ Could not pull model automatically: {e}")

def get_user_model_choice():
    """Prompt user to select an LLM model."""
    models = {
        "1": "llama3.2:3b",
        "2": "qwen2.5:7b",
        "3": "gemma2"
    }
    print("\nSelect an AI Model:")
    for key, model in models.items():
        print(f"{key}. {model}")
    
    choice = input("Enter choice (1-3) or type custom model name (e.g., kimi): ").strip()
    return models.get(choice, choice)

def get_user_library_choice():
    """Allows user to specify which library to extract code from."""
    print("\nSelect a Target Library to Refactor:")
    print("1. requests")
    print("2. urllib.request")
    print("3. json")
    print("4. Custom Library (type name)")
    
    choice = input("Enter choice (1-4 or name): ").strip()
    
    lib_mapping = {
        "1": "requests",
        "2": "urllib.request",
        "3": "json"
    }
    
    lib_name = lib_mapping.get(choice, choice)
    
    try:
        print(f"📦 Importing target library '{lib_name}'...")
        target_lib = importlib.import_module(lib_name)
        return target_lib
    except ImportError:
        print(f"⚠️ Library '{lib_name}' is not installed. Falling back to default 'requests'.")
        import requests as fallback_lib
        return fallback_lib

if __name__ == "__main__":
    # 0. Setup System Environment
    setup_environment()
    
    # 1. Select Model & Library Target
    selected_model = get_user_model_choice()
    setup_model(selected_model)
    
    target_library = get_user_library_choice()
    
    # 2. Extract Data from Chosen Library
    functions = run_extraction(target_library)
    
    if not functions:
        print(f"⚠️ No inspectable Python functions were found in target library. Exiting.")
        sys.exit(0)
    
    # 3. Execution Pipeline
    print("\n--- 🛠️ Starting Refactoring Pipeline ---")
    
    # Run Refactoring
    process_and_save_dataset(functions, model_name=selected_model)
    
    # Run Validation & Self-Healing Loop
    run_self_healing_pipeline(functions, model_name=selected_model)
    
    # Run Analytics & Plotting
    generate_plot("final_dataset_validated.json")
    run_comparative_analytics(model_name=selected_model)
    
    print("\n✅ Pipeline complete. All outputs generated successfully.")
