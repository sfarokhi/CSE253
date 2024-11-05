import schedule
from datetime import datetime
import time
from twitter_scraper import getTwitterData

def job():
    print("Extracting Twitter Data")
    file_name = (datetime.now().strftime('%Y-%m-%d %H:00'))
    getTwitterData()

schedule.every().hour.at(":00").do(job)

while True:
    schedule.run_pending()
    time.sleep(30)