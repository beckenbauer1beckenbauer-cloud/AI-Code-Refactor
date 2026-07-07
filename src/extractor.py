import inspect
import logging

# Set up logging to track what the tool is doing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                logger.info(f"Successfully extracted function: {name}")
            except (TypeError, OSError):
                # Some functions (like built-ins) don't have accessible source code
                # We skip these to avoid errors
                continue
                
    return extracted_data
