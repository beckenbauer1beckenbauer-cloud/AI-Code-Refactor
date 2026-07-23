import json
import time
from engine import refactor_code

def process_and_save_dataset(functions_list, model_name="llama3.2:3b", output_file="final_dataset.json"):
    """
    Processes all extracted functions using the refactor engine and saves incrementally.
    """
    print(f"🚀 Starting full dataset processing of {len(functions_list)} functions using {model_name}...")
    dataset = []

    for name, code in functions_list:
        print(f"Processing: {name}...")
        
        result = refactor_code(name, code, model_name=model_name)
        
        refactored_code = result.get("refactored_code", code) if result else code
        explanation = result.get("explanation", "No explanation provided.") if result else "Engine failed."

        dataset.append({
            "function_name": name,
            "original_code": code,
            "refactored_code": refactored_code,
            "explanation": explanation
        })

        # Save incrementally
        with open(output_file, "w") as f:
            json.dump(dataset, f, indent=4)

        time.sleep(1)

    print(f"✅ Success! Dataset saved to '{output_file}'.")
