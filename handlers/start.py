import logging

from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import WELCOME_VIDEO
from database import register_user, get_user_orders
from keyboards import subscription_keyboard, main_menu_keyboard
from keyboards.callbacks import NavCallback
from utils import check_subscription

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    """Entry point — register user, check subscription, then show welcome."""
    user = message.from_user

    # Always register / update user record in the database
    await register_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
    )
    logger.info("User %s (%s) sent /start", user.id, user.username or "no-username")

    subscribed = await check_subscription(bot, user.id)
    if not subscribed:
        await message.answer(
            "⚠️ يجب الاشتراك في القنوات التالية أولاً",
            reply_markup=subscription_keyboard(),
        )
        return

    await _send_welcome(message, user.first_name)


@router.callback_query(NavCallback.filter(F.dest == "check_subscription"))
async def check_sub_callback(callback: CallbackQuery, bot: Bot):
    """Re-check subscription when user presses the verify button."""
    user = callback.from_user
    subscribed = await check_subscription(bot, user.id)

    if not subscribed:
        await callback.answer(
            "❌ لم يتم التحقق. يرجى الاشتراك في القنوات أولاً.",
            show_alert=True,
        )
        return

    await callback.message.delete()
    await _send_welcome(callback.message, user.first_name)
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel the active order at any FSM step and return to the main menu."""
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "ℹ️ لا يوجد طلب نشط حالياً.\n\nيمكنك البدء من القائمة الرئيسية.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await state.clear()
    logger.info("User %s cancelled their active order (was in state: %s)", message.from_user.id, current_state)
    await message.answer(
        "✅ <b>تم إلغاء الطلب بنجاح.</b>\n\n"
        "يمكنك البدء من جديد في أي وقت.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(NavCallback.filter(F.dest == "cancel"))
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Handle the ❌ إلغاء الطلب inline button — mirrors /cancel."""
    current_state = await state.get_state()
    await state.clear()

    if current_state is None:
        await callback.answer("لا يوجد طلب نشط.", show_alert=False)
    else:
        logger.info(
            "User %s cancelled via button (was in state: %s)",
            callback.from_user.id, current_state,
        )

    await callback.message.answer(
        "✅ <b>تم إلغاء الطلب بنجاح.</b>\n\n"
        "يمكنك البدء من جديد في أي وقت.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


def _fmt_user_order(order: dict, index: int) -> str:
    """Format a single order row for the user-facing order history view."""
    status_map = {
        "pending":  "⏳ معلق",
        "accepted": "✅ مقبول",
        "rejected": "❌ مرفوض",
    }
    status_label = status_map.get(order.get("status", ""), "—")
    return (
        f"<b>#{index} — طلب رقم {order['id']}</b>\n"
        f"📱 الخدمة: {order.get('service', '—')}\n"
        f"💳 الدفع: {order.get('payment_method', '—')}\n"
        f"📊 الحالة: {status_label}\n"
        f"📅 التاريخ: {order.get('created_at', '—')}"
    )


@router.message(Command("myorders"))
async def cmd_myorders(message: Message):
    """Show the user's own last 10 orders with statuses."""
    user = message.from_user
    orders = await get_user_orders(user.id, limit=10)

    if not orders:
        await message.answer(
            "📭 <b>لا توجد طلبات مسجلة بعد.</b>\n\n"
            "ابدأ أول طلب الآن من القائمة الرئيسية 👇",
            reply_markup=main_menu_keyboard(),
        )
        return

    lines = [f"📋 <b>سجل طلباتك — آخر {len(orders)} طلب</b>\n"]
    for i, order in enumerate(orders, start=1):
        lines.append(_fmt_user_order(order, i))
        lines.append("─" * 24)

    # Remove the trailing separator
    if lines and lines[-1].startswith("─"):
        lines.pop()

    await message.answer("\n".join(lines))
    logger.info("User %s viewed their order history (%s orders)", user.id, len(orders))


@router.callback_query(NavCallback.filter(F.dest == "my_orders"))
async def my_orders_callback(callback: CallbackQuery):
    """Handle the 📋 طلباتي inline button — mirrors /myorders."""
    user = callback.from_user
    orders = await get_user_orders(user.id, limit=10)

    if not orders:
        await callback.message.answer(
            "📭 <b>لا توجد طلبات مسجلة بعد.</b>\n\n"
            "ابدأ أول طلب الآن من القائمة الرئيسية 👇",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    lines = [f"📋 <b>سجل طلباتك — آخر {len(orders)} طلب</b>\n"]
    for i, order in enumerate(orders, start=1):
        lines.append(_fmt_user_order(order, i))
        lines.append("─" * 24)

    if lines and lines[-1].startswith("─"):
        lines.pop()

    await callback.message.answer("\n".join(lines))
    await callback.answer()
    logger.info("User %s viewed their order history via button (%s orders)", user.id, len(orders))


async def _send_welcome(message: Message, first_name: str):
    """Send the welcome video with caption and main menu keyboard."""
    caption = (
        f"مرحباً <b>{first_name}</b> 👋\n\n"
        "أهلاً بك في بوت <b>YS | 777</b>\n\n"
        "يوفر لك البوت خدمات السوشيال ميديا الاحترافية بأفضل الأسعار.\n\n"
        "اختر الخدمة المناسبة من القائمة بالأسفل."
    )
    try:
        await message.answer_video(
            video=WELCOME_VIDEO,
            caption=caption,
            reply_markup=main_menu_keyboard(),
        )
    except Exception as exc:
        logger.warning("Failed to send welcome video (%s) — falling back to text.", exc)
        await message.answer(caption, reply_markup=main_menu_keyboard())
