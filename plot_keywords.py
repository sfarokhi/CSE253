import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

def plot_Keyword_counts(df, base_filename):
    # Filter out rows where the value in 'Keyword' is the same as the column name
    df = df[df['Keyword'] != 'Keyword']
    
    # Count the entries for each Keyword
    Keyword_counts = df['Keyword'].value_counts()
    
    # Filter out categories with fewer than 25 entries
    Keyword_counts = Keyword_counts[Keyword_counts >= 5]
    
    # Plot the bar graph
    plt.figure(figsize=(14, 8))
    bars = Keyword_counts.plot(kind='bar', color='skyblue')
    
    # Add title and labels
    plt.title(f'Number of Entries per Keyword in {base_filename}')
    plt.xlabel('Keyword')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right', fontsize=10, x=0.02)  # Move labels slightly to the right
    plt.legend(['Keyword Count'])
    
    # Add the total number of each entry above their respective bar
    for bar in bars.containers:
        bars.bar_label(bar, label_type='edge', padding=3, rotation=90)
    
    # Save the plot as a PNG file in the 'graphs' folder
    os.makedirs('keyword_graphs', exist_ok=True)
    plt.tight_layout()
    plt.savefig(f'keyword_graphs/{base_filename}_Keyword_counts.png')
    
    # Clear the plot to avoid overlap in subsequent plots
    plt.clf()

def plot_all_csv_in_folder(folder_path):
    grouped_files = defaultdict(list)
    
    # Group files by their base name (excluding date and time)
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            base_name = '_'.join(filename.split('_')[:-2])  # Assuming the last two parts are date and time
            grouped_files[base_name].append(os.path.join(folder_path, filename))
    
    # Iterate over each group and plot combined data
    for base_name, file_list in grouped_files.items():
        combined_df = pd.DataFrame()
        for file_path in file_list:
            try:
                df = pd.read_csv(file_path)
                combined_df = pd.concat([combined_df, df], ignore_index=True)
            except pd.errors.EmptyDataError:
                print(f"The file {file_path} is empty. Skipping...")
            except pd.errors.ParserError:
                print(f"The file {file_path} could not be parsed. Skipping...")
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")
        
        if not combined_df.empty:
            plot_Keyword_counts(combined_df, base_name)

# Example usage
folder_path = 'reddit_data'  # Change this to the path where your CSV files are stored
plot_all_csv_in_folder(folder_path)
