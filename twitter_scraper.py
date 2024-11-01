from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
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

def compile_results(data, filename):
    try:
        # Ensure data is a list of dictionaries (JSON objects)
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Data successfully saved to {filename}")
        else:
            raise ValueError("Input data must be a list of dictionaries (JSON objects).")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")

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

    wait = WebDriverWait(driver, 10)

    username_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
    username_input.send_keys(username)
    username_input.send_keys(Keys.RETURN)

    password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(2)

    for parameters in settings['test-parameters']:

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
        last_height = driver.execute_script("return document.body.scrollHeight")
        new_height = last_height

        flag = True

        # While extracting tweets
        while flag and len(tweets) < max_tweets:
            
            # Get current tweets on page
            current_url = driver.current_url
            tweet_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='tweet']")))

            # For each tweet
            for tweet in tweet_elements:
                try:
                    tweet_expanded = False  # Track if "Show more" was clicked
                    tweet_data = {
                        "username": "N/A",
                        "icon-verified": False,
                        "fact-checked": False,
                        "text": "N/A",
                        "timestamp": "N/A",
                        "replies": 0,
                        "reposts": 0,
                        "likes": 0,
                        "bookmarks": 0,
                        "views": 0,
                    }

                    # Extract tweet information
                    metadata = tweet.find_element(By.XPATH, './/div[@aria-label][@role="group"]').get_attribute('aria-label')
                    try:
                        for value in metadata.split(','):
                            parts = value.strip().split(' ')
                            if len(parts) >= 2:
                                metadata_number = int(parts[0])
                                metadata_type = parts[1]
                                tweet_data[metadata_type] = metadata_number
                    except Exception as e:
                        print("Metadata parsing error")

                    try:
                        tweet_data['username'] = tweet.find_element(By.XPATH, './/a[contains(@href, "/") and @role="link"]').get_attribute("href").split('/')[-1]
                    except Exception as e:
                        print("Username doesn't exist???")

                    try:
                        tweet_data['timestamp'] = tweet.find_element(By.XPATH, './/time[@datetime]').get_attribute('datetime')
                    except Exception as e:
                        print("No timestamp")
                    
                    try:
                        tweet.find_element(By.CSS_SELECTOR, '[data-testid="icon-verified"]')
                        print("Verified")
                        tweet_data['icon-verified'] = True
                    except NoSuchElementException:
                        print("Not verified")
                    except Exception as e:
                        print("Error")

                    try:
                        tweet.find_element(By.CSS_SELECTOR, '[data-testid="birdwatch-pivot"]')
                        print("Fact Checked")
                        tweet_data['fact-checked'] = True
                    except NoSuchElementException:
                        print("Not Fact Checked")
                    except Exception as e:
                        print("Error")

                    # Click "Show more" if the button is present to expand the tweet text
                    try:
                        show_more_button = tweet.find_element(By.CSS_SELECTOR, "[data-testid='tweet-text-show-more-link']")
                        show_more_button.click()
                        tweet_expanded = True
                    except:
                        print("No extra text")

                    tweet_data['text'] = tweet.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']").text
                    
                    # If "Show more" was clicked, go back to the main tweet view
                    if tweet_expanded:
                        go_back = tweet.find_element(By.CSS_SELECTOR, "[data-testid='app-bar-back']")
                        go_back.click()
                        tweet_expanded = False
                    
                    # Check for duplicate tweets before adding to the list
                    if tweet_data not in tweets:
                        print("Added tweet")
                        tweets.append(tweet_data)
                    else:
                        print("Duplicate tweet")

                    print("-" * 20)

                    if len(tweets) >= max_tweets:
                        print("Max Tweets Reached")
                        compile_results(data=tweets, filename=f"results_{parameters['test-id']}.json")
                        flag = False
                        break

                except Exception as e:
                    print(f"There was an error {e}\n\n")
                    continue

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                print("No more tweets to load.")
                compile_results(data=tweets, filename=f"results_{parameters['test-id']}.json")
                flag = False
                break

            elif len(tweets) >= max_tweets:
                print("Complete.")
                compile_results(data=tweets, filename=f"results_{parameters['test-id']}.json")
                flag = False
                break

            else:
                last_height = new_height
