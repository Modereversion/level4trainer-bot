from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Lesson


# ---------- Обучение ----------

def get_learning_navigation_keyboard(language: str) -> InlineKeyboardMarkup:
    texts = {
        "ru": {
            "prev": "↩️ Предыдущий урок",
            "next": "▶️ Следующий урок",
            "choose": "📂 Выбрать тему",
            "repeat": "🔁 Повторить позже"
        },
        "en": {
            "prev": "↩️ Previous lesson",
            "next": "▶️ Next lesson",
            "choose": "📂 Choose topic",
            "repeat": "🔁 Repeat later"
        }
    }
    t = texts.get(language, texts["en"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["prev"], callback_data="lesson_prev")
    builder.button(text=t["next"], callback_data="lesson_next")
    builder.button(text=t["choose"], callback_data="lesson_topics")
    builder.button(text=t["repeat"], callback_data="lesson_repeat")
    builder.adjust(2, 2)
    return builder.as_markup()


def get_learning_complete_keyboard(language: str) -> InlineKeyboardMarkup:
    texts = {
        "ru": {
            "repeat": "🔁 Повторить обучение",
            "train": "🚀 Начать тренировку",
            "exam": "🎤 Пройти экзамен"
        },
        "en": {
            "repeat": "🔁 Repeat training",
            "train": "🚀 Start training",
            "exam": "🎤 Take the exam"
        }
    }
    t = texts.get(language, texts["en"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["repeat"], callback_data="start_learning_again")
    builder.button(text=t["train"], callback_data="go_to_training")
    builder.button(text=t["exam"], callback_data="go_to_exam")
    builder.adjust(1)
    return builder.as_markup()


def get_lesson_topics_keyboard(lessons: list[Lesson]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for lesson in lessons:
        builder.button(text=lesson.title, callback_data=f"lesson_{lesson.id}")
    builder.adjust(1)
    return builder.as_markup()


# ---------- Кнопка “Больше не показывать” ----------

def get_dont_show_again_button(language: str, section: str) -> InlineKeyboardMarkup:
    texts = {
        "ru": "Не показывать снова",
        "en": "Don't show again"
    }
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.get(language, "Don't show again"),
            callback_data=f"hide_intro_{section}"
        )]
    ])


# ---------- Озвучка ----------

def get_voice_menu(language: str, current_state: dict) -> InlineKeyboardMarkup:
    texts = {
        "ru": {
            "questions": "🗣️ Озвучка вопросов",
            "answers": "🗣️ Озвучка ответов",
            "on": "Включена",
            "off": "Отключена"
        },
        "en": {
            "questions": "🗣️ Question voice",
            "answers": "🗣️ Answer voice",
            "on": "On",
            "off": "Off"
        }
    }
    t = texts.get(language, texts["en"])
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"{t['questions']}: {t['on'] if current_state['question'] else t['off']}",
        callback_data="toggle_voice_question"
    )
    builder.button(
        text=f"{t['answers']}: {t['on'] if current_state['answer'] else t['off']}",
        callback_data="toggle_voice_answer"
    )
    builder.adjust(1)
    return builder.as_markup()


# ---------- Повторение ----------

def get_repeat_menu(language: str, has_questions: bool, has_lessons: bool) -> InlineKeyboardMarkup:
    texts = {
        "ru": {"questions": "❓ Вопросы", "lessons": "📘 Темы"},
        "en": {"questions": "❓ Questions", "lessons": "📘 Topics"}
    }
    t = texts.get(language, texts["en"])
    buttons = []

    if has_questions:
        buttons.append(InlineKeyboardButton(text=t["questions"], callback_data="repeat_questions"))
    if has_lessons:
        buttons.append(InlineKeyboardButton(text=t["lessons"], callback_data="repeat_lessons"))

    if not buttons:
        return None

    return InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
