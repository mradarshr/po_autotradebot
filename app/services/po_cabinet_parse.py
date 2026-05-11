from __future__ import annotations

import json
import re
from typing import Any

from app.services.po_balance_parse import extract_real_demo_usd

_NEXT_DATA_RE = re.compile(
    r'<script\s+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)

# Loose JSON fragments sometimes embedded in cabinet HTML
_BALANCE_NUM_RE = re.compile(
    r'"(?:demo|real)(?:Balance|_balance|Money)"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
    re.IGNORECASE,
)
_LIVE_PRACTICE_RE = re.compile(
    r'"(?:liveBalance|practiceBalance)"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
    re.IGNORECASE,
)


def _normalize_uid(raw: object) -> str | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        try:
            if raw != raw:
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


_UID_KEYS = frozenset(
    {
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
    }
)


def extract_uid_from_json_blob(data: Any, *, depth: int = 0) -> str | None:
    if depth > 24:
        return None
    if isinstance(data, dict):
        for k in _UID_KEYS:
            got = _normalize_uid(data.get(k))
            if got:
                return got
        for key in ("user", "profile", "data", "result", "account", "auth", "pageProps", "props"):
            sub = data.get(key)
            got = extract_uid_from_json_blob(sub, depth=depth + 1)
            if got:
                return got
        for v in data.values():
            if isinstance(v, (dict, list)):
                got = extract_uid_from_json_blob(v, depth=depth + 1)
                if got:
                    return got
    elif isinstance(data, list):
        for it in data[:40]:
            got = extract_uid_from_json_blob(it, depth=depth + 1)
            if got:
                return got
    return None


def extract_balances_and_uid_from_cabinet_body(body: bytes) -> tuple[float | None, float | None, str | None]:
    """
    Parse real/demo balances and optional UID from /en/cabinet HTML or JSON.
    """
    text = body.decode("utf-8", errors="replace")
    uid: str | None = None
    real_v: float | None = None
    demo_v: float | None = None

    m = _NEXT_DATA_RE.search(text)
    if m:
        try:
            blob = json.loads(m.group(1))
            uid = extract_uid_from_json_blob(blob)
            r, d = extract_real_demo_usd(blob)
            if r is not None:
                real_v = r
            if d is not None:
                demo_v = d
            if real_v is None and demo_v is None:
                props = blob.get("props") if isinstance(blob, dict) else None
                pp = (props or {}).get("pageProps") if isinstance(props, dict) else None
                if isinstance(pp, dict):
                    r, d = extract_real_demo_usd(pp)
                    if r is not None:
                        real_v = r
                    if d is not None:
                        demo_v = d
                    if uid is None:
                        uid = extract_uid_from_json_blob(pp)
        except Exception:
            pass

    if real_v is None and demo_v is None:
        try:
            data = json.loads(text.strip())
            if isinstance(data, (dict, list)):
                r, d = extract_real_demo_usd(data)
                if r is not None:
                    real_v = r
                if d is not None:
                    demo_v = d
                if uid is None:
                    uid = extract_uid_from_json_blob(data)
        except Exception:
            pass

    if real_v is None and demo_v is None:
        pairs: dict[str, list[float]] = {"demo": [], "real": []}
        for m2 in _BALANCE_NUM_RE.finditer(text):
            key = m2.group(0).lower()
            try:
                val = float(m2.group(1))
            except ValueError:
                continue
            if "demo" in key:
                pairs["demo"].append(val)
            elif "real" in key:
                pairs["real"].append(val)
        if pairs["real"]:
            real_v = pairs["real"][0]
        if pairs["demo"]:
            demo_v = pairs["demo"][0]

    if real_v is None or demo_v is None:
        for m3 in _LIVE_PRACTICE_RE.finditer(text):
            key = (m3.group(0) or "").lower()
            try:
                val = float(m3.group(1))
            except ValueError:
                continue
            if "practice" in key and demo_v is None:
                demo_v = val
            elif "live" in key and real_v is None:
                real_v = val

    if uid is None:
        for pat in (
            r'"userId"\s*:\s*"?([0-9]{4,16})"?',
            r'"uid"\s*:\s*"?([0-9]{4,16})"?',
            r'"id"\s*:\s*"?([0-9]{4,16})"?\s*,\s*"[^"]*email',
        ):
            mx = re.search(pat, text)
            if mx:
                uid = _normalize_uid(mx.group(1))
                if uid:
                    break

    return real_v, demo_v, uid
