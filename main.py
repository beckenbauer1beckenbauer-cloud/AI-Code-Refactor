# --- Execution ---
if __name__ == "__main__":
    target_library = requests
    funcs = extract_functions_from_library(target_library)
    json_path = run_self_healing_pipeline(funcs)
    run_comparative_analytics("final_dataset.json", json_path)
