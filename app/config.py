from __future__ import annotations

from functools import lru_cache
from urllib.parse import urlsplit, urlunsplit

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_VALID_GLOBAL_EXPIRY = frozenset({5, 10, 15, 30})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = ""
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "trading_bot"
    admin_telegram_ids: str = ""
    webhook_secret: str = ""
    webhook_hmac_secret: str = ""
    webhook_rate_limit_per_minute: int = 120
    webhook_trust_x_forwarded_for: bool = False
    global_min_payout_percent: float = 0.0
    trade_otc_only: bool = True
    trade_min_payout_floor_percent: float = 90.0
    affiliate_postback_secret: str = ""
    affiliate_postback_hmac_secret: str = ""
    affiliate_trust_x_forwarded_for: bool = False
    affiliate_gate_required: bool = True
    affiliate_email_confirm_required: bool = True
    affiliate_email_confirm_events: str = (
        "email confirmation,email_confirmation,emailconfirmed,confirm_email,mail_confirm"
    )

    token_system_enabled: bool = True
    tokens_per_trade: int = 1
    token_deposit_events: str = "first deposit,first_deposit,re-deposit,redeposit,rediposit,deposit"
    token_deposit_min_usd: float = 20.0
    token_bracket_low_grant: int = 15
    token_bracket_high_min_usd: float = 100.0
    token_bracket_high_per_dollar: float = 1.0

    strategy_enabled_global: bool = False
    strategy_poll_interval_seconds: float = 1.0
    strategy_min_learning_ticks: int = 30
    strategy_min_confidence: float = 0.65
    strategy_bucket_seconds: int = 10
    strategy_signal_expiry_seconds: int = 5
    strategy_emit_cooldown_seconds: float = 3.0
    # Step 2: strategy / market_data watch OTC symbols from Mongo (see otc_assets sync), not only user picks.
    strategy_subscribe_otc_from_db: bool = True
    strategy_max_otc_ws_symbols: int = 500
    strategy_ws_subscribe_chunk_size: int = 100
    global_trade_expiry_seconds: int = 10
    auto_trade_only: bool = False
    po_api_base_url: str = ""
    po_login_path: str = ""
    # If false, login fails fast with a clear error when URL looks like pocketoption.com/en/login (public site).
    # Default true so POST is attempted; that URL often still times out from servers — use a real API when possible.
    po_allow_public_web_login: bool = True
    # JSON field names for POST / login (default: email, password).
    po_login_email_field: str = "email"
    po_login_password_field: str = "password"
    # Optional JSON merged into login POST (same idea as PO_TRADE_BODY_EXTRA_JSON).
    po_login_body_extra_json: str = ""
    # Dotted path to token string in login JSON, e.g. data.accessToken. Empty = auto-detect common keys.
    po_login_token_json_path: str = ""
    # Prefix for Authorization header from token (default "Bearer "). Set empty to send raw token only.
    po_login_authorization_prefix: str = "Bearer "
    po_profile_path: str = ""
    # Dotted paths into profile JSON for balances (e.g. user.balances.live). Empty = auto-detect.
    po_profile_real_balance_json_path: str = ""
    po_profile_demo_balance_json_path: str = ""
    po_balance_path: str = ""
    # Browser cabinet page (often HTML with embedded JSON). Used to refresh balances when JSON profile API is empty.
    po_cabinet_path: str = "/en/cabinet"
    po_place_trade_path: str = ""
    po_trade_field_asset_id: str = "asset_id"
    po_trade_field_amount: str = "amount"
    po_trade_field_direction: str = "direction"
    po_trade_field_expiry: str = "expiry_seconds"
    po_trade_direction_up: str = "up"
    po_trade_direction_down: str = "down"
    po_trade_body_extra_json: str = ""
    po_trade_response_broker_id_path: str = "id"
    po_trade_result_path_template: str = ""
    po_trade_result_http_method: str = "GET"
    po_trade_result_post_json: str = ""
    po_trade_result_pnl_path: str = ""
    po_trade_result_state_path: str = "status"
    po_trade_result_exit_price_path: str = ""
    po_trade_result_win_states: str = "win,won,success"
    po_trade_result_loss_states: str = "loss,lost"
    po_trade_result_draw_states: str = "draw,tie,refund"
    po_trade_result_open_states: str = "open,pending,active,running"
    po_trade_result_poll_interval_seconds: float = 1.0
    po_trade_result_max_polls: int = 45
    po_trade_result_extra_wait_seconds: float = 0.0
    po_balance_refresh_interval_seconds: float = 60.0 * 60.0 * 12.0
    po_balance_refresh_per_user_timeout_seconds: float = 8.0
    # aiohttp total timeout for each PO HTTP request (login, profile, balance, trades).
    po_http_timeout_seconds: float = 45.0
    # Some APIs / WAFs reject default aiohttp User-Agent; set a browser-like string if needed.
    po_http_user_agent: str = ""
    # Step 1: fetch OTC asset list from PocketOption API (authenticated GET), cache in Mongo.
    po_assets_list_path: str = ""
    po_assets_refresh_interval_seconds: float = 60.0 * 60.0
    po_assets_refresh_telegram_id: int = 0
    po_otc_assets_db_enabled: bool = True
    po_asset_map_json: str = ""
    po_ws_url: str = ""
    po_ws_subscribe_action: str = "subscribe"
    po_ws_symbol_key: str = "symbol"
    po_ws_price_key: str = "price"
    po_ws_timestamp_key: str = "ts"
    master_key: str = ""
    admin_api_key: str = ""
    http_host: str = "0.0.0.0"
    http_port: int = Field(default=8000, validation_alias=AliasChoices("PORT", "HTTP_PORT"))
    settlement_poll_interval_seconds: float = 1.0
    log_level: str = "INFO"

    support_text: str = ""
    support_url: str = ""
    pocketoption_register_url: str = "https://p.finance/en/register/"
    deposit_url: str = ""
    withdraw_url: str = ""
    deposit_promo_code: str = "10INAROW"
    faq_text: str = ""
    faq_url: str = ""
    token_topup_text: str = ""
    token_topup_url: str = ""
    get_tokens_promo_code: str = "RSI100"
    # Username only (no @). Opens https://t.me/... from Support buttons and Get Tokens caption.
    support_telegram_username: str = "alex_trading_support"

    status_tier_rule: str = "tokens"
    status_tiers_json: str = ""

    # "Signal accuracy" display config (computed from recent settled trades).
    accuracy_window_trades: int = 50
    accuracy_min_trades: int = 10
    accuracy_session_trades: int = 10
    accuracy_count_only_base_martingale_trades: bool = True

    @field_validator("global_trade_expiry_seconds", mode="after")
    @classmethod
    def _normalize_global_trade_expiry(cls, v: int) -> int:
        return int(v) if int(v) in _VALID_GLOBAL_EXPIRY else 10

    def http_deposit_page_url(self) -> str:
        """
        First http(s) URL from deposit_url, then token_topup_url.
        Use this for InlineKeyboardButton(url=...) so the Telegram client shows
        the native “Open this link?” sheet; Open launches the system browser.
        """
        for raw in (self.deposit_url, self.token_topup_url):
            u = (raw or "").strip()
            if u.startswith("http://") or u.startswith("https://"):
                return self._normalize_po_public_domain(u)
        return ""

    def http_withdraw_page_url(self) -> str:
        u = (self.withdraw_url or "").strip()
        if u.startswith("http://") or u.startswith("https://"):
            return self._normalize_po_public_domain(u)
        return ""

    def pocketoption_register_http_url(self) -> str:
        u = (self.pocketoption_register_url or "").strip()
        if u.startswith("http://") or u.startswith("https://"):
            return self._normalize_po_public_domain(u)
        return "https://p.finance/en/register/"

    def _normalize_po_public_domain(self, url: str) -> str:
        """
        Client requirement: PocketOption public links must use p.finance domain.
        If a configured URL points at pocketoption.com, rewrite host to p.finance.
        """
        try:
            p = urlsplit(url)
            host = (p.netloc or "").lower()
            if "pocketoption.com" in host:
                return urlunsplit((p.scheme, "p.finance", p.path, p.query, p.fragment))
        except Exception:
            return url
        return url

    def admin_ids(self) -> set[int]:
        raw = self.admin_telegram_ids.strip()
        if not raw:
            return set()
        out: set[int] = set()
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                out.add(int(part))
            except ValueError:
                continue
        return out

    def require_master_key(self) -> str:
        if not self.master_key.strip():
            raise ValueError("MASTER_KEY is required for credential encryption")
        return self.master_key.strip()

    def require_bot_token(self) -> str:
        if not self.bot_token.strip():
            raise ValueError("BOT_TOKEN is required to run the telegram bot")
        return self.bot_token.strip()

    def require_admin_api_key(self) -> str:
        if not self.admin_api_key.strip():
            raise ValueError("ADMIN_API_KEY is required for admin api access")
        return self.admin_api_key.strip()

    def optional_webhook_secret(self) -> str:
        return self.webhook_secret.strip()

    def optional_webhook_hmac_secret(self) -> str:
        return self.webhook_hmac_secret.strip()

    def optional_po_asset_map_json(self) -> str:
        return self.po_asset_map_json.strip()

    def optional_affiliate_postback_secret(self) -> str:
        return self.affiliate_postback_secret.strip()

    def optional_affiliate_postback_hmac_secret(self) -> str:
        return self.affiliate_postback_hmac_secret.strip()

    def affiliate_email_confirm_event_list(self) -> list[str]:
        raw = self.affiliate_email_confirm_events.strip()
        if not raw:
            return []
        return [x for x in (p.strip() for p in raw.split(",")) if x]

    def token_deposit_event_list(self) -> list[str]:
        raw = self.token_deposit_events.strip()
        if not raw:
            return []
        return [x for x in (p.strip() for p in raw.split(",")) if x]

    def pocketoption_place_trade_enabled(self) -> bool:
        return bool(self.po_api_base_url.strip() and self.po_place_trade_path.strip())

    def pocketoption_trade_result_enabled(self) -> bool:
        t = self.po_trade_result_path_template.strip()
        return bool(self.po_api_base_url.strip() and t and "{id}" in t)

    def pocketoption_balance_path_configured(self) -> bool:
        """GET path for balance; if empty, use profile-only flows for balances when possible."""
        return bool(self.po_balance_path.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

