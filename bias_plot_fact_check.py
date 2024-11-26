import os
import pandas as pd
import matplotlib.pyplot as plt

# Load and clean data
def load_clean_data(file_path):
    df = pd.read_csv(file_path)
    for column in ['Upvotes', 'Comments', 'Members']:
        df = df[df[column] != column]
    df['Upvotes'] = df['Upvotes'].astype(int)
    df['Comments'] = df['Comments'].astype(int)
    df['Members'] = df['Members'].astype(int)
    df = df[(df['Upvotes'] > 0) & (df['Comments'] > 0) & (df['Members'] > 0)]
    return df

# Filter data on Category
def filter_ideological_politics(df, filter):
    if filter == True:
        return df[df['Category'] == 'Ideological Politics']
    else:
        return df[df['Category'] == 'General Politics']

# Calculate engagement metrics and filter popular posts
def filter_popular_posts(df):
    # Calculate engagement rate
    df = df.copy()  # Avoid SettingWithCopyWarning
    df['engagement_rate'] = ((df['Upvotes'] + df['Comments']) / df['Members']) * 100
    
    # Calculate z-scores
    df['upvote_mean'] = df.groupby('Subreddit')['Upvotes'].transform('mean')
    df['upvote_std'] = df.groupby('Subreddit')['Upvotes'].transform('std')
    df['upvote_zscore'] = (df['Upvotes'] - df['upvote_mean']) / df['upvote_std']
    
    # Filter popular posts
    popular_posts_df = df[
        (df['upvote_zscore'] > 0.4) &
        (df['engagement_rate'] > df['engagement_rate'].quantile(0.4))
    ].copy()
    return popular_posts_df

# Plot grouped bar chart for popular posts and fact-check/mod interaction by bias
def plot_posts_by_bias(df, popular_posts_df, filter):
    biases = ['L', 'R', 'N']
    metrics = {
        'Total Posts': [],
        'Fact Check Posts': [],
        'Popular Posts': [],
        'Fact Checked Popular Posts': []
    }
    
    for bias in biases:
        bias_df = df[df['Bias'] == bias]
        popular_bias_df = popular_posts_df[popular_posts_df['Bias'] == bias]
        
        total_count = len(bias_df)
        fact_check_count = len(bias_df[bias_df['Fact-Checking Mention'] == 'Yes'])
        popular_count = len(popular_bias_df)
        fact_checked_popular_count = len(popular_bias_df[popular_bias_df['Fact-Checking Mention'] == 'Yes'])
        
        metrics['Total Posts'].append(total_count)
        metrics['Fact Check Posts'].append(fact_check_count)
        metrics['Popular Posts'].append(popular_count)
        metrics['Fact Checked Popular Posts'].append(fact_checked_popular_count)
    
    # Create grouped bar chart
    x = range(len(biases))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bars_total = ax.bar(x, metrics['Total Posts'], width, label='Total Posts')
    bars_fact_check = ax.bar([i + width for i in x], metrics['Fact Check Posts'], width, label='Fact Check Posts')
    bars_popular = ax.bar([i + 2 * width for i in x], metrics['Popular Posts'], width, label='Popular Posts')
    bars_fact_checked_popular = ax.bar([i + 3 * width for i in x], metrics['Fact Checked Popular Posts'], width, label='Fact Checked Popular Posts')
    
    
    ax.set_xlabel('Bias')
    ax.set_ylabel('Total Number of Posts')
    #change title based on Ideological or General
    if filter == True:
        ax.set_title('Post Metrics across Ideological Subreddits aligned with Biases')
    else:
        ax.set_title('Post Metrics across General Subreddits aligned with Biases')
    ax.set_xticks([i + 1.5 * width for i in x])
    ax.set_xticklabels(biases)
    ax.legend()

    # Add value labels to each bar
    for bars in [bars_total, bars_fact_check, bars_popular, bars_fact_checked_popular]:
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval + 1, int(yval), ha='center', va='bottom')

    
    plt.tight_layout()
    os.makedirs('fact_check_graphs', exist_ok=True)
    if filter == True:
        plt.savefig('fact_check_graphs/w1_ideological_bias_fact_check_analysis_bias.png')
    else:
        plt.savefig('fact_check_graphs/w1_general_bias_fact_check_analysis_bias.png')

# Main script to execute
def main():
    file_path = 'reddit_data/cumulative_reddit_political_posts_analysis_with_bias.csv'
    df = load_clean_data(file_path)
    filter = True
    while filter == True:
        ideological_df = filter_ideological_politics(df, filter)
        popular_posts_df = filter_popular_posts(ideological_df)
        plot_posts_by_bias(ideological_df, popular_posts_df, filter)
        filter = False
        continue
    else:
        print(filter)
        ideological_df = filter_ideological_politics(df, filter)
        popular_posts_df = filter_popular_posts(ideological_df)
        plot_posts_by_bias(ideological_df, popular_posts_df, filter)
    

if __name__ == "__main__":
    main()
