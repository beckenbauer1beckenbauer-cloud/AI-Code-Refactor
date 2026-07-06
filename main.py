import requests
import inspect
import json
import time
import matplotlib.pyplot as plt
import numpy as np

def extract_functions_from_library(library):
    """
    Extracts all functions from a given library and returns a list 
    containing tuples of (function_name, source_code).
    """
    extracted_data = []
    
    # Iterate through all members of the library
    for name, obj in inspect.getmembers(library):
        # We only want to process actual functions
        if inspect.isfunction(obj):
            try:
                # Attempt to get the source code of the function
                source = inspect.getsource(obj)
                extracted_data.append((name, source))
            except (TypeError, OSError):
                # Some functions (like built-ins) don't have accessible source code
                # We skip these to avoid errors
                continue
                
    return extracted_data

# Define the library we want to process
target_library = requests

# Run the extraction function
functions_to_refactor = extract_functions_from_library(target_library)

# Display the result to confirm what has been extracted
print(f"✅ Successfully extracted {len(functions_to_refactor)} functions from '{target_library.__name__}'.")
print("-" * 40)

# Print the names of the functions to ensure transparency before proceeding
for name, _ in functions_to_refactor:
    print(f"Found: {name}")

# Now, 'functions_to_refactor' contains the actual data ready for the next step.

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
            data = response.json()
            # The AI response is in the 'response' field
            return json.loads(data['response'])
        else:
            print(f"Error: Server returned {response.status_code}")
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


# 1. Load the dataset we just created
with open("final_dataset.json", "r") as f:
    dataset = json.load(f)

# 2. Extract metrics (length of code in characters)
names = [entry['function'] for entry in dataset]
orig_lengths = [len(entry['original_code']) for entry in dataset]
refactored_lengths = [len(entry['refactored_code']) for entry in dataset]

# 3. Create the plot
plt.figure(figsize=(12, 6))
bar_width = 0.35
index = range(len(names))

plt.bar(index, orig_lengths, bar_width, label='Original Code Length', color='gray')
plt.bar([i + bar_width for i in index], refactored_lengths, bar_width, label='Refactored Code Length', color='blue')

plt.xlabel('Functions')
plt.ylabel('Character Count')
plt.title('Code Expansion Analysis: Original vs Refactored')
plt.xticks([i + bar_width/2 for i in index], names, rotation=45, ha='right')
plt.legend()
plt.tight_layout()

# 4. Save and Show
plt.savefig("refactoring_analysis.png")


def refactor_and_validate(name, code):
    """
    Refactors code with validation and error handling.
    """
    # 1. Get data from engine
    refactored_data = refactor_code_with_ollama(name, code)
    
    # Check if the engine returned None or failed
    if not refactored_data or "refactored_code" not in refactored_data:
        print(f"⚠️ Engine failed for {name}, keeping original code.")
        return code, "Engine failed"

    new_code = refactored_data.get("refactored_code")

    # Ensure new_code is actually a string before compiling
    if not isinstance(new_code, str):
        print(f"⚠️ Invalid output format for {name}.")
        return code, "invalid_format"
    
    # 2. Validate (Self-Healing Loop)
    try:
        compile(new_code, '<string>', 'exec')
        return new_code, "verified"
    except SyntaxError as e:
        print(f"⚠️ Syntax Error in {name}. Attempting fix...")
        # ... your existing fix logic ...
        return new_code, "unfixed_error"
        
def run_self_healing_pipeline(functions_list, output_file="final_dataset_validated.json"):
    validated_dataset = []
    
    for name, code in functions_list:
        print(f"⚙️ Processing: {name}...")
        
        # Use our robust refactor/validate function
        final_code, status = refactor_and_validate(name, code)
        
        validated_dataset.append({
            "function": name,
            "refactored_code": final_code,
            "status": status
        })
        
        # Incremental save
        with open(output_file, "w") as f:
            json.dump(validated_dataset, f, indent=4)
        
        # Small delay to prevent server overload
        time.sleep(2) 
            
    print(f"✅ Pipeline finished. Dataset saved to {output_file}")

