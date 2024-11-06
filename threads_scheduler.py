import schedule
import time
import threads_scraper  # Import the main module itself

if __name__ == '__main__':

    def run_threads_scraper():
        try:
            print("Running Threads Scraper")
            threads_scraper.main()  # Call the main function in threads_scraper.py
        except Exception as error:
            print("ERROR: Threads scraper aborted\n", error)

    # Schedule the Threads scraper job to run every hour at the start of the hour
    schedule.every(30).minutes.do(run_threads_scraper)

    # Keep the script running and check for pending tasks every 30 seconds
    while True:
        schedule.run_pending()
        time.sleep(30)
