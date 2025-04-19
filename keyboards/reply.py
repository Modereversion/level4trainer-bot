from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard(lang: str = "en"):
    if lang == "ru":
        buttons = [
            [KeyboardButton(text="📚 Обучение"), KeyboardButton(text="🚀 Тренировка")],
            [KeyboardButton(text="🚨 Аварийные ситуации"), KeyboardButton(text="🎤 Экзамен")],
            [KeyboardButton(text="📥 Повторение"), KeyboardButton(text="📊 Прогресс")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="💳 Поддержать проект")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="📚 Learning"), KeyboardButton(text="🚀 Training")],
            [KeyboardButton(text="🚨 Emergencies"), KeyboardButton(text="🎤 Exam")],
            [KeyboardButton(text="📥 Review"), KeyboardButton(text="📊 Progress")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="💳 Support Project")]
        ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
