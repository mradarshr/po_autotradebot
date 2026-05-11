from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.config import get_settings
from app.i18n import tr


def _support_inline_button(lang: str) -> InlineKeyboardButton:
    u = (get_settings().support_telegram_username or "").strip().lstrip("@")
    if u:
        return InlineKeyboardButton(text=tr(lang, "kb.support"), url=f"https://t.me/{u}")
    return InlineKeyboardButton(text=tr(lang, "kb.support"), callback_data="start:support")


def support_open_chat_keyboard(lang: str) -> InlineKeyboardMarkup | None:
    """Inline row to open a private chat with the configured support username."""
    u = (get_settings().support_telegram_username or "").strip().lstrip("@")
    if not u:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(lang, "kb.support_dm", u=u), url=f"https://t.me/{u}")],
        ]
    )


def support_screen_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Support screen actions: open chat + Main Menu (client-style).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_support_inline_button(lang)],
            [InlineKeyboardButton(text=tr(lang, "kb.main_menu"), callback_data="support:main")],
        ]
    )


def faq_screen_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    FAQ screen actions: Support + Main Menu (client-style).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_support_inline_button(lang)],
            [InlineKeyboardButton(text=tr(lang, "kb.main_menu"), callback_data="faq:main")],
        ]
    )


def logout_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Yes, Logout", callback_data="account:logout:yes")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="account:logout:cancel")],
        ]
    )


def start_menu(lang: str) -> InlineKeyboardMarkup:
    """
    Client-clone `/start` menu: only the three inline rows under the banner
    (Deposit / Account / Status / FAQ live on the reply keyboard).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(lang, "kb.start_trading"), callback_data="start:start_trading")],
            [InlineKeyboardButton(text=tr(lang, "kb.get_tokens"), callback_data="start:get_tokens")],
            [_support_inline_button(lang)],
        ]
    )


def demo_account_bet_menu(lang: str) -> InlineKeyboardMarkup:
    """Bet grid after Demo account is selected (matches client reference)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=tr(lang, "kb.demo_1"), callback_data="demo:stake:1"),
                InlineKeyboardButton(text=tr(lang, "kb.demo_1_5"), callback_data="demo:stake:1.5"),
                InlineKeyboardButton(text=tr(lang, "kb.demo_2"), callback_data="demo:stake:2"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.demo_2_5"), callback_data="demo:stake:2.5"),
                InlineKeyboardButton(text=tr(lang, "kb.demo_5"), callback_data="demo:stake:5"),
            ],
            [InlineKeyboardButton(text=tr(lang, "kb.demo_custom"), callback_data="demo:stake:custom")],
            [InlineKeyboardButton(text=tr(lang, "kb.main_menu"), callback_data="demo:main")],
        ]
    )


def demo_lever_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="4", callback_data="demo:lever:4"),
                InlineKeyboardButton(text="5", callback_data="demo:lever:5"),
                InlineKeyboardButton(text="6", callback_data="demo:lever:6"),
            ],
            [InlineKeyboardButton(text=tr(lang, "kb.demo_lever_7_rec"), callback_data="demo:lever:7")],
            [InlineKeyboardButton(text=tr(lang, "kb.back"), callback_data="demo:lever:back")],
        ]
    )


def deposit_link_keyboard(deposit_url: str, lang: str) -> InlineKeyboardMarkup | None:
    """
    Opens deposit in the browser. Telegram shows the native “Open this link?” sheet
    for url buttons (Cancel / Open) — cannot be customized from the Bot API.
    """
    url = (deposit_url or "").strip()
    if url.startswith("http://") or url.startswith("https://"):
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=tr(lang, "kb.deposit"), url=url)]]
        )
    return None


def real_account_deposit_keyboard(deposit_url: str, lang: str) -> InlineKeyboardMarkup:
    """Single 💰 Deposit row — URL (native open-link sheet) or callback fallback."""
    kb = deposit_link_keyboard(deposit_url, lang)
    if kb is not None:
        return kb
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=tr(lang, "kb.deposit"), callback_data="start:deposit")]]
    )


