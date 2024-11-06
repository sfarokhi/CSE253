import os
import json
import csv
import time
from datetime import datetime
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright
from typing import Dict
import random

def login_to_threads(page, username, password): 
    """Logs into Threads using provided credentials."""
    page.goto("https://www.threads.net/login")
    try:
        page.wait_for_selector('input[placeholder="Username, phone or email"]', timeout=3000)
    except:
        try:
            page.wait_for_selector('a[role="link"]', timeout=3000)
            page.click('a[role="link"]')
        except:
            print("Neither main login form nor alternative login link is available.")
            raise Exception("Login option not found.")
    page.wait_for_selector('input[placeholder="Username, phone or email"]', timeout=10000)
    page.fill('input[placeholder="Username, phone or email"]', username)
    page.fill('input[placeholder="Password"]', password)
    page.click('text="Log in"')
    page.wait_for_load_state('networkidle')
    if page.url == "https://www.threads.net/?login_success=true":
        print("Login successful!")
    else:   
        raise Exception("Login failed.")

def parse_thread(data: Dict) -> Dict:
    """Parse Threads JSON dataset for the most important fields."""
    result = jmespath.search(
        """{
        text: post.caption.text,
        published_on: post.taken_at,
        id: post.id,
        code: post.code,
        username: post.user.username,
        user_verified: post.user.is_verified,
        user_id: post.user.id,
        repost_count: post.text_post_app_info.repost_count,
        reshare_count: post.text_post_app_info.reshare_count,
        like_count: post.like_count,
        comment_count: post.text_post_app_info.direct_reply_count
    }""",
        data,
    )
    if result:
        result["url"] = f"https://www.threads.net/@{result['username']}/post/{result['code']}"
    return result

def read_existing_codes(csv_filename):
    """Read existing post codes from the CSV file."""
    existing_codes = set()
    try:
        with open(csv_filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row:
                    existing_codes.add(row[0])
    except FileNotFoundError:
        print(f"CSV file {csv_filename} not found. A new one will be created.")
    return existing_codes

def fetch_posts(page, extracted_post_codes):
    """Fetches posts from the current page."""
    page_content = page.content()
    selector = Selector(page_content)
    hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()

    if not hidden_datasets:
        print("No embedded JSON data found on the page.")
        return []

    new_posts = []

    for hidden_dataset in hidden_datasets:
        if '"ScheduledServerJS"' not in hidden_dataset or "thread_items" not in hidden_dataset:
            continue
        data = json.loads(hidden_dataset)
        thread_items = nested_lookup("thread_items", data)
        if not thread_items:
            continue

        for thread in thread_items:
            for t in thread:
                parsed_post = parse_thread(t)
                if parsed_post:
                    post_code = parsed_post.get('code')
                    if post_code and post_code not in extracted_post_codes:
                        extracted_post_codes.add(post_code)
                        new_posts.append(parsed_post)
                        print(f"Found new post: {post_code}")

    return new_posts

def save_posts_to_csv(posts, csv_filename):
    """Saves posts to CSV, only saving new posts."""
    os.makedirs("thread_results", exist_ok=True)  # Ensure the output folder exists
    file_path = os.path.join("thread_results", csv_filename)
    
    with open(file_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["code", "like_count", "comment_count", "username", "user_verified", "repost_count", "reshare_count", "text", "timestamp", "post_url"])

        for post in posts:
            readable_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([
                post.get('code', ''), post.get('like_count', 0), post.get('comment_count', 0),
                post.get('username', ''), post.get('user_verified', ''), post.get('repost_count', 0), post.get('reshare_count', 0),
                post.get('text', ''), readable_date, post.get('url', '')
            ])
            print(f"Saved post: {post['code']}")

def filter_posts_by_keywords(posts, keywords):
    """Filters posts to include only those containing specified keywords."""
    return [post for post in posts if any(keyword.lower() in post.get('text', '').lower() for keyword in keywords)]

# Main execution
with sync_playwright() as pw:
    chromium_path = "/Users/riyaaggarwal/Library/Caches/ms-playwright/chromium-1112/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
    browser = pw.chromium.launch(executable_path=chromium_path, headless=False)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    try:
        # Load credentials and test cases from threads_config.json
        with open("threads_config.json", 'r') as config_file:
            config = json.load(config_file)
        username = config["credentials"]["username"]
        password = config["credentials"]["password"]
        test_cases = config["test_cases"]

        login_to_threads(page, username, password)
        time.sleep(3)

        # Iterate through each test case
        for test_name, test_info in test_cases.items():
            urls = test_info["urls"]
            keywords = test_info.get("keywords", [])
            csv_filename = test_info["csv_filename"]

            for url in urls:
                print(f"Processing URL for {test_name}: {url}")
                page.goto(url)
                delay = random.randint(0, 10)
                print(f"Sleeping for {delay} seconds before processing the page...")
                time.sleep(delay)
                
                existing_post_codes = read_existing_codes(os.path.join("thread_results", csv_filename))
                new_posts = fetch_posts(page, existing_post_codes)
                
                # Filter posts by keywords if keywords are provided
                relevant_posts = filter_posts_by_keywords(new_posts, keywords) if keywords else new_posts
                
                if relevant_posts:
                    save_posts_to_csv(relevant_posts, csv_filename)
                else:
                    print(f"No relevant posts found for {test_name} at {url}.")

    finally:
        browser.close()
