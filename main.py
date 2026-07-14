import subprocess
import json
import time

def run_step_with_healing(script_name):
    """Runs a script and keeps looping if it returns an error code."""
    max_retries = 3
    for attempt in range(max_retries):
        print(f"\n🚀 Attempting step: {script_name} (Attempt {attempt+1})")
        
        # Run the script as a process
        process = subprocess.run(['python3', script_name], capture_output=True, text=True)
        
        if process.returncode == 0:
            print(f"✅ {script_name} passed.")
            return True
        else:
            print(f"❌ Error in {script_name}:")
            error_log = process.stderr
            print(error_log)
            
            # --- AI HEALING AGENT ---
            print("🤖 AI Agent: Analyzing and fixing errors...")
            # Here you call your refactor_code_with_engine logic
            # to feed the 'error_log' back to the model 
            # and rewrite the script file.
            
            time.sleep(2) # Give the system a breath
            
    return False

# Main Pipeline Controller
pipeline = ["extractor.py", "engine.py","processor.py", "plotting.py","refactor_and_validate.py","generate_analytics_report.py"]

for step in pipeline:
    if not run_step_with_healing(step):
        print(f"🚨 Critical Failure: {step} could not be fixed. Stopping Pipeline.")
        break
