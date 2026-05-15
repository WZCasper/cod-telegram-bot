import asyncio
import random
import logging
from telegram import Bot
from telegram.error import TelegramError, RetryAfter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def publish_post(bot_token, chat_id, post, translate, state):
    from utils.formatter import build_message
    text = build_message(post, translate=translate)
    bot = Bot(token=bot_token)
    image_url = post.get("image")

    logging.info(f"Пост из {post.get('source')}: image={image_url}, text={text[:50]}...")

    # Проверяем, что URL картинки валидный (начинается с http)
    valid_image = image_url and isinstance(image_url, str) and image_url.startswith("http")
    
    # Если есть валидная картинка, пытаемся отправить её до 5 раз
    if valid_image:
        for attempt in range(5):
            try:
                logging.info(f"Попытка {attempt+1}/5 отправить фото: {image_url}")
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=image_url,
                    caption=text,
                    parse_mode="HTML"
                )
                logging.info(f"Фото успешно отправлено!")
                return True
            except RetryAfter as e:
                wait = e.retry_after + random.uniform(1, 5)
                logging.warning(f"Flood control. Жду {wait:.1f} сек.")
                await asyncio.sleep(wait)
            except TelegramError as e:
                error_str = str(e)
                logging.error(f"Ошибка отправки фото: {error_str}")
                if "url host is empty" in error_str.lower() or "invalid file" in error_str.lower():
                    # Картинка битая, не будем пытаться отправить текст
                    logging.warning("Битая ссылка на изображение, отменяем пост.")
                    return False
                elif "flood" in error_str.lower():
                    await asyncio.sleep(15 + random.uniform(1, 5))
                else:
                    break
            except Exception as e:
                logging.error(f"Неизвестная ошибка при отправке фото: {e}")
                break
    
    # Если картинки нет, отправляем только текст
    logging.info("Отправка текстового сообщения (изображение отсутствует)")
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            disable_web_page_preview=True,
            parse_mode="HTML"
        )
        return True
    except TelegramError as e:
        logging.error(f"Не удалось отправить даже текст: {e}")
        return False
