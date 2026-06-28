import aiosqlite
import asyncio
from datetime import datetime

DB_PATH = "bot.db"

_conn: aiosqlite.Connection = None


class _DBCtx:
    async def __aenter__(self):
        return _conn
    async def __aexit__(self, *_):
        pass


def get_db() -> _DBCtx:
    return _DBCtx()


async def init_db():
    global _conn
    _conn = await aiosqlite.connect(DB_PATH)
    _conn.row_factory = aiosqlite.Row
    db = _conn
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    await db.execute("PRAGMA synchronous=NORMAL")
    await db.execute("PRAGMA cache_size=10000")
    await db.execute("PRAGMA temp_store=MEMORY")

    await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                username TEXT,
                balance REAL DEFAULT 0.0,
                total_orders INTEGER DEFAULT 0,
                ref_by INTEGER DEFAULT NULL,
                referrals_count INTEGER DEFAULT 0,
                referral_earnings REAL DEFAULT 0.0,
                is_banned INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            provider_type TEXT DEFAULT 'smm_v2',
            api_url TEXT NOT NULL,
            api_key TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            last_check_status TEXT DEFAULT '',
            last_check_message TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    # Migrations for existing databases
    for col, default in [
        ("provider_type", "'smm_v2'"),
        ("last_check_status", "''"),
        ("last_check_message", "''"),
    ]:
        try:
            await db.execute(f"ALTER TABLE providers ADD COLUMN {col} TEXT DEFAULT {default}")
        except Exception:
            pass

    await db.execute("""
        CREATE TABLE IF NOT EXISTS services_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_id INTEGER NOT NULL,
            provider_name TEXT NOT NULL,
            provider_service_id TEXT NOT NULL,
            platform TEXT,
            category TEXT,
            original_name TEXT,
            arabic_name TEXT,
            rate REAL,
            final_rate REAL,
            min INTEGER,
            max INTEGER,
            status TEXT DEFAULT 'active',
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (provider_id) REFERENCES providers(id)
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            provider_id INTEGER,
            provider_name TEXT,
            provider_order_id TEXT,
            service_id INTEGER,
            service_name TEXT,
            link TEXT,
            quantity INTEGER,
            price REAL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS manual_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS manual_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            instructions TEXT,
            required_data_type TEXT DEFAULT 'text',
            price REAL NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES manual_categories(id)
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS manual_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id INTEGER,
            service_name TEXT,
            user_data TEXT,
            price REAL,
            status TEXT DEFAULT 'pending',
            admin_response TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL,
            method TEXT,
            network TEXT,
            wallet_address TEXT,
            proof_photo_id TEXT,
            status TEXT DEFAULT 'pending',
            admin_note TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user INTEGER NOT NULL,
            to_user INTEGER NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_id INTEGER NOT NULL UNIQUE,
            bonus REAL DEFAULT 0.0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS balance_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            operation_type TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS virtual_number_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fivesim_order_id INTEGER NOT NULL,
            phone TEXT,
            country TEXT,
            product TEXT,
            operator TEXT DEFAULT 'any',
            cost REAL DEFAULT 0.0,
            status TEXT DEFAULT 'PENDING',
            sms_code TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    default_settings = [
        ("force_subscription_enabled", "1"),
        ("channel_username", "@YourChannel"),
        ("channel_link", "https://t.me/YourChannel"),
        ("profit_percent", "10"),
        ("referral_bonus", "0.01"),
        ("stars_rate", "77"),
        ("support_username", "@YourSupportUsername"),
        ("wallet_btc", "bc1qxjdvlrez3ehf96pxwhdyaeg8s987pvdlehz3r9"),
        ("wallet_usdt_bep20", "0x4DA3761310D9a528aAb475079f2ED4b0F2ef9840"),
        ("wallet_ton_gram", "UQC9Dr6duL1IY8AJLjanwWKbMzjFj8Q-aFCGSSqo8PdahbFa"),
        ("wallet_ltc", "ltc1qxjdvlrez3ehf96pxwhdyaeg8s987pvdlatc4m4"),
        ("wallet_sol", "CEG5wLF2Y4nAkTf8gp9N4Y5Rjc7b8dyDmwsKTvy7cknx"),
    ]
    for key, val in default_settings:
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, val)
        )

    await db.commit()


async def get_setting(key: str, default=None):
    async with get_db() as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else default


async def set_setting(key: str, value: str):
    async with get_db() as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, str(value))
        )
        await db.commit()


async def add_user(user_id: int, full_name: str, username: str, ref_by: int = None):
    async with get_db() as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, full_name, username, ref_by)
            VALUES (?, ?, ?, ?)
        """, (user_id, full_name, username, ref_by))
        await db.commit()


