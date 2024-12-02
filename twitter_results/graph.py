import pandas as pd
import matplotlib.pyplot as plt
import argparse
from scipy.stats import gaussian_kde
import numpy as np

def filter_outliers(df, column):
    """
    Filter out outliers using the IQR method for a given column.
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

def plot_heatwave(csv_file, x_column, y_column):
    """
    Plot a heat wave-style graph for the selected columns in a CSV.
    """
    try:
        # Read the CSV file
        data = pd.read_csv(csv_file)

        # Filter out outliers for both x and y columns
        data = filter_outliers(data, x_column)
        data = filter_outliers(data, y_column)

        # Extract the data points
        x = data[x_column]
        y = data[y_column]

        # Calculate the density of points using a Gaussian kernel
        xy = np.vstack([x, y])
        z = gaussian_kde(xy)(xy)
        
        # Normalize density for better visualization
        z = (z - z.min()) / (z.max() - z.min())

        # Create the scatter plot with density coloring
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(
            x,
            y,
            c=z,
            cmap="viridis",
            edgecolors="none",  # No visible edges
            alpha=0.8,         # Adjust point transparency
            s=50               # Point size
        )

        # Add color bar to indicate density levels
        cbar = plt.colorbar(scatter)
        cbar.set_label('Density')

        # Add labels and title
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(f"{y_column} vs {x_column}")
        plt.grid(True, alpha=0.5)

        # Save and show the plot
        output_file = f"{csv_file.split('.')[0].split('/')[1]},{x_column},{y_column}.png"
        plt.savefig(output_file)
        print("Heat wave graph saved as", output_file)
    except Exception as e:
        print(f"Error generating the plot: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot data from a CSV file.")
    parser.add_argument("x_column", help="Column name for the X-axis.")
    parser.add_argument("y_column", help="Column name for the Y-axis.")
    parser.add_argument("csv_file", help="Path to the CSV file.")
    args = parser.parse_args()

    # plot_graph(args.csv_file, args.x_column, args.y_column)
    plot_heatwave(args.csv_file, args.x_column, args.y_column)