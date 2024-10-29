from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Important
username = "UCSCResearch"
password = "wasd123!!!"
phone_number = ""

# Set up Selenium WebDriver (Chrome in this case)
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode, comment this out if you want to see the browser
chrome_options.binary_location = "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"    
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Provide path to your chromedriver
webdriver_service = Service()  # Update with the actual path to your chromedriver
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Navigate to X (Twitter)
driver.get("https://x.com/i/flow/login")

# Wait for the page to load
time.sleep(2)

# Wait for the page to load and for the element to be present
wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds

# Enter username
username_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
username_input.send_keys(username)
username_input.send_keys(Keys.RETURN)

# Wait for the page to load and for the element to be present
wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds

# try:
#     # Check if there's additional authentication
#     search_words = ["unusual", "activity", "safe"]
#     # Get the page content as text
#     page_text = driver.find_element(By.CLASS_NAME, "modal-header").text
#     print(page_text)

#     # Check each word
#     for word in search_words:
#         if word in page_text:
#             # Enter phone number

# INCLUDE LATER
# phone_number_input = wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
# phone_number_input.send_keys(phone_number)
# phone_number_input.send_keys(Keys.RETURN)


#             break
# except:
#     pass

# Enter password (assuming username has been entered successfully)
password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
password_input.send_keys(password)
password_input.send_keys(Keys.RETURN)

# Wait for the home page to load
time.sleep(5)

# Navigate to the profile page or search for a hashtag/user
# For example, we'll scrape tweets from a specific user's profile
driver.get("https://x.com/elonmusk")

time.sleep(5)

# Scroll the page to load more tweets
last_height = driver.execute_script("return document.body.scrollHeight")

tweets = []

start_time = time.time()
timeout = 15

while True:
    # Extract tweets
    tweet_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweetText']")

    for tweet in tweet_elements:
        tweets.append(tweet.text)
    
    # Scroll down to load more tweets
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # Wait for new tweets to load
    time.sleep(1)
    
    # Check if the page height has changed, to stop scrolling
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

    # Check if the time limit has been reached
    elapsed_time = time.time() - start_time
    if elapsed_time > timeout:
        print(f"Time limit of {timeout} seconds reached. Exiting loop.")
        break

# Close the browser
driver.quit()

# Print extracted tweets
for i, tweet in enumerate(tweets):
    print(f"Tweet {i+1}: {tweet}")
