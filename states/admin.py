from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    # Admin sent /broadcast and is waiting to type the message body
    waiting_for_broadcast = State()
