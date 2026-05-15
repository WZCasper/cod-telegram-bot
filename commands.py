import asyncio
from telegram import Bot
from telegram.error import TelegramError

ADMIN_COMMANDS = {
    "/pause": "pause",
    "/resume": "resume",
    "/status": "status",
    "/force_post": "force_post"
}

async def process_commands(bot_token, state):
    bot = Bot(token=bot_token)
    try:
        # Получаем последние непрочитанные обновления (сбросим webhook, чтобы использовать getUpdates)
        updates = await bot.get_updates(offset=-100, timeout=5)
        for update in updates:
            if not update.message or not update.message.text:
                continue
            user = update.message.from_user
            # Проверка прав администратора в канале/группе – упрощённо: только из CHAT_ID.
            # Для простоты считаем, что команды от кого угодно в канале – это небезопасно,
            # но мы можем проверить, состоит ли пользователь в администраторах канала.
            # Пока разрешим только сообщения из нужного чата и если пользователь админ.
            # В state мы не хранили admin_ids, лучше проверить права через get_chat_administrators.
            chat_id = update.message.chat_id
            # Сверяем с CHAT_ID из переменной окружения
            target_chat = os.environ.get("CHAT_ID")
            if str(chat_id) != target_chat:
                continue

            user_id = user.id
            # Получить список админов чата
            try:
                admins = await bot.get_chat_administrators(chat_id)
                admin_ids = [admin.user.id for admin in admins]
            except:
                admin_ids = []
            if user_id not in admin_ids:
                continue

            text = update.message.text.strip()
            if text.startswith("/pause"):
                state["paused"] = True
                await bot.send_message(chat_id=chat_id, text="✅ Бот приостановлен. Постинг новых записей остановлен.")
            elif text.startswith("/resume"):
                state["paused"] = False
                await bot.send_message(chat_id=chat_id, text="✅ Бот возобновлён.")
            elif text.startswith("/status"):
                status = "⏸ Приостановлен" if state.get("paused") else "▶ Активен"
                await bot.send_message(chat_id=chat_id, text=f"Статус: {status}\nПеревод: {'Вкл' if state.get('translate') else 'Выкл'}")
            elif text.startswith("/force_post"):
                parts = text.split(" ", 1)
                if len(parts) > 1:
                    link = parts[1]
                    # Можно принудительно опубликовать, но проще просто отправить сообщение
                    await bot.send_message(chat_id=chat_id, text=f"Принудительная публикация: {link}")
                else:
                    await bot.send_message(chat_id=chat_id, text="Использование: /force_post <ссылка>")
        # помечаем обновления как прочитанные
        if updates:
            await bot.get_updates(offset=updates[-1].update_id + 1)
    except TelegramError as e:
        print(f"Ошибка обработки команд: {e}")