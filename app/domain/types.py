from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

UiLanguage = Literal["ar", "de", "en", "es", "fr", "id", "it", "fil", "pt", "ru", "hi"]


class UserSettings(BaseModel):
    trading_enabled: bool = False
    trade_account: Literal["demo", "real"] = "demo"
    language: UiLanguage = "en"
    pocketoption_uid: str = ""
    signal_timeframe_minutes: int = 5
    strategy_enabled: bool = False
    strategy_preset: Literal["precision", "high_profit", "balanced", "conservative"] = "precision"
    stake: float = 1.0
    expiry_seconds: int = 5
    assets: list[str] = Field(default_factory=list)
    min_payout_percent: float = 0.0
    max_stake_per_trade: float = 0.0
    max_stake_per_day: float = 0.0
    max_trades_per_day: int = 15
    max_loss_per_day: float = 0.0
    cooldown_seconds: int = 0
    max_consecutive_losses: int = 0
    martingale_enabled: bool = False
    martingale_max_levels: int = Field(default=5, ge=1, le=20)
    martingale_multipliers_csv: str = "1,2,4,8,16,32,64"


class User(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    created_at: datetime
    blocked: bool = False
    settings: UserSettings = Field(default_factory=UserSettings)
    martingale_step: int = Field(default=0, ge=0)
    po_real_balance_usd: float | None = None
    po_demo_balance_usd: float | None = None
    po_real_balance_updated_at: datetime | None = None


class Event(BaseModel):
    type: Literal[
        "user_created",
        "user_updated",
        "settings_updated",
        "trading_enabled",
        "trading_disabled",
        "user_blocked",
        "user_unblocked",
    ]
    telegram_id: int
    created_at: datetime
    payload: dict = Field(default_factory=dict)

