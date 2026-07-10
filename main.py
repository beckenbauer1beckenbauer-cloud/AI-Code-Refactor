import sys
import os

# Add the src directory to the path so Python can find your code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/src')))


import requests
import inspect
import json
import time
import matplotlib.pyplot as plt
import numpy as np

import requests
print(f"Requests module location: {requests.__file__}")
print(f"Available members: {dir(requests)[:10]}") # Check if it has 'get' or 'post'

# --- Execution ---
if __name__ == "__main__":
    # Ensure requests is imported at the top of the file: 
    # import requests 
    
    # Check if requests is defined to prevent NameError
    try:
        target_library = requests
        print(f"Targeting library: {target_library.__name__}")
        
        extracted_funcs = extract_functions_from_library(target_library)
        if extracted_funcs:
            json_path = run_self_healing_pipeline(extracted_funcs)
            run_comparative_analytics("final_dataset.json", json_path)
        else:
            print("No functions were extracted. Check your target library.")
            
    except NameError:
        print("Error: 'requests' is not defined. Please ensure 'import requests' is at the top of main.py")
