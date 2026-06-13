"""
handlers/payment.py — YS | 94 Bot

Two distinct payment paths:
  ① Orange Money / ila bank / PayPal
      → user uploads receipt photo
      → admin reviews and accepts/rejects manually

  ② Telegram Stars (XTR)
      → bot sends a real Telegram invoice via send_invoice()
      → user pays inside Telegram (no external app needed)
      → pre_checkout_query is auto-approved
      → successful_payment fires → order auto-accepted + DB updated
"""

import logging
import re
from datetime import datetime

from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from config import (
    ADMIN_CHANNEL_ID,
    ILA_BANK_IMAGE,
    ORANGE_MONEY_IMAGE,
    PAYPAL_IMAGE,
)
from database import (
    log_order,
    log_payment,
    log_stars_payment,
    update_order_status,
)
from keyboards import admin_action_keyboard, main_menu_keyboard, payment_methods_keyboard
from keyboards.callbacks import NavCallback, PaymentMethodCallback
from states import OrderStates

router = Router()
logger = logging.getLogger(__name__)


# ── Price table: JOD amount string → XTR stars ────────────────
# Conversion: ~50 XTR per 1 JOD (adjustable here without touching keyboards)
PRICE_TO_STARS: dict[str, int] = {
    "5":  250,
    "10": 500,
    "15": 750,
    "20": 1000,
    "30": 1500,
}

PLATFORM_DISPLAY: dict[str, str] = {
    "tiktok":    "TikTok",
    "instagram": "Instagram",
    "facebook":  "Facebook",
    "telegram":  "Telegram",
    "snapchat":  "Snapchat",
    "youtube":   "YouTube",
}

METHOD_NAMES: dict[str, str] = {
    "orange": "Orange Money 🟠",
    "ila":    "ila bank 🏦",
    "stars":  "شحن نجوم ⭐",
    "paypal": "PayPal 💙",
}

METHOD_IMAGES: dict[str, str | None] = {
    "orange": ORANGE_MONEY_IMAGE,
    "ila":    ILA_BANK_IMAGE,
    "stars":  None,
    "paypal": PAYPAL_IMAGE,
}


def _extract_price_num(price_str: str) -> str:
    """Return the first integer found in a price string like '10 د.أ' → '10'."""
    match = re.search(r"\d+", price_str)
    return match.group() if match else "5"


# ═══════════════════════════════════════════════════════════
# Show payment methods
# ═══════════════════════════════════════════════════════════

@router.callback_query(NavCallback.filter(F.dest == "payment_methods_select"))
async def show_payment_methods(callback: CallbackQuery, state: FSMContext):
    """Display payment options when user has a pending FSM order."""
    await callback.message.answer(
        "💳 اختر طريقة الدفع:",
        reply_markup=payment_methods_keyboard(),
    )
    await callback.answer()


# ═══════════════════════════════════════════════════════════
# User selects a payment method
# ═══════════════════════════════════════════════════════════

@router.callback_query(PaymentMethodCallback.filter(), OrderStates.waiting_for_payment_method)
async def select_payment_method(
    callback: CallbackQuery,
    callback_data: PaymentMethodCallback,
    state: FSMContext,
    bot: Bot,
):
    """
    Route to the correct payment path based on the chosen method.
    Stars → real Telegram invoice (no receipt needed).
    Others → ask user to upload a receipt photo.
    """
    method      = callback_data.method
    method_name = METHOD_NAMES.get(method, method)
    data        = await state.get_data()

    # ── Path A: Telegram Stars ────────────────────────────
    if method == "stars":
        await _handle_stars_payment(callback, state, bot, data)
        return

    # ── Path B: Receipt upload (Orange / ila / PayPal) ───
    image_url = METHOD_IMAGES.get(method)
    await state.update_data(payment_method=method_name)
    await state.set_state(OrderStates.waiting_for_receipt)

    if image_url:
        try:
            await callback.message.answer_photo(
                photo=image_url,
                caption=f"💳 طريقة الدفع: <b>{method_name}</b>",
            )
        except Exception as exc:
            logger.warning("Failed to send payment image for %s: %s", method, exc)

    await callback.message.answer(
        f"✅ اخترت: <b>{method_name}</b>\n\n"
        "📷 يرجى إرسال <b>صورة الإيصال</b> لإتمام المراجعة."
    )
    logger.info("User %s selected payment method: %s", callback.from_user.id, method_name)
    await callback.answer()


# ═══════════════════════════════════════════════════════════
# Path A — Telegram Stars invoice
# ═══════════════════════════════════════════════════════════

