import sys
import os

# Pin base directory to prevent working directory corruption in Colab
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
    """Ensures Ollama background daemon is active."""
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

    print(f"⚡ Starting Ollama server background daemon from {BASE_DIR}...")
    subprocess.Popen(
        ["ollama", "serve"],
        cwd=BASE_DIR,
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    for _ in range(10):
        try:
            urllib.request.urlopen(url, timeout=2)
            print("✅ Ollama server is active and ready.")
            return
        except Exception:
            time.sleep(2)

    print("❌ Failed to reach Ollama server.")
    sys.exit(1)

def install_selected_model(model_name: str):
    """
    EXPLICIT INSTALLATION STEP:
    Triggers 'ollama pull <model_name>' right after selection, showing live download status.
    """
    print("\n" + "=" * 60)
    print(f"📥 STEP 1: INSTALLING TARGET LLM MODEL ('{model_name}')")
    print("=" * 60)

    # Check if already present
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True, cwd=BASE_DIR)
        if model_name in res.stdout:
            print(f"✅ Model '{model_name}' is already installed locally.")
            return
    except Exception:
        pass

    print(f"🚀 Downloading '{model_name}' from Ollama library... (this may take a minute)")
    
    # Run pull command with real-time terminal output
    process = subprocess.Popen(
        ["ollama", "pull", model_name],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Stream output line by line so you see the download progress live
    for line in process.stdout:
        print(f"   {line.strip()}")

    process.wait()

    if process.returncode == 0:
        print(f"\n✅ Successfully installed '{model_name}'!")
    else:
        print(f"\n❌ Failed to install model '{model_name}'.")
        sys.exit(1)

def select_model():
    """Allows choosing from Qwen, Llama, Gemma, DeepSeek, or entering a custom model."""
    print("\nSelect Ollama Model to Install & Use:")
    print("1. qwen2.5:7b")
    print("2. llama3.2:3b")
    print("3. gemma2:2b")
    print("4. deepseek-r1:7b")
    print("5. Custom model name")

    choice = input("\nEnter choice (1-5) [default: 1]: ").strip()
    
    models = {
        "1": "qwen2.5:7b",
        "2": "llama3.2:3b",
        "3": "gemma2:2b",
        "4": "deepseek-r1:7b"
    }

    if choice == "5":
        selected = input("Enter custom Ollama model tag (e.g., mistral:7b): ").strip()
        if not selected:
            selected = "qwen2.5:7b"
    else:
        selected = models.get(choice, "qwen2.5:7b")

    # Force explicit download step right after selection
    install_selected_model(selected)
    return selected

def main():
    os.chdir(BASE_DIR)
    
    print("=" * 60)
    print("🤖 Universal AI Refactoring Pipeline")
    print("=" * 60)

    # Ensure background service is alive
    ensure_ollama_running()

    # Step 1: User chooses library
    target_input = input("\nEnter ANY Python library name (e.g., scikit-learn, httpx, django, scipy): ").strip()
    if not target_input:
        target_input = "scikit-learn"

    # Step 2: User chooses model -> Triggers explicit INSTALLATION
    model_name = select_model()

    # Step 3: Resolve & Install target package
    print("\n" + "=" * 60)
    print(f"📦 STEP 2: RESOLVING & INSPECTING LIBRARY ('{target_input}')")
    print("=" * 60)
    module, pip_name, import_name = resolve_and_install_package(target_input, model_name=model_name)
    if not module:
        print(f"❌ Pipeline halted: Unable to process target '{target_input}'.")
        return

    os.chdir(BASE_DIR)

    # Step 4: Extract Source Code
    print(f"\n⚙️ Extracting functions from '{import_name}'...")
    functions = extract_functions_deep(module, max_functions=10)

    if not functions:
        print(f"⚠️ No pure Python functions with source code found in '{import_name}'.")
        return

    print(f"✅ Extracted {len(functions)} functions from '{import_name}':")
    for fname, _ in functions:
        print(f"   • {fname}")

    # Step 5: Refactor & Validate
    print("\n" + "=" * 60)
    print(f"🚀 STEP 3: REFACTORING & AI SELF-HEALING ({model_name})")
    print("=" * 60)
    validated_file = os.path.join(BASE_DIR, f"dataset_{import_name}_validated.json")
    run_self_healing_pipeline(functions, model_name=model_name, output_file=validated_file)

    # Step 6: Visualizations & Executive Markdown Report
    print("\n" + "=" * 60)
    print("📊 STEP 4: GENERATING ANALYTICS & REPORTS")
    print("=" * 60)
    generate_plot(dataset_file=validated_file, library_name=import_name)
    
    report_file = os.path.join(BASE_DIR, f"report_{import_name}.md")
    run_comparative_analytics(model_name=model_name, input_file=validated_file, library_name=import_name, report_file=report_file)

    print(f"\n🎉 Pipeline completed successfully for '{import_name}' using model '{model_name}'!")

if __name__ == "__main__":
    main()
