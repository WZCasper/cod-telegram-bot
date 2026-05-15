import asyncio
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

    # Проверяем, что URL картинки валидный
    send_photo = False
    if image_url and isinstance(image_url, str) and image_url.startswith("http"):
        send_photo = True
    else:
        if image_url:
            logging.warning(f"Пропущена невалидная ссылка на изображение: {image_url}")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            if send_photo:
                logging.info(f"Отправка фото: {image_url}")
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=image_url,
                    caption=text,
                    parse_mode="HTML"
                )
            else:
                logging.info("Отправка текста (изображение отсутствует или невалидно)")
                await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    disable_web_page_preview=True,
                    parse_mode="HTML"
                )
            return True
        except RetryAfter as e:
            wait = e.retry_after + 1
            logging.warning(f"Flood control: жду {wait} сек.")
            await asyncio.sleep(wait)
        except TelegramError as e:
            error_str = str(e)
            logging.error(f"Ошибка отправки: {error_str}")
            if "url host is empty" in error_str.lower() or "invalid file" in error_str.lower():
                send_photo = False
                await asyncio.sleep(0.5)
            elif "flood" in error_str.lower():
                await asyncio.sleep(15)
            else:
                break
        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            break

    if send_photo:
        logging.info("Повторная попытка отправки без фото")
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )
            return True
        except Exception as e:
            logging.error(f"Не удалось отправить даже текст: {e}")
    return False
