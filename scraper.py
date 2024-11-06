import schedule
import time
from twitter_scraper import getTwitterData
from reddit_scraper import getRedditData

if __name__=='__main__':

    def job():
        try:
            print("Extracting Twitter Data")
            getTwitterData()
        except Exception as error:
            print("ERROR: Scraper aborted\n", error)

        try:
            print("Extracting Reddit Data")
            getRedditData()
        except Exception as error:
            print("ERROR: Scraper aborted\n", error)

    schedule.every().hour.at(":00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(30)