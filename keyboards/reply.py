from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu(language: str, is_admin: bool = False) -> ReplyKeyboardMarkup:
    texts = {
        "ru": {
            "learning": "📚 Обучение",
            "training": "🚀 Тренировка",
            "emergency": "🚨 Аварийные ситуации",
            "exam": "🎤 Экзамен",
            "repeat": "📥 Повторение",
            "progress": "📊 Прогресс",
            "settings": "⚙️ Настройки",
            "support": "💳 Поддержать проект",
            "subscribe": "🧾 Оформить подписку",
            "admin": "🛠 Управление"
        },
        "en": {
            "learning": "📚 Learning",
            "training": "🚀 Training",
            "emergency": "🚨 Emergencies",
            "exam": "🎤 Exam",
            "repeat": "📥 Repeat",
            "progress": "📊 Progress",
            "settings": "⚙️ Settings",
            "support": "💳 Support Project",
            "subscribe": "🧾 Subscribe",
            "admin": "🛠 Admin"
        }
    }
    t = texts.get(language, texts["en"])

    buttons = [
        [KeyboardButton(text=t["learning"]), KeyboardButton(text=t["training"]), KeyboardButton(text=t["emergency"]), KeyboardButton(text=t["exam"])],
        [KeyboardButton(text=t["repeat"]), KeyboardButton(text=t["progress"]), KeyboardButton(text=t["settings"])],
        [KeyboardButton(text=t["support"] if not is_admin else t["subscribe"])]
    ]

    if is_admin:
        buttons.append([KeyboardButton(text=t["admin"])])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
