from __future__ import annotations

import asyncio
import html
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
from typing import Any

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from app.bot.formatting import user_status_text
from app.bot.keyboards import (
    demo_account_bet_menu,
    demo_lever_menu,
    demo_real_gate_keyboard,
    get_tokens_screen_keyboard,
    main_menu,
    my_account_menu,
    real_account_deposit_keyboard,
    autotrade_strategy_menu,
    manual_settings_compact_menu,
    max_steps_quick_pick_menu,
    max_cycles_quick_pick_menu,
    EXPIRY_QUICK_PICK_SECONDS,
    expiration_time_pick_menu,
    language_pick_menu,
    settings_hub_menu,
    settings_menu,
    start_menu,
    start_reply_menu,
    status_screen_keyboard,
    support_open_chat_keyboard,
    support_screen_keyboard,
    faq_screen_keyboard,
    logout_confirm_keyboard,
    trade_account_choice_menu,
)
from app.bot.state import AdminMediaFlow, BroadcastFlow, ConnectFlow, SettingsFlow
from app.config import get_settings
from app.db.mongo import mongo
from app.domain.execution import Trade, WebhookSignalIn
from app.domain.types import User
from app.i18n import tr
from app.observability.log import log_exception
from app.repo.affiliate import affiliate_repo
from app.repo.tokens import tokens_repo
from app.repo.trades import trades_repo
from app.repo.credentials import credentials_repo
from app.repo.system import system_repo
from app.repo.users import users_repo
from app.repo.media import media_repo
from app.repo.signals import signals_repo
from app.services.assets import assets
from app.services.market_data import market_data
from app.services.po_balance_cache import (
    refresh_balances_from_cabinet,
    refresh_po_balance_cache_for_telegram,
)
from app.services.pocketoption_auth import pocketoption_auth
from app.services.po_balance_parse import extract_real_demo_usd
from app.services.trade_engine import trade_engine

router = Router()

_demo_sessions: dict[int, dict[str, Any]] = {}

_DEMO_FRAMES_RAW: list[list[tuple[str, str, float, bool]]] = [
    [("win", "GBP/JPY OTC", 4.6, False)],
    [
        ("win", "GBP/JPY OTC", 4.6, False),
        ("win", "USD/CNH OTC", 4.6, False),
    ],
    [
        ("win", "GBP/JPY OTC", 4.6, False),
        ("win", "USD/CNH OTC", 4.6, False),
        ("win", "Microsoft OTC", 4.6, False),
    ],
    [
        ("win", "GBP/JPY OTC", 4.6, False),
        ("win", "USD/CNH OTC", 4.6, False),
        ("win", "Microsoft OTC", 4.6, False),
        ("loss", "TRON OTC", 5.0, False),
    ],
    [
        ("win", "GBP/JPY OTC", 4.6, False),
        ("win", "USD/CNH OTC", 4.6, False),
        ("win", "Microsoft OTC", 4.6, False),
        ("loss", "TRON OTC", 5.0, False),
        ("pending", "BHD/CNY OTC", 10.9, False),
    ],
    [
        ("win", "GBP/JPY OTC", 4.6, False),
        ("win", "USD/CNH OTC", 4.6, False),
        ("win", "Microsoft OTC", 4.6, False),
        ("loss", "TRON OTC", 5.0, False),
        ("pending", "BHD/CNY OTC", 10.9, False),
        ("pending", "BHD/CNY OTC", 10.9, True),
    ],
    [
        ("win", "GBP/JPY OTC", 4.6, False),
        ("win", "USD/CNH OTC", 4.6, False),
        ("win", "Microsoft OTC", 4.6, False),
        ("loss", "TRON OTC", 5.0, False),
        ("win", "BHD/CNY OTC", 10.9, False),
        ("pending", "BHD/CNY OTC", 10.9, True),
    ],
    [
        ("win", "GBP/JPY OTC", 4.6, False),
        ("win", "USD/CNH OTC", 4.6, False),
        ("win", "Microsoft OTC", 4.6, False),
        ("loss", "TRON OTC", 5.0, False),
        ("win", "BHD/CNY OTC", 10.9, False),
        ("loss", "BHD/CNY OTC", 10.9, False),
    ],
    [
        ("win", "GBP/JPY OTC", 4.6, False),
        ("win", "USD/CNH OTC", 4.6, False),
        ("win", "Microsoft OTC", 4.6, False),
        ("loss", "TRON OTC", 5.0, False),
        ("win", "BHD/CNY OTC", 10.9, False),
        ("loss", "BHD/CNY OTC", 10.9, False),
        ("pending", "LBP/USD OTC", 22.7, False),
    ],
    [
        ("win", "GBP/JPY OTC", 4.6, False),
        ("win", "USD/CNH OTC", 4.6, False),
        ("win", "Microsoft OTC", 4.6, False),
        ("loss", "TRON OTC", 5.0, False),
        ("win", "BHD/CNY OTC", 10.9, False),
        ("loss", "BHD/CNY OTC", 10.9, False),
        ("win", "LBP/USD OTC", 22.7, False),
    ],
]

_EXTRA_DEMO_ASSETS: tuple[str, ...] = (
    "Gold OTC",
    "EUR/USD OTC",
    "AUD/CAD OTC",
    "CHF/JPY OTC",
    "NZD/USD OTC",
    "BTC OTC",
    "ETH OTC",
    "Apple OTC",
    "Tesla OTC",
)


@dataclass(frozen=True)
class _DemoProgressLine:
    status: str
    asset: str
    amount: float
    arrow: bool = False


def _materialize_demo_frame(raw: list[tuple[str, str, float, bool]]) -> list[_DemoProgressLine]:
    return [_DemoProgressLine(st, asset, amt, arr) for st, asset, amt, arr in raw]


def _format_demo_line(ln: _DemoProgressLine) -> str:
    if ln.status == "win":
        return f"✅ {ln.asset}  +${ln.amount:.2f}"
    if ln.status == "loss":
        return f"❌ {ln.asset}  -${ln.amount:.2f}"
    if ln.arrow:
        return f"🔄 {ln.asset}  -${ln.amount:.2f} ↗️"
    return f"🔄 {ln.asset}  ${ln.amount:.2f}"


def _resolved_pnl_running_total(lines: list[_DemoProgressLine]) -> float:
    t = 0.0
    for ln in lines:
        if ln.status == "win":
            t += ln.amount
        elif ln.status == "loss":
            t -= ln.amount
    return t


def _pending_resolved_pnl(ln: _DemoProgressLine, telegram_id: int, idx: int) -> float:
    raw = f"{telegram_id}:demo:pend:{idx}:{ln.asset}:{ln.amount}".encode("utf-8")
    h = hashlib.sha256(raw).digest()
    if (h[0] % 2) == 0:
        return ln.amount
    return -ln.amount


def _session_total_pnl(lines: list[_DemoProgressLine], telegram_id: int) -> float:
    total = 0.0
    for i, ln in enumerate(lines):
        if ln.status == "win":
            total += ln.amount
        elif ln.status == "loss":
            total -= ln.amount
        else:
            total += _pending_resolved_pnl(ln, telegram_id, i)
    return total


def _render_demo_progress_caption(lang: str, lines: list[_DemoProgressLine], balance: float, tokens: int) -> str:
    title = tr(lang, "caption.demo_session_progress_title")
    trade_block = "\n".join(_format_demo_line(ln) for ln in lines) if lines else "…"
    bal_s = f"{balance:,.2f}"
    return f"{title}\n\n{trade_block}\n\n💰 Balance: ${bal_s} ⚪ Tokens: {tokens}"


async def _demo_starting_balance_usd(telegram_id: int) -> float:
    _, _, demo_s = await _live_or_cached_balance_strings(telegram_id)
    v = _extract_number(str(demo_s).replace("USD", "").strip())
    if v is not None:
        return float(v)
    u = await users_repo.get_user(telegram_id)
    if u is not None and u.po_demo_balance_usd is not None:
        return float(u.po_demo_balance_usd)
    return 50200.0


def _demo_session_stop_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=tr(lang, "kb.demo_stop_results"),
                    callback_data="demo:session:stop",
                )
            ],
        ]
    )


def _demo_session_results_keyboard(lang: str) -> InlineKeyboardMarkup:
    u = (get_settings().support_telegram_username or "").strip().lstrip("@")
    if u:
        support_btn = InlineKeyboardButton(
            text=tr(lang, "kb.demo_support_external"),
            url=f"https://t.me/{u}",
        )
    else:
        support_btn = InlineKeyboardButton(
            text=tr(lang, "kb.demo_support_external"),
            callback_data="start:support",
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(lang, "kb.demo_start_again"), callback_data="demo:session:again")],
            [InlineKeyboardButton(text=tr(lang, "kb.main_menu"), callback_data="demo:main_menu")],
            [support_btn],
        ]
    )


