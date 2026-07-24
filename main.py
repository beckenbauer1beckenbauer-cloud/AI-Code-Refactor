import sys
import subprocess
import importlib
import inspect
import pkgutil
import json
import re

# Import pipeline components
from engine import refactor_code
from refactor_and_validate import run_self_healing_pipeline
from plotting import generate_plot
from generate_analytics_report import run_comparative_analytics

def resolve_library_with_llm(user_input, model_name="qwen2.5:7b"):
    """
    Asks the LLM directly to map ANY package name in the world to its exact 
    PyPI install name and Python import module name.
    """
    print(f"🤖 Asking LLM to resolve package metadata for '{user_input}'...")
    
    prompt = (
        f"The user wants to use the Python library: '{user_input}'.\n"
        "Tell me the exact PyPI package name used for 'pip install' and the exact primary module name used for 'import' in Python.\n"
        "Return ONLY a JSON object with two keys: 'pip_name' and 'import_name'.\n"
        "Examples:\n"
        "Input: 'scikit-learn' -> {\"pip_name\": \"scikit-learn\", \"import_name\": \"sklearn\"}\n"
        "Input: 'pillow' -> {\"pip_name\": \"Pillow\", \"import_name\": \"PIL\"}\n"
        "Input: 'opencv' -> {\"pip_name\": \"opencv-python\", \"import_name\": \"cv2\"}\n"
        "Do NOT include markdown formatting or explanations."
    )

    response = refactor_code("PackageResolver", prompt, model_name=model_name)
    
    # Fallbacks if LLM fails
    pip_name = user_input.strip()
    import_name = user_input.strip().replace("-", "_")

    if response and isinstance(response, dict):
        pip_name = response.get("pip_name", pip_name)
        import_name = response.get("import_name", import_name)

    print(f"💡 LLM Resolved: pip install '{pip_name}' ➔ import '{import_name}'")
    return pip_name, import_name


def auto_install_and_import(pip_name, import_name):
    """
    Imports the module. If missing, automatically runs 'pip install <pip_name>'
    and re-imports without stopping the program.
    """
    # 1. First attempt to import directly
    try:
        module = importlib.import_module(import_name)
        print(f"✅ Successfully imported '{import_name}'.")
        return module
    except ImportError:
        print(f"📦 Module '{import_name}' not found. Auto-installing '{pip_name}' via pip...")

    # 2. Run pip install dynamically
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        importlib.invalidate_caches()
        module = importlib.import_module(import_name)
        print(f"✅ Successfully installed and imported '{import_name}'.")
        return module
    except Exception as e:
        print(f"❌ Failed to auto-install '{pip_name}': {e}")
        return None


def extract_functions_deep(module, max_functions=10):
    """
    Recursively inspects top-level module and submodules to find pure Python functions 
    with extractable source code (handles complex packages like sklearn, scipy, pandas).
    """
    functions_list = []
    seen_names = set()

    def search_module(mod, max_depth=2, current_depth=0):
        if len(functions_list) >= max_functions or current_depth > max_depth:
            return

        # Inspect members of current module
        try:
            members = inspect.getmembers(mod)
        except Exception:
            return

        for name, obj in members:
            if len(functions_list) >= max_functions:
                break

            # Extract pure Python functions
            if inspect.isfunction(obj) and not name.startswith("_"):
                full_name = f"{mod.__name__}.{name}"
                if full_name not in seen_names:
                    try:
                        source = inspect.getsource(obj)
                        if len(source.strip().splitlines()) > 3:  # Skip trivial 1-liners
                            functions_list.append((name, source))
                            seen_names.add(full_name)
                    except (TypeError, OSError):
                        pass

        # If we need more functions, explore submodules
        if len(functions_list) < max_functions and hasattr(mod, "__path__"):
            try:
                for _, subname, ispkg in pkgutil.walk_packages(mod.__path__, mod.__name__ + "."):
                    if len(functions_list) >= max_functions:
                        break
                    # Avoid private or test submodules
                    if ".tests" in subname or "._" in subname:
                        continue
                    try:
                        submod = importlib.import_module(subname)
                        search_module(submod, max_depth, current_depth + 1)
                    except Exception:
                        continue
            except Exception:
                pass

    search_module(module)
    return functions_list


def main():
    print("=" * 60)
    print("🤖 Universal AI Refactoring Pipeline (All Libraries)")
    print("=" * 60)

    target_input = input("Enter ANY Python library in the world (e.g. scikit-learn, httpx, django, scipy, sympy): ").strip()
    if not target_input:
        target_input = "requests"

    model_name = input("Enter Ollama model name [default: qwen2.5:7b]: ").strip()
    if not model_name:
        model_name = "qwen2.5:7b"

    # Step 1: Ask LLM to resolve pip name and import module name
    pip_name, import_name = resolve_library_with_llm(target_input, model_name=model_name)

    # Step 2: Auto-install & Import
    module = auto_install_and_import(pip_name, import_name)
    if not module:
        print(f"⚠️ Could not load library '{target_input}'. Falling back to 'requests'.")
        import requests
        module = requests
        import_name = "requests"

    # Step 3: Deep Function Extraction across root & submodules
    print(f"\n⚙️ Extracting functions from '{import_name}' (including submodules)...")
    functions = extract_functions_deep(module, max_functions=10)

    if not functions:
        print(f"⚠️ No pure Python functions with source code found in '{import_name}'.")
        return

    print(f"✅ Successfully extracted {len(functions)} functions from '{import_name}':")
    for fname, _ in functions:
        print(f"   • {fname}")

    # Step 4: Run Refactoring & Self-Healing Pipeline
    validated_file = f"dataset_{import_name}_validated.json"
    print("\n--- 🛠️ Running Refactoring & Self-Healing Pipeline ---")
    run_self_healing_pipeline(functions, model_name=model_name, output_file=validated_file)

    # Step 5: Generate Charts (Line Count & Status)
    print("\n--- 📊 Generating Visualization Charts ---")
    generate_plot(dataset_file=validated_file)

    # Step 6: Generate AI Executive Analytics Report
    print("\n--- 📝 Generating Executive AI Quality Report ---")
    run_comparative_analytics(model_name=model_name, input_file=validated_file, report_file=f"report_{import_name}.md")

    print(f"\n🎉 Process completed for '{import_name}'! Outputs created:")
    print(f"   📄 Validated Dataset: {validated_file}")
    print(f"   📊 Chart 1: line_count_comparison.png")
    print(f"   📊 Chart 2: refactoring_status_distribution.png")
    print(f"   📝 AI Report: report_{import_name}.md")

if __name__ == "__main__":
    main()
