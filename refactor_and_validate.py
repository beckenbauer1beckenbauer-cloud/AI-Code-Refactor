def refactor_and_validate(name, code):
    """
    Refactors code and performs a syntax check. 
    If invalid, attempts a one-time self-healing fix using the selected engine.
    """
    # 1. Attempt Refactoring
    refactored_data = refactor_code_with_engine(name, code)

    if refactored_data is None:
        print(f"⚠️ Engine failed for {name}, skipping refactoring.")
        return code, "Engine failed"

    new_code = refactored_data.get("refactored_code")
    if not isinstance(new_code, str):
        new_code = code

    # 2. Validate (Self-Healing Loop)
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except SyntaxError as e:
        print(f"⚠️ Syntax Error in {name}. Attempting fix...")
        fix_prompt = f"The following code has a syntax error: {str(e)}. Provide the corrected code in JSON format:\n{new_code}"

        # We call the engine again for the fix
        fix_data = refactor_code_with_engine(name, fix_prompt)
        
        if fix_data and isinstance(fix_data.get("refactored_code"), str):
            fixed_code = fix_data["refactored_code"]
            return fixed_code, "fixed"
        
        return new_code, "unfixed_error"

def run_self_healing_pipeline(functions_list, output_file="final_dataset_validated.json"):
    """
    Orchestrates the validation process.
    """
    validated_dataset = []

    print(f"⚙️ Starting self-healing validation of {len(functions_list)} functions...")

    for name, code in functions_list:
        print(f"⚙️ Processing: {name}...")

        final_code, status = refactor_and_validate(name, code)

        validated_dataset.append({
            "function": name,
            "refactored_code": final_code,
            "status": status
        })

        # Incremental save to prevent data loss if the pipeline crashes
        with open(output_file, "w") as f:
            json.dump(validated_dataset, f, indent=4)

    print(f"✅ Pipeline finished. Dataset saved to {output_file}")

# Execute the pipeline
if 'functions_to_refactor' in globals():
    run_self_healing_pipeline(functions_to_refactor)
else:
    print("❌ Error: 'functions_to_refactor' not found. Ensure 1_extract.py ran successfully.")