async def _safe_edit_demo_caption(
    bot: Any,
    chat_id: int,
    message_id: int,
    caption: str,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    try:
        await bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=caption[:1020],
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
    except TelegramBadRequest as e:
        msg = (getattr(e, "message", None) or str(e) or "").lower()
        if "message is not modified" in msg or "not modified" in msg:
            return
        raise


async def _cancel_prior_demo_session(telegram_id: int) -> None:
    prev = _demo_sessions.pop(telegram_id, None)
    if not prev:
        return
    ev: asyncio.Event = prev["stop"]
    ev.set()
    task: asyncio.Task[None] = prev["task"]
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    except Exception:
        pass


_UI_LANGS: tuple[str, ...] = ("ar", "de", "en", "es", "fr", "id", "it", "fil", "pt", "ru", "hi")


def _reply_text_variants(key: str) -> frozenset[str]:
    """All localized labels for a reply-keyboard string (so handlers match any UI language)."""
    return frozenset(tr(l, key) for l in _UI_LANGS)


ADMIN_HELP_TEXT = (
    "🛠 Admin commands\n\n"
    "👥 Users\n"
    "- /admin_users — list latest 50 users\n"
    "- /admin_block telegram_id — block a user\n"
    "- /admin_unblock telegram_id — unblock a user\n\n"
    "🖼️ Media (file_id)\n"
    "- /admin_media — list available media keys\n"
    "- /admin_media_set key — set key (then send photo/video)\n"
    "- /admin_media_clear key — clear key\n\n"
    "📣 Broadcast\n"
    "- /broadcast attribute — start broadcast wizard\n"
    "  attributes:\n"
    "  - global\n"
    "  - signed_in\n"
    "  - not_signed_in\n"
    "  - signed_in_low_balance_20\n\n"
    "⚙️ Global trading\n"
    "- /global_on — enable global trading\n"
    "- /global_off — disable global trading\n\n"
    "📡 Signal ingest\n"
    "- /signal_mode — show mode (all | admin_only | webhook_only | strategy_only)\n"
    "- /signal_mode <mode> — set who may emit live signals\n"
    "- /admin_signal <symbol> <UP|DOWN> — inject admin signal (always allowed)\n\n"
    "⏱ Trade expiry (global)\n"
    "- /admin_expiry — show current seconds\n"
    "- /admin_expiry 5|10|15|30 — set for all non-webhook-overridden trades\n\n"
    "🆔 UID & balances\n"
    "- /sync_uid — try to re-fetch PO UID via API (needs working PO_*)\n"
    "- /sync_balance — try to refresh balances via API\n"
    "- /set_uid <digits> — save PO UID manually\n"
    "- /set_balances <real_usd> <demo_usd> — set cached balances (use - to skip one side)\n\n"
    "💎 Tokens\n"
    "- /admin_tokens telegram_id delta — adjust tokens balance"
)


MEDIA_KEYS: dict[str, str] = {
    "start_banner": "photo",
    "register_banner": "photo",
    "register_video": "video",
    "start_trading_video": "video",
    "demo_settings_video": "video",
    "demo_loss_banner": "photo",
    "demo_profit_banner": "photo",
    "start_trading_tutorial": "photo",
    "get_tokens_banner": "photo",
    "my_account_banner": "photo",
    "settings_banner": "photo",
    "autotrade_settings_banner": "photo",
    "language_banner": "photo",
    "status_banner": "photo",
    "support_banner": "photo",
    "faq_banner": "photo",
}


def _is_admin(user_id: int) -> bool:
    return user_id in get_settings().admin_ids()


async def _ensure_user_from_message(message: Message):
    u = message.from_user
    if u is None:
        return None
    return await users_repo.ensure_user(u.id, u.username, u.first_name)


async def _ensure_user_from_callback(cb: CallbackQuery):
    u = cb.from_user
    return await users_repo.ensure_user(u.id, u.username, u.first_name)


def _registration_keyboard(lang: str) -> InlineKeyboardMarkup:
    s = get_settings()
    sup = (s.support_telegram_username or "").strip().lstrip("@")
    reg_url = s.pocketoption_register_http_url()
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=tr(lang, "kb.register_on_po"), url=reg_url)],
        [InlineKeyboardButton(text=tr(lang, "kb.ive_registered"), callback_data="reg:connect")],
    ]
    if sup:
        rows.append([InlineKeyboardButton(text=tr(lang, "kb.support"), url=f"https://t.me/{sup}")])
    else:
        rows.append([InlineKeyboardButton(text=tr(lang, "kb.support"), callback_data="start:support")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _lang_of(user: User | None) -> str:
    if user is None:
        return "en"
    return user.settings.language


async def _lang_for_telegram(telegram_id: int) -> str:
    u = await users_repo.get_user(telegram_id)
    return _lang_of(u)


def _project_root() -> Path:
    # handlers.py -> bot/ -> app/ -> repo root
    return Path(__file__).resolve().parents[2]


def _start_banner_path() -> Path:
    return _project_root() / "assets" / "start_banner.png"


def _get_tokens_banner_path() -> Path:
    return _project_root() / "assets" / "get_tokens_banner.png"


def _my_account_banner_path() -> Path:
    return _project_root() / "assets" / "my_account_banner.png"


def _settings_banner_path() -> Path:
    return _project_root() / "assets" / "settings_banner.png"


def _autotrade_settings_banner_path() -> Path:
    return _project_root() / "assets" / "autotrade_settings_banner.png"


def _language_banner_path() -> Path:
    return _project_root() / "assets" / "language_banner.png"


def _status_banner_path() -> Path:
    return _project_root() / "assets" / "status_banner.png"


def _support_banner_path() -> Path:
    return _project_root() / "assets" / "support_banner.png"

def _faq_banner_path() -> Path:
    return _project_root() / "assets" / "faq_banner.png"


async def _media_file_id(key: str) -> str | None:
    item = await media_repo.get_media(key)
    if item is None:
        return None
    return item.file_id


_AUTO_STRAT_PRESETS: dict[str, dict[str, int]] = {
    "precision": {"martingale_max_levels": 5, "max_trades_per_day": 15, "expiry_seconds": 5},
    "high_profit": {"martingale_max_levels": 7, "max_trades_per_day": 25, "expiry_seconds": 5},
    "balanced": {"martingale_max_levels": 5, "max_trades_per_day": 20, "expiry_seconds": 10},
    "conservative": {"martingale_max_levels": 3, "max_trades_per_day": 10, "expiry_seconds": 15},
}
_AUTO_STRAT_LINE_EMOJI: dict[str, str] = {
    "precision": "🎯",
    "high_profit": "⚡",
    "balanced": "📊",
    "conservative": "🛡️",
}
_AUTO_STRAT_TR_KEYS: dict[str, str] = {
    "precision": "strat.precision",
    "high_profit": "strat.high_profit",
    "balanced": "strat.balanced",
    "conservative": "strat.conservative",
}


def _autotrade_settings_caption_html(user: User) -> str:
    lang = user.settings.language
    key = user.settings.strategy_preset
    tkey = _AUTO_STRAT_TR_KEYS.get(key, "strat.precision")
    title = tr(lang, tkey)
    emoji = _AUTO_STRAT_LINE_EMOJI.get(key, "🎯")
    ms = user.settings.martingale_max_levels
    md = user.settings.max_trades_per_day
    ex = user.settings.expiry_seconds
    return tr(
        lang,
        "caption.autotrade",
        title=html.escape(title),
        emoji=emoji,
        ms=ms,
        md=md,
        ex=ex,
    )


async def _send_autotrade_settings_screen(message: Message, telegram_id: int) -> None:
    user = await users_repo.get_user(telegram_id)
    if user is None:
        return
    cap = _autotrade_settings_caption_html(user)
    kb = autotrade_strategy_menu(user.settings.language)
    file_id = await _media_file_id("autotrade_settings_banner")
    banner = _autotrade_settings_banner_path()
    if file_id:
        await message.answer_photo(
            photo=file_id,
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    elif banner.exists():
        await message.answer_photo(
            photo=FSInputFile(str(banner)),
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            cap + "\n\n(add assets/autotrade_settings_banner.png)",
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )


async def _send_manual_settings_compact(message: Message, telegram_id: int) -> None:
    """🔧 Manual settings + Max steps / Max cycles / Back (client-style)."""
    user = await users_repo.get_user(telegram_id)
    if user is None:
        return
    ms = user.settings.martingale_max_levels
    mc = user.settings.max_trades_per_day
    lang = user.settings.language
    cap = tr(lang, "caption.manual_compact", ms=ms, mc=mc)
    await message.answer(
        cap,
        reply_markup=manual_settings_compact_menu(lang),
        parse_mode=ParseMode.HTML,
    )


def _start_trading_tutorial_path() -> Path:
    return _project_root() / "assets" / "start_trading_tutorial.png"


def _start_trading_tutorial_video_path() -> Path:
    return _project_root() / "assets" / "en_how_to_switch.mp4"


def _demo_settings_video_path() -> Path:
    return _project_root() / "assets" / "en_settings.mp4"


def _register_video_path() -> Path:
    return _project_root() / "assets" / "en_how_to_register.mp4"


def _demo_loss_banner_path() -> Path:
    return _project_root() / "assets" / "demo_loss.png"


def _demo_profit_banner_path() -> Path:
    return _project_root() / "assets" / "demo_profit.png"


def _fmt_money(value: object) -> str:
    try:
        v = float(value)  # type: ignore[arg-type]
    except Exception:
        return "N/A"
    return f"{v:,.2f} USD"


def _mask_email(email: str) -> str:
    e = (email or "").strip()
    if "@" not in e:
        return "N/A"
    name, domain = e.split("@", 1)
    if len(name) <= 2:
        masked = name[:1] + "*"
    else:
        masked = name[:1] + "*" * (len(name) - 2) + name[-1:]
    return f"{masked}@{domain}"


def _extract_number(obj: object) -> float | None:
    if obj is None:
        return None
    if isinstance(obj, (int, float)):
        return float(obj)
    if isinstance(obj, str):
        t = obj.strip().replace(",", "")
        try:
            return float(t)
        except Exception:
            return None
    return None


def _extract_balance_fields(payload: object) -> tuple[str, str, str]:
    """
    Returns (mode, real_balance_str, demo_balance_str) best-effort from a balance payload.
    """
    mode = "QT-Demo"
    if isinstance(payload, dict):
        mode = str(payload.get("mode") or payload.get("trading_mode") or mode)
    real_v, demo_v = extract_real_demo_usd(payload)
    return mode, (_fmt_money(real_v) if real_v is not None else "N/A"), (_fmt_money(demo_v) if demo_v is not None else "N/A")


def _normalize_po_uid_value(raw: object) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        try:
            if raw != raw:  # NaN
                return None
            i = int(raw)
            if abs(float(raw) - float(i)) > 1e-9:
                return None
            s = str(i)
            return s if 4 <= len(s) <= 16 else None
        except Exception:
            return None
    s = str(raw).strip()
    if not s:
        return None
    if s.isdigit() and 4 <= len(s) <= 16:
        return s
    if re.fullmatch(r"[A-Za-z0-9_-]{4,32}", s):
        return s
    return None


def _extract_pocketoption_uid(payload: object) -> str | None:
    """
    Best-effort UID extraction from PO profile/balance payloads.
    """
    if not isinstance(payload, dict):
        return None
    keys = (
        "uid",
        "user_id",
        "userId",
        "id",
        "account_id",
        "accountId",
        "trader_id",
        "traderId",
        "customer_id",
        "customerId",
        "pocketoption_id",
        "po_uid",
        "registration_id",
    )
    for k in keys:
        got = _normalize_po_uid_value(payload.get(k))
        if got:
            return got
    for key in ("user", "profile", "data", "result", "account"):
        sub = payload.get(key)
        if isinstance(sub, dict):
            got = _extract_pocketoption_uid(sub)
            if got:
                return got
    return None


async def _fetch_po_profile_balance_uid(telegram_id: int) -> tuple[str | None, object | None]:
    uid: str | None = None
    bal: object | None = None
    prof: object | None = None
    try:
        prof = await asyncio.wait_for(pocketoption_auth.profile(telegram_id), timeout=6.0)
        uid = _extract_pocketoption_uid(prof)
    except Exception:
        pass
    try:
        if get_settings().pocketoption_balance_path_configured():
            bal = await asyncio.wait_for(pocketoption_auth.balance(telegram_id), timeout=8.0)
            if not uid:
                uid = _extract_pocketoption_uid(bal)
        else:
            bal = prof
    except Exception:
        bal = None if get_settings().pocketoption_balance_path_configured() else prof
    return uid, bal


async def _ensure_pocketoption_uid_persisted(telegram_id: int, uid_from_api: str | None) -> str | None:
    uid = uid_from_api
    if uid:
        await users_repo.update_settings(telegram_id, {"pocketoption_uid": uid})
    else:
        u2 = await users_repo.get_user(telegram_id)
        uid = (u2.settings.pocketoption_uid if u2 else "").strip() or None
    if uid:
        await affiliate_repo.merge_pocketoption_uid(telegram_id, uid)
    return uid


async def _run_demo_trade_anim(
    message: Message,
    telegram_id: int,
    stake: float,
    lang: str,
    sess: dict[str, Any],
) -> None:
    stop: asyncio.Event = sess["stop"]
    base_balance: float = float(sess["base_balance"])
    tokens: int = int(sess["tokens"])
    bot = message.bot
    kb_stop = _demo_session_stop_keyboard(lang)

    lines = _materialize_demo_frame(_DEMO_FRAMES_RAW[0])
    sess["lines"] = lines
    running = base_balance + _resolved_pnl_running_total(lines)
    cap = _render_demo_progress_caption(lang, lines, running, tokens)

    banner_id = await _media_file_id("demo_profit_banner")
    banner_path = _demo_profit_banner_path()
    if banner_id:
        sent = await message.answer_photo(
            photo=banner_id,
            caption=cap,
            reply_markup=kb_stop,
            parse_mode=ParseMode.HTML,
        )
    elif banner_path.exists():
        sent = await message.answer_photo(
            photo=FSInputFile(str(banner_path)),
            caption=cap,
            reply_markup=kb_stop,
            parse_mode=ParseMode.HTML,
        )
    else:
        sent = await message.answer(cap, reply_markup=kb_stop, parse_mode=ParseMode.HTML)

    sess["message"] = sent
    frame_i = 1
    extra_i = 0

    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=2.5)
        except asyncio.TimeoutError:
            pass
        if stop.is_set():
            break
        if frame_i < len(_DEMO_FRAMES_RAW):
            lines = _materialize_demo_frame(_DEMO_FRAMES_RAW[frame_i])
            frame_i += 1
        else:
            prev = list(sess["lines"])
            lines = [_DemoProgressLine(x.status, x.asset, x.amount, x.arrow) for x in prev]
            asset = _EXTRA_DEMO_ASSETS[extra_i % len(_EXTRA_DEMO_ASSETS)]
            extra_i += 1
            bump = round(3.2 + (extra_i % 11) * 0.31, 2)
            lines.append(_DemoProgressLine("win", asset, bump, False))

        sess["lines"] = lines
        running = base_balance + _resolved_pnl_running_total(lines)
        cap = _render_demo_progress_caption(lang, lines, running, tokens)
        try:
            await _safe_edit_demo_caption(bot, sent.chat.id, sent.message_id, cap, kb_stop)
        except Exception:
            break


async def _start_manual_demo_trade(message: Message, telegram_id: int, stake: float) -> None:
    """
    Opens a client-style manual demo session: profit banner, growing trade list,
    live caption updates until the user taps Stop (then one simulated trade row is stored).
    """
    user = await users_repo.get_user(telegram_id)
    if user is None or user.blocked:
        return

    await _cancel_prior_demo_session(telegram_id)

    lang = (user.settings.language or "en").strip() or "en"
    base_balance = await _demo_starting_balance_usd(telegram_id)
    tokens = await tokens_repo.get_balance(telegram_id)
    stop = asyncio.Event()
    sess: dict[str, Any] = {
        "stop": stop,
        "lines": [],
        "base_balance": base_balance,
        "stake": float(stake),
        "telegram_id": telegram_id,
        "lang": lang,
        "tokens": tokens,
    }
    _demo_sessions[telegram_id] = sess

    async def _runner() -> None:
        try:
            await _run_demo_trade_anim(message, telegram_id, float(stake), lang, sess)
        except asyncio.CancelledError:
            raise
        except Exception:
            pass

    task = asyncio.create_task(_runner())
    sess["task"] = task


def _status_tier_for_tokens(tokens: int) -> str:
    s = get_settings()
    raw = (s.status_tiers_json or "").strip()
    tiers: list[dict] = []
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                tiers = [x for x in parsed if isinstance(x, dict)]
        except Exception:
            tiers = []

    # Default tiers if not configured.
    if not tiers:
        tiers = [
            {"name": "Bronze", "min": 0},
            {"name": "Silver", "min": 100},
            {"name": "Gold", "min": 500},
            {"name": "Platinum", "min": 2000},
        ]

    best_name = str(tiers[0].get("name") or "Bronze")
    best_min = -1
    for t in tiers:
        name = str(t.get("name") or "").strip() or best_name
        try:
            mn = int(t.get("min") if t.get("min") is not None else 0)
        except Exception:
            continue
        if mn <= tokens and mn >= best_min:
            best_min = mn
            best_name = name
    return best_name


def _status_tier(tokens: int) -> str:
    rule = (get_settings().status_tier_rule or "").strip().lower() or "tokens"
    if rule == "tokens":
        return _status_tier_for_tokens(tokens)
    # Unknown rule → safe default.
    return _status_tier_for_tokens(tokens)


def _tier_line_emoji(tier_name: str) -> str:
    """Medal / badge emoji for the status line (matches client dashboard style)."""
    key = tier_name.strip().casefold()
    return {
        "bronze": "🥉",
        "silver": "🥈",
        "gold": "🥇",
        "platinum": "💠",
    }.get(key, "🏅")


async def _signal_accuracy_text(telegram_id: int) -> str:
    s = get_settings()
    min_n = max(0, int(s.accuracy_min_trades))
    if s.accuracy_count_only_base_martingale_trades:
        window = max(0, int(s.accuracy_session_trades))
        pnls = await trades_repo.last_settled_pnls_session(
            telegram_id,
            window,
            exclude_martingale_recovery=True,
        )
    else:
        window = max(0, int(s.accuracy_window_trades))
        pnls = await trades_repo.last_settled_pnls(telegram_id, window)
    if not pnls:
        return "0%"
    if len(pnls) < min_n:
        return "0%"
    wins = sum(1 for p in pnls if p > 0)
    total = len(pnls)
    pct = (wins / total) * 100.0 if total else 0.0
    return f"{pct:.0f}%"


async def _live_or_cached_balance_strings(telegram_id: int) -> tuple[str, str, str]:
    """
    (mode, real_balance_str, demo_balance_str) from live PO balance when possible,
    else fall back to values saved at last successful refresh (login / worker).
    """
    mode = "QT-Demo"
    real_bal = "N/A"
    demo_bal = "N/A"
    u = await users_repo.get_user(telegram_id)
    creds = await credentials_repo.get_credentials(telegram_id)
    if creds:
        try:
            if get_settings().pocketoption_balance_path_configured():
                bal = await pocketoption_auth.balance(telegram_id)
            else:
                bal = await pocketoption_auth.profile(telegram_id)
            mode, real_bal, demo_bal = _extract_balance_fields(bal)
        except Exception:
            pass
    if real_bal == "N/A" and u is not None and u.po_real_balance_usd is not None:
        real_bal = _fmt_money(u.po_real_balance_usd)
    if demo_bal == "N/A" and u is not None and u.po_demo_balance_usd is not None:
        demo_bal = _fmt_money(u.po_demo_balance_usd)
    if creds and real_bal == "N/A" and demo_bal == "N/A":
        try:
            if await refresh_balances_from_cabinet(telegram_id):
                u2 = await users_repo.get_user(telegram_id)
                if u2 is not None:
                    if u2.po_real_balance_usd is not None:
                        real_bal = _fmt_money(u2.po_real_balance_usd)
                    if u2.po_demo_balance_usd is not None:
                        demo_bal = _fmt_money(u2.po_demo_balance_usd)
        except Exception:
            pass
    return mode, real_bal, demo_bal


async def _start_caption_for_user(
    telegram_id: int,
    *,
    post_connect: bool = False,
    po_sync_ok: bool = True,
) -> str:
    """
    Dashboard caption for the client-clone `/start` screen.
    Uses best-effort values; if broker data isn't available, shows N/A.
    """
    lang = await _lang_for_telegram(telegram_id)
    tokens = await tokens_repo.get_balance(telegram_id)
    u_row = await users_repo.get_user(telegram_id)
    uid_saved = (u_row.settings.pocketoption_uid if u_row else "").strip()
    uid_display = uid_saved or "N/A"

    tier = _status_tier(tokens)
    accuracy = await _signal_accuracy_text(telegram_id)

    mode, real_bal, demo_bal = await _live_or_cached_balance_strings(telegram_id)

    pad = "  "
    tier_icon = _tier_line_emoji(tier)
    creds = await credentials_repo.get_credentials(telegram_id)
    head: list[str] = []
    if creds:
        email, _pw = creds
        head.append(tr(lang, "dash.linked_email", pad=pad, email=_mask_email(email)))
        head.append(tr(lang, "dash.pocket_uid", pad=pad, uid=uid_display))
    if post_connect:
        head.append(tr(lang, "dash.login_successful"))
        if not po_sync_ok:
            head.append(tr(lang, "dash.broker_pending", pad=pad))
    body = (
        tr(lang, "dash.trading_mode", pad=pad, mode=mode)
        + "\n\n"
        + tr(lang, "dash.real_balance", pad=pad, real_bal=real_bal)
        + "\n"
        + tr(lang, "dash.demo_balance", pad=pad, demo_bal=demo_bal)
        + "\n"
        + tr(lang, "dash.tokens", pad=pad, tokens=tokens)
        + "\n\n"
        + tr(lang, "dash.status", pad=pad, tier_icon=tier_icon, tier=tier)
        + "\n"
        + tr(lang, "dash.accuracy", pad=pad, accuracy=accuracy)
    )
    if head:
        return "\n\n".join(head) + "\n\n" + body
    return body


async def _send_start_sequence(
    message: Message,
    telegram_id: int,
    *,
    post_connect: bool = False,
    po_sync_ok: bool = True,
) -> None:
    """Banner dashboard + inline row + 👇 reply keyboard (same as /start)."""
    if get_settings().auto_trade_only:
        u = await users_repo.get_user(telegram_id)
        if u is not None and not u.settings.strategy_enabled:
            await users_repo.update_settings(telegram_id, {"strategy_enabled": True})
    caption = await _start_caption_for_user(
        telegram_id, post_connect=post_connect, po_sync_ok=po_sync_ok
    )
    lang = await _lang_for_telegram(telegram_id)
    file_id = await _media_file_id("start_banner")
    banner = _start_banner_path()
    km = start_menu(lang)
    if post_connect:
        try:
            await message.answer("\u200c", reply_markup=ReplyKeyboardRemove(), parse_mode=None)
        except TelegramBadRequest:
            pass
    try:
        if file_id:
            await message.answer_photo(photo=file_id, caption=caption, reply_markup=km, parse_mode=None)
        elif banner.exists():
            await message.answer_photo(
                photo=FSInputFile(str(banner)),
                caption=caption,
                reply_markup=km,
                parse_mode=None,
            )
        else:
            await message.answer(
                caption + "\n\n(banner missing: add assets/start_banner.png)",
                reply_markup=km,
                parse_mode=None,
            )
    except TelegramBadRequest:
        # Stale file_id from another bot/deploy is common on Heroku if Mongo was copied.
        await message.answer(caption, reply_markup=km, parse_mode=None)
    await message.answer("👇", reply_markup=start_reply_menu(lang), parse_mode=None)


async def _send_registration_screen(message: Message, telegram_id: int) -> None:
    user = await users_repo.get_user(telegram_id)
    lang = user.settings.language if user is not None else "en"
    cap = tr(lang, "caption.register")
    kb = _registration_keyboard(lang)

    vid_id = await _media_file_id("register_video")
    if vid_id:
        try:
            await message.answer_video(video=vid_id, caption=cap, reply_markup=kb, parse_mode=None)
            return
        except TelegramBadRequest:
            pass
    vid = _register_video_path()
    if vid.exists():
        try:
            await message.answer_video(video=FSInputFile(str(vid)), caption=cap, reply_markup=kb, parse_mode=None)
            return
        except TelegramBadRequest:
            pass
    banner_id = await _media_file_id("register_banner")
    if banner_id:
        try:
            await message.answer_photo(photo=banner_id, caption=cap, reply_markup=kb, parse_mode=None)
            return
        except TelegramBadRequest:
            pass
    await message.answer(cap, reply_markup=kb, parse_mode=None)


async def _send_demo_account_screen(message: Message, telegram_id: int) -> None:
    """Tutorial for settings + DEMO ACCOUNT caption + bet grid (client style)."""
    user = await users_repo.get_user(telegram_id)
    if user is None:
        return
    levels = int(user.settings.martingale_max_levels)
    lang = user.settings.language
    caption = tr(lang, "caption.demo_account", levels=levels)
    file_id = await _media_file_id("demo_settings_video")
    vid = _demo_settings_video_path()
    kb = demo_account_bet_menu(lang)
    if file_id:
        await message.answer_video(
            video=file_id,
            caption=caption,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    elif vid.exists():
        await message.answer_video(
            video=FSInputFile(str(vid)),
            caption=caption,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            caption + "\n\n(add assets/en_settings.mp4)",
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )


async def _send_demo_lever_screen(message: Message, telegram_id: int) -> None:
    user = await users_repo.get_user(telegram_id)
    if user is None:
        return
    lang = user.settings.language
    ex = await system_repo.get_global_trade_expiry_seconds()
    await message.answer(
        tr(lang, "caption.demo_lever", expiry=int(ex)),
        reply_markup=demo_lever_menu(lang),
        parse_mode=ParseMode.HTML,
    )


async def _send_trade_account_choice(message: Message, telegram_id: int) -> None:
    """Tutorial video (or fallback image) + caption + demo / real / main inline buttons."""
    if not await credentials_repo.get_credentials(telegram_id):
        await _send_registration_screen(message, telegram_id)
        return
    lang = await _lang_for_telegram(telegram_id)
    caption = tr(lang, "caption.trade_where")
    kb = trade_account_choice_menu(lang)
    video_id = await _media_file_id("start_trading_video")
    video = _start_trading_tutorial_video_path()
    if video_id:
        await message.answer_video(
            video=video_id,
            caption=caption,
            reply_markup=kb,
            parse_mode=None,
        )
        return
    if video.exists():
        await message.answer_video(
            video=FSInputFile(str(video)),
            caption=caption,
            reply_markup=kb,
            parse_mode=None,
        )
        return
    tut_id = await _media_file_id("start_trading_tutorial")
    tut = _start_trading_tutorial_path()
    if tut_id:
        await message.answer_photo(
            photo=tut_id,
            caption=caption,
            reply_markup=kb,
            parse_mode=None,
        )
    elif tut.exists():
        await message.answer_photo(
            photo=FSInputFile(str(tut)),
            caption=caption,
            reply_markup=kb,
            parse_mode=None,
        )
    else:
        await message.answer(
            caption
            + "\n\n(add assets/en_how_to_switch.mp4, or start_trading_tutorial.png)",
            reply_markup=kb,
            parse_mode=None,
        )


async def _send_get_tokens_screen(message: Message, telegram_id: int) -> None:
    """ADD BALANCE image + token tiers + promo + support link + deposit / main menu."""
    lang = await _lang_for_telegram(telegram_id)
    cap = _get_tokens_screen_caption_html()
    kb = get_tokens_screen_keyboard(get_settings().http_deposit_page_url(), lang)
    file_id = await _media_file_id("get_tokens_banner")
    banner = _get_tokens_banner_path()
    if file_id:
        await message.answer_photo(
            photo=file_id,
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    elif banner.exists():
        await message.answer_photo(
            photo=FSInputFile(str(banner)),
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            cap + "\n\n(add assets/get_tokens_banner.png)",
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )


async def _my_account_caption_html(telegram_id: int) -> str:
    """My Account stats under MY ACCOUNT banner (HTML)."""
    lang = await _lang_for_telegram(telegram_id)
    tokens_bal = await tokens_repo.get_balance(telegram_id)
    tier = _status_tier(tokens_bal)
    tier_e = _tier_line_emoji(tier)
    real_n, real_pnl = await trades_repo.settled_count_and_pnl(telegram_id, "pocketoption")
    demo_n, demo_pnl = await trades_repo.settled_count_and_pnl(telegram_id, "simulated")
    _, real_bal, demo_bal = await _live_or_cached_balance_strings(telegram_id)

    cap = tr(
        lang,
        "caption.my_account",
        tier_e=tier_e,
        tier=html.escape(tier),
        real_bal=html.escape(real_bal),
        real_n=real_n,
        real_pnl=f"{real_pnl:,.2f}",
        demo_bal=html.escape(demo_bal),
        demo_n=demo_n,
        demo_pnl=f"{demo_pnl:,.2f}",
        tokens_bal=tokens_bal,
    )
    u = await users_repo.get_user(telegram_id)
    uid = (u.settings.pocketoption_uid if u else "").strip()
    if uid:
        cap += f"\n\n🆔 <b>PO UID:</b> {html.escape(uid)}"
    return cap


async def _send_my_account_screen(message: Message, telegram_id: int) -> None:
    creds = await credentials_repo.get_credentials(telegram_id)
    connected = bool(creds)
    lang = await _lang_for_telegram(telegram_id)
    po_label = _mask_email(creds[0]) if creds else "not linked"
    po_btn = (
        tr(lang, "kb.po_linked", email=po_label) if connected else tr(lang, "kb.po_connect")
    )
    if len(po_btn) > 64:
        po_btn = po_btn[:61] + "..."
    s = get_settings()
    cap = await _my_account_caption_html(telegram_id)
    kb = my_account_menu(
        po_connected=connected,
        po_button_text=po_btn,
        deposit_page_url=s.http_deposit_page_url(),
        withdraw_page_url=s.http_withdraw_page_url(),
        lang=lang,
    )
    file_id = await _media_file_id("my_account_banner")
    banner = _my_account_banner_path()
    if file_id:
        await message.answer_photo(
            photo=file_id,
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    elif banner.exists():
        await message.answer_photo(
            photo=FSInputFile(str(banner)),
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            cap + "\n\n(add assets/my_account_banner.png)",
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )


async def _send_status_screen(message: Message, telegram_id: int) -> None:
    """
    STATUS banner + status summary + Deposit / Main Menu buttons (client-style).
    """
    user = await users_repo.get_user(telegram_id)
    if user is None:
        return
    lang = user.settings.language
    tokens_bal = await tokens_repo.get_balance(telegram_id)
    tier = _status_tier(tokens_bal)
    tier_e = _tier_line_emoji(tier)
    acc = await _signal_accuracy_text(telegram_id)
    # We do not currently track real-money deposit per user, so show tokens-based status.
    cap = (
        f"🏅 Your status: {tier_e} {html.escape(tier)}\n\n"
        f"💎 Tokens: {tokens_bal}\n"
        f"📊 Signal accuracy: {acc}\n"
    )
    s = get_settings()
    kb = status_screen_keyboard(s.http_deposit_page_url(), lang)
    file_id = await _media_file_id("status_banner")
    banner = _status_banner_path()
    if file_id:
        await message.answer_photo(
            photo=file_id,
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    elif banner.exists():
        await message.answer_photo(
            photo=FSInputFile(str(banner)),
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            cap + "\n\n(add assets/status_banner.png)",
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )


async def _send_support_screen(message: Message, telegram_id: int) -> None:
    """
    SUPPORT banner + configured support message + Support / Main Menu buttons.
    """
    lang = await _lang_for_telegram(telegram_id)
    text = _support_message()
    kb = support_screen_keyboard(lang)
    file_id = await _media_file_id("support_banner")
    banner = _support_banner_path()
    if file_id:
        await message.answer_photo(
            photo=file_id,
            caption=text,
            reply_markup=kb,
            parse_mode=None,
        )
    elif banner.exists():
        await message.answer_photo(
            photo=FSInputFile(str(banner)),
            caption=text,
            reply_markup=kb,
            parse_mode=None,
        )
    else:
        await message.answer(
            text + "\n\n(add assets/support_banner.png)",
            reply_markup=kb,
            parse_mode=None,
        )


async def _send_faq_screen(message: Message, telegram_id: int) -> None:
    """
    FAQ banner + FAQ text + Support / Main Menu buttons.
    """
    lang = await _lang_for_telegram(telegram_id)
    text = _faq_message()
    kb = faq_screen_keyboard(lang)
    file_id = await _media_file_id("faq_banner")
    banner = _faq_banner_path()
    if file_id:
        await message.answer_photo(
            photo=file_id,
            caption=text,
            reply_markup=kb,
            parse_mode=None,
        )
    elif banner.exists():
        await message.answer_photo(
            photo=FSInputFile(str(banner)),
            caption=text,
            reply_markup=kb,
            parse_mode=None,
        )
    else:
        await message.answer(
            text + "\n\n(add assets/faq_banner.png)",
            reply_markup=kb,
            parse_mode=None,
        )


def _settings_hub_caption_html(lang: str) -> str:
    if get_settings().auto_trade_only:
        return tr(lang, "caption.settings_hub_auto_only")
    return tr(lang, "caption.settings_hub")


def _expiration_time_caption_html(lang: str, current_seconds: int) -> str:
    return tr(lang, "caption.expiration", seconds=current_seconds)


async def _send_language_screen(message: Message, telegram_id: int) -> None:
    lang = await _lang_for_telegram(telegram_id)
    cap = tr(lang, "msg.choose_language")
    kb = language_pick_menu(lang)
    file_id = await _media_file_id("language_banner")
    banner = _language_banner_path()
    if file_id:
        await message.answer_photo(
            photo=file_id,
            caption=cap,
            reply_markup=kb,
            parse_mode=None,
        )
    elif banner.exists():
        await message.answer_photo(
            photo=FSInputFile(str(banner)),
            caption=cap,
            reply_markup=kb,
            parse_mode=None,
        )
    else:
        await message.answer(
            cap + "\n\n(add assets/language_banner.png)",
            reply_markup=kb,
            parse_mode=None,
        )


async def _send_settings_hub_screen(message: Message, telegram_id: int) -> None:
    lang = await _lang_for_telegram(telegram_id)
    if get_settings().auto_trade_only:
        u0 = await users_repo.get_user(telegram_id)
        if u0 is not None and not u0.settings.strategy_enabled:
            await users_repo.update_settings(telegram_id, {"strategy_enabled": True})
    cap = _settings_hub_caption_html(lang)
    kb = settings_hub_menu(lang)
    file_id = await _media_file_id("settings_banner")
    banner = _settings_banner_path()
    if file_id:
        await message.answer_photo(
            photo=file_id,
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    elif banner.exists():
        await message.answer_photo(
            photo=FSInputFile(str(banner)),
            caption=cap,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            cap + "\n\n(add assets/settings_banner.png)",
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )


async def _real_account_balance_usd(telegram_id: int) -> float | None:
    """Parsed real balance from PocketOption, or None if unknown / N/A."""
    try:
        if get_settings().pocketoption_balance_path_configured():
            bal = await pocketoption_auth.balance(telegram_id)
        else:
            bal = await pocketoption_auth.profile(telegram_id)
        _, real_s, _ = _extract_balance_fields(bal)
        if real_s == "N/A":
            return None
        cleaned = real_s.replace("USD", "").strip().replace(",", "")
        return _extract_number(cleaned)
    except Exception:
        return None


def _is_real_balance_empty(value: float | None) -> bool:
    if value is None:
        return True
    return value <= 0


async def _send_real_mode_unavailable_screen(message: Message, telegram_id: int) -> None:
    """Client copy when real mode is blocked (empty real balance)."""
    lang = await _lang_for_telegram(telegram_id)
    text = tr(lang, "gate.real_unavailable")
    await message.answer(text, reply_markup=demo_real_gate_keyboard(lang), parse_mode=None)


def _support_message() -> str:
    s = get_settings()
    text = (s.support_text or "").strip()
    if not text:
        u = (s.support_telegram_username or "").strip().lstrip("@")
        if u:
            text = f"😊 Questions? Message @{u}"
        else:
            text = "😊 Questions? Tap Support below."
    url = (s.support_url or "").strip()
    if url:
        return f"{text}\n{url}"
    return text


def _fmt_usd_amount(n: float) -> str:
    if n == int(n):
        return str(int(n))
    return f"{n:g}"


def _get_tokens_screen_caption_html() -> str:
    """HTML caption for Get Tokens (ADD BALANCE banner). Numbers follow token bracket settings."""
    s = get_settings()
    low_min = float(s.token_deposit_min_usd)
    high_min = float(s.token_bracket_high_min_usd)
    low_grant = int(s.token_bracket_low_grant)
    per = float(s.token_bracket_high_per_dollar)
    tier_top = high_min - 0.01
    ex_tokens = int(round(high_min * per))
    per_txt = _fmt_usd_amount(per)
    per_rate = int(per) if per == int(per) else per

    lines = [
        "🔥 Top up your balance and get tokens for trading",
        "",
        f"💰 ${_fmt_usd_amount(low_min)}–{_fmt_usd_amount(tier_top)} → {low_grant} tokens",
        f"💰 ${_fmt_usd_amount(high_min)}+ → {per_rate:g} token per {per_txt}$ "
        f"(${_fmt_usd_amount(high_min)}$ = {ex_tokens} tokens)",
    ]
    promo = (s.get_tokens_promo_code or "").strip()
    if promo:
        lines.extend(["", f"💯 PROMO CODE — <code>{html.escape(promo)}</code>"])
    sup = (s.support_telegram_username or "").strip().lstrip("@")
    if sup:
        lines.extend(
            [
                "",
                f'😊 Have questions? Message <a href="https://t.me/{html.escape(sup)}">@{html.escape(sup)}</a>',
            ]
        )
    return "\n".join(lines)


def _real_account_first_deposit_html() -> str:
    """Copy for Real account path — numbers follow token/deposit settings."""
    s = get_settings()
    min_usd = float(s.token_deposit_min_usd)
    low_grant = int(s.token_bracket_low_grant)
    hi_min = float(s.token_bracket_high_min_usd)
    per = float(s.token_bracket_high_per_dollar)
    rec_tokens = int(hi_min * per)
    per_disp = _fmt_usd_amount(per)
    promo = (s.deposit_promo_code or "").strip()

    lines: list[str] = [
        "💰 Real trading requires a first deposit",
        "",
        f"<b>MINIMUM</b> ${_fmt_usd_amount(min_usd)} → get {low_grant} tokens",
        f"Recommended ${_fmt_usd_amount(hi_min)}+ → get {rec_tokens}+ tokens (${per_disp} → 1 token)",
    ]
    if promo:
        lines.extend(
            [
                "",
                "Use PROMO CODE to get x2 balance 👇",
                f"<code>{html.escape(promo)}</code>",
            ]
        )
    lines.extend(["", "Try demo mode first or deposit now 👇"])
    return "\n".join(lines)


def _faq_message() -> str:
    s = get_settings()
    text = (s.faq_text or "").strip()
    if not text:
        sup = (s.support_telegram_username or "").strip().lstrip("@") or "support"
        text = "\n".join(
            [
                "❓ FAQ",
                "",
                "1️⃣ How does the bot work?",
                "Connects to Pocket Option and trades automatically",
                "",
                "2️⃣ Which platform?",
                "Pocket Option — since 2017",
                "",
                "3️⃣ Min balance?",
                "MINIMUM $20, recommended $50-100",
                "",
                "4️⃣ Bonuses?",
                "Promo codes +100% to +200%",
                "",
                "5️⃣ What are Tokens?",
                "1 Token = 1 AI trading cycle",
                "",
                "6️⃣ Is it safe?",
                "Bot has no withdrawal access",
                "",
                "7️⃣ Earnings?",
                "10-20% daily potential",
                "",
                "8️⃣ Can I lose?",
                "Yes, no 100% guarantee",
                "",
                "9️⃣ Setup time?",
                "Under 1 minute",
                "",
                "🔟 Online required?",
                "No, 5-10 min sessions",
                "",
                f"😊 Questions? Message @{sup}",
            ]
        )
    url = (s.faq_url or "").strip()
    if url:
        return f"{text}\n{url}"
    return text


def _tokens_topup_message() -> str:
    s = get_settings()
    url = (s.token_topup_url or "").strip() or (s.deposit_url or "").strip()
    text = (s.token_topup_text or "").strip()
    if not text:
        text = (
            "To get tokens, make a deposit using the Deposit link. "
            "If token credits are enabled, the server will credit tokens from affiliate/deposit postbacks."
        )
    if url:
        return f"{text}\n{url}"
    return text


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user is None:
        await message.answer("Could not read your Telegram user. Open the bot from your account and try again.")
        return
    try:
        user = await users_repo.ensure_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )
    except Exception as exc:
        log_exception(
            "start_ensure_user_failed",
            exc,
            telegram_id=getattr(message.from_user, "id", None),
        )
        await message.answer(
            "The bot could not load your profile (usually MongoDB is down, unreachable, or misconfigured).\n\n"
            "Start the bot with:\n"
            "  python -m app\n"
            "and set MONGODB_URI / MONGODB_DB in .env.\n\n"
            "Note: running only the API (python -m app.web) does not process Telegram messages.",
            parse_mode=None,
        )
        return
    if user.blocked:
        await message.answer("access denied")
        return
    try:
        creds = await credentials_repo.get_credentials(user.telegram_id)
        if not creds:
            await _send_registration_screen(message, user.telegram_id)
            return
        await _send_start_sequence(message, user.telegram_id)
    except Exception as exc:
        log_exception(
            "start_send_flow_failed",
            exc,
            telegram_id=user.telegram_id,
        )
        await message.answer(
            "Could not finish /start (see server logs). Common fixes:\n"
            "• Set MASTER_KEY in .env and keep it stable (changing it breaks saved logins).\n"
            "• If you rotated MASTER_KEY, use /connect again after clearing old credentials.\n"
            "• Ensure MongoDB is reachable.",
            parse_mode=None,
        )


@router.message(Command("help", ignore_mention=True))
async def help_cmd(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    await message.answer(ADMIN_HELP_TEXT, parse_mode=None)


@router.message(Command("status"))
async def status_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    aff = await affiliate_repo.describe_status(user.telegram_id)
    bal = await tokens_repo.get_balance(user.telegram_id)
    await message.answer(
        user_status_text(user) + f"\ntokens: {bal}\naffiliate: {aff}",
        reply_markup=main_menu(user.settings.language, user.settings.trading_enabled),
    )


@router.message(Command("tokens"))
async def tokens_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    bal = await tokens_repo.get_balance(user.telegram_id)
    st = get_settings()
    per = int(st.tokens_per_trade) if st.token_system_enabled else 0
    await message.answer(f"balance: {bal}\nper trade: {per}")


@router.message(Command("settings"))
async def settings_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await _send_settings_hub_screen(message, user.telegram_id)


@router.message(Command("enable"))
async def enable_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await users_repo.set_trading_enabled(user.telegram_id, True)
    user = await users_repo.get_user(user.telegram_id)
    if user is None:
        return
    await message.answer("trading enabled", reply_markup=main_menu(user.settings.language, user.settings.trading_enabled))


@router.message(Command("disable"))
async def disable_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await users_repo.set_trading_enabled(user.telegram_id, False)
    user = await users_repo.get_user(user.telegram_id)
    if user is None:
        return
    await message.answer("trading disabled", reply_markup=main_menu(user.settings.language, user.settings.trading_enabled))


@router.message(Command("connect"))
async def connect_cmd(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await state.set_state(ConnectFlow.email)
    await message.answer("send pocketoption email")


@router.callback_query(F.data == "reg:connect")
async def reg_connect(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(ConnectFlow.email)
    await cb.message.answer(
        "📝 Enter your Pocket Option email:\n\n"
        "Your UID will be detected automatically after you sign in.",
        parse_mode=None,
    )
    await cb.answer()


@router.message(ConnectFlow.uid)
async def connect_uid(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    uid = (message.text or "").strip()
    if not uid.isdigit() or len(uid) < 6 or len(uid) > 16:
        await message.answer("invalid UID. send digits only (example: 125704464).", parse_mode=None)
        return
    await users_repo.update_settings(user.telegram_id, {"pocketoption_uid": uid})
    await state.set_state(ConnectFlow.email)
    await message.answer("✅ UID confirmed! Registration complete!", parse_mode=None)
    await message.answer("📝 Enter your Pocket Option email:", parse_mode=None)


@router.message(ConnectFlow.email)
async def connect_email(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    email = (message.text or "").strip()
    if "@" not in email or len(email) < 5:
        await message.answer("invalid email")
        return
    await state.update_data(email=email)
    await state.set_state(ConnectFlow.password)
    await message.answer(f"📧 Email: {email}", parse_mode=None)
    await message.answer(
        "🔒 Now enter the password for your Pocket Option account:\n"
        "(message with password will be deleted)",
        parse_mode=None,
    )


@router.message(ConnectFlow.password)
async def connect_password(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    data = await state.get_data()
    email = str(data.get("email") or "").strip()
    password = (message.text or "").strip()
    if not email or not password:
        await message.answer("missing email or password")
        await state.clear()
        return
    # Hide password from chat history ASAP.
    try:
        await message.delete()
    except Exception:
        pass
    await credentials_repo.set_credentials(user.telegram_id, email, password)
    await affiliate_repo.link_telegram_id(email, user.telegram_id)
    pending = await affiliate_repo.take_pending_tokens(email)
    if pending > 0:
        await tokens_repo.add_tokens(
            user.telegram_id,
            pending,
            "pending_deposit_sync",
            {"email": email},
        )
    await state.clear()
    po_login_ok = False
    try:
        await pocketoption_auth.login_for_user(user.telegram_id)
        po_login_ok = True
    except Exception as exc:
        log_exception("connect_login_or_profile_failed", exc, telegram_id=user.telegram_id)

    if po_login_ok:
        try:
            uid_from_api, bal = await _fetch_po_profile_balance_uid(user.telegram_id)
            await _ensure_pocketoption_uid_persisted(user.telegram_id, uid_from_api)
            if bal is not None:
                r_f, d_f = extract_real_demo_usd(bal)
                if r_f is not None or d_f is not None:
                    await users_repo.merge_po_balance_cache(
                        user.telegram_id, real_usd=r_f, demo_usd=d_f
                    )
        except Exception as exc:
            log_exception("connect_profile_fetch_failed", exc, telegram_id=user.telegram_id)

        try:
            await refresh_balances_from_cabinet(user.telegram_id)
        except Exception as exc:
            log_exception("connect_cabinet_sync_failed", exc, telegram_id=user.telegram_id)

    if get_settings().affiliate_gate_required and po_login_ok:
        u_chk = await users_repo.get_user(user.telegram_id)
        uid_chk = (u_chk.settings.pocketoption_uid if u_chk else "").strip() or None
        ok_uid = uid_chk is not None and await affiliate_repo.is_uid_registered_with_affiliate(
            uid_chk
        )
        if not ok_uid:
            await credentials_repo.delete_credentials(user.telegram_id)
            await affiliate_repo.clear_telegram_link(user.telegram_id)
            await message.answer(
                "❌ This account has not been registered with our link.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode=None,
            )
            await _send_registration_screen(message, user.telegram_id)
            return

    u_final = await users_repo.get_user(user.telegram_id)
    has_bal = u_final is not None and (
        u_final.po_real_balance_usd is not None or u_final.po_demo_balance_usd is not None
    )
    po_sync_ok = po_login_ok and has_bal

    await _send_start_sequence(
        message,
        user.telegram_id,
        post_connect=True,
        po_sync_ok=po_sync_ok,
    )


@router.message(Command("disconnect"))
async def disconnect_cmd(message: Message, state: FSMContext):
    await state.clear()
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await credentials_repo.delete_credentials(user.telegram_id)
    await affiliate_repo.clear_telegram_link(user.telegram_id)
    await message.answer("disconnected")


@router.message(Command("sync_uid"))
async def sync_uid_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    if await credentials_repo.get_credentials(user.telegram_id) is None:
        await message.answer("use /connect first", parse_mode=None)
        return
    try:
        await pocketoption_auth.login_for_user(user.telegram_id)
    except Exception:
        await message.answer("login refresh failed", parse_mode=None)
        return
    uid_from_api, _bal = await _fetch_po_profile_balance_uid(user.telegram_id)
    uid = await _ensure_pocketoption_uid_persisted(user.telegram_id, uid_from_api)
    await refresh_po_balance_cache_for_telegram(user.telegram_id)
    if uid:
        await message.answer(f"UID ok: {uid}", parse_mode=None)
        return
    await message.answer("could not read UID from Pocket Option", parse_mode=None)


@router.message(Command("sync_balance"))
async def sync_balance_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    if await credentials_repo.get_credentials(user.telegram_id) is None:
        await message.answer("use /connect first", parse_mode=None)
        return
    await refresh_po_balance_cache_for_telegram(user.telegram_id)
    u2 = await users_repo.get_user(user.telegram_id)
    if u2 is None:
        await message.answer("done", parse_mode=None)
        return
    r = _fmt_money(u2.po_real_balance_usd) if u2.po_real_balance_usd is not None else "N/A"
    d = _fmt_money(u2.po_demo_balance_usd) if u2.po_demo_balance_usd is not None else "N/A"
    await message.answer(f"cached real {r} demo {d}", parse_mode=None)


def _parse_manual_balance_arg(raw: str) -> float | None:
    t = (raw or "").strip()
    if not t or t.lower() in ("-", "na", "n/a", "skip", "x", "none"):
        return None
    try:
        return float(t.replace(",", ""))
    except ValueError:
        raise ValueError("bad number")


@router.message(Command("set_uid"))
async def set_uid_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "usage: /set_uid <PO UID>\nExample: /set_uid 128657409",
            parse_mode=None,
        )
        return
    uid = parts[1].strip()
    if not uid.isdigit() or len(uid) < 6 or len(uid) > 16:
        await message.answer("invalid UID — send 6–16 digits only.", parse_mode=None)
        return
    await users_repo.update_settings(user.telegram_id, {"pocketoption_uid": uid})
    await affiliate_repo.merge_pocketoption_uid(user.telegram_id, uid)
    await message.answer(f"✅ PO UID saved: {uid}", parse_mode=None)


@router.message(Command("set_balances"))
async def set_balances_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer(
            "usage: /set_balances <real_usd> <demo_usd>\n"
            "Use - or na to leave one side unchanged.\n"
            "Example: /set_balances 150.50 50000",
            parse_mode=None,
        )
        return
    try:
        real_usd = _parse_manual_balance_arg(parts[1])
        demo_usd = _parse_manual_balance_arg(parts[2])
    except ValueError:
        await message.answer("invalid number — use e.g. 100.5 or - to skip.", parse_mode=None)
        return
    if real_usd is None and demo_usd is None:
        await message.answer("at least one of real or demo must be a number.", parse_mode=None)
        return
    await users_repo.merge_po_balance_cache(
        user.telegram_id, real_usd=real_usd, demo_usd=demo_usd
    )
    u2 = await users_repo.get_user(user.telegram_id)
    r = _fmt_money(u2.po_real_balance_usd) if u2 and u2.po_real_balance_usd is not None else "N/A"
    d = _fmt_money(u2.po_demo_balance_usd) if u2 and u2.po_demo_balance_usd is not None else "N/A"
    await message.answer(f"✅ Cached balances updated.\nReal: {r}\nDemo: {d}", parse_mode=None)


@router.message(Command("account"))
async def account_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    try:
        profile = await pocketoption_auth.profile(user.telegram_id)
        if get_settings().pocketoption_balance_path_configured():
            balance = await pocketoption_auth.balance(user.telegram_id)
            await message.answer(f"profile: {profile}\n\nbalance: {balance}")
        else:
            await message.answer(
                f"profile: {profile}\n\n"
                "(no PO_BALANCE_PATH — balances are taken from profile when available)"
            )
    except Exception as e:
        await message.answer(f"account lookup failed: {type(e).__name__}")


@router.message(Command("watch"))
async def watch_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("usage: /watch eurusd,btcusd")
        return
    symbols = [s.strip() for s in parts[1].split(",") if s.strip()]
    if not symbols:
        await message.answer("no symbols")
        return
    lowered = [s.lower() for s in symbols]
    await users_repo.update_settings(user.telegram_id, {"assets": lowered})
    await market_data.watch(user.telegram_id, symbols)
    st = get_settings()
    eff = max(
        float(user.settings.min_payout_percent or 0.0),
        float(st.global_min_payout_percent or 0.0),
        float(st.trade_min_payout_floor_percent or 0.0),
    )
    min_p = eff if eff > 0 else None
    warns: list[str] = []
    for sym in lowered:
        ok, reason = assets.is_tradable(sym, min_payout_percent=min_p, require_otc=st.trade_otc_only)
        if not ok:
            warns.append(f"{sym}: {reason}")
    msg = "watching updated"
    if warns:
        msg += "\n\nnot tradable with current OTC/payout rules:\n" + "\n".join(warns)
    await message.answer(msg)


@router.message(Command("unwatch"))
async def unwatch_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("usage: /unwatch eurusd,btcusd or /unwatch all")
        return
    arg = parts[1].strip().lower()
    if arg == "all":
        await market_data.unwatch(user.telegram_id, None)
        await users_repo.update_settings(user.telegram_id, {"assets": []})
        await message.answer("watching cleared")
        return
    symbols = [s.strip() for s in arg.split(",") if s.strip()]
    if not symbols:
        await message.answer("no symbols")
        return
    current = set(user.settings.assets)
    for s in symbols:
        current.discard(s.lower())
    await users_repo.update_settings(user.telegram_id, {"assets": sorted(current)})
    await market_data.unwatch(user.telegram_id, symbols)
    await message.answer("watching updated")


@router.message(Command("prices"))
async def prices_cmd(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    symbols = await market_data.get_user_symbols(user.telegram_id)
    if not symbols:
        symbols = user.settings.assets
    if not symbols:
        await message.answer("no watched symbols. use /watch")
        return
    prices = await market_data.get_prices(symbols)
    if not prices:
        await message.answer("no prices yet")
        return
    lines = [f"{k}: {v}" for k, v in sorted(prices.items())]
    await message.answer("\n".join(lines))


@router.callback_query(F.data == "menu:status")
async def menu_status(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    aff = await affiliate_repo.describe_status(user.telegram_id)
    bal = await tokens_repo.get_balance(user.telegram_id)
    await cb.message.answer(
        user_status_text(user) + f"\ntokens: {bal}\naffiliate: {aff}",
        reply_markup=main_menu(user.settings.language, user.settings.trading_enabled),
    )
    await cb.answer()


@router.callback_query(F.data == "menu:settings")
async def menu_settings(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_settings_hub_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "settings:hub:autotrade")
async def settings_hub_autotrade(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_autotrade_settings_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data.startswith("auto:strat:"))
async def autotrade_strat_pick(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    key = cb.data.removeprefix("auto:strat:")
    if key == "manual":
        await _send_manual_settings_compact(cb.message, user.telegram_id)
        await cb.answer()
        return
    if key not in _AUTO_STRAT_PRESETS:
        await cb.answer("unknown preset", show_alert=True)
        return
    patch: dict = {**_AUTO_STRAT_PRESETS[key], "strategy_preset": key}
    await users_repo.update_settings(user.telegram_id, patch)
    await _send_autotrade_settings_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "auto:manual:mg_pick")
async def manual_max_steps_pick_open(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    lang = user.settings.language
    await cb.message.answer(
        tr(lang, "caption.max_mg_steps"),
        reply_markup=max_steps_quick_pick_menu(lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.callback_query(F.data == "auto:manual:mg_cancel")
async def manual_max_steps_pick_cancel(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_manual_settings_compact(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data.startswith("auto:manual:mgval:"))
async def manual_max_steps_pick_value(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    try:
        v = int(cb.data.split(":")[-1])
    except ValueError:
        await cb.answer("invalid", show_alert=True)
        return
    if v < 1 or v > 20:
        await cb.answer("use 1–20", show_alert=True)
        return
    await users_repo.update_settings(user.telegram_id, {"martingale_max_levels": v})
    await _send_manual_settings_compact(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "auto:manual:cy_pick")
async def manual_max_cycles_pick_open(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    lang = user.settings.language
    await cb.message.answer(
        tr(lang, "caption.max_cycles"),
        reply_markup=max_cycles_quick_pick_menu(lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.callback_query(F.data == "auto:manual:cy_cancel")
async def manual_max_cycles_pick_cancel(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_manual_settings_compact(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data.startswith("auto:manual:cyval:"))
async def manual_max_cycles_pick_value(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    try:
        v = int(cb.data.split(":")[-1])
    except ValueError:
        await cb.answer("invalid", show_alert=True)
        return
    if v < 1 or v > 100000:
        await cb.answer("out of range", show_alert=True)
        return
    await users_repo.update_settings(user.telegram_id, {"max_trades_per_day": v})
    await _send_manual_settings_compact(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "auto:manual:back")
async def manual_settings_back(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_autotrade_settings_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "settings:hub:language")
async def settings_hub_language(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_language_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data.startswith("settings:lang:"))
async def settings_language_pick(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    rest = cb.data.removeprefix("settings:lang:")
    if rest == "back":
        await _send_settings_hub_screen(cb.message, user.telegram_id)
        await cb.answer()
        return
    allowed = {"ar", "de", "en", "es", "fr", "id", "it", "fil", "pt", "ru", "hi"}
    if rest not in allowed:
        await cb.answer("invalid", show_alert=True)
        return
    await users_repo.update_settings(user.telegram_id, {"language": rest})
    u2 = await users_repo.get_user(user.telegram_id)
    lang = u2.settings.language if u2 else rest
    cap = tr(lang, "msg.choose_language")
    kb = language_pick_menu(lang)
    try:
        await cb.message.edit_caption(caption=cap, reply_markup=kb)
    except Exception:
        try:
            await cb.message.edit_text(text=cap, reply_markup=kb, parse_mode=None)
        except Exception:
            file_id = await _media_file_id("language_banner")
            if file_id:
                await cb.message.answer_photo(
                    photo=file_id,
                    caption=cap,
                    reply_markup=kb,
                    parse_mode=None,
                )
            else:
                await cb.message.answer_photo(
                    photo=FSInputFile(str(_language_banner_path())),
                    caption=cap,
                    reply_markup=kb,
                    parse_mode=None,
                )
    await cb.answer(tr(lang, "msg.language_updated"))


@router.callback_query(F.data == "settings:hub:back")
async def settings_hub_back(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_start_sequence(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "settings:hub:reopen")
async def settings_hub_reopen(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_settings_hub_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "menu:help")
async def menu_help(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    if cb.from_user is None or not _is_admin(cb.from_user.id):
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.clear()
    await cb.message.answer(ADMIN_HELP_TEXT, parse_mode=None)
    await cb.answer()


@router.callback_query(F.data == "start:start_trading")
async def start_start_trading(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_trade_account_choice(cb.message, user.telegram_id)
    await cb.answer()

@router.message(F.text.in_(_reply_text_variants("kb.start_trading")))
async def start_start_trading_text(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await _send_trade_account_choice(message, user.telegram_id)


@router.callback_query(F.data == "trade:pick:demo")
async def trade_pick_demo(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await users_repo.update_settings(user.telegram_id, {"trade_account": "demo"})
    await users_repo.set_trading_enabled(user.telegram_id, True)
    await _send_demo_account_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "demo:lever:back")
async def demo_lever_back(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_demo_account_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data.startswith("demo:lever:"))
async def demo_lever_pick(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    if cb.data == "demo:lever:back":
        await cb.answer()
        return
    try:
        v = int(cb.data.split(":")[-1])
    except Exception:
        await cb.answer("invalid", show_alert=True)
        return
    if v not in (4, 5, 6, 7):
        await cb.answer("invalid", show_alert=True)
        return
    await users_repo.update_settings(user.telegram_id, {"martingale_max_levels": v})
    u2 = await users_repo.get_user(user.telegram_id)
    stake = float(u2.settings.stake) if u2 else 1.0
    await _start_manual_demo_trade(cb.message, user.telegram_id, stake)
    await cb.answer()


@router.callback_query(F.data == "demo:session:stop")
async def demo_session_stop(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    tid = user.telegram_id
    sess = _demo_sessions.pop(tid, None)
    if not sess:
        await cb.answer()
        return
    sess["stop"].set()
    t = sess.get("task")
    if isinstance(t, asyncio.Task):
        try:
            await asyncio.wait_for(t, timeout=5.0)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass
    lines = list(sess.get("lines") or [])
    base = float(sess.get("base_balance") or 0.0)
    stake = float(sess.get("stake") or 1.0)
    lang = str(sess.get("lang") or "en")
    msg: Message | None = sess.get("message")

    total_pnl = _session_total_pnl(lines, tid)
    end_bal = base + total_pnl
    now = datetime.now(timezone.utc)
    trade_id = uuid.uuid4().hex
    mg_open = int(user.martingale_step) if user.settings.martingale_enabled else 0
    exp = max(1, min(3600, await system_repo.get_global_trade_expiry_seconds()))
    trec = Trade(
        trade_id=trade_id,
        telegram_id=tid,
        broker="simulated",
        broker_trade_id=None,
        symbol="demo_session",
        direction="UP",
        stake=stake,
        expiry_seconds=exp,
        placed_at=now,
        expiry_at=now,
        entry_price=None,
        entry_ts=None,
        status="settled",
        pnl=total_pnl,
        win_profit_percent=0.80,
        loss_percent=1.0,
        signal_source="manual_demo",
        signal_id=f"manual_demo_session:{trade_id}",
        created_at=now,
        result={"demo_ui_session": True, "line_count": len(lines)},
        error=None,
        martingale_step_at_open=mg_open,
    )
    await trades_repo.create(trec)

    tokens_spent = 0
    header = (
        tr(lang, "caption.demo_session_result_profit")
        if total_pnl >= 0
        else tr(lang, "caption.demo_session_result_loss")
    )
    result_s = f"{total_pnl:+.2f}"
    balance_s = f"{end_bal:,.2f}"
    body = tr(
        lang,
        "caption.demo_session_result_body",
        result=result_s,
        balance=balance_s,
        tokens_spent=tokens_spent,
    )
    cap = f"{header}\n\n{body}"
    kb = _demo_session_results_keyboard(lang)
    target = msg or cb.message
    try:
        await cb.bot.edit_message_caption(
            chat_id=target.chat.id,
            message_id=target.message_id,
            caption=cap[:1020],
            reply_markup=kb,
            parse_mode=None,
        )
    except Exception:
        await cb.message.answer(cap, reply_markup=kb, parse_mode=None)
    await cb.answer()


@router.callback_query(F.data == "demo:session:again")
async def demo_session_again(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_demo_account_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "trade:pick:real")
async def trade_pick_real(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    bal_real = await _real_account_balance_usd(user.telegram_id)
    if _is_real_balance_empty(bal_real):
        await _send_real_mode_unavailable_screen(cb.message, user.telegram_id)
        await cb.answer()
        return
    await users_repo.update_settings(user.telegram_id, {"trade_account": "real"})
    await users_repo.set_trading_enabled(user.telegram_id, True)
    st = get_settings()
    lang = user.settings.language
    await cb.message.answer(
        _real_account_first_deposit_html(),
        reply_markup=real_account_deposit_keyboard(st.http_deposit_page_url(), lang),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.callback_query(F.data == "trade:pick:main")
async def trade_pick_main(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_start_sequence(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data.startswith("demo:stake:"))
async def demo_stake_pick(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    suffix = cb.data.removeprefix("demo:stake:")
    if suffix == "custom":
        await state.set_state(SettingsFlow.stake)
        await state.update_data(demo_stake_flow=True)
        await cb.message.answer(
            "Send bet amount (number).",
            reply_markup=start_reply_menu(user.settings.language),
            parse_mode=None,
        )
        await cb.answer()
        return
    try:
        stake = float(suffix)
    except ValueError:
        await cb.answer("invalid amount", show_alert=True)
        return
    if stake <= 0:
        await cb.answer("invalid amount", show_alert=True)
        return
    await users_repo.update_settings(user.telegram_id, {"stake": stake})
    await cb.message.answer(f"Bet amount set to {_fmt_money(stake)}.", parse_mode=None)
    await _send_demo_lever_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "demo:main")
async def demo_main_menu(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_start_sequence(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "demo:more_signals")
async def demo_more_signals(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_demo_account_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "demo:main_menu")
async def demo_main_menu_from_result(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_start_sequence(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "start:get_tokens")
async def start_get_tokens(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_get_tokens_screen(cb.message, user.telegram_id)
    await cb.answer()

@router.message(F.text.in_(_reply_text_variants("kb.get_tokens")))
async def start_get_tokens_text(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await _send_get_tokens_screen(message, user.telegram_id)


@router.callback_query(F.data == "tokens:main")
async def tokens_main_menu(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_start_sequence(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "start:support")
async def start_support(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    await _send_support_screen(cb.message, user.telegram_id)
    await cb.answer()

@router.message(F.text.in_(_reply_text_variants("kb.reply_support")))
async def start_support_text(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    await _send_support_screen(message, user.telegram_id)


@router.callback_query(F.data == "start:deposit")
async def start_deposit(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_get_tokens_screen(cb.message, user.telegram_id)
    await cb.answer()

@router.message(F.text.in_(_reply_text_variants("kb.reply_deposit")))
async def start_deposit_text(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await _send_get_tokens_screen(message, user.telegram_id)


@router.callback_query(F.data == "start:my_account")
async def start_my_account(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_my_account_screen(cb.message, user.telegram_id)
    await cb.answer()

@router.message(F.text.in_(_reply_text_variants("kb.reply_my_account")))
async def start_my_account_text(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await _send_my_account_screen(message, user.telegram_id)


@router.callback_query(F.data == "account:po_tip")
async def account_po_tip(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    creds = await credentials_repo.get_credentials(user.telegram_id)
    if creds:
        await cb.answer(_mask_email(creds[0]), show_alert=True)
    else:
        await cb.answer("Not connected.", show_alert=True)


@router.callback_query(F.data == "account:connect_tip")
async def account_connect_tip(cb: CallbackQuery):
    await cb.answer("Use /connect in this chat to link PocketOption.", show_alert=True)


@router.callback_query(F.data == "account:withdraw_tip")
async def account_withdraw_tip(cb: CallbackQuery):
    await cb.answer("Withdraw in PocketOption or set WITHDRAW_URL.", show_alert=True)


@router.callback_query(F.data == "account:trade_mode")
async def account_trade_mode(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    bal_real = await _real_account_balance_usd(user.telegram_id)
    if _is_real_balance_empty(bal_real):
        await _send_real_mode_unavailable_screen(cb.message, user.telegram_id)
    else:
        await _send_trade_account_choice(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "account:logout")
async def account_logout(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    creds = await credentials_repo.get_credentials(user.telegram_id)
    email = creds[0] if creds else "your account"
    text = (
        f"⚠️ Are you sure you want to logout from {email}?\n\n"
        "Trading session will be stopped. You can switch back anytime."
    )
    await cb.message.answer(text, reply_markup=logout_confirm_keyboard(), parse_mode=None)
    await cb.answer()


@router.callback_query(F.data == "account:logout:cancel")
async def account_logout_cancel(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_my_account_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "account:logout:yes")
async def account_logout_yes(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await credentials_repo.delete_credentials(user.telegram_id)
    await affiliate_repo.clear_telegram_link(user.telegram_id)
    await cb.message.answer(
        "✅ You have been logged out.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=None,
    )
    await _send_registration_screen(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "account:main")
async def account_main(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_start_sequence(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "start:my_status")
async def start_my_status(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    await _send_status_screen(cb.message, user.telegram_id)
    await cb.answer()

@router.message(F.text.in_(_reply_text_variants("kb.reply_status")))
async def start_my_status_text(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        return
    await _send_status_screen(message, user.telegram_id)


@router.callback_query(F.data == "start:faq")
async def start_faq(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    lang = user.settings.language
    await _send_faq_screen(cb.message, user.telegram_id)
    await cb.answer()

@router.message(F.text.in_(_reply_text_variants("kb.reply_faq")))
async def start_faq_text(message: Message):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    await _send_faq_screen(message, user.telegram_id)


@router.callback_query(F.data == "status:main")
async def status_main(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_start_sequence(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "support:main")
async def support_main(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_start_sequence(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "faq:main")
async def faq_main(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await _send_start_sequence(cb.message, user.telegram_id)
    await cb.answer()


@router.callback_query(F.data == "menu:back")
async def menu_back(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await cb.message.answer("menu", reply_markup=main_menu(user.settings.language, user.settings.trading_enabled))
    await cb.answer()


@router.callback_query(F.data == "trade:enable")
async def trade_enable(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await users_repo.set_trading_enabled(user.telegram_id, True)
    user = await users_repo.get_user(user.telegram_id)
    if user is None:
        await cb.answer()
        return
    await cb.message.answer("trading enabled", reply_markup=main_menu(user.settings.language, user.settings.trading_enabled))
    await cb.answer()


@router.callback_query(F.data == "trade:disable")
async def trade_disable(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await users_repo.set_trading_enabled(user.telegram_id, False)
    user = await users_repo.get_user(user.telegram_id)
    if user is None:
        await cb.answer()
        return
    await cb.message.answer("trading disabled", reply_markup=main_menu(user.settings.language, user.settings.trading_enabled))
    await cb.answer()


@router.callback_query(F.data == "set:stake")
async def set_stake_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.stake)
    await cb.message.answer("send stake amount (number)")
    await cb.answer()


@router.message(SettingsFlow.stake)
async def set_stake_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    try:
        stake = float(message.text.strip())
    except Exception:
        await message.answer("invalid number")
        return
    if stake <= 0:
        await message.answer("stake must be > 0")
        return
    await users_repo.update_settings(user.telegram_id, {"stake": stake})
    data = await state.get_data()
    from_demo = bool(data.get("demo_stake_flow"))
    await state.clear()
    user = await users_repo.get_user(user.telegram_id)
    if user is None:
        return
    if from_demo:
        await message.answer(f"Bet amount saved: {_fmt_money(stake)}.", parse_mode=None)
        await _send_demo_lever_screen(message, user.telegram_id)
    else:
        await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:expiry")
async def set_expiry_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    sec = int(user.settings.expiry_seconds)
    lang = user.settings.language
    await cb.message.answer(
        _expiration_time_caption_html(lang, sec),
        reply_markup=expiration_time_pick_menu(lang, sec),
        parse_mode=ParseMode.HTML,
    )
    await cb.answer()


@router.callback_query(F.data.startswith("settings:exp:"))
async def settings_expiry_pick(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    rest = cb.data.removeprefix("settings:exp:")
    if rest == "back":
        await _send_settings_hub_screen(cb.message, user.telegram_id)
        await cb.answer()
        return
    try:
        v = int(rest)
    except ValueError:
        await cb.answer("invalid", show_alert=True)
        return
    if v not in EXPIRY_QUICK_PICK_SECONDS:
        await cb.answer("invalid", show_alert=True)
        return
    await users_repo.update_settings(user.telegram_id, {"expiry_seconds": v})
    u3 = await users_repo.get_user(user.telegram_id)
    lang = u3.settings.language if u3 else user.settings.language
    text = _expiration_time_caption_html(lang, v)
    kb = expiration_time_pick_menu(lang, v)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    except Exception:
        await cb.message.answer(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    await cb.answer()


@router.message(SettingsFlow.expiry)
async def set_expiry_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    try:
        expiry = int(txt)
    except Exception:
        await message.answer("invalid integer")
        return
    if expiry < 1 or expiry > 3600:
        await message.answer("expiry must be between 1 and 3600")
        return
    await users_repo.update_settings(user.telegram_id, {"expiry_seconds": expiry})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:assets")
async def set_assets_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.assets)
    await cb.message.answer("send assets as comma-separated symbols (example: eurusd, btcusd)")
    await cb.answer()


@router.message(SettingsFlow.assets)
async def set_assets_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    assets = [a.strip().lower() for a in txt.split(",") if a.strip()]
    if len(assets) > 25:
        await message.answer("too many assets (max 25)")
        return
    await users_repo.update_settings(user.telegram_id, {"assets": assets})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:min_payout_percent")
async def set_min_payout_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.min_payout_percent)
    await cb.message.answer("send min payout percent (0 disables). requires payout in PO_ASSET_MAP_JSON")
    await cb.answer()


@router.message(SettingsFlow.min_payout_percent)
async def set_min_payout_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    try:
        v = float(txt)
    except Exception:
        await message.answer("invalid number")
        return
    if v < 0 or v > 100:
        await message.answer("out of range (0-100)")
        return
    await users_repo.update_settings(user.telegram_id, {"min_payout_percent": v})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:max_stake_per_trade")
async def set_max_stake_trade_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.max_stake_per_trade)
    await cb.message.answer("send max stake per trade (0 disables cap)")
    await cb.answer()


@router.message(SettingsFlow.max_stake_per_trade)
async def set_max_stake_trade_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    try:
        v = float(txt)
    except Exception:
        await message.answer("invalid number")
        return
    if v < 0 or v > 1e12:
        await message.answer("out of range")
        return
    await users_repo.update_settings(user.telegram_id, {"max_stake_per_trade": v})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:max_stake_per_day")
async def set_max_stake_day_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.max_stake_per_day)
    await cb.message.answer("send max total stake per day (0 disables). counts sum of trade stakes since utc midnight")
    await cb.answer()


@router.message(SettingsFlow.max_stake_per_day)
async def set_max_stake_day_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    try:
        v = float(txt)
    except Exception:
        await message.answer("invalid number")
        return
    if v < 0 or v > 1e12:
        await message.answer("out of range")
        return
    await users_repo.update_settings(user.telegram_id, {"max_stake_per_day": v})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:martingale_enabled")
async def toggle_martingale(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    new_val = not bool(user.settings.martingale_enabled)
    if not new_val:
        await users_repo.set_martingale_step(user.telegram_id, 0)
    await users_repo.update_settings(user.telegram_id, {"martingale_enabled": new_val})
    u2 = await users_repo.get_user(user.telegram_id)
    if u2 is not None:
        await cb.message.answer(
            f"martingale {'enabled' if u2.settings.martingale_enabled else 'disabled (step reset)'}",
            reply_markup=settings_menu(u2.settings.language),
        )
    await cb.answer()


@router.callback_query(F.data == "set:martingale_max_levels")
async def set_martingale_levels_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.martingale_levels)
    await cb.message.answer("send martingale ladder size (1-20). step 0 uses first multiplier after a win reset.")
    await cb.answer()


@router.message(SettingsFlow.martingale_levels)
async def set_martingale_levels_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    try:
        v = int(txt)
    except Exception:
        await message.answer("invalid integer")
        return
    if v < 1 or v > 20:
        await message.answer("use 1-20")
        return
    await users_repo.update_settings(user.telegram_id, {"martingale_max_levels": v})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:martingale_multipliers")
async def set_martingale_csv_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.martingale_multipliers)
    await cb.message.answer(
        "send comma-separated multipliers vs base stake (e.g. 1,2,4,8,16,32,64). "
        "first value = step 0 after win or start; each loss advances one step capped at last."
    )
    await cb.answer()


@router.message(SettingsFlow.martingale_multipliers)
async def set_martingale_csv_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    if not txt:
        await message.answer("send at least one positive number")
        return
    parts = [p.strip() for p in txt.split(",") if p.strip()]
    if not parts:
        parts = [txt]
    ok = False
    for p in parts:
        try:
            if float(p) > 0:
                ok = True
                break
        except ValueError:
            continue
    if not ok:
        await message.answer("invalid multipliers")
        return
    await users_repo.update_settings(user.telegram_id, {"martingale_multipliers_csv": txt})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:max_trades_per_day")
async def set_mtpd_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.max_trades_per_day)
    await cb.message.answer("send max trades per day (0 disables limit)")
    await cb.answer()


@router.message(SettingsFlow.max_trades_per_day)
async def set_mtpd_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    try:
        v = int(txt)
    except Exception:
        await message.answer("invalid integer")
        return
    if v < 0 or v > 100000:
        await message.answer("out of range")
        return
    await users_repo.update_settings(user.telegram_id, {"max_trades_per_day": v})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:max_loss_per_day")
async def set_mlpd_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.max_loss_per_day)
    await cb.message.answer("send max loss per day (0 disables limit)")
    await cb.answer()


@router.message(SettingsFlow.max_loss_per_day)
async def set_mlpd_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    try:
        v = float(txt)
    except Exception:
        await message.answer("invalid number")
        return
    if v < 0 or v > 1e12:
        await message.answer("out of range")
        return
    await users_repo.update_settings(user.telegram_id, {"max_loss_per_day": v})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:cooldown_seconds")
async def set_cd_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.cooldown_seconds)
    await cb.message.answer("send cooldown seconds (0 disables)")
    await cb.answer()


@router.message(SettingsFlow.cooldown_seconds)
async def set_cd_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    try:
        v = int(txt)
    except Exception:
        await message.answer("invalid integer")
        return
    if v < 0 or v > 3600:
        await message.answer("out of range")
        return
    await users_repo.update_settings(user.telegram_id, {"cooldown_seconds": v})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.callback_query(F.data == "set:max_consecutive_losses")
async def set_mcl_start(cb: CallbackQuery, state: FSMContext):
    user = await _ensure_user_from_callback(cb)
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    await state.set_state(SettingsFlow.max_consecutive_losses)
    await cb.message.answer("send max consecutive losses (0 disables)")
    await cb.answer()


@router.message(SettingsFlow.max_consecutive_losses)
async def set_mcl_value(message: Message, state: FSMContext):
    user = await _ensure_user_from_message(message)
    if user is None:
        return
    if user.blocked:
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    try:
        v = int(txt)
    except Exception:
        await message.answer("invalid integer")
        return
    if v < 0 or v > 1000:
        await message.answer("out of range")
        return
    await users_repo.update_settings(user.telegram_id, {"max_consecutive_losses": v})
    await state.clear()
    await message.answer("saved", reply_markup=settings_menu(user.settings.language))


@router.message(Command("admin_media"))
async def admin_media(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    photos: list[str] = []
    videos: list[str] = []
    set_keys: set[str] = set()
    err: str | None = None
    try:
        # Never hang here — admin UI should always respond.
        set_keys = set(await asyncio.wait_for(media_repo.list_keys(), timeout=2.0))
    except TimeoutError:
        err = "media DB timed out (showing defaults)"
    except Exception as e:
        err = f"media DB error: {type(e).__name__} (showing defaults)"

    for k, t in sorted(MEDIA_KEYS.items()):
        line = k
        if t == "video":
            videos.append(line)
        else:
            photos.append(line)

    lines: list[str] = []
    if err:
        lines.append(f"⚠️ {err}")
        lines.append("")
    lines.append("🖼️ Photos:")
    lines.extend([f"- {x}" for x in photos] if photos else ["- (none)"])
    lines.append("")
    lines.append("🎞️ Videos:")
    lines.extend([f"- {x}" for x in videos] if videos else ["- (none)"])
    lines.append("")
    lines.append("Use:")
    lines.append("- /admin_media_set key (then send photo/video)")
    lines.append("- /admin_media_clear key")
    await message.answer("\n".join(lines), parse_mode=None)


@router.message(Command("admin_media_set"))
async def admin_media_set(message: Message, state: FSMContext):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("usage: /admin_media_set key", parse_mode=None)
        return
    key = parts[1].strip()
    if key not in MEDIA_KEYS:
        await message.answer("unknown key. use /admin_media to list.", parse_mode=None)
        return
    await state.clear()
    await state.set_state(AdminMediaFlow.waiting_media)
    await state.update_data(media_key=key)
    await message.answer(f"send {MEDIA_KEYS[key]} for {key}", parse_mode=None)


@router.message(Command("admin_media_clear"))
async def admin_media_clear(message: Message, state: FSMContext):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("usage: /admin_media_clear key", parse_mode=None)
        return
    key = parts[1].strip()
    if key not in MEDIA_KEYS:
        await message.answer("unknown key. use /admin_media to list.", parse_mode=None)
        return
    await state.clear()
    ok = await media_repo.clear_media(key)
    await message.answer("cleared" if ok else "not set", parse_mode=None)


@router.message(AdminMediaFlow.waiting_media)
async def admin_media_waiting_media(message: Message, state: FSMContext):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        await state.clear()
        return
    data = await state.get_data()
    key = str(data.get("media_key") or "").strip()
    if not key or key not in MEDIA_KEYS:
        await message.answer("missing key. run /admin_media_set key again.", parse_mode=None)
        await state.clear()
        return
    expected = MEDIA_KEYS[key]

    file_id: str | None = None
    type_: str | None = None
    if message.photo:
        file_id = message.photo[-1].file_id
        type_ = "photo"
    elif message.video:
        file_id = message.video.file_id
        type_ = "video"
    elif message.document and message.document.mime_type:
        mt = message.document.mime_type.lower()
        if mt.startswith("video/"):
            file_id = message.document.file_id
            type_ = "video"
        elif mt.startswith("image/"):
            file_id = message.document.file_id
            type_ = "photo"

    if not file_id or not type_:
        await message.answer("send a photo or video", parse_mode=None)
        return
    if type_ != expected:
        await message.answer(f"expected {expected}, got {type_}", parse_mode=None)
        return

    await media_repo.set_media(key=key, type_=expected, file_id=file_id, updated_by=message.from_user.id)
    await state.clear()
    await message.answer(f"saved {key}", parse_mode=None)


_BCAST_ATTRS: frozenset[str] = frozenset(
    ("global", "signed_in", "not_signed_in", "signed_in_low_balance_20")
)


def _bcast_kb_content_type() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Text only", callback_data="bcast:ct:text")],
            [InlineKeyboardButton(text="🖼️/🎞️ Media + text", callback_data="bcast:ct:media")],
            [InlineKeyboardButton(text="✖ Cancel", callback_data="bcast:cancel")],
        ]
    )


def _bcast_kb_button_type() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="No button", callback_data="bcast:bt:none")],
            [InlineKeyboardButton(text="🔗 Link button", callback_data="bcast:bt:link")],
            [InlineKeyboardButton(text="🤖 Bot function button", callback_data="bcast:bt:action")],
            [InlineKeyboardButton(text="✖ Cancel", callback_data="bcast:cancel")],
        ]
    )


def _bcast_kb_action_pick() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Start Trading", callback_data="bcast:act:start_trading")],
            [InlineKeyboardButton(text="🏠 /start (Main)", callback_data="bcast:act:start")],
            [InlineKeyboardButton(text="✖ Cancel", callback_data="bcast:cancel")],
        ]
    )


def _bcast_kb_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Send now", callback_data="bcast:confirm")],
            [InlineKeyboardButton(text="✖ Cancel", callback_data="bcast:cancel")],
        ]
    )


def _bcast_build_button(button: dict[str, str] | None) -> InlineKeyboardMarkup | None:
    if not button:
        return None
    label = (button.get("label") or "").strip()
    kind = (button.get("kind") or "").strip()
    target = (button.get("target") or "").strip()
    if not label or not kind or not target:
        return None
    if kind == "link":
        if not (target.startswith("http://") or target.startswith("https://")):
            return None
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=label, url=target)]]
        )
    if kind == "action":
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=target)]]
        )
    return None


def _parse_usd_amount(text: str) -> float | None:
    t = (text or "").replace(",", " ")
    m = re.search(r"([-+]?\d+(?:\.\d+)?)", t)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


async def _bcast_credential_ids() -> set[int]:
    cur = mongo.db.credentials.find({}, projection={"_id": 0, "telegram_id": 1})
    docs = await cur.to_list(length=None)
    out: set[int] = set()
    for d in docs:
        try:
            out.add(int(d.get("telegram_id")))
        except Exception:
            continue
    return out


async def _bcast_pick_recipients(attr: str) -> list[int]:
    all_ids = set(await users_repo.list_telegram_ids(include_blocked=False))
    cred_ids = await _bcast_credential_ids()
    if attr == "global":
        return sorted(all_ids)
    if attr == "signed_in":
        return sorted(all_ids.intersection(cred_ids))
    if attr == "not_signed_in":
        return sorted(all_ids.difference(cred_ids))
    if attr == "signed_in_low_balance_20":
        # Step 3: use DB-cached balances (no live PO calls during broadcast).
        cur = mongo.db.users.find(
            {
                "blocked": False,
                "po_real_balance_usd": {"$ne": None, "$lt": 20.0},
            },
            projection={"_id": 0, "telegram_id": 1},
        )
        docs = await cur.to_list(length=None)
        low_ids: set[int] = set()
        for d in docs:
            try:
                low_ids.add(int(d.get("telegram_id")))
            except Exception:
                continue
        return sorted(low_ids.intersection(all_ids).intersection(cred_ids))
    return []


@router.message(Command("broadcast"))
async def admin_broadcast_start(message: Message, state: FSMContext):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer(
            "usage: /broadcast attribute\n\n"
            "attributes:\n"
            "- global\n"
            "- signed_in\n"
            "- not_signed_in\n"
            "- signed_in_low_balance_20",
            parse_mode=None,
        )
        return
    attr = parts[1].strip()
    if attr not in _BCAST_ATTRS:
        await message.answer(
            "unknown attribute.\n\n"
            "use one of:\n"
            "- global\n"
            "- signed_in\n"
            "- not_signed_in\n"
            "- signed_in_low_balance_20",
            parse_mode=None,
        )
        return
    await state.clear()
    await state.update_data(bcast_attr=attr)
    await state.set_state(BroadcastFlow.content_type)
    await message.answer(f"Broadcast audience: {attr}\n\nChoose content type:", reply_markup=_bcast_kb_content_type())


@router.callback_query(F.data == "bcast:cancel")
async def admin_broadcast_cancel(cb: CallbackQuery, state: FSMContext):
    if cb.from_user is None or not _is_admin(cb.from_user.id):
        await cb.answer()
        return
    await state.clear()
    if cb.message:
        await cb.message.answer("cancelled", parse_mode=None)
    await cb.answer()


@router.callback_query(BroadcastFlow.content_type, F.data.startswith("bcast:ct:"))
async def admin_broadcast_pick_content_type(cb: CallbackQuery, state: FSMContext):
    if cb.from_user is None or not _is_admin(cb.from_user.id):
        await cb.answer()
        return
    kind = (cb.data or "").removeprefix("bcast:ct:").strip()
    await state.update_data(bcast_content_kind=kind)
    if kind == "text":
        await state.set_state(BroadcastFlow.text)
        await cb.message.answer("Send the broadcast text now.", parse_mode=None)  # type: ignore[union-attr]
        await cb.answer()
        return
    if kind == "media":
        await state.set_state(BroadcastFlow.media)
        await cb.message.answer("Send a photo or video (with optional caption).", parse_mode=None)  # type: ignore[union-attr]
        await cb.answer()
        return
    await cb.answer("invalid", show_alert=True)


@router.message(BroadcastFlow.text)
async def admin_broadcast_receive_text(message: Message, state: FSMContext):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        await state.clear()
        return
    txt = (message.text or "").strip()
    if not txt:
        await message.answer("empty text. send again.", parse_mode=None)
        return
    await state.update_data(bcast_text=txt, bcast_media=None)
    await state.set_state(BroadcastFlow.button_type)
    await message.answer("Choose button type:", reply_markup=_bcast_kb_button_type())


@router.message(BroadcastFlow.media)
async def admin_broadcast_receive_media(message: Message, state: FSMContext):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        await state.clear()
        return
    media_type: str | None = None
    file_id: str | None = None
    if message.photo:
        media_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        media_type = "video"
        file_id = message.video.file_id
    elif message.document and message.document.mime_type:
        mt = message.document.mime_type.lower()
        if mt.startswith("image/"):
            media_type = "photo"
            file_id = message.document.file_id
        elif mt.startswith("video/"):
            media_type = "video"
            file_id = message.document.file_id
    if not media_type or not file_id:
        await message.answer("Send a photo or video.", parse_mode=None)
        return
    cap = (message.caption or "").strip()
    await state.update_data(
        bcast_text=cap,
        bcast_media={"type": media_type, "file_id": file_id},
    )
    await state.set_state(BroadcastFlow.button_type)
    await message.answer("Choose button type:", reply_markup=_bcast_kb_button_type())


@router.callback_query(BroadcastFlow.button_type, F.data.startswith("bcast:bt:"))
async def admin_broadcast_pick_button_type(cb: CallbackQuery, state: FSMContext):
    if cb.from_user is None or not _is_admin(cb.from_user.id):
        await cb.answer()
        return
    bt = (cb.data or "").removeprefix("bcast:bt:").strip()
    if bt == "none":
        await state.update_data(bcast_button=None)
        await state.set_state(BroadcastFlow.confirm)
        await _bcast_send_preview(cb.message, state)  # type: ignore[arg-type]
        await cb.answer()
        return
    if bt == "link":
        await state.update_data(bcast_button={"kind": "link", "label": "", "target": ""})
        await state.set_state(BroadcastFlow.button_label)
        await cb.message.answer("Send button label (text).", parse_mode=None)  # type: ignore[union-attr]
        await cb.answer()
        return
    if bt == "action":
        await state.update_data(bcast_button={"kind": "action", "label": "Start", "target": "bcast:act:start"})
        await state.set_state(BroadcastFlow.button_action)
        await cb.message.answer("Pick bot function button:", reply_markup=_bcast_kb_action_pick(), parse_mode=None)  # type: ignore[union-attr]
        await cb.answer()
        return
    await cb.answer("invalid", show_alert=True)


@router.message(BroadcastFlow.button_label)
async def admin_broadcast_button_label(message: Message, state: FSMContext):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        await state.clear()
        return
    label = (message.text or "").strip()
    if not label:
        await message.answer("empty label. send again.", parse_mode=None)
        return
    data = await state.get_data()
    btn = dict(data.get("bcast_button") or {})
    btn["label"] = label
    await state.update_data(bcast_button=btn)
    await state.set_state(BroadcastFlow.button_link)
    await message.answer("Send URL starting with http:// or https://", parse_mode=None)


@router.message(BroadcastFlow.button_link)
async def admin_broadcast_button_link(message: Message, state: FSMContext):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        await state.clear()
        return
    url = (message.text or "").strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.answer("invalid url. send again.", parse_mode=None)
        return
    data = await state.get_data()
    btn = dict(data.get("bcast_button") or {})
    btn["target"] = url
    await state.update_data(bcast_button=btn)
    await state.set_state(BroadcastFlow.confirm)
    await _bcast_send_preview(message, state)


@router.callback_query(BroadcastFlow.button_action, F.data.startswith("bcast:act:"))
async def admin_broadcast_button_action_pick(cb: CallbackQuery, state: FSMContext):
    if cb.from_user is None or not _is_admin(cb.from_user.id):
        await cb.answer()
        return
    action = (cb.data or "").removeprefix("bcast:act:").strip()
    if action == "start_trading":
        btn = {"kind": "action", "label": "🚀 Start Trading", "target": "bcast:user:start_trading"}
    elif action == "start":
        btn = {"kind": "action", "label": "🏠 Start", "target": "bcast:user:start"}
    else:
        await cb.answer("invalid", show_alert=True)
        return
    await state.update_data(bcast_button=btn)
    await state.set_state(BroadcastFlow.confirm)
    await _bcast_send_preview(cb.message, state)  # type: ignore[arg-type]
    await cb.answer()


async def _bcast_send_preview(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    attr = str(data.get("bcast_attr") or "")
    txt = str(data.get("bcast_text") or "")
    media = data.get("bcast_media")
    btn = data.get("bcast_button")
    kb = _bcast_build_button(btn if isinstance(btn, dict) else None)
    header = f"Preview (audience={attr})"
    await message.answer(header, parse_mode=None)
    if isinstance(media, dict) and media.get("type") == "photo":
        await message.answer_photo(
            photo=str(media.get("file_id")),
            caption=txt or None,
            reply_markup=kb,
            parse_mode=None,
        )
    elif isinstance(media, dict) and media.get("type") == "video":
        await message.answer_video(
            video=str(media.get("file_id")),
            caption=txt or None,
            reply_markup=kb,
            parse_mode=None,
        )
    else:
        await message.answer(txt or "(no text)", reply_markup=kb, parse_mode=None)
    await message.answer("Confirm send?", reply_markup=_bcast_kb_confirm(), parse_mode=None)


@router.callback_query(BroadcastFlow.confirm, F.data == "bcast:confirm")
async def admin_broadcast_confirm(cb: CallbackQuery, state: FSMContext):
    if cb.from_user is None or not _is_admin(cb.from_user.id):
        await cb.answer()
        return
    data = await state.get_data()
    attr = str(data.get("bcast_attr") or "")
    txt = str(data.get("bcast_text") or "")
    media = data.get("bcast_media")
    btn = data.get("bcast_button")
    kb = _bcast_build_button(btn if isinstance(btn, dict) else None)

    await cb.answer("sending…")
    recipients = await _bcast_pick_recipients(attr)
    ok = 0
    fail = 0
    for i, tid in enumerate(recipients):
        try:
            if isinstance(media, dict) and media.get("type") == "photo":
                await cb.bot.send_photo(
                    chat_id=tid,
                    photo=str(media.get("file_id")),
                    caption=txt or None,
                    reply_markup=kb,
                    parse_mode=None,
                )
            elif isinstance(media, dict) and media.get("type") == "video":
                await cb.bot.send_video(
                    chat_id=tid,
                    video=str(media.get("file_id")),
                    caption=txt or None,
                    reply_markup=kb,
                    parse_mode=None,
                )
            else:
                await cb.bot.send_message(
                    chat_id=tid,
                    text=txt or "",
                    reply_markup=kb,
                    parse_mode=None,
                    disable_web_page_preview=True,
                )
            ok += 1
        except Exception:
            fail += 1
        if i and i % 25 == 0:
            await asyncio.sleep(0.2)
    await state.clear()
    if cb.message:
        await cb.message.answer(
            f"Broadcast done.\n\nAudience: {attr}\nRecipients: {len(recipients)}\nSent: {ok}\nFailed: {fail}",
            parse_mode=None,
        )


@router.callback_query(F.data.startswith("bcast:user:"))
async def broadcast_user_action(cb: CallbackQuery):
    user = await _ensure_user_from_callback(cb)
    if user is None:
        await cb.answer()
        return
    if user.blocked:
        await cb.message.answer("access denied")
        await cb.answer()
        return
    action = (cb.data or "").removeprefix("bcast:user:").strip()
    if action == "start_trading":
        await _send_trade_account_choice(cb.message, user.telegram_id)
    elif action == "start":
        await _send_start_sequence(cb.message, user.telegram_id)
    else:
        await cb.answer("invalid", show_alert=True)
        return
    await cb.answer()


_SIGNAL_MODES_TXT = "all, admin_only, webhook_only, strategy_only"


@router.message(Command("admin_expiry"))
async def admin_expiry_cmd(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    parts = (message.text or "").split()
    if len(parts) == 1:
        cur = await system_repo.get_global_trade_expiry_seconds()
        await message.answer(
            f"global trade expiry: {cur}s (allowed: 5, 10, 15, 30)",
            parse_mode=None,
        )
        return
    if len(parts) != 2:
        await message.answer("usage: /admin_expiry 5|10|15|30", parse_mode=None)
        return
    try:
        v = int(parts[1])
    except Exception:
        await message.answer("invalid", parse_mode=None)
        return
    if v not in (5, 10, 15, 30):
        await message.answer("invalid", parse_mode=None)
        return
    try:
        await system_repo.set_global_trade_expiry_seconds(v)
    except ValueError:
        await message.answer("invalid", parse_mode=None)
        return
    await message.answer(f"global trade expiry set to {v}s", parse_mode=None)


@router.message(Command("signal_mode"))
async def admin_signal_mode_cmd(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 1:
        m = await system_repo.get_signal_ingest_mode()
        await message.answer(f"signal_ingest_mode={m}", parse_mode=None)
        return
    raw = parts[1].strip().lower()
    valid = {"all", "admin_only", "webhook_only", "strategy_only"}
    if raw not in valid:
        await message.answer(f"invalid mode. use: {_SIGNAL_MODES_TXT}", parse_mode=None)
        return
    await system_repo.set_signal_ingest_mode(raw)
    await message.answer(f"signal_ingest_mode={raw}", parse_mode=None)


@router.message(Command("admin_signal"))
async def admin_signal_cmd(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("usage: /admin_signal <symbol> <UP|DOWN>", parse_mode=None)
        return
    sym = parts[1].strip().lower()
    dire_raw = parts[2].strip().upper()
    if dire_raw not in ("UP", "DOWN"):
        await message.answer("direction must be UP or DOWN", parse_mode=None)
        return
    if not await system_repo.get_global_trading_enabled():
        await message.answer("global trading is off; enable with /global_on", parse_mode=None)
        return
    sig_id = f"admin:tg:{message.from_user.id}:{uuid.uuid4().hex}"
    sig = WebhookSignalIn(
        source="admin",
        signal_id=sig_id,
        symbol=sym,
        direction=dire_raw,
        payload={},
    )
    created, stored = await signals_repo.store(sig)
    if not created:
        await message.answer("duplicate signal (id collision); retry", parse_mode=None)
        return
    result = await trade_engine.on_signal(stored)
    elig = result.get("eligible", 0)
    await message.answer(f"ok signal_id={sig_id} eligible={elig}", parse_mode=None)


@router.message(Command("global_on"))
async def global_on(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    await system_repo.set_global_trading_enabled(True)
    await message.answer("global trading enabled")


@router.message(Command("global_off"))
async def global_off(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    await system_repo.set_global_trading_enabled(False)
    await message.answer("global trading disabled")


@router.message(Command("admin_users"))
async def admin_users(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    users = await users_repo.list_users(limit=50)
    if not users:
        await message.answer("no users")
        return
    lines: list[str] = []
    lines.append("👥 Users (latest 50):")
    lines.append("")
    for u in users:
        b = "🚫" if u.blocked else "✅"
        t = "🟢" if u.settings.trading_enabled else "⚪"
        uname = f"@{u.username}" if u.username else "(@no_username)"
        lines.append(f"{b} {t} {u.telegram_id} {uname}")
    lines.append("")
    lines.append("Legend: 🚫 blocked | ✅ active, 🟢 trading on | ⚪ trading off")
    await message.answer("\n".join(lines), parse_mode=None)


@router.message(Command("admin_block"))
async def admin_block(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("usage: /admin_block <telegram_id>")
        return
    try:
        tid = int(parts[1])
    except Exception:
        await message.answer("invalid telegram_id")
        return
    ok = await users_repo.set_blocked(tid, True)
    await message.answer("blocked" if ok else "user not found")


@router.message(Command("admin_unblock"))
async def admin_unblock(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("usage: /admin_unblock <telegram_id>")
        return
    try:
        tid = int(parts[1])
    except Exception:
        await message.answer("invalid telegram_id")
        return
    ok = await users_repo.set_blocked(tid, False)
    await message.answer("unblocked" if ok else "user not found")


@router.message(Command("admin_tokens"))
async def admin_tokens(message: Message):
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("access denied")
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("usage: /admin_tokens <telegram_id> <delta>")
        return
    try:
        tid = int(parts[1])
        delta = int(parts[2])
    except Exception:
        await message.answer("invalid telegram_id or delta")
        return
    await tokens_repo.add_tokens(tid, delta, "admin_telegram", {})
    bal = await tokens_repo.get_balance(tid)
    await message.answer(f"ok balance={bal}")

