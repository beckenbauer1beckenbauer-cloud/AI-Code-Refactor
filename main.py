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

if __name__ == "__main__":
    # Your numbered pipeline steps
    pipeline = [
        "extractor.py",
        "engine.py",
        "processor.py.py",
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
