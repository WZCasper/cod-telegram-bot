import asyncio
import logging
import requests
from io import BytesIO
from telegram import Bot, InputFile
from telegram.error import TelegramError, RetryAfter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def publish_post(bot_token, chat_id, post, translate, state):
    from utils.formatter import build_message
    text = build_message(post, translate=translate)
    bot = Bot(token=bot_token)
    image_url = post.get("image")

    logging.info(f"Пост из {post.get('source')}: image={image_url}, text={text[:60]}...")

    valid_image = image_url and isinstance(image_url, str) and image_url.startswith("http")

    if valid_image:
        for attempt in range(5):
            try:
                logging.info(f"Скачиваю изображение: {image_url}")
                response = requests.get(image_url, timeout=15)
                response.raise_for_status()
                photo_file = InputFile(BytesIO(response.content), filename="image.jpg")
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=text,
                    parse_mode="HTML"
                )
                logging.info("Фото успешно отправлено!")
                return True
            except RetryAfter as e:
                wait = e.retry_after + 2
                logging.warning(f"Flood control, жду {wait} сек.")
                await asyncio.sleep(wait)
            except requests.exceptions.RequestException as e:
                logging.error(f"Ошибка загрузки изображения: {e}")
                break
            except TelegramError as e:
                error_str = str(e)
                logging.error(f"Ошибка Telegram: {error_str}")
                if "url host is empty" in error_str.lower() or "invalid file" in error_str.lower():
                    break
                elif "flood" in error_str.lower():
                    await asyncio.sleep(15)
                else:
                    break
            except Exception as e:
                logging.error(f"Неизвестная ошибка: {e}")
                break
        # fallback to text
        logging.info("Пытаюсь отправить только текст без фото")
        try:
            await bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True, parse_mode="HTML")
            return True
        except Exception as e:
            logging.error(f"Не удалось отправить текст: {e}")
            return False
    else:
        try:
            await bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True, parse_mode="HTML")
            return True
        except TelegramError as e:
            logging.error(f"Ошибка отправки текста: {e}")
            return False
