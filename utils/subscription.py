import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from config import SUPPORT_CHANNEL, GIFT_CHANNEL

logger = logging.getLogger(__name__)

# Channels that must be subscribed to before using the bot
REQUIRED_CHANNELS = [SUPPORT_CHANNEL, GIFT_CHANNEL]


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """
    Check whether a user is subscribed to all required channels.
    Returns True if subscribed to all, False otherwise.
    """
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ("left", "kicked", "banned"):
                return False
        except TelegramBadRequest as e:
            logger.warning("Could not check membership for channel %s: %s", channel, e)
            # If we cannot verify, treat as not subscribed to be safe
            return False
        except Exception as e:
            logger.error("Unexpected error checking subscription for %s: %s", channel, e)
            return False
    return True
