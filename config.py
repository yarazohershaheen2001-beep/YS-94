# ============================================================
# config.py — YS | 94 Bot
# All sensitive values are loaded from the .env file.
# ============================================================
import os
from dotenv import load_dotenv

# Load .env into the environment (safe no-op if file is absent)
load_dotenv()

# ──────────────────────────────────────────────────────────
# [BOT_TOKEN] — Your Telegram bot token from @BotFather
# ──────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# ──────────────────────────────────────────────────────────
# [ADMIN_CHANNEL_ID] — Numeric ID of the private admin channel
# where order receipts are forwarded (e.g. -1001234567890)
# ──────────────────────────────────────────────────────────
_raw_channel = os.getenv("ADMIN_CHANNEL_ID", "0")
ADMIN_CHANNEL_ID: int = int(_raw_channel) if _raw_channel.lstrip("-").isdigit() else 0

# ──────────────────────────────────────────────────────────
# [ADMIN_IDS] — Comma-separated Telegram user IDs that have
# access to admin commands (e.g. "123456789,987654321")
# ──────────────────────────────────────────────────────────
_raw_admin_ids = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in _raw_admin_ids.split(",") if x.strip().isdigit()
]

# ──────────────────────────────────────────────────────────
# [SUPPORT_CHANNEL] — Mandatory subscription channel username
# ──────────────────────────────────────────────────────────
SUPPORT_CHANNEL: str = os.getenv("SUPPORT_CHANNEL", "@shaheen_ys")

# ──────────────────────────────────────────────────────────
# [GIFT_CHANNEL] — Mandatory subscription channel username
# ──────────────────────────────────────────────────────────
GIFT_CHANNEL: str = os.getenv("GIFT_CHANNEL", "@fi1_oo")

# ──────────────────────────────────────────────────────────
# Media URLs
# ──────────────────────────────────────────────────────────

# [WELCOME_VIDEO] — Intro video sent on /start
WELCOME_VIDEO: str = "https://files.catbox.moe/w62q88.mp4"

# [DEVELOPER_IMAGE] — Photo shown on the developer profile screen
DEVELOPER_IMAGE: str = "https://files.catbox.moe/szdu73.jpg"

# ──────────────────────────────────────────────────────────
# Platform image URLs
# ──────────────────────────────────────────────────────────
TIKTOK_IMAGE: str    = "https://files.catbox.moe/lsvbmp.png"
INSTAGRAM_IMAGE: str = "https://files.catbox.moe/mez2hy.png"
FACEBOOK_IMAGE: str  = "https://files.catbox.moe/43l9fz.png"
TELEGRAM_IMAGE: str  = "https://files.catbox.moe/ahcn57.png"
SNAPCHAT_IMAGE: str  = "https://files.catbox.moe/pomnzb.png"
YOUTUBE_IMAGE: str   = "https://files.catbox.moe/uxxphc.png"

# ──────────────────────────────────────────────────────────
# Payment method image URLs
# ──────────────────────────────────────────────────────────
ORANGE_MONEY_IMAGE: str = "https://files.catbox.moe/s30ogs.png"
ILA_BANK_IMAGE: str     = "https://files.catbox.moe/99w4zi.png"
PAYPAL_IMAGE: str       = "https://files.catbox.moe/9x51br.jpg"
