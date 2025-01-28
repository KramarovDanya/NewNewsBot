from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter


from states import PublishStates
from middlewares.helpers import finalize_post

router = Router()
 
 
@router.callback_query(lambda c: c.data == "cancel")
async def cancel_callback(callback: CallbackQuery):
    """
    Обработчик нажатия на кнопку "Отменить".
    """
    await callback.message.answer("Действие отменено.")


@router.callback_query(lambda c: c.data == "publish")
async def publish_callback(callback: CallbackQuery):
    """
    Обработчик нажатия на кнопку "Опубликовать в канале".
    """
    await callback.message.answer("Текст будет опубликован в канале (заглушка).")
    
    
@router.callback_query(lambda c: c.data == "cancel_publish")
async def cancel_publish(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Отменить публикацию".
    """
    await state.set_state(PublishStates.idle)  # Возвращаем бота в начальное состояние
    await callback.message.answer("Процесс публикации отменен.")
    await callback.answer()
    

@router.callback_query(StateFilter(PublishStates.waiting_for_media_decision), F.data == "add_media")
async def on_add_media(callback: CallbackQuery, state: FSMContext):
    """
    Пользователь выбирает "Добавить медиа".
    """
    await callback.answer()
    await callback.message.answer(
        "Отправьте фото или видео одним сообщением.\n"
        "Если нужно отправить несколько фото подряд (альбом), придётся доработать код отдельно."
    )
    await state.set_state(PublishStates.waiting_for_media)
    
       
@router.callback_query(lambda c: c.data == "publish_now")
async def on_publish_now(callback: CallbackQuery, state: FSMContext):

    await callback.answer()
    await finalize_post(callback.message, state)


@router.callback_query(lambda c: c.data == "schedule_later")
async def on_schedule_later(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer("Введите дату и время в формате DD.MM.YYYY HH:MM, например: 27.01.2025 12:30")
    await state.set_state(PublishStates.waiting_for_scheduled_time)