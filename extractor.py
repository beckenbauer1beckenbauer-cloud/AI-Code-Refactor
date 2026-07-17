import inspect

def extract_functions_from_library(library):
    """
    Extracts all functions from a given library and returns a list
    containing tuples of (function_name, source_code).
    """
    extracted_data = []

    # Iterate through all members of the library
    for name, obj in inspect.getmembers(library):
        # We only want to process actual functions
        if inspect.isfunction(obj):
            try:
                # Attempt to get the source code of the function
                source = inspect.getsource(obj)
                extracted_data.append((name, source))
            except (TypeError, OSError):
                # Skip built-ins or functions without source code
                continue

    return extracted_data

def run_extraction(target_library):
    """
    Main entry point for this module to be called by the pipeline.
    """
    print(f"🔍 Extracting functions from '{target_library.__name__}'...")
    functions = extract_functions_from_library(target_library)
    print(f"✅ Successfully extracted {len(functions)} functions.")
    return functions
