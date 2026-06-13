"""
database/db.py — YS | 94 Bot
Async SQLite helpers using aiosqlite.

Tables
------
users    — one row per Telegram user who started the bot
orders   — one row per placed order (after receipt upload)
payments — one row per payment attempt (receipt photo metadata)
"""

import aiosqlite
import logging
from datetime import datetime

DB_PATH = "database/orders.db"
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────
# Init
# ──────────────────────────────────────────────────────────

async def init_db() -> None:
    """Create all tables if they do not yet exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER PRIMARY KEY,
                username   TEXT,
                first_name TEXT,
                created_at TEXT NOT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                username       TEXT,
                first_name     TEXT,
                service        TEXT NOT NULL,
                payment_method TEXT,
                status         TEXT NOT NULL DEFAULT 'pending',
                created_at     TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id        INTEGER NOT NULL,
                user_id         INTEGER NOT NULL,
                payment_method  TEXT NOT NULL,
                receipt_file_id TEXT NOT NULL,
                created_at      TEXT NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """)

        await db.commit()
    logger.info("Database initialized — tables ready.")


# ──────────────────────────────────────────────────────────
# Users
# ──────────────────────────────────────────────────────────

async def register_user(user_id: int, username: str, first_name: str) -> None:
    """Insert a new user or ignore if already registered (upsert by user_id)."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, first_name, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username   = excluded.username,
                first_name = excluded.first_name
            """,
            (user_id, username or "", first_name or "", created_at),
        )
        await db.commit()


async def get_user_count() -> int:
    """Return the total number of registered users."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_all_user_ids() -> list[int]:
    """Return all registered user IDs (for broadcast)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]


# ──────────────────────────────────────────────────────────
# Orders
# ──────────────────────────────────────────────────────────

async def log_order(
    user_id: int,
    username: str,
    first_name: str,
    service: str,
    payment_method: str,
) -> int:
    """Insert a new order and return its auto-generated ID."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO orders
                (user_id, username, first_name, service, payment_method, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """,
            (user_id, username or "", first_name or "", service, payment_method, created_at),
        )
        await db.commit()
        order_id = cursor.lastrowid
    logger.info("New order #%s logged — user %s — %s", order_id, user_id, service)
    return order_id


async def log_payment(
    order_id: int,
    user_id: int,
    payment_method: str,
    receipt_file_id: str,
) -> None:
    """Record a payment receipt upload."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO payments
                (order_id, user_id, payment_method, receipt_file_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, user_id, payment_method, receipt_file_id, created_at),
        )
        await db.commit()
    logger.info("Payment receipt logged — order #%s — method: %s", order_id, payment_method)


async def get_user_orders(user_id: int, limit: int = 10) -> list[dict]:
    """Return the latest N orders placed by a specific user (newest first)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_order_by_id(order_id: int) -> dict | None:
    """Fetch a single order row by primary key."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def update_order_status(order_id: int, status: str) -> None:
    """Update order status: 'accepted' | 'rejected'."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id),
        )
        await db.commit()
    logger.info("Order #%s status updated to '%s'", order_id, status)


async def get_all_orders(limit: int = 20) -> list[dict]:
    """Return the latest N orders (newest first)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_orders_by_status(status: str, limit: int = 20) -> list[dict]:
    """Return the latest N orders filtered by status."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE status = ? ORDER BY id DESC LIMIT ?",
            (status, limit),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


# ──────────────────────────────────────────────────────────
# Statistics
# ──────────────────────────────────────────────────────────

async def get_payment_stats() -> list[dict]:
    """Return order counts grouped by payment method."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT
                payment_method,
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) AS accepted,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS rejected,
                SUM(CASE WHEN status = 'pending'  THEN 1 ELSE 0 END) AS pending
            FROM orders
            GROUP BY payment_method
            ORDER BY total DESC
        """) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "method":   r[0] or "غير محدد",
                    "total":    r[1],
                    "accepted": r[2],
                    "rejected": r[3],
                    "pending":  r[4],
                }
                for r in rows
            ]


async def get_stats() -> dict:
    """Return a summary dict with user and order counts."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            user_count = (await cur.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM orders") as cur:
            total_orders = (await cur.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM orders WHERE status = 'accepted'"
        ) as cur:
            accepted = (await cur.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM orders WHERE status = 'rejected'"
        ) as cur:
            rejected = (await cur.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM orders WHERE status = 'pending'"
        ) as cur:
            pending = (await cur.fetchone())[0]

    return {
        "users": user_count,
        "total_orders": total_orders,
        "accepted": accepted,
        "rejected": rejected,
        "pending": pending,
    }
