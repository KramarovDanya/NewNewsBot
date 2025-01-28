from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from states import PublishStates
from services.openai_service import rewrite_text
from keyboards.inline import create_buttons, create_media_decision_keyboard, create_publish_time_keyboard
from services.openai_service import rewrite_text
from keyboards.inline import create_buttons
from middlewares.helpers import finalize_post

router = Router()

# @router.message(lambda message: message.text)
# async def handle_text(message: Message, state: FSMContext):
#     """
#     Обработчик текстовых сообщений.
#     """
#     user_text = message.text
#     await state.update_data(last_text=user_text)
#     await message.answer("Переписываю текст, подождите немного...")

#     rewritten_text = await rewrite_text(user_text)
#     buttons = create_buttons()
#     await message.answer(f"Вот переписанный текст:\n\n{rewritten_text}", reply_markup=buttons)


# @router.message(lambda message: message.text)
# async def publish_post(message: Message, state: FSMContext):
#     """
#     Функция «публикации» поста (текста и медиа).
#     """
#     user_text = message.text

#     await state.update_data(post_text=user_text)
#     await message.answer("Публикую ваш пост, подождите немного...")

#     data = await state.get_data()
#     post_text = data.get("post_text", "Текст не найден")
#     media_type = data.get("media_type")  
#     media_id = data.get("media_id")      


#     if media_type == "photo" and media_id:
#         await message.answer_photo(photo=media_id, caption=post_text)
#     elif media_type == "video" and media_id:
#         await message.answer_video(video=media_id, caption=post_text)
#     else:
#         await message.answer(post_text)

#     buttons = create_buttons()
#     await message.answer("Пост опубликован!", reply_markup=buttons)

@router.message(StateFilter(PublishStates.idle or None))
async def handle_text(message: Message, state: FSMContext):
    # В этом состоянии бот будет переписывать тексты
    last_text = message.text
    rewritten_text = await rewrite_text(last_text)
    buttons = create_buttons()
    await message.answer(f"Вот переписанный текст:\n\n{rewritten_text}", reply_markup=buttons)
 
    
@router.message(StateFilter(PublishStates.waiting_for_text))
async def get_post_text(message: Message, state: FSMContext):

    await state.update_data(post_text=message.text)
    keyboard = create_media_decision_keyboard()  
    await message.answer("Хотите добавить медиа (фото или видео)?", reply_markup=keyboard)
    await state.set_state(PublishStates.waiting_for_media_decision)


async def ask_publish_now_or_later(message: Message, state: FSMContext):
    keyboard = create_publish_time_keyboard()
    await message.answer("Опубликовать сейчас или запланировать на будущее?", reply_markup=keyboard)
    await state.set_state(PublishStates.waiting_for_publish_choice)
    
    
@router.message(
    StateFilter(PublishStates.waiting_for_media),
    F.content_type.in_({"photo", "video"}),
)
async def get_media(message: Message, state: FSMContext):
    """
    Принимаем одно фото или видео.
    Если требуется альбом, нужно будет обработать это через MediaGroup.
    """
    data = await state.get_data()

    # Если фото
    if message.photo:
        file_id = message.photo[-1].file_id
        data["media_type"] = "photo"
        data["media_id"] = file_id
    # Если видео
    elif message.video:
        file_id = message.video.file_id
        data["media_type"] = "video"
        data["media_id"] = file_id

    await state.update_data(**data)

    # Переходим к выбору времени публикации
    await ask_publish_now_or_later(message, state)

   
@router.message(StateFilter(PublishStates.waiting_for_scheduled_time))
async def get_scheduled_time(message: Message, state: FSMContext):

    datetime_str = message.text.strip()
    await finalize_post(message, state, scheduled_time=datetime_str)