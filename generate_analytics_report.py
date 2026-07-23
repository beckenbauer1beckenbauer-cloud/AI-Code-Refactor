import json
import os
from engine import refactor_code

def run_comparative_analytics(model_name="llama3.2:3b", input_file="final_dataset_validated.json", report_file="analytics_report.md"):
    """
    Generates comparative metrics and delegates AI quality summary to engine.py.
    """
    print("\n📊 Starting Comparative Analytics...")
    
    if not os.path.exists(input_file):
        print(f"❌ Cannot generate report: '{input_file}' not found.")
        return

    with open(input_file, "r") as f:
        data = json.load(f)

    total_functions = len(data)
    verified_count = sum(1 for item in data if item.get("status") == "verified")
    fixed_count = sum(1 for item in data if item.get("status") == "fixed")
    failed_count = sum(1 for item in data if "error" in item.get("status", "") or item.get("status") == "Engine failed")

    print("\n🤖 Generating AI Quality Report...")
    prompt_summary = (
        f"Out of {total_functions} Python functions refactored by {model_name}:\n"
        f"- {verified_count} compiled cleanly on the first try.\n"
        f"- {fixed_count} required AI self-healing repairs to fix syntax.\n"
        f"- {failed_count} failed refactoring/validation.\n"
        "Provide a concise, 2-paragraph summary on the code quality, reliability, and refactoring performance."
    )

    # Route through engine.py to avoid broken local requests call
    ai_response = refactor_code("AnalyticsReport", prompt_summary, model_name=model_name)
    summary_text = ai_response.get("explanation") or ai_response.get("refactored_code") if ai_response else "Summary generation unavailable."

    report_content = f"""# 📈 AI Code Refactoring & Quality Report

**Model Evaluated:** `{model_name}`  
**Total Functions Processed:** `{total_functions}`  

---

## 📊 Performance Metrics

| Metric | Count | Percentage |
|---|---|---|
| **Verified (1st Attempt)** | {verified_count} | {(verified_count/total_functions)*100:.1f}% |
| **Self-Healed (AI Fixed)** | {fixed_count} | {(fixed_count/total_functions)*100:.1f}% |
| **Failed / Skipped** | {failed_count} | {(failed_count/total_functions)*100:.1f}% |

---

## 📝 Executive AI Summary

{summary_text}
"""

    with open(report_file, "w") as f:
        f.write(report_content)

    print(f"✅ Analytics report saved to '{report_file}'.")