def demo_real_gate_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Shown when real balance is empty — deposit, home, support (t.me)."""
    s = get_settings()
    du = s.http_deposit_page_url()
    sup = (s.support_telegram_username or "").strip().lstrip("@")
    rows: list[list[InlineKeyboardButton]] = []
    if du:
        rows.append([InlineKeyboardButton(text=tr(lang, "kb.deposit"), url=du)])
    else:
        rows.append([InlineKeyboardButton(text=tr(lang, "kb.deposit"), callback_data="start:deposit")])
    rows.append([InlineKeyboardButton(text=tr(lang, "kb.main_menu"), callback_data="account:main")])
    if sup:
        rows.append([InlineKeyboardButton(text=tr(lang, "kb.support_caps"), url=f"https://t.me/{sup}")])
    else:
        rows.append([InlineKeyboardButton(text=tr(lang, "kb.support_caps"), callback_data="start:support")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def my_account_menu(
    *,
    po_connected: bool,
    po_button_text: str,
    deposit_page_url: str,
    withdraw_page_url: str,
    lang: str,
) -> InlineKeyboardMarkup:
    """My Account dashboard inline actions (client-style)."""
    po_cb = "account:po_tip" if po_connected else "account:connect_tip"
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=po_button_text[:64], callback_data=po_cb)],
    ]
    du = (deposit_page_url or "").strip()
    if du.startswith("http://") or du.startswith("https://"):
        rows.append([InlineKeyboardButton(text=tr(lang, "kb.deposit"), url=du)])
    else:
        rows.append([InlineKeyboardButton(text=tr(lang, "kb.deposit"), callback_data="start:deposit")])
    wu = (withdraw_page_url or "").strip()
    if wu.startswith("http://") or wu.startswith("https://"):
        withdraw_btn = InlineKeyboardButton(text=tr(lang, "kb.withdraw"), url=wu)
    else:
        withdraw_btn = InlineKeyboardButton(text=tr(lang, "kb.withdraw"), callback_data="account:withdraw_tip")
    rows.append(
        [
            withdraw_btn,
            InlineKeyboardButton(text=tr(lang, "kb.settings"), callback_data="menu:settings"),
        ]
    )
    rows.append([InlineKeyboardButton(text=tr(lang, "kb.demo_real"), callback_data="account:trade_mode")])
    rows.append([InlineKeyboardButton(text=tr(lang, "kb.logout"), callback_data="account:logout")])
    rows.append([InlineKeyboardButton(text=tr(lang, "kb.account_main"), callback_data="account:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def status_screen_keyboard(deposit_url: str, lang: str) -> InlineKeyboardMarkup:
    """
    Status screen actions: Deposit + Main Menu (client-style).
    """
    url = (deposit_url or "").strip()
    if url.startswith("http://") or url.startswith("https://"):
        dep_btn = InlineKeyboardButton(text=tr(lang, "kb.deposit"), url=url)
    else:
        dep_btn = InlineKeyboardButton(text=tr(lang, "kb.deposit"), callback_data="start:deposit")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [dep_btn],
            [InlineKeyboardButton(text=tr(lang, "kb.main_menu"), callback_data="status:main")],
        ]
    )


def get_tokens_screen_keyboard(deposit_url: str, lang: str) -> InlineKeyboardMarkup:
    """
    Get Tokens screen: open deposit + main menu.
    Pass an https URL so the button uses url= (Telegram shows “Open this link?” then browser).
    """
    url = (deposit_url or "").strip()
    if url.startswith("http://") or url.startswith("https://"):
        open_row = [InlineKeyboardButton(text=tr(lang, "kb.open_deposit_page"), url=url)]
    else:
        open_row = [
            InlineKeyboardButton(text=tr(lang, "kb.open_deposit_page"), callback_data="start:deposit")
        ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            open_row,
            [InlineKeyboardButton(text=tr(lang, "kb.main_menu"), callback_data="tokens:main")],
        ]
    )


def trade_account_choice_menu(lang: str) -> InlineKeyboardMarkup:
    """
    After "Start trading" — tutorial graphic + demo / real / main menu (client style).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(lang, "kb.trade_demo"), callback_data="trade:pick:demo")],
            [InlineKeyboardButton(text=tr(lang, "kb.trade_real"), callback_data="trade:pick:real")],
            [InlineKeyboardButton(text=tr(lang, "kb.main_menu"), callback_data="trade:pick:main")],
        ]
    )


