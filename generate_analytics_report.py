import json
import os
from engine import refactor_code

def run_comparative_analytics(model_name="qwen2.5:7b", input_file="final_dataset_validated.json", library_name="target", report_file="analytics_report.md"):
    """Generates an executive markdown report for the specific target library."""
    if not os.path.exists(input_file):
        return

    with open(input_file, "r") as f:
        data = json.load(f)

    total = len(data)
    verified = sum(1 for item in data if item.get("status") == "verified")
    fixed = sum(1 for item in data if item.get("status") == "fixed")
    failed = total - verified - fixed

    prompt = (
        f"Out of {total} functions from '{library_name}' refactored by {model_name}:\n"
        f"- {verified} passed syntax validation on first try.\n"
        f"- {fixed} required AI self-healing syntax repairs.\n"
        f"- {failed} failed.\n"
        f"Provide a concise executive summary on the refactoring quality and structural improvements for '{library_name}'."
    )

    ai_res = refactor_code("AnalyticsReport", prompt, model_name=model_name)
    summary = ai_res.get("explanation") or ai_res.get("refactored_code") if ai_res else "Summary unavailable."

    report_md = f"""# 📈 AI Refactoring Report: `{library_name}`

**Model Evaluated:** `{model_name}`  
**Total Functions Processed:** `{total}`  

---

## 📊 Performance Breakdown

| Metric | Count | Percentage |
|---|---|---|
| **Verified (1st Attempt)** | {verified} | {(verified/total)*100 if total else 0:.1f}% |
| **Self-Healed (Fixed)** | {fixed} | {(fixed/total)*100 if total else 0:.1f}% |
| **Failed / Skipped** | {failed} | {(failed/total)*100 if total else 0:.1f}% |

---

## 📝 Executive AI Summary

{summary}
"""

    with open(report_file, "w") as f:
        f.write(report_md)

    print(f"📝 Report saved: '{report_file}'")
