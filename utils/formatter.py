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

def build_message(post, translate=False):
    original_text = post["text"]
    if translate:
        # Используем безопасный перевод
        ru_text = translate_text_safe(original_text)
    else:
        ru_text = original_text

    text_with_emoji = add_category_emoji(ru_text)
    # Никаких ссылок не добавляем
    return text_with_emoji
