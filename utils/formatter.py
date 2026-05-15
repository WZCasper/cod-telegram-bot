import re

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
    if translate:
        # Переводим только текст, ссылку не трогаем
        from utils.translator import translate_to_russian
        ru_text = translate_to_russian(post["text"])
    else:
        ru_text = post["text"]

    text_with_emoji = add_category_emoji(ru_text)
    message = f"{text_with_emoji}\n\n🔗 {post['link']}"
    return message