from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from services.openai_service import rewrite_text
from keyboards.inline import create_buttons

router = Router()

@router.callback_query(lambda c: c.data == "rewrite_text")
async def rewrite_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Переписать текст".
    """
    data = await state.get_data()
    last_text = data.get("last_text")

    if not last_text:
        await callback.message.answer("Сначала отправьте текст для переписывания.")
        return

    await callback.message.answer("Переписываю текст, подождите немного...")
    rewritten_text = await rewrite_text(last_text)
    buttons = create_buttons()
    await callback.message.answer(f"Вот переписанный текст:\n\n{rewritten_text}", reply_markup=buttons)

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