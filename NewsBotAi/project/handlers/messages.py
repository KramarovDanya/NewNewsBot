from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.openai_service import rewrite_text
from keyboards.inline import create_buttons

router = Router()

@router.message(lambda message: message.text)
async def handle_text(message: Message, state: FSMContext):
    """
    Обработчик текстовых сообщений.
    """
    user_text = message.text
    await state.update_data(last_text=user_text)
    await message.answer("Переписываю текст, подождите немного...")

    rewritten_text = await rewrite_text(user_text)
    buttons = create_buttons()
    await message.answer(f"Вот переписанный текст:\n\n{rewritten_text}", reply_markup=buttons)