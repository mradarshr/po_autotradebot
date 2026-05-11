from __future__ import annotations

import re
from typing import Any

from app.integrations.pocketoption.jsonpath import get_by_dotted_path


def _num(obj: object) -> float | None:
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


def _money_str(s: str) -> float | None:
    t = (s or "").replace(",", " ")
    m = re.search(r"([-+]?\d+(?:\.\d+)?)", t)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _coerce_money(v: object) -> float | None:
    if isinstance(v, str):
        return _num(v) or _money_str(v)
    return _num(v)


def _deep_scan_balances(obj: Any, depth: int = 0) -> tuple[float | None, float | None]:
    """
    Walk nested dict/list; assign numeric values whose keys look like real vs demo balance.
    """
    if depth > 18:
        return None, None
    real_v: float | None = None
    demo_v: float | None = None

    def consider_key_val(kl: str, val: object) -> None:
        nonlocal real_v, demo_v
        v = _coerce_money(val)
        if v is None:
            return
        if any(
            x in kl
            for x in (
                "demo_balance",
                "demobalance",
                "balance_demo",
                "practice_balance",
                "practicebalance",
                "virtual_balance",
                "virtualbalance",
                "fun_balance",
                "money_demo",
                "moneydemo",
                "deposit_demo",
                "wallet_demo",
            )
        ):
            if demo_v is None:
                demo_v = v
            return
        if kl in ("demo", "practice", "virtual") and "profit" not in kl:
            if demo_v is None:
                demo_v = v
            return
        if any(
            x in kl
            for x in (
                "real_balance",
                "realbalance",
                "balance_real",
                "live_balance",
                "livebalance",
                "money_real",
                "moneyreal",
                "deposit_real",
                "wallet_real",
                "main_balance",
            )
        ):
            if real_v is None:
                real_v = v
            return
        if kl == "live" and "deliver" not in kl:
            if real_v is None:
                real_v = v
            return

    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            consider_key_val(kl, v)
            if isinstance(v, (dict, list)):
                rr, dd = _deep_scan_balances(v, depth + 1)
                if real_v is None:
                    real_v = rr
                if demo_v is None:
                    demo_v = dd
    elif isinstance(obj, list):
        for it in obj[:80]:
            if isinstance(it, (dict, list)):
                rr, dd = _deep_scan_balances(it, depth + 1)
                if real_v is None:
                    real_v = rr
                if demo_v is None:
                    demo_v = dd
    return real_v, demo_v


def extract_real_demo_usd(payload: object) -> tuple[float | None, float | None]:
    """
    Best-effort real + demo balances from profile/balance API JSON.
    Uses env PO_PROFILE_*_BALANCE_JSON_PATH when set, then known keys, recursion, then deep scan.
    """
    if isinstance(payload, list) and payload:
        if isinstance(payload[0], dict):
            return extract_real_demo_usd(payload[0])
        return None, None
    if not isinstance(payload, dict):
        return None, None

    from app.config import get_settings

    s = get_settings()
    real_v: float | None = None
    demo_v: float | None = None

    rp = (s.po_profile_real_balance_json_path or "").strip()
    dp = (s.po_profile_demo_balance_json_path or "").strip()
    if rp:
        real_v = _coerce_money(get_by_dotted_path(payload, rp))
    if dp:
        demo_v = _coerce_money(get_by_dotted_path(payload, dp))

    real_v = real_v or (
        _num(payload.get("real_balance"))
        or _num(payload.get("real"))
        or _num(payload.get("realBalance"))
        or _num(payload.get("balance_real"))
        or _num(payload.get("real_money"))
        or _num(payload.get("realMoney"))
        or _num(payload.get("live_balance"))
        or _num(payload.get("liveBalance"))
        or _num(payload.get("money_real"))
        or _num(payload.get("moneyReal"))
    )
    demo_v = demo_v or (
        _num(payload.get("demo_balance"))
        or _num(payload.get("demo"))
        or _num(payload.get("demoBalance"))
        or _num(payload.get("balance_demo"))
        or _num(payload.get("demo_money"))
        or _num(payload.get("demoMoney"))
        or _num(payload.get("practice_balance"))
        or _num(payload.get("practiceBalance"))
        or _num(payload.get("virtual_balance"))
        or _num(payload.get("virtualBalance"))
    )

    bal = payload.get("balance")
    if isinstance(bal, dict):
        if real_v is None:
            real_v = _num(bal.get("real")) or _num(bal.get("amount")) or _num(bal.get("real_balance"))
        if demo_v is None:
            demo_v = _num(bal.get("demo")) or _num(bal.get("demo_amount"))

    demo_obj = payload.get("demo")
    if isinstance(demo_obj, dict) and demo_v is None:
        demo_v = _num(demo_obj.get("amount")) or _num(demo_obj.get("balance"))

    for key in ("balances", "accounts", "wallets"):
        arr = payload.get(key)
        if not isinstance(arr, list):
            continue
        for item in arr:
            if not isinstance(item, dict):
                continue
            t = str(item.get("type") or item.get("account") or item.get("name") or "").lower()
            amt = _num(item.get("balance")) or _num(item.get("amount")) or _num(item.get("sum"))
            if amt is None:
                continue
            if "real" in t or t in ("live", "main", "usd", "account"):
                if real_v is None:
                    real_v = amt
            if "demo" in t or "practice" in t or "virtual" in t:
                if demo_v is None:
                    demo_v = amt

    if real_v is None and isinstance(payload, dict):
        for k in ("real_balance_str", "realBalanceStr", "realBalance", "real_balance"):
            raw = payload.get(k)
            if isinstance(raw, str) and raw.strip():
                real_v = _money_str(raw)
                if real_v is not None:
                    break

    if demo_v is None and isinstance(payload, dict):
        for k in ("demo_balance_str", "demoBalanceStr", "demoBalance", "demo_balance"):
            raw = payload.get(k)
            if isinstance(raw, str) and raw.strip():
                demo_v = _money_str(raw)
                if demo_v is not None:
                    break

    for key in ("data", "result", "body", "response", "user", "profile", "account"):
        sub = payload.get(key)
        if isinstance(sub, dict):
            rr, dd = extract_real_demo_usd(sub)
            if real_v is None:
                real_v = rr
            if demo_v is None:
                demo_v = dd
        elif isinstance(sub, list) and sub and isinstance(sub[0], dict):
            rr, dd = extract_real_demo_usd(sub[0])
            if real_v is None:
                real_v = rr
            if demo_v is None:
                demo_v = dd

    if real_v is None or demo_v is None:
        dr, dd = _deep_scan_balances(payload)
        if real_v is None:
            real_v = dr
        if demo_v is None:
            demo_v = dd

    return real_v, demo_v
