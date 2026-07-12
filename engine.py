def refactor_code_with_engine(name, code, prompt_type="refactor"):
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

    # CRITICAL: Force the model to output ONLY valid JSON
    system_instruction = (
        "You are a coding assistant. "
        "You must return your response ONLY as a valid JSON object with this exact structure: "
        '{"refactored_code": "your code here"}. '
        "Do not include any introductory text, markdown formatting like ```json, or explanations."
    )
    
    # When sending the prompt, include the structure requirement
    full_prompt = f"{system_instruction}\n\nTask: {code}"
    
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
     # 2. Sanitize the output before parsing
    try:
        # Step A: Strip whitespace
        raw_output = raw_output.strip()
        
        # Step B: Remove markdown code blocks if the AI included them
        # This regex looks for ```json ... ``` and removes the markers
        clean_output = re.sub(r'^```json\s*', '', raw_output, flags=re.IGNORECASE)
        clean_output = re.sub(r'```$', '', clean_output).strip()
        
        # Step C: Final attempt at parsing
        return json.loads(clean_output)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing failed for {name}. Raw output was: {raw_output}")
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