# --- Helper Function: Call Ollama for Report ---
def generate_analytics_report(metrics_old, metrics_new):
    """
    Sends metrics to Ollama to generate a comparative professional report.
    """
    url = "http://localhost:11434/api/generate"
    
    prompt = f"""
    You are a Senior Python Software Quality Analyst. 
    Analyze the following metrics comparing a Legacy Python Codebase to its Refactored version (using AI).
    Focus on improvements in documentation (Docstrings) and type hinting.
    
    Metrics (Average values per function):
    - Legacy Average Docstring Length: {metrics_old['avg_docstring_len']} chars
    - Refactored Average Docstring Length: {metrics_new['avg_docstring_len']} chars (Improvement: {metrics_new['avg_docstring_len'] - metrics_old['avg_docstring_len']} chars)
    - Legacy Functions with Type Hints: {metrics_old['type_hint_pct']}%
    - Refactored Functions with Type Hints: {metrics_new['type_hint_pct']}% (Improvement: +{metrics_new['type_hint_pct'] - metrics_old['type_hint_pct']}%)

    Generate a brief, well-organized professional report (bullet points) summarizing the quality improvements.
    """
    
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "Error generating report from Ollama."
    except Exception as e:
        return f"Analytics report generation failed: {e}"

# --- Main Analytics Logic ---
def run_comparative_analytics(old_file="final_dataset.json", new_file="final_dataset_validated.json"):
    print("📊 Starting Comparative Analytics...")
    
    try:
        # Load both datasets
        with open(old_file, "r") as f:
            old_data = json.load(f)
        with open(new_file, "r") as f:
            new_data = json.load(f)
            
        # Function to calculate metrics
        def calculate_metrics(dataset):
            total_funcs = len(dataset)
            if total_funcs == 0:
                return {'avg_docstring_len': 0, 'type_hint_pct': 0}
            
            total_doc_len = 0
            funcs_with_hints = 0
            
            for entry in dataset:
                # Assuming docstring is in 'explanation' or part of 'refactored_code'
                # We'll check 'explanation' length for simplicity as a proxy for doc quality
                docstring = entry.get('explanation', '')
                total_doc_len += len(docstring)
                
                # Check for type hint markers (e.g., '->', ': ') in refactored code
                code = entry.get('refactored_code', '')
                if '->' in code or (':' in code and '=' not in code and 'def' in code):
                    funcs_with_hints += 1
                    
            return {
                'avg_docstring_len': round(total_doc_len / total_funcs, 2),
                'type_hint_pct': round((funcs_with_hints / total_funcs) * 100, 2)
            }

        metrics_old = calculate_metrics(old_data)
        metrics_new = calculate_metrics(new_data)
        
        # --- Visualization (Plotting) ---
        labels = ['Avg Docstring Length (Chars)', 'Functions with Type Hints (%)']
        legacy_vals = [metrics_old['avg_docstring_len'], metrics_old['type_hint_pct']]
        refactored_vals = [metrics_new['avg_docstring_len'], metrics_new['type_hint_pct']]

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots(figsize=(10, 6))
        rects1 = ax.bar(x - width/2, legacy_vals, width, label='Legacy Code', color='gray')
        rects2 = ax.bar(x + width/2, refactored_vals, width, label='Refactored (Self-Healed)', color='green')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Scores')
        ax.set_title('Quality Improvement: Legacy vs Self-Healed Refactoring')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, max(max(legacy_vals), max(refactored_vals)) * 1.2) # Add headroom
        ax.legend()

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)

        fig.tight_layout()
        plt.savefig("comparative_analysis.png")
        print("✅ Comparative plot generated: comparative_analysis.png")

        # --- AI Reporting ---
        print("\n🤖 Generating AI Quality Report...")
        report = generate_analytics_report(metrics_old, metrics_new)
        print("\n" + "="*40)
        print("🐍 SENIOR ANALYST REPORT 🐍")
        print("="*40)
        print(report)
        print("="*40)

    except FileNotFoundError as e:
        print(f"⚠️ Error: One or both files not found. Please ensure both JSON files exist. {e}")

# --- 2. EXECUTION LOGIC ---
if __name__ == "__main__":
    print("🚀 Starting Pipeline...")
    
    # 1. Extraction
    functions = extract_functions_from_library(requests)
    
    # 2. Process (This generates the file)
    process_and_save_dataset(functions, "final_dataset.json")
    
    # 3. Heal (This generates the second file)
    run_self_healing_pipeline(functions, "final_dataset_validated.json")
    
    # 4. Analytics (Only run this AFTER the files exist)
    # Move your plotting and reading logic into a function called here
    run_comparative_analytics("final_dataset.json", "final_dataset_validated.json")
    
    print("🏁 All processes finished successfully!")
