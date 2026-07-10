def refactor_code_with_ollama(name, code):
    """
    Sends the raw function code to the local Ollama instance and
    returns the refactored code and explanation in JSON format.
    """
    url = "http://localhost:11434/api/generate"

    # We define the role and task for the AI engine
    system_prompt = (
        "You are an expert Python engineer. Refactor the provided function to: "
        "1. Add comprehensive type hints. "
        "2. Add Google-style docstrings (Parameters, Returns, Raises). "
        "3. Improve code structure if needed. "
        "Return ONLY a raw JSON object with two keys: 'refactored_code' and 'explanation'."
    )

    payload = {
        "model": "llama3.2:3b",
        "prompt": f"{system_prompt}\n\nFunction '{name}' code:\n{code}",
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            try:
                data = response.json()
                # The AI response is in the 'response' field
                return json.loads(data['response'])
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from Ollama for {name}: {e}. Response was: {response.text}")
                return None
        else:
            print(f"Error: Server returned {response.status_code} for {name}. Response: {response.text}")
            return None
    except Exception as e:
        print(f"Engine failure for {name}: {e}")
        return None

# Test the engine with the first function in our list
if 'functions_to_refactor' in globals() and functions_to_refactor:
    sample_name, sample_code = functions_to_refactor[0]
    print(f"🚀 Running engine test on: {sample_name}...")
    result = refactor_code_with_ollama(sample_name, sample_code)

    if result:
        print("✅ Engine Test Successful!")
        print(f"Explanation: {result['explanation']}")
    else:
        print("❌ Engine Test Failed.")
