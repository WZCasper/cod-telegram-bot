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
    if not url:
        return url
    normalized = re.sub(r'https?://nitter\.net/', 'https://x.com/', url)
    normalized = re.sub(r'#m$', '', normalized)
    return normalized

def build_message(post, translate=False):
    original_text = post["text"]
    if translate:
        ru_text = translate_text_safe(original_text)
    else:
        ru_text = original_text

    text_with_emoji = add_category_emoji(ru_text)

    link = post.get("link")
    if link:
        clean_link = normalize_link(link)
        text_with_emoji += f'\n\n<a href="{clean_link}">ОРИГИНАЛ</a>'

    return text_with_emoji
