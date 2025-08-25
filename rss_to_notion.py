import os
import requests
import feedparser
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

NOTION_API_URL = "https://api.notion.com/v1/pages"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

# File to store last fetched timestamp
LAST_FETCH_FILE = "last_fetched.json"
FEEDS_FILE = "feeds.txt"

def load_last_fetched():
    if os.path.exists(LAST_FETCH_FILE):
        with open(LAST_FETCH_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_fetched(last_fetched):
    with open(LAST_FETCH_FILE, "w") as f:
        json.dump(last_fetched, f)

def create_notion_page(title, link, published):
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "URL": {"url": link},
            "Published": {"date": {"start": published}},
        },
    }
    response = requests.post(NOTION_API_URL, headers=HEADERS, json=data)
    if response.status_code != 200:
        print(f"❌ Failed to add page: {response.text}")
    else:
        print(f"✅ Added: {title}")

def fetch_and_push():
    # Read RSS feeds from file
    if not os.path.exists(FEEDS_FILE):
        print(f"⚠️ No feeds.txt found.")
        return

    with open(FEEDS_FILE, "r") as f:
        rss_feeds = [line.strip() for line in f.readlines() if line.strip()]

    last_fetched = load_last_fetched()

    for rss_url in rss_feeds:
        print(f"\n🔄 Fetching RSS: {rss_url}")
        feed = feedparser.parse(rss_url)

        last_time = last_fetched.get(rss_url, "1970-01-01T00:00:00")
        new_items = []

        for entry in feed.entries:
            published_time = datetime(*entry.published_parsed[:6]).isoformat()
            if published_time > last_time:
                new_items.append((entry.title, entry.link, published_time))

        # Sort new items by time ascending
        new_items.sort(key=lambda x: x[2])

        for title, link, published in new_items:
            create_notion_page(title, link, published)

        # Update last fetched timestamp
        if new_items:
            last_fetched[rss_url] = new_items[-1][2]

    save_last_fetched(last_fetched)

if __name__ == "__main__":
    fetch_and_push()
