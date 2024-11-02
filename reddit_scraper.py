import praw
import pandas as pd
import re # Joey - this is used for fact checking

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


def scrape_subreddits(subreddits, category):
    for sub_name in subreddits:
        try:
            subreddit = reddit.subreddit(sub_name)
            num_members = subreddit.subscribers

            #Joey - hot posts in each subreddit with a cap of 15. 

            ## Is hot a good category? - Maybe Top of this month? week?

            for post in subreddit.hot(limit=15):
                mod_interaction = "Yes" if post.stickied else "No"

                fact_checking = "Yes" if detect_fact_checking(post) else "No"
                
                keyword = "kamala" #Joey - keyword searching
                if re.search(keyword, post.title + post.selftext, re.IGNORECASE):
                    awards = post.total_awards_received
                    data.append({
                        'Keyword' : keyword,
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

# Joey - run scrapper!
scrape_subreddits(political_subreddits, 'General Politics')
scrape_subreddits(ideological_subreddits, "Ideological Politics")

df = pd.DataFrame(data)

df.to_csv('reddit_political_posts_analysis.csv', index=False)
print("Data collection completed. Check csv for info.")


