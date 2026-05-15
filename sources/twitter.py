import feedparser
import random
from datetime import datetime, timezone

NITTER_MIRRORS = [
    "https://nitter.net",
    "https://nitter.1d4.us",
    "https://nitter.poast.org",
]

ACCOUNTS = {
    "twitter_main": "CallofDuty",
    "twitter_cm": "CallofDutyCM",
    "twitter_updates": "CODUpdates"
}

def fetch_new_tweets(state):
    new_posts = []
    last_ids = state.get("last_ids", {})
    for source_key, username in ACCOUNTS.items():
        # Пробуем разные зеркала
        url = None
        for mirror in NITTER_MIRRORS:
            try:
                rss_url = f"{mirror}/{username}/rss"
                feed = feedparser.parse(rss_url)
                if feed.entries:
                    url = rss_url
                    break
            except:
                continue
        if not url:
            print(f"Не удалось получить RSS для {username}")
            continue

        last_id = last_ids.get(source_key)
        if not last_id:
            # если запускаем впервые, берём только последний твит
            if feed.entries:
                entry = feed.entries[0]
                new_posts.append(format_tweet_entry(entry, source_key))
                last_ids[source_key] = entry.link
        else:
            # собираем все новые, пока не встретим last_id
            for entry in feed.entries:
                if entry.link == last_id:
                    break
                new_posts.append(format_tweet_entry(entry, source_key))
            if feed.entries:
                last_ids[source_key] = feed.entries[0].link

    return new_posts, last_ids

def format_tweet_entry(entry, source_key):
    # Очищаем описание от HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(entry.summary, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    # Забираем первую картинку, если есть
    image_url = None
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        image_url = img_tag["src"]
        if image_url.startswith("//"):
            image_url = "https:" + image_url
    return {
        "text": text,
        "link": entry.link,
        "image": image_url,
        "source": source_key
    }