def start_reply_menu(lang: str) -> ReplyKeyboardMarkup:
    """
    Bottom persistent menu (matches client reference style).
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=tr(lang, "kb.start_trading"))],
            [KeyboardButton(text=tr(lang, "kb.reply_deposit")), KeyboardButton(text=tr(lang, "kb.reply_my_account"))],
            [KeyboardButton(text=tr(lang, "kb.reply_status")), KeyboardButton(text=tr(lang, "kb.reply_support"))],
            [KeyboardButton(text=tr(lang, "kb.reply_faq"))],
        ],
        resize_keyboard=True,
    )


def main_menu(lang: str, trading_enabled: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=tr(lang, "kb.main_settings"), callback_data="menu:settings"),
                InlineKeyboardButton(text=tr(lang, "kb.main_status"), callback_data="menu:status"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.main_help"), callback_data="menu:help"),
            ],
            [
                InlineKeyboardButton(
                    text=(
                        tr(lang, "kb.main_disable_trading")
                        if trading_enabled
                        else tr(lang, "kb.main_enable_trading")
                    ),
                    callback_data=("trade:disable" if trading_enabled else "trade:enable"),
                )
            ],
        ]
    )


def autotrade_strategy_menu(lang: str) -> InlineKeyboardMarkup:
    """Named autotrade presets + manual + back to settings hub."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(lang, "kb.auto_precision"), callback_data="auto:strat:precision")],
            [InlineKeyboardButton(text=tr(lang, "kb.auto_high"), callback_data="auto:strat:high_profit")],
            [InlineKeyboardButton(text=tr(lang, "kb.auto_balanced"), callback_data="auto:strat:balanced")],
            [InlineKeyboardButton(text=tr(lang, "kb.auto_conservative"), callback_data="auto:strat:conservative")],
            [InlineKeyboardButton(text=tr(lang, "kb.auto_manual"), callback_data="auto:strat:manual")],
            [InlineKeyboardButton(text=tr(lang, "kb.back"), callback_data="settings:hub:reopen")],
        ]
    )


def max_steps_quick_pick_menu(lang: str) -> InlineKeyboardMarkup:
    """Max martingale steps: preset row + back to manual compact."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="5", callback_data="auto:manual:mgval:5"),
                InlineKeyboardButton(text="7", callback_data="auto:manual:mgval:7"),
                InlineKeyboardButton(text="9", callback_data="auto:manual:mgval:9"),
                InlineKeyboardButton(text="10", callback_data="auto:manual:mgval:10"),
            ],
            [InlineKeyboardButton(text=tr(lang, "kb.back"), callback_data="auto:manual:mg_cancel")],
        ]
    )


def max_cycles_quick_pick_menu(lang: str) -> InlineKeyboardMarkup:
    """Max cycles (trades/session): preset row + back to manual compact."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="5", callback_data="auto:manual:cyval:5"),
                InlineKeyboardButton(text="10", callback_data="auto:manual:cyval:10"),
                InlineKeyboardButton(text="15", callback_data="auto:manual:cyval:15"),
            ],
            [InlineKeyboardButton(text=tr(lang, "kb.back"), callback_data="auto:manual:cy_cancel")],
        ]
    )


EXPIRY_QUICK_PICK_SECONDS: tuple[int, ...] = (5, 10, 15, 30)


def expiration_time_pick_menu(lang: str, current_seconds: int) -> InlineKeyboardMarkup:
    """Expiry picker: checkmark on current value if it matches a preset; row + back to settings hub."""
    row: list[InlineKeyboardButton] = []
    for sec in EXPIRY_QUICK_PICK_SECONDS:
        mark = "✅ " if current_seconds == sec else ""
        label = f"{mark}{tr(lang, 'kb.expiry_sec', n=sec)}"
        row.append(InlineKeyboardButton(text=label, callback_data=f"settings:exp:{sec}"))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            row,
            [InlineKeyboardButton(text=tr(lang, "kb.back"), callback_data="settings:exp:back")],
        ]
    )


