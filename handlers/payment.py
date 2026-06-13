import logging
from datetime import datetime

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import (
    ADMIN_CHANNEL_ID,
    ORANGE_MONEY_IMAGE,
    ILA_BANK_IMAGE,
    PAYPAL_IMAGE,
)
from keyboards import payment_methods_keyboard, admin_action_keyboard
from keyboards.callbacks import NavCallback, PaymentMethodCallback
from states import OrderStates
from database import log_order, log_payment

router = Router()
logger = logging.getLogger(__name__)

# Map method key → display name
METHOD_NAMES: dict[str, str] = {
    "orange": "Orange Money 🟠",
    "ila":    "ila bank 🏦",
    "stars":  "شحن نجوم ⭐",
    "paypal": "PayPal 💙",
}

# Map method key → image URL (None = text only)
METHOD_IMAGES: dict[str, str | None] = {
    "orange": ORANGE_MONEY_IMAGE,
    "ila":    ILA_BANK_IMAGE,
    "stars":  None,
    "paypal": PAYPAL_IMAGE,
}


# ─────────────────────────────────────────────────────────
# Show payment methods (user has an active FSM order)
# ─────────────────────────────────────────────────────────

@router.callback_query(NavCallback.filter(F.dest == "payment_methods_select"))
async def show_payment_methods(callback: CallbackQuery, state: FSMContext):
    """Display payment method options when user has a pending order."""
    await callback.message.answer(
        "💳 اختر طريقة الدفع:",
        reply_markup=payment_methods_keyboard(),
    )
    await callback.answer()


# ─────────────────────────────────────────────────────────
# User selects a payment method
# ─────────────────────────────────────────────────────────

@router.callback_query(PaymentMethodCallback.filter(), OrderStates.waiting_for_payment_method)
async def select_payment_method(
    callback: CallbackQuery,
    callback_data: PaymentMethodCallback,
    state: FSMContext,
):
    """Store chosen payment method in FSM and prompt for receipt."""
    method = callback_data.method
    method_name = METHOD_NAMES.get(method, method)
    image_url = METHOD_IMAGES.get(method)

    await state.update_data(payment_method=method_name)
    await state.set_state(OrderStates.waiting_for_receipt)

    # Show payment-method image if one exists
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
    logger.info(
        "User %s selected payment method: %s",
        callback.from_user.id, method_name,
    )
    await callback.answer()


# ─────────────────────────────────────────────────────────
# User uploads receipt photo
# ─────────────────────────────────────────────────────────

@router.message(OrderStates.waiting_for_receipt, F.photo)
async def receive_receipt(message: Message, bot: Bot, state: FSMContext):
    """
    Accept receipt photo:
      1. Log order to the orders table.
      2. Log payment receipt to the payments table.
      3. Forward photo to the admin channel with accept/reject buttons.
      4. Confirm to the user and clear FSM state.
    """
    user = message.from_user
    data = await state.get_data()
    selected_service: str = data.get("selected_service", "غير محدد")
    payment_method: str   = data.get("payment_method", "غير محدد")

    # 1 — Save order
    order_id = await log_order(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        service=selected_service,
        payment_method=payment_method,
    )

    # 2 — Save payment receipt metadata
    photo_file_id = message.photo[-1].file_id
    await log_payment(
        order_id=order_id,
        user_id=user.id,
        payment_method=payment_method,
        receipt_file_id=photo_file_id,
    )

    # 3 — Forward to admin channel
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username_str = f"@{user.username}" if user.username else "لا يوجد"

    admin_caption = (
        "📦 <b>طلب جديد</b>\n\n"
        f"👤 المستخدم: {user.first_name}\n"
        f"🔖 اليوزر: {username_str}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📱 الخدمة: {selected_service}\n"
        f"💳 الدفع: {payment_method}\n"
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
# Non-photo message while waiting for receipt
# ─────────────────────────────────────────────────────────

@router.message(OrderStates.waiting_for_receipt, ~F.photo)
async def receipt_not_photo(message: Message):
    """Reject any non-photo input while waiting for a receipt."""
    await message.answer(
        "⚠️ يرجى إرسال <b>صورة</b> الإيصال فقط.\n"
        "الملفات والنصوص والفيديوهات غير مقبولة."
    )
