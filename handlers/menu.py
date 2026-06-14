import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import DEVELOPER_IMAGE
from keyboards import (
    main_menu_keyboard,
    developer_keyboard,
    platforms_keyboard,
    payment_methods_keyboard,
    dream_keyboard,
)
from keyboards.callbacks import NavCallback

router = Router()
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────
# Standard navigation callbacks
# ─────────────────────────────────────────────────────────

@router.callback_query(NavCallback.filter(F.dest == "main_menu"))
async def nav_main_menu(callback: CallbackQuery):
    """Navigate back to the main menu."""
    await callback.message.edit_reply_markup(reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(NavCallback.filter(F.dest == "platforms"))
async def nav_platforms(callback: CallbackQuery):
    """Show platforms selection screen."""
    await callback.message.answer(
        "اختر المنصة المطلوبة",
        reply_markup=platforms_keyboard(),
    )
    await callback.answer()


@router.callback_query(NavCallback.filter(F.dest == "developer"))
async def nav_developer(callback: CallbackQuery):
    """Show developer profile."""
    caption = (
        "معلومات المطور\n\n"
        "YS Developer"
    )
    try:
        await callback.message.answer_photo(
            photo=DEVELOPER_IMAGE,
            caption=caption,
            reply_markup=developer_keyboard(),
        )
    except Exception as e:
        logger.warning("Failed to send developer image: %s. Falling back to text.", e)
        await callback.message.answer(caption, reply_markup=developer_keyboard())
    await callback.answer()


@router.callback_query(NavCallback.filter(F.dest == "payment_methods_info"))
async def nav_payment_methods_info(callback: CallbackQuery):
    """Show payment methods from the main menu (info only, no active order)."""
    await callback.message.answer(
        "💳 طرق الدفع المتاحة\n\nاختر طريقة الدفع المناسبة:",
        reply_markup=payment_methods_keyboard(),
    )
    await callback.answer()


# ─────────────────────────────────────────────────────────
# 🎁 قسم الربح والجوائز — "أرسل كلمة حلم أو dream"
# ─────────────────────────────────────────────────────────

DREAM_MESSAGE = """🎉 أهلاً بك في قسم الربح والجوائز! 🎉

💰 حوّل وقت المشاهدة إلى نقاط ومكافآت قيّمة.

🎬 شاهد الفيديوهات المتاحة واحصل على:
⭐ 300 نقطة لكل فيديو تشاهده حتى النهاية.

🏆 لماذا تشارك؟
• جمع النقاط بسهولة وسرعة.
• استبدال النقاط بمكافآت وجوائز مميزة.
• المشاركة في العروض والسحوبات الحصرية.
• فرصة الوصول إلى قائمة أفضل المستخدمين.

📊 رصيدك يزداد مع كل مشاهدة ناجحة، وكل نقطة تقربك من جائزتك القادمة.

⚡ طريقة الربح:
1️⃣ اضغط على "مشاهدة فيديو".
2️⃣ شاهد الفيديو بالكامل.
3️⃣ استلم 300 نقطة مباشرة في رصيدك.

🚨 تنبيه:
يجب إكمال مشاهدة الفيديو للحصول على المكافأة، وأي استخدام غير مشروع قد يؤدي إلى إلغاء النقاط.

🎁 ابدأ الآن واجمع آلاف النقاط يومياً واستمتع بالمكافآت المتاحة!"""


@router.callback_query(NavCallback.filter(F.dest == "dream"))
async def nav_dream(callback: CallbackQuery):
    """Show the prize and rewards section when user presses the dream button."""
    logger.info("User %s opened the dream/rewards section.", callback.from_user.id)
    await callback.message.answer(
        DREAM_MESSAGE,
        reply_markup=dream_keyboard(),
    )
    await callback.answer()