async def _handle_stars_payment(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    fsm_data: dict,
) -> None:
    """
    Create and send a real Telegram invoice denominated in XTR (Stars).

    Steps:
      1. Extract price and convert to stars.
      2. Log a 'pending' order in the DB to get an order_id.
      3. Embed order_id in the invoice payload.
      4. Send the invoice — Telegram handles the payment UI natively.
      5. Clear FSM (SuccessfulPayment handler takes over from here).
    """
    user             = callback.from_user
    selected_service = fsm_data.get("selected_service", "خدمة")
    price_str        = fsm_data.get("price_str", "5 د.أ")
    platform         = fsm_data.get("platform", "")
    package_label    = fsm_data.get("package_label", selected_service)

    price_num    = _extract_price_num(price_str)
    stars_amount = PRICE_TO_STARS.get(price_num, 250)

    # Log order first — we need an order_id for the invoice payload
    order_id = await log_order(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        service=selected_service,
        payment_method="شحن نجوم ⭐",
    )

    # Build invoice strings (Telegram limits: title ≤ 32, description ≤ 255)
    platform_display = PLATFORM_DISPLAY.get(platform, platform.upper())
    raw_title        = f"{platform_display} | {package_label}"
    invoice_title    = raw_title[:32]
    invoice_desc     = (
        f"⭐ {package_label}\n"
        f"💰 {price_str}  =  {stars_amount} نجمة تيليجرام"
    )[:255]

    # payload must be 1-128 chars; we embed order_id + user_id for verification
    payload = f"order:{order_id}:{user.id}"

    await state.clear()  # FSM no longer needed once invoice is sent

    logger.info(
        "Sending Stars invoice — order #%s — user %s — %s XTR",
        order_id, user.id, stars_amount,
    )

    try:
        await bot.send_invoice(
            chat_id=callback.message.chat.id,
            title=invoice_title,
            description=invoice_desc,
            payload=payload,
            currency="XTR",
            prices=[LabeledPrice(label="⭐ نجوم تيليجرام", amount=stars_amount)],
        )
    except Exception as exc:
        logger.error(
            "Failed to send Stars invoice for order #%s: %s", order_id, exc
        )
        await callback.message.answer(
            "⚠️ حدث خطأ أثناء إنشاء الفاتورة.\n"
            "يرجى المحاولة مجدداً أو اختيار طريقة دفع أخرى.",
            reply_markup=main_menu_keyboard(),
        )

    await callback.answer()


# ═══════════════════════════════════════════════════════════
# Path A — Pre-checkout query (must respond within 10 s)
# ═══════════════════════════════════════════════════════════

@router.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery, bot: Bot):
    """
    Telegram sends this before completing any Stars payment.
    We auto-approve all invoices issued by this bot.
    """
    logger.info(
        "PreCheckoutQuery — user %s — payload: %s — %s XTR",
        query.from_user.id, query.invoice_payload, query.total_amount,
    )
    await bot.answer_pre_checkout_query(query.id, ok=True)


# ═══════════════════════════════════════════════════════════
# Path A — Successful payment (Stars transaction complete)
# ═══════════════════════════════════════════════════════════

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, bot: Bot):
    """
    Fires after the user completes a Telegram Stars payment.

    Actions:
      1. Parse order_id from the invoice payload.
      2. Auto-accept the order in the DB.
      3. Record Stars payment details in stars_payments table.
      4. Send success confirmation to the user.
      5. Notify the admin channel.
    """
    sp         = message.successful_payment
    payload    = sp.invoice_payload              # "order:{order_id}:{user_id}"
    stars_paid = sp.total_amount                 # integer, e.g. 250
    charge_id  = sp.telegram_payment_charge_id   # Telegram's transaction reference
    user       = message.from_user

    # ── Parse payload ───────────────────────────────────────
    try:
        _, order_id_str, _ = payload.split(":")
        order_id = int(order_id_str)
    except (ValueError, AttributeError) as exc:
        logger.error("Malformed Stars payment payload '%s': %s", payload, exc)
        await message.answer(
            "✅ تم استلام الدفع، لكن حدث خطأ في تسجيل الطلب تلقائياً.\n"
            "يرجى التواصل مع الدعم الفني وإرسال هذا الرقم:\n"
            f"<code>{charge_id}</code>",
        )
        return

    # ── 1. Auto-accept the order ────────────────────────────
    await update_order_status(order_id, "accepted")

    # ── 2. Record Stars payment ─────────────────────────────
    await log_stars_payment(
        order_id=order_id,
        user_id=user.id,
        stars_amount=stars_paid,
        charge_id=charge_id,
    )

    logger.info(
        "Stars payment SUCCESS — order #%s — user %s — %s XTR — charge: %s",
        order_id, user.id, stars_paid, charge_id,
    )

    # ── 3. Confirm to user ──────────────────────────────────
    await message.answer(
        "✅ <b>تم الدفع بالنجوم بنجاح!</b>\n\n"
        f"⭐ النجوم المدفوعة: <b>{stars_paid}</b>\n"
        f"🔢 رقم الطلب: <code>#{order_id}</code>\n\n"
        "🚀 تم قبول طلبك تلقائياً — سيتم التنفيذ قريباً.\n"
        "شكراً لثقتك بـ <b>YS | 94</b> ⭐",
        reply_markup=main_menu_keyboard(),
    )

    # ── 4. Notify admin channel ─────────────────────────────
    now          = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username_str = f"@{user.username}" if user.username else "لا يوجد"

    admin_text = (
        "⭐ <b>دفع ناجح بالنجوم — طلب مقبول تلقائياً</b>\n\n"
        f"👤 المستخدم: {user.first_name}\n"
        f"🔖 اليوزر: {username_str}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"⭐ النجوم: <b>{stars_paid} XTR</b>\n"
        f"🔢 رقم الطلب: <code>#{order_id}</code>\n"
        f"📅 التاريخ: {now}\n"
        f"🔑 Charge ID: <code>{charge_id}</code>\n\n"
        "✅ <b>تم قبول الطلب تلقائياً — لا يلزم إجراء يدوي</b>"
    )

    try:
        await bot.send_message(chat_id=ADMIN_CHANNEL_ID, text=admin_text)
    except Exception as exc:
        logger.error(
            "Failed to notify admin channel for Stars payment (order #%s): %s",
            order_id, exc,
        )