async def get_user(user_id: int):
    async with get_db() as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchone()


async def get_all_users():
    async with get_db() as db:
        async with db.execute("SELECT * FROM users ORDER BY created_at DESC") as cur:
            return await cur.fetchall()


async def get_users_paginated(offset: int = 0, limit: int = 10):
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ) as cur:
            rows = await cur.fetchall()
        async with db.execute("SELECT COUNT(*) FROM users") as cur2:
            total = (await cur2.fetchone())[0]
        return rows, total


async def search_user_by_id(user_id: int):
    async with get_db() as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchone()


async def get_user_balance(user_id: int) -> float:
    async with get_db() as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0.0


async def add_balance(user_id: int, amount: float, description: str = ""):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.execute(
            "INSERT INTO balance_operations (user_id, amount, operation_type, description) VALUES (?, ?, 'add', ?)",
            (user_id, amount, description)
        )
        await db.commit()


async def deduct_balance(user_id: int, amount: float, description: str = "") -> bool:
    async with get_db() as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row or row[0] < amount:
            return False
        await db.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.execute(
            "INSERT INTO balance_operations (user_id, amount, operation_type, description) VALUES (?, ?, 'deduct', ?)",
            (user_id, amount, description)
        )
        await db.commit()
        return True


async def deduct_balance_atomic(user_id: int, amount: float, description: str = "") -> bool:
    """
    خصم ذري باستخدام UPDATE واحد مع WHERE balance >= amount.
    يمنع نهائياً حالة TOCTOU (قراءة ثم تعديل منفصلَين).
    يضمن عدم الوصول إلى رصيد سالب حتى مع طلبات متزامنة.
    """
    async with get_db() as db:
        cur = await db.execute(
            "UPDATE users SET balance = ROUND(balance - ?, 8) "
            "WHERE user_id = ? AND balance >= ?",
            (amount, user_id, amount),
        )
        if cur.rowcount == 0:
            return False
        await db.execute(
            "INSERT INTO balance_operations (user_id, amount, operation_type, description) "
            "VALUES (?, ?, 'deduct', ?)",
            (user_id, amount, description),
        )
        await db.commit()
        return True


async def create_order_pending(
    user_id: int, provider_id: int, provider_name: str,
    service_id: int, service_name: str,
    link: str, quantity: int, price: float,
) -> int:
    """
    أنشئ سجل طلب بحالة PENDING قبل استدعاء API المورد.
    يضمن وجود سجل قابل للاسترجاع حتى لو انقطع الاتصال بعد الخصم.
    """
    async with get_db() as db:
        cur = await db.execute(
            """INSERT INTO orders
               (user_id, provider_id, provider_name, provider_order_id,
                service_id, service_name, link, quantity, price, status)
               VALUES (?, ?, ?, '', ?, ?, ?, ?, ?, 'pending')""",
            (user_id, provider_id, provider_name, service_id, service_name,
             link, quantity, price),
        )
        await db.execute(
            "UPDATE users SET total_orders = total_orders + 1 WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()
        return cur.lastrowid


async def refund_order(order_id: int, user_id: int, amount: float, reason: str = "") -> None:
    """
    يُرجع المبلغ للمستخدم ويضع حالة الطلب REFUNDED في عملية ذرية واحدة.
    يُستدعى فقط عند فشل API المورد أو خطأ غير متوقع بعد الخصم.
    """
    desc = reason or f"استرجاع تلقائي للطلب #{order_id}"
    async with get_db() as db:
        await db.execute(
            "UPDATE orders SET status = 'refunded', updated_at = datetime('now') "
            "WHERE id = ? AND user_id = ?",
            (order_id, user_id),
        )
        await db.execute(
            "UPDATE users SET balance = ROUND(balance + ?, 8) WHERE user_id = ?",
            (amount, user_id),
        )
        await db.execute(
            "INSERT INTO balance_operations (user_id, amount, operation_type, description) "
            "VALUES (?, ?, 'refund', ?)",
            (user_id, amount, desc),
        )
        await db.commit()


async def set_balance(user_id: int, amount: float):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET balance = ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def ban_user(user_id: int):
    async with get_db() as db:
        await db.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()


async def unban_user(user_id: int):
    async with get_db() as db:
        await db.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
        await db.commit()


async def get_user_orders_count(user_id: int) -> int:
    async with get_db() as db:
        async with db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,)
        ) as cur:
            r = await cur.fetchone()
            c1 = r[0] if r else 0
        async with db.execute(
            "SELECT COUNT(*) FROM manual_orders WHERE user_id = ?", (user_id,)
        ) as cur:
            r2 = await cur.fetchone()
            c2 = r2[0] if r2 else 0
        return c1 + c2


