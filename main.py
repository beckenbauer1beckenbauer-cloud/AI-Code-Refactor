import requests
import logging
from src.extractor import extract_functions_from_library
from src.processor import process_dataset
from src.analytics import run_analysis

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    # 1. Define your target
    import requests as target_library
    
    # 2. Extract
    logging.info("Step 1: Extracting functions...")
    functions = extract_functions_from_library(target_library)
    
    # 3. Process
    logging.info("Step 2: Processing and self-healing...")
    # Note: We save to the 'data/' folder we created earlier
    process_dataset(functions, output_file="data/final_dataset.json")
    
    # 4. Analyze
    logging.info("Step 3: Generating analytics...")
    report = run_analysis("data/final_dataset.json", "data/final_dataset.json")
    
    print("\n" + "="*40)
    print("🐍 FINAL PROJECT REPORT 🐍")
    print("="*40)
    print(report)
    print("="*40)

if __name__ == "__main__":
    main()
