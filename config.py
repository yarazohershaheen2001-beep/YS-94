# ============================================================
# config.py — ✳️ YS | Followers Bot
# All sensitive values are loaded from the .env file.
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────────────────
# Bot identity
# ──────────────────────────────────────────────────────────
BOT_NAME: str = "✳️ - YS | Followers"

# ──────────────────────────────────────────────────────────
# [BOT_TOKEN] — Your Telegram bot token from @BotFather
# ──────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# ──────────────────────────────────────────────────────────
# [ADMIN_CHANNEL_ID] — Numeric ID of the private admin channel
# ──────────────────────────────────────────────────────────
_raw_channel = os.getenv("ADMIN_CHANNEL_ID", "0")
ADMIN_CHANNEL_ID: int = int(_raw_channel) if _raw_channel.lstrip("-").isdigit() else 0

# ──────────────────────────────────────────────────────────
# [OWNER_ID] — The bot owner's Telegram user ID.
# Has full control — bypasses subscription, sees admin panel.
# ──────────────────────────────────────────────────────────
_raw_owner = os.getenv("OWNER_ID", "0")
OWNER_ID: int = int(_raw_owner) if _raw_owner.isdigit() else 0

# ──────────────────────────────────────────────────────────
# [ADMIN_IDS] — Comma-separated admin user IDs.
# OWNER_ID is always included automatically.
# ──────────────────────────────────────────────────────────
_raw_admin_ids = os.getenv("ADMIN_IDS", "")
_parsed_ids: set[int] = {
    int(x.strip()) for x in _raw_admin_ids.split(",") if x.strip().isdigit()
}
if OWNER_ID:
    _parsed_ids.add(OWNER_ID)
ADMIN_IDS: list[int] = list(_parsed_ids)

# ──────────────────────────────────────────────────────────
# [SUPPORT_CHANNEL] — Support / community channel (kept for admin panel display)
# ──────────────────────────────────────────────────────────
SUPPORT_CHANNEL: str = os.getenv("SUPPORT_CHANNEL", "@shaheen_ys")

# ──────────────────────────────────────────────────────────
# [GIFT_CHANNEL] — Gift / daily-reward channel
# ──────────────────────────────────────────────────────────
GIFT_CHANNEL: str = os.getenv("GIFT_CHANNEL", "@shaheen_mall_ys")

# ──────────────────────────────────────────────────────────
# Media URLs
# ──────────────────────────────────────────────────────────
WELCOME_VIDEO: str   = "https://files.catbox.moe/p8vyoa.mp4"
DEVELOPER_IMAGE: str = "https://files.catbox.moe/szdu73.jpg"

# Platform images
TIKTOK_IMAGE: str    = "https://files.catbox.moe/lsvbmp.png"
INSTAGRAM_IMAGE: str = "https://files.catbox.moe/mez2hy.png"
FACEBOOK_IMAGE: str  = "https://files.catbox.moe/43l9fz.png"
TELEGRAM_IMAGE: str  = "https://files.catbox.moe/ahcn57.png"
SNAPCHAT_IMAGE: str  = "https://files.catbox.moe/pomnzb.png"
YOUTUBE_IMAGE: str   = "https://files.catbox.moe/uxxphc.png"

# Payment images
ORANGE_MONEY_IMAGE: str = "https://files.catbox.moe/s30ogs.png"
ILA_BANK_IMAGE: str     = "https://files.catbox.moe/99w4zi.png"
PAYPAL_IMAGE: str       = "https://files.catbox.moe/9x51br.jpg"
