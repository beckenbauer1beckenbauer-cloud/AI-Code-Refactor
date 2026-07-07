# --- 2. EXECUTION LOGIC ---
if __name__ == "__main__":
    print("🚀 Starting Pipeline...")
    
    # Ensure Ollama is reachable
    try:
        # Step 1: Extraction
        target_library = requests
        functions_to_refactor = extract_functions_from_library(target_library)
        print(f"✅ Extracted {len(functions_to_refactor)} functions.")

        # Step 2: Processing & Self-Healing
        # We process to save the base dataset first
        process_and_save_dataset(functions_to_refactor, "final_dataset.json")
        
        # Then run the healing pipeline
        run_self_healing_pipeline(functions_to_refactor, "final_dataset_validated.json")
        
        # Step 3: Analytics
        run_comparative_analytics("final_dataset.json", "final_dataset_validated.json")
        
        print("🏁 All processes finished successfully!")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
