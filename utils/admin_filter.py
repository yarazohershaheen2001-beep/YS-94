"""
utils/admin_filter.py — YS | 94 Bot
Permission helpers and aiogram filters for owner / admin checks.

Hierarchy
─────────
  OWNER_ID  — full control, always bypasses subscription
  ADMIN_IDS — subset of elevated users (OWNER_ID always included)
  everyone else — regular users, full subscription gate
"""

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message


# ──────────────────────────────────────────────────────────
# Pure helper functions (callable anywhere without aiogram)
# ──────────────────────────────────────────────────────────

def is_owner(user_id: int) -> bool:
    """Return True if user_id matches the configured OWNER_ID."""
    from config import OWNER_ID
    return bool(OWNER_ID) and user_id == OWNER_ID


def is_admin(user_id: int) -> bool:
    """Return True if user_id is the owner OR appears in ADMIN_IDS."""
    from config import OWNER_ID, ADMIN_IDS
    return user_id == OWNER_ID or user_id in ADMIN_IDS


# ──────────────────────────────────────────────────────────
# Aiogram filters (work on both Message and CallbackQuery)
# ──────────────────────────────────────────────────────────

class IsOwner(BaseFilter):
    """
    Passes only for the bot owner (OWNER_ID).
    Usage:  @router.message(Command("owneronly"), IsOwner())
    """
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return is_owner(event.from_user.id)


class IsAdmin(BaseFilter):
    """
    Passes for the owner AND any user in ADMIN_IDS.
    Usage:  @router.message(Command("admin"), IsAdmin())
            @router.callback_query(SomeCallback.filter(), IsAdmin())
    """
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return is_admin(event.from_user.id)
