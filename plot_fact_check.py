import os
import pandas as pd
import matplotlib.pyplot as plt

#Joey fact checking on political posts. only using cumulative file as of now

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

# Calculate engagement metrics and filter popular posts
def filter_popular_posts(df):
    # Calculate engagement rate
    df['engagement_rate'] = ((df['Upvotes'] + df['Comments']) / df['Members']) * 100
    
    # Calculate z-scores
    df['upvote_mean'] = df.groupby('Subreddit')['Upvotes'].transform('mean')
    df['upvote_std'] = df.groupby('Subreddit')['Upvotes'].transform('std')
    df['upvote_zscore'] = (df['Upvotes'] - df['upvote_mean']) / df['upvote_std']
    
    # Filter popular posts
    popular_posts_df = df[
        (df['upvote_zscore'] > 0.4) &
        (df['engagement_rate'] > df['engagement_rate'].quantile(0.4))
    ]
    return popular_posts_df

# Plot grouped bar chart for popular posts and fact-check/mod interaction
def plot_popular_posts(df, popular_posts_df):
    categories = ['General Politics', 'Ideological Politics']
    metrics = {
        'Total Posts': [],
        'Fact Check Posts': [],
        'Popular Posts': [],
        'Fact Checked Popular Posts': []
    }
    
    for category in categories:
        category_df = df[df['Category'] == category]
        popular_category_df = popular_posts_df[popular_posts_df['Category'] == category]
        
        total_count = len(category_df)
        fact_check_count = len(category_df[category_df['Fact-Checking Mention'] == 'Yes'])
        popular_count = len(popular_category_df)
        fact_checked_popular_count = len(popular_category_df[popular_category_df['Fact-Checking Mention'] == 'Yes'])
        
        metrics['Total Posts'].append(total_count)
        metrics['Fact Check Posts'].append(fact_check_count)
        metrics['Popular Posts'].append(popular_count)
        metrics['Fact Checked Popular Posts'].append(fact_checked_popular_count)
    
    # Print Moderator Interaction and Fact-Checking Mention columns for debugging
    print("Moderator Interaction column values:\n", df['Moderator Interaction'].value_counts())
    print("Fact-Checking Mention column values:\n", df['Fact-Checking Mention'].value_counts())
    
    # Create grouped bar chart
    x = range(len(categories))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.bar(x, metrics['Total Posts'], width, label='Total Posts')
    ax.bar([i + width for i in x], metrics['Fact Check Posts'], width, label='Fact Check Posts')
    ax.bar([i + 2 * width for i in x], metrics['Popular Posts'], width, label='Popular Posts')
    ax.bar([i + 3 * width for i in x], metrics['Fact Checked Popular Posts'], width, label='Fact Checked Popular Posts')
    
    ax.set_xlabel('Category')
    ax.set_ylabel('Count')
    ax.set_title('Comparison of Posts and Fact-Checking')
    ax.set_xticks([i + 1.5 * width for i in x])
    ax.set_xticklabels(categories)
    ax.legend()
    
    plt.tight_layout()
    os.makedirs('fact_check_graphs', exist_ok=True)
    plt.savefig('fact_check_graphs/fact_check_analysis_w1.png')
    plt.show()

# Main script to execute
def main():
    file_path = 'reddit_data/cumulative_reddit_political_posts_analysis.csv'
    df = load_clean_data(file_path)
    popular_posts_df = filter_popular_posts(df)
    plot_popular_posts(df, popular_posts_df)

if __name__ == "__main__":
    main()
