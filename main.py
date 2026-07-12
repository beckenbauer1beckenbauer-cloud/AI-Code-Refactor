import requests
import inspect
import json
import time
import matplotlib.pyplot as plt
import numpy as np


import os

def run_pipeline_step(script_name):
    print(f"\n--- Ready to execute: {script_name} ---")
    
    try:
        # Executes the file as if it were a notebook cell
        exec(open(script_name).read(), globals())
        print(f"✅ Success: {script_name} completed.")
    except Exception as e:
        print(f"❌ Error in {script_name}: {e}")
        # Stop the pipeline if an error occurs
        return False
    return True

# Interactive model picker
print("Available Models:")
print("1. Llama 3.2 (General)")
print("2. Codellama (Coding focus)")
choice = input("Choose a model (1/2): ")

if choice == "1":
    SELECTED_MODEL = "llama3.2:3b"
else:
    SELECTED_MODEL = "codellama"

globals()['SELECTED_MODEL'] = SELECTED_MODEL

if __name__ == "__main__":
    # Your numbered pipeline steps
    pipeline = [
        "extractor.py",
        "engine.py",
        "processor.py",
        "plotting.py",
        "refactor_and_validate.py",
        "generate_analytics_report.py"
    ]
    
    for step in pipeline:
        if not run_pipeline_step(step):
            print("\n🛑 Pipeline halted due to error.")
            break
    else:
        print("\n🎉 Entire pipeline finished successfully!")
