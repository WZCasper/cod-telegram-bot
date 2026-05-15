import json
import os

STATE_FILE = "state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "last_ids": {},     # по источникам: {"blog": "...", "twitter_main": "...", ...}
            "paused": False,
            "min_interval_minutes": 15,
            "translate": True,
            "category_emojis": True,
            "anti_spam": True,
            "admin_ids": []     # пока не используется, но можно добавить
        }
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"Состояние успешно сохранено в {STATE_FILE}")
    except Exception as e:
        print(f"ОШИБКА сохранения state.json: {e}")
