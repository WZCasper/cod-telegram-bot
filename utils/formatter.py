import re
from utils.translator import translate_text_safe

CATEGORIES = {
    "double_xp": "🔥",
    "update": "⚙️",
    "patch": "⚙️",
    "trailer": "🎬",
    "stream": "📡",
    "event": "🎉",
    "warzone": "🪂",
    "modern warfare": "💣",
    "black ops": "🕵️",
}

def add_category_emoji(text):
    lower = text.lower()
    for keyword, emoji in CATEGORIES.items():
        if re.search(rf'\b{keyword}\b', lower):
            return f"{emoji} {text}"
    return f"📰 {text}"

def normalize_link(url):
    """Преобразует ссылки nitter.net в исходные x.com, остальные оставляет как есть."""
    if not url:
        return url
    # Заменяем домен nitter.net на x.com
    normalized = re.sub(r'https?://nitter\.net/', 'https://x.com/', url)
    # Убираем якорь #m, если он есть (обычно добавляется Nitter)
    normalized = re.sub(r'#m$', '', normalized)
    return normalized

def build_message(post, translate=False):
    original_text = post["text"]
    if translate:
        ru_text = translate_text_safe(original_text)
    else:
        ru_text = original_text

    text_with_emoji = add_category_emoji(ru_text)

    # Добавляем ссылку на оригинал, предварительно нормализовав её
    link = post.get("link")
    if link:
        clean_link = normalize_link(link)
        text_with_emoji += f'\n\n<a href="{clean_link}">ОРИГИНАЛ</a>'

    return text_with_emoji
