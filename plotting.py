def generate_refactoring_report(input_file="final_dataset.json", output_image="refactoring_analysis.png"):
    """
    Reads the processed dataset and generates a comparison plot 
    between original and refactored code lengths.
    """
    try:
        # Load the dataset
        with open(input_file, "r") as f:
            dataset = json.load(f)
        
        if not dataset:
            print("⚠️ Dataset is empty. Cannot generate plot.")
            return

        # Extract data
        names = [entry['function'] for entry in dataset]
        orig_lengths = [len(entry['original_code']) for entry in dataset]
        refactored_lengths = [len(entry['refactored_code'] or '') for entry in dataset]

        # Create the plot
        plt.figure(figsize=(12, 6))
        bar_width = 0.35
        index = range(len(names))

        plt.bar(index, orig_lengths, bar_width, label='Original Code Length', color='gray')
        plt.bar([i + bar_width for i in index], refactored_lengths, bar_width, label='Refactored Code Length', color='blue')

        # Formatting
        plt.xlabel('Functions')
        plt.ylabel('Character Count')
        plt.title('Code Expansion Analysis: Original vs Refactored')
        plt.xticks([i + bar_width/2 for i in index], names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        # Save and display
        plt.savefig(output_image)
        plt.show()
        print(f"✅ Analysis saved to '{output_image}'.")

    except FileNotFoundError:
        print(f"❌ Error: '{input_file}' not found. Did you run the processor?")
    except Exception as e:
        print(f"❌ Plotting error: {e}")

# Execute the analysis
generate_refactoring_report()
