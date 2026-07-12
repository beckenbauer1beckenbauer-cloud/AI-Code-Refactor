import inspect
import importlib

def extract_functions_from_library(library_name):
    """
    Extracts all functions from a given library name string.
    Returns a list of (function_name, source_code).
    """
    try:
        # Dynamically import the library by name
        lib = importlib.import_module(library_name)
    except ImportError:
        raise ValueError(f"Could not find library: {library_name}")

    extracted_data = []
    for name, obj in inspect.getmembers(lib):
        if inspect.isfunction(obj):
            try:
                source = inspect.getsource(obj)
                extracted_data.append((name, source))
            except (TypeError, OSError):
                continue
    return extracted_data

# --- Generalization ---
# We will set the target library name globally 
# This can be easily changed in main.py or a config file
TARGET_LIB = "requests" 

try:
    functions_to_refactor = extract_functions_from_library(TARGET_LIB)
    print(f"✅ Successfully extracted {len(functions_to_refactor)} functions from '{TARGET_LIB}'.")
    for name, _ in functions_to_refactor:
        print(f"Found: {name}")
except Exception as e:
    print(f"❌ Error during extraction: {e}")
