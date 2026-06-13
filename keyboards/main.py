from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .callbacks import NavCallback, AdminActionCallback, PaymentMethodCallback


def subscription_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown when a user has not subscribed to required channels."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="الدعم ⚙️", url="https://t.me/shaheen_ys"),
        ],
        [
            InlineKeyboardButton(text="هدية يومية 🎁", url="https://t.me/fi1_oo"),
        ],
        [
            InlineKeyboardButton(
                text="تحقق من الاشتراك ✅",
                callback_data=NavCallback(dest="check_subscription").pack(),
            ),
        ],
    ])


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu shown after the welcome video."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 بدء الطلب",
                callback_data=NavCallback(dest="platforms").pack(),
            ),
        ],
        [
            InlineKeyboardButton(text="⭐ بريميوم", url="https://t.me/TYS_GBot"),
            InlineKeyboardButton(text="تـرنــد²⁰³⁰", url="https://t.me/YZAS_YBOT"),
        ],
        [
            InlineKeyboardButton(text="🤖 Bot 2030", url="https://t.me/shaheen_mall"),
            InlineKeyboardButton(
                text="المطور 🛡️",
                callback_data=NavCallback(dest="developer").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="💳 طرق الدفع",
                callback_data=NavCallback(dest="payment_methods_info").pack(),
            ),
            InlineKeyboardButton(text="🎧 الدعم الفني", url="https://t.me/shaheen_ys"),
        ],
        [
            InlineKeyboardButton(
                text="📋 طلباتي",
                callback_data=NavCallback(dest="my_orders").pack(),
            ),
            InlineKeyboardButton(text="نظام الإحالة", url="https://t.me/fi1_oo"),
        ],
    ])


def developer_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown on the developer profile screen."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="تليجرام", url="https://t.me/Y9_S4"),
            InlineKeyboardButton(
                text="انستغرام",
                url="https://www.instagram.com/1.0_v_?igsh=N2N5MXNwN3p4ZDY2",
            ),
        ],
        [
            InlineKeyboardButton(
                text="تيك توك",
                url="https://www.tiktok.com/@zix8ii?_r=1&_d=f3c01a6371bii9&sec_uid=",
            ),
            InlineKeyboardButton(text="واتساب", url="https://wa.link/lc6f5w"),
        ],
        [
            InlineKeyboardButton(
                text="رجوع ↩️",
                callback_data=NavCallback(dest="main_menu").pack(),
            ),
        ],
    ])


def platforms_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting a social media platform."""
    from .callbacks import PlatformCallback
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="TikTok", callback_data=PlatformCallback(name="tiktok").pack()),
            InlineKeyboardButton(text="Instagram", callback_data=PlatformCallback(name="instagram").pack()),
        ],
        [
            InlineKeyboardButton(text="Telegram", callback_data=PlatformCallback(name="telegram").pack()),
            InlineKeyboardButton(text="Snapchat", callback_data=PlatformCallback(name="snapchat").pack()),
        ],
        [
            InlineKeyboardButton(text="Facebook", callback_data=PlatformCallback(name="facebook").pack()),
            InlineKeyboardButton(text="YouTube", callback_data=PlatformCallback(name="youtube").pack()),
        ],
        [
            InlineKeyboardButton(
                text="رجوع ↩️",
                callback_data=NavCallback(dest="main_menu").pack(),
            ),
        ],
    ])


def payment_choice_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown immediately after user selects a package."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💳 طرق الدفع",
                callback_data=NavCallback(dest="payment_methods_select").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="↩️ رجوع",
                callback_data=NavCallback(dest="platforms").pack(),
            ),
            InlineKeyboardButton(
                text="❌ إلغاء الطلب",
                callback_data=NavCallback(dest="cancel").pack(),
            ),
        ],
    ])


def payment_methods_keyboard() -> InlineKeyboardMarkup:
    """Keyboard listing all payment methods."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Orange Money 🟠",
                callback_data=PaymentMethodCallback(method="orange").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="ila bank 🏦",
                callback_data=PaymentMethodCallback(method="ila").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="شحن نجوم ⭐",
                callback_data=PaymentMethodCallback(method="stars").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="PayPal 💙",
                callback_data=PaymentMethodCallback(method="paypal").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="↩️ رجوع",
                callback_data=NavCallback(dest="platforms").pack(),
            ),
            InlineKeyboardButton(
                text="❌ إلغاء الطلب",
                callback_data=NavCallback(dest="cancel").pack(),
            ),
        ],
    ])


def admin_action_keyboard(order_id: int, target_user_id: int) -> InlineKeyboardMarkup:
    """Keyboard attached to order receipts in the admin channel."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ قبول الطلب",
                callback_data=AdminActionCallback(
                    action="accept", order_id=order_id, target_user_id=target_user_id
                ).pack(),
            ),
            InlineKeyboardButton(
                text="❌ رفض الطلب",
                callback_data=AdminActionCallback(
                    action="reject", order_id=order_id, target_user_id=target_user_id
                ).pack(),
            ),
        ],
    ])
