import os
import asyncio
import sys
import random
import logging
from datetime import datetime, timedelta

from state_manager import load_state, save_state
from sources.twitter import fetch_new_tweets
from sources.youtube import fetch_new_videos
from publisher import publish_post

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logging.error("BOT_TOKEN или CHAT_ID не заданы. Проверьте Secrets в репозитории.")
    sys.exit(1)

async def main():
    state = load_state()
    logging.info(f"=== Бот запущен. Состояние: paused={state.get('paused')}, last_ids={state.get('last_ids')} ===")

    if state.get("paused"):
        logging.info("Бот на паузе, выход.")
        return

    new_posts = []
    new_ids = state.get("last_ids", {}).copy()

    # Twitter
    try:
        tweets, updated_ids = fetch_new_tweets(state)
        new_posts.extend(tweets)
        new_ids.update(updated_ids)
        logging.info(f"Twitter: получено {len(tweets)} новых постов")
    except Exception as e:
        logging.error(f"Ошибка Twitter: {e}")

    # YouTube
    try:
        videos, updated_ids = fetch_new_videos(state)
        new_posts.extend(videos)
        new_ids.update(updated_ids)
        logging.info(f"YouTube: получено {len(videos)} новых постов")
    except Exception as e:
        logging.error(f"Ошибка YouTube: {e}")

    # Фильтрация пустых заголовков
    filtered = []
    for post in new_posts:
        text = post.get("text", "").strip()
        if text and text.lower() not in ["новость", ""]:
            filtered.append(post)
        else:
            logging.warning(f"Пропущен пост с пустым или шаблонным заголовком: {post.get('link')}")

    if not filtered:
        logging.info("Нет постов для публикации после фильтрации.")
        state["last_ids"] = new_ids
        save_state(state)
        return

    translate = state.get("translate", True)
    delay = 30  # секунд между постами
    for idx, post in enumerate(filtered):
        logging.info(f"Публикую пост {idx+1}/{len(filtered)}: {post.get('text', '')[:60]}...")
        success = await publish_post(BOT_TOKEN, CHAT_ID, post, translate, state)
        if success:
            logging.info("Успешно опубликован.")
        else:
            logging.warning("Не удалось опубликовать.")

        if idx < len(filtered) - 1:
            wait = delay + random.uniform(0, 5)
            logging.info(f"Жду {wait:.1f} сек.")
            await asyncio.sleep(wait)

    state["last_ids"] = new_ids
    save_state(state)
    logging.info("=== Бот завершил работу ===")

if __name__ == "__main__":
    asyncio.run(main())
