import re
import feedparser
from bs4 import BeautifulSoup

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
            if feed.entries:
                entry = feed.entries[0]
                new_posts.append(format_tweet_entry(entry, source_key))
                last_ids[source_key] = entry.link
        else:
            for entry in feed.entries:
                if entry.link == last_id:
                    break
                new_posts.append(format_tweet_entry(entry, source_key))
            if feed.entries:
                last_ids[source_key] = feed.entries[0].link

    return new_posts, last_ids

def format_tweet_entry(entry, source_key):
    soup = BeautifulSoup(entry.summary, "html.parser")

    # Сохраняем переносы строк: заменяем <br> и <p> на \n
    for tag in soup.find_all(["br", "p", "div"]):
        tag.insert_after("\n")
    text = soup.get_text()
    # Чистим двойные переносы и убираем пустые строки без потери структуры
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)

    # Картинка
    image_url = None
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        image_url = img_tag["src"]
        if image_url.startswith("//"):
            image_url = "https:" + image_url
        if not image_url.startswith("http"):
            image_url = None

    # Ссылку на сам твит нормализуем позже в formatter.py, здесь оставляем как есть
    return {
        "text": text,
        "link": entry.link,   # будет исправлен на x.com в build_message
        "image": image_url,
        "source": source_key
    }
