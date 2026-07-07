import inspect

def extract_functions_from_library(library):
    """Extracts all functions from a library."""
    extracted_data = []
    for name, obj in inspect.getmembers(library):
        if inspect.isfunction(obj):
            try:
                source = inspect.getsource(obj)
                extracted_data.append((name, source))
            except (TypeError, OSError):
                continue
    return extracted_data
