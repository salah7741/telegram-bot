import asyncio
import logging
import traceback
from typing import Optional

import aiohttp
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

import database as db

# =============================================
# الإعدادات الأساسية
# =============================================

import os
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("TELEGRAM_OWNER_ID", "6091140905"))
CHANNEL_USERNAME = "@YourChannel"
CHANNEL_LINK = "https://t.me/YourChannel"
FORCE_SUBSCRIPTION_ENABLED = True
SUPPORT_USERNAME = "@YourSupportUsername"
PROFIT_PERCENT = 10
REFERRAL_BONUS = 0.01
STARS_RATE = 77  # 77 Telegram Stars = 1 USD

SMM_PROVIDERS = [
    {
        "name": "المورد الأول",
        "api_url": "https://provider1.com/api/v2",
        "api_key": "PUT_PROVIDER_1_API_KEY",
        "enabled": True,
    },
    {
        "name": "المورد الثاني",
        "api_url": "https://provider2.com/api/v2",
        "api_key": "PUT_PROVIDER_2_API_KEY",
        "enabled": True,
    },
    {
        "name": "المورد الثالث",
        "api_url": "https://provider3.com/api/v2",
        "api_key": "PUT_PROVIDER_3_API_KEY",
        "enabled": True,
    },
]

CRYPTO_WALLETS = {
    "BTC": "bc1qxjdvlrez3ehf96pxwhdyaeg8s987pvdlehz3r9",
    "USDT BEP20": "0x4DA3761310D9a528aAb475079f2ED4b0F2ef9840",
    "TON / GRAM": "UQC9Dr6duL1IY8AJLjanwWKbMzjFj8Q-aFCGSSqo8PdahbFa",
    "LTC": "ltc1qxjdvlrez3ehf96pxwhdyaeg8s987pvdlatc4m4",
    "SOL": "CEG5wLF2Y4nAkTf8gp9N4Y5Rjc7b8dyDmwsKTvy7cknx",
}

STARS_PACKAGES = [
    {"usd": 1, "stars": 77},
    {"usd": 5, "stars": 385},
    {"usd": 10, "stars": 770},
    {"usd": 20, "stars": 1540},
]

PLATFORMS = [
    "YouTube", "Facebook", "Instagram", "TikTok", "Telegram",
    "WhatsApp", "X / Twitter", "Snapchat", "Threads",
    "Spotify", "SoundCloud", "Website Traffic",
]

PLATFORM_ICONS = {
    "YouTube": "▶️", "Facebook": "👤", "Instagram": "📷", "TikTok": "🎵",
    "Telegram": "✈️", "WhatsApp": "💬", "X / Twitter": "🐦", "Snapchat": "👻",
    "Threads": "🧵", "Spotify": "🎧", "SoundCloud": "🔊", "Website Traffic": "🌐",
    "أرقام وهمية": "📱",
}

# دول الأرقام الوهمية (5SIM)
VNUM_COUNTRIES = {
    "russia": "🇷🇺 روسيا",
    "ukraine": "🇺🇦 أوكرانيا",
    "usa": "🇺🇸 أمريكا",
    "england": "🇬🇧 إنجلترا",
    "france": "🇫🇷 فرنسا",
    "germany": "🇩🇪 ألمانيا",
    "poland": "🇵🇱 بولندا",
    "china": "🇨🇳 الصين",
    "india": "🇮🇳 الهند",
    "indonesia": "🇮🇩 إندونيسيا",
    "vietnam": "🇻🇳 فيتنام",
    "philippines": "🇵🇭 الفلبين",
    "thailand": "🇹🇭 تايلاند",
    "myanmar": "🇲🇲 ميانمار",
    "turkey": "🇹🇷 تركيا",
    "cambodia": "🇰🇭 كمبوديا",
    "bangladesh": "🇧🇩 بنغلاديش",
    "malaysia": "🇲🇾 ماليزيا",
    "brazil": "🇧🇷 البرازيل",
    "mexico": "🇲🇽 المكسيك",
    "colombia": "🇨🇴 كولومبيا",
    "argentina": "🇦🇷 الأرجنتين",
    "peru": "🇵🇪 بيرو",
    "chile": "🇨🇱 تشيلي",
    "egypt": "🇪🇬 مصر",
    "kenya": "🇰🇪 كينيا",
    "nigeria": "🇳🇬 نيجيريا",
    "ghana": "🇬🇭 غانا",
    "pakistan": "🇵🇰 باكستان",
    "ethiopia": "🇪🇹 إثيوبيا",
    "uzbekistan": "🇺🇿 أوزبكستان",
    "kazakhstan": "🇰🇿 كازاخستان",
    "kyrgyzstan": "🇰🇬 قرغيزستان",
    "tajikistan": "🇹🇯 طاجيكستان",
    "moldova": "🇲🇩 مولدوفا",
    "georgia": "🇬🇪 جورجيا",
    "armenia": "🇦🇲 أرمينيا",
    "azerbaijan": "🇦🇿 أذربيجان",
    "indonesia": "🇮🇩 إندونيسيا",
    "srilanka": "🇱🇰 سريلانكا",
    "nepal": "🇳🇵 نيبال",
    "laos": "🇱🇦 لاوس",
    "morocco": "🇲🇦 المغرب",
    "tanzania": "🇹🇿 تنزانيا",
    "cameroon": "🇨🇲 الكاميرون",
    "senegal": "🇸🇳 السنغال",
    "cotedivoire": "🇨🇮 ساحل العاج",
    "angola": "🇦🇴 أنغولا",
    "mozambique": "🇲🇿 موزمبيق",
    "rwanda": "🇷🇼 رواندا",
    "guinea": "🇬🇳 غينيا",
    "zambia": "🇿🇲 زامبيا",
    "zimbabwe": "🇿🇼 زيمبابوي",
    "israel": "🇮🇱 إسرائيل",
    "netherlands": "🇳🇱 هولندا",
    "spain": "🇪🇸 إسبانيا",
    "italy": "🇮🇹 إيطاليا",
    "portugal": "🇵🇹 البرتغال",
    "czechia": "🇨🇿 التشيك",
    "romania": "🇷🇴 رومانيا",
    "bulgaria": "🇧🇬 بلغاريا",
    "serbia": "🇷🇸 صربيا",
    "estonia": "🇪🇪 إستونيا",
    "latvia": "🇱🇻 لاتفيا",
    "lithuania": "🇱🇹 ليتوانيا",
    "sweden": "🇸🇪 السويد",
    "finland": "🇫🇮 فنلندا",
    "norway": "🇳🇴 النرويج",
    "denmark": "🇩🇰 الدنمارك",
    "canada": "🇨🇦 كندا",
    "australia": "🇦🇺 أستراليا",
    "newzealand": "🇳🇿 نيوزيلندا",
    "hongkong": "🇭🇰 هونغ كونغ",
    "taiwan": "🇹🇼 تايوان",
    "southkorea": "🇰🇷 كوريا الجنوبية",
    "japan": "🇯🇵 اليابان",
}

# خدمات الأرقام الوهمية — ترجمة الأسماء
VNUM_SERVICE_NAMES = {
    "telegram": "✈️ تيليجرام",
    "whatsapp": "💬 واتساب",
    "instagram": "📷 انستغرام",
    "facebook": "👤 فيسبوك",
    "tiktok": "🎵 تيك توك",
    "twitter": "🐦 تويتر/X",
    "snapchat": "👻 سناب شات",
    "gmail": "📧 جيميل",
    "google": "🔍 جوجل",
    "youtube": "▶️ يوتيوب",
    "yahoo": "📧 ياهو",
    "microsoft": "🖥️ مايكروسوفت",
    "apple": "🍎 آبل",
    "amazon": "📦 أمازون",
    "uber": "🚗 أوبر",
    "airbnb": "🏠 أيرنب",
    "viber": "📞 فايبر",
    "line": "💬 لاين",
    "wechat": "💬 وي شات",
    "tinder": "❤️ تيندر",
    "paypal": "💰 باي بال",
    "steam": "🎮 ستيم",
    "discord": "🎮 ديسكورد",
    "netflix": "🎬 نتفليكس",
    "spotify": "🎧 سبوتيفاي",
    "linkedin": "💼 لينكد إن",
    "reddit": "🔴 ريديت",
    "pinterest": "📌 بينتيريست",
    "shopify": "🛒 شوبيفاي",
    "binance": "💰 بايننس",
    "bybit": "💹 بايبيت",
    "any": "🌐 أي خدمة",
}

STATUS_AR = {
    "pending": "⏳ قيد الانتظار",
    "processing": "⚙️ قيد التنفيذ",
    "in progress": "⚙️ قيد التنفيذ",
    "completed": "✅ مكتمل",
    "partial": "🔶 مكتمل جزئياً",
    "cancelled": "❌ ملغي",
    "canceled": "❌ ملغي",
    "refunded": "↩️ مسترجع",
}

CATEGORY_ICONS = {
    "متابعين": "👥", "مشتركين": "🔔", "أعضاء": "👥", "أصدقاء": "👤",
    "لايكات": "❤️", "تفاعلات": "🔥", "مشاهدات": "👁️",
    "مشاهدات بث مباشر": "🔴", "مشاهدات ستوري": "📱", "تعليقات": "💬",
    "تعليقات مخصصة": "✍️", "مشاركات": "🔁", "إعادة نشر": "🔄",
    "ريتويت": "🔁", "حفظ": "💾", "زيارات موقع": "🌐",
}

# =============================================
# تصنيف خدمات المزود (عربي + إنجليزي)
# =============================================

PLATFORM_KEYWORDS = {
    "YouTube": ["youtube", "يوتيوب", "يوتيب", "يوتوب", "yt "],
    "Facebook": ["facebook", "fb ", "فيسبوك", "فيس بوك"],
    "Instagram": ["instagram", "ig ", "انستقرام", "انستغرام", "انستجرام", "انستا"],
    "TikTok": ["tiktok", "tik tok", "تيك توك", "تيكتوك"],
    "Telegram": ["telegram", "tg ", " tg", "تيليجرام", "تلجرام", "تليجرام", "تليغرام", "تيلجرام"],
    "WhatsApp": ["whatsapp", "واتساب", "واتس اب"],
    "X / Twitter": ["twitter", "x/twitter", " x ", "تويتر", "تويت"],
    "Snapchat": ["snapchat", "snap", "سناب", "سنابشات"],
    "Threads": ["threads", "ثريدز"],
    "Spotify": ["spotify", "سبوتيفاي", "سبوتيفي"],
    "SoundCloud": ["soundcloud", "ساوند كلاود"],
    "Website Traffic": ["website", "traffic", "web traffic", "موقع", "زيارات موقع"],
}

CATEGORY_KEYWORDS = {
    "متابعين": ["followers", "follow", "متابعين", "متابعون", "متابع", "فولورز"],
    "مشتركين": ["subscribers", "subscribe", "مشتركين", "مشتركون", "مشترك", "سبسكرايب"],
    "أعضاء": ["members", "member", "أعضاء", "اعضاء", "عضو", "ميمبرز"],
    "أصدقاء": ["friends", "friend", "أصدقاء", "صديق"],
    "لايكات": ["likes", "like", "لايكات", "لايك", "إعجابات", "اعجابات", "لايكس"],
    "تفاعلات": [
        "reactions", "reaction", "تفاعلات", "تفاعل", "رياكشن", "رياكشنات",
        "تفاعلات للمنشورات", "تليجرام تفاعلات", "emoji reactions",
    ],
    "مشاهدات": ["views", "view", "مشاهدات", "مشاهدة", "فيوز"],
    "مشاهدات بث مباشر": ["live views", "livestream", "live stream", "بث مباشر", "لايف"],
    "مشاهدات ستوري": ["story views", "stories views", "مشاهدات ستوري", "ستوري"],
    "تعليقات": ["comments", "comment", "تعليقات", "تعليق", "تعليقات تليجرام", "telegram comments"],
    "تعليقات مخصصة": ["custom comments", "تعليقات مخصصة", "تعليقات خاصة"],
    "مشاركات": ["shares", "share", "مشاركات", "مشاركة"],
    "إعادة نشر": ["reposts", "repost", "إعادة نشر", "اعادة نشر"],
    "ريتويت": ["retweets", "retweet", "ريتويت", "ريتويتات"],
    "حفظ": ["saves", "save", "حفظ", "سيفز"],
    "زيارات موقع": ["website traffic", "web traffic", "site traffic", "زيارات موقع", "زيارات الموقع"],
}


def detect_platform(service_name: str) -> str:
    name_lower = service_name.lower()
    for platform, keywords in PLATFORM_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return platform
    return "أخرى"


def detect_service_type(service_name: str) -> str:
    name_lower = service_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return category
    return "عام"


def translate_service_name(original_name: str) -> str:
    return original_name


# =============================================
# حالات FSM
# =============================================

class OrderStates(StatesGroup):
    waiting_link = State()
    waiting_quantity = State()
    confirming = State()


class ManualOrderStates(StatesGroup):
    waiting_data = State()
    confirming = State()


class PaymentStates(StatesGroup):
    waiting_amount = State()
    waiting_proof = State()


class TransferStates(StatesGroup):
    waiting_target = State()
    waiting_amount = State()
    confirming = State()


class AdminStates(StatesGroup):
    broadcast = State()
    add_balance_id = State()
    add_balance_amount = State()
    add_balance_confirm = State()
    deduct_balance_id = State()
    deduct_balance_amount = State()
    deduct_balance_confirm = State()
    search_user = State()
    add_provider_name = State()
    add_provider_type = State()
    add_provider_url = State()
    add_provider_key = State()
    edit_provider_field = State()
    edit_provider_value = State()
    payment_approve_amount = State()
    payment_approve_note = State()
    add_manual_cat = State()
    edit_manual_cat_id = State()
    edit_manual_cat_name = State()
    add_service_cat = State()
    add_service_name = State()
    add_service_desc = State()
    add_service_instr = State()
    add_service_dtype = State()
    add_service_price = State()
    edit_service_field = State()
    edit_service_value = State()
    manual_order_respond = State()
    manual_order_id_respond = State()
    edit_sub_channel = State()
    edit_sub_link = State()
    admin_send_message = State()
    delete_cats_multi = State()


class SupportStates(StatesGroup):
    waiting_message = State()
    waiting_suggestion = State()


class AdminReplyStates(StatesGroup):
    reply_support = State()
    reply_suggestion = State()


class VNumberStates(StatesGroup):
    selecting_country = State()
    selecting_service = State()


# =============================================
# الإعداد
# =============================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

pending_orders: set = set()

# ── حماية من السبام: حد أقصى 3 طلبات كل 60 ثانية لكل مستخدم ──
import time as _time
from collections import defaultdict as _defaultdict

class _RateLimiter:
    """Rate limiter بسيط في الذاكرة لمنع سبام أزرار الشراء."""
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self._calls: dict = _defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        now = _time.monotonic()
        calls = [t for t in self._calls[user_id] if now - t < self.period]
        self._calls[user_id] = calls
        if len(calls) >= self.max_calls:
            return False
        calls.append(now)
        return True

_order_rate_limiter = _RateLimiter(max_calls=3, period=60)


# =============================================
# دوال مساعدة
# =============================================

async def send_admin_error(error_text: str):
    try:
        await bot.send_message(ADMIN_ID, f"⚠️ <b>خطأ في البوت:</b>\n<code>{error_text[:3000]}</code>")
    except Exception:
        pass


async def check_subscription(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    force_enabled = await db.get_setting("force_subscription_enabled", "1")
    if force_enabled == "0":
        return True
    channel = await db.get_setting("channel_username", CHANNEL_USERNAME)
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ("creator", "administrator", "member")
    except Exception as e:
        await send_admin_error(f"check_subscription error: {e}")
        return False


_ban_cache: dict[int, tuple[bool, float]] = {}
_BAN_CACHE_TTL = 60.0  # ثانية

async def is_banned(user_id: int) -> bool:
    now = _time.monotonic()
    cached = _ban_cache.get(user_id)
    if cached is not None and now - cached[1] < _BAN_CACHE_TTL:
        return cached[0]
    user = await db.get_user(user_id)
    result = bool(user and user["is_banned"])
    _ban_cache[user_id] = (result, now)
    return result

def invalidate_ban_cache(user_id: int) -> None:
    _ban_cache.pop(user_id, None)


def build_main_menu(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🛒 الخدمات المتكاملة", callback_data="smm:platforms"),
            InlineKeyboardButton(text="🎮 شحن الألعاب والبطاقات", callback_data="manual:categories"),
        ],
        [
            InlineKeyboardButton(text="💳 شحن الحساب", callback_data="charge:menu"),
            InlineKeyboardButton(text="👤 حسابي ورصيدي", callback_data="account:menu"),
        ],
        [
            InlineKeyboardButton(text="🎁 رابط الدعوة", callback_data="referral:show"),
            InlineKeyboardButton(text="📦 طلباتي ومتابعتها", callback_data="orders:list"),
        ],
        [InlineKeyboardButton(text="📞 الدعم الفني", callback_data="support:menu")],
    ]
    if user_id == ADMIN_ID:
        buttons.append([InlineKeyboardButton(text="🛠 لوحة الأدمن", callback_data="admin:panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def send_subscription_message(chat_id: int, message_id: int = None):
    channel_link = await db.get_setting("channel_link", CHANNEL_LINK)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 الاشتراك في القناة", url=channel_link)],
        [InlineKeyboardButton(text="🔄 تحقق من الاشتراك", callback_data="check_sub")],
    ])
    text = (
        "🔐 <b>عذراً عزيزي، يجب عليك الاشتراك في قناة البوت الرسمية أولاً حتى تتمكن من استخدام الخدمات.</b>"
    )
    if message_id:
        try:
            await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=kb)
        except Exception:
            await bot.send_message(chat_id, text, reply_markup=kb)
    else:
        await bot.send_message(chat_id, text, reply_markup=kb)


# =============================================
# 5SIM Client
# =============================================

def _normalize_fivesim_url(raw_url: str) -> str:
    """يُنظّف Base URL لـ 5SIM ويضمن أنه ينتهي بـ /v1 فقط مرة واحدة."""
    url = (raw_url or "").strip().rstrip("/")
    # احذف أي مسار مضاف بالغلط مثل /user/profile أو /user/buy
    for bad_suffix in ["/user/profile", "/user/buy", "/user/check",
                       "/user/cancel", "/user/finish", "/guest/products",
                       "/guest/prices"]:
        if url.endswith(bad_suffix):
            url = url[: -len(bad_suffix)].rstrip("/")
    # إذا ينتهي بـ /v1/v1 اختصره
    while "/v1/v1" in url:
        url = url.replace("/v1/v1", "/v1")
    # إذا لا يوجد /v1 في النهاية أضفه
    if not url.endswith("/v1"):
        url = url + "/v1"
    return url


