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
    """Detects if the code is running in a Google Colab environment."""
    return 'google.colab' in sys.modules

def run_command(command):
    """Executes shell commands, handling Colab's specific syntax."""
    if is_colab():
        from IPython import get_ipython
        get_ipython().system(command)
    else:
        subprocess.run(command, shell=True, check=True)

def start_ollama_background():
    """Helper function to run Ollama inside a background daemon thread with env vars set."""
    ollama_path = "/usr/local/bin/ollama" if os.path.exists("/usr/local/bin/ollama") else "ollama"
    
    # Configure environment variables so Ollama binds to localhost
    env = os.environ.copy()
    env["OLLAMA_HOST"] = "127.0.0.1:11434"
    
    # Start Ollama server process
    subprocess.Popen([ollama_path, "serve"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def setup_environment():
    """Verifies Ollama is running and handles Colab startup using threading and apt dependencies."""
    print("--- 🚀 Initializing Refactoring Pipeline ---")
    
    if is_colab():
        print("🌍 Detected Google Colab environment. Setting up Ollama...")
        
        # 1. Install necessary Colab system dependencies (required by Ollama installer)
        print("🔧 Installing system dependencies (pciutils, zstd)...")
        subprocess.run("sudo apt-get update -qq && sudo apt-get install -y -qq pciutils zstd", shell=True, check=True)

        # 2. Install Ollama binary directly via official install script
        print("📥 Installing Ollama binary...")
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
            
        # 3. Start Ollama in background thread
        print("⚙️ Spawning background Ollama process...")
        thread = threading.Thread(target=start_ollama_background, daemon=True)
        thread.start()

    # 4. Poll Ollama server until ready (up to 30 seconds)
    print("⏳ Waiting for Ollama server to respond...")
    for attempts in range(30):
        try:
            response = requests.get("http://127.0.0.1:11434")
            if response.status_code == 200:
                print("✅ Ollama server is reachable and ready.")
                return
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    print("❌ Error: Ollama server not found. Please ensure it is running.")
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
    # 0. Setup Environment (Installs dependencies + Ollama & starts server)
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
