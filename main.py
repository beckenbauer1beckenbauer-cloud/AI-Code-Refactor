import requests
import inspect
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import subprocess

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


def is_colab():
    return 'google.colab' in sys.modules

def run_command(command):
    if is_colab():
        from IPython import get_ipython
        get_ipython().magic(f"!{command}")
    else:
        subprocess.run(command, shell=True)

def setup_environment():
    with open('models_config.json', 'r') as f:
        config = json.load(f)
    
    print("--- Choose your AI Engine ---")
    for i, model in enumerate(config.keys()):
        print(f"{i+1}. {model}")
    
    choice_idx = int(input("Enter the number of your choice: ")) - 1
    choice = list(config.keys())[choice_idx]
    selected = config[choice]
    
    print(f"🚀 Initializing {choice}...")
    run_command(selected['install'])
    
    if selected['engine'] == "ollama":
        if is_colab():
            get_ipython().system_raw("ollama serve &")
        else:
            subprocess.Popen(["ollama", "serve"])
            
    # Save choice to a file so other scripts can read it
    with open("engine_state.json", "w") as f:
        json.dump(selected, f)
    
    return choice

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
