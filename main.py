import sys
import subprocess
import requests
import time
import os
import threading

# Importing your modular components
from extractor import run_extraction
from processor import process_and_save_dataset
from plotting import generate_plot
from refactor_and_validate import run_self_healing_pipeline
from generate_analytics_report import run_comparative_analytics

def is_colab():
    """Reliably detects if code is executing in Google Colab (even inside python subprocesses)."""
    if "COLAB_RELEASE_TAG" in os.environ or "COLAB_GPU" in os.environ:
        return True
    try:
        import google.colab
        return True
    except ImportError:
        return os.path.exists("/content")

def run_command(command):
    """Executes shell commands, handling Colab's specific syntax."""
    if is_colab():
        from IPython import get_ipython
        if get_ipython():
            get_ipython().system(command)
            return
    subprocess.run(command, shell=True, check=True)

def start_ollama_background():
    """Runs Ollama serve in a background daemon thread with local host bindings."""
    ollama_path = "/usr/local/bin/ollama" if os.path.exists("/usr/local/bin/ollama") else "ollama"
    env = os.environ.copy()
    env["OLLAMA_HOST"] = "127.0.0.1:11434"
    subprocess.Popen([ollama_path, "serve"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def setup_environment():
    """Installs dependencies and ensures Ollama is actively running."""
    print("--- 🚀 Initializing Refactoring Pipeline ---")
    
    in_colab = is_colab()
    
    # 1. First, check if Ollama is ALREADY running
    try:
        if requests.get("http://127.0.0.1:11434").status_code == 200:
            print("✅ Ollama server is already up and reachable.")
            return
    except requests.exceptions.ConnectionError:
        pass

    # 2. If running on Colab or local Linux without active Ollama, set it up
    print(f"🌍 Environment detected: {'Google Colab' if in_colab else 'Local/Server'}")
    
    if in_colab:
        print("🔧 Installing system dependencies (pciutils, zstd)...")
        subprocess.run("sudo apt-get update -qq && sudo apt-get install -y -qq pciutils zstd", shell=True, check=True)

    # Install Ollama binary if missing
    ollama_bin = "/usr/local/bin/ollama"
    if not os.path.exists(ollama_bin) and subprocess.run("which ollama", shell=True, capture_output=True).returncode != 0:
        print("📥 Installing Ollama binary...")
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)

    # 3. Start background server thread
    print("⚙️ Spawning background Ollama process...")
    thread = threading.Thread(target=start_ollama_background, daemon=True)
    thread.start()

    # 4. Wait for server readiness
    print("⏳ Waiting for Ollama server to respond...")
    for attempts in range(30):
        try:
            response = requests.get("http://127.0.0.1:11434")
            if response.status_code == 200:
                print("✅ Ollama server is reachable and ready.")
                return
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    print("❌ Error: Ollama server failed to start.")
    sys.exit(1)

def setup_model(model_name):
    """Checks for model and pulls it if missing."""
    print(f"\n🔍 Checking for model: {model_name}...")
    try:
        output = subprocess.check_output("ollama list", shell=True).decode()
        if model_name in output:
            print(f"✅ Model '{model_name}' is already installed.")
        else:
            print(f"📥 Pulling model '{model_name}'... (this may take a few minutes)")
            run_command(f"ollama pull {model_name}")
    except Exception as e:
        print(f"⚠️ Could not verify/pull model automatically: {e}")

def get_user_model_choice():
    """Prompt user to select a model."""
    models = {
        "1": "llama3.2:3b",
        "2": "qwen2.5:7b",
        "3": "gemma2"
    }
    print("\nSelect a model to use:")
    for key, model in models.items():
        print(f"{key}. {model}")
    
    choice = input("Enter choice (1-3) or type custom model name (e.g., kimi): ").strip()
    return models.get(choice, choice)

if __name__ == "__main__":
    # 0. Setup Environment (Detects Colab, installs, and starts background server)
    setup_environment()
    
    # 1. Select and Install Model
    selected_model = get_user_model_choice()
    setup_model(selected_model)
    
    # 2. Extract Data
    import requests as lib_to_process # Example library to process
    functions = run_extraction(lib_to_process)
    
    # 3. Execution Pipeline
    print("\n--- 🛠️ Starting Refactoring Pipeline ---")
    
    # Run Refactoring
    process_and_save_dataset(functions, model_name=selected_model)
    
    # Run Validation
    run_self_healing_pipeline(functions, model_name=selected_model)
    
    # Run Analytics
    generate_plot("final_dataset_validated.json")
    run_comparative_analytics(model_name=selected_model)
    
    print("\n✅ Pipeline complete. All files saved.")
