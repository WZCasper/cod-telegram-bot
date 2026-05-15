import feedparser
import requests
from bs4 import BeautifulSoup

BLOG_RSS = "https://www.callofduty.com/blog/feed"

def fetch_new_blog_posts(state):
    last_ids = state.get("last_ids", {})
    last_id = last_ids.get("blog")
    new_posts = []

    try:
        # Парсим RSS с тайм-аутом
        feed = feedparser.parse(BLOG_RSS, request_headers={"User-Agent": "Mozilla/5.0"})
        # Дополнительная проверка: если статус не 200, feed.entries может быть пустым
        if hasattr(feed, 'status') and feed.status != 200:
            print(f"Ошибка загрузки RSS блога: статус {feed.status}")
            return [], last_ids

        if not feed.entries:
            print("RSS блога вернул 0 записей.")
            return [], last_ids

    except Exception as e:
        print(f"Ошибка при запросе RSS блога: {e}")
        return [], last_ids

    # Если last_id не задан, берём только последнюю запись
    if not last_id:
        entry = feed.entries[0]
        try:
            post = format_rss_entry(entry)
            if post:
                new_posts.append(post)
                last_ids["blog"] = entry.id
        except Exception as e:
            print(f"Ошибка форматирования записи блога: {e}")
        return new_posts, last_ids

    # Собираем новые записи до тех пор, пока не встретим last_id
    for entry in feed.entries:
        if entry.id == last_id:
            break
        try:
            post = format_rss_entry(entry)
            if post:
                new_posts.append(post)
        except Exception as e:
            print(f"Ошибка форматирования записи блога: {e}")

    # Обновляем last_id самой свежей записью
    if feed.entries:
        last_ids["blog"] = feed.entries[0].id

    return new_posts, last_ids

def format_rss_entry(entry):
    title = entry.title.strip() if hasattr(entry, 'title') else "Без названия"
    link = entry.link if hasattr(entry, 'link') else ""

    # Пытаемся найти изображение в содержимом (summary)
    image = None
    if hasattr(entry, 'summary'):
        soup = BeautifulSoup(entry.summary, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            image = img_tag["src"]
            if image.startswith("//"):
                image = "https:" + image
            if not image.startswith("http"):
                image = None

    # Если не нашли изображение, пробуем по атрибуту media_content (есть в некоторых RSS)
    if not image and hasattr(entry, 'media_content'):
        for media in entry.media_content:
            if 'image' in media.get('type', ''):
                image = media.get('url')
                break

    # Если всё равно нет, можно взять og:image со страницы, но это медленно – пока пропускаем
    return {
        "text": title,
        "link": link,
        "image": image,
        "source": "blog"
    }
