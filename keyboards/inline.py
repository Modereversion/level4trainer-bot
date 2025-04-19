from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def language_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru")
        ]
    ])

def inline_back_button(lang: str = "en"):
    text = "⬅️ Back" if lang == "en" else "⬅️ Назад"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data="go_back")]
    ])
