import feedparser
import json
from datetime import datetime

FEEDS = [
    "https://techcrunch.com/tag/healthtech/feed/",
    "https://techcrunch.com/tag/biotech/feed/",
    "https://www.fiercebiotech.com/rss/xml",
    "https://www.mobihealthnews.com/rss"
]

KEYWORDS = ["funding", "raises", "series", "seed", "investment"]

def fetch_articles():
    results = []

    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.title.lower()

            if any(keyword in title for keyword in KEYWORDS):
                results.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", "")
                })

    return results


def save_data(data):
    output = {
        "last_updated": str(datetime.now()),
        "articles": data
    }

    with open("data/funding.json", "w") as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    articles = fetch_articles()
    save_data(articles)