async def create_referral(referrer_id: int, referred_id: int, bonus: float):
    async with get_db() as db:
        try:
            await db.execute(
                "INSERT OR IGNORE INTO referrals (referrer_id, referred_id, bonus) VALUES (?, ?, ?)",
                (referrer_id, referred_id, bonus)
            )
            await db.execute(
                "UPDATE users SET referrals_count = referrals_count + 1 WHERE user_id = ?",
                (referrer_id,)
            )
            await db.commit()
            return True
        except Exception:
            return False


async def add_referral_bonus(referrer_id: int, bonus: float):
    async with get_db() as db:
        await db.execute(
            "UPDATE users SET referral_earnings = referral_earnings + ?, balance = balance + ? WHERE user_id = ?",
            (bonus, bonus, referrer_id)
        )
        await db.execute(
            "INSERT INTO balance_operations (user_id, amount, operation_type, description) VALUES (?, ?, 'add', 'مكافأة الإحالة')",
            (referrer_id, bonus)
        )
        await db.commit()


async def get_referral_stats(user_id: int):
    async with get_db() as db:
        async with db.execute(
            "SELECT COUNT(*), SUM(bonus) FROM referrals WHERE referrer_id = ?",
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return {"count": row[0] or 0, "earnings": row[1] or 0.0}


async def add_provider(name: str, api_url: str, api_key: str, provider_type: str = "smm_v2") -> int:
    async with get_db() as db:
        cur = await db.execute(
            "INSERT INTO providers (name, provider_type, api_url, api_key) VALUES (?, ?, ?, ?)",
            (name, provider_type, api_url, api_key)
        )
        await db.commit()
        return cur.lastrowid


async def update_provider(provider_id: int, name: str = None, api_url: str = None,
                           api_key: str = None, provider_type: str = None,
                           last_check_status: str = None, last_check_message: str = None):
    async with get_db() as db:
        fields = {"name": name, "api_url": api_url, "api_key": api_key,
                  "provider_type": provider_type, "last_check_status": last_check_status,
                  "last_check_message": last_check_message}
        for field, value in fields.items():
            if value is not None:
                await db.execute(
                    f"UPDATE providers SET {field} = ?, updated_at = datetime('now') WHERE id = ?",
                    (value, provider_id)
                )
        await db.commit()


async def delete_provider(provider_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM providers WHERE id = ?", (provider_id,))
        await db.commit()


async def toggle_provider(provider_id: int):
    async with get_db() as db:
        await db.execute(
            "UPDATE providers SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END, updated_at = datetime('now') WHERE id = ?",
            (provider_id,)
        )
        await db.commit()


async def get_active_providers():
    async with get_db() as db:
        async with db.execute("SELECT * FROM providers WHERE is_active = 1") as cur:
            return await cur.fetchall()


async def get_all_providers():
    async with get_db() as db:
        async with db.execute("SELECT * FROM providers ORDER BY id") as cur:
            return await cur.fetchall()


async def get_provider(provider_id: int):
    async with get_db() as db:
        async with db.execute("SELECT * FROM providers WHERE id = ?", (provider_id,)) as cur:
            return await cur.fetchone()


async def save_services_cache(services: list):
    async with get_db() as db:
        for s in services:
            await db.execute("""
                INSERT INTO services_cache
                (provider_id, provider_name, provider_service_id, platform, category,
                 original_name, arabic_name, rate, final_rate, min, max, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                s.get("provider_id"),
                s.get("provider_name"),
                s.get("provider_service_id"),
                s.get("platform"),
                s.get("category"),
                s.get("original_name"),
                s.get("arabic_name"),
                s.get("rate"),
                s.get("final_rate"),
                s.get("min"),
                s.get("max"),
                s.get("status", "active"),
            ))
        await db.commit()


async def clear_services_cache():
    async with get_db() as db:
        await db.execute("DELETE FROM services_cache")
        await db.commit()


async def clear_services_by_provider(provider_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM services_cache WHERE provider_id = ?", (provider_id,))
        await db.commit()


async def get_services_by_platform_category(platform: str, category: str, offset: int = 0, limit: int = 6):
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM services_cache WHERE platform = ? AND category = ? AND status = 'active' LIMIT ? OFFSET ?",
            (platform, category, limit, offset)
        ) as cur:
            rows = await cur.fetchall()
        async with db.execute(
            "SELECT COUNT(*) FROM services_cache WHERE platform = ? AND category = ? AND status = 'active'",
            (platform, category)
        ) as cur2:
            total = (await cur2.fetchone())[0]
        return rows, total


async def get_distinct_categories_for_platform(platform: str):
    async with get_db() as db:
        async with db.execute(
            "SELECT DISTINCT category FROM services_cache WHERE platform = ? AND status = 'active' ORDER BY category",
            (platform,)
        ) as cur:
            rows = await cur.fetchall()
        return [r[0] for r in rows if r[0]]


async def get_service_by_id(service_id: int):
    async with get_db() as db:
        async with db.execute("SELECT * FROM services_cache WHERE id = ?", (service_id,)) as cur:
            return await cur.fetchone()


async def create_order(user_id: int, provider_id: int, provider_name: str,
                       provider_order_id: str, service_id: int, service_name: str,
                       link: str, quantity: int, price: float) -> int:
    async with get_db() as db:
        cur = await db.execute("""
            INSERT INTO orders
            (user_id, provider_id, provider_name, provider_order_id, service_id, service_name, link, quantity, price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (user_id, provider_id, provider_name, provider_order_id, service_id, service_name, link, quantity, price))
        await db.execute(
            "UPDATE users SET total_orders = total_orders + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()
        return cur.lastrowid


async def update_order_status(order_id: int, status: str, provider_order_id: str = None):
    async with get_db() as db:
        if provider_order_id:
            await db.execute(
                "UPDATE orders SET status = ?, provider_order_id = ?, updated_at = datetime('now') WHERE id = ?",
                (status, provider_order_id, order_id)
            )
        else:
            await db.execute(
                "UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?",
                (status, order_id)
            )
        await db.commit()


async def get_user_orders(user_id: int, limit: int = 10):
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ) as cur:
            return await cur.fetchall()


async def get_order_by_id(order_id: int):
    async with get_db() as db:
        async with db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)) as cur:
            return await cur.fetchone()


async def create_manual_category(name: str) -> int:
    async with get_db() as db:
        cur = await db.execute("INSERT INTO manual_categories (name) VALUES (?)", (name,))
        await db.commit()
        return cur.lastrowid


async def update_manual_category(cat_id: int, name: str):
    async with get_db() as db:
        await db.execute("UPDATE manual_categories SET name = ? WHERE id = ?", (name, cat_id))
        await db.commit()


async def delete_manual_category(cat_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM manual_services WHERE category_id = ?", (cat_id,))
        await db.execute("DELETE FROM manual_categories WHERE id = ?", (cat_id,))
        await db.commit()


async def toggle_manual_category(cat_id: int):
    async with get_db() as db:
        await db.execute(
            "UPDATE manual_categories SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?",
            (cat_id,)
        )
        await db.commit()


async def get_manual_categories(active_only: bool = True):
    async with get_db() as db:
        if active_only:
            async with db.execute("SELECT * FROM manual_categories WHERE is_active = 1 ORDER BY id") as cur:
                return await cur.fetchall()
        else:
            async with db.execute("SELECT * FROM manual_categories ORDER BY id") as cur:
                return await cur.fetchall()


async def create_manual_service(category_id: int, name: str, description: str,
                                 instructions: str, required_data_type: str, price: float) -> int:
    async with get_db() as db:
        cur = await db.execute("""
            INSERT INTO manual_services (category_id, name, description, instructions, required_data_type, price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (category_id, name, description, instructions, required_data_type, price))
        await db.commit()
        return cur.lastrowid


async def update_manual_service(service_id: int, **kwargs):
    async with get_db() as db:
        for field, value in kwargs.items():
            if field in ("name", "description", "instructions", "required_data_type", "price", "category_id"):
                await db.execute(
                    f"UPDATE manual_services SET {field} = ? WHERE id = ?",
                    (value, service_id)
                )
        await db.commit()


async def delete_manual_service(service_id: int):
    async with get_db() as db:
        await db.execute("DELETE FROM manual_services WHERE id = ?", (service_id,))
        await db.commit()


async def toggle_manual_service(service_id: int):
    async with get_db() as db:
        await db.execute(
            "UPDATE manual_services SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?",
            (service_id,)
        )
        await db.commit()


async def get_manual_services_by_category(category_id: int, active_only: bool = True):
    async with get_db() as db:
        if active_only:
            async with db.execute(
                "SELECT * FROM manual_services WHERE category_id = ? AND is_active = 1 ORDER BY id",
                (category_id,)
            ) as cur:
                return await cur.fetchall()
        else:
            async with db.execute(
                "SELECT * FROM manual_services WHERE category_id = ? ORDER BY id",
                (category_id,)
            ) as cur:
                return await cur.fetchall()


async def get_manual_service(service_id: int):
    async with get_db() as db:
        async with db.execute("SELECT * FROM manual_services WHERE id = ?", (service_id,)) as cur:
            return await cur.fetchone()


async def create_manual_order(user_id: int, service_id: int, service_name: str,
                               user_data: str, price: float) -> int:
    async with get_db() as db:
        cur = await db.execute("""
            INSERT INTO manual_orders (user_id, service_id, service_name, user_data, price, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (user_id, service_id, service_name, user_data, price))
        await db.execute(
            "UPDATE users SET total_orders = total_orders + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()
        return cur.lastrowid


async def update_manual_order_status(order_id: int, status: str):
    async with get_db() as db:
        await db.execute(
            "UPDATE manual_orders SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, order_id)
        )
        await db.commit()


async def save_manual_order_response(order_id: int, response: str):
    async with get_db() as db:
        await db.execute(
            "UPDATE manual_orders SET admin_response = ?, status = 'completed', updated_at = datetime('now') WHERE id = ?",
            (response, order_id)
        )
        await db.commit()


async def get_manual_orders(status: str = None, limit: int = 20):
    async with get_db() as db:
        if status:
            async with db.execute(
                "SELECT * FROM manual_orders WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            ) as cur:
                return await cur.fetchall()
        else:
            async with db.execute(
                "SELECT * FROM manual_orders ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ) as cur:
                return await cur.fetchall()


async def get_manual_order_by_id(order_id: int):
    async with get_db() as db:
        async with db.execute("SELECT * FROM manual_orders WHERE id = ?", (order_id,)) as cur:
            return await cur.fetchone()


async def get_user_manual_orders(user_id: int, limit: int = 10):
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM manual_orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ) as cur:
            return await cur.fetchall()


async def create_payment(user_id: int, amount: float, method: str, network: str,
                          wallet_address: str, proof_photo_id: str) -> int:
    async with get_db() as db:
        cur = await db.execute("""
            INSERT INTO payments (user_id, amount, method, network, wallet_address, proof_photo_id, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """, (user_id, amount, method, network, wallet_address, proof_photo_id))
        await db.commit()
        return cur.lastrowid


async def update_payment_status(payment_id: int, status: str, admin_note: str = ""):
    async with get_db() as db:
        await db.execute(
            "UPDATE payments SET status = ?, admin_note = ?, updated_at = datetime('now') WHERE id = ?",
            (status, admin_note, payment_id)
        )
        await db.commit()


async def get_payment_by_id(payment_id: int):
    async with get_db() as db:
        async with db.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)) as cur:
            return await cur.fetchone()


async def get_pending_payments():
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM payments WHERE status = 'pending' ORDER BY created_at DESC"
        ) as cur:
            return await cur.fetchall()


async def create_transfer(from_user: int, to_user: int, amount: float) -> int:
    async with get_db() as db:
        cur = await db.execute(
            "INSERT INTO transfers (from_user, to_user, amount) VALUES (?, ?, ?)",
            (from_user, to_user, amount)
        )
        await db.commit()
        return cur.lastrowid


async def get_stats():
    async with get_db() as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            total_users = (await cur.fetchone())[0]
        async with db.execute("SELECT SUM(balance) FROM users") as cur:
            total_balance = (await cur.fetchone())[0] or 0.0
        async with db.execute("SELECT COUNT(*) FROM orders") as cur:
            total_orders = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM manual_orders") as cur:
            total_manual_orders = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM payments") as cur:
            total_payments = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM referrals") as cur:
            total_referrals = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM providers WHERE is_active = 1") as cur:
            active_providers = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM services_cache") as cur:
            total_services = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT user_id, full_name, created_at FROM users ORDER BY created_at DESC LIMIT 5"
        ) as cur:
            recent_users = await cur.fetchall()
        return {
            "total_users": total_users,
            "total_balance": total_balance,
            "total_orders": total_orders,
            "total_manual_orders": total_manual_orders,
            "total_payments": total_payments,
            "total_referrals": total_referrals,
            "active_providers": active_providers,
            "total_services": total_services,
            "recent_users": recent_users,
        }


async def add_admin_balance_operation(user_id: int, amount: float, op_type: str, description: str = ""):
    async with get_db() as db:
        await db.execute(
            "INSERT INTO balance_operations (user_id, amount, operation_type, description) VALUES (?, ?, ?, ?)",
            (user_id, amount, op_type, description)
        )
        await db.commit()


async def check_referral_exists(referred_id: int) -> bool:
    async with get_db() as db:
        async with db.execute(
            "SELECT id FROM referrals WHERE referred_id = ?", (referred_id,)
        ) as cur:
            row = await cur.fetchone()
            return row is not None


async def get_user_transactions(user_id: int, limit: int = 30):
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM balance_operations WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ) as cur:
            return await cur.fetchall()


