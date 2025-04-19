from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_language_settings():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
    )
    return kb.as_markup()


def get_level_choice():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="✈️ Level 4", callback_data="level_4"),
        InlineKeyboardButton(text="🚀 Level 5", callback_data="level_5")
    )
    return kb.as_markup()


def get_voice_settings(step="question"):
    if step == "question":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔊 Включить", callback_data="voice_q_on"),
             InlineKeyboardButton(text="🔇 Выключить", callback_data="voice_q_off")]
        ])
    elif step == "answer":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔊 Включить", callback_data="voice_a_on"),
             InlineKeyboardButton(text="🔇 Выключить", callback_data="voice_a_off")]
        ])


def get_yes_no_keyboard(prefix: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data=f"{prefix}_yes"),
         InlineKeyboardButton(text="❌ Нет", callback_data=f"{prefix}_no")]
    ])


def get_start_choice_keyboard(lang: str = "ru"):
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Начать обучение", callback_data="start_learning")],
            [InlineKeyboardButton(text="🚀 Перейти к тренировке", callback_data="start_training")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Start learning", callback_data="start_learning")],
            [InlineKeyboardButton(text="🚀 Start training", callback_data="start_training")]
        ])
