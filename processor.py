def process_and_save_dataset(functions_list, output_file="final_dataset.json"):
    """
    Processes all extracted functions using the selected engine
    and saves them to a structured JSON file.
    """
    final_dataset = []

    print(f"🚀 Starting full dataset processing of {len(functions_list)} functions...")

    for name, code in functions_list:
        print(f"Processing: {name}...")

        # Use the unified refactoring engine function from 2_engine.py
        result = refactor_code_with_engine(name, code)

        if result:
            # Structuring the data consistently
            dataset_entry = {
                "function": name,
                "original_code": code,
                "refactored_code": result.get("refactored_code", "N/A"),
                "explanation": result.get("explanation", "N/A")
            }
            final_dataset.append(dataset_entry)
        else:
            print(f"⚠️ Skipping {name} due to engine failure.")

        # Optional: Short pause to prevent resource thrashing
        # time.sleep(1)

    # Save to JSON file
    with open(output_file, "w") as f:
        json.dump(final_dataset, f, indent=4)

    print(f"✅ Success! Dataset saved to '{output_file}'.")

# Execute the pipeline
# We assume 'functions_to_refactor' is available in globals()
if 'functions_to_refactor' in globals():
    process_and_save_dataset(functions_to_refactor)
else:
    print("❌ Error: 'functions_to_refactor' list not found.")
