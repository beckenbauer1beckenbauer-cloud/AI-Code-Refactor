def process_and_save_dataset(functions_list, output_file="final_dataset.json"):
    """
    Processes all extracted functions and saves them to a structured JSON file.
    """
    final_dataset = []

    print(f"🚀 Starting full dataset processing of {len(functions_list)} functions...")

    for name, code in functions_list:
        print(f"Processing: {name}...")

        # Call the refactoring engine
        result = refactor_code_with_ollama(name, code)

        if result:
            # Structuring the data
            dataset_entry = {
                "function": name,
                "original_code": code,
                "refactored_code": result.get("refactored_code", ""),
                "explanation": result.get("explanation", "")
            }
            final_dataset.append(dataset_entry)

        # Adding a short pause to ensure the local Ollama server stays responsive
        time.sleep(1)

    # Save to JSON file
    with open(output_file, "w") as f:
        json.dump(final_dataset, f, indent=4)

    print(f"✅ Success! Dataset saved to '{output_file}'.")

# Execute the final pipeline
process_and_save_dataset(functions_to_refactor)
