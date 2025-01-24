from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    """
    Обработчик команды /start.
    """
    await message.answer("Привет! Отправь мне текст, и я помогу его переписать.")