class FiveSimClient:
    def __init__(self, api_key: str, base_url: str = "https://5sim.net/v1"):
        # حذف "Bearer " تلقائياً إذا أضافها المستخدم بالغلط
        clean_key = api_key.strip()
        if clean_key.lower().startswith("bearer "):
            clean_key = clean_key[7:].strip()
        self.base_url = _normalize_fivesim_url(base_url)
        self.headers = {
            "Authorization": f"Bearer {clean_key}",
            "Accept": "application/json",
        }

    async def _get(self, endpoint: str) -> dict:
        import json as _json
        url = f"{self.base_url}{endpoint}"
        logger.info(f"5SIM GET {url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    status = resp.status
                    text = await resp.text()
                    logger.info(f"5SIM {url} → status={status} body={text[:200]}")
                    if not text or not text.strip():
                        return {"_status": status, "message": f"empty response (status {status})"}
                    try:
                        data = _json.loads(text)
                        if not isinstance(data, dict):
                            return {"_status": status, "message": text.strip()[:300]}
                        data["_status"] = status
                        return data
                    except Exception:
                        return {"_status": status, "message": text.strip()[:300]}
        except aiohttp.InvalidURL:
            logger.error(f"5SIM InvalidURL: {url}")
            return {"_status": 0, "message": "invalid_url"}
        except aiohttp.ClientConnectorError as e:
            logger.error(f"5SIM ConnectionError: {url} — {e}")
            return {"_status": 0, "message": "connection_error"}
        except Exception as e:
            logger.error(f"5SIM Error: {url} — {e}")
            return {"_status": 0, "message": f"error: {str(e)[:200]}"}

    async def test_connection(self) -> dict:
        return await self._get("/user/profile")

    async def get_balance(self) -> float:
        data = await self._get("/user/profile")
        return float(data.get("balance", 0.0))

    async def get_prices(self) -> dict:
        return await self._get("/guest/prices")

    async def get_products(self, country: str, operator: str = "any") -> dict:
        return await self._get(f"/guest/products/{country}/{operator}")

    async def get_operator_prices(self, country: str, product: str) -> list:
        """Returns sorted list of {operator, cost, count, rate} where count > 0"""
        data = await self._get(f"/guest/prices?country={country}&product={product}")
        data.pop("_status", None)
        if not data:
            return []
        # Handle nested format: {country: {product: {operator: {...}}}}
        operators_raw = {}
        if country in data:
            operators_raw = data.get(country, {}).get(product, {})
        else:
            # Flat format: {operator: {Cost, Count, Rate}}
            operators_raw = data
        result = []
        for op, info in operators_raw.items():
            if not isinstance(info, dict):
                continue
            # 5SIM يرجع lowercase keys: cost/count/rate
            # أحيانًا uppercase: Cost/Count/Rate — نقبل الاثنين
            count = int(info.get("count", info.get("Count", 0)))
            if count <= 0:
                continue
            cost = float(info.get("cost", info.get("Cost", 0)))
            rate = float(info.get("rate", info.get("Rate", 0)))
            result.append({
                "operator": op,
                "cost": cost,
                "count": count,
                "rate": rate,
            })
        result.sort(key=lambda x: x["cost"])
        return result

    async def get_provider_balance(self) -> float:
        data = await self._get("/user/profile")
        return float(data.get("balance", -1.0))

    async def buy_activation(self, country: str, operator: str, product: str) -> dict:
        return await self._get(f"/user/buy/activation/{country}/{operator}/{product}")

    async def check_order(self, order_id: int) -> dict:
        return await self._get(f"/user/check/{order_id}")

    async def finish_order(self, order_id: int) -> dict:
        return await self._get(f"/user/finish/{order_id}")

    async def cancel_order(self, order_id: int) -> dict:
        return await self._get(f"/user/cancel/{order_id}")

    async def ban_order(self, order_id: int) -> dict:
        return await self._get(f"/user/ban/{order_id}")


def mask_api_key(key: str) -> str:
    if len(key) <= 10:
        return key[:3] + "***"
    return key[:6] + "..." + key[-4:]


async def fetch_services_from_provider(provider: dict) -> list:
    # موردو 5SIM لا يستخدمون نظام SMM — تخطّهم
    if provider.get("provider_type") == "fivesim":
        return []
    services = []
    try:
        profit_percent = float(await db.get_setting("profit_percent", str(PROFIT_PERCENT)))
        async with aiohttp.ClientSession() as session:
            async with session.post(
                provider["api_url"],
                data={"key": provider["api_key"], "action": "services"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                data = await resp.json(content_type=None)
        if not isinstance(data, list):
            return []
        for item in data:
            name = str(item.get("name", ""))
            platform = detect_platform(name)
            category = detect_service_type(name)
            rate = float(item.get("rate", 0))
            final_rate = round(rate * (1 + profit_percent / 100), 4)
            services.append({
                "provider_id": provider["id"],
                "provider_name": provider["name"],
                "provider_service_id": str(item.get("service", "")),
                "platform": platform,
                "category": category,
                "original_name": name,
                "arabic_name": translate_service_name(name),
                "rate": rate,
                "final_rate": final_rate,
                "min": int(item.get("min", 0)),
                "max": int(item.get("max", 0)),
                "status": "active" if item.get("status", "Active").lower() == "active" else "inactive",
            })
    except Exception as e:
        await send_admin_error(f"خطأ في جلب خدمات المورد [{provider['name']}]: {e}")
    return services


async def place_smm_order(provider: dict, service_id: str, link: str, quantity: int) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                provider["api_url"],
                data={
                    "key": provider["api_key"],
                    "action": "add",
                    "service": service_id,
                    "link": link,
                    "quantity": quantity,
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                data = await resp.json(content_type=None)
        return data
    except Exception as e:
        return {"error": str(e)}


async def check_smm_order_status(provider: dict, provider_order_id: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                provider["api_url"],
                data={
                    "key": provider["api_key"],
                    "action": "status",
                    "order": provider_order_id,
                },
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                data = await resp.json(content_type=None)
        return data
    except Exception as e:
        return {"error": str(e)}


# =============================================
# /start
# =============================================

@router.message(Command("help"))
async def cmd_help(message: Message):
    support_username = await db.get_setting("support_username", SUPPORT_USERNAME)
    await message.answer(
        "📖 <b>مساعدة — كيفية استخدام البوت</b>\n\n"
        "🔹 <b>الخدمات المتاحة:</b>\n"
        "  • 📱 <b>شحن الألعاب والبطاقات</b> — شحن ألعابك ببطاقات رقمية\n"
        "  • 📊 <b>خدمات SMM</b> — زيادة متابعين، لايكات، مشاهدات\n"
        "  • 💰 <b>شحن الرصيد</b> — عبر كريبتو أو Stars\n"
        "  • 📦 <b>طلباتي</b> — متابعة حالة طلباتك\n"
        "  • 👥 <b>الإحالات</b> — ادعُ أصدقاءك واربح رصيداً\n\n"
        "🔹 <b>الأوامر:</b>\n"
        "  /start — بدء البوت والقائمة الرئيسية\n"
        "  /help — عرض هذه الرسالة\n\n"
        "🔹 <b>للتواصل مع الدعم:</b>\n"
        f"  {support_username}\n\n"
        "أو اضغط على <b>الدعم الفني</b> في القائمة الرئيسية.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="main:menu")]
        ]),
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    full_name = message.from_user.full_name or ""
    username = message.from_user.username or ""
    args = message.text.split() if message.text else []
    ref_by = None
    if len(args) > 1:
        try:
            ref_id = int(args[1])
            if ref_id != user_id:
                ref_by = ref_id
        except ValueError:
            pass

    existing = await db.get_user(user_id)
    await db.add_user(user_id, full_name, username, ref_by if not existing else None)

    if not existing and ref_by:
        already = await db.check_referral_exists(user_id)
        if not already:
            bonus = float(await db.get_setting("referral_bonus", str(REFERRAL_BONUS)))
            await db.create_referral(ref_by, user_id, bonus)
            await db.add_referral_bonus(ref_by, bonus)
            try:
                await bot.send_message(
                    ref_by,
                    f"🎁 <b>تهانينا!</b> انضم صديق جديد عبر رابط دعوتك!\n💰 حصلت على مكافأة <b>{bonus}$</b>",
                )
            except Exception:
                pass

    if await is_banned(user_id):
        await message.answer("🚫 تم حظرك من استخدام هذا البوت.")
        return

    subscribed = await check_subscription(user_id)
    if not subscribed:
        await send_subscription_message(message.chat.id)
        return

    user_data = await db.get_user(user_id)
    balance = user_data["balance"] if user_data else 0.0
    orders_count = await db.get_user_orders_count(user_id)
    await message.answer(
        f"👋 <b>مرحباً {full_name}!</b>\n\n"
        f"💰 رصيدك: <b>{balance}$</b>\n"
        f"📦 طلباتك: <b>{orders_count}</b>\n\n"
        f"اختر ما تريد من الأزرار أدناه:",
        reply_markup=build_main_menu(user_id),
    )


@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_banned(user_id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    subscribed = await check_subscription(user_id)
    if not subscribed:
        await callback.answer("❌ لم تشترك بعد! اشترك في القناة أولاً.", show_alert=True)
        return
    await callback.message.edit_text(
        "👋 <b>تم التحقق بنجاح!</b>\nاختر ما تريد:",
        reply_markup=build_main_menu(user_id),
    )
    await callback.answer()


@router.callback_query(F.data == "main:menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    if await is_banned(user_id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    await callback.answer()
    subscribed = await check_subscription(user_id)
    if not subscribed:
        await send_subscription_message(callback.message.chat.id, callback.message.message_id)
        return
    user_data_row = await db.get_user(user_id)
    balance = user_data_row["balance"] if user_data_row else 0.0
    orders_count = await db.get_user_orders_count(user_id)
    full_name = callback.from_user.full_name or ""
    try:
        await callback.message.edit_text(
            f"👋 <b>مرحباً {full_name}!</b>\n\n"
            f"💰 رصيدك: <b>{balance}$</b>\n"
            f"📦 طلباتك: <b>{orders_count}</b>\n\n"
            f"اختر ما تريد من الأزرار أدناه:",
            reply_markup=build_main_menu(user_id),
        )
    except TelegramBadRequest:
        pass


# =============================================
# الخدمات المتكاملة
# =============================================

@router.callback_query(F.data == "smm:platforms")
async def smm_platforms(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_banned(user_id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    await callback.answer()
    if not await check_subscription(user_id):
        await send_subscription_message(callback.message.chat.id, callback.message.message_id)
        return
    buttons = []
    row = []
    for i, platform in enumerate(PLATFORMS):
        icon = PLATFORM_ICONS.get(platform, "📌")
        row.append(InlineKeyboardButton(text=f"{icon} {platform}", callback_data=f"smm:platform:{platform}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="📱 الأرقام الوهمية", callback_data="vnumbers:menu")])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")])
    await callback.message.edit_text(
        "🛒 <b>الخدمات المتكاملة</b>\nاختر المنصة:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("smm:platform:"))
async def smm_platform_categories(callback: CallbackQuery):
    user_id = callback.from_user.id
    platform = callback.data.split("smm:platform:")[1]
    categories = await db.get_distinct_categories_for_platform(platform)
    if not categories:
        await callback.answer("⚠️ لا توجد خدمات لهذه المنصة حالياً. يرجى تحديث الخدمات من لوحة الأدمن.", show_alert=True)
        return
    buttons = []
    row = []
    for cat in categories:
        icon = CATEGORY_ICONS.get(cat, "📌")
        row.append(InlineKeyboardButton(
            text=f"{icon} {cat}",
            callback_data=f"smm:cat:{platform}:{cat}:0"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="smm:platforms")])
    await callback.answer()
    await callback.message.edit_text(
        f"📌 <b>{platform}</b>\nاختر نوع الخدمة:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("smm:cat:"))
async def smm_services_list(callback: CallbackQuery):
    parts = callback.data.split(":")
    platform = parts[2]
    category = parts[3]
    page = int(parts[4]) if len(parts) > 4 else 0
    limit = 6
    offset = page * limit
    services, total = await db.get_services_by_platform_category(platform, category, offset, limit)
    if not services:
        await callback.answer("⚠️ لا توجد خدمات متاحة.", show_alert=True)
        return
    buttons = []
    for svc in services:
        name = svc["arabic_name"] or svc["original_name"]
        name_short = name[:30] + "..." if len(name) > 30 else name
        buttons.append([InlineKeyboardButton(
            text=f"{name_short} - {svc['final_rate']}$/1000",
            callback_data=f"smm:svc:{svc['id']}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ السابق", callback_data=f"smm:cat:{platform}:{category}:{page-1}"))
    if offset + limit < total:
        nav.append(InlineKeyboardButton(text="➡️ التالي", callback_data=f"smm:cat:{platform}:{category}:{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data=f"smm:platform:{platform}")])
    await callback.answer()
    await callback.message.edit_text(
        f"📋 <b>{platform} > {category}</b>\n"
        f"الصفحة {page+1} | إجمالي {total} خدمة",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("smm:svc:"))
async def smm_service_detail(callback: CallbackQuery):
    service_id = int(callback.data.split(":")[2])
    svc = await db.get_service_by_id(service_id)
    if not svc:
        await callback.answer("❌ الخدمة غير موجودة.", show_alert=True)
        return
    name = svc["arabic_name"] or svc["original_name"]
    text = (
        f"📌 <b>{name}</b>\n\n"
        f"💰 <b>السعر:</b> {svc['final_rate']}$ لكل 1000\n"
        f"📉 <b>الحد الأدنى:</b> {svc['min']}\n"
        f"📈 <b>الحد الأقصى:</b> {svc['max']}\n"
        f"📊 <b>المنصة:</b> {svc['platform']}\n"
        f"🗂 <b>النوع:</b> {svc['category']}\n\n"
        f"اضغط <b>طلب الخدمة</b> للمتابعة."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ طلب الخدمة", callback_data=f"smm:order:{service_id}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data=f"smm:cat:{svc['platform']}:{svc['category']}:0")],
    ])
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=kb)


@router.callback_query(F.data.startswith("smm:order:"))
async def smm_order_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_banned(user_id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    service_id = int(callback.data.split(":")[2])
    svc = await db.get_service_by_id(service_id)
    if not svc:
        await callback.answer("❌ الخدمة غير موجودة.", show_alert=True)
        return
    await state.set_state(OrderStates.waiting_link)
    await state.update_data(service_id=service_id, msg_id=callback.message.message_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="main:menu")]
    ])
    await callback.message.edit_text(
        f"🔗 <b>أدخل الرابط المطلوب تعزيزه:</b>\n"
        f"(مثال: رابط صفحتك على {svc['platform']})",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(OrderStates.waiting_link)
async def smm_order_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not link.startswith("http"):
        await message.answer("❌ الرابط غير صالح. أدخل رابطاً يبدأ بـ http أو https.")
        return
    await state.update_data(link=link)
    await state.set_state(OrderStates.waiting_quantity)
    data = await state.get_data()
    svc = await db.get_service_by_id(data["service_id"])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="main:menu")]
    ])
    await message.answer(
        f"🔢 <b>أدخل الكمية المطلوبة:</b>\n"
        f"📉 الحد الأدنى: {svc['min']}\n"
        f"📈 الحد الأقصى: {svc['max']}",
        reply_markup=kb,
    )


@router.message(OrderStates.waiting_quantity)
async def smm_order_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text.strip())
    except ValueError:
        await message.answer("❌ الكمية يجب أن تكون رقماً صحيحاً.")
        return
    data = await state.get_data()
    svc = await db.get_service_by_id(data["service_id"])
    if quantity < svc["min"] or quantity > svc["max"]:
        await message.answer(
            f"❌ الكمية يجب أن تكون بين {svc['min']} و {svc['max']}."
        )
        return
    price = round((svc["final_rate"] / 1000) * quantity, 4)
    balance = await db.get_user_balance(message.from_user.id)
    await state.update_data(quantity=quantity, price=price)
    await state.set_state(OrderStates.confirming)
    name = svc["arabic_name"] or svc["original_name"]
    text = (
        f"📋 <b>ملخص الطلب:</b>\n\n"
        f"📌 الخدمة: {name}\n"
        f"🔗 الرابط: {data['link']}\n"
        f"🔢 الكمية: {quantity}\n"
        f"💰 السعر: {price}$\n"
        f"💳 رصيدك: {balance}$\n\n"
    )
    if balance < price:
        text += "❌ رصيدك غير كافٍ. يرجى شحن رصيدك أولاً."
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 شحن الحساب", callback_data="charge:menu")],
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
        ])
        await state.clear()
        await message.answer(text, reply_markup=kb)
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تأكيد الطلب", callback_data="smm:confirm"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="main:menu"),
        ]
    ])
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "smm:confirm")
async def smm_order_confirm(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # ── 1. Rate limit: منع السبام على زر التأكيد ──
    if not _order_rate_limiter.is_allowed(user_id):
        await callback.answer("⚠️ طلبات كثيرة جداً، انتظر دقيقة ثم حاول.", show_alert=True)
        return

    # ── 2. منع الطلبات المتزامنة (idempotency) ──
    if user_id in pending_orders:
        await callback.answer("⏳ طلبك قيد المعالجة، انتظر قليلاً.", show_alert=True)
        return

    data = await state.get_data()
    if not data.get("service_id"):
        await callback.answer("❌ انتهت الجلسة. ابدأ من جديد.", show_alert=True)
        await state.clear()
        return

    pending_orders.add(user_id)
    await callback.answer("⏳ جاري معالجة طلبك...")

    order_id = None
    price = 0.0
    try:
        # ── 3. إعادة جلب الخدمة من DB (لا نثق بالسعر من الـ state) ──
        svc = await db.get_service_by_id(data["service_id"])
        if not svc:
            await callback.message.edit_text("❌ الخدمة غير موجودة.")
            await state.clear()
            return

        # ── 4. التحقق من المدخلات ──
        try:
            quantity = int(data.get("quantity", 0))
        except (TypeError, ValueError):
            await callback.message.edit_text("❌ كمية غير صالحة.")
            await state.clear()
            return

        link = str(data.get("link", "")).strip()
        if not (link.startswith("http://") or link.startswith("https://")):
            await callback.message.edit_text("❌ الرابط غير صالح.")
            await state.clear()
            return

        if quantity < svc["min"] or quantity > svc["max"]:
            await callback.message.edit_text(
                f"❌ الكمية يجب أن تكون بين {svc['min']} و {svc['max']}."
            )
            await state.clear()
            return

        # ── 5. حساب السعر من السيرفر فقط (لا من الزر أو state) ──
        price = round((svc["final_rate"] / 1000) * quantity, 4)

        # ── 6. جلب المورد ──
        provider = await db.get_provider(svc["provider_id"])
        if not provider:
            await callback.message.edit_text("❌ مورد الخدمة غير متاح حالياً.")
            await state.clear()
            return

        # ── 7. خصم ذري قبل أي استدعاء خارجي ──
        deducted = await db.deduct_balance_atomic(
            user_id, price, f"طلب SMM: {svc['original_name']}"
        )
        if not deducted:
            await callback.message.edit_text(
                "❌ رصيدك غير كافٍ لإتمام هذا الطلب.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💳 شحن الحساب", callback_data="charge:menu")],
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
                ]),
            )
            await state.clear()
            return

        # ── 8. إنشاء سجل PENDING قبل استدعاء API ──
        order_id = await db.create_order_pending(
            user_id=user_id,
            provider_id=svc["provider_id"],
            provider_name=svc["provider_name"],
            service_id=svc["id"],
            service_name=svc["original_name"],
            link=link,
            quantity=quantity,
            price=price,
        )
        logger.info(
            "SMM order created | order_id=%s user_id=%s service_id=%s "
            "quantity=%s price=%s status=PENDING",
            order_id, user_id, svc["id"], quantity, price,
        )

        # ── 9. استدعاء API المورد ──
        provider_dict = dict(provider)
        result = await place_smm_order(
            provider_dict, svc["provider_service_id"], link, quantity
        )

        if "order" in result:
            # ── 10a. نجاح: تحديث الطلب إلى PROCESSING ──
            provider_order_id = str(result["order"])
            await db.update_order_status(order_id, "processing", provider_order_id)
            new_balance = await db.get_user_balance(user_id)
            logger.info(
                "SMM order success | order_id=%s user_id=%s provider_order_id=%s "
                "price=%s status=PROCESSING",
                order_id, user_id, provider_order_id, price,
            )
            await callback.message.edit_text(
                f"✅ <b>تم تنفيذ طلبك بنجاح!</b>\n\n"
                f"📦 رقم الطلب: #{order_id}\n"
                f"💰 المبلغ المخصوم: {price}$\n"
                f"💳 رصيدك المتبقي: {new_balance}$\n\n"
                f"يمكنك متابعة حالة طلبك من قسم <b>طلباتي ومتابعتها</b>.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📦 طلباتي", callback_data="orders:list")],
                    [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main:menu")],
                ]),
            )
        else:
            # ── 10b. فشل: استرجاع المبلغ وتحديث الطلب إلى REFUNDED ──
            err_msg = result.get("error", "رد غير متوقع من المورد")
            await db.refund_order(order_id, user_id, price, f"فشل API للطلب #{order_id}")
            logger.warning(
                "SMM order failed | order_id=%s user_id=%s error=%s refunded=%s",
                order_id, user_id, err_msg, price,
            )
            await send_admin_error(
                f"فشل طلب SMM\norder_id={order_id} user_id={user_id}\n{err_msg}"
            )
            await callback.message.edit_text(
                "❌ <b>فشل تنفيذ الطلب لدى المورد.</b>\n"
                "تم إرجاع رصيدك كاملاً. حاول مجدداً أو تواصل مع الدعم.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")]
                ]),
            )

    except Exception:
        logger.error(
            "smm_order_confirm unexpected error | user_id=%s order_id=%s",
            user_id, order_id, exc_info=True,
        )
        # إذا تم الخصم وأُنشئ الطلب، نُعيد المبلغ فوراً
        if order_id and price > 0:
            try:
                await db.refund_order(
                    order_id, user_id, price, f"خطأ غير متوقع في طلب #{order_id}"
                )
                logger.info("Refunded order_id=%s user_id=%s amount=%s", order_id, user_id, price)
            except Exception:
                logger.error("CRITICAL: failed to refund order_id=%s", order_id, exc_info=True)
                await send_admin_error(
                    f"⚠️ فشل استرجاع رصيد!\norder_id={order_id} user_id={user_id} amount={price}"
                )
        try:
            await callback.message.edit_text(
                "❌ حدث خطأ أثناء تنفيذ الطلب.\n"
                "لم يتم خصم أي مبلغ إذا لم يكتمل الطلب. تواصل مع الدعم إذا لاحظت أي مشكلة.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")]
                ]),
            )
        except Exception:
            pass
    finally:
        pending_orders.discard(user_id)
        await state.clear()


# =============================================
# شحن الألعاب والبطاقات - خدمات يدوية
# =============================================

