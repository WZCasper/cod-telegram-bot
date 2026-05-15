import os
import asyncio
import sys
from datetime import datetime, timedelta

from state_manager import load_state, save_state
from sources.twitter import fetch_new_tweets
from sources.youtube import fetch_new_videos
from sources.blog import fetch_new_blog_posts
from publisher import publish_post
from commands import process_commands

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("Установите переменные окружения BOT_TOKEN и CHAT_ID")
    sys.exit(1)

async def main():
    state = load_state()

    # Обрабатываем команды администратора
    await process_commands(BOT_TOKEN, state)

    if state.get("paused"):
        print("Бот на паузе, выход.")
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
        print(f"Ошибка Twitter: {e}")

    # YouTube
    try:
        videos, updated_ids = fetch_new_videos(state)
        new_posts.extend(videos)
        new_ids.update(updated_ids)
    except Exception as e:
        print(f"Ошибка YouTube: {e}")

    # Блог
    try:
        blogs, updated_ids = fetch_new_blog_posts(state)
        new_posts.extend(blogs)
        new_ids.update(updated_ids)
    except Exception as e:
        print(f"Ошибка блога: {e}")

    if not new_posts:
        print("Нет новых постов.")
        # обновим last_ids на случай если RSS-читалки сбились, но не будем коммитить если не меняли
        state["last_ids"] = new_ids
        save_state(state)
        return

    # Антиспам: минимальный интервал (проверяем по времени последнего запуска - не идеально, но ок)
    # В простом варианте просто публикуем все, не чаще одного раза в минуту
    # Но так как Actions запускается раз в 15 мин, можно не проверять

    # Сортируем по времени? У нас нет точного времени публикации в исходных данных,
    # поэтому просто публикуем как есть.

    # Публикация постов
    translate = state.get("translate", True)
    for post in new_posts:
        success = await publish_post(BOT_TOKEN, CHAT_ID, post, translate, state)
        if success:
            # ждём немного между сообщениями, чтобы не упереться в лимиты Telegram
            await asyncio.sleep(1)

    # Обновляем состояние
    state["last_ids"] = new_ids
    # Отправляем краткий отчёт администратору (в канал) - опционально
    await publish_report(BOT_TOKEN, CHAT_ID, len(new_posts))

    save_state(state)

async def publish_report(bot_token, chat_id, count):
    from telegram import Bot
    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=f"📊 Опубликовано новых постов: {count}")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())