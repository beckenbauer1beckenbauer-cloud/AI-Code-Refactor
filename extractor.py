import json
import inspect
import importlib
import sys

# Load the state
with open("engine_state.json", "r") as f:
    state = json.load(f)

# Strictly get the library name
target_lib_name = state.get('target_lib')

if not target_lib_name:
    print("❌ Error: No library selected. Please restart the pipeline.")
    sys.exit(1)

def extract_functions_from_library(library_name):
    try:
        lib = importlib.import_module(library_name)
        extracted_data = []
        for name, obj in inspect.getmembers(lib):
            if inspect.isfunction(obj):
                try:
                    source = inspect.getsource(obj)
                    extracted_data.append((name, source))
                except (TypeError, OSError):
                    continue
        return extracted_data
    except ImportError:
        print(f"❌ Error: Library '{library_name}' could not be found.")
        return []

# Run
functions_to_refactor = extract_functions_from_library(target_lib_name)

if not functions_to_refactor:
    print(f"⚠️ No extractable functions found in '{target_lib_name}'.")
    sys.exit(1) # Stop pipeline if there's nothing to process