@router.callback_query(F.data == "manual:categories")
async def manual_categories(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_banned(user_id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    await callback.answer()
    categories = await db.get_manual_categories(active_only=True)
    if not categories:
        await callback.message.edit_text("⚠️ لا توجد أقسام متاحة حالياً.")
        return
    buttons = []
    row = []
    for cat in categories:
        row.append(InlineKeyboardButton(
            text=f"🎮 {cat['name']}",
            callback_data=f"manual:category:{cat['id']}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")])
    await callback.message.edit_text(
        "🎮 <b>شحن الألعاب والبطاقات</b>\nاختر القسم:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("manual:category:"))
async def manual_category_services(callback: CallbackQuery):
    cat_id = int(callback.data.split(":")[2])
    await callback.answer()
    services = await db.get_manual_services_by_category(cat_id, active_only=True)
    if not services:
        await callback.message.edit_text("⚠️ لا توجد خدمات في هذا القسم حالياً.")
        return
    buttons = []
    row = []
    for svc in services:
        row.append(InlineKeyboardButton(
            text=f"💎 {svc['name']} - {svc['price']}$",
            callback_data=f"manual:service:{svc['id']}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="manual:back_categories")])
    cats = await db.get_manual_categories(active_only=True)
    cat_name = next((c["name"] for c in cats if c["id"] == cat_id), "")
    await callback.message.edit_text(
        f"🎮 <b>{cat_name}</b>\nاختر الخدمة:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data == "manual:back_categories")
async def manual_back_categories(callback: CallbackQuery):
    await manual_categories(callback)


# --- قسم الأرقام الوهمية ---

VNUM_POPULAR_APPS = [
    ("whatsapp", "💬 واتساب"),
    ("telegram", "✈️ تيليجرام"),
    ("instagram", "📷 انستغرام"),
    ("facebook", "👤 فيسبوك"),
    ("tiktok", "🎵 تيك توك"),
    ("gmail", "📧 جيميل"),
    ("twitter", "🐦 تويتر/X"),
    ("snapchat", "👻 سناب شات"),
    ("viber", "📞 فايبر"),
    ("wechat", "💬 وي شات"),
    ("line", "💬 لاين"),
    ("discord", "🎮 ديسكورد"),
    ("google", "🔍 جوجل"),
    ("youtube", "▶️ يوتيوب"),
    ("microsoft", "🖥️ مايكروسوفت"),
    ("apple", "🍎 آبل"),
    ("paypal", "💰 باي بال"),
    ("amazon", "📦 أمازون"),
    ("uber", "🚗 أوبر"),
    ("tinder", "❤️ تيندر"),
]


@router.callback_query(F.data == "vnumbers:menu")
async def vnumbers_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_banned(user_id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    await callback.answer()
    user = await db.get_user(user_id)
    if not user:
        await callback.message.edit_text("⚠️ يرجى بدء البوت أولاً.")
        return
    provider = await db.get_active_fivesim_provider()
    if provider:
        buttons = [
            [
                InlineKeyboardButton(text="🌍 عبر الدولة", callback_data="vnum:browse:country"),
                InlineKeyboardButton(text="📲 عبر التطبيق", callback_data="vnum:browse:app"),
            ],
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
        ]
        await callback.message.edit_text(
            "📱 <b>الأرقام الوهمية</b>\n\n"
            "اختر طريقة البحث:\n\n"
            "🌍 <b>عبر الدولة</b> — اختر دولة ثم التطبيق\n"
            "📲 <b>عبر التطبيق</b> — اختر التطبيق ثم الدولة",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
    else:
        categories = await db.get_manual_categories(active_only=True)
        vnum_cat = next((c for c in categories if "وهمي" in c["name"] or "أرقام" in c["name"]), None)
        services = await db.get_manual_services_by_category(vnum_cat["id"], active_only=True) if vnum_cat else []
        buttons = []
        row = []
        for svc in services:
            row.append(InlineKeyboardButton(
                text=f"📱 {svc['name']} - {svc['price']}$",
                callback_data=f"manual:service:{svc['id']}"
            ))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        if not services:
            text = "📱 <b>الأرقام الوهمية</b>\n\n⚠️ لا توجد خدمات متاحة حالياً."
        else:
            text = "📱 <b>الأرقام الوهمية</b>\nاختر الخدمة:"
        buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")])
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data == "vnum:browse:country")
async def vnum_browse_by_country(callback: CallbackQuery):
    if await is_banned(callback.from_user.id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    await callback.answer()
    buttons = []
    row = []
    for code, name in VNUM_COUNTRIES.items():
        row.append(InlineKeyboardButton(text=name, callback_data=f"vnum:country:{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="vnumbers:menu")])
    await callback.message.edit_text(
        "🌍 <b>اختر الدولة</b>\n\nسيتم عرض التطبيقات المتاحة في الدولة المختارة:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "vnum:browse:app")
async def vnum_browse_by_app(callback: CallbackQuery):
    if await is_banned(callback.from_user.id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    await callback.answer()
    buttons = []
    row = []
    for app_key, app_name in VNUM_POPULAR_APPS:
        row.append(InlineKeyboardButton(text=app_name, callback_data=f"vnum:app:{app_key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="vnumbers:menu")])
    await callback.message.edit_text(
        "📲 <b>اختر التطبيق</b>\n\nسيتم عرض الدول المتاحة للتطبيق المختار:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("vnum:app:"))
async def vnum_select_app(callback: CallbackQuery):
    if await is_banned(callback.from_user.id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    product = callback.data.split(":")[2]
    app_name = VNUM_SERVICE_NAMES.get(product.lower(), f"📱 {product}")
    buttons = []
    row = []
    for code, name in VNUM_COUNTRIES.items():
        row.append(InlineKeyboardButton(text=name, callback_data=f"vnum:service:{code}:{product}:app"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 رجوع للتطبيقات", callback_data="vnum:browse:app")])
    await callback.answer()
    await callback.message.edit_text(
        f"📲 <b>{app_name}</b>\n\nاختر الدولة التي تريد رقماً منها:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("vnum:country:"))
async def vnum_select_country(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_banned(user_id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    country = callback.data.split(":")[2]
    country_name = VNUM_COUNTRIES.get(country, country)
    provider = await db.get_active_fivesim_provider()
    if not provider:
        await callback.answer("❌ لا يوجد مورد أرقام وهمية نشط.", show_alert=True)
        return
    await callback.answer("⏳ جاري جلب الخدمات المتاحة...")
    try:
        client = FiveSimClient(api_key=provider["api_key"], base_url=provider["api_url"])
        products = await client.get_products(country, "any")
    except Exception as e:
        await callback.message.edit_text(
            f"❌ فشل الاتصال بمورد الأرقام الوهمية.\nحاول مجدداً لاحقاً.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="vnum:browse:country")]
            ])
        )
        return
    if not products or not isinstance(products, dict):
        await callback.message.edit_text(
            f"⚠️ لا توجد أرقام متاحة في {country_name} حالياً.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع للدول", callback_data="vnum:browse:country")]
            ])
        )
        return
    profit_percent = float(await db.get_setting("profit_percent", str(PROFIT_PERCENT)))
    priority_services = ["telegram", "whatsapp", "instagram", "facebook", "tiktok", "gmail", "google", "twitter", "snapchat"]
    all_items = [(k, v) for k, v in products.items() if isinstance(v, dict)]
    priority = [(k, v) for k, v in all_items if k.lower() in priority_services]
    others = [(k, v) for k, v in all_items if k.lower() not in priority_services]
    priority.sort(key=lambda x: x[1].get("Qty", 0), reverse=True)
    others.sort(key=lambda x: x[1].get("Qty", 0), reverse=True)
    sorted_products = (priority + others)[:24]
    buttons = []
    row = []
    for prod_name, prod_data in sorted_products:
        cost = float(prod_data.get("Price", 0))
        if cost == 0:
            continue
        qty = prod_data.get("Qty", 0)
        final_cost = round(cost * (1 + profit_percent / 100), 3)
        display = VNUM_SERVICE_NAMES.get(prod_name.lower(), f"📱 {prod_name}")
        stock_badge = "" if qty > 0 else " ⚠️"
        btn_text = f"{display}{stock_badge} — {final_cost}$"
        row.append(InlineKeyboardButton(
            text=btn_text,
            callback_data=f"vnum:service:{country}:{prod_name}"
        ))
        if len(row) == 1:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    if not buttons:
        await callback.message.edit_text(
            f"⚠️ لا توجد أرقام متاحة في {country_name} حالياً.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع للدول", callback_data="vnum:browse:country")]
            ])
        )
        return
    buttons.append([InlineKeyboardButton(text="🔙 رجوع للدول", callback_data="vnum:browse:country")])
    await callback.message.edit_text(
        f"📱 <b>الأرقام الوهمية — {country_name}</b>\n\n"
        f"⚠️ الخدمات التي تحمل علامة ⚠️ قد يكون مخزونها محدوداً.\n\n"
        f"اختر الخدمة:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )



@router.callback_query(F.data.startswith("vnum:service:"))
async def vnum_select_service(callback: CallbackQuery):
    """عرض المشغّلين المتاحين مع أسعارهم بعد اختيار الخدمة"""
    import math as _math
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user or await is_banned(user_id):
        await callback.answer("🚫", show_alert=True)
        return
    parts = callback.data.split(":")
    country = parts[2]
    product = parts[3]
    # parts[4] = "app" إذا جاء من "عبر التطبيق"، غير موجود أو غيره = "country"
    origin = parts[4] if len(parts) > 4 else "country"
    back_cb = f"vnum:app:{product}" if origin == "app" else f"vnum:country:{country}"
    country_name = VNUM_COUNTRIES.get(country, country)
    service_name = VNUM_SERVICE_NAMES.get(product.lower(), f"📱 {product}")
    provider = await db.get_active_fivesim_provider()
    if not provider:
        await callback.answer("❌ لا يوجد مورد نشط.", show_alert=True)
        return
    await callback.answer("⏳ جاري جلب المشغّلين المتاحين...")
    operators = []
    try:
        client = FiveSimClient(api_key=provider["api_key"], base_url=provider["api_url"])
        operators = await client.get_operator_prices(country, product)
    except Exception as e:
        logger.error(f"vnum:service get_operator_prices error: {e}")
    if not operators:
        try:
            client = FiveSimClient(api_key=provider["api_key"], base_url=provider["api_url"])
            products_data = await client.get_products(country, "any")
            prod_data = products_data.get(product, {})
            if isinstance(prod_data, dict) and prod_data.get("Qty", 0) > 0:
                operators = [{"operator": "any", "cost": float(prod_data.get("Price", 0)),
                              "count": prod_data.get("Qty", 0), "rate": 0}]
        except Exception as e:
            logger.error(f"vnum:service fallback error: {e}")
    if not operators:
        await callback.message.edit_text(
            f"⚠️ لا يوجد مشغّل متاح لـ <b>{service_name}</b> في {country_name} حالياً.\n"
            "جرّب دولة أو خدمة أخرى.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 رجوع", callback_data=back_cb)
            ]])
        )
        return
    profit_percent = float(await db.get_setting("profit_percent", str(PROFIT_PERCENT)))
    balance = float(user["balance"])
    op_labels = {
        "any": "أي مشغّل", "virtual1": "Virtual1", "virtual2": "Virtual2",
        "virtual3": "Virtual3", "virtual4": "Virtual4", "virtual5": "Virtual5",
        "virtual6": "Virtual6", "virtual7": "Virtual7", "virtual8": "Virtual8",
        "virtual9": "Virtual9", "virtual10": "Virtual10", "virtual11": "Virtual11",
        "virtual12": "Virtual12", "virtual13": "Virtual13", "virtual14": "Virtual14",
        "virtual15": "Virtual15", "virtual16": "Virtual16", "virtual17": "Virtual17",
        "virtual18": "Virtual18", "virtual19": "Virtual19", "virtual20": "Virtual20",
        "virtual21": "Virtual21", "virtual22": "Virtual22",
    }
    buttons = []
    for op in operators:
        op_name = op["operator"]
        provider_price = op["cost"]
        user_price = provider_price * (1 + profit_percent / 100)
        display_price = _math.ceil(user_price * 100) / 100
        count = op["count"]
        rate = op.get("rate", 0)
        op_label = op_labels.get(op_name, op_name.title())
        rate_str = f" • {rate:.0f}%" if rate > 0 else ""
        icon = "✅" if balance >= display_price else "💸"
        btn_text = f"{icon} {op_label} — {display_price}$ ({count:,} رقم{rate_str})"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"vnum:operator:{country}:{product}:{op_name}:{origin}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data=back_cb)])
    await callback.message.edit_text(
        f"📱 <b>{service_name}</b>\n"
        f"🌍 {country_name}\n"
        f"💰 رصيدك: <b>{balance:.3f}$</b>\n\n"
        f"اختر المشغّل المناسب:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("vnum:operator:"))
async def vnum_select_operator(callback: CallbackQuery):
    """عرض صفحة التأكيد بعد اختيار المشغّل"""
    import math as _math
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user or await is_banned(user_id):
        await callback.answer("🚫", show_alert=True)
        return
    parts = callback.data.split(":")
    country = parts[2]
    product = parts[3]
    operator = parts[4]
    country_name = VNUM_COUNTRIES.get(country, country)
    service_name = VNUM_SERVICE_NAMES.get(product.lower(), f"📱 {product}")
    op_labels = {
        "any": "أي مشغّل", "virtual1": "Virtual1", "virtual2": "Virtual2",
        "virtual3": "Virtual3", "virtual4": "Virtual4", "virtual5": "Virtual5",
        "virtual6": "Virtual6", "virtual7": "Virtual7", "virtual8": "Virtual8",
        "virtual9": "Virtual9", "virtual10": "Virtual10", "virtual11": "Virtual11",
        "virtual12": "Virtual12", "virtual13": "Virtual13", "virtual14": "Virtual14",
        "virtual15": "Virtual15", "virtual16": "Virtual16", "virtual17": "Virtual17",
        "virtual18": "Virtual18", "virtual19": "Virtual19", "virtual20": "Virtual20",
        "virtual21": "Virtual21", "virtual22": "Virtual22",
    }
    op_label = op_labels.get(operator, operator.title())
    provider = await db.get_active_fivesim_provider()
    if not provider:
        await callback.answer("❌ لا يوجد مورد نشط.", show_alert=True)
        return
    await callback.answer("⏳ جاري التحقق من السعر...")
    try:
        client = FiveSimClient(api_key=provider["api_key"], base_url=provider["api_url"])
        products_data = await client.get_products(country, operator)
        prod_data = products_data.get(product, {})
        provider_price = float(prod_data.get("Price", 0)) if isinstance(prod_data, dict) else 0.0
        count = int(prod_data.get("Qty", 0)) if isinstance(prod_data, dict) else 0
    except Exception as e:
        logger.error(f"vnum:operator price check error: {e}")
        await callback.message.edit_text(
            "❌ تعذّر جلب السعر، حاول مجدداً.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 رجوع", callback_data=f"vnum:service:{country}:{product}")
            ]])
        )
        return
    profit_percent = float(await db.get_setting("profit_percent", str(PROFIT_PERCENT)))
    user_price = provider_price * (1 + profit_percent / 100)
    display_price = _math.ceil(user_price * 100) / 100
    balance = float(user["balance"])
    enough = balance >= display_price
    kb_rows = []
    if enough and count > 0:
        kb_rows.append([InlineKeyboardButton(
            text=f"✅ شراء الرقم — {display_price}$",
            callback_data=f"vnum:confirm:{country}:{product}:{operator}"
        )])
    elif not enough:
        kb_rows.append([InlineKeyboardButton(
            text="💰 شحن الرصيد", callback_data="charge:menu"
        )])
    kb_rows.append([InlineKeyboardButton(
        text="🔙 رجوع للمشغّلين", callback_data=f"vnum:service:{country}:{product}"
    )])
    status_line = ""
    if not enough:
        status_line = f"\n⚠️ رصيدك غير كافٍ — تحتاج <b>{display_price}$</b>"
    elif count == 0:
        status_line = "\n⚠️ لا توجد أرقام متاحة حاليًا"
    await callback.message.edit_text(
        f"📱 <b>{service_name}</b>\n"
        f"🌍 الدولة: {country_name}\n"
        f"📡 المشغّل: <b>{op_label}</b>\n"
        f"📦 المتاح: {count:,} رقم\n"
        f"💵 السعر: <b>{display_price}$</b>\n"
        f"💰 رصيدك: <b>{balance:.3f}$</b>"
        f"{status_line}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows)
    )


@router.callback_query(F.data.startswith("vnum:confirm:"))
async def vnum_confirm_buy(callback: CallbackQuery):
    """تنفيذ الشراء الفعلي من 5SIM"""
    import math as _math
    user_id = callback.from_user.id

    # ── Rate limit + idempotency ──
    if not _order_rate_limiter.is_allowed(user_id):
        await callback.answer("⚠️ طلبات كثيرة جداً، انتظر دقيقة ثم حاول.", show_alert=True)
        return
    if user_id in pending_orders:
        await callback.answer("⏳ طلبك قيد المعالجة، انتظر قليلاً.", show_alert=True)
        return
    pending_orders.add(user_id)

    try:
        user = await db.get_user(user_id)
        if not user or await is_banned(user_id):
            await callback.answer("🚫", show_alert=True)
            return
        parts = callback.data.split(":")
        country = parts[2]
        product = parts[3]
        operator = parts[4] if len(parts) > 4 else "any"
        country_name = VNUM_COUNTRIES.get(country, country)
        service_name = VNUM_SERVICE_NAMES.get(product.lower(), f"📱 {product}")
        provider = await db.get_active_fivesim_provider()
        if not provider:
            await callback.answer("❌ لا يوجد مورد نشط.", show_alert=True)
            return
        await callback.answer("⏳ جاري شراء الرقم...")

        raw_key = provider["api_key"] or ""
        clean_key = raw_key.strip()
        if clean_key.lower().startswith("bearer "):
            clean_key = clean_key[7:].strip()
        key_preview = (clean_key[:6] + "****" + clean_key[-4:]) if len(clean_key) > 10 else "(فارغ)"
        base_url = _normalize_fivesim_url(provider["api_url"] or "")
        client = FiveSimClient(api_key=raw_key, base_url=provider["api_url"])

        # 1. جلب السعر الحقيقي من 5SIM
        products_data = await client.get_products(country, operator)
        prod_data = products_data.get(product, {})
        provider_price = float(prod_data.get("Price", 0)) if isinstance(prod_data, dict) else 0.0

        profit_percent = float(await db.get_setting("profit_percent", str(PROFIT_PERCENT)))
        user_price = provider_price * (1 + profit_percent / 100)
        display_price = _math.ceil(user_price * 100) / 100
        profit_amount = round(display_price - provider_price, 4)
        balance = float(user["balance"])

        # 2. فحص رصيد 5SIM
        provider_balance = await client.get_provider_balance()
        buy_url = f"{base_url}/user/buy/activation/{country}/{operator}/{product}"

        logger.info(
            f"5SIM BUY DEBUG | user_id={user_id} provider_id={provider['id']} "
            f"country={country} product={product} operator={operator} "
            f"buy_url={buy_url} api_key_preview={key_preview} "
            f"provider_price={provider_price} profit_percent={profit_percent} "
            f"profit_amount={profit_amount} user_price={user_price} display_price={display_price} "
            f"user_balance={balance} provider_balance={provider_balance}"
        )

        # 3. فحص رصيد المستخدم
        if balance < display_price:
            await callback.message.edit_text(
                f"❌ رصيدك غير كافٍ\n\n"
                f"سعر الرقم: <b>{display_price}$</b>\n"
                f"رصيدك: <b>{balance:.3f}$</b>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💰 شحن الرصيد", callback_data="charge:menu")],
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="vnumbers:menu")],
                ])
            )
            return

        # 4. فحص رصيد 5SIM
        if 0 <= provider_balance < provider_price:
            logger.warning(f"5SIM provider balance {provider_balance} < required {provider_price}")
            await callback.message.edit_text(
                "❌ رصيد حساب 5SIM غير كافٍ لشراء هذا الرقم\nتواصل مع الأدمن",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 رجوع", callback_data="vnumbers:menu")
                ]])
            )
            return

        # 5. الشراء الفعلي
        order = await client.buy_activation(country, operator, product)
        http_status = order.get("_status", 0)
        body_raw = (order.get("message", "") or "").strip()

        logger.info(
            f"5SIM BUY DEBUG | status={http_status} raw_body={body_raw[:200]} "
            f"has_phone={'phone' in order} result={'SUCCESS' if 'phone' in order else 'FAIL'}"
        )

        # 6. معالجة الأخطاء
        ERR_MAP = {
            "not enough user balance": "❌ رصيد حساب 5SIM غير كافٍ\nتواصل مع الأدمن لإعادة الشحن",
            "no free phones":          "❌ لا توجد أرقام متاحة حاليًا\nجرّب مشغّلاً أو دولة أخرى",
            "no product":              "❌ الخدمة غير متوفرة في هذه الدولة",
            "bad country":             "❌ الدولة غير صحيحة",
            "bad operator":            "❌ المشغّل غير صحيح أو غير متاح",
            "not enough product":      "❌ الكمية المطلوبة غير متوفرة",
            "server offline":          "❌ خادم 5SIM غير متاح حاليًا، حاول لاحقاً",
            "bad api_key":             "❌ مفتاح API خاطئ، تواصل مع الأدمن",
            "invalid_url":             "❌ خطأ في إعدادات المورد",
            "connection_error":        "❌ فشل الاتصال بخادم 5SIM، حاول لاحقاً",
        }

        if http_status == 401:
            await callback.message.edit_text(
                "❌ مفتاح 5SIM غير صحيح (401)\n"
                "استخدم <b>API key for 5SIM protocol</b> وليس Deprecated API",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 رجوع", callback_data="vnumbers:menu")
                ]])
            )
            return

        if http_status == 403:
            await callback.message.edit_text(
                "❌ وصول مرفوض من 5SIM (403)\nتواصل مع الأدمن",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 رجوع", callback_data="vnumbers:menu")
                ]])
            )
            return

        if "phone" not in order or "id" not in order:
            err_msg = ERR_MAP.get(body_raw, f"❌ تعذّر شراء الرقم حاليًا\nالسبب: {body_raw or 'غير معروف'}")
            await callback.message.edit_text(
                err_msg,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 رجوع", callback_data="vnumbers:menu")
                ]])
            )
            return

        # 7. نجاح — احسب السعر الفعلي من رد 5SIM إن وُجد
        actual_provider_price = float(order.get("price", provider_price))
        actual_user_price = actual_provider_price * (1 + profit_percent / 100)
        actual_display_price = _math.ceil(actual_user_price * 100) / 100

        fivesim_order_id = order["id"]
        phone = order["phone"]

        # 8. خصم ذري — يجب أن ينجح وإلا نلغي الطلب عند 5SIM
        deducted = await db.deduct_balance_atomic(
            user_id, actual_display_price,
            f"رقم وهمي {service_name} — {country_name} ({operator})"
        )
        if not deducted:
            # حاول إلغاء الطلب في 5SIM لاسترداد الرصيد هناك أيضاً
            try:
                await client.cancel_order(fivesim_order_id)
            except Exception:
                pass
            logger.error(
                "vnum deduction failed after 5SIM success | user_id=%s fivesim_order=%s amount=%s",
                user_id, fivesim_order_id, actual_display_price
            )
            await callback.message.edit_text(
                "❌ خطأ في خصم الرصيد — تم إلغاء الطلب تلقائياً.\n"
                "حاول مجدداً أو تواصل مع الدعم.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 رجوع", callback_data="vnumbers:menu")
                ]])
            )
            return

        await db.save_vnum_order(user_id, fivesim_order_id, phone,
                                 country, product, operator, actual_display_price)
        logger.info(
            "vnum order success | user_id=%s fivesim_order=%s phone=%s amount=%s",
            user_id, fivesim_order_id, phone, actual_display_price,
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📨 تحقق من الكود", callback_data=f"vnum:check:{fivesim_order_id}")],
            [InlineKeyboardButton(text="❌ إلغاء واسترجاع", callback_data=f"vnum:cancel:{fivesim_order_id}")],
            [InlineKeyboardButton(text="✅ انتهيت", callback_data=f"vnum:finish:{fivesim_order_id}")],
        ])
        await callback.message.edit_text(
            f"✅ <b>تم شراء الرقم بنجاح!</b>\n\n"
            f"📱 الرقم: <code>{phone}</code>\n"
            f"🌍 الدولة: {country_name}\n"
            f"💎 الخدمة: {service_name}\n"
            f"📡 المشغّل: {operator}\n"
            f"💵 التكلفة: {actual_display_price}$\n\n"
            f"⏳ انتظر وصول رسالة SMS ثم اضغط <b>تحقق من الكود</b>.",
            reply_markup=kb
        )

    except Exception as e:
        logger.error("vnum_confirm_buy unexpected error | user_id=%s", user_id, exc_info=True)
        try:
            await callback.message.edit_text(
                "❌ حدث خطأ أثناء تنفيذ الطلب، لم يتم خصم أي مبلغ إذا لم يكتمل الطلب.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 رجوع", callback_data="vnumbers:menu")
                ]])
            )
        except Exception:
            pass
    finally:
        pending_orders.discard(user_id)



