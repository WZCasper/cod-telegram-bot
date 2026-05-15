import asyncio
from telegram import Bot
from telegram.error import TelegramError

async def publish_post(bot_token, chat_id, post, translate, state):
    from utils.formatter import build_message
    text = build_message(post, translate=translate)
    bot = Bot(token=bot_token)
    try:
        if post.get("image"):
            # отправляем фото с подписью
            await bot.send_photo(
                chat_id=chat_id,
                photo=post["image"],
                caption=text,
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )
        return True
    except TelegramError as e:
        print(f"Ошибка отправки: {e}")
        return False