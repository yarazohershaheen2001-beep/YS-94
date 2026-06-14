"""
utils/subscription.py — YS | 94 Bot

Whitelist-based subscription checker.
Only statuses in SUBSCRIBED_STATUSES count as "subscribed".
Returns (True, None) on success, (False, channel) on failure.
Owner / Admin IDs bypass the check entirely.
"""

import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from config import SUPPORT_CHANNEL, GIFT_CHANNEL

logger = logging.getLogger(__name__)

# Channels the user must be subscribed to
REQUIRED_CHANNELS: list[str] = [SUPPORT_CHANNEL, GIFT_CHANNEL]

# ✅ Whitelist — only these statuses are considered "subscribed"
SUBSCRIBED_STATUSES: frozenset[str] = frozenset({"member", "administrator", "creator"})


async def check_subscription(bot: Bot, user_id: int) -> tuple[bool, str | None]:
    """
    Verify the user is subscribed to every channel in REQUIRED_CHANNELS.

    Returns
    -------
    (True,  None)        — subscribed to all channels
    (False, channel_id)  — not subscribed; channel_id is the first failing channel

    Notes
    -----
    • The bot MUST be an admin in each channel for getChatMember to work.
    • Owner / Admin bypass is handled by callers (handlers/start.py) before
      this function is ever called, so no duplicate import is needed here.
    • Statuses checked: member | administrator | creator  → ✅ subscribed
      Everything else (left, kicked, restricted, …)      → ❌ not subscribed
    """
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            status = member.status

            subscribed = status in SUBSCRIBED_STATUSES

            logger.info(
                "Sub-check | user=%s | channel=%s | status=%s | result=%s",
                user_id,
                channel,
                status,
                "✅ مشترك" if subscribed else "❌ غير مشترك",
            )

            if not subscribed:
                logger.warning(
                    "Sub-check FAILED | user=%s blocked on channel=%s (status=%s)",
                    user_id, channel, status,
                )
                return False, channel

        except TelegramForbiddenError as exc:
            # Bot is not admin in the channel — cannot verify membership
            logger.error(
                "Sub-check ERROR | bot has no admin rights in channel=%s: %s",
                channel, exc,
            )
            return False, channel

        except TelegramBadRequest as exc:
            logger.warning(
                "Sub-check BAD REQUEST | channel=%s | user=%s: %s",
                channel, user_id, exc,
            )
            return False, channel

        except Exception as exc:
            logger.error(
                "Sub-check UNEXPECTED ERROR | channel=%s | user=%s: %s",
                channel, user_id, exc,
            )
            return False, channel

    logger.info("Sub-check PASSED | user=%s — subscribed to all channels.", user_id)
    return True, None