@router.callback_query(F.data.startswith("vnum:check:"))
async def vnum_check_sms(callback: CallbackQuery):
    fivesim_order_id = int(callback.data.split(":")[2])
    order_row = await db.get_vnum_order(fivesim_order_id)
    if not order_row or order_row["user_id"] != callback.from_user.id:
        await callback.answer("❌ طلب غير موجود.", show_alert=True)
        return
    provider = await db.get_active_fivesim_provider()
    if not provider:
        await callback.answer("❌ لا يوجد مورد نشط.", show_alert=True)
        return
    await callback.answer("⏳ جاري التحقق...")
    try:
        client = FiveSimClient(api_key=provider["api_key"], base_url=provider["api_url"])
        result = await client.check_order(fivesim_order_id)
    except Exception:
        await callback.answer("❌ فشل الاتصال بـ 5SIM.", show_alert=True)
        return
    status = result.get("status", "")
    sms_list = result.get("sms", [])
    phone = order_row["phone"]
    country_name = VNUM_COUNTRIES.get(order_row["country"], order_row["country"])
    service_name = VNUM_SERVICE_NAMES.get(order_row["product"].lower(), order_row["product"])
    if sms_list:
        # وصل الكود
        first_sms = sms_list[0] if isinstance(sms_list, list) else sms_list
        sms_text = first_sms.get("text", "") if isinstance(first_sms, dict) else str(first_sms)
        sms_code = first_sms.get("code", "") if isinstance(first_sms, dict) else ""
        await db.update_vnum_order(fivesim_order_id, "RECEIVED", sms_code or sms_text)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ انتهيت (إنهاء الطلب)", callback_data=f"vnum:finish:{fivesim_order_id}")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main:menu")],
        ])
        await callback.message.edit_text(
            f"✅ <b>وصل الكود!</b>\n\n"
            f"📱 الرقم: <code>{phone}</code>\n"
            f"💬 رسالة SMS:\n<code>{sms_text}</code>\n"
            + (f"🔑 الكود: <b><code>{sms_code}</code></b>\n" if sms_code else "")
            + f"\n🌍 الدولة: {country_name} | 💎 الخدمة: {service_name}",
            reply_markup=kb
        )
    else:
        # لم يصل الكود بعد
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 تحقق مجدداً", callback_data=f"vnum:check:{fivesim_order_id}")],
            [InlineKeyboardButton(text="❌ إلغاء واسترجاع", callback_data=f"vnum:cancel:{fivesim_order_id}")],
            [InlineKeyboardButton(text="✅ انتهيت", callback_data=f"vnum:finish:{fivesim_order_id}")],
        ])
        await callback.message.edit_text(
            f"⏳ <b>لم يصل الكود بعد</b>\n\n"
            f"📱 الرقم: <code>{phone}</code>\n"
            f"🌍 الدولة: {country_name} | 💎 الخدمة: {service_name}\n\n"
            f"اضغط <b>تحقق مجدداً</b> بعد ثوانٍ.",
            reply_markup=kb
        )


@router.callback_query(F.data.startswith("vnum:cancel:"))
async def vnum_cancel_order(callback: CallbackQuery):
    fivesim_order_id = int(callback.data.split(":")[2])
    order_row = await db.get_vnum_order(fivesim_order_id)
    if not order_row or order_row["user_id"] != callback.from_user.id:
        await callback.answer("❌ طلب غير موجود.", show_alert=True)
        return
    if order_row["status"] in ("CANCELLED", "RECEIVED", "FINISHED"):
        await callback.answer("⚠️ لا يمكن إلغاء هذا الطلب.", show_alert=True)
        return
    provider = await db.get_active_fivesim_provider()
    await callback.answer("⏳ جاري الإلغاء...")
    refunded = False
    try:
        if provider:
            client = FiveSimClient(api_key=provider["api_key"], base_url=provider["api_url"])
            await client.cancel_order(fivesim_order_id)
        refunded = True
    except Exception:
        pass
    await db.update_vnum_order(fivesim_order_id, "CANCELLED")
    cost = float(order_row["cost"])
    if refunded and cost > 0:
        await db.add_balance(order_row["user_id"], cost, f"استرجاع رقم وهمي ملغى #{fivesim_order_id}")
    await callback.message.edit_text(
        f"❌ <b>تم إلغاء الطلب</b>\n\n"
        + (f"↩️ تم استرجاع <b>{cost}$</b> إلى رصيدك." if refunded else "⚠️ فشل الإلغاء عند المورد، تواصل مع الدعم.")
        + f"\n\n📱 الرقم: {order_row['phone']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main:menu")]
        ])
    )


@router.callback_query(F.data.startswith("vnum:finish:"))
async def vnum_finish_order(callback: CallbackQuery):
    fivesim_order_id = int(callback.data.split(":")[2])
    order_row = await db.get_vnum_order(fivesim_order_id)
    if not order_row or order_row["user_id"] != callback.from_user.id:
        await callback.answer("❌ طلب غير موجود.", show_alert=True)
        return
    provider = await db.get_active_fivesim_provider()
    await callback.answer("✅ جاري إنهاء الطلب...")
    try:
        if provider:
            client = FiveSimClient(api_key=provider["api_key"], base_url=provider["api_url"])
            await client.finish_order(fivesim_order_id)
    except Exception:
        pass
    await db.update_vnum_order(fivesim_order_id, "FINISHED")
    await callback.message.edit_text(
        f"✅ <b>تم إنهاء الطلب بنجاح</b>\n\n"
        f"📱 الرقم: {order_row['phone']}\n"
        f"شكراً لاستخدامك خدماتنا!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main:menu")]
        ])
    )


@router.callback_query(F.data.startswith("manual:back_services:"))
async def manual_back_services(callback: CallbackQuery):
    cat_id = int(callback.data.split(":")[2])
    callback.data = f"manual:category:{cat_id}"
    await manual_category_services(callback)


@router.callback_query(F.data.startswith("manual:service:"))
async def manual_service_detail(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_banned(user_id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    service_id = int(callback.data.split(":")[2])
    await callback.answer()
    svc = await db.get_manual_service(service_id)
    if not svc:
        await callback.message.edit_text("❌ الخدمة غير موجودة.")
        return
    text = (
        f"💎 <b>{svc['name']}</b>\n\n"
        f"💰 <b>السعر:</b> {svc['price']}$\n"
    )
    if svc["description"]:
        text += f"📝 <b>الوصف:</b> {svc['description']}\n"
    if svc["instructions"]:
        text += f"📋 <b>التعليمات:</b> {svc['instructions']}\n"
    text += f"\nاضغط <b>طلب الخدمة</b> لإتمام الطلب."
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ طلب الخدمة", callback_data=f"manual:order:{service_id}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data=f"manual:back_services:{svc['category_id']}")],
    ])
    await callback.message.edit_text(text, reply_markup=kb)


@router.callback_query(F.data.startswith("manual:order:"))
async def manual_order_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    service_id = int(callback.data.split(":")[2])
    await callback.answer()
    svc = await db.get_manual_service(service_id)
    if not svc:
        await callback.message.edit_text("❌ الخدمة غير موجودة.")
        return
    balance = await db.get_user_balance(user_id)
    if balance < svc["price"]:
        await callback.message.edit_text(
            f"❌ رصيدك غير كافٍ.\n\n💳 رصيدك: {balance}$\n💰 سعر الخدمة: {svc['price']}$",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 شحن الحساب", callback_data="charge:menu")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
            ]),
        )
        return
    # استخدام حقل instructions كنص المطلوب من المستخدم إذا كان موجوداً
    instructions = svc["instructions"] if svc["instructions"] else ""
    dtype = svc["required_data_type"] or "text"
    if instructions:
        prompt = instructions
    elif dtype == "id":
        prompt = "🆔 أدخل معرف الحساب (ID):"
    elif dtype == "email":
        prompt = "📧 أدخل البريد الإلكتروني:"
    elif dtype == "phone":
        prompt = "📱 أدخل رقم الهاتف:"
    else:
        prompt = "📝 أدخل المعلومات المطلوبة:"
    await state.set_state(ManualOrderStates.waiting_data)
    await state.update_data(service_id=service_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="main:menu")]
    ])
    await callback.message.edit_text(
        f"💎 <b>{svc['name']}</b>\n\n{prompt}",
        reply_markup=kb,
    )


@router.message(ManualOrderStates.waiting_data)
async def manual_order_data(message: Message, state: FSMContext):
    user_data = message.text.strip()
    data = await state.get_data()
    service_id = data["service_id"]
    svc = await db.get_manual_service(service_id)
    await state.update_data(user_data=user_data)
    await state.set_state(ManualOrderStates.confirming)
    text = (
        f"📋 <b>ملخص الطلب:</b>\n\n"
        f"💎 الخدمة: {svc['name']}\n"
        f"📝 البيانات المدخلة: {user_data}\n"
        f"💰 السعر: {svc['price']}$\n\n"
        f"هل تريد تأكيد الطلب؟"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تأكيد", callback_data="manual:confirm"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="main:menu"),
        ]
    ])
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "manual:confirm")
async def manual_order_confirm(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # ── Rate limit + idempotency ──
    if not _order_rate_limiter.is_allowed(user_id):
        await callback.answer("⚠️ طلبات كثيرة جداً، انتظر دقيقة ثم حاول.", show_alert=True)
        return
    if user_id in pending_orders:
        await callback.answer("⏳ طلبك قيد المعالجة.", show_alert=True)
        return
    pending_orders.add(user_id)
    await callback.answer("⏳ جاري معالجة طلبك...")
    try:
        data = await state.get_data()
        service_id = data.get("service_id")
        user_data_val = data.get("user_data", "")

        # ── إعادة جلب الخدمة وسعرها من DB (لا من state) ──
        svc = await db.get_manual_service(service_id)
        if not svc:
            await callback.message.edit_text("❌ الخدمة غير موجودة.")
            await state.clear()
            return

        price = float(svc["price"])

        # ── خصم ذري ──
        deducted = await db.deduct_balance_atomic(
            user_id, price, f"طلب يدوي: {svc['name']}"
        )
        if not deducted:
            await callback.message.edit_text(
                "❌ رصيدك غير كافٍ لإتمام هذا الطلب.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💳 شحن الحساب", callback_data="charge:menu")],
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
                ]),
            )
            await state.clear()
            return

        order_id = await db.create_manual_order(
            user_id=user_id,
            service_id=service_id,
            service_name=svc["name"],
            user_data=user_data_val,
            price=price,
        )
        logger.info(
            "Manual order created | order_id=%s user_id=%s service=%s price=%s",
            order_id, user_id, svc["name"], price,
        )
        user = await db.get_user(user_id)
        username_str = f"@{user['username']}" if user["username"] else "لا يوجد"
        admin_text = (
            f"📦 <b>طلب يدوي جديد #{order_id}</b>\n\n"
            f"👤 الاسم: {user['full_name']}\n"
            f"🆔 ID: {user_id}\n"
            f"📱 يوزر: {username_str}\n"
            f"💎 الخدمة: {svc['name']}\n"
            f"📝 البيانات: {user_data_val}\n"
            f"💰 السعر: {price}$\n"
            f"📅 التاريخ: {callback.message.date}"
        )
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ تنفيذ بدون رسالة", callback_data=f"admin:morder:done:{order_id}"),
                InlineKeyboardButton(text="✉️ تنفيذ مع رسالة", callback_data=f"admin:morder:respond:{order_id}"),
            ],
            [InlineKeyboardButton(text="❌ إلغاء وإرجاع الرصيد", callback_data=f"admin:morder:cancel:{order_id}")],
        ])
        await bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_kb)
        new_balance = await db.get_user_balance(user_id)
        await callback.message.edit_text(
            f"✅ <b>تم إرسال طلبك بنجاح!</b>\n\n"
            f"📦 رقم الطلب: #{order_id}\n"
            f"💰 المبلغ المخصوم: {price}$\n"
            f"💳 رصيدك المتبقي: {new_balance}$\n\n"
            f"سيتم مراجعة طلبك وتنفيذه في أقرب وقت.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📦 طلباتي", callback_data="orders:list")],
                [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main:menu")],
            ]),
        )
    except Exception:
        logger.error("manual_order_confirm | user_id=%s", user_id, exc_info=True)
        await send_admin_error(f"manual_order_confirm: {traceback.format_exc()}")
        await callback.message.edit_text(
            "❌ حدث خطأ أثناء تنفيذ الطلب، لم يتم خصم أي مبلغ إذا لم يكتمل الطلب."
        )
    finally:
        pending_orders.discard(user_id)
        await state.clear()


# =============================================
# شحن الحساب
# =============================================

@router.callback_query(F.data == "charge:menu")
async def charge_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_banned(user_id):
        await callback.answer("🚫 تم حظرك.", show_alert=True)
        return
    await callback.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ الشحن عبر نجوم تيليجرام", callback_data="charge:stars")],
        [InlineKeyboardButton(text="💰 الشحن اليدوي عبر العملات الرقمية", callback_data="charge:crypto:menu")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
    ])
    await callback.message.edit_text(
        "💳 <b>شحن الحساب</b>\nاختر طريقة الدفع:",
        reply_markup=kb,
    )


# --- Stars ---

@router.callback_query(F.data == "charge:stars")
async def charge_stars(callback: CallbackQuery):
    buttons = []
    for pkg in STARS_PACKAGES:
        buttons.append([InlineKeyboardButton(
            text=f"⭐ {pkg['stars']} نجمة = {pkg['usd']}$",
            callback_data=f"charge:stars:buy:{pkg['usd']}:{pkg['stars']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="charge:menu")])
    await callback.message.edit_text(
        "⭐ <b>الشحن عبر نجوم تيليجرام</b>\n\n"
        f"المعادلة: {STARS_RATE} نجمة = 1$\n\n"
        "اختر الباقة:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("charge:stars:buy:"))
async def charge_stars_buy(callback: CallbackQuery):
    parts = callback.data.split(":")
    usd = int(parts[3])
    stars = int(parts[4])
    try:
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=f"شحن {usd}$ عبر نجوم تيليجرام",
            description=f"شحن رصيد بقيمة {usd}$ مقابل {stars} نجمة تيليجرام",
            payload=f"stars_{usd}_{stars}_{callback.from_user.id}",
            currency="XTR",
            prices=[LabeledPrice(label=f"شحن {usd}$", amount=stars)],
        )
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ فشل إنشاء الفاتورة.", show_alert=True)
        await send_admin_error(f"stars invoice error: {e}")


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    stars = message.successful_payment.total_amount
    stars_rate = int(await db.get_setting("stars_rate", str(STARS_RATE)))
    usd = round(stars / stars_rate, 2)
    await db.add_balance(user_id, usd, f"شحن عبر نجوم تيليجرام ({stars} نجمة)")
    await db.create_payment(
        user_id=user_id,
        amount=usd,
        method="stars",
        network="telegram",
        wallet_address="",
        proof_photo_id="",
    )
    payment_id = None
    payments = await db.get_pending_payments()
    new_balance = await db.get_user_balance(user_id)
    await message.answer(
        f"✅ <b>تم الشحن بنجاح!</b>\n\n"
        f"⭐ النجوم المدفوعة: {stars}\n"
        f"💰 المبلغ المضاف: {usd}$\n"
        f"💳 رصيدك الحالي: {new_balance}$",
        reply_markup=build_main_menu(user_id),
    )


# --- Crypto ---

@router.callback_query(F.data == "charge:crypto:menu")
async def charge_crypto_menu(callback: CallbackQuery):
    wallets = {}
    for key in ["wallet_btc", "wallet_usdt_bep20", "wallet_ton_gram", "wallet_ltc", "wallet_sol"]:
        wallets[key] = await db.get_setting(key)
    network_names = {
        "wallet_btc": "BTC",
        "wallet_usdt_bep20": "USDT BEP20",
        "wallet_ton_gram": "TON / GRAM",
        "wallet_ltc": "LTC",
        "wallet_sol": "SOL",
    }
    buttons = []
    for key, name in network_names.items():
        buttons.append([InlineKeyboardButton(
            text=f"💰 {name}",
            callback_data=f"charge:crypto:{key}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="charge:menu")])
    await callback.message.edit_text(
        "💰 <b>الشحن اليدوي عبر العملات الرقمية</b>\nاختر الشبكة:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("charge:crypto:wallet_"))
async def charge_crypto_select(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("charge:crypto:")[1]
    network_names = {
        "wallet_btc": "BTC",
        "wallet_usdt_bep20": "USDT BEP20",
        "wallet_ton_gram": "TON / GRAM",
        "wallet_ltc": "LTC",
        "wallet_sol": "SOL",
    }
    network = network_names.get(key, key)
    wallet = await db.get_setting(key)
    await state.set_state(PaymentStates.waiting_amount)
    await state.update_data(network=network, wallet=wallet, wallet_key=key)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تم التحويل", callback_data="charge:crypto:transferred")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="charge:crypto:menu")],
    ])
    await callback.message.edit_text(
        f"💰 <b>شحن عبر {network}</b>\n\n"
        f"📬 عنوان المحفظة:\n<code>{wallet}</code>\n\n"
        f"1. قم بتحويل المبلغ المطلوب إلى العنوان أعلاه.\n"
        f"2. اضغط <b>تم التحويل</b> لإرسال إثبات الدفع.",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data == "charge:crypto:transferred", PaymentStates.waiting_amount)
async def charge_crypto_transferred(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="charge:crypto:menu")]
    ])
    await callback.message.edit_text(
        "💵 <b>أدخل المبلغ المحوّل بالدولار (مثال: 10):</b>",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(PaymentStates.waiting_amount)
async def charge_amount_input(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ المبلغ غير صالح. أدخل رقماً موجباً.")
        return
    await state.update_data(amount=amount)
    await state.set_state(PaymentStates.waiting_proof)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="main:menu")]
    ])
    await message.answer(
        "📸 <b>أرسل صورة إثبات التحويل:</b>\n(لن يقبل الطلب بدون صورة)",
        reply_markup=kb,
    )


@router.message(PaymentStates.waiting_proof, F.photo)
async def charge_proof_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    amount = data["amount"]
    network = data["network"]
    wallet = data["wallet"]
    payment_id = await db.create_payment(
        user_id=user_id,
        amount=amount,
        method="crypto",
        network=network,
        wallet_address=wallet,
        proof_photo_id=photo_id,
    )
    user = await db.get_user(user_id)
    username_str = f"@{user['username']}" if user["username"] else "لا يوجد"
    admin_text = (
        f"💳 <b>طلب شحن يدوي جديد #{payment_id}</b>\n\n"
        f"👤 الاسم: {user['full_name']}\n"
        f"🆔 ID: {user_id}\n"
        f"📱 يوزر: {username_str}\n"
        f"💰 المبلغ: {amount}$\n"
        f"🌐 الشبكة: {network}\n"
        f"📬 المحفظة: {wallet}\n"
        f"📊 الحالة: قيد المراجعة"
    )
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ قبول وتحديد المبلغ", callback_data=f"admin:payment:approve_ask:{payment_id}")],
        [InlineKeyboardButton(text="❌ رفض الطلب", callback_data=f"admin:payment:reject:{payment_id}")],
    ])
    await bot.send_photo(ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_kb)
    await state.clear()
    await message.answer(
        f"✅ <b>تم إرسال طلب الشحن بنجاح!</b>\n\n"
        f"رقم الطلب: #{payment_id}\n"
        f"المبلغ: {amount}$\n"
        f"الشبكة: {network}\n\n"
        f"سيتم مراجعة طلبك وإضافة الرصيد خلال فترة قصيرة.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main:menu")]
        ]),
    )


