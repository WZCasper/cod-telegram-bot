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

def clean_nitter_links(text):
    """Заменяет все ссылки nitter.net в тексте на оригинальные x.com"""
    # заменяем https://nitter.net/любой_путь на https://x.com/тот_же_путь
    text = re.sub(r'https?://nitter\.net/', 'https://x.com/', text)
    # убираем #m в конце ссылок
    text = re.sub(r'#m\b', '', text)
    return text

def format_tweet_entry(entry, source_key):
    soup = BeautifulSoup(entry.summary, "html.parser")
    # Заменяем <br> и <p> на переносы строк, чтобы сохранить форматирование
    for tag in soup.find_all(["br", "p"]):
        tag.replace_with("\n")
    # Получаем текст, теперь с сохранением переносов
    text = soup.get_text()
    # Убираем лишние пробелы и пустые строки, но сохраняем абзацы
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)

    # Заменяем nitter-ссылки внутри текста на x.com
    text = clean_nitter_links(text)

    # Извлекаем картинку, если есть
    image_url = None
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        image_url = img_tag["src"]
        if image_url.startswith("//"):
            image_url = "https:" + image_url
        # Проверяем, что это настоящая картинка, а не аватар/пиксель
        if not image_url.startswith("http"):
            image_url = None

    # Нормализуем ссылку на сам твит (для ОРИГИНАЛ)
    link = entry.link
    link = re.sub(r'https?://nitter\.net/', 'https://x.com/', link)
    link = re.sub(r'#m$', '', link)

    return {
        "text": text,
        "link": link,
        "image": image_url,
        "source": source_key
    }
