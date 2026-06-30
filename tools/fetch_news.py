"""
fetch_news.py — Fetch recent sports news via Tavily API
Usage: python tools/fetch_news.py "Premier League"
Output: .tmp/news.json
"""

import sys
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    print("ERROR: TAVILY_API_KEY not set in .env")
    sys.exit(1)

TRUSTED_DOMAINS = [
    "bbc.com", "bbc.co.uk",
    "espn.com", "skysports.com",
    "theguardian.com", "theathletic.com",
    "goal.com", "football365.com",
    "bleacherreport.com", "cbssports.com",
    "nytimes.com", "reuters.com",
    "marca.com", "sportyou.es",
]

def fetch_news(competition: str, days_back: int = 2) -> dict:
    query = f"{competition} latest news results highlights {datetime.now().strftime('%B %Y')}"

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "max_results": 10,
        "include_domains": TRUSTED_DOMAINS,
        "topic": "news",
    }

    print(f"Searching Tavily for: {query}")
    resp = requests.post("https://api.tavily.com/search", json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    cutoff = datetime.now() - timedelta(days=days_back)
    articles = []

    for result in data.get("results", []):
        # Filter out articles older than cutoff if published_date is available
        pub_date = result.get("published_date")
        if pub_date:
            try:
                parsed = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                if parsed.replace(tzinfo=None) < cutoff:
                    continue
            except Exception:
                pass  # Keep article if date parsing fails

        articles.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
            "source": result.get("url", "").split("/")[2].replace("www.", ""),
            "published_date": pub_date,
            "score": result.get("score", 0),
        })

    # Deduplicate by URL
    seen = set()
    unique_articles = []
    for a in articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique_articles.append(a)

    output = {
        "competition": competition,
        "fetched_at": datetime.now().isoformat(),
        "article_count": len(unique_articles),
        "articles": unique_articles,
    }

    os.makedirs(".tmp", exist_ok=True)
    out_path = ".tmp/news.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(unique_articles)} articles to {out_path}")
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/fetch_news.py 'Premier League'")
        sys.exit(1)
    competition = " ".join(sys.argv[1:])
    fetch_news(competition)
