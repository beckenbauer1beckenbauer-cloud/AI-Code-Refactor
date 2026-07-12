def refactor_code_with_engine(name, code):
    """
    Refactors code using the engine specified in engine_state.json.
    """
    # Load the shared engine state
    with open("engine_state.json", "r") as f:
        engine_state = json.load(f)

    # Common system prompt
    system_prompt = (
        "You are an expert Python engineer. Refactor the provided function to: "
        "1. Add comprehensive type hints. "
        "2. Add Google-style docstrings (Parameters, Returns, Raises). "
        "3. Improve code structure if needed. "
        "Return ONLY a raw JSON object with two keys: 'refactored_code' and 'explanation'."
    )

    # --- ENGINE: OLLAMA ---
    if engine_state['engine'] == "ollama":
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": engine_state.get("model_id", "llama3.2:3b"),
            "prompt": f"{system_prompt}\n\nFunction '{name}' code:\n{code}",
            "stream": False,
            "format": "json"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return json.loads(data['response'])
            print(f"Error: Server returned {response.status_code} for {name}")
        except Exception as e:
            print(f"Engine failure (Ollama) for {name}: {e}")
        return None

    # --- ENGINE: NATIVE (llama-cpp-python) ---
    elif engine_state['engine'] == "native":
        try:
            # We delay the import so this only runs if 'native' is chosen
            from llama_cpp import Llama
            
            # Initialize model (this may take a moment)
            llm = Llama(model_path=engine_state['model_file'])
            
            output = llm(f"{system_prompt}\n\nFunction '{name}' code:\n{code}")
            
            # Clean up the output string to be valid JSON
            return json.loads(output['choices'][0]['text'])
        except Exception as e:
            print(f"Engine failure (Native) for {name}: {e}")
        return None

# --- Pipeline Execution ---
if 'functions_to_refactor' in globals() and functions_to_refactor:
    sample_name, sample_code = functions_to_refactor[0]
    print(f"🚀 Running engine test on: {sample_name}...")
    
    result = refactor_code_with_engine(sample_name, sample_code)

    if result:
        print("✅ Engine Test Successful!")
        print(f"Explanation: {result['explanation']}")
    else:
        print("❌ Engine Test Failed.")