@router.message(PaymentStates.waiting_proof)
async def charge_proof_not_photo(message: Message):
    await message.answer("❌ يجب إرسال <b>صورة</b> إثبات التحويل فقط.")


# =============================================
# حسابي ورصيدي
# =============================================

@router.callback_query(F.data == "account:menu")
async def account_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.answer()
        return
    orders_count = await db.get_user_orders_count(user_id)
    ref_stats = await db.get_referral_stats(user_id)
    username_str = f"@{user['username']}" if user["username"] else "لا يوجد"
    text = (
        f"👤 <b>حسابك</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 الاسم: {user['full_name']}\n"
        f"📱 يوزر: {username_str}\n"
        f"💰 الرصيد الحالي: <b>{user['balance']}$</b>\n"
        f"📦 عدد الطلبات: {orders_count}\n"
        f"🎁 عدد الدعوات: {ref_stats['count']}\n"
        f"💵 أرباح الدعوات: {ref_stats['earnings']}$"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 تحويل رصيد لصديق", callback_data="transfer:start")],
        [
            InlineKeyboardButton(text="📦 طلباتي", callback_data="orders:list"),
            InlineKeyboardButton(text="🎁 رابط الدعوة", callback_data="referral:show"),
        ],
        [InlineKeyboardButton(text="📊 سجل معاملاتي", callback_data="account:transactions")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "account:transactions")
async def account_transactions(callback: CallbackQuery):
    user_id = callback.from_user.id
    summary = await db.get_user_transaction_summary(user_id)
    transactions = await db.get_user_transactions(user_id, limit=20)
    text = (
        f"📊 <b>سجل معاملاتك</b>\n\n"
        f"💳 إجمالي الشحن: <b>{summary['total_charged']}$</b>\n"
        f"💸 إجمالي الإنفاق: <b>{summary['total_spent']}$</b>\n"
        f"↩️ إجمالي المسترجع: <b>{summary['total_refunded']}$</b>\n"
        f"❌ خدمات ملغاة (مسترجعة): <b>{summary['cancelled_count']}</b>\n"
    )
    if summary["per_service"]:
        text += "\n🔝 <b>أعلى إنفاق حسب الخدمة:</b>\n"
        for row in summary["per_service"]:
            desc = row[0] or "خدمة غير محددة"
            total = round(row[1], 4)
            text += f"  • {desc[:30]}: {total}$\n"
    if transactions:
        text += "\n📋 <b>آخر 20 معاملة:</b>\n"
        for t in transactions:
            op = t["operation_type"]
            op_emoji = {"add": "➕", "deduct": "➖", "refund": "↩️"}.get(op, "🔹")
            desc = (t["description"] or "")[:25]
            text += f"{op_emoji} {t['amount']}$ — {desc} — {t['created_at'][:10]}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع لحسابي", callback_data="account:menu")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# =============================================
# تحويل الرصيد
# =============================================

@router.callback_query(F.data == "transfer:start")
async def transfer_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TransferStates.waiting_target)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="account:menu")]
    ])
    await callback.message.edit_text(
        "💰 <b>تحويل رصيد لصديق</b>\n\nأدخل ID المستخدم المراد التحويل إليه:",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(TransferStates.waiting_target)
async def transfer_target(message: Message, state: FSMContext):
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ ID غير صالح.")
        return
    if target_id == message.from_user.id:
        await message.answer("❌ لا يمكنك التحويل لنفسك.")
        return
    target = await db.get_user(target_id)
    if not target:
        await message.answer("❌ المستخدم غير موجود.")
        return
    await state.update_data(target_id=target_id, target_name=target["full_name"])
    await state.set_state(TransferStates.waiting_amount)
    await message.answer(
        f"💰 <b>التحويل إلى:</b> {target['full_name']}\n\nأدخل المبلغ بالدولار:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="account:menu")]
        ]),
    )


@router.message(TransferStates.waiting_amount)
async def transfer_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ مبلغ غير صالح.")
        return
    balance = await db.get_user_balance(message.from_user.id)
    if balance < amount:
        await message.answer(f"❌ رصيدك غير كافٍ. رصيدك: {balance}$")
        return
    data = await state.get_data()
    await state.update_data(amount=amount)
    await state.set_state(TransferStates.confirming)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تأكيد", callback_data="transfer:confirm"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="account:menu"),
        ]
    ])
    await message.answer(
        f"📋 <b>ملخص التحويل:</b>\n\n"
        f"👤 إلى: {data['target_name']}\n"
        f"💰 المبلغ: {amount}$\n\n"
        f"هل تريد التأكيد؟",
        reply_markup=kb,
    )


@router.callback_query(F.data == "transfer:confirm")
async def transfer_confirm(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # ── Rate limit: منع التحويلات المتكررة بسرعة ──
    if not _order_rate_limiter.is_allowed(user_id):
        await callback.answer("⚠️ طلبات كثيرة جداً، انتظر دقيقة ثم حاول.", show_alert=True)
        return

    data = await state.get_data()
    target_id = data.get("target_id")
    amount = data.get("amount")
    if not target_id or not amount:
        await callback.answer("❌ انتهت الجلسة.", show_alert=True)
        await state.clear()
        return

    # ── خصم ذري ──
    deducted = await db.deduct_balance_atomic(user_id, amount, f"تحويل إلى {target_id}")
    if not deducted:
        await callback.message.edit_text("❌ رصيدك غير كافٍ.")
        await state.clear()
        await callback.answer()
        return

    await db.add_balance(target_id, amount, f"تحويل من {user_id}")
    await db.create_transfer(user_id, target_id, amount)
    sender = await db.get_user(user_id)
    new_balance = await db.get_user_balance(user_id)
    logger.info("Transfer | from=%s to=%s amount=%s", user_id, target_id, amount)
    try:
        await bot.send_message(
            target_id,
            f"💰 <b>تم استلام تحويل!</b>\n\n"
            f"المرسل: {sender['full_name']}\n"
            f"المبلغ: {amount}$",
        )
    except Exception:
        pass
    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>تم التحويل بنجاح!</b>\n\n"
        f"💰 المبلغ المحوّل: {amount}$\n"
        f"💳 رصيدك المتبقي: {new_balance}$",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="account:menu")]
        ]),
    )
    await callback.answer()


# =============================================
# رابط الدعوة
# =============================================

@router.callback_query(F.data == "referral:show")
async def referral_show(callback: CallbackQuery):
    user_id = callback.from_user.id
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    bonus = await db.get_setting("referral_bonus", str(REFERRAL_BONUS))
    ref_stats = await db.get_referral_stats(user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")]
    ])
    await callback.message.edit_text(
        f"🎁 <b>رابط دعوتك الخاص:</b>\n\n"
        f"<code>{ref_link}</code>\n\n"
        f"💰 مكافأة لكل دعوة: {bonus}$\n"
        f"👥 عدد الدعوات: {ref_stats['count']}\n"
        f"💵 أرباح الدعوات: {ref_stats['earnings']}$\n\n"
        f"شارك الرابط مع أصدقائك واربح مكافآت!",
        reply_markup=kb,
    )
    await callback.answer()


# =============================================
# طلباتي ومتابعتها
# =============================================

async def _render_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    auto_orders = await db.get_user_orders(user_id, limit=10)
    manual_orders = await db.get_user_manual_orders(user_id, limit=5)
    if not auto_orders and not manual_orders:
        await callback.message.edit_text(
            "📦 <b>لا توجد طلبات حتى الآن.</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")]
            ]),
        )
        return
    text = "📦 <b>طلباتي ومتابعتها</b>\n\n"
    if auto_orders:
        text += "🤖 <b>الطلبات الآلية (SMM):</b>\n"
        for order in auto_orders:
            status_str = STATUS_AR.get(order["status"], f"❓ {order['status']}")
            text += (
                f"#{order['id']} | {order['service_name'][:18]}\n"
                f"   🔢 {order['quantity']} | 💰 {order['price']}$ | {status_str}\n"
            )
    if manual_orders:
        text += "\n🖐 <b>الطلبات اليدوية:</b>\n"
        for order in manual_orders:
            status_str = STATUS_AR.get(order["status"], f"❓ {order['status']}")
            text += f"#{order['id']} | {order['service_name'][:18]} | 💰 {order['price']}$ | {status_str}\n"
            if order["admin_response"]:
                text += f"   ↳ 📝 {order['admin_response']}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 تحديث الحالة", callback_data="orders:refresh")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
    ])
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "orders:list")
async def orders_list(callback: CallbackQuery):
    await _render_orders(callback)
    await callback.answer()


@router.callback_query(F.data == "orders:refresh")
async def orders_refresh(callback: CallbackQuery):
    user_id = callback.from_user.id
    auto_orders = await db.get_user_orders(user_id, limit=10)
    updated_count = 0
    for order in auto_orders:
        if order["status"] in ("pending", "processing") and order["provider_id"] and order["provider_order_id"]:
            provider = await db.get_provider(order["provider_id"])
            if provider:
                result = await check_smm_order_status(dict(provider), order["provider_order_id"])
                if "status" in result:
                    new_status = result["status"].lower()
                    if new_status != order["status"]:
                        await db.update_order_status(order["id"], new_status)
                        updated_count += 1
    await _render_orders(callback)
    await callback.answer(f"✅ تم التحديث. {updated_count} طلب تم تحديثه.", show_alert=True)


# =============================================
# الدعم الفني
# =============================================

@router.callback_query(F.data == "support:menu")
async def support_menu(callback: CallbackQuery):
    support_username = await db.get_setting("support_username", SUPPORT_USERNAME)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 تواصل مباشرة", url=f"https://t.me/{support_username.lstrip('@')}")],
        [InlineKeyboardButton(text="✉️ إرسال رسالة للأدمن", callback_data="support:send")],
        [InlineKeyboardButton(text="💡 اقتراح خدمة", callback_data="support:suggest")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
    ])
    await callback.message.edit_text(
        f"📞 <b>الدعم الفني</b>\n\n"
        f"للتواصل مباشرة: {support_username}\n\n"
        f"أو اختر من الخيارات أدناه:",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data == "support:send")
async def support_send(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SupportStates.waiting_message)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="support:menu")]
    ])
    await callback.message.edit_text(
        "✉️ <b>أرسل رسالتك وسيتم توصيلها للأدمن:</b>",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(SupportStates.waiting_message)
async def support_message_send(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    username_str = f"@{user['username']}" if user and user["username"] else "لا يوجد"
    user_id = message.from_user.id
    await state.clear()
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 رد على المستخدم", callback_data=f"admin:reply_support:{user_id}")]
    ])
    await bot.send_message(
        ADMIN_ID,
        f"📨 <b>رسالة دعم من مستخدم</b>\n\n"
        f"👤 الاسم: {user['full_name'] if user else message.from_user.full_name}\n"
        f"🆔 ID: {user_id}\n"
        f"📱 يوزر: {username_str}\n\n"
        f"💬 الرسالة:\n{message.text}",
        reply_markup=reply_kb,
    )
    await message.answer(
        "✅ تم إرسال رسالتك للأدمن. سنرد عليك في أقرب وقت.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")]
        ]),
    )


@router.callback_query(F.data.startswith("admin:reply_support:"))
async def admin_reply_support_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    user_id = int(callback.data.split(":")[2])
    await state.set_state(AdminReplyStates.reply_support)
    await state.update_data(reply_to_user_id=user_id)
    await callback.message.reply(
        f"✏️ اكتب ردك على المستخدم <code>{user_id}</code>:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:cancel_reply")]
        ]),
    )
    await callback.answer()


@router.message(AdminReplyStates.reply_support)
async def admin_reply_support_send(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    user_id = data.get("reply_to_user_id")
    await state.clear()
    try:
        await bot.send_message(
            user_id,
            f"📩 <b>رد من الأدمن</b>\n\n{message.text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📞 الدعم الفني", callback_data="support:menu")]
            ]),
        )
        await message.answer(f"✅ تم إرسال الرد للمستخدم {user_id} بنجاح.")
    except Exception as e:
        await message.answer(f"❌ فشل إرسال الرد: {e}")


@router.callback_query(F.data == "support:suggest")
async def support_suggest(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SupportStates.waiting_suggestion)
    await callback.message.edit_text(
        "💡 <b>اقتراح خدمة</b>\n\n"
        "أرسل اقتراحك للخدمة التي تريد إضافتها وسنراجعه:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="support:menu")]
        ]),
    )
    await callback.answer()


@router.message(SupportStates.waiting_suggestion)
async def support_suggestion_send(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    username_str = f"@{user['username']}" if user and user["username"] else "لا يوجد"
    user_id = message.from_user.id
    await state.clear()
    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 رد على المقترح", callback_data=f"admin:reply_suggestion:{user_id}")]
    ])
    await bot.send_message(
        ADMIN_ID,
        f"💡 <b>اقتراح خدمة جديد</b>\n\n"
        f"👤 الاسم: {user['full_name'] if user else message.from_user.full_name}\n"
        f"🆔 ID: {user_id}\n"
        f"📱 يوزر: {username_str}\n\n"
        f"📝 الاقتراح:\n{message.text}",
        reply_markup=reply_kb,
    )
    await message.answer(
        "✅ شكراً! تم إرسال اقتراحك للأدمن وسيتم مراجعته.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")]
        ]),
    )


@router.callback_query(F.data.startswith("admin:reply_suggestion:"))
async def admin_reply_suggestion_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    user_id = int(callback.data.split(":")[2])
    await state.set_state(AdminReplyStates.reply_suggestion)
    await state.update_data(reply_to_user_id=user_id)
    await callback.message.reply(
        f"✏️ اكتب ردك على المقترح <code>{user_id}</code>:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:cancel_reply")]
        ]),
    )
    await callback.answer()


@router.message(AdminReplyStates.reply_suggestion)
async def admin_reply_suggestion_send(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    user_id = data.get("reply_to_user_id")
    await state.clear()
    try:
        await bot.send_message(
            user_id,
            f"💡 <b>رد الأدمن على اقتراحك</b>\n\n{message.text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main:menu")]
            ]),
        )
        await message.answer(f"✅ تم إرسال الرد للمستخدم {user_id} بنجاح.")
    except Exception as e:
        await message.answer(f"❌ فشل إرسال الرد: {e}")


@router.callback_query(F.data == "admin:cancel_reply")
async def admin_cancel_reply(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await callback.answer("❌ تم إلغاء الرد.", show_alert=True)


# =============================================
# لوحة الأدمن
# =============================================

def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 الإحصائيات", callback_data="admin:stats"),
            InlineKeyboardButton(text="📢 الإذاعة", callback_data="admin:broadcast"),
        ],
        [
            InlineKeyboardButton(text="🔌 إدارة الموردين", callback_data="admin:providers"),
            InlineKeyboardButton(text="🔄 تحديث الخدمات", callback_data="admin:update_all_services"),
        ],
        [
            InlineKeyboardButton(text="🎮 إدارة الخدمات اليدوية", callback_data="admin:manual_mgmt"),
            InlineKeyboardButton(text="📦 الطلبات اليدوية", callback_data="admin:manual_orders"),
        ],
        [
            InlineKeyboardButton(text="💳 طلبات الشحن", callback_data="admin:payments"),
            InlineKeyboardButton(text="👥 المستخدمون", callback_data="admin:users:0"),
        ],
        [
            InlineKeyboardButton(text="💰 إضافة رصيد", callback_data="admin:add_balance"),
            InlineKeyboardButton(text="➖ خصم رصيد", callback_data="admin:deduct_balance"),
        ],
        [
            InlineKeyboardButton(text="🔐 الاشتراك الإجباري", callback_data="admin:subscription"),
            InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="admin:settings"),
        ],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main:menu")],
    ])


@router.callback_query(F.data == "admin:panel")
async def admin_panel(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ غير مصرح.", show_alert=True)
        return
    await callback.message.edit_text("🛠 <b>لوحة الأدمن</b>", reply_markup=admin_panel_kb())
    await callback.answer()


# --- الإحصائيات ---

@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    stats = await db.get_stats()
    recent = "\n".join([f"• {u['full_name']} ({u['user_id']})" for u in stats["recent_users"]]) or "لا يوجد"
    text = (
        f"📊 <b>إحصائيات البوت</b>\n\n"
        f"👥 المستخدمون: {stats['total_users']}\n"
        f"💰 إجمالي الأرصدة: {stats['total_balance']:.2f}$\n"
        f"📦 الطلبات الآلية: {stats['total_orders']}\n"
        f"🖐 الطلبات اليدوية: {stats['total_manual_orders']}\n"
        f"💳 طلبات الشحن: {stats['total_payments']}\n"
        f"🎁 الإحالات: {stats['total_referrals']}\n"
        f"🔌 الموردون النشطون: {stats['active_providers']}\n"
        f"🗂 الخدمات المخزنة: {stats['total_services']}\n\n"
        f"👤 آخر المستخدمين:\n{recent}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# --- الإذاعة ---

@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.broadcast)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:panel")]
    ])
    await callback.message.edit_text(
        "📢 <b>الإذاعة</b>\nأرسل الرسالة التي تريد بثها لجميع المستخدمين:",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(AdminStates.broadcast)
async def admin_broadcast_send(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    users = await db.get_all_users()
    sent = 0
    failed = 0
    for user in users:
        try:
            await bot.send_message(user["user_id"], f"📢 <b>رسالة من الإدارة:</b>\n\n{message.text}")
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    await message.answer(
        f"✅ <b>تم الإرسال!</b>\n\n✅ تم الإرسال لـ {sent} مستخدم\n❌ فشل الإرسال لـ {failed} مستخدم",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")]
        ]),
    )


# --- إدارة الموردين ---

@router.callback_query(F.data == "admin:providers")
async def admin_providers(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 عرض الموردين", callback_data="admin:providers:list")],
        [InlineKeyboardButton(text="➕ إضافة مورد", callback_data="admin:providers:add")],
        [InlineKeyboardButton(text="✏️ تعديل مورد", callback_data="admin:providers:edit_select")],
        [InlineKeyboardButton(text="🚫 تعطيل / تفعيل مورد", callback_data="admin:providers:toggle_select")],
        [InlineKeyboardButton(text="🧪 اختبار مورد", callback_data="admin:providers:test_select")],
        [InlineKeyboardButton(text="🔄 تحديث خدمات مورد", callback_data="admin:providers:update_select")],
        [InlineKeyboardButton(text="🔄 تحديث خدمات كل الموردين", callback_data="admin:update_all_services")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")],
    ])
    await callback.message.edit_text("🔌 <b>إدارة الموردين</b>", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "admin:providers:list")
async def admin_providers_list(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    providers = await db.get_all_providers()
    if not providers:
        await callback.answer("⚠️ لا يوجد موردون مضافون.", show_alert=True)
        return
    text = "📋 <b>قائمة الموردين:</b>\n\n"
    for p in providers:
        status = "✅ نشط" if p["is_active"] else "❌ معطل"
        ptype = p["provider_type"] if "provider_type" in p.keys() else "smm_v2"
        type_label = "📱 أرقام وهمية (5SIM)" if ptype == "fivesim" else "🔵 رشق (SMM)"
        last_check = p["last_check_status"] if "last_check_status" in p.keys() else ""
        check_line = f"\n   🧪 آخر اختبار: {last_check}" if last_check else ""
        text += (
            f"🔌 <b>{p['name']}</b> (ID: {p['id']})\n"
            f"   النوع: {type_label}\n"
            f"   URL: <code>{p['api_url']}</code>\n"
            f"   الحالة: {status}{check_line}\n\n"
        )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:providers")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "admin:providers:add")
async def admin_providers_add(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.add_provider_name)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:providers")]
    ])
    await callback.message.edit_text("➕ <b>إضافة مورد جديد</b>\nأدخل اسم المورد:", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.add_provider_name)
async def admin_add_provider_name(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(provider_name=message.text.strip())
    await state.set_state(AdminStates.add_provider_type)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 مورد رشق (SMM)", callback_data="addprov:type:smm_v2")],
        [InlineKeyboardButton(text="📱 مورد أرقام وهمية (5SIM)", callback_data="addprov:type:fivesim")],
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:providers")],
    ])
    await message.answer("📋 <b>اختر نوع المورد:</b>", reply_markup=kb)


@router.callback_query(F.data.startswith("addprov:type:"), AdminStates.add_provider_type)
async def admin_add_provider_type(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    ptype = callback.data.split(":")[2]
    await state.update_data(provider_type=ptype)
    await state.set_state(AdminStates.add_provider_url)
    if ptype == "fivesim":
        default_note = "\n💡 الرابط الافتراضي لـ 5SIM: <code>https://5sim.net/v1</code>"
    else:
        default_note = "\n💡 مثال: <code>https://example.com/api/v2</code>"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:providers")]
    ])
    await callback.message.edit_text(f"🌐 أدخل رابط API المورد:{default_note}", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.add_provider_url)
