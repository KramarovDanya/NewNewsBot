
import logging
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio


# Замените токены на свои
TELEGRAM_API_TOKEN = "7649223528:AAFHMjC1E14cT1XKmDGv1Nq-SLE3rgBl23U"
openai.api_key = ""

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Функция для переписывания текста с использованием OpenAI
async def rewrite_text(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощник, который переписывает тексты."},
                {"role": "user", "content": text},
            ],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Ошибка при запросе к OpenAI API: {e}")
        return None



# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Отправь мне текст, и я помогу его переписать.")

# Создание кнопок
async def create_buttons():
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Переписать текст", callback_data="rewrite_text")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")],
            [InlineKeyboardButton(text="Опубликовать в канале", callback_data="publish")],
        ]
    )
    return buttons

# Обработчик входящих сообщений
@dp.message(lambda message: message.text)
async def handle_text(message: Message):
    user_text = message.text
    await message.answer("Переписываю текст, подождите немного...")

    rewritten_text = await rewrite_text(user_text)
    if rewritten_text:
        buttons = await create_buttons()
        await message.answer(f"Вот переписанный текст:\n\n{rewritten_text}", reply_markup=buttons)
    else:
        buttons = await create_buttons()
        await message.answer("Произошла ошибка при переписывании текста. Попробуйте позже.",reply_markup=buttons )

# Обработчик нажатий на кнопки
@dp.callback_query()
async def handle_buttons(callback: CallbackQuery):
    if callback.data == "rewrite_text":
        await callback.message.answer("Отправьте текст, который нужно переписать.")
    elif callback.data == "cancel":
        await callback.message.answer("Действие отменено.")
    elif callback.data == "publish":
        await callback.message.answer("Текст будет опубликован в канале (заглушка).")

# Главная функция для запуска бота
async def main():
    # Убедимся, что обновления не будут потеряны
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск диспетчера
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())