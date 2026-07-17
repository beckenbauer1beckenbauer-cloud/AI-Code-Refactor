import json
import time
from engine import refactor_code

def process_and_save_dataset(functions_list, model_name, output_file="final_dataset.json"):
    """
    Processes all extracted functions and saves them to a structured JSON file.
    
    Args:
        functions_list (list): List of (name, code) tuples.
        model_name (str): The model selected by the user.
        output_file (str): File path to save the dataset.
    """
    final_dataset = []

    print(f"🚀 Starting full dataset processing of {len(functions_list)} functions using {model_name}...")

    for name, code in functions_list:
        print(f"Processing: {name}...")

        # Pass the model_name to the engine
        result = refactor_code(name, code, model_name=model_name)

        if result:
            dataset_entry = {
                "function": name,
                "original_code": code,
                "refactored_code": result.get("refactored_code", ""),
                "explanation": result.get("explanation", "")
            }
            final_dataset.append(dataset_entry)

        # Pause to prevent server overload
        time.sleep(1)

    # Save to JSON file
    with open(output_file, "w") as f:
        json.dump(final_dataset, f, indent=4)

    print(f"✅ Success! Dataset saved to '{output_file}'.")
