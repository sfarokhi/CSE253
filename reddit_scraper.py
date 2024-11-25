import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib

# Use a non-interactive backend to avoid display issues
matplotlib.use('Agg')

def plot_Keyword_counts(csv_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Filter out rows where the value in 'Keyword' is the same as the column name
    df = df[df['Keyword'] != 'Keyword']
    
    # Count the entries for each Keyword
    Keyword_counts = df['Keyword'].value_counts()
    
    # If there are no valid entries, skip the plotting
    if Keyword_counts.empty:
        print(f"No valid entries to plot in {csv_file}")
        return
    
    # Filter out categories with fewer than 25 entries
    Keyword_counts = Keyword_counts[Keyword_counts >= 25]
    
    # If there are no categories left after filtering, skip the plotting
    if Keyword_counts.empty:
        print(f"No categories with more than 25 entries in {csv_file}")
        return
    
    # Plot the bar graph
    plt.figure(figsize=(14, 8))
    bars = Keyword_counts.plot(kind='bar', color='skyblue')
    
    # Add title and labels
    plt.title(f'Number of Entries per Keyword in {os.path.basename(csv_file)}')
    plt.xlabel('Keyword')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right', fontsize=10, x=0.02)  # Move labels slightly to the right
    plt.legend(['Keyword Count'])
    
    # Add the total number of each entry above their respective bar
    for bar in bars.containers:
        bars.bar_label(bar, label_type='edge', padding=3, rotation=90)
    
    # Save the plot as a PNG file in the 'graphs' folder
    os.makedirs('graphs', exist_ok=True)
    plt.tight_layout()
    plt.savefig(f'graphs/{os.path.splitext(os.path.basename(csv_file))[0]}_Keyword_counts.png')
    
    # Clear the plot to avoid overlap in subsequent plots
    plt.clf()

def plot_all_csv_in_folder(folder_path):
    # Iterate over all CSV files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            csv_file = os.path.join(folder_path, file_name)
            plot_Keyword_counts(csv_file)

# Example usage
folder_path = 'reddit_data'  # Update this variable with the appropriate folder path
plot_all_csv_in_folder(folder_path)
