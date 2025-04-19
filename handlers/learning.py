from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.models import get_lessons_by_level, get_lesson_by_id
from keyboards.inline import (
    get_learning_navigation_keyboard,
    get_learning_complete_keyboard,
    get_dont_show_again_button,
    get_lesson_topics_keyboard
)
from services.access import get_user_level, update_user_lesson_progress
from services.progress import (
    save_lesson_progress,
    get_user_lesson_progress,
    mark_lesson_for_repeat,
    get_repeat_lessons
)
from utils.texts import get_intro_text, get_message_text
from utils.helpers import send_temp_message


router = Router()


# --- Состояния ---

class LearningStates(StatesGroup):
    learning = State()


# --- Вход в раздел обучения ---

@router.message(F.text.in_(["📚 Обучение", "Learning"]))
async def enter_learning(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = message.from_user.language_code or "en"
    level = await get_user_level(user_id)

    await state.set_state(LearningStates.learning)

    show_intro = await state.get_data()
    if not show_intro.get("intro_learning_shown"):
        text = get_intro_text("learning", language)
        await message.answer(text, reply_markup=get_dont_show_again_button(language, "learning"))
        await state.update_data(intro_learning_shown=True)
    else:
        await show_current_lesson(message, user_id, level, language)


@router.callback_query(F.data == "hide_intro_learning")
async def hide_intro_learning(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user_id = callback.from_user.id
    language = callback.from_user.language_code or "en"
    level = await get_user_level(user_id)
    await show_current_lesson(callback.message, user_id, level, language)


# --- Показ текущего урока ---

async def show_current_lesson(message: Message, user_id: int, level: str, language: str):
    lesson = await get_user_lesson_progress(user_id, level)
    if not lesson:
        lessons = await get_lessons_by_level(level)
        lesson = lessons[0]
        await save_lesson_progress(user_id, lesson.id)

    text = f"📘 <b>{lesson.title}</b>\n\n{lesson.content}"
    await message.answer(
        text=text,
        reply_markup=get_learning_navigation_keyboard(language)
    )


# --- Навигация по урокам ---

@router.callback_query(F.data.in_(["lesson_next", "lesson_prev"]))
async def navigate_lessons(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    direction = callback.data.split("_")[-1]
    level = await get_user_level(user_id)
    language = callback.from_user.language_code or "en"
    lessons = await get_lessons_by_level(level)
    current = await get_user_lesson_progress(user_id, level)

    try:
        idx = [l.id for l in lessons].index(current.id)
        next_lesson = lessons[idx + 1] if direction == "next" else lessons[idx - 1]
        await save_lesson_progress(user_id, next_lesson.id)
        await callback.message.edit_text(
            text=f"📘 <b>{next_lesson.title}</b>\n\n{next_lesson.content}",
            reply_markup=get_learning_navigation_keyboard(language)
        )
    except (ValueError, IndexError):
        await callback.answer("Это крайний урок", show_alert=False)


# --- Выбор темы ---

@router.callback_query(F.data == "lesson_topics")
async def choose_topic(callback: CallbackQuery):
    user_id = callback.from_user.id
    level = await get_user_level(user_id)
    lessons = await get_lessons_by_level(level)
    await callback.message.edit_text(
        text="📚 Выберите тему:",
        reply_markup=get_lesson_topics_keyboard(lessons)
    )


@router.callback_query(F.data.startswith("lesson_"))
async def load_selected_topic(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[1])
    lesson = await get_lesson_by_id(lesson_id)
    user_id = callback.from_user.id
    language = callback.from_user.language_code or "en"

    await save_lesson_progress(user_id, lesson.id)
    await callback.message.edit_text(
        text=f"📘 <b>{lesson.title}</b>\n\n{lesson.content}",
        reply_markup=get_learning_navigation_keyboard(language)
    )


# --- Повторить позже ---

@router.callback_query(F.data == "lesson_repeat")
async def mark_for_repeat(callback: CallbackQuery):
    user_id = callback.from_user.id
    level = await get_user_level(user_id)
    current = await get_user_lesson_progress(user_id, level)
    await mark_lesson_for_repeat(user_id, current.id)
    await send_temp_message(callback.message, "Тема добавлена в повторение")


# --- Завершение обучения ---

@router.message(F.text.in_(["Закончить обучение", "Finish learning"]))
async def complete_learning(message: Message):
    language = message.from_user.language_code or "en"
    await message.answer(
        text=get_message_text("learning_complete", language),
        reply_markup=get_learning_complete_keyboard(language)
    )
