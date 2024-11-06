import schedule
from datetime import datetime
import time
from twitter_scraper import getTwitterData
# from reddit_scraper import getRedditData

if __name__=='__main__':
    getTwitterData()

# def job():
    
#     try:
#         print("Extracting Twitter Data")
#         getTwitterData()

#         print("Extracting Reddit Data")
#         getRedditData()
#     except Exception as error:
#         print("ERROR: Scraper aborted\n", error)

# schedule.every().hour.at(":00").do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(60)