async def get_user_transaction_summary(user_id: int):
    async with get_db() as db:
        async with db.execute(
            "SELECT COALESCE(SUM(amount),0) FROM balance_operations WHERE user_id = ? AND operation_type = 'add'",
            (user_id,)
        ) as cur:
            total_charged = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COALESCE(SUM(amount),0) FROM balance_operations WHERE user_id = ? AND operation_type = 'deduct'",
            (user_id,)
        ) as cur:
            total_spent = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COALESCE(SUM(amount),0) FROM balance_operations WHERE user_id = ? AND operation_type = 'refund'",
            (user_id,)
        ) as cur:
            total_refunded = (await cur.fetchone())[0]
        async with db.execute(
            """SELECT description, COALESCE(SUM(amount),0) as total
               FROM balance_operations WHERE user_id = ? AND operation_type = 'deduct'
               GROUP BY description ORDER BY total DESC LIMIT 5""",
            (user_id,)
        ) as cur:
            per_service = await cur.fetchall()
        async with db.execute(
            "SELECT COUNT(*) FROM balance_operations WHERE user_id = ? AND operation_type = 'refund'",
            (user_id,)
        ) as cur:
            cancelled_count = (await cur.fetchone())[0]
        return {
            "total_charged": round(total_charged, 4),
            "total_spent": round(total_spent, 4),
            "total_refunded": round(total_refunded, 4),
            "per_service": per_service,
            "cancelled_count": cancelled_count,
        }


