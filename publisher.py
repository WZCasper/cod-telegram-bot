import asyncio
import random
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

    logging.info(f"Пост из {post.get('source')}: image={image_url}, text={text[:50]}...")

    # Проверяем, что URL картинки валидный (начинается с http)
    valid_image = image_url and isinstance(image_url, str) and image_url.startswith("http")
    
    # Если есть валидная картинка, пытаемся отправить её с повторами
    if valid_image:
        for attempt in range(5):
            try:
                # --- ГЛАВНОЕ ИЗМЕНЕНИЕ: Скачиваем картинку сами, а не отдаём URL ---
                logging.info(f"Попытка {attempt+1}/5 скачать изображение: {image_url}")
                response = requests.get(image_url, timeout=15)
                response.raise_for_status() # Проверим, что не 404 и не 500
                
                # Отправляем фото как файл из памяти
                photo_file = InputFile(BytesIO(response.content), filename="image.jpg")
                logging.info("Изображение скачано. Отправляю в Telegram...")
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=text,
                    parse_mode="HTML"
                )
                logging.info("Фото успешно отправлено!")
                return True

            except RetryAfter as e:
                wait = e.retry_after + random.uniform(5, 10)
                logging.warning(f"Flood control. Жду {wait:.1f} сек.")
                await asyncio.sleep(wait)
            except requests.exceptions.RequestException as e:
                logging.error(f"Не удалось скачать изображение: {e}")
                break # Нет смысла повторять, если URL не работает
            except TelegramError as e:
                error_str = str(e)
                logging.error(f"Ошибка Telegram: {error_str}")
                if "flood" in error_str.lower():
                    await asyncio.sleep(60 + random.uniform(1, 5)) # Увеличенная пауза при флуде
                else:
                    break # Другая ошибка, пробовать не будем
            except Exception as e:
                logging.error(f"Неизвестная ошибка при отправке фото: {e}")
                break
    
    # Если картинки нет, отправляем только текст
    elif not valid_image:
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
            logging.error(f"Не удалось отправить текст: {e}")
            return False
    else:
        logging.warning("Пост не был отправлен из-за проблем с изображением.")
        return False