# ═══════════════════════════════════════════════════════════
# Path B — Receipt upload (Orange / ila / PayPal)
# ═══════════════════════════════════════════════════════════

@router.message(OrderStates.waiting_for_receipt, F.photo)
async def receive_receipt(message: Message, bot: Bot, state: FSMContext):
    """
    Accept a receipt photo:
      1. Log order to the orders table (status = pending).
      2. Log payment receipt to the payments table.
      3. Forward photo to the admin channel with accept/reject buttons.
      4. Confirm to the user and clear FSM state.
    """
    user    = message.from_user
    data    = await state.get_data()
    service = data.get("selected_service", "غير محدد")
    method  = data.get("payment_method", "غير محدد")

    # 1 — Save order
    order_id = await log_order(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        service=service,
        payment_method=method,
    )

    # 2 — Save receipt metadata
    photo_file_id = message.photo[-1].file_id
    await log_payment(
        order_id=order_id,
        user_id=user.id,
        payment_method=method,
        receipt_file_id=photo_file_id,
    )

    # 3 — Forward to admin channel
    now          = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username_str = f"@{user.username}" if user.username else "لا يوجد"

    admin_caption = (
        "📦 <b>طلب جديد — يحتاج مراجعة</b>\n\n"
        f"👤 المستخدم: {user.first_name}\n"
        f"🔖 اليوزر: {username_str}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📱 الخدمة: {service}\n"
        f"💳 الدفع: {method}\n"
        f"🔢 رقم الطلب: <code>#{order_id}</code>\n"
        f"📅 التاريخ: {now}"
    )

    try:
        await bot.send_photo(
            chat_id=ADMIN_CHANNEL_ID,
            photo=photo_file_id,
            caption=admin_caption,
            reply_markup=admin_action_keyboard(
                order_id=order_id,
                target_user_id=user.id,
            ),
        )
        logger.info(
            "Receipt forwarded to admin channel — order #%s — user %s",
            order_id, user.id,
        )
    except Exception as exc:
        logger.error(
            "Failed to forward receipt to admin channel (order #%s): %s",
            order_id, exc,
        )

    # 4 — Confirm to user
    await message.answer(
        "✅ <b>تم استلام الإيصال بنجاح!</b>\n\n"
        "سيتم مراجعة طلبك من قِبل الإدارة وسنرد عليك قريباً.\n"
        f"رقم طلبك: <code>#{order_id}</code>"
    )
    await state.clear()


# ─────────────────────────────────────────────────────────
# Reject non-photo input while waiting for receipt
# ─────────────────────────────────────────────────────────

@router.message(OrderStates.waiting_for_receipt, ~F.photo)
async def receipt_not_photo(message: Message):
    """Reject any non-photo input while waiting for a receipt."""
    await message.answer(
        "⚠️ يرجى إرسال <b>صورة</b> الإيصال فقط.\n"
        "الملفات والنصوص والفيديوهات غير مقبولة."
    )
