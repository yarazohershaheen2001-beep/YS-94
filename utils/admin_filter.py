from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdmin(BaseFilter):
    """
    Passes only when the message sender's user_id is in config.ADMIN_IDS.
    Usage:  @router.message(Command("admin"), IsAdmin())
    """
    async def __call__(self, message: Message) -> bool:
        from config import ADMIN_IDS
        if not ADMIN_IDS:
            return False
        return message.from_user.id in ADMIN_IDS
