from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizedOtcAsset:
    symbol: str
    asset_id: str
    payout_percent: float | None
    is_open: bool
    is_otc: bool


def _norm_symbol_key(raw: str) -> str:
    t = (raw or "").strip().lower()
    if not t:
        return ""
    t = t.replace("/", "").replace(" ", "").replace("-", "_")
    while "__" in t:
        t = t.replace("__", "_")
    return t


def _truthy_otc(item: dict[str, Any]) -> bool | None:
    """Return True/False if explicit, None if unknown."""
    v = item.get("is_otc")
    if v is True:
        return True
    if v is False:
        return False
    v2 = item.get("otc")
    if v2 is True:
        return True
    if v2 is False:
        return False
    t = str(item.get("type") or item.get("market") or item.get("category") or "").lower()
    if "otc" in t:
        return True
    if t in ("forex", "crypto", "stock") and "otc" not in t:
        return False
    return None


def _is_probably_otc(item: dict[str, Any], symbol_key: str) -> bool:
    ex = _truthy_otc(item)
    if ex is True:
        return True
    if ex is False:
        return False
    if "_otc" in symbol_key or symbol_key.endswith("otc"):
        return True
    name = str(item.get("name") or item.get("symbol") or item.get("title") or "").lower()
    return "otc" in name or "_otc" in name.replace(" ", "_")


def _extract_id(item: dict[str, Any]) -> str | None:
    for k in ("id", "asset_id", "assetId", "instrument_id", "instrumentId", "binary_id", "pair_id"):
        v = item.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return None


def _extract_symbol_raw(item: dict[str, Any]) -> str | None:
    for k in ("symbol", "name", "code", "pair", "asset", "title", "ticker"):
        v = item.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return None


def _extract_payout(item: dict[str, Any]) -> float | None:
    for k in ("payout", "payout_percent", "profit", "profit_percent", "percent", "rate"):
        v = item.get(k)
        if v is None:
            continue
        try:
            return float(v)
        except Exception:
            continue
    return None


def _extract_open(item: dict[str, Any]) -> bool:
    for k in ("is_open", "open", "active", "enabled", "is_active"):
        v = item.get(k)
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            return v.strip().lower() in ("1", "true", "yes", "open")
    return True


def _iter_asset_dict_lists(payload: Any) -> list[dict[str, Any]]:
    """Collect dict-like rows that look like instruments from common wrapper shapes."""
    out: list[dict[str, Any]] = []
    if isinstance(payload, list):
        for x in payload:
            if isinstance(x, dict):
                out.append(x)
        return out
    if not isinstance(payload, dict):
        return out
    for k in ("data", "assets", "result", "items", "instruments", "pairs", "rows", "list"):
        v = payload.get(k)
        if isinstance(v, list):
            for x in v:
                if isinstance(x, dict):
                    out.append(x)
            if out:
                return out
    # Single wrapper object
    if any(k in payload for k in ("id", "asset_id", "symbol", "name")):
        out.append(payload)
    return out


def normalize_otc_assets_from_payload(payload: Any) -> list[NormalizedOtcAsset]:
    rows = _iter_asset_dict_lists(payload)
    seen: set[str] = set()
    result: list[NormalizedOtcAsset] = []
    for item in rows:
        sym_raw = _extract_symbol_raw(item)
        aid = _extract_id(item)
        if not sym_raw or not aid:
            continue
        sym_key = _norm_symbol_key(sym_raw)
        if not sym_key:
            continue
        if not _is_probably_otc(item, sym_key):
            continue
        if sym_key in seen:
            continue
        seen.add(sym_key)
        result.append(
            NormalizedOtcAsset(
                symbol=sym_key,
                asset_id=aid,
                payout_percent=_extract_payout(item),
                is_open=_extract_open(item),
                is_otc=True,
            )
        )
    return result
