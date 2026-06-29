import re
import pandas as pd
import feedparser
import sqlite3
from datetime import datetime, timezone, timedelta
from dateutil import parser as dateparser

# ================= CONFIG =================
RSS_FEEDS = [
    "https://techcrunch.com/tag/healthcare/feed/",
    "https://www.fiercebiotech.com/rss/xml",
    "https://www.mobihealthnews.com/rss.xml"
]

KEYWORDS = ["health", "biotech", "medtech", "hospital", "pharma"]
FUNDING_WORDS = ["raise", "funding", "investment", "series", "seed"]

DAYS_BACK = 7
DB_FILE = "funding.db"

# ================= HELPERS =================

def clean_text(text):
    return re.sub(r"<.*?>", "", text or "").strip()

def contains_keyword(text, keywords):
    return any(k.lower() in text.lower() for k in keywords)

def safe_parse_date(entry):
    try:
        return dateparser.parse(entry.published)
    except:
        return None

def extract_amount(text):
    match = re.search(r"\$[\d,.]+ ?(million|billion)?", text, re.IGNORECASE)
    return match.group(0) if match else None

def extract_company(title):
    # Simple assumption: company name is first word(s) before "raises"
    match = re.search(r"^([A-Z][a-zA-Z0-9& ]+?) (raises|secures|gets)", title)
    return match.group(1) if match else title.split(" ")[0]

def extract_stage(text):
    match = re.search(r"(Series [A-F]|Seed|Pre-Seed)", text, re.IGNORECASE)
    return match.group(0) if match else None

def generate_summary(title, summary):
    text = clean_text(summary)
    return (text[:150] + "...") if len(text) > 150 else title[:120]

def freshness_score(published):
    hours_old = (datetime.now(timezone.utc) - published).total_seconds() / 3600
    return round(max(0, 100 - hours_old), 2)

# ================= MAIN =================

def fetch_funding_data():
    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
    results = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            published = safe_parse_date(entry)
            if not published or published < cutoff:
                continue

            title = entry.title
            summary = entry.get("summary", "")
            cleaned_summary = clean_text(summary)

            text = (title + " " + cleaned_summary).lower()

            if contains_keyword(text, KEYWORDS) and contains_keyword(text, FUNDING_WORDS):
                amount = extract_amount(text)
                company = extract_company(title)
                stage = extract_stage(text)
                score = freshness_score(published)

                results.append({
                    "company": company,
                    "title": title,
                    "amount": amount,
                    "stage": stage,
                    "summary": generate_summary(title, cleaned_summary),
                    "link": entry.link,
                    "published": published.isoformat(),
                    "score": score,
                    "source": url
                })

    return pd.DataFrame(results)

def save_to_database(df):
    if df.empty:
        print("No new data found.")
        return

    conn = sqlite3.connect(DB_FILE)

    # Remove duplicates based on link
    try:
        existing = pd.read_sql("SELECT link FROM funding", conn)
        df = df[~df["link"].isin(existing["link"])]
    except:
        pass

    df.to_sql("funding", conn, if_exists="append", index=False)
    conn.close()

    print(f"Saved {len(df)} new records to database.")

# ================= RUN =================

if __name__ == "__main__":
    df = fetch_funding_data()
    df = df.sort_values(by=["score", "published"], ascending=False)
    save_to_database(df)
