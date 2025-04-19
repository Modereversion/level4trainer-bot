from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.models import User, Lesson
from keyboards.inline import (
    get_learning_navigation_keyboard,
    get_learning_complete_keyboard,
    get_lesson_topics_keyboard
)
from utils.helpers import get_localized_text, set_user_lesson_progress

router = Router()


@router.message(F.text == "📚 Обучение")
async def enter_learning(message: Message, state: FSMContext):
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        return await message.answer("Ошибка доступа. Пожалуйста, перезапустите бота.")

    if not user.learning_intro_shown:
        text = get_localized_text(user.language, "learning_intro")
        await message.answer(text)
        user.learning_intro_shown = True
        await user.save()

    last_lesson = await Lesson.filter(level=user.level).order_by("id").first()
    if last_lesson:
        await send_lesson(message, user, last_lesson.id, state)


async def send_lesson(message: Message, user: User, lesson_id: int, state: FSMContext):
    lesson = await Lesson.get_or_none(id=lesson_id, level=user.level)
    if not lesson:
        return await message.answer("Урок не найден.")

    await state.update_data(current_lesson_id=lesson.id)
    await set_user_lesson_progress(user.id, lesson.id)

    await message.answer(
        f"<b>{lesson.title}</b>\n\n{lesson.content}",
        reply_markup=get_learning_navigation_keyboard(user.language),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "lesson_next")
async def next_lesson(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_id = data.get("current_lesson_id", 0)
    current_lesson = await Lesson.get_or_none(id=current_id)
    next_lesson = await Lesson.filter(level=current_lesson.level, id__gt=current_id).order_by("id").first()

    if next_lesson:
        await send_lesson(callback.message, current_lesson.user, next_lesson.id, state)
    else:
        await callback.message.edit_text(
            "🎉 Вы завершили обучение!",
            reply_markup=get_learning_complete_keyboard(current_lesson.user.language)
        )


@router.callback_query(F.data == "lesson_prev")
async def previous_lesson(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_id = data.get("current_lesson_id", 0)
    current_lesson = await Lesson.get_or_none(id=current_id)
    prev_lesson = await Lesson.filter(level=current_lesson.level, id__lt=current_id).order_by("-id").first()

    if prev_lesson:
        await send_lesson(callback.message, current_lesson.user, prev_lesson.id, state)
    else:
        await callback.answer("Это первый урок.")


@router.callback_query(F.data == "lesson_repeat")
async def repeat_lesson(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lesson_id = data.get("current_lesson_id", 0)
    user = await User.get_or_none(telegram_id=callback.from_user.id)

    if user and lesson_id:
        await user.lessons_to_repeat.add(lesson_id)
        await callback.answer("Урок добавлен в список повторения.")
    else:
        await callback.answer("Ошибка сохранения.")


@router.callback_query(F.data == "lesson_topics")
async def choose_topic(callback: CallbackQuery):
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    lessons = await Lesson.filter(level=user.level).order_by("id")
    await callback.message.edit_text("📂 Выберите тему:", reply_markup=get_lesson_topics_keyboard(lessons))


@router.callback_query(F.data.startswith("lesson_"))
async def go_to_topic(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split("_")[1])
    user = await User.get_or_none(telegram_id=callback.from_user.id)
    await send_lesson(callback.message, user, lesson_id, state)
