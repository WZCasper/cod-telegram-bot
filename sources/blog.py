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

    # Ищем все ссылки, которые могут вести на статьи блога
    articles = soup.select("a[href*='/blog/']")

    last_ids = state.get("last_ids", {})
    last_url = last_ids.get("blog")
    new_posts = []
    found_last = False

    for article in articles:
        url = article.get("href")
        if not url:
            continue
        if not url.startswith("http"):
            url = "https://www.callofduty.com" + url

        # Пропускаем, если это не статья, а служебная ссылка
        if "/blog/" not in url:
            continue

        # Если достигли последнего обработанного URL, дальше не идём
        if url == last_url:
            found_last = True
            break

        # Пытаемся найти заголовок
        title = None
        # Ищем любой заголовочный тег внутри родительского элемента статьи
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            title_tag = article.find_parent().find(tag) if article.find_parent() else None
            if title_tag:
                title = title_tag.get_text(strip=True)
                break
        # Если не нашли, ищем в самой ссылке атрибут title
        if not title:
            title = article.get("title", "").strip()
        # Если и там пусто, берём текст ссылки, но только если он не слишком длинный
        if not title:
            raw_text = article.get_text(separator=" ", strip=True)
            if len(raw_text) < 150 and raw_text:
                title = raw_text

        # Если заголовок так и не найден — пропускаем эту статью
        if not title or title.lower() == "новость":
            continue

        # Ищем картинку
        image = None
        img_tag = article.find_parent().find("img") if article.find_parent() else None
        if not img_tag:
            img_tag = article.find("img")
        if img_tag and img_tag.get("src"):
            image = img_tag["src"]
            if image.startswith("//"):
                image = "https:" + image
            if not image.startswith("http"):
                image = None

        new_posts.append({
            "text": title,
            "link": url,
            "image": image,
            "source": "blog"
        })

    # Обновляем last_id только если нашли новые посты
    if new_posts:
        last_ids["blog"] = new_posts[0]["link"]
    elif found_last and not new_posts:
        # если мы дошли до last_url, но новых нет, оставляем last_id как есть
        pass

    return new_posts, last_ids
