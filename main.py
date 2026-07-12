import os, sys, json, subprocess

def is_colab(): return 'google.colab' in sys.modules

def setup_environment():
    with open('models_config.json', 'r') as f: config = json.load(f)
    print("--- Choose your AI Engine ---")
    for i, model in enumerate(config.keys()): print(f"{i+1}. {model}")
    choice = list(config.keys())[int(input("Selection: "))-1]
    
    # Install command handling
    cmd = config[choice]['install']
    if is_colab(): 
        from IPython import get_ipython
        get_ipython().magic(f"!{cmd}")
    else: subprocess.run(cmd, shell=True)
    
    # Save engine state
    with open("engine_state.json", "w") as f: json.dump(config[choice], f)
    return choice

if __name__ == "__main__":
    setup_environment()
    # Define your pipeline sequence
    pipeline = ["1_extract.py", "2_engine.py", "3_processor.py", "4_plot.py", "5_validate.py", "6_analytics.py"]
    for step in pipeline:
        print(f"\n🚀 Running: {step}")
        exec(open(step).read(), globals())
