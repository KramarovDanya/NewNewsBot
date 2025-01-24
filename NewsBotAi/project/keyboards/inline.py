from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_buttons() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с кнопками.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Переписать текст", callback_data="rewrite_text")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")],
            [InlineKeyboardButton(text="Опубликовать в канале", callback_data="publish")],
        ]
    )