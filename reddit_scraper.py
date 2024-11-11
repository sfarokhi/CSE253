import praw
import pandas as pd
import re # Joey - this is used for fact checking
from datetime import datetime
import schedule 
import time 

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

def getRedditData():
    global data
    tests ={
        "Post-Election Analysis & Results": ["results", "victory", "loss", "outcome", "recount", "certify", "electoral", "fraud", "election results", "biden", "harris", "trump", "vance", "president", "presidency", "house", "senate", "bernie", "supreme court"],
        "Voting Demographics": ["vote", "white", "black", "latino", "male", "female", "michigan", "urban", "rural", "suburban", "election map", "survey", "poll", "North Carolina", "Wisconsin", "Michigan", "Nevada", "Arizona", "Texas"],
        "International Affairs": ["gaza", "ukraine", "Zelenskyy", "putin", "north korea", "Kim Jong Un", "israel", "palestinian", "War", "Iran", "world war", "russia", "british", "uk", "europe", "china"],
        "Immigration": ["immigration", "policy change", "foreign relations", "treaties", "border", "asylum", "citizenship reform", "illegal", "haitian", "mexican", "south america", "border patrol", "mexico", "texas"],
        "Economic Projections and Environmental Policy": ["economic outlook", "inflation", "market response", "environmental plans", "clean energy", "sustainability", "economy", "gas", "prices", "tariffs", "money", "treasury", "hurricane", "wildfires", "global warming", "climate change", "plastic", "coal"],
        "Technology and Health": ["elon musk", "ai", "artificial intelligence", "cyber security", "RFK", "vaccine", "diseases", "Covid", "social media"]]
    }
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for test_name, keywords in tests.items():
        data = []
        scrape_subreddits(political_subreddits, 'General Politics', keywords)
        scrape_subreddits(ideological_subreddits, "Ideological Politics", keywords)

        df = pd.DataFrame(data)
        df.to_csv(f'reddit_results/{test_name}_{timestamp}.csv', index=False)
        df.to_csv('reddit_results/cumulative_reddit_political_posts_analysis.csv', mode='a', index=False, header=not pd.io.common.file_exists(f'reddit_results/cumulative_reddit_political_posts_analysis_{timestamp}.csv'))
    
    print("Data collection completed. Check csv for info.")

#scheduling

# schedule.every(1).hours.do(run_tests)
# end_time = time.time() + 30 * 24 * 60 * 60 #runs for 30 days, every hour

# while time.time() < end_time:
#     schedule.run_pending()
#     time.sleep(1)


    

