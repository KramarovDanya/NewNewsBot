from aiogram.types import Message
from aiogram.fsm.context import FSMContext


async def finalize_post(message: Message, state: FSMContext, scheduled_time=None):
    data = await state.get_data()
    post_text = data.get("post_text", "")
    if scheduled_time:
        await message.answer(f"Публикация запланирована на {scheduled_time}.\n\nТекст:\n{post_text}")
    else:
        await message.answer("Пост опубликован!")
    await state.clear()