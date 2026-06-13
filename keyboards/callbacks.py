from aiogram.filters.callback_data import CallbackData


class PlatformCallback(CallbackData, prefix="platform"):
    name: str  # e.g. "tiktok", "instagram"


class PackageCallback(CallbackData, prefix="pkg"):
    platform: str
    label: str   # Short human-readable label stored in FSM
    price: str


class PaymentMethodCallback(CallbackData, prefix="pay"):
    method: str  # e.g. "orange", "ila", "stars", "paypal"


class AdminActionCallback(CallbackData, prefix="admin"):
    action: str   # "accept" or "reject"
    order_id: int
    target_user_id: int


class NavCallback(CallbackData, prefix="nav"):
    dest: str  # e.g. "main_menu", "platforms", "payment_methods"
