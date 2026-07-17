import json
import matplotlib.pyplot as plt

def generate_plot(data_file="final_dataset.json"):
    """
    Reads the dataset and generates a comparison plot of code lengths.
    """
    try:
        with open(data_file, "r") as f:
            dataset = json.load(f)
        
        if not dataset:
            print("⚠️ Dataset is empty. Cannot generate plot.")
            return

        # Extract metrics
        names = [entry['function'] for entry in dataset]
        orig_lengths = [len(entry['original_code']) for entry in dataset]
        refactored_lengths = [len(entry['refactored_code']) for entry in dataset]

        # Create the plot
        plt.figure(figsize=(12, 6))
        bar_width = 0.35
        index = range(len(names))

        plt.bar(index, orig_lengths, bar_width, label='Original Code Length', color='gray')
        plt.bar([i + bar_width for i in index], refactored_lengths, bar_width, 
                label='Refactored Code Length', color='blue')

        plt.xlabel('Functions')
        plt.ylabel('Character Count')
        plt.title('Code Expansion Analysis: Original vs Refactored')
        plt.xticks([i + bar_width/2 for i in index], names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        # Save and Show
        plt.savefig("refactoring_analysis.png")
        plt.show()
        print("✅ Plot saved as 'refactoring_analysis.png'.")
        
    except FileNotFoundError:
        print(f"⚠️ Error: File '{data_file}' not found.")
    except Exception as e:
        print(f"⚠️ An error occurred during plotting: {e}")
