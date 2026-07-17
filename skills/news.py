import feedparser

FEEDS = {
    "tecnologia": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "mundo": "https://feeds.bbci.co.uk/news/rss.xml",
    "tech": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "default": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "ciencia": "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
    "deportes": "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml"
}

import ssl
if hasattr(ssl, '_create_default_https_context') and 'SSL' in ssl.__dict__:
  ssl._create_default_https_context = ssl._create_unverified_context

def handle_news(text: str) -> str:
    topic = "default"
    for key in FEEDS:
        if key.lower() in text.lower():
            topic = key
            break
    try:
        feed = feedparser.parse(FEEDS[topic])
        entries = feed.entries[:7]
        if not entries:
            return "No news found."
        result = f"Latest {topic.capitalize()} News:\n\n"
        for i, entry in enumerate(entries):
            title = entry.title
            published = getattr(entry, "published", "")
            result += f"{i + 1}. {title}\n   {published}\n\n"
        return result.strip()
    except Exception as e:
        return f"Error fetching news: {e}"