async def admin_add_provider_url(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(provider_url=message.text.strip())
    await state.set_state(AdminStates.add_provider_key)
    data = await state.get_data()
    if data.get("provider_type") == "fivesim":
        note = "\n💡 أدخل مفتاح API الجديد (يبدأ بـ eyJ...)"
    else:
        note = ""
    await message.answer(f"🔑 أدخل مفتاح API المورد:{note}")


@router.message(AdminStates.add_provider_key)
async def admin_add_provider_key(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    await state.clear()
    ptype = data.get("provider_type", "smm_v2")
    provider_id = await db.add_provider(
        data["provider_name"], data["provider_url"],
        message.text.strip(), provider_type=ptype
    )
    type_label = "📱 أرقام وهمية (5SIM)" if ptype == "fivesim" else "🔵 رشق (SMM)"
    await message.answer(
        f"✅ تم إضافة المورد <b>{data['provider_name']}</b>\n"
        f"🔌 النوع: {type_label}\n"
        f"🆔 ID: {provider_id}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧪 اختبار الاتصال", callback_data=f"admin:providers:test:{provider_id}")],
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:providers")],
        ]),
    )


@router.callback_query(F.data == "admin:providers:edit_select")
async def admin_providers_edit_select(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    providers = await db.get_all_providers()
    if not providers:
        await callback.answer("⚠️ لا يوجد موردون.", show_alert=True)
        return
    buttons = [[InlineKeyboardButton(text=f"✏️ {p['name']}", callback_data=f"admin:providers:edit_menu:{p['id']}")] for p in providers]
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:providers")])
    await callback.message.edit_text("✏️ <b>اختر المورد للتعديل أو الحذف:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:providers:edit_menu:"))
async def admin_provider_edit_menu(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    provider_id = int(callback.data.split(":")[3])
    provider = await db.get_provider(provider_id)
    if not provider:
        await callback.answer("❌ المورد غير موجود.", show_alert=True)
        return
    status = "✅ نشط" if provider["is_active"] else "❌ معطل"
    ptype = provider["provider_type"] if "provider_type" in provider.keys() else "smm_v2"
    type_label = "🟡 5SIM API" if ptype == "fivesim" else "🔵 SMM API v2"
    last_check = provider["last_check_status"] if "last_check_status" in provider.keys() else ""
    last_msg = provider["last_check_message"] if "last_check_message" in provider.keys() else ""
    masked_key = mask_api_key(provider["api_key"])
    text = (
        f"🔌 <b>{provider['name']}</b>\n\n"
        f"🔌 النوع: {type_label}\n"
        f"🌐 URL: <code>{provider['api_url']}</code>\n"
        f"🔑 Key: <code>{masked_key}</code>\n"
        f"📊 الحالة: {status}"
    )
    if last_check:
        text += f"\n🧪 آخر اختبار: {last_check}"
    if last_msg:
        text += f"\n📝 {last_msg[:80]}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ تعديل الاسم", callback_data=f"admin:providers:editfield:{provider_id}:name")],
        [InlineKeyboardButton(text="🔌 تعديل النوع", callback_data=f"admin:providers:editfield:{provider_id}:type")],
        [InlineKeyboardButton(text="🌐 تعديل URL", callback_data=f"admin:providers:editfield:{provider_id}:url")],
        [InlineKeyboardButton(text="🔑 تعديل API Key", callback_data=f"admin:providers:editfield:{provider_id}:key")],
        [InlineKeyboardButton(text="🧪 اختبار الاتصال", callback_data=f"admin:providers:test:{provider_id}")],
        [InlineKeyboardButton(text="🚫 تفعيل/تعطيل", callback_data=f"admin:providers:toggle:{provider_id}")],
        [InlineKeyboardButton(text="🗑 حذف المورد", callback_data=f"admin:providers:delete:{provider_id}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:providers:edit_select")],
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:providers:editfield:"))
async def admin_provider_editfield(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split(":")
    provider_id = int(parts[3])
    field = parts[4]
    if field == "type":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔵 مورد رشق (SMM)", callback_data=f"admin:providers:settype:{provider_id}:smm_v2")],
            [InlineKeyboardButton(text="📱 مورد أرقام وهمية (5SIM)", callback_data=f"admin:providers:settype:{provider_id}:fivesim")],
            [InlineKeyboardButton(text="❌ إلغاء", callback_data=f"admin:providers:edit_menu:{provider_id}")],
        ])
        await callback.message.edit_text("🔌 <b>اختر النوع الجديد للمورد:</b>", reply_markup=kb)
        await callback.answer()
        return
    field_labels = {"name": "الاسم", "url": "رابط API", "key": "مفتاح API"}
    await state.set_state(AdminStates.edit_provider_field)
    await state.update_data(edit_provider_id=provider_id, edit_provider_field=field)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data=f"admin:providers:edit_menu:{provider_id}")]
    ])
    await callback.message.edit_text(f"✏️ أدخل القيمة الجديدة لـ <b>{field_labels.get(field, field)}</b>:", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:providers:settype:"))
async def admin_provider_settype(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split(":")
    provider_id = int(parts[3])
    new_type = parts[4]
    await db.update_provider(provider_id, provider_type=new_type)
    type_label = "📱 أرقام وهمية (5SIM)" if new_type == "fivesim" else "🔵 رشق (SMM)"
    await callback.answer(f"✅ تم تغيير النوع إلى {type_label}", show_alert=True)
    # Reload edit menu
    callback.data = f"admin:providers:edit_menu:{provider_id}"
    await admin_provider_edit_menu(callback)


@router.message(AdminStates.edit_provider_field)
async def admin_provider_editfield_input(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    provider_id = data.get("edit_provider_id")
    field = data.get("edit_provider_field")
    await state.clear()
    value = message.text.strip()
    if field == "name":
        await db.update_provider(provider_id, name=value)
    elif field == "url":
        await db.update_provider(provider_id, api_url=value)
    elif field == "key":
        await db.update_provider(provider_id, api_key=value)
    await message.answer(
        f"✅ تم تحديث <b>{field}</b> بنجاح.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data=f"admin:providers:edit_menu:{provider_id}")]
        ]),
    )


@router.callback_query(F.data.startswith("admin:providers:delete:"))
async def admin_provider_delete(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    provider_id = int(callback.data.split(":")[3])
    provider = await db.get_provider(provider_id)
    if not provider:
        await callback.answer("❌ المورد غير موجود.", show_alert=True)
        return
    await db.delete_provider(provider_id)
    await callback.answer(f"✅ تم حذف المورد {provider['name']}.", show_alert=True)
    await admin_providers(callback)


@router.callback_query(F.data == "admin:providers:toggle_select")
async def admin_providers_toggle_select(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    providers = await db.get_all_providers()
    buttons = []
    for p in providers:
        status = "✅" if p["is_active"] else "❌"
        buttons.append([InlineKeyboardButton(
            text=f"{status} {p['name']}",
            callback_data=f"admin:providers:toggle:{p['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:providers")])
    await callback.message.edit_text("🚫 <b>تعطيل / تفعيل مورد</b>:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:providers:toggle:"))
async def admin_providers_toggle(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    provider_id = int(callback.data.split(":")[3])
    await db.toggle_provider(provider_id)
    provider = await db.get_provider(provider_id)
    status = "نشط ✅" if provider["is_active"] else "معطل ❌"
    await callback.answer(f"تم تغيير حالة {provider['name']} إلى {status}", show_alert=True)
    # If coming from edit_menu, go back to edit_menu
    callback.data = f"admin:providers:edit_menu:{provider_id}"
    await admin_provider_edit_menu(callback)


@router.callback_query(F.data == "admin:providers:test_select")
async def admin_providers_test_select(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    providers = await db.get_all_providers()
    buttons = [[InlineKeyboardButton(text=p["name"], callback_data=f"admin:providers:test:{p['id']}")] for p in providers]
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:providers")])
    await callback.message.edit_text("🧪 <b>اختر المورد للاختبار:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:providers:test:"))
async def admin_providers_test(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    provider_id = int(callback.data.split(":")[3])
    provider = await db.get_provider(provider_id)
    if not provider:
        await callback.answer("❌ المورد غير موجود.", show_alert=True)
        return
    await callback.answer("⏳ جاري اختبار الاتصال...")
    ptype = provider["provider_type"] if "provider_type" in provider.keys() else "smm_v2"
    back_cb = f"admin:providers:edit_menu:{provider_id}"
    try:
        if ptype == "fivesim":
            raw_key = provider["api_key"] or ""
            clean_key = raw_key.strip()
            if clean_key.lower().startswith("bearer "):
                clean_key = clean_key[7:].strip()
            base_url = _normalize_fivesim_url(provider["api_url"] or "")
            final_url = base_url + "/user/profile"
            key_exists = bool(clean_key)
            key_preview = (clean_key[:6] + "****" + clean_key[-4:]) if len(clean_key) > 10 else "(فارغ)"

            # طباعة تقرير debug في اللوج بدون كشف المفتاح
            logger.info(
                f"5SIM DEBUG | provider_id={provider_id} provider_name={provider['name']} "
                f"provider_type={ptype} base_url={base_url} final_url={final_url} "
                f"api_key_exists={key_exists} api_key_preview={key_preview} method=GET"
            )

            client = FiveSimClient(api_key=raw_key, base_url=provider["api_url"])
            profile = await client.test_connection()
            http_status = profile.get("_status", 0)
            raw_msg = profile.get("message", "")

            logger.info(
                f"5SIM DEBUG | status={http_status} "
                f"body={str(profile)[:200]}"
            )

            if http_status == 200 and "balance" in profile:
                balance_val = profile.get("balance", 0)
                email = profile.get("email", "—")
                result_text = (
                    f"✅ تم الاتصال بنجاح!\n\n"
                    f"💰 الرصيد: <b>{balance_val}$</b>\n"
                    f"📧 البريد: {email}\n\n"
                    f"🔗 الرابط: <code>{final_url}</code>"
                )
                await db.update_provider(provider_id,
                    last_check_status="✅ ناجح",
                    last_check_message=f"الرصيد: {balance_val}$")
            elif http_status == 401:
                result_text = (
                    "❌ فشل الاتصال — المفتاح غير صحيح (401)\n\n"
                    "السبب الأكثر شيوعاً:\n"
                    "• استخدمت <b>Deprecated API</b> بدل <b>API key for 5SIM protocol</b>\n"
                    "• أو المفتاح منتهي الصلاحية\n\n"
                    "الحل:\n"
                    "1. ادخل 5sim.net → Profile → API &amp; Integrations\n"
                    "2. انسخ <b>API key for 5SIM protocol</b> فقط\n"
                    "3. حدّث المورد بالمفتاح الجديد\n\n"
                    f"🔗 الرابط المستخدم: <code>{final_url}</code>\n"
                    f"🔑 المفتاح (مخفي): <code>{key_preview}</code>"
                )
                await db.update_provider(provider_id,
                    last_check_status="❌ فشل",
                    last_check_message="401 — Deprecated API أو مفتاح خاطئ")
            elif http_status == 403:
                result_text = (
                    "❌ فشل الاتصال (403 Forbidden)\n\n"
                    "احتمال: IP الخاص بـ Replit محظور من 5SIM\n"
                    "أو المفتاح لا يملك الصلاحيات الكافية"
                )
                await db.update_provider(provider_id,
                    last_check_status="❌ فشل",
                    last_check_message="403 — IP محظور أو صلاحيات ناقصة")
            elif raw_msg in ("invalid_url", "connection_error"):
                result_text = (
                    "❌ فشل الاتصال — خطأ في الرابط أو الشبكة\n\n"
                    "تأكد أن API URL هو:\n"
                    "<code>https://5sim.net/v1</code>"
                )
                await db.update_provider(provider_id,
                    last_check_status="❌ فشل",
                    last_check_message="خطأ في الرابط أو الاتصال")
            else:
                result_text = (
                    f"❌ فشل الاتصال بـ 5SIM\n"
                    f"الكود: {http_status}\n"
                    f"السبب: {raw_msg[:150]}\n\n"
                    f"🔗 الرابط: <code>{final_url}</code>"
                )
                await db.update_provider(provider_id,
                    last_check_status="❌ فشل",
                    last_check_message=f"{http_status}: {raw_msg[:80]}")
        else:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    provider["api_url"],
                    data={"key": provider["api_key"], "action": "balance"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    data_resp = await resp.json(content_type=None)
            balance_val = data_resp.get("balance", "غير متوفر")
            currency = data_resp.get("currency", "")
            result_text = f"✅ الاتصال ناجح!\n💰 الرصيد: {balance_val} {currency}"
            await db.update_provider(provider_id,
                last_check_status="✅ ناجح",
                last_check_message=f"الرصيد: {balance_val} {currency}")
        await callback.message.edit_text(
            f"🧪 <b>اختبار المورد: {provider['name']}</b>\n\n{result_text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع للمورد", callback_data=back_cb)],
                [InlineKeyboardButton(text="📋 كل الموردين", callback_data="admin:providers")],
            ]),
        )
    except Exception as e:
        err_msg = str(e)[:200]
        await db.update_provider(provider_id, last_check_status="❌ خطأ", last_check_message=err_msg[:100])
        await callback.message.edit_text(
            f"🧪 <b>اختبار المورد: {provider['name']}</b>\n\n❌ فشل الاتصال!\n📝 {err_msg}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع للمورد", callback_data=back_cb)],
            ]),
        )


@router.callback_query(F.data == "admin:providers:update_select")
async def admin_providers_update_select(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    providers = await db.get_active_providers()
    buttons = [[InlineKeyboardButton(text=p["name"], callback_data=f"admin:providers:update_one:{p['id']}")] for p in providers]
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:providers")])
    await callback.message.edit_text("🔄 <b>اختر المورد لتحديث خدماته:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:providers:update_one:"))
async def admin_update_one_provider(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    provider_id = int(callback.data.split(":")[3])
    provider = await db.get_provider(provider_id)
    await callback.answer("⏳ جاري التحديث...")
    await callback.message.edit_text(f"⏳ جاري جلب خدمات المورد <b>{provider['name']}</b>...")
    await db.clear_services_by_provider(provider_id)
    services = await fetch_services_from_provider(dict(provider))
    if services:
        await db.save_services_cache(services)
    await callback.message.edit_text(
        f"✅ تم تحديث خدمات <b>{provider['name']}</b>\n💾 تم حفظ {len(services)} خدمة.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:providers")]
        ]),
    )


@router.callback_query(F.data == "admin:update_all_services")
async def admin_update_all_services(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.answer("⏳ جاري التحديث...")
    await callback.message.edit_text("⏳ جاري تحديث خدمات جميع الموردين...")
    providers = await db.get_active_providers()
    total = 0
    for provider in providers:
        await db.clear_services_by_provider(provider["id"])
        services = await fetch_services_from_provider(dict(provider))
        if services:
            await db.save_services_cache(services)
            total += len(services)
    await callback.message.edit_text(
        f"✅ تم تحديث خدمات جميع الموردين!\n💾 إجمالي الخدمات المحفوظة: {total}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")]
        ]),
    )


# --- إدارة الخدمات اليدوية ---

@router.callback_query(F.data == "admin:manual_mgmt")
async def admin_manual_mgmt(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 عرض الأقسام", callback_data="admin:manual:cats")],
        [InlineKeyboardButton(text="➕ إضافة قسم", callback_data="admin:manual:add_cat")],
        [InlineKeyboardButton(text="✏️ تعديل قسم", callback_data="admin:manual:edit_cat_select")],
        [InlineKeyboardButton(text="🔄 تفعيل / إخفاء قسم", callback_data="admin:manual:toggle_cat_select")],
        [InlineKeyboardButton(text="🗑️ حذف قسم", callback_data="admin:manual:delete_cat_select")],
        [InlineKeyboardButton(text="📦 إدارة خدمات قسم", callback_data="admin:manual:manage_services_select")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")],
    ])
    await callback.message.edit_text("🎮 <b>إدارة الخدمات اليدوية</b>", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "admin:manual:cats")
async def admin_manual_cats(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    cats = await db.get_manual_categories(active_only=False)
    text = "📋 <b>أقسام الخدمات اليدوية:</b>\n\n"
    for c in cats:
        status = "✅" if c["is_active"] else "❌"
        text += f"{status} {c['name']} (ID: {c['id']})\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual_mgmt")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "admin:manual:add_cat")
async def admin_manual_add_cat(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.add_manual_cat)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:manual_mgmt")]
    ])
    await callback.message.edit_text("➕ أدخل اسم القسم الجديد:", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.add_manual_cat)
async def admin_manual_cat_name(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    cat_id = await db.create_manual_category(message.text.strip())
    await message.answer(
        f"✅ تم إضافة القسم <b>{message.text.strip()}</b> (ID: {cat_id})",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual_mgmt")]
        ]),
    )


@router.callback_query(F.data == "admin:manual:edit_cat_select")
async def admin_manual_edit_cat_select(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    cats = await db.get_manual_categories(active_only=False)
    buttons = [[InlineKeyboardButton(text=c["name"], callback_data=f"admin:manual:edit_cat:{c['id']}")] for c in cats]
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual_mgmt")])
    await callback.message.edit_text("✏️ اختر القسم للتعديل:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:manual:edit_cat:"))
async def admin_manual_edit_cat(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    cat_id = int(callback.data.split(":")[3])
    await state.set_state(AdminStates.edit_manual_cat_name)
    await state.update_data(cat_id=cat_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:manual_mgmt")]
    ])
    await callback.message.edit_text(f"✏️ أدخل الاسم الجديد للقسم (ID: {cat_id}):", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.edit_manual_cat_name)
async def admin_manual_cat_name_update(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    await state.clear()
    await db.update_manual_category(data["cat_id"], message.text.strip())
    await message.answer(
        f"✅ تم تعديل اسم القسم.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual_mgmt")]
        ]),
    )


@router.callback_query(F.data == "admin:manual:toggle_cat_select")
async def admin_manual_toggle_cat_select(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    cats = await db.get_manual_categories(active_only=False)
    buttons = []
    for c in cats:
        status = "✅" if c["is_active"] else "❌"
        buttons.append([InlineKeyboardButton(
            text=f"{status} {c['name']}",
            callback_data=f"admin:manual:toggle_cat:{c['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual_mgmt")])
    await callback.message.edit_text("🔄 <b>تفعيل / إخفاء قسم:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:manual:toggle_cat:"))
