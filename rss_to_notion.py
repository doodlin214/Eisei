import os
import requests
import feedparser
from datetime import datetime
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Headers for Notion API
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Notion API endpoint
NOTION_API_URL = "https://api.notion.com/v1/pages"

def fetch_rss(url):
    """Fetch RSS feed and return parsed entries."""
    feed = feedparser.parse(url)
    return feed.entries

def create_page_in_notion(title, url, published_date):
    """Create a new page in Notion database."""
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {
                "title": [{"text": {"content": title}}]
            },
            "URL": {
                "url": url
            },
            "Published": {
                "date": {"start": published_date}
            }
        }
    }

    response = requests.post(NOTION_API_URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        print(f"✅ Added: {title}")
    else:
        print(f"❌ Failed: {title} — {response.text}")

def main():
    rss_url = "https://www.sumitomo-chem.co.jp/news/rss.xml"
    entries = fetch_rss(rss_url)

    for entry in entries:
        title = entry.title
        link = entry.link
        published = entry.get("published", datetime.now().isoformat())
        published_date = datetime(*entry.published_parsed[:6]).isoformat()

        create_page_in_notion(title, link, published_date)

if __name__ == "__main__":
    main()
