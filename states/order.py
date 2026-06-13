from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    # User has selected a service and is viewing payment options
    waiting_for_payment_method = State()

    # User selected a payment method and must upload receipt photo
    waiting_for_receipt = State()
