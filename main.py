import os
import asyncio
import sys
import random
import logging
from datetime import datetime, timedelta

from state_manager import load_state, save_state
from sources.twitter import fetch_new_tweets
from sources.youtube import fetch_new_videos
from sources.blog import fetch_new_blog_posts
from publisher import publish_post
from commands import process_commands

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logging.error("Установите переменные окружения BOT_TOKEN и CHAT_ID")
    sys.exit(1)

async def main():
    state = load_state()

    # Обрабатываем команды администратора
    # await process_commands(BOT_TOKEN, state)

    if state.get("paused"):
        logging.info("Бот на паузе, выход.")
        return

    # Загружаем новости из всех источников
    new_posts = []
    new_ids = state.get("last_ids", {}).copy()

    # Twitter
    try:
        tweets, updated_ids = fetch_new_tweets(state)
        new_posts.extend(tweets)
        new_ids.update(updated_ids)
    except Exception as e:
        logging.error(f"Ошибка Twitter: {e}")

    # YouTube
    try:
        videos, updated_ids = fetch_new_videos(state)
        new_posts.extend(videos)
        new_ids.update(updated_ids)
    except Exception as e:
        logging.error(f"Ошибка YouTube: {e}")

    # Блог (временно можно отключить, закомментировав следующие строки)
    try:
        blogs, updated_ids = fetch_new_blog_posts(state)
        new_posts.extend(blogs)
        new_ids.update(updated_ids)
    except Exception as e:
        logging.error(f"Ошибка блога: {e}")

    # Фильтрация: убираем посты с пустым текстом или заголовком-заглушкой
    filtered_posts = []
    for post in new_posts:
        text = post.get("text", "").strip()
        if text and text.lower() not in ["новость", ""]:
            filtered_posts.append(post)
        else:
            logging.warning(f"Пропущен пост с пустым или шаблонным заголовком: {post.get('link')}")

    if not filtered_posts:
        logging.info("После фильтрации не осталось постов для публикации.")
        state["last_ids"] = new_ids
        save_state(state)
        return

    # Публикация отфильтрованных постов с большой задержкой
    translate = state.get("translate", True)
    post_delay = 30  # секунд между постами
    for idx, post in enumerate(filtered_posts):
        success = await publish_post(BOT_TOKEN, CHAT_ID, post, translate, state)
        if not success:
            logging.warning(f"Пост не был отправлен, пропускаю: {post.get('text', '')[:50]}...")

        if idx < len(filtered_posts) - 1:
            delay = post_delay + random.uniform(0, 5)
            logging.info(f"Жду {delay:.1f} сек. перед следующим постом")
            await asyncio.sleep(delay)

    # Обновляем состояние
    state["last_ids"] = new_ids
    save_state(state)

    # Краткий отчёт
    try:
        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=f"📊 Опубликовано новых постов: {len(filtered_posts)}")
    except Exception:
        pass

if __name__ == "__main__":
    asyncio.run(main())
