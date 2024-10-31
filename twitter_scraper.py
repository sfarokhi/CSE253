from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import json
import time

class JSONObject:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.data = self._load_json()
    
    def _load_json(self):
        """Loads the JSON data from the specified file."""
        with open(self.json_file_path, 'r') as file:
            return json.load(file)
    
    def get(self, key, default=None):
        """Retrieves the value for a given key, or returns a default if the key is not found."""
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
    
    def save(self):
        with open(self.json_file_path, 'w') as file:
            json.dump(self.data, file, indent=4)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __str__(self):
        return json.dumps(self.data, indent=4)

def return_data(tweets):
    for i, tweet in enumerate(tweets):
        print(f"Tweet {i+1}:")
        print(f"Author: {tweet['author']}")
        print(f"Text: {tweet['text']}")
        print(f"View Count: {tweet['view_count']}")
        print(f"Timestamp: {tweet['timestamp']}")
        print(f"Certified: {tweet['certified']}")
        print(f"Likes: {tweet['likes']}")
        print(f"Retweets: {tweet['retweets']}")
        print("-" * 40)

if __name__ == '__main__':
    settings = JSONObject(sys.argv[1])
    username = settings['username']
    password = settings['password']

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    webdriver_service = Service()
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.get("https://x.com/i/flow/login")

    time.sleep(2)
    wait = WebDriverWait(driver, 10)

    username_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
    username_input.send_keys(username)
    username_input.send_keys(Keys.RETURN)

    password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

    driver.get("https://x.com/search-advanced?vertical=trends")
    try:
        for option, value in settings['advanced-search'].items():
            if value:
                foo = wait.until(EC.presence_of_element_located((By.NAME, option)))
                foo.send_keys(value)
        foo.send_keys(Keys.RETURN)

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(5)
    tweets = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    # While extracting tweets
    while len(tweets) < settings['max-tweets']:
        
        # Get current tweets on page
        current_url = driver.current_url
        tweet_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='tweet']")))

        # For each tweet
        for tweet in tweet_elements:
            try:
                tweet_expanded = False  # Track if "Show more" was clicked
                
                # Click "Show more" if the button is present to expand the tweet text
                show_more_button = tweet.find_element(By.CSS_SELECTOR, "[data-testid='tweet-text-show-more-link']")
                if show_more_button:
                    show_more_button.click()
                    tweet_expanded = True

                # Extract tweet information
                tweet_text = tweet.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']").text
                view_count = tweet.find_element(By.CSS_SELECTOR, "[data-testid='viewCount']").text
                timestamp = tweet.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
                certified = "Yes" if tweet.find_element(By.CSS_SELECTOR, "[data-testid='icon-verified']") else "No"
                fact_checked = "Yes" if tweet.find_element(By.CSS_SELECTOR, "[data-testid='birdwatch-pivot']") else "No"
                author = tweet.find_element(By.CSS_SELECTOR, "div[role='link'] span").text
                
                # Safely get likes and retweets, handling potential empty elements
                likes_element = tweet.find_element(By.CSS_SELECTOR, "[data-testid='like']")
                likes = likes_element.text if likes_element else "0"
                
                retweets_element = tweet.find_element(By.CSS_SELECTOR, "[data-testid='reply']")
                retweets = retweets_element.text if retweets_element else "0"
                
                # Create a tweet dictionary to store the information
                tweet_info = {
                    "text": tweet_text,
                    "view_count": view_count,
                    "timestamp": timestamp,
                    "certified": certified,
                    "fact_checked": fact_checked,
                    "author": author,
                    "likes": likes,
                    "retweets": retweets,
                }

                # Check for duplicate tweets before adding to the list
                if tweet_info not in tweets:
                    tweets.append(tweet_info)
                
                # If "Show more" was clicked, go back to the main tweet view
                if tweet_expanded:
                    go_back = tweet.find_elements(By.CSS_SELECTOR, "[data-testid='app-bar-back']")
                    if go_back:
                        go_back[0].click()
                        tweet_expanded = False

            except Exception as e:
                print(f"Error in tweet extraction: {e}")

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("No more tweets to load.")
                driver.quit()    
                return_data(tweets)
                exit(0)
            last_height = new_height
