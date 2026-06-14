from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .callbacks import NavCallback, AdminActionCallback, PaymentMethodCallback


# ══════════════════════════════════════════════════════════
# User-facing keyboards
# ══════════════════════════════════════════════════════════

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu — shown to every regular user right after /start."""
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
            InlineKeyboardButton(
                text="🛍️ متجر شاهين",
                url="https://t.me/shaheen_mall_ys",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🎁 أرسل كلمة حلم أو dream",
                callback_data=NavCallback(dest="dream").pack(),
            ),
        ],
    ])


def developer_keyboard() -> InlineKeyboardMarkup:
    """Developer profile buttons."""
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
                text="↩️ رجوع",
                callback_data=NavCallback(dest="main_menu").pack(),
            ),
        ],
    ])


def platforms_keyboard() -> InlineKeyboardMarkup:
    """Platform selection keyboard."""
    from .callbacks import PlatformCallback
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="TikTok",    callback_data=PlatformCallback(name="tiktok").pack()),
            InlineKeyboardButton(text="Instagram", callback_data=PlatformCallback(name="instagram").pack()),
        ],
        [
            InlineKeyboardButton(text="Telegram",  callback_data=PlatformCallback(name="telegram").pack()),
            InlineKeyboardButton(text="Snapchat",  callback_data=PlatformCallback(name="snapchat").pack()),
        ],
        [
            InlineKeyboardButton(text="Facebook",  callback_data=PlatformCallback(name="facebook").pack()),
            InlineKeyboardButton(text="YouTube",   callback_data=PlatformCallback(name="youtube").pack()),
        ],
        [
            InlineKeyboardButton(
                text="↩️ رجوع",
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
    """All payment methods."""
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


def dream_keyboard() -> InlineKeyboardMarkup:
    """Prize and reward links — the dream/حلم section."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🏆 كن الفائز",
                url="https://www.effectivecpmnetwork.com/rxq4tac0?key=bbe818c4c2fe1f47f526cb5f7229e6ea",
            ),
            InlineKeyboardButton(
                text="🎯 ضربة حظ",
                url="https://omg10.com/4/11053040",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📦 الصندوق السحري",
                url="https://omg10.com/4/11018852",
            ),
            InlineKeyboardButton(
                text="🌟 هدية الموسم",
                url="https://pndk.to/GzkItkp2T",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⚡ جائزة فورية",
                url="https://pndk.to/iWQ9QfdEY",
            ),
            InlineKeyboardButton(
                text="🎡 عجلة الحظ",
                url="https://pndk.to/aNGaCjHQf",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🎁 صندوق المفاجآت",
                url="https://pndk.to/Cy5KTOU5",
            ),
            InlineKeyboardButton(
                text="🥇 صندوق الذهب",
                url="https://www.effectivecpmnetwork.com/rxq4tac0?key=bbe818c4c2fe1f47f526cb5f7229e6ea",
            ),
        ],
        [
            InlineKeyboardButton(
                text="↩️ رجوع",
                callback_data=NavCallback(dest="main_menu").pack(),
            ),
        ],
    ])


# ══════════════════════════════════════════════════════════
# Admin / Owner keyboards (never shown to regular users)
# ══════════════════════════════════════════════════════════

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Control panel — shown ONLY to owner and admins on /start."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 الإحصائيات",
                callback_data=NavCallback(dest="ap_stats").pack(),
            ),
            InlineKeyboardButton(
                text="📦 الطلبات",
                callback_data=NavCallback(dest="ap_orders").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="📢 إذاعة",
                callback_data=NavCallback(dest="ap_broadcast").pack(),
            ),
            InlineKeyboardButton(
                text="👥 المستخدمين",
                callback_data=NavCallback(dest="ap_users").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="⚙️ الإعدادات",
                callback_data=NavCallback(dest="ap_settings").pack(),
            ),
            InlineKeyboardButton(
                text="💳 المدفوعات",
                callback_data=NavCallback(dest="ap_payments").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="🌐 القائمة الرئيسية",
                callback_data=NavCallback(dest="ap_main_menu").pack(),
            ),
        ],
    ])


def admin_action_keyboard(order_id: int, target_user_id: int) -> InlineKeyboardMarkup:
    """Buttons on order receipt messages in the admin channel."""
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
