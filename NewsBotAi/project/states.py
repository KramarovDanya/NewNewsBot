from aiogram.fsm.state import StatesGroup, State

class PublishStates(StatesGroup):
    idle = State()
    waiting_for_text = State()
    waiting_for_media_decision = State()
    waiting_for_media = State()
    waiting_for_publish_choice = State()
    waiting_for_scheduled_time = State()