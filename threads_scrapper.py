import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the Chrome WebDriver
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service)

# Start the timer
start_time = time.time()

# Open the login page
driver.get('https://www.threads.net')

try:
    # Wait for the initial "Log in" button to be present and click it
    login_prompt_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'x6ikm8r') and contains(@class, 'x10wlt62') and contains(text(), 'Log in')]"))
    )
    login_prompt_button.click()

    # Wait for the username field to be present and fill it in using class
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'x1i10hfl') and contains(@class, 'x9f619') and contains(@class, 'xggy1nq')]"))
    )
    username_input.send_keys('aggarwalriya48@gmail.com')

    # Wait for the password field to be present and fill it in using class
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
    )
    password_input.send_keys('ucsc@UCSC.23')

    # Wait for the login button to be present and click it
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'x6s0dn4') and contains(@class, 'xrvj5dj')]//div[contains(text(), 'Log in')]"))
    )
    login_button.click()

    # Wait for the login to complete by checking the URL
    WebDriverWait(driver, 10).until(EC.url_contains('login_success=true'))  # Using part of the expected URL

    # Print the current URL for debugging
    current_url = driver.current_url
    print(f"Current URL after login attempt: {current_url}")

    # Open the Threads profile
    driver.get('https://www.threads.net/@vp?hl=en')

    # Allow the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'x1a6qonq')]")))

    # Function to fetch post texts
    def fetch_posts():
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

    # Fetch initial posts before scrolling
    fetch_posts()

    # Scroll to load more posts
    scroll_pause_time = 2  # Time to wait after each scroll
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Check if 30 seconds have passed
        if time.time() - start_time > 30:
            print("Stopping the script after 30 seconds.")
            break
        
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait to load the page
        time.sleep(scroll_pause_time)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Fetch posts again after scrolling
    fetch_posts()

finally:
    # Close WebDriver
    driver.quit()
