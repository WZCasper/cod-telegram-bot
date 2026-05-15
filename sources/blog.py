import feedparser
import re

BLOG_RSS = "https://www.callofduty.com/blog/feed"

def fetch_new_blog_posts(state):
    feed = feedparser.parse(BLOG_RSS)
    last_ids = state.get("last_ids", {})
    last_id = last_ids.get("blog")
    new_posts = []

    if not feed.entries:
        print("RSS блога недоступен или пуст.")
        return [], last_ids

    # Если last_id не задан – берём только последнюю статью
    if not last_id:
        entry = feed.entries[0]
        new_posts.append(format_rss_entry(entry))
        last_ids["blog"] = entry.id
        return new_posts, last_ids

    # Собираем новые статьи, пока не встретим last_id
    for entry in feed.entries:
        if entry.id == last_id:
            break
        new_posts.append(format_rss_entry(entry))

    if feed.entries:
        last_ids["blog"] = feed.entries[0].id

    return new_posts, last_ids

def format_rss_entry(entry):
    # Берём заголовок
    title = entry.title.strip()
    # Ищем изображение из содержимого (обычно в description)
    image = None
    if hasattr(entry, "summary"):
        # Ищем первый тег img
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(entry.summary, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            image = img_tag["src"]
            if image.startswith("//"):
                image = "https:" + image
            if not image.startswith("http"):
                image = None
    return {
        "text": title,
        "link": entry.link,
        "image": image,
        "source": "blog"
    }
