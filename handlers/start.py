import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import WELCOME_VIDEO, BOT_NAME
from database import register_user, get_user_orders
from keyboards import main_menu_keyboard, admin_panel_keyboard
from keyboards.callbacks import NavCallback
from utils import is_admin, is_owner

router = Router()
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# /start — open access (no mandatory subscription)
# ═══════════════════════════════════════════════════════════

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Entry point — no subscription gate.
      • Owner / Admin  → admin control panel.
      • Any other user → welcome video + main menu.
    """
    user = message.from_user

    await register_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
    )
    logger.info("User %s (%s) sent /start", user.id, user.username or "no-username")

    if is_admin(user.id):
        await _send_admin_welcome(message, user.first_name or "مشرف")
    else:
        await _send_welcome(message, user.first_name or "صديقي")


# ═══════════════════════════════════════════════════════════
# /cancel — exit any active FSM state
# ═══════════════════════════════════════════════════════════

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
    logger.info(
        "User %s cancelled their active order (was in state: %s)",
        message.from_user.id, current_state,
    )
    await message.answer(
        "✅ <b>تم إلغاء الطلب بنجاح.</b>\n\nيمكنك البدء من جديد في أي وقت.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(NavCallback.filter(F.dest == "cancel"))
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Handle the ❌ إلغاء الطلب inline button."""
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
        "✅ <b>تم إلغاء الطلب بنجاح.</b>\n\nيمكنك البدء من جديد في أي وقت.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


# ═══════════════════════════════════════════════════════════
# /myorders — user order history
# ═══════════════════════════════════════════════════════════

def _fmt_user_order(order: dict, index: int) -> str:
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
    user = message.from_user
    orders = await get_user_orders(user.id, limit=10)

    if not orders:
        await message.answer(
            "📭 <b>لا توجد طلبات مسجلة بعد.</b>\n\nابدأ أول طلب الآن من القائمة الرئيسية 👇",
            reply_markup=main_menu_keyboard(),
        )
        return

    lines = [f"📋 <b>سجل طلباتك — آخر {len(orders)} طلب</b>\n"]
    for i, order in enumerate(orders, start=1):
        lines.append(_fmt_user_order(order, i))
        lines.append("─" * 24)
    if lines[-1].startswith("─"):
        lines.pop()

    await message.answer("\n".join(lines))
    logger.info("User %s viewed their order history (%s orders)", user.id, len(orders))


@router.callback_query(NavCallback.filter(F.dest == "my_orders"))
async def my_orders_callback(callback: CallbackQuery):
    user = callback.from_user
    orders = await get_user_orders(user.id, limit=10)

    if not orders:
        await callback.message.answer(
            "📭 <b>لا توجد طلبات مسجلة بعد.</b>\n\nابدأ أول طلب الآن من القائمة الرئيسية 👇",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    lines = [f"📋 <b>سجل طلباتك — آخر {len(orders)} طلب</b>\n"]
    for i, order in enumerate(orders, start=1):
        lines.append(_fmt_user_order(order, i))
        lines.append("─" * 24)
    if lines[-1].startswith("─"):
        lines.pop()

    await callback.message.answer("\n".join(lines))
    await callback.answer()
    logger.info("User %s viewed order history via button (%s orders)", user.id, len(orders))


# ═══════════════════════════════════════════════════════════
# Private helpers
# ═══════════════════════════════════════════════════════════

async def _send_welcome(message: Message, first_name: str):
    """Send the welcome video + main menu to any user (no subscription gate)."""
    caption = (
        f"مرحباً <b>{first_name}</b> 👋\n\n"
        f"أهلاً بك في <b>{BOT_NAME}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌟 المتجر الاحترافي لخدمات السوشيال ميديا\n\n"
        "📱 <b>خدماتنا المتاحة:</b>\n"
        "• زيادة المتابعين والمشتركين\n"
        "• زيادة المشاهدات والإعجابات\n"
        "• جميع المنصات: TikTok · Instagram · YouTube\n"
        "  Facebook · Snapchat · Telegram\n\n"
        "💎 أسعار تنافسية وجودة مضمونة\n"
        "⚡ تنفيذ سريع بعد تأكيد الطلب\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "اختر الخدمة المناسبة من القائمة أدناه 👇"
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


async def _send_admin_welcome(message: Message, first_name: str):
    """Send the admin control panel to owner / admins."""
    user_id = message.from_user.id if message.from_user else 0
    role    = "👑 المالك" if is_owner(user_id) else "🛡️ مشرف"

    text = (
        f"مرحباً <b>{first_name}</b> — {role}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔐 <b>{BOT_NAME}</b> — وضع الإدارة\n\n"
        "الاشتراك الإجباري: <b>مُعطَّل</b>\n"
        "صلاحياتك: <b>كاملة</b>\n\n"
        "اختر من لوحة التحكم أدناه:"
    )
    await message.answer(text, reply_markup=admin_panel_keyboard())
    logger.info("Admin/Owner %s (%s) accessed the control panel.", user_id, role)
