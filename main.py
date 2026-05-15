import os
import sys
import asyncio
import random
import logging

from state_manager import load_state, save_state
from sources.twitter import fetch_new_tweets
from sources.youtube import fetch_new_videos
from sources.blog import fetch_new_blog_posts
from publisher import publish_post

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("BOT_TOKEN или CHAT_ID не заданы. Проверьте Secrets в репозитории.")
    sys.exit(1)

async def main():
    logger.info("=== Бот запущен ===")
    state = load_state()
    logger.info(f"Текущее состояние: paused={state.get('paused')}, last_ids={state.get('last_ids')}")

    if state.get("paused"):
        logger.info("Бот на паузе. Завершаю работу.")
        return

    # Загрузка новостей
    new_posts = []
    new_ids = state.get("last_ids", {}).copy()

    # Twitter
    try:
        logger.info("Загружаю Twitter...")
        tweets, updated_ids = fetch_new_tweets(state)
        new_posts.extend(tweets)
        new_ids.update(updated_ids)
        logger.info(f"Twitter: получено {len(tweets)} новых постов")
    except Exception as e:
        logger.error(f"Ошибка Twitter: {e}")

    # YouTube
    try:
        logger.info("Загружаю YouTube...")
        videos, updated_ids = fetch_new_videos(state)
        new_posts.extend(videos)
        new_ids.update(updated_ids)
        logger.info(f"YouTube: получено {len(videos)} новых постов")
    except Exception as e:
        logger.error(f"Ошибка YouTube: {e}")

    # Блог
    try:
        logger.info("Загружаю блог...")
        blogs, updated_ids = fetch_new_blog_posts(state)
        new_posts.extend(blogs)
        new_ids.update(updated_ids)
        logger.info(f"Блог: получено {len(blogs)} новых постов")
    except Exception as e:
        logger.error(f"Ошибка блога: {e}")

    # Фильтрация пустых заголовков
    filtered = []
    for post in new_posts:
        text = post.get("text", "").strip()
        if text and text.lower() not in ["новость", ""]:
            filtered.append(post)
        else:
            logger.warning(f"Пропущен пост с пустым или шаблонным заголовком: {post.get('link')}")

    if not filtered:
        logger.info("Нет постов для публикации после фильтрации.")
    else:
        translate = state.get("translate", True)
        delay = 30  # секунд между постами
        for idx, post in enumerate(filtered):
            logger.info(f"Публикую пост {idx+1}/{len(filtered)}: {post.get('text', '')[:60]}...")
            success = await publish_post(BOT_TOKEN, CHAT_ID, post, translate, state)
            if success:
                logger.info("Успешно.")
            else:
                logger.warning("Не удалось опубликовать.")
            if idx < len(filtered) - 1:
                wait = delay + random.uniform(0, 5)
                logger.info(f"Жду {wait:.1f} сек.")
                await asyncio.sleep(wait)

    # Обновляем last_ids в любом случае
    state["last_ids"] = new_ids
    save_state(state)
    logger.info("=== Бот завершил работу ===")

if __name__ == "__main__":
    asyncio.run(main())
