from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .callbacks import PackageCallback, NavCallback


def _back_button(platform: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="رجوع ↩️",
        callback_data=NavCallback(dest="platforms").pack(),
    )


def tiktok_packages_keyboard() -> InlineKeyboardMarkup:
    platform = "tiktok"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🥉 باقة البداية 👥 3K متابع — 5 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة البداية - 3K متابع", price="5 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥈 باقة النمو 👥 5K متابع — 10 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة النمو - 5K متابع", price="10 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥇 باقة التفاعل ❤️ 20K لايك — 15 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة التفاعل - 20K لايك", price="15 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="💎 باقة الترند 👥 15K متابع — 20 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة الترند - 15K متابع", price="20 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🚀 باقة الهيمنة 👥 30K متابع — 30 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة الهيمنة - 30K متابع", price="30 د.أ").pack(),
        )],
        [_back_button(platform)],
    ])


def instagram_packages_keyboard() -> InlineKeyboardMarkup:
    platform = "instagram"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🥉 باقة البداية 👥 3K متابع — 5 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة البداية - 3K متابع", price="5 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥈 باقة النمو 👥 5K متابع — 10 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة النمو - 5K متابع", price="10 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥇 باقة التفاعل ❤️ 20K لايك — 15 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة التفاعل - 20K لايك", price="15 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="💎 باقة المؤثر 👥 15K متابع — 20 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة المؤثر - 15K متابع", price="20 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🚀 باقة VIP Elite 👥 30K متابع — 30 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة VIP Elite - 30K متابع", price="30 د.أ").pack(),
        )],
        [_back_button(platform)],
    ])


def facebook_packages_keyboard() -> InlineKeyboardMarkup:
    platform = "facebook"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🥉 باقة البداية 👥 3K متابع — 5 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة البداية - 3K متابع", price="5 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥈 باقة النمو 👥 7K متابع — 10 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة النمو - 7K متابع", price="10 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥇 باقة التفاعل 👍 15K تفاعل — 15 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة التفاعل - 15K تفاعل", price="15 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="💎 باقة الاحتراف 👥 15K متابع — 20 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة الاحتراف - 15K متابع", price="20 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🚀 باقة الهيمنة 👥 30K متابع — 30 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة الهيمنة - 30K متابع", price="30 د.أ").pack(),
        )],
        [_back_button(platform)],
    ])


def telegram_packages_keyboard() -> InlineKeyboardMarkup:
    platform = "telegram"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🥉 باقة الانطلاق 👥 3K عضو — 5 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة الانطلاق - 3K عضو", price="5 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥈 باقة التوسع 👥 5K عضو — 10 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة التوسع - 5K عضو", price="10 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥇 باقة النشاط 👁️ 10K مشاهدة — 15 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة النشاط - 10K مشاهدة", price="15 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="💎 باقة الاحتراف 👥 15K عضو — 20 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة الاحتراف - 15K عضو", price="20 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🚀 باقة النخبة 👥 30K عضو — 30 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة النخبة - 30K عضو", price="30 د.أ").pack(),
        )],
        [_back_button(platform)],
    ])


def snapchat_packages_keyboard() -> InlineKeyboardMarkup:
    platform = "snapchat"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🥉 باقة البداية 👥 3K متابع — 5 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة البداية - 3K متابع", price="5 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥈 باقة النمو 👥 5K متابع — 10 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة النمو - 5K متابع", price="10 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥇 باقة المشاهدات 👁️ 15K مشاهدة — 15 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة المشاهدات - 15K مشاهدة", price="15 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="💎 باقة الاحتراف 👥 15K متابع — 20 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة الاحتراف - 15K متابع", price="20 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🚀 باقة VIP 👥 30K متابع — 30 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة VIP - 30K متابع", price="30 د.أ").pack(),
        )],
        [_back_button(platform)],
    ])


def youtube_packages_keyboard() -> InlineKeyboardMarkup:
    platform = "youtube"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🥉 باقة البداية 👁️ 10K مشاهدة — 5 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة البداية - 10K مشاهدة", price="5 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥈 باقة النمو 👍 15K لايك — 10 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة النمو - 15K لايك", price="10 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🥇 باقة التفاعل 💬 5K تعليق — 15 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة التفاعل - 5K تعليق", price="15 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="💎 باقة صانع المحتوى 👥 15K مشترك — 20 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة صانع المحتوى - 15K مشترك", price="20 د.أ").pack(),
        )],
        [InlineKeyboardButton(
            text="🚀 باقة القناة الذهبية 👥 30K مشترك — 30 د.أ",
            callback_data=PackageCallback(platform=platform, label="باقة القناة الذهبية - 30K مشترك", price="30 د.أ").pack(),
        )],
        [_back_button(platform)],
    ])
