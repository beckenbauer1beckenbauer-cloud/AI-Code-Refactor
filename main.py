import os
import requests
import logging
from src.extractor import extract_functions_from_library
from src.processor import process_dataset
from src.analytics import run_analysis

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    # 1. Define your target
    import requests as target_library
    
    # 2. Extract
    logging.info("Step 1: Extracting functions...")
    extract_functions_from_library(target_library)
    
    # 3. Process
    logging.info("Step 2: Processing and self-healing...")
    # Note: We save to the 'data/' folder we created earlier
    functions = process_dataset(functions, output_file="data/final_dataset.json")
    functions
    
    # 4. Analyze
    logging.info("Step 3: Generating analytics...")
    report = run_analysis("data/final_dataset.json", "data/final_dataset.json")
    report
    
    print("\n" + "="*40)
    print("🐍 FINAL PROJECT REPORT 🐍")
    print("="*40)
    print(report)
    print("="*40)

if __name__ == "__main__":
    main()
