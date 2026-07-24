import sys
import os
import shutil
import time
import subprocess
import urllib.request

# Pin working directory to avoid directory corruption
BASE_DIR = "/content" if os.path.exists("/content") else "/tmp"
os.chdir(BASE_DIR)

from package_resolver import resolve_and_install_package
from extractor import extract_functions_deep
from refactor_and_validate import run_self_healing_pipeline
from plotting import generate_plot
from generate_analytics_report import run_comparative_analytics

def ensure_ollama_engine_ready():
    """Verifies that the Ollama engine background service is running."""
    url = "http://127.0.0.1:11434/api/version"
    try:
        urllib.request.urlopen(url, timeout=3)
        return
    except Exception:
        pass

    if not shutil.which("ollama"):
        print("❌ Ollama engine binary not found. Please run 'bash setup.sh' first.")
        sys.exit(1)

    print("⚡ Starting Ollama engine service...")
    subprocess.Popen(
        ["ollama", "serve"],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)

def install_model_first(model_name: str):
    """
    EXECUTABLE INSTALLATION PHASE:
    Runs the exact command to pull/install the selected model binary 
    and blocks all execution until installation is 100% complete.
    """
    print("\n" + "=" * 60)
    print(f"📥 PHASE 1: INSTALLING LLM MODEL WEIGHTS ({model_name})")
    print("=" * 60)

    # Check if weights exist locally
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, cwd=BASE_DIR)
        if model_name in res.stdout:
            print(f"✅ Model '{model_name}' is already installed on local disk.")
            return
    except Exception:
        pass

    print(f"⌛ Executing install command: 'ollama pull {model_name}'...")
    print("⏳ Please wait while model layers are downloaded into Ollama...\n")

    # Run blocking install command and stream live output
    process = subprocess.Popen(
        ["ollama", "pull", model_name],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"  [INSTALLING] {line.strip()}", flush=True)

    process.wait()

    if process.returncode == 0:
        print(f"\n✅ Model '{model_name}' installation finished successfully!")
    else:
        print(f"\n❌ Installation failed for model '{model_name}'. Exiting.")
        sys.exit(1)

def select_model():
    """Prompts model choice and immediately triggers installation."""
    print("\nSelect Model to Install & Execute:")
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
        selected = input("Enter custom model tag (e.g., mistral:7b): ").strip()
        selected = selected if selected else "qwen2.5:7b"
    else:
        selected = models.get(choice, "qwen2.5:7b")

    # MANDATORY STEP: Download/Install model BEFORE returning
    install_model_first(selected)
    return selected

def main():
    ensure_ollama_engine_ready()

    print("=" * 60)
    print("🤖 Universal AI Refactoring Pipeline")
    print("=" * 60)

    # 1. Select Library Target
    target_input = input("\nEnter Python library name (e.g., scikit-learn, httpx, scipy): ").strip()
    if not target_input:
        target_input = "scikit-learn"

    # 2. Select & Install Model
    model_name = select_model()

    # 3. Resolve & Install Target Python Package
    print("\n" + "=" * 60)
    print(f"📦 PHASE 2: RESOLVING & INSPECTING LIBRARY ('{target_input}')")
    print("=" * 60)
    module, pip_name, import_name = resolve_and_install_package(target_input, model_name=model_name)
    if not module:
        print(f"❌ Could not resolve or import '{target_input}'. Halting.")
        return

    # 4. Extract Source Code
    print(f"\n⚙️ Extracting target source code functions from '{import_name}'...")
    functions = extract_functions_deep(module, max_functions=10)

    if not functions:
        print(f"⚠️ No Python source code functions found for '{import_name}'.")
        return

    print(f"✅ Extracted {len(functions)} functions from '{import_name}':")
    for fname, _ in functions:
        print(f"   • {fname}")

    # 5. Refactor & Self-Heal
    print("\n" + "=" * 60)
    print(f"🚀 PHASE 3: REFACTORING & AST VALIDATION ({model_name})")
    print("=" * 60)
    validated_file = os.path.join(BASE_DIR, f"dataset_{import_name}_validated.json")
    run_self_healing_pipeline(functions, model_name=model_name, output_file=validated_file)

    # 6. Generate Analytics & Reports
    print("\n" + "=" * 60)
    print("📊 PHASE 4: GENERATING ANALYTICS & EXECUTIVE REPORT")
    print("=" * 60)
    generate_plot(dataset_file=validated_file, library_name=import_name)
    
    report_file = os.path.join(BASE_DIR, f"report_{import_name}.md")
    run_comparative_analytics(model_name=model_name, input_file=validated_file, library_name=import_name, report_file=report_file)

    print(f"\n🎉 Refactoring pipeline completed successfully for '{import_name}' using model '{model_name}'!")

if __name__ == "__main__":
    main()
