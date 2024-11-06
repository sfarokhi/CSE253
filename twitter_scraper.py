from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import json
from datetime import datetime
import time
import csv
import random

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

def compile_results(data, testname):
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'twitter_results/{testname}_{timestamp}.csv'

        # Ensure data is a list of dictionaries (JSON objects)
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # Gather all unique keys across all dictionaries in data
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())
            
            # Open the CSV file for writing
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                # Create a CSV writer object with all unique keys as fieldnames
                writer = csv.DictWriter(f, fieldnames=all_keys)
                
                # Write the header
                writer.writeheader()
                
                # Write the rows
                writer.writerows(data)
            
            print(f"Data successfully saved to {filename}")
        else:
            raise ValueError("Input data must be a list of dictionaries (JSON objects).")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")



def getTwitterData():
    settings = JSONObject("util/twitter_config.json")
    username = settings['username']
    email = settings['email']
    password = settings['password']

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    webdriver_service = Service()
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.implicitly_wait(0.5)
    wait = WebDriverWait(driver, 10)

    
    try:
        driver.get("https://x.com/i/flow/login")

        username_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)

        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(2)
        
    except:
        wait(3)
        driver.get("https://x.com/i/flow/login")

        email_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)

        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

    for parameters in settings['test-parameters']:

        time.sleep(random.randint(10, 15))
        max_tweets = parameters['max-tweets']
        driver.get("https://x.com/search-advanced?vertical=trends")
        try:
            for option, value in parameters['advanced-search'].items():
                if value:
                    foo = wait.until(EC.presence_of_element_located((By.NAME, option)))
                    foo.send_keys(value)
            foo.send_keys(Keys.RETURN)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(5)
        tweets = []
        duplicate_tweet_counter = 0

        # While extracting tweets
        while len(tweets) < max_tweets:
            try:
                # Get current tweets on page
                tweet_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='tweet']")))

                # For each tweet
                for tweet in tweet_elements:
                    tweet_data = {
                        "username": "N/A",
                        "icon-verified": False,
                        "text": "N/A",
                        "timestamp": "N/A",
                        "replies": 0,
                        "reposts": 0,
                        "likes": 0,
                        "views": 0,
                        "fact-checked": False,
                    }

                    try:
                        metadata = tweet.find_element(By.XPATH, './/div[@aria-label][@role="group"]').get_attribute('aria-label')
                        for value in metadata.split(','):
                            parts = value.strip().split(' ')
                            if len(parts) >= 2:
                                metadata_number = int(parts[0])
                                metadata_type = parts[1]
                                tweet_data[metadata_type] = metadata_number
                    except Exception:
                        pass

                    try:
                        tweet_data['username'] = tweet.find_element(By.XPATH, './/a[contains(@href, "/") and @role="link"]').get_attribute("href").split('/')[-1]
                    except Exception:
                        pass

                    try:
                        tweet_data['timestamp'] = tweet.find_element(By.XPATH, './/time[@datetime]').get_attribute('datetime')
                    except Exception:
                        pass
                    
                    try:
                        tweet.find_element(By.CSS_SELECTOR, '[data-testid="icon-verified"]')
                        tweet_data['icon-verified'] = True
                    except NoSuchElementException:
                        pass

                    try:
                        tweet.find_element(By.CSS_SELECTOR, '[data-testid="birdwatch-pivot"]')
                        tweet_data['fact-checked'] = True
                    except NoSuchElementException:
                        pass

                    tweet_data['text'] = tweet.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']").text

                    # Check for duplicate tweets before adding to the list
                    if tweet_data not in tweets:
                        tweets.append(tweet_data)
                        duplicate_tweet_counter = 0
                    else:
                        duplicate_tweet_counter += 1
                        if duplicate_tweet_counter > 5:
                            print("Ran out of unique tweets.")
                            break

                # Scroll down to load more tweets
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

            except Exception as e:
                print(f"Error while fetching tweets: {e}")
                break

        # Compile results after exiting the while loop
        if tweets:
            compile_results(data=tweets, testname=parameters['test-id'])
        else:
            print("No tweets found for this test parameter set.")
