import os, sys, json, subprocess

def is_colab(): return 'google.colab' in sys.modules

def setup_environment():
    with open('models_config.json', 'r') as f: config = json.load(f)
    print("--- Choose your AI Engine ---")
    for i, model in enumerate(config.keys()): print(f"{i+1}. {model}")
    choice = list(config.keys())[int(input("Selection: "))-1]

    target_lib = input("Enter the name of the Python library you want to analyze (e.g., requests, os, json): ")
    
    # Save both model choice AND target library to state
    state = config[choice]
    state['target_lib'] = target_lib
    
    with open("engine_state.json", "w") as f:
        json.dump(state, f)
    
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
    pipeline = [
        "extractor.py",
        "engine.py",
        "processor.py",
        "plotting.py",
        "refactor_and_validate.py",
        "generate_analytics_report.py"
    ]
    for step in pipeline:
        print(f"\n🚀 Running: {step}")
        exec(open(step).read(), globals())
