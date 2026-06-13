import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import (
    TIKTOK_IMAGE,
    INSTAGRAM_IMAGE,
    FACEBOOK_IMAGE,
    TELEGRAM_IMAGE,
    SNAPCHAT_IMAGE,
    YOUTUBE_IMAGE,
)
from keyboards import (
    tiktok_packages_keyboard,
    instagram_packages_keyboard,
    facebook_packages_keyboard,
    telegram_packages_keyboard,
    snapchat_packages_keyboard,
    youtube_packages_keyboard,
)
from keyboards.callbacks import PlatformCallback, PackageCallback
from keyboards.main import payment_choice_keyboard
from states import OrderStates
from aiogram.fsm.context import FSMContext

router = Router()
logger = logging.getLogger(__name__)

PLATFORM_CONFIG = {
    "tiktok":    (TIKTOK_IMAGE,    "خدمات تيك توك المتاحة",    tiktok_packages_keyboard),
    "instagram": (INSTAGRAM_IMAGE, "خدمات انستغرام المتاحة",   instagram_packages_keyboard),
    "facebook":  (FACEBOOK_IMAGE,  "خدمات فيسبوك المتاحة",     facebook_packages_keyboard),
    "telegram":  (TELEGRAM_IMAGE,  "خدمات تيليجرام المتاحة",   telegram_packages_keyboard),
    "snapchat":  (SNAPCHAT_IMAGE,  "خدمات سناب شات المتاحة",   snapchat_packages_keyboard),
    "youtube":   (YOUTUBE_IMAGE,   "خدمات يوتيوب المتاحة",     youtube_packages_keyboard),
}


@router.callback_query(PlatformCallback.filter())
async def show_platform_packages(callback: CallbackQuery, callback_data: PlatformCallback):
    """Display service packages for the selected platform."""
    platform = callback_data.name
    config = PLATFORM_CONFIG.get(platform)

    if not config:
        await callback.answer("منصة غير معروفة.", show_alert=True)
        return

    image_url, caption, keyboard_fn = config

    try:
        await callback.message.answer_photo(
            photo=image_url,
            caption=caption,
            reply_markup=keyboard_fn(),
        )
    except Exception as e:
        logger.warning(
            "Failed to send platform image for %s: %s. Falling back to text.", platform, e
        )
        await callback.message.answer(caption, reply_markup=keyboard_fn())

    await callback.answer()


@router.callback_query(PackageCallback.filter())
async def select_package(
    callback: CallbackQuery,
    callback_data: PackageCallback,
    state: FSMContext,
):
    """
    Store selected service details in FSM and prompt user to proceed to payment.
    Saves extra fields (price_str, platform, package_label) so the Stars payment
    handler can build a correct Telegram invoice without re-parsing the combined label.
    """
    platform      = callback_data.platform
    label         = callback_data.label
    price         = callback_data.price

    service_label = f"{platform.upper()} | {label} | {price}"

    await state.update_data(
        selected_service=service_label,
        price_str=price,          # e.g. "5 د.أ"
        platform=platform,        # e.g. "tiktok"
        package_label=label,      # e.g. "باقة البداية - 3K متابع"
    )
    await state.set_state(OrderStates.waiting_for_payment_method)

    await callback.message.answer(
        "تم اختيار الخدمة بنجاح ✅\n\n"
        "لبدء التنفيذ يرجى إتمام عملية الدفع أولاً.",
        reply_markup=payment_choice_keyboard(),
    )
    await callback.answer()
