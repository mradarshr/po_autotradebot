from __future__ import annotations

from datetime import datetime, timezone

from app.db.mongo import mongo

VALID_SIGNAL_INGEST_MODES = frozenset({"all", "admin_only", "webhook_only", "strategy_only"})
VALID_GLOBAL_TRADE_EXPIRY = frozenset({5, 10, 15, 30})


def _now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_signal_ingest_mode(raw: str | None) -> str:
    m = (raw or "all").strip().lower()
    return m if m in VALID_SIGNAL_INGEST_MODES else "all"


def webhook_ingest_allowed(mode: str) -> bool:
    return normalize_signal_ingest_mode(mode) in ("all", "webhook_only")


def strategy_ingest_allowed(mode: str) -> bool:
    return normalize_signal_ingest_mode(mode) in ("all", "strategy_only")


class SystemRepo:
    async def set_global_trading_enabled(self, enabled: bool) -> None:
        await mongo.db.system.update_one(
            {"key": "global_trading_enabled"},
            {"$set": {"key": "global_trading_enabled", "enabled": bool(enabled), "updated_at": _now()}},
            upsert=True,
        )

    async def get_global_trading_enabled(self) -> bool:
        doc = await mongo.db.system.find_one({"key": "global_trading_enabled"})
        if doc is None:
            return True
        return bool(doc.get("enabled", True))

    async def get_signal_ingest_mode(self) -> str:
        doc = await mongo.db.system.find_one({"key": "signal_ingest_mode"})
        if doc is None:
            return "all"
        return normalize_signal_ingest_mode(str(doc.get("mode") or "all"))

    async def set_signal_ingest_mode(self, mode: str) -> None:
        m = (mode or "").strip().lower()
        if m not in VALID_SIGNAL_INGEST_MODES:
            raise ValueError("invalid_signal_ingest_mode")
        await mongo.db.system.update_one(
            {"key": "signal_ingest_mode"},
            {"$set": {"key": "signal_ingest_mode", "mode": m, "updated_at": _now()}},
            upsert=True,
        )

    async def get_global_trade_expiry_seconds(self) -> int:
        from app.config import get_settings

        doc = await mongo.db.system.find_one({"key": "global_trade_expiry_seconds"})
        if doc is not None and doc.get("value") is not None:
            try:
                v = int(doc["value"])
                if v in VALID_GLOBAL_TRADE_EXPIRY:
                    return v
            except Exception:
                pass
        return normalize_global_trade_expiry_seconds(int(get_settings().global_trade_expiry_seconds))

    async def set_global_trade_expiry_seconds(self, seconds: int) -> None:
        v = int(seconds)
        if v not in VALID_GLOBAL_TRADE_EXPIRY:
            raise ValueError("invalid_global_trade_expiry_seconds")
        await mongo.db.system.update_one(
            {"key": "global_trade_expiry_seconds"},
            {"$set": {"key": "global_trade_expiry_seconds", "value": v, "updated_at": _now()}},
            upsert=True,
        )


def normalize_global_trade_expiry_seconds(raw: int) -> int:
    return int(raw) if int(raw) in VALID_GLOBAL_TRADE_EXPIRY else 10


system_repo = SystemRepo()