# =============================================
# Virtual Number Orders (5SIM)
# =============================================

async def save_vnum_order(user_id: int, fivesim_order_id: int, phone: str, country: str, product: str, operator: str, cost: float) -> int:
    async with get_db() as db:
        cur = await db.execute(
            """INSERT INTO virtual_number_orders
               (user_id, fivesim_order_id, phone, country, product, operator, cost)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, fivesim_order_id, phone, country, product, operator, cost)
        )
        await db.commit()
        return cur.lastrowid


async def get_vnum_order(fivesim_order_id: int):
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM virtual_number_orders WHERE fivesim_order_id = ?",
            (fivesim_order_id,)
        ) as cur:
            return await cur.fetchone()


async def update_vnum_order(fivesim_order_id: int, status: str, sms_code: str = None):
    async with get_db() as db:
        if sms_code:
            await db.execute(
                "UPDATE virtual_number_orders SET status=?, sms_code=?, updated_at=datetime('now') WHERE fivesim_order_id=?",
                (status, sms_code, fivesim_order_id)
            )
        else:
            await db.execute(
                "UPDATE virtual_number_orders SET status=?, updated_at=datetime('now') WHERE fivesim_order_id=?",
                (status, fivesim_order_id)
            )
        await db.commit()


async def get_user_vnum_orders(user_id: int, limit: int = 10):
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM virtual_number_orders WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ) as cur:
            return await cur.fetchall()


async def get_active_fivesim_provider():
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM providers WHERE provider_type='fivesim' AND is_active=1 LIMIT 1"
        ) as cur:
            return await cur.fetchone()