async def admin_manual_toggle_cat(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    cat_id = int(callback.data.split(":")[3])
    await db.toggle_manual_category(cat_id)
    await callback.answer("✅ تم تغيير حالة القسم.", show_alert=True)
    await admin_manual_toggle_cat_select(callback)


async def _render_delete_multi(callback: CallbackQuery, selected: list):
    cats = await db.get_manual_categories(active_only=False)
    if not cats:
        await callback.answer("⚠️ لا توجد أقسام.", show_alert=True)
        return
    buttons = []
    for c in cats:
        icon = "✅" if c["id"] in selected else "☐"
        buttons.append([InlineKeyboardButton(
            text=f"{icon} {c['name']}",
            callback_data=f"admin:manual:delmulti:toggle:{c['id']}"
        )])
    all_selected = len(selected) == len(cats)
    buttons.append([
        InlineKeyboardButton(
            text="☑️ تحديد الكل" if not all_selected else "🔲 إلغاء تحديد الكل",
            callback_data="admin:manual:delmulti:all"
        )
    ])
    count = len(selected)
    delete_text = f"🗑️ حذف المحدد ({count})" if count > 0 else "🗑️ حذف المحدد"
    buttons.append([InlineKeyboardButton(text=delete_text, callback_data="admin:manual:delmulti:confirm")])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual_mgmt")])
    try:
        await callback.message.edit_text(
            "🗑️ <b>حذف أقسام</b>\n\nحدّد الأقسام التي تريد حذفها ثم اضغط <b>حذف المحدد</b>:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "admin:manual:delete_cat_select")
async def admin_manual_delete_cat_select(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.delete_cats_multi)
    await state.update_data(selected_ids=[])
    await _render_delete_multi(callback, [])
    await callback.answer()


@router.callback_query(F.data.startswith("admin:manual:delmulti:toggle:"))
async def admin_manual_delmulti_toggle(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    cat_id = int(callback.data.split(":")[4])
    data = await state.get_data()
    selected = data.get("selected_ids", [])
    if cat_id in selected:
        selected.remove(cat_id)
    else:
        selected.append(cat_id)
    await state.update_data(selected_ids=selected)
    await _render_delete_multi(callback, selected)
    await callback.answer()


@router.callback_query(F.data == "admin:manual:delmulti:all")
async def admin_manual_delmulti_all(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    cats = await db.get_manual_categories(active_only=False)
    data = await state.get_data()
    selected = data.get("selected_ids", [])
    all_ids = [c["id"] for c in cats]
    if len(selected) == len(cats):
        selected = []
    else:
        selected = all_ids
    await state.update_data(selected_ids=selected)
    await _render_delete_multi(callback, selected)
    await callback.answer()


@router.callback_query(F.data == "admin:manual:delmulti:confirm")
async def admin_manual_delmulti_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    selected = data.get("selected_ids", [])
    if not selected:
        await callback.answer("⚠️ لم تحدد أي قسم.", show_alert=True)
        return
    cats = await db.get_manual_categories(active_only=False)
    names = [c["name"] for c in cats if c["id"] in selected]
    names_text = "\n".join(f"• {n}" for n in names)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"✅ نعم، احذف ({len(selected)})", callback_data="admin:manual:delmulti:do"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:manual:delete_cat_select"),
        ]
    ])
    await callback.message.edit_text(
        f"⚠️ <b>تأكيد الحذف</b>\n\n"
        f"سيتم حذف الأقسام التالية وجميع خدماتها نهائياً:\n\n{names_text}",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data == "admin:manual:delmulti:do")
async def admin_manual_delmulti_do(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    selected = data.get("selected_ids", [])
    await state.clear()
    for cat_id in selected:
        await db.delete_manual_category(cat_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 عرض الأقسام", callback_data="admin:manual:cats")],
        [InlineKeyboardButton(text="➕ إضافة قسم", callback_data="admin:manual:add_cat")],
        [InlineKeyboardButton(text="✏️ تعديل قسم", callback_data="admin:manual:edit_cat_select")],
        [InlineKeyboardButton(text="🔄 تفعيل / إخفاء قسم", callback_data="admin:manual:toggle_cat_select")],
        [InlineKeyboardButton(text="🗑️ حذف أقسام", callback_data="admin:manual:delete_cat_select")],
        [InlineKeyboardButton(text="📦 إدارة خدمات قسم", callback_data="admin:manual:manage_services_select")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")],
    ])
    await callback.message.edit_text(
        f"✅ تم حذف <b>{len(selected)}</b> قسم بنجاح.\n\n🎮 <b>إدارة الخدمات اليدوية</b>",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data == "admin:manual:manage_services_select")
async def admin_manual_manage_services_select(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    cats = await db.get_manual_categories(active_only=False)
    buttons = [[InlineKeyboardButton(text=c["name"], callback_data=f"admin:manual:services:{c['id']}")] for c in cats]
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual_mgmt")])
    await callback.message.edit_text("📦 اختر القسم لإدارة خدماته:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:manual:services:"))
async def admin_manual_services(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    cat_id = int(callback.data.split(":")[3])
    services = await db.get_manual_services_by_category(cat_id, active_only=False)
    cats = await db.get_manual_categories(active_only=False)
    cat_name = next((c["name"] for c in cats if c["id"] == cat_id), str(cat_id))
    buttons = []
    for svc in services:
        status = "✅" if svc["is_active"] else "❌"
        buttons.append([InlineKeyboardButton(
            text=f"{status} {svc['name']} - {svc['price']}$",
            callback_data=f"admin:manual:svc_detail:{svc['id']}:{cat_id}"
        )])
    buttons.append([InlineKeyboardButton(text="➕ إضافة خدمة", callback_data=f"admin:manual:add_svc:{cat_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual:manage_services_select")])
    await callback.message.edit_text(
        f"📦 <b>خدمات قسم: {cat_name}</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:manual:svc_detail:"))
async def admin_manual_svc_detail(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split(":")
    svc_id = int(parts[3])
    cat_id = int(parts[4])
    svc = await db.get_manual_service(svc_id)
    if not svc:
        await callback.answer("❌ الخدمة غير موجودة.", show_alert=True)
        return
    status = "✅ نشطة" if svc["is_active"] else "❌ مخفية"
    text = (
        f"💎 <b>{svc['name']}</b>\n\n"
        f"💰 السعر: {svc['price']}$\n"
        f"📝 الوصف: {svc['description'] or 'لا يوجد'}\n"
        f"📋 التعليمات: {svc['instructions'] or 'لا يوجد'}\n"
        f"🔠 نوع البيانات: {svc['required_data_type']}\n"
        f"📊 الحالة: {status}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ تعديل", callback_data=f"admin:manual:edit_svc:{svc_id}:{cat_id}")],
        [InlineKeyboardButton(text="🔄 تفعيل / إخفاء", callback_data=f"admin:manual:toggle_svc:{svc_id}:{cat_id}")],
        [InlineKeyboardButton(text="🗑 حذف", callback_data=f"admin:manual:delete_svc:{svc_id}:{cat_id}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data=f"admin:manual:services:{cat_id}")],
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:manual:toggle_svc:"))
async def admin_manual_toggle_svc(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split(":")
    svc_id = int(parts[3])
    cat_id = int(parts[4])
    await db.toggle_manual_service(svc_id)
    await callback.answer("✅ تم تغيير حالة الخدمة.", show_alert=True)
    callback.data = f"admin:manual:svc_detail:{svc_id}:{cat_id}"
    await admin_manual_svc_detail(callback)


@router.callback_query(F.data.startswith("admin:manual:delete_svc:"))
async def admin_manual_delete_svc(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split(":")
    svc_id = int(parts[3])
    cat_id = int(parts[4])
    await db.delete_manual_service(svc_id)
    await callback.answer("✅ تم حذف الخدمة.", show_alert=True)
    callback.data = f"admin:manual:services:{cat_id}"
    await admin_manual_services(callback)


@router.callback_query(F.data.startswith("admin:manual:add_svc:"))
async def admin_manual_add_svc_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    cat_id = int(callback.data.split(":")[3])
    await state.set_state(AdminStates.add_service_name)
    await state.update_data(add_svc_cat_id=cat_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data=f"admin:manual:services:{cat_id}")]
    ])
    await callback.message.edit_text("➕ <b>إضافة خدمة جديدة</b>\nأدخل اسم الخدمة:", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.add_service_name)
async def admin_add_svc_name(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(svc_name=message.text.strip())
    await state.set_state(AdminStates.add_service_desc)
    await message.answer("📝 أدخل وصف الخدمة (أو أرسل - للتخطي):")


@router.message(AdminStates.add_service_desc)
async def admin_add_svc_desc(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    desc = "" if message.text.strip() == "-" else message.text.strip()
    await state.update_data(svc_desc=desc)
    await state.set_state(AdminStates.add_service_instr)
    await message.answer("📋 أدخل تعليمات الخدمة (أو أرسل - للتخطي):")


@router.message(AdminStates.add_service_instr)
async def admin_add_svc_instr(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    instr = "" if message.text.strip() == "-" else message.text.strip()
    await state.update_data(svc_instr=instr)
    await state.set_state(AdminStates.add_service_dtype)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 نص", callback_data="admin:svc_dtype:text"),
            InlineKeyboardButton(text="🆔 ID", callback_data="admin:svc_dtype:id"),
        ],
        [
            InlineKeyboardButton(text="📧 إيميل", callback_data="admin:svc_dtype:email"),
            InlineKeyboardButton(text="📱 هاتف", callback_data="admin:svc_dtype:phone"),
        ],
    ])
    await message.answer("🔠 اختر نوع البيانات المطلوبة من المستخدم:", reply_markup=kb)


@router.callback_query(F.data.startswith("admin:svc_dtype:"), AdminStates.add_service_dtype)
async def admin_add_svc_dtype(callback: CallbackQuery, state: FSMContext):
    dtype = callback.data.split(":")[2]
    await state.update_data(svc_dtype=dtype)
    await state.set_state(AdminStates.add_service_price)
    await callback.message.edit_text("💰 أدخل سعر الخدمة بالدولار:")
    await callback.answer()


@router.message(AdminStates.add_service_price)
async def admin_add_svc_price(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        price = float(message.text.strip())
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ سعر غير صالح.")
        return
    data = await state.get_data()
    await state.clear()
    svc_id = await db.create_manual_service(
        category_id=data["add_svc_cat_id"],
        name=data["svc_name"],
        description=data.get("svc_desc", ""),
        instructions=data.get("svc_instr", ""),
        required_data_type=data.get("svc_dtype", "text"),
        price=price,
    )
    await message.answer(
        f"✅ تم إضافة الخدمة <b>{data['svc_name']}</b> (ID: {svc_id}) بسعر {price}$",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data=f"admin:manual:services:{data['add_svc_cat_id']}")]
        ]),
    )


@router.callback_query(F.data.startswith("admin:manual:edit_svc:"))
async def admin_manual_edit_svc(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split(":")
    svc_id = int(parts[3])
    cat_id = int(parts[4])
    await state.set_state(AdminStates.edit_service_field)
    await state.update_data(edit_svc_id=svc_id, edit_svc_cat_id=cat_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 الاسم", callback_data="admin:edit_svc_field:name")],
        [InlineKeyboardButton(text="💰 السعر", callback_data="admin:edit_svc_field:price")],
        [InlineKeyboardButton(text="📋 الوصف", callback_data="admin:edit_svc_field:description")],
        [InlineKeyboardButton(text="📌 التعليمات", callback_data="admin:edit_svc_field:instructions")],
        [InlineKeyboardButton(text="🔠 نوع البيانات", callback_data="admin:edit_svc_field:required_data_type")],
        [InlineKeyboardButton(text="❌ إلغاء", callback_data=f"admin:manual:svc_detail:{svc_id}:{cat_id}")],
    ])
    await callback.message.edit_text("✏️ <b>اختر الحقل للتعديل:</b>", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:edit_svc_field:"), AdminStates.edit_service_field)
async def admin_edit_svc_field_select(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split(":")[2]
    await state.update_data(edit_field=field)
    await state.set_state(AdminStates.edit_service_value)
    await callback.message.edit_text(f"✏️ أدخل القيمة الجديدة لـ <b>{field}</b>:")
    await callback.answer()


@router.message(AdminStates.edit_service_value)
async def admin_edit_svc_value(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    field = data["edit_field"]
    value = message.text.strip()
    svc_id = data["edit_svc_id"]
    cat_id = data["edit_svc_cat_id"]
    if field == "price":
        try:
            value = float(value)
        except ValueError:
            await message.answer("❌ سعر غير صالح.")
            return
    await db.update_manual_service(svc_id, **{field: value})
    await state.clear()
    await message.answer(
        f"✅ تم تعديل <b>{field}</b>.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data=f"admin:manual:svc_detail:{svc_id}:{cat_id}")]
        ]),
    )


# --- الطلبات اليدوية للأدمن ---

@router.callback_query(F.data == "admin:manual_orders")
async def admin_manual_orders(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    orders = await db.get_manual_orders(status="pending", limit=20)
    if not orders:
        await callback.message.edit_text(
            "📦 <b>لا توجد طلبات يدوية قيد الانتظار.</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")]
            ]),
        )
        await callback.answer()
        return
    buttons = []
    for order in orders:
        buttons.append([InlineKeyboardButton(
            text=f"#{order['id']} | {order['service_name'][:20]} | {order['price']}$",
            callback_data=f"admin:morder:view:{order['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")])
    await callback.message.edit_text(
        f"📦 <b>الطلبات اليدوية قيد الانتظار ({len(orders)}):</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:morder:view:"))
async def admin_morder_view(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    order_id = int(callback.data.split(":")[3])
    order = await db.get_manual_order_by_id(order_id)
    if not order:
        await callback.answer("❌ الطلب غير موجود.", show_alert=True)
        return
    user = await db.get_user(order["user_id"])
    username_str = f"@{user['username']}" if user and user["username"] else "لا يوجد"
    text = (
        f"📦 <b>طلب يدوي #{order_id}</b>\n\n"
        f"👤 المستخدم: {user['full_name'] if user else 'غير معروف'}\n"
        f"🆔 ID: {order['user_id']}\n"
        f"📱 يوزر: {username_str}\n"
        f"💎 الخدمة: {order['service_name']}\n"
        f"📝 البيانات: {order['user_data']}\n"
        f"💰 السعر: {order['price']}$\n"
        f"📊 الحالة: {order['status']}\n"
        f"📅 التاريخ: {order['created_at']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تنفيذ بدون رسالة", callback_data=f"admin:morder:done:{order_id}"),
            InlineKeyboardButton(text="✉️ تنفيذ مع رسالة", callback_data=f"admin:morder:respond:{order_id}"),
        ],
        [InlineKeyboardButton(text="❌ إلغاء وإرجاع الرصيد", callback_data=f"admin:morder:cancel:{order_id}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual_orders")],
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:morder:done:"))
async def admin_morder_done(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    order_id = int(callback.data.split(":")[3])
    order = await db.get_manual_order_by_id(order_id)
    if not order:
        await callback.answer("❌ الطلب غير موجود.", show_alert=True)
        return
    await db.update_manual_order_status(order_id, "completed")
    try:
        await bot.send_message(
            order["user_id"],
            f"✅ <b>تم تنفيذ طلبك!</b>\n\n"
            f"📦 رقم الطلب: #{order_id}\n"
            f"💎 الخدمة: {order['service_name']}\n\n"
            f"شكراً لاستخدامك خدماتنا.",
        )
    except Exception:
        pass
    await callback.answer("✅ تم تنفيذ الطلب.", show_alert=True)
    await admin_manual_orders(callback)


@router.callback_query(F.data.startswith("admin:morder:respond:"))
async def admin_morder_respond_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    order_id = int(callback.data.split(":")[3])
    await state.set_state(AdminStates.manual_order_respond)
    await state.update_data(morder_id=order_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data=f"admin:morder:view:{order_id}")]
    ])
    await callback.message.edit_text(
        f"✉️ <b>إرسال رسالة / كود للمستخدم للطلب #{order_id}:</b>\nأرسل الرسالة أو الكود:",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(AdminStates.manual_order_respond)
async def admin_morder_respond_send(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    order_id = data.get("morder_id")
    await state.clear()
    order = await db.get_manual_order_by_id(order_id)
    if not order:
        await message.answer("❌ الطلب غير موجود.")
        return
    await db.save_manual_order_response(order_id, message.text.strip())
    try:
        await bot.send_message(
            order["user_id"],
            f"✅ <b>تم تنفيذ طلبك!</b>\n\n"
            f"📦 رقم الطلب: #{order_id}\n"
            f"💎 الخدمة: {order['service_name']}\n\n"
            f"📝 <b>رد الأدمن / الكود:</b>\n<code>{message.text.strip()}</code>",
        )
    except Exception:
        pass
    await message.answer(
        f"✅ تم تنفيذ الطلب #{order_id} وإرسال الرسالة للمستخدم.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:manual_orders")]
        ]),
    )


@router.callback_query(F.data.startswith("admin:morder:cancel:"))
async def admin_morder_cancel(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    order_id = int(callback.data.split(":")[3])
    order = await db.get_manual_order_by_id(order_id)
    if not order:
        await callback.answer("❌ الطلب غير موجود.", show_alert=True)
        return
    await db.update_manual_order_status(order_id, "cancelled")
    await db.add_balance(order["user_id"], order["price"], f"إرجاع رصيد طلب يدوي #{order_id}")
    try:
        await bot.send_message(
            order["user_id"],
            f"❌ <b>تم إلغاء طلبك.</b>\n\n"
            f"📦 رقم الطلب: #{order_id}\n"
            f"💎 الخدمة: {order['service_name']}\n"
            f"💰 تم إرجاع {order['price']}$ إلى رصيدك.",
        )
    except Exception:
        pass
    await callback.answer("✅ تم إلغاء الطلب وإرجاع الرصيد.", show_alert=True)
    await admin_manual_orders(callback)


# --- طلبات الشحن اليدوي ---

@router.callback_query(F.data == "admin:payments")
async def admin_payments(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    payments = await db.get_pending_payments()
    if not payments:
        await callback.message.edit_text(
            "💳 <b>لا توجد طلبات شحن قيد الانتظار.</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")]
            ]),
        )
        await callback.answer()
        return
    buttons = []
    for p in payments:
        buttons.append([InlineKeyboardButton(
            text=f"#{p['id']} | {p['amount']}$ | {p['network']}",
            callback_data=f"admin:payment:view:{p['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")])
    await callback.message.edit_text(
        f"💳 <b>طلبات الشحن قيد الانتظار ({len(payments)}):</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:payment:view:"))
async def admin_payment_view(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    payment_id = int(callback.data.split(":")[3])
    payment = await db.get_payment_by_id(payment_id)
    if not payment:
        await callback.answer("❌ الطلب غير موجود.", show_alert=True)
        return
    user = await db.get_user(payment["user_id"])
    username_str = f"@{user['username']}" if user and user["username"] else "لا يوجد"
    text = (
        f"💳 <b>طلب شحن #{payment_id}</b>\n\n"
        f"👤 الاسم: {user['full_name'] if user else 'غير معروف'}\n"
        f"🆔 ID: {payment['user_id']}\n"
        f"📱 يوزر: {username_str}\n"
        f"💰 المبلغ: {payment['amount']}$\n"
        f"🌐 الشبكة: {payment['network']}\n"
        f"📅 التاريخ: {payment['created_at']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ قبول وتحديد المبلغ", callback_data=f"admin:payment:approve_ask:{payment_id}")],
        [InlineKeyboardButton(text="❌ رفض الطلب", callback_data=f"admin:payment:reject:{payment_id}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:payments")],
    ])
    if payment["proof_photo_id"]:
        try:
            await bot.send_photo(callback.from_user.id, photo=payment["proof_photo_id"], caption=text, reply_markup=kb)
            await callback.answer()
            return
        except Exception:
            pass
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:payment:approve_ask:"))
async def admin_payment_approve_ask(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    payment_id = int(callback.data.split(":")[3])
    payment = await db.get_payment_by_id(payment_id)
    if not payment or payment["status"] != "pending":
        await callback.answer("❌ الطلب غير موجود أو تمت معالجته.", show_alert=True)
        return
    await state.set_state(AdminStates.payment_approve_amount)
    await state.update_data(payment_id=payment_id, payment_user_id=payment["user_id"],
                            payment_network=payment["network"])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ استخدام المبلغ الأصلي ({payment['amount']}$)",
                              callback_data=f"admin:payment:use_orig_amount:{payment_id}:{payment['amount']}")],
        [InlineKeyboardButton(text="❌ إلغاء", callback_data=f"admin:payment:view:{payment_id}")],
    ])
    await callback.message.answer(
        f"💰 <b>أدخل المبلغ الذي تريد إضافته للعميل</b>\n"
        f"(المبلغ المطلوب من العميل: <b>{payment['amount']}$</b>)\n\n"
        f"أو اضغط الزر لاستخدام نفس المبلغ:",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:payment:use_orig_amount:"))
async def admin_payment_use_orig_amount(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split(":")
    payment_id = int(parts[3])
    amount = float(parts[4])
    await state.update_data(approve_amount=amount, payment_id=payment_id)
    await state.set_state(AdminStates.payment_approve_note)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ بدون ملاحظة", callback_data=f"admin:payment:no_note:{payment_id}:{amount}")],
    ])
    await callback.message.edit_text("📝 <b>اكتب ملاحظة للعميل</b> (تُرسل مع إشعار الرصيد):", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.payment_approve_amount)
async def admin_payment_approve_amount_input(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        amount = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer("❌ أدخل رقماً صحيحاً مثل: 5 أو 10.5")
        return
    await state.update_data(approve_amount=amount)
    await state.set_state(AdminStates.payment_approve_note)
    data = await state.get_data()
    payment_id = data.get("payment_id")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ بدون ملاحظة", callback_data=f"admin:payment:no_note:{payment_id}:{amount}")],
    ])
    await message.answer(f"✅ المبلغ: <b>{amount}$</b>\n\n📝 <b>اكتب ملاحظة للعميل</b> (تُرسل مع إشعار الرصيد):",
                         reply_markup=kb)


@router.callback_query(F.data.startswith("admin:payment:no_note:"))
async def admin_payment_no_note(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split(":")
    payment_id = int(parts[3])
    amount = float(parts[4])
    await state.clear()
    await _finalize_payment_approval(callback, payment_id, amount, note="")


@router.message(AdminStates.payment_approve_note)
async def admin_payment_approve_note_input(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    payment_id = data.get("payment_id")
    amount = data.get("approve_amount")
    note = message.text.strip()
    await state.clear()
    await _finalize_payment_approval(message, payment_id, amount, note=note)


async def _finalize_payment_approval(event, payment_id: int, amount: float, note: str = ""):
    payment = await db.get_payment_by_id(payment_id)
    if not payment or payment["status"] != "pending":
        return
    await db.update_payment_status(payment_id, "approved", admin_note=note)
    await db.add_balance(payment["user_id"], amount, f"شحن يدوي معتمد #{payment_id}")
    new_balance = await db.get_user_balance(payment["user_id"])
    note_line = f"\n📝 ملاحظة الأدمن: {note}" if note else ""
    try:
        await bot.send_message(
            payment["user_id"],
            f"✅ <b>تم إضافة رصيد إلى حسابك!</b>\n\n"
            f"💰 المبلغ المضاف: <b>{amount}$</b>\n"
            f"🌐 الشبكة: {payment['network']}\n"
            f"💳 رصيدك الحالي: <b>{new_balance}$</b>{note_line}",
        )
    except Exception:
        pass
    confirm_text = f"✅ تم قبول طلب #{payment_id} وإضافة {amount}$ للعميل."
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 طلبات الشحن", callback_data="admin:payments")]
    ])
    if isinstance(event, CallbackQuery):
        await event.answer(confirm_text, show_alert=True)
        try:
            await event.message.edit_text(confirm_text, reply_markup=kb)
        except Exception:
            pass
    else:
        await event.answer(confirm_text, reply_markup=kb)


