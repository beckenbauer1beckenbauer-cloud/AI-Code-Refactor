import json
import matplotlib.pyplot as plt
import numpy as np
import logging
from src.engine import refactor_code_with_ollama

logger = logging.getLogger(__name__)

def generate_analytics_report(metrics_old, metrics_new):
    """Sends metrics to Ollama to generate a professional summary report."""
    prompt = f"""
    You are a Senior Python Software Quality Analyst. 
    Analyze the following metrics comparing a Legacy Python Codebase to its Refactored version.
    
    Metrics:
    - Legacy Avg Docstring Length: {metrics_old['avg_docstring_len']} chars
    - Refactored Avg Docstring Length: {metrics_new['avg_docstring_len']} chars
    - Legacy Functions with Type Hints: {metrics_old['type_hint_pct']}%
    - Refactored Functions with Type Hints: {metrics_new['type_hint_pct']}%

    Generate a brief, well-organized professional report (bullet points).
    """
    
    # We use the engine to generate the text report
    report_data = refactor_code_with_ollama("AnalyticsReport", prompt)
    return report_data.get("explanation", "Could not generate report.") if report_data else "Report generation failed."

def calculate_metrics(dataset):
    """Calculates code quality metrics for a given dataset."""
    total_funcs = len(dataset)
    if total_funcs == 0:
        return {'avg_docstring_len': 0, 'type_hint_pct': 0}
    
    total_doc_len = 0
    funcs_with_hints = 0
    
    for entry in dataset:
        docstring = entry.get('explanation', '')
        total_doc_len += len(docstring)
        
        code = entry.get('refactored_code', '')
        if '->' in code or (':' in code and '=' not in code and 'def' in code):
            funcs_with_hints += 1
            
    return {
        'avg_docstring_len': round(total_doc_len / total_funcs, 2),
        'type_hint_pct': round((funcs_with_hints / total_funcs) * 100, 2)
    }

def run_analysis(old_file, new_file, output_plot="data/comparative_analysis.png"):
    """Runs the full analytics suite and saves a plot."""
    with open(old_file, "r") as f: old_data = json.load(f)
    with open(new_file, "r") as f: new_data = json.load(f)
    
    metrics_old = calculate_metrics(old_data)
    metrics_new = calculate_metrics(new_data)
    
    # Plotting code...
    labels = ['Docstring Len', 'Type Hints (%)']
    legacy_vals = [metrics_old['avg_docstring_len'], metrics_old['type_hint_pct']]
    refactored_vals = [metrics_new['avg_docstring_len'], metrics_new['type_hint_pct']]
    
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - 0.17, legacy_vals, 0.35, label='Legacy', color='gray')
    ax.bar(x + 0.17, refactored_vals, 0.35, label='Refactored', color='green')
    
    ax.set_title('Quality Improvement Analysis')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    plt.savefig(output_plot)
    logger.info(f"Report plot saved to {output_plot}")
    
    return generate_analytics_report(metrics_old, metrics_new)
