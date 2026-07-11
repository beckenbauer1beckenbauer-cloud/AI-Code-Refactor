import requests
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
                # Some functions (like built-ins) don't have accessible source code
                # We skip these to avoid errors
                continue

    return extracted_data

# Define the library we want to process
target_library = requests

# Run the extraction function
functions_to_refactor = extract_functions_from_library(target_library)

# Display the result to confirm what has been extracted
print(f"✅ Successfully extracted {len(functions_to_refactor)} functions from '{target_library.__name__}'.")
print("-" * 40)

# Print the names of the functions to ensure transparency before proceeding
for name, _ in functions_to_refactor:
    print(f"Found: {name}")

# Now, 'functions_to_refactor' contains the actual data ready for the next step.
