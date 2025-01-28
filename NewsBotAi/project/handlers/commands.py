from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.inline import cancel_publish_button
from handlers.callbacks import PublishStates

router = Router()

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await state.set_state(PublishStates.idle)
    await message.answer("Привет! Отправь мне текст для переписывания или используй команду /new_publish для начала публикации.")

@router.message(Command("new_publish"))
async def start_publish_command(message: Message, state: FSMContext):
    await state.set_state(PublishStates.waiting_for_text)
    buttons = cancel_publish_button()
    await message.answer("Отправь мне текст публикации.", reply_markup=buttons)
    
@router.message(Command("state"))
async def show_current_state(message: Message, state: FSMContext):
    """
    Обработчик команды /state, который выводит текущее состояние пользователя.
    """
    current_state = await state.get_state()  # Получаем текущее состояние пользователя
    if current_state is None:
        await message.answer("Текущее состояние: None (бот в основном режиме ожидания)")
    else:
        await message.answer(f"Текущее состояние: {current_state}")