@router.callback_query(F.data.startswith("admin:payment:approve:"))
async def admin_payment_approve(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    payment_id = int(callback.data.split(":")[3])
    payment = await db.get_payment_by_id(payment_id)
    if not payment or payment["status"] != "pending":
        await callback.answer("❌ الطلب غير موجود أو تمت معالجته.", show_alert=True)
        return
    await db.update_payment_status(payment_id, "approved")
    await db.add_balance(payment["user_id"], payment["amount"], f"شحن يدوي معتمد #{payment_id}")
    new_balance = await db.get_user_balance(payment["user_id"])
    try:
        await bot.send_message(
            payment["user_id"],
            f"✅ <b>تم إضافة رصيد إلى حسابك!</b>\n\n"
            f"💰 المبلغ المضاف: {payment['amount']}$\n"
            f"🌐 الشبكة: {payment['network']}\n"
            f"💳 رصيدك الحالي: {new_balance}$",
        )
    except Exception:
        pass
    await callback.answer("✅ تم قبول الطلب وإضافة الرصيد.", show_alert=True)
    await admin_payments(callback)


@router.callback_query(F.data.startswith("admin:payment:reject:"))
async def admin_payment_reject(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    payment_id = int(callback.data.split(":")[3])
    payment = await db.get_payment_by_id(payment_id)
    if not payment or payment["status"] != "pending":
        await callback.answer("❌ الطلب غير موجود أو تمت معالجته.", show_alert=True)
        return
    await db.update_payment_status(payment_id, "rejected")
    try:
        await bot.send_message(
            payment["user_id"],
            f"❌ <b>تم رفض طلب الشحن.</b>\n\n"
            f"💰 المبلغ: {payment['amount']}$\n"
            f"🌐 الشبكة: {payment['network']}\n\n"
            f"للاستفسار تواصل مع الدعم الفني.",
        )
    except Exception:
        pass
    await callback.answer("✅ تم رفض الطلب.", show_alert=True)
    await admin_payments(callback)


# --- المستخدمون ---

@router.callback_query(F.data.startswith("admin:users:"))
async def admin_users(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    page = int(callback.data.split(":")[2])
    limit = 5
    users, total = await db.get_users_paginated(offset=page * limit, limit=limit)
    if not users:
        await callback.answer("⚠️ لا يوجد مستخدمون.", show_alert=True)
        return
    text = f"👥 <b>المستخدمون</b> (الصفحة {page+1} | إجمالي {total})\n\n"
    for u in users:
        banned_str = "🚫 محظور" if u["is_banned"] else "✅ غير محظور"
        username_str = f"@{u['username']}" if u["username"] else "لا يوجد"
        text += (
            f"👤 <b>{u['full_name']}</b>\n"
            f"🆔 {u['user_id']} | 📱 {username_str}\n"
            f"💰 الرصيد: {u['balance']}$ | 📦 الطلبات: {u['total_orders']}\n"
            f"📊 الحالة: {banned_str}\n\n"
        )
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ السابق", callback_data=f"admin:users:{page-1}"))
    if (page + 1) * limit < total:
        nav.append(InlineKeyboardButton(text="➡️ التالي", callback_data=f"admin:users:{page+1}"))
    buttons = []
    if nav:
        buttons.append(nav)
    buttons.append([
        InlineKeyboardButton(text="🔍 بحث عن مستخدم", callback_data="admin:users:search"),
        InlineKeyboardButton(text="💰 إضافة رصيد", callback_data="admin:add_balance"),
    ])
    buttons.append([
        InlineKeyboardButton(text="➖ خصم رصيد", callback_data="admin:deduct_balance"),
        InlineKeyboardButton(text="🚫 حظر", callback_data="admin:ban_user"),
    ])
    buttons.append([
        InlineKeyboardButton(text="✅ فك الحظر", callback_data="admin:unban_user"),
        InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel"),
    ])
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data == "admin:users:search")
async def admin_users_search_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.search_user)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:users:0")]
    ])
    await callback.message.edit_text("🔍 أدخل ID المستخدم للبحث:", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.search_user)
async def admin_users_search(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(message.text.strip())
    except ValueError:
        await message.answer("❌ ID غير صالح.")
        return
    await state.clear()
    user = await db.search_user_by_id(uid)
    if not user:
        await message.answer(
            "❌ لا يوجد مستخدم بهذا ID.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:users:0")]
            ]),
        )
        return
    orders = await db.get_user_orders_count(uid)
    banned_str = "🚫 محظور" if user["is_banned"] else "✅ غير محظور"
    username_str = f"@{user['username']}" if user["username"] else "لا يوجد"
    text = (
        f"👤 <b>{user['full_name']}</b>\n"
        f"🆔 {user['user_id']}\n"
        f"📱 يوزر: {username_str}\n"
        f"💰 الرصيد: {user['balance']}$\n"
        f"📦 عدد الطلبات: {orders}\n"
        f"🎁 الدعوات: {user['referrals_count']}\n"
        f"📊 الحالة: {banned_str}\n"
        f"📅 تاريخ التسجيل: {user['created_at']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 إضافة رصيد", callback_data=f"admin:add_balance_uid:{uid}"),
            InlineKeyboardButton(text="➖ خصم رصيد", callback_data=f"admin:deduct_balance_uid:{uid}"),
        ],
        [
            InlineKeyboardButton(text="🚫 حظر", callback_data=f"admin:ban_uid:{uid}"),
            InlineKeyboardButton(text="✅ فك الحظر", callback_data=f"admin:unban_uid:{uid}"),
        ],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:users:0")],
    ])
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("admin:ban_uid:"))
async def admin_ban_uid(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    uid = int(callback.data.split(":")[2])
    await db.ban_user(uid)
    invalidate_ban_cache(uid)
    try:
        await bot.send_message(uid, "🚫 <b>تم حظرك من استخدام البوت.</b>\nللتواصل مع الإدارة يرجى التواصل عبر القنوات الرسمية.")
    except Exception:
        pass
    await callback.answer(f"✅ تم حظر المستخدم {uid}.", show_alert=True)


@router.callback_query(F.data.startswith("admin:unban_uid:"))
async def admin_unban_uid(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    uid = int(callback.data.split(":")[2])
    await db.unban_user(uid)
    invalidate_ban_cache(uid)
    try:
        await bot.send_message(uid, "✅ <b>تم رفع الحظر عنك.</b>\nيمكنك الآن استخدام البوت بشكل طبيعي.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 ابدأ الآن", callback_data="main:menu")]
            ]))
    except Exception:
        pass
    await callback.answer(f"✅ تم فك حظر المستخدم {uid}.", show_alert=True)


@router.callback_query(F.data == "admin:ban_user")
async def admin_ban_user_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.search_user)
    await state.update_data(ban_action="ban")
    await callback.message.edit_text("🚫 أدخل ID المستخدم للحظر:")
    await callback.answer()


@router.callback_query(F.data == "admin:unban_user")
async def admin_unban_user_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.search_user)
    await state.update_data(ban_action="unban")
    await callback.message.edit_text("✅ أدخل ID المستخدم لفك الحظر:")
    await callback.answer()


# --- إضافة وخصم الرصيد ---

@router.callback_query(F.data == "admin:add_balance")
async def admin_add_balance_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.add_balance_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:panel")]
    ])
    await callback.message.edit_text("💰 <b>إضافة رصيد لمستخدم</b>\nأدخل ID المستخدم:", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.add_balance_id)
async def admin_add_balance_id(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(message.text.strip())
    except ValueError:
        await message.answer("❌ ID غير صالح.")
        return
    user = await db.get_user(uid)
    if not user:
        await message.answer("❌ المستخدم غير موجود.")
        return
    await state.update_data(target_uid=uid, target_name=user["full_name"])
    await state.set_state(AdminStates.add_balance_amount)
    await message.answer(f"💰 أدخل المبلغ لإضافته لـ <b>{user['full_name']}</b>:")


@router.message(AdminStates.add_balance_amount)
async def admin_add_balance_amount(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ مبلغ غير صالح.")
        return
    data = await state.get_data()
    await state.update_data(add_amount=amount)
    await state.set_state(AdminStates.add_balance_confirm)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تأكيد", callback_data="admin:add_balance_exec"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:panel"),
        ]
    ])
    await message.answer(
        f"📋 <b>ملخص:</b>\n\n"
        f"👤 المستخدم: {data['target_name']}\n"
        f"🆔 ID: {data['target_uid']}\n"
        f"💰 المبلغ: {amount}$\n\n"
        f"هل تريد التأكيد؟",
        reply_markup=kb,
    )


@router.callback_query(F.data == "admin:add_balance_exec", AdminStates.add_balance_confirm)
async def admin_add_balance_exec(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    uid = data["target_uid"]
    amount = data["add_amount"]
    await state.clear()
    await db.add_balance(uid, amount, "إضافة رصيد من الأدمن")
    await db.add_admin_balance_operation(uid, amount, "admin_add", "إضافة من الأدمن")
    new_balance = await db.get_user_balance(uid)
    try:
        await bot.send_message(
            uid,
            f"✅ <b>تم إضافة رصيد إلى حسابك من الإدارة</b>\n\n"
            f"💰 المبلغ المضاف: {amount}$\n"
            f"💳 رصيدك الحالي: {new_balance}$",
        )
    except Exception:
        pass
    await callback.message.edit_text(
        f"✅ تم إضافة <b>{amount}$</b> لـ <b>{data['target_name']}</b>\nرصيده الحالي: {new_balance}$",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")]
        ]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:add_balance_uid:"))
async def admin_add_balance_uid_quick(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    uid = int(callback.data.split(":")[2])
    user = await db.get_user(uid)
    await state.update_data(target_uid=uid, target_name=user["full_name"])
    await state.set_state(AdminStates.add_balance_amount)
    await callback.message.edit_text(f"💰 أدخل المبلغ لإضافته لـ <b>{user['full_name']}</b>:")
    await callback.answer()


@router.callback_query(F.data == "admin:deduct_balance")
async def admin_deduct_balance_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.deduct_balance_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:panel")]
    ])
    await callback.message.edit_text("➖ <b>خصم رصيد من مستخدم</b>\nأدخل ID المستخدم:", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.deduct_balance_id)
async def admin_deduct_balance_id(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(message.text.strip())
    except ValueError:
        await message.answer("❌ ID غير صالح.")
        return
    user = await db.get_user(uid)
    if not user:
        await message.answer("❌ المستخدم غير موجود.")
        return
    await state.update_data(target_uid=uid, target_name=user["full_name"], target_balance=user["balance"])
    await state.set_state(AdminStates.deduct_balance_amount)
    await message.answer(f"➖ أدخل المبلغ للخصم من <b>{user['full_name']}</b> (رصيده: {user['balance']}$):")


@router.message(AdminStates.deduct_balance_amount)
async def admin_deduct_balance_amount(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ مبلغ غير صالح.")
        return
    data = await state.get_data()
    if amount > data["target_balance"]:
        await message.answer(f"❌ المبلغ أكبر من رصيد المستخدم ({data['target_balance']}$).")
        return
    await state.update_data(deduct_amount=amount)
    await state.set_state(AdminStates.deduct_balance_confirm)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تأكيد", callback_data="admin:deduct_balance_exec"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:panel"),
        ]
    ])
    await message.answer(
        f"📋 <b>ملخص:</b>\n\n"
        f"👤 المستخدم: {data['target_name']}\n"
        f"🆔 ID: {data['target_uid']}\n"
        f"💰 المبلغ المخصوم: {amount}$\n\n"
        f"هل تريد التأكيد؟",
        reply_markup=kb,
    )


@router.callback_query(F.data == "admin:deduct_balance_exec", AdminStates.deduct_balance_confirm)
async def admin_deduct_balance_exec(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    uid = data["target_uid"]
    amount = data["deduct_amount"]
    await state.clear()
    deducted = await db.deduct_balance(uid, amount, "خصم رصيد من الأدمن")
    if not deducted:
        await callback.message.edit_text("❌ رصيد المستخدم غير كافٍ.")
        return
    await db.add_admin_balance_operation(uid, amount, "admin_deduct", "خصم من الأدمن")
    new_balance = await db.get_user_balance(uid)
    try:
        await bot.send_message(
            uid,
            f"⚠️ <b>تم خصم رصيد من حسابك بواسطة الإدارة</b>\n\n"
            f"💰 المبلغ المخصوم: {amount}$\n"
            f"💳 رصيدك الحالي: {new_balance}$",
        )
    except Exception:
        pass
    await callback.message.edit_text(
        f"✅ تم خصم <b>{amount}$</b> من <b>{data['target_name']}</b>\nرصيده الحالي: {new_balance}$",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")]
        ]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:deduct_balance_uid:"))
async def admin_deduct_balance_uid_quick(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    uid = int(callback.data.split(":")[2])
    user = await db.get_user(uid)
    await state.update_data(target_uid=uid, target_name=user["full_name"], target_balance=user["balance"])
    await state.set_state(AdminStates.deduct_balance_amount)
    await callback.message.edit_text(f"➖ أدخل المبلغ للخصم من <b>{user['full_name']}</b> (رصيده: {user['balance']}$):")
    await callback.answer()


# --- الاشتراك الإجباري ---

@router.callback_query(F.data == "admin:subscription")
async def admin_subscription(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    force = await db.get_setting("force_subscription_enabled", "1")
    channel = await db.get_setting("channel_username", CHANNEL_USERNAME)
    link = await db.get_setting("channel_link", CHANNEL_LINK)
    status = "✅ مفعّل" if force == "1" else "❌ متوقف"
    text = (
        f"🔐 <b>الاشتراك الإجباري</b>\n\n"
        f"الحالة: {status}\n"
        f"القناة: {channel}\n"
        f"الرابط: {link}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تفعيل الاشتراك", callback_data="admin:sub:enable"),
            InlineKeyboardButton(text="❌ إيقاف الاشتراك", callback_data="admin:sub:disable"),
        ],
        [
            InlineKeyboardButton(text="✏️ تعديل القناة", callback_data="admin:sub:edit_channel"),
            InlineKeyboardButton(text="🔗 تعديل الرابط", callback_data="admin:sub:edit_link"),
        ],
        [InlineKeyboardButton(text="🧪 اختبار الاشتراك", callback_data="admin:sub:test")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")],
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "admin:sub:enable")
async def admin_sub_enable(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await db.set_setting("force_subscription_enabled", "1")
    await callback.answer("✅ تم تفعيل الاشتراك الإجباري.", show_alert=True)
    await admin_subscription(callback)


@router.callback_query(F.data == "admin:sub:disable")
async def admin_sub_disable(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await db.set_setting("force_subscription_enabled", "0")
    await callback.answer("✅ تم إيقاف الاشتراك الإجباري.", show_alert=True)
    await admin_subscription(callback)


@router.callback_query(F.data == "admin:sub:edit_channel")
async def admin_sub_edit_channel(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.edit_sub_channel)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:subscription")]
    ])
    await callback.message.edit_text(
        "✏️ أدخل username القناة (مثال: @MyChannel) أو chat_id للقنوات الخاصة:",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(AdminStates.edit_sub_channel)
async def admin_sub_edit_channel_input(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await db.set_setting("channel_username", message.text.strip())
    await message.answer(
        f"✅ تم تحديث القناة إلى: {message.text.strip()}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:subscription")]
        ]),
    )


@router.callback_query(F.data == "admin:sub:edit_link")
async def admin_sub_edit_link(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.edit_sub_link)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:subscription")]
    ])
    await callback.message.edit_text("🔗 أدخل الرابط الجديد للقناة:", reply_markup=kb)
    await callback.answer()


@router.message(AdminStates.edit_sub_link)
async def admin_sub_edit_link_input(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await db.set_setting("channel_link", message.text.strip())
    await message.answer(
        f"✅ تم تحديث رابط القناة.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:subscription")]
        ]),
    )


@router.callback_query(F.data == "admin:sub:test")
async def admin_sub_test(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    channel = await db.get_setting("channel_username", CHANNEL_USERNAME)
    link = await db.get_setting("channel_link", CHANNEL_LINK)
    force = await db.get_setting("force_subscription_enabled", "1")
    test_text = (
        f"🧪 <b>اختبار الاشتراك الإجباري</b>\n\n"
        f"🔐 الفحص: {'مفعّل ✅' if force == '1' else 'متوقف ❌'}\n"
        f"📢 القناة: {channel}\n"
        f"🔗 الرابط: {link}\n"
    )
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id=channel, user_id=ADMIN_ID)
        test_text += f"✅ get_chat_member يعمل بنجاح!\n"
        test_text += f"📊 حالة الأدمن في القناة: {member.status}"
    except Exception as e:
        test_text += f"❌ فشل get_chat_member!\n🔴 السبب: {str(e)}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:subscription")]
    ])
    await callback.message.edit_text(test_text, reply_markup=kb)
    await callback.answer()


# --- الإعدادات ---

@router.callback_query(F.data == "admin:settings")
async def admin_settings(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    profit = await db.get_setting("profit_percent", str(PROFIT_PERCENT))
    ref_bonus = await db.get_setting("referral_bonus", str(REFERRAL_BONUS))
    stars_rate_val = await db.get_setting("stars_rate", str(STARS_RATE))
    support = await db.get_setting("support_username", SUPPORT_USERNAME)
    wallets = {}
    for k in ["wallet_btc", "wallet_usdt_bep20", "wallet_ton_gram", "wallet_ltc", "wallet_sol"]:
        wallets[k] = await db.get_setting(k)
    text = (
        f"⚙️ <b>إعدادات البوت</b>\n\n"
        f"💹 نسبة الربح: {profit}%\n"
        f"🎁 مكافأة الإحالة: {ref_bonus}$\n"
        f"⭐ معدل النجوم: {stars_rate_val} نجمة = 1$\n"
        f"📞 يوزر الدعم: {support}\n\n"
        f"<b>المحافظ:</b>\n"
        f"BTC: <code>{wallets['wallet_btc']}</code>\n"
        f"USDT BEP20: <code>{wallets['wallet_usdt_bep20']}</code>\n"
        f"TON: <code>{wallets['wallet_ton_gram']}</code>\n"
        f"LTC: <code>{wallets['wallet_ltc']}</code>\n"
        f"SOL: <code>{wallets['wallet_sol']}</code>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💹 تعديل نسبة الربح", callback_data="admin:set:profit_percent")],
        [InlineKeyboardButton(text="🎁 تعديل مكافأة الإحالة", callback_data="admin:set:referral_bonus")],
        [InlineKeyboardButton(text="⭐ تعديل معدل النجوم", callback_data="admin:set:stars_rate")],
        [InlineKeyboardButton(text="📞 تعديل يوزر الدعم", callback_data="admin:set:support_username")],
        [InlineKeyboardButton(text="💰 تعديل محفظة BTC", callback_data="admin:set:wallet_btc")],
        [InlineKeyboardButton(text="💰 تعديل محفظة USDT BEP20", callback_data="admin:set:wallet_usdt_bep20")],
        [InlineKeyboardButton(text="💰 تعديل محفظة TON/GRAM", callback_data="admin:set:wallet_ton_gram")],
        [InlineKeyboardButton(text="💰 تعديل محفظة LTC", callback_data="admin:set:wallet_ltc")],
        [InlineKeyboardButton(text="💰 تعديل محفظة SOL", callback_data="admin:set:wallet_sol")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:panel")],
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:set:"))
async def admin_settings_edit(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    key = callback.data.split("admin:set:")[1]
    await state.set_state(AdminStates.edit_provider_value)
    await state.update_data(settings_key=key)
    labels = {
        "profit_percent": "نسبة الربح (مثال: 10)",
        "referral_bonus": "مكافأة الإحالة (مثال: 0.01)",
        "stars_rate": "معدل النجوم (مثال: 77)",
        "support_username": "يوزر الدعم (مثال: @Support)",
        "wallet_btc": "عنوان محفظة BTC",
        "wallet_usdt_bep20": "عنوان محفظة USDT BEP20",
        "wallet_ton_gram": "عنوان محفظة TON/GRAM",
        "wallet_ltc": "عنوان محفظة LTC",
        "wallet_sol": "عنوان محفظة SOL",
    }
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:settings")]
    ])
    await callback.message.edit_text(
        f"✏️ أدخل القيمة الجديدة لـ <b>{labels.get(key, key)}</b>:",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(AdminStates.edit_provider_value)
async def admin_settings_value_input(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    key = data.get("settings_key")
    await state.clear()
    if key:
        await db.set_setting(key, message.text.strip())
        await message.answer(
            f"✅ تم تحديث الإعداد <b>{key}</b>.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع للإعدادات", callback_data="admin:settings")]
            ]),
        )
    else:
        await message.answer("❌ خطأ في حفظ الإعداد.")


# =============================================
# معالج الأخطاء العام
# =============================================

@router.errors()
async def error_handler(event):
    try:
        tb = traceback.format_exc()
        await send_admin_error(f"⚠️ خطأ غير متوقع:\n{tb[:3000]}")
    except Exception:
        pass
    return True


# =============================================
# تشغيل البوت
# =============================================

async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await db.init_db()
    providers_in_db = await db.get_all_providers()
    if not providers_in_db:
        for p in SMM_PROVIDERS:
            if p.get("enabled", True):
                await db.add_provider(p["name"], p["api_url"], p["api_key"])
    await bot.set_my_commands([
        BotCommand(command="start", description="🏠 بدء البوت والقائمة الرئيسية"),
        BotCommand(command="help", description="📖 المساعدة وكيفية استخدام البوت"),
    ])
    try:
        await bot.send_message(ADMIN_ID, "✅ <b>البوت تم تشغيله بنجاح!</b>")
    except Exception:
        pass
    logger.info("Bot started successfully.")


async def main():
    await on_startup()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
