from deep_translator import GoogleTranslator

def translate_to_russian(text):
    try:
        if len(text) > 5000:
            text = text[:5000]  # ограничение Google Translate
        translated = GoogleTranslator(source='auto', target='ru').translate(text)
        return translated
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text  # возвращаем оригинал