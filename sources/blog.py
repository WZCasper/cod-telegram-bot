import requests
from bs4 import BeautifulSoup

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
    # Ищем все ссылки на статьи блога (обычно это карточки или просто теги <a>)
    articles = soup.select("a.blog-card")
    if not articles:
        # запасной вариант — любые ссылки, ведущие на /blog/
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

        # Пытаемся найти заголовок несколькими способами
        title = None
        # 1. Поиск по тегам заголовков внутри карточки
        for selector in ["h3", ".title", ".blog-title", "h2", "h4"]:
            title_tag = article.select_one(selector)
            if title_tag:
                title = title_tag.get_text(strip=True)
                break
        # 2. Если не нашли, проверяем атрибут title у самой ссылки
        if not title:
            title = article.get("title", "").strip()
        # 3. Если всё ещё нет, берём текст ссылки, но убираем лишнее
        if not title:
            title = article.get_text(separator=" ", strip=True)
            if len(title) > 100:
                title = title[:100] + "..."

        # Если заголовок всё равно пустой или стандартный — пропускаем
        if not title or title.lower() == "новость":
            continue

        # Ищем картинку
        img_tag = article.select_one("img")
        image = img_tag["src"] if img_tag else None
        if image and image.startswith("//"):
            image = "https:" + image
        if image and not image.startswith("http"):
            image = None

        new_posts.append({
            "text": title,
            "link": url,
            "image": image,
            "source": "blog"
        })

    if new_posts:
        last_ids["blog"] = new_posts[0]["link"]
    return new_posts, last_ids
