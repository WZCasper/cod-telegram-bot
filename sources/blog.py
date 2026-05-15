import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

BLOG_URL = "https://www.callofduty.com/blog"

def fetch_new_blog_posts(state):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(BLOG_URL, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Ошибка загрузки блога: {e}")
        return [], state.get("last_ids", {})

    soup = BeautifulSoup(resp.text, "html.parser")
    # Селектор для статей (надо проверять в браузере, сейчас предположим .blog-card)
    articles = soup.select("a.blog-card")
    if not articles:
        # запасной вариант – ищем любые ссылки на статьи
        articles = soup.select("a[href*='/blog/']")

    last_ids = state.get("last_ids", {})
    last_url = last_ids.get("blog")
    new_posts = []

    for article in articles:
        url = article.get("href")
        if not url:
            continue
        if not url.startswith("http"):
            url = "https://www.callofduty.com" + url
        if url == last_url:
            break
        # ищем заголовок
        title_tag = article.select_one("h3, .title, .blog-title")
        title = title_tag.get_text(strip=True) if title_tag else "Новость"
        # ищем картинку
        img_tag = article.select_one("img")
        image = img_tag["src"] if img_tag else None
        if image and image.startswith("//"):
            image = "https:" + image
        new_posts.append({
            "text": title,
            "link": url,
            "image": image,
            "source": "blog"
        })

    if new_posts:
        last_ids["blog"] = new_posts[0]["link"]
    return new_posts, last_ids