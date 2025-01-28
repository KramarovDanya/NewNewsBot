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
            # [InlineKeyboardButton(text="Публикация", callback_data="сreate_publish")],
        ]
    )

def cancel_publish_button() -> InlineKeyboardMarkup:
    """
    Создает кнопки для управления процессом публикации.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить публикацию", callback_data="cancel_publish")],
    ])
    
def create_media_decision_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопки: "Добавить медиа" | "Пропустить"
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить медиа", callback_data="add_media")],
            [InlineKeyboardButton(text="Пропустить", callback_data="skip_media"),],
        ]
    )


def create_publish_time_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопки: "Опубликовать сейчас" | "Запланировать"
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Опубликовать сейчас", callback_data="publish_now"),],
            [InlineKeyboardButton(text="Запланировать", callback_data="schedule_later"),],
        ]
    )