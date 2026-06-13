"""
handlers/admin.py — YS | 94 Bot
Permission model
────────────────
  OWNER_ID  → full control of everything
  ADMIN_IDS → access to all admin commands + panel (OWNER always included)
  everyone else → receives ⛔ message when attempting admin commands

Sections
────────
  1. Accept / Reject inline callbacks (admin channel)
  2. Admin panel button callbacks (ap_*) — require IsAdmin
  3. Admin text commands (/admin … /helpadmin) — require IsAdmin
  4. Broadcast FSM handlers — require IsAdmin
  5. Unauthorized catch-all — fires for non-admins (MUST be last)
"""

import asyncio
import logging

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import SUPPORT_CHANNEL, GIFT_CHANNEL, OWNER_ID
from database import (
    get_order_by_id,
    update_order_status,
    get_all_orders,
    get_orders_by_status,
    get_stats,
    get_payment_stats,
    get_all_user_ids,
    get_user_count,
)
from keyboards import admin_panel_keyboard, main_menu_keyboard
from keyboards.callbacks import AdminActionCallback, NavCallback
from states.admin import AdminStates
from utils.admin_filter import IsAdmin, is_owner

router = Router()
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════

def _fmt_order(order: dict) -> str:
    """Format a single order row into a human-readable block."""
    status_icons = {
        "pending":  "⏳ معلق",
        "accepted": "✅ مقبول",
        "rejected": "❌ مرفوض",
    }
    status_label = status_icons.get(order.get("status", ""), order.get("status", "—"))
    username = f"@{order['username']}" if order.get("username") else "—"
    return (
        f"📦 <b>الطلب #{order['id']}</b>\n"
        f"👤 المستخدم: {order.get('first_name', '—')}\n"
        f"🔖 اليوزر: {username}\n"
        f"🆔 ID: <code>{order['user_id']}</code>\n"
        f"📱 الخدمة: {order.get('service', '—')}\n"
        f"💳 الدفع: {order.get('payment_method', '—')}\n"
        f"📊 الحالة: {status_label}\n"
        f"📅 التاريخ: {order.get('created_at', '—')}\n"
        "─────────────────────────"
    )


def _chunk(text: str, size: int = 4096) -> list[str]:
    """Split a long string into Telegram-safe message chunks."""
    return [text[i : i + size] for i in range(0, len(text), size)]


# ═══════════════════════════════════════════════════════════
# 1 — Inline accept / reject callbacks (from admin channel)
# ═══════════════════════════════════════════════════════════

@router.callback_query(AdminActionCallback.filter())
async def handle_admin_action(
    callback: CallbackQuery,
    callback_data: AdminActionCallback,
    bot: Bot,
):
    """Process ✅ / ❌ button presses forwarded to the admin channel."""
    action = callback_data.action
    order_id = callback_data.order_id
    target_user_id = callback_data.target_user_id

    order = await get_order_by_id(order_id)
    if not order:
        await callback.answer("⚠️ الطلب غير موجود في قاعدة البيانات.", show_alert=True)
        return

    if action == "accept":
        await update_order_status(order_id, "accepted")
        user_msg = (
            "✅ <b>تم قبول طلبك بنجاح</b>\n\n"
            "سيتم التنفيذ خلال وقت قصير.\n"
            f"رقم الطلب: <code>#{order_id}</code>"
        )
        admin_feedback = f"✅ تم قبول الطلب #{order_id}"
        logger.info("Order #%s accepted by admin %s", order_id, callback.from_user.id)

    elif action == "reject":
        await update_order_status(order_id, "rejected")
        user_msg = (
            "❌ <b>تم رفض الطلب</b>\n\n"
            "يرجى التواصل مع الدعم الفني.\n"
            f"رقم الطلب: <code>#{order_id}</code>"
        )
        admin_feedback = f"❌ تم رفض الطلب #{order_id}"
        logger.info("Order #%s rejected by admin %s", order_id, callback.from_user.id)

    else:
        await callback.answer("إجراء غير معروف.", show_alert=True)
        return

    try:
        await bot.send_message(chat_id=target_user_id, text=user_msg)
    except Exception as exc:
        logger.error("Failed to notify user %s: %s", target_user_id, exc)
        admin_feedback += " (⚠️ فشل إرسال الإشعار للمستخدم)"

    await callback.answer(admin_feedback, show_alert=True)

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════
# 2 — Admin panel button callbacks (IsAdmin required)
# ═══════════════════════════════════════════════════════════

