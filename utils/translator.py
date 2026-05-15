import re
from deep_translator import GoogleTranslator

# Игровые названия, которые не нужно переводить (можно дополнить)
PROTECTED_TERMS = [
    "Call of Duty", "Warzone", "Modern Warfare", "Black Ops",
    "Vanguard", "Cold War", "Infinite Warfare", "Advanced Warfare",
    "WWII", "Mobile", "Blackout", "Zombies", "DMZ", "Spec Ops",
    "Season", "Battle Pass", "Operator", "Multiplayer", "Campaign",
    "CallofDuty", "CODM", "COD"
]

# Создаём словарь для замены: {плейсхолдер: оригинал}
PLACEHOLDERS = {}
for i, term in enumerate(PROTECTED_TERMS):
    placeholder = f"__TERM{i}__"
    PLACEHOLDERS[placeholder] = term

def translate_text_safe(text: str) -> str:
    """Переводит текст на русский, не трогая указанные игровые термины."""
    # Заменяем защищённые слова на плейсхолдеры
    for placeholder, term in PLACEHOLDERS.items():
        # Используем регистронезависимую замену
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        text = pattern.sub(placeholder, text)

    try:
        if len(text) > 5000:
            text = text[:5000]
        translated = GoogleTranslator(source='auto', target='ru').translate(text)
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        translated = text  # если ошибка, возвращаем оригинал

    # Возвращаем обратно оригинальные названия
    for placeholder, term in PLACEHOLDERS.items():
        translated = translated.replace(placeholder, term)
        # Также заменяем возможные искажения пробелов
        translated = translated.replace(placeholder.lower(), term)

    return translated
