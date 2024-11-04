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

# Function to fetch post texts
def fetch_posts(driver):
    post_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1a6qonq')]")
    post_texts = []
    for i, post_container in enumerate(post_containers):
        try:
            post_text_elements = post_container.find_elements(By.XPATH, ".//span[contains(@class, 'x1lliihq')]")
            post_text = " ".join([element.text for element in post_text_elements if element.text.strip()]).strip()
            if post_text:
                post_texts.append(post_text)
                print(f"Post {i + 1}: {post_text}")
            else:
                print(f"Post {i + 1}: No Post Text")
            print('-' * 80)
        except Exception as e:
            print(f"An error occurred while processing post {i + 1}: {str(e)}")
    return post_texts

if __name__=='__main__':

    # Set up the Chrome WebDriver
    service = Service() # Service('/usr/local/bin/chromedriver')

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.implicitly_wait(0.5)
    wait = WebDriverWait(driver, 10)    

    # Start the timer
    start_time = time.time()

    # Open the login page
    driver.get('https://www.threads.net/login')
    
    username = 'aggarwalriya48@gmail.com'
    password = 'ucsc@UCSC.23'
    searches = ["Kamala Harris", "Donald Trump"]
    max_results = 10

    username_input = wait.until(EC.presence_of_element_located((By.XPATH, './/input[@placeholder="Username, phone or email"]')))
    username_input.send_keys(username)

    password_input = wait.until(EC.presence_of_element_located((By.XPATH, './/input[@placeholder="Password"]')))
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

    # Print the current URL for debugging
    current_url = driver.current_url
    print(f"Current URL after login attempt: {current_url}")

    for search in searches:
        # Go to the search bar
        driver.get('https://www.threads.net/search')
        search_tab = wait.until(EC.presence_of_element_located((By.XPATH, './/input[@placeholder="Search"]')))
        search_tab.send_keys(search)
        search_tab.send_keys(Keys.ENTER)

        # Fetch initial posts before scrolling
        fetch_posts(driver=driver)

        # Scroll to load more posts
        scroll_pause_time = 2  # Time to wait after each scroll
        last_height = driver.execute_script("return document.body.scrollHeight")

        num_results = 0
        flag = True
        
        while flag and num_results < max_results:
            # Check if 30 seconds have passed
            if time.time() - start_time > 30:
                print("Stopping the script after 30 seconds.")
                flag = False
                break
            
            # Fetch posts again after scrolling
            results = fetch_posts(driver=driver)
            num_results += len(results)
            
            # Wait to load the page
            time.sleep(scroll_pause_time)
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height or num_results == max_results:
                flag = False

            last_height = new_height
