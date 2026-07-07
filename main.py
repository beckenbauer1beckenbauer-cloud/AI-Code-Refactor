import os
import requests
import logging
from src.extractor import extract_functions_from_library
from src.processor import process_dataset
from src.analytics import run_analysis

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    # 1. Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    import requests as target_library
    
    # 2. Extract
    logging.info("Step 1: Extracting functions...")
    # This line DEFINES the 'functions' variable
    functions_to_process = extract_functions_from_library(target_library)
    
    # 3. Process
    logging.info("Step 2: Processing and self-healing...")
    # Now we pass that defined variable to process_dataset
    process_dataset(functions_to_process, output_file="data/final_dataset.json")
    
    # 4. Analyze
    logging.info("Step 3: Generating analytics...")
    # Make sure your paths match here
    report = run_analysis("data/final_dataset.json", "data/final_dataset.json")
    
    # ... (rest of your print statements)
