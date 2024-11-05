import praw
import pandas as pd
import re # Joey - this is used for fact checking
from datetime import datetime

# Joey - initializes the API
reddit = praw.Reddit(
    client_id='H9PAUJDUsGccxBGweJPsuA',
    client_secret='mRPoa2Lhnv-lT_fEqQhMNH9ikv1I9Q',
    user_agent='cse253_reddit_scraper: v1.0'  
)

# Joey - list of political subreddits, add more or less depending on resources

political_subreddits = ['Wikileaks', 'News', 'PoliticalDiscussion','NeutralPolitics' , 'moderatepolitics', 'technology']

# Joey - above list is more neutral based politics, below is a list of 
#        subreddits that are more ideologically focused.
ideological_subreddits = ['democrats', 'Republican', 'Conservative', 'Libertarian', 'Anarchism', 'Socialism',
                          'Progressive','Republicanism', 'Conservatives', 'dailywire', 'Liberal', 'KamalaHarris', 'Impeach_Trump']

data = []

# Joey - is fact checking mentioned? function below
def detect_fact_checking(post):
    fact_check_keywords = r'fact[-\s]?check|disinformation|misinformation|verified|debunk|factchecked|false|true|hoax|rumor|truth'
    return bool(re.search(fact_check_keywords, post.title + post.selftext, re.IGNORECASE))


def scrape_subreddits(subreddits, category, keywords):
    for sub_name in subreddits:
        try:
            subreddit = reddit.subreddit(sub_name)
            num_members = subreddit.subscribers

            #Joey - hot posts in each subreddit with a cap of 15. 

            ## Is hot a good category? - Maybe Top of this month? week?

            for post in subreddit.hot(limit=15):
                mod_interaction = "Yes" if post.stickied else "No"

                fact_checking = "Yes" if detect_fact_checking(post) else "No"
                
                matched_keyword = next((keyword for keyword in keywords if re.search(keyword, post.title + post.selftext, re.IGNORECASE)), None)
                if matched_keyword:
                    awards = post.total_awards_received
                    data.append({
                        'Keyword' : matched_keyword,
                        'Subreddit': sub_name,
                        'Category': category,
                        'Members': num_members,
                        'Title': post.title,
                        'Upvotes': post.score,
                        'Comments': post.num_comments,
                        'Moderator Interaction': mod_interaction,
                        'Fact-Checking Mention': fact_checking,
                        'Total Awards': awards,
                        'URL': post.url,
                        'Original Post URL': post.permalink
                    })

        except Exception as e:
            print(f"Error accessing {sub_name}: {e}")
            continue

keywords_list = ["election", "campaign", "win", "Trump", "Kamala", "America", "turnout", "vote", "ballot"]

# Joey - run scrapper!
scrape_subreddits(political_subreddits, 'General Politics', keywords_list)
scrape_subreddits(ideological_subreddits, "Ideological Politics", keywords_list)

df = pd.DataFrame(data)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

df.to_csv('csv/reddit/cumulative_reddit_political_posts_analysis.csv', mode='a', index=False, header=not pd.io.common.file_exists(f'cumulative_reddit_political_posts_analysis_{timestamp}.csv'))
df.to_csv(f'csv/reddit/General_Election_Tone_{timestamp}.csv', index=False) ## change for each run

print("Data collection completed. Check csv for info.")


