import sys
import os
import shutil
import time
import subprocess
import urllib.request

# Force main script execution context
BASE_DIR = "/content" if os.path.exists("/content") else "/tmp"
os.chdir(BASE_DIR)

from package_resolver import resolve_and_install_package
from extractor import extract_functions_deep
from refactor_and_validate import run_self_healing_pipeline
from plotting import generate_plot
from generate_analytics_report import run_comparative_analytics

def ensure_ollama_engine_ready():
    """Verifies Ollama is healthy; restarts it from root (/) if dead or broken."""
    url = "http://127.0.0.1:11434/api/version"
    
    # Try reaching server
    try:
        urllib.request.urlopen(url, timeout=3)
        return
    except Exception:
        pass

    if not shutil.which("ollama"):
        print("❌ Ollama engine binary not found. Please run 'bash setup.sh' first.")
        sys.exit(1)

    print("⚡ Starting background Ollama daemon anchored at '/'...")
    # Kill any zombie instances first
    subprocess.run(["pkill", "-f", "ollama serve"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", "llama-server"], stderr=subprocess.DEVNULL)
    time.sleep(1)

    # Launch daemon from root directory '/'
    subprocess.Popen(
        ["ollama", "serve"],
        cwd="/",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    for _ in range(10):
        try:
            urllib.request.urlopen(url, timeout=2)
            print("✅ Ollama engine started successfully.")
            return
        except Exception:
            time.sleep(2)

    print("❌ Failed to launch Ollama server.")
    sys.exit(1)

def install_model_first(model_name: str):
    """Downloads model weights with real-time output from root directory."""
    print("\n" + "=" * 60)
    print(f"📥 PHASE 1: INSTALLING LLM MODEL WEIGHTS ({model_name})")
    print("=" * 60)

    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True, cwd="/")
        if model_name in res.stdout:
            print(f"✅ Model '{model_name}' is ready on local disk.")
            return
    except Exception:
        pass

    print(f"⌛ Executing: 'ollama pull {model_name}'...\n")

    process = subprocess.Popen(
        ["ollama", "pull", model_name],
        cwd="/",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"  [INSTALLING] {line.strip()}", flush=True)

    process.wait()

    if process.returncode == 0:
        print(f"\n✅ Model '{model_name}' downloaded successfully!")
    else:
        print(f"\n❌ Download failed for '{model_name}'.")
        sys.exit(1)

def select_model():
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

    selected = models.get(choice, "qwen2.5:7b") if choice != "5" else input("Enter model tag: ").strip()
    selected = selected if selected else "qwen2.5:7b"

    install_model_first(selected)
    return selected

def main():
    ensure_ollama_engine_ready()

    print("=" * 60)
    print("🤖 Universal AI Refactoring Pipeline")
    print("=" * 60)

    target_input = input("\nEnter Python library name (e.g., scikit-learn, httpx, scipy): ").strip()
    if not target_input:
        target_input = "scikit-learn"

    model_name = select_model()

    print("\n" + "=" * 60)
    print(f"📦 PHASE 2: RESOLVING & INSPECTING LIBRARY ('{target_input}')")
    print("=" * 60)
    module, pip_name, import_name = resolve_and_install_package(target_input, model_name=model_name)
    if not module:
        print(f"❌ Could not resolve '{target_input}'. Halting.")
        return

    print(f"\n⚙️ Extracting target source code functions from '{import_name}'...")
    functions = extract_functions_deep(module, max_functions=10)

    if not functions:
        print(f"⚠️ No source code functions found for '{import_name}'.")
        return

    print(f"✅ Extracted {len(functions)} functions from '{import_name}':")
    for fname, _ in functions:
        print(f"   • {fname}")

    print("\n" + "=" * 60)
    print(f"🚀 PHASE 3: REFACTORING & AST VALIDATION ({model_name})")
    print("=" * 60)
    validated_file = os.path.join(BASE_DIR, f"dataset_{import_name}_validated.json")
    run_self_healing_pipeline(functions, model_name=model_name, output_file=validated_file)

    print("\n" + "=" * 60)
    print("📊 PHASE 4: GENERATING ANALYTICS & EXECUTIVE REPORT")
    print("=" * 60)
    generate_plot(dataset_file=validated_file, library_name=import_name)
    
    report_file = os.path.join(BASE_DIR, f"report_{import_name}.md")
    run_comparative_analytics(model_name=model_name, input_file=validated_file, library_name=import_name, report_file=report_file)

    print(f"\n🎉 Refactoring pipeline completed successfully for '{import_name}' using '{model_name}'!")

if __name__ == "__main__":
    main()
