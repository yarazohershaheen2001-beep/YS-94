"""
✳️ YS | Followers — Telegram Bot Entry Point
============================================
Startup sequence:
  1. Load .env via config.py
  2. Configure logging (console + rotating file in logs/)
  3. Validate BOT_TOKEN
  4. Create database directory and init tables
  5. Build Bot + Dispatcher
  6. Register all routers
  7. Start polling

Required env vars (set in .env):
  BOT_TOKEN        ← your Telegram bot token
  ADMIN_CHANNEL_ID ← numeric ID of the private admin channel
  OWNER_ID         ← your personal Telegram user ID
  ADMIN_IDS        ← comma-separated admin user IDs
  GIFT_CHANNEL     ← @shaheen_mall_ys
"""

import asyncio
import logging
import logging.handlers
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, BOT_NAME, ADMIN_IDS
from database import init_db
from handlers import (
    start_router,
    menu_router,
    platforms_router,
    payment_router,
    admin_router,
)


# ── Logging ──────────────────────────────────────────────────────────────────

def _setup_logging() -> None:
    """Configure console + rotating-file logging."""
    os.makedirs("logs", exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    console.setLevel(logging.INFO)

    file_handler = logging.handlers.RotatingFileHandler(
        filename="logs/bot.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.INFO)

    error_handler = logging.handlers.RotatingFileHandler(
        filename="logs/errors.log",
        maxBytes=2 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8",
    )
    error_handler.setFormatter(fmt)
    error_handler.setLevel(logging.ERROR)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(console)
    root.addHandler(file_handler)
    root.addHandler(error_handler)


_setup_logging()
logger = logging.getLogger(__name__)


# ── Main ─────────────────────────────────────────────────────────────────────

async def main() -> None:
    if not BOT_TOKEN:
        logger.error(
            "❌ BOT_TOKEN is not set. "
            "Open .env and set BOT_TOKEN=<your_token>, then restart."
        )
        sys.exit(1)

    if not ADMIN_IDS:
        logger.warning(
            "⚠️  ADMIN_IDS is empty. Admin panel will not be accessible "
            "until you add at least one admin user ID to .env."
        )

    os.makedirs("database", exist_ok=True)
    await init_db()
    logger.info("✅ Database ready.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers — order matters: most-specific first
    dp.include_router(start_router)      # /start — open access, admin panel
    dp.include_router(admin_router)      # admin commands + accept/reject callbacks
    dp.include_router(menu_router)       # main menu navigation
    dp.include_router(platforms_router)  # platform & package selection
    dp.include_router(payment_router)    # payment method + receipt upload

    logger.info("🤖 %s is starting — polling…", BOT_NAME)

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()
        logger.info("🔴 %s stopped.", BOT_NAME)


if __name__ == "__main__":
    asyncio.run(main())