def manual_settings_compact_menu(lang: str) -> InlineKeyboardMarkup:
    """Client-style manual slice: steps (martingale depth) & cycles (max trades/day)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tr(lang, "kb.manual_max_steps"), callback_data="auto:manual:mg_pick")],
            [InlineKeyboardButton(text=tr(lang, "kb.manual_max_cycles"), callback_data="auto:manual:cy_pick")],
            [InlineKeyboardButton(text=tr(lang, "kb.back"), callback_data="auto:manual:back")],
        ]
    )


def language_pick_menu(lang: str) -> InlineKeyboardMarkup:
    """Language grid (client-style) + back to settings hub."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=tr(lang, "lang.ar"), callback_data="settings:lang:ar"),
                InlineKeyboardButton(text=tr(lang, "lang.de"), callback_data="settings:lang:de"),
                InlineKeyboardButton(text=tr(lang, "lang.en"), callback_data="settings:lang:en"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "lang.es"), callback_data="settings:lang:es"),
                InlineKeyboardButton(text=tr(lang, "lang.fr"), callback_data="settings:lang:fr"),
                InlineKeyboardButton(text=tr(lang, "lang.id"), callback_data="settings:lang:id"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "lang.it"), callback_data="settings:lang:it"),
                InlineKeyboardButton(text=tr(lang, "lang.fil"), callback_data="settings:lang:fil"),
                InlineKeyboardButton(text=tr(lang, "lang.pt"), callback_data="settings:lang:pt"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "lang.ru"), callback_data="settings:lang:ru"),
                InlineKeyboardButton(text=tr(lang, "lang.hi"), callback_data="settings:lang:hi"),
            ],
            [InlineKeyboardButton(text=tr(lang, "kb.back"), callback_data="settings:lang:back")],
        ]
    )


def settings_hub_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=tr(lang, "kb.hub_autotrade"),
                    callback_data="settings:hub:autotrade",
                )
            ],
            [
                InlineKeyboardButton(
                    text=tr(lang, "kb.hub_expiry"),
                    callback_data="set:expiry",
                )
            ],
            [
                InlineKeyboardButton(
                    text=tr(lang, "kb.hub_language"),
                    callback_data="settings:hub:language",
                )
            ],
            [
                InlineKeyboardButton(
                    text=tr(lang, "kb.back"),
                    callback_data="settings:hub:back",
                )
            ],
        ]
    )


def settings_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=tr(lang, "kb.legacy_stake"), callback_data="set:stake"),
                InlineKeyboardButton(text=tr(lang, "kb.legacy_expiry"), callback_data="set:expiry"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.legacy_mg_on"), callback_data="set:martingale_enabled"),
                InlineKeyboardButton(text=tr(lang, "kb.legacy_mg_levels"), callback_data="set:martingale_max_levels"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.legacy_mg_csv"), callback_data="set:martingale_multipliers"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.legacy_assets"), callback_data="set:assets"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.legacy_min_payout"), callback_data="set:min_payout_percent"),
                InlineKeyboardButton(text=tr(lang, "kb.legacy_max_stake_trade"), callback_data="set:max_stake_per_trade"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.legacy_max_stake_day"), callback_data="set:max_stake_per_day"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.legacy_max_trades"), callback_data="set:max_trades_per_day"),
                InlineKeyboardButton(text=tr(lang, "kb.legacy_max_loss"), callback_data="set:max_loss_per_day"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.legacy_cooldown"), callback_data="set:cooldown_seconds"),
                InlineKeyboardButton(text=tr(lang, "kb.legacy_loss_streak"), callback_data="set:max_consecutive_losses"),
            ],
            [
                InlineKeyboardButton(text=tr(lang, "kb.legacy_back"), callback_data="settings:hub:reopen"),
            ],
        ]
    )