@router.callback_query(NavCallback.filter(F.dest == "ap_stats"), IsAdmin())
async def panel_stats(callback: CallbackQuery):
    """📊 الإحصائيات button."""
    stats = await get_stats()
    text = (
        "📊 <b>إحصائيات البوت</b>\n\n"
        f"👥 المستخدمون المسجلون: <b>{stats['users']}</b>\n"
        f"📦 إجمالي الطلبات: <b>{stats['total_orders']}</b>\n"
        f"✅ الطلبات المقبولة: <b>{stats['accepted']}</b>\n"
        f"❌ الطلبات المرفوضة: <b>{stats['rejected']}</b>\n"
        f"⏳ الطلبات المعلقة: <b>{stats['pending']}</b>"
    )
    await callback.message.answer(text, reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.callback_query(NavCallback.filter(F.dest == "ap_orders"), IsAdmin())
async def panel_orders(callback: CallbackQuery):
    """📦 الطلبات button."""
    orders = await get_all_orders(limit=20)
    if not orders:
        await callback.message.answer("📭 لا توجد طلبات بعد.", reply_markup=admin_panel_keyboard())
        await callback.answer()
        return
    body = "\n\n".join(_fmt_order(o) for o in orders)
    header = f"📋 <b>آخر {len(orders)} طلب</b>\n\n"
    for chunk in _chunk(header + body):
        await callback.message.answer(chunk)
    await callback.message.answer("↩️ العودة إلى لوحة التحكم:", reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.callback_query(NavCallback.filter(F.dest == "ap_broadcast"), IsAdmin())
async def panel_broadcast(callback: CallbackQuery, state: FSMContext):
    """📢 إذاعة button — starts broadcast FSM."""
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.message.answer(
        "📢 <b>الرسالة الجماعية</b>\n\n"
        "أرسل نص الرسالة التي تريد إرسالها لجميع المستخدمين.\n\n"
        "أرسل /cancel للإلغاء."
    )
    await callback.answer()


@router.callback_query(NavCallback.filter(F.dest == "ap_users"), IsAdmin())
async def panel_users(callback: CallbackQuery):
    """👥 المستخدمين button."""
    count = await get_user_count()
    await callback.message.answer(
        f"👥 <b>المستخدمون المسجلون:</b> <b>{count}</b>",
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer()


@router.callback_query(NavCallback.filter(F.dest == "ap_settings"), IsAdmin())
async def panel_settings(callback: CallbackQuery):
    """⚙️ الإعدادات button — shows current bot configuration."""
    role = "👑 المالك" if is_owner(callback.from_user.id) else "🛡️ مشرف"
    owner_display = f"<code>{OWNER_ID}</code>" if OWNER_ID else "غير مُحدَّد"
    text = (
        "⚙️ <b>إعدادات البوت — YS | 94</b>\n\n"
        f"👤 صلاحيتك: {role}\n"
        f"🔑 OWNER_ID: {owner_display}\n\n"
        "📡 <b>قنوات الاشتراك الإجباري:</b>\n"
        f"  • الدعم الفني: {SUPPORT_CHANNEL}\n"
        f"  • الهدايا: {GIFT_CHANNEL}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>لتغيير الإعدادات، عدّل متغيرات البيئة في Railway وأعد تشغيل البوت.</i>"
    )
    await callback.message.answer(text, reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.callback_query(NavCallback.filter(F.dest == "ap_payments"), IsAdmin())
async def panel_payments(callback: CallbackQuery):
    """💳 المدفوعات button — shows orders grouped by payment method."""
    rows = await get_payment_stats()
    if not rows:
        await callback.message.answer(
            "💳 لا توجد مدفوعات مسجلة بعد.",
            reply_markup=admin_panel_keyboard(),
        )
        await callback.answer()
        return

    lines = ["💳 <b>إحصائيات طرق الدفع</b>\n"]
    for r in rows:
        lines.append(
            f"◈ <b>{r['method']}</b>\n"
            f"  إجمالي: {r['total']} | ✅ {r['accepted']} | ❌ {r['rejected']} | ⏳ {r['pending']}"
        )
    await callback.message.answer("\n".join(lines), reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.callback_query(NavCallback.filter(F.dest == "ap_main_menu"), IsAdmin())
async def panel_main_menu(callback: CallbackQuery):
    """🌐 القائمة الرئيسية button — lets admin browse the user-facing menu."""
    caption = (
        f"مرحباً <b>{callback.from_user.first_name}</b> 👋\n\n"
        "أهلاً بك في بوت <b>YS | 777</b>\n\n"
        "أنت تتصفح القائمة الرئيسية كمشرف.\n"
        "الاشتراك الإجباري مُعطَّل لك."
    )
    await callback.message.answer(caption, reply_markup=main_menu_keyboard())
    await callback.answer()


# ═══════════════════════════════════════════════════════════
# 3 — Admin text commands (IsAdmin required)
# ═══════════════════════════════════════════════════════════

@router.message(Command("admin"), IsAdmin())
async def cmd_admin(message: Message):
    """Show the admin control panel."""
    stats = await get_stats()
    text = (
        "🛡️ <b>لوحة تحكم YS | 94</b>\n\n"
        f"👥 المستخدمون: <b>{stats['users']}</b>\n"
        f"📦 إجمالي الطلبات: <b>{stats['total_orders']}</b>\n"
        f"✅ مقبولة: <b>{stats['accepted']}</b>\n"
        f"❌ مرفوضة: <b>{stats['rejected']}</b>\n"
        f"⏳ معلقة: <b>{stats['pending']}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>الأوامر المتاحة:</b>\n\n"
        "/orders — آخر 20 طلب\n"
        "/pending — الطلبات المعلقة\n"
        "/approved — الطلبات المقبولة\n"
        "/rejected — الطلبات المرفوضة\n"
        "/stats — الإحصائيات الكاملة\n"
        "/broadcast — رسالة جماعية\n"
        "/users — عدد المستخدمين\n"
        "/helpadmin — شرح الأوامر"
    )
    await message.answer(text, reply_markup=admin_panel_keyboard())


@router.message(Command("stats"), IsAdmin())
async def cmd_stats(message: Message):
    """Display full bot statistics."""
    stats = await get_stats()
    text = (
        "📊 <b>إحصائيات البوت</b>\n\n"
        f"👥 المستخدمون المسجلون: <b>{stats['users']}</b>\n"
        f"📦 إجمالي الطلبات: <b>{stats['total_orders']}</b>\n"
        f"✅ الطلبات المقبولة: <b>{stats['accepted']}</b>\n"
        f"❌ الطلبات المرفوضة: <b>{stats['rejected']}</b>\n"
        f"⏳ الطلبات المعلقة: <b>{stats['pending']}</b>"
    )
    await message.answer(text, reply_markup=admin_panel_keyboard())


@router.message(Command("users"), IsAdmin())
async def cmd_users(message: Message):
    """Show total registered user count."""
    count = await get_user_count()
    await message.answer(
        f"👥 <b>المستخدمون المسجلون:</b> {count}",
        reply_markup=admin_panel_keyboard(),
    )


@router.message(Command("orders"), IsAdmin())
async def cmd_orders(message: Message):
    """Show the latest 20 orders (all statuses)."""
    orders = await get_all_orders(limit=20)
    if not orders:
        await message.answer("📭 لا توجد طلبات بعد.")
        return
    body = "\n\n".join(_fmt_order(o) for o in orders)
    header = f"📋 <b>آخر {len(orders)} طلب</b>\n\n"
    for chunk in _chunk(header + body):
        await message.answer(chunk)


@router.message(Command("pending"), IsAdmin())
async def cmd_pending(message: Message):
    """Show latest 20 pending orders."""
    orders = await get_orders_by_status("pending", limit=20)
    if not orders:
        await message.answer("✅ لا توجد طلبات معلقة.")
        return
    body = "\n\n".join(_fmt_order(o) for o in orders)
    header = f"⏳ <b>الطلبات المعلقة ({len(orders)})</b>\n\n"
    for chunk in _chunk(header + body):
        await message.answer(chunk)


@router.message(Command("approved"), IsAdmin())
async def cmd_approved(message: Message):
    """Show latest 20 accepted orders."""
    orders = await get_orders_by_status("accepted", limit=20)
    if not orders:
        await message.answer("📭 لا توجد طلبات مقبولة.")
        return
    body = "\n\n".join(_fmt_order(o) for o in orders)
    header = f"✅ <b>الطلبات المقبولة ({len(orders)})</b>\n\n"
    for chunk in _chunk(header + body):
        await message.answer(chunk)


@router.message(Command("rejected"), IsAdmin())
async def cmd_rejected(message: Message):
    """Show latest 20 rejected orders."""
    orders = await get_orders_by_status("rejected", limit=20)
    if not orders:
        await message.answer("📭 لا توجد طلبات مرفوضة.")
        return
    body = "\n\n".join(_fmt_order(o) for o in orders)
    header = f"❌ <b>الطلبات المرفوضة ({len(orders)})</b>\n\n"
    for chunk in _chunk(header + body):
        await message.answer(chunk)


@router.message(Command("broadcast"), IsAdmin())
async def cmd_broadcast_start(message: Message, state: FSMContext):
    """Begin broadcast flow — ask admin for the message text."""
    await state.set_state(AdminStates.waiting_for_broadcast)
    await message.answer(
        "📢 <b>الرسالة الجماعية</b>\n\n"
        "أرسل نص الرسالة التي تريد إرسالها لجميع المستخدمين.\n\n"
        "أرسل /cancel لإلغاء العملية."
    )


@router.message(Command("helpadmin"), IsAdmin())
async def cmd_helpadmin(message: Message):
    """Show full admin command reference."""
    text = (
        "📖 <b>دليل أوامر الإدارة — YS | 94</b>\n\n"
        "┌ <b>/admin</b>\n"
        "│ عرض لوحة التحكم مع إحصائيات سريعة\n\n"
        "┌ <b>/stats</b>\n"
        "│ إحصائيات تفصيلية: مستخدمون، طلبات، مقبولة، مرفوضة\n\n"
        "┌ <b>/users</b>\n"
        "│ عدد المستخدمين المسجلين في البوت\n\n"
        "┌ <b>/orders</b>\n"
        "│ آخر 20 طلب (جميع الحالات)\n\n"
        "┌ <b>/pending</b>\n"
        "│ آخر 20 طلب معلق ينتظر المراجعة\n\n"
        "┌ <b>/approved</b>\n"
        "│ آخر 20 طلب تمت الموافقة عليه\n\n"
        "┌ <b>/rejected</b>\n"
        "│ آخر 20 طلب تم رفضه\n\n"
        "┌ <b>/broadcast</b>\n"
        "│ إرسال رسالة نصية لجميع المستخدمين\n\n"
        "┌ <b>/helpadmin</b>\n"
        "│ عرض هذا الدليل\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>جميع هذه الأوامر متاحة للمشرفين والمالك فقط.</i>"
    )
    await message.answer(text, reply_markup=admin_panel_keyboard())


# ═══════════════════════════════════════════════════════════
# 4 — Broadcast FSM handlers (IsAdmin required)
# ═══════════════════════════════════════════════════════════

@router.message(AdminStates.waiting_for_broadcast, IsAdmin(), F.text)
async def cmd_broadcast_send(message: Message, bot: Bot, state: FSMContext):
    """Receive broadcast text, send to all users, and report results."""
    await state.clear()
    broadcast_text = message.text.strip()

    if broadcast_text.lower() == "/cancel":
        await message.answer("❌ تم إلغاء الرسالة الجماعية.", reply_markup=admin_panel_keyboard())
        return

    user_ids = await get_all_user_ids()
    if not user_ids:
        await message.answer("📭 لا يوجد مستخدمون مسجلون بعد.", reply_markup=admin_panel_keyboard())
        return

    status_msg = await message.answer(f"⏳ جاري الإرسال إلى {len(user_ids)} مستخدم…")
    success, failed = 0, 0

    for uid in user_ids:
        try:
            await bot.send_message(uid, broadcast_text)
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    logger.info(
        "Broadcast completed by admin %s — success: %s, failed: %s",
        message.from_user.id, success, failed,
    )
    await status_msg.edit_text(
        f"✅ <b>اكتمل الإرسال</b>\n\n"
        f"✔️ نجح: <b>{success}</b>\n"
        f"✖️ فشل: <b>{failed}</b>"
    )
    await message.answer("↩️ العودة:", reply_markup=admin_panel_keyboard())


@router.message(AdminStates.waiting_for_broadcast, IsAdmin(), ~F.text)
async def cmd_broadcast_invalid(message: Message):
    """Reject non-text input during broadcast flow."""
    await message.answer(
        "⚠️ يرجى إرسال نص فقط للرسالة الجماعية، أو أرسل /cancel للإلغاء."
    )


# ═══════════════════════════════════════════════════════════
# 5 — Unauthorized catch-all  ← MUST be registered LAST
#     Fires for non-admin users who attempt admin commands.
#     Because all handlers above carry IsAdmin(), aiogram skips
#     them for non-admins and falls through to this handler.
# ═══════════════════════════════════════════════════════════

@router.message(
    Command(
        "admin", "orders", "pending", "approved",
        "rejected", "stats", "users", "broadcast", "helpadmin",
    )
)
async def unauthorized_admin_cmd(message: Message):
    """Block non-admin users from admin commands."""
    logger.warning(
        "Unauthorized admin command attempt by user %s (%s)",
        message.from_user.id, message.from_user.username or "no-username",
    )
    await message.answer("⛔ ليس لديك صلاحية لاستخدام هذا الأمر.")
