from __future__ import annotations

from app.config import get_settings
from app.observability.log import log_event, log_exception
from app.repo.affiliate import affiliate_repo
from app.repo.credentials import credentials_repo
from app.repo.users import users_repo
from app.services.po_balance_parse import extract_real_demo_usd
from app.services.po_cabinet_parse import extract_balances_and_uid_from_cabinet_body
from app.services.pocketoption_auth import pocketoption_auth
from app.services.pocketoption_sessions import pocketoption_sessions


async def refresh_po_balance_cache_for_telegram(telegram_id: int) -> None:
    tid = int(telegram_id)
    if await credentials_repo.get_credentials(tid) is None:
        return
    s = get_settings()
    if s.affiliate_gate_required:
        ok, _ = await affiliate_repo.is_trading_allowed(tid)
        if not ok:
            return
    try:
        await pocketoption_auth.login_for_user(tid)
        if s.pocketoption_balance_path_configured():
            payload = await pocketoption_auth.balance(tid)
        else:
            payload = await pocketoption_auth.profile(tid)
        r_f, d_f = extract_real_demo_usd(payload)
        if r_f is not None or d_f is not None:
            await users_repo.merge_po_balance_cache(tid, real_usd=r_f, demo_usd=d_f)
        await refresh_balances_from_cabinet(tid)
        log_event("po_balance.cache_refreshed", telegram_id=tid)
    except Exception as e:
        log_exception("po_balance.cache_refresh_failed", e, telegram_id=tid)


async def refresh_balances_from_cabinet(telegram_id: int) -> bool:
    """
    GET PO_CABINET_PATH with the user's session; parse balances (and UID) from HTML/JSON.
    Returns True if at least one balance or UID was written.
    """
    tid = int(telegram_id)
    if not get_settings().po_cabinet_path.strip():
        return False
    if await credentials_repo.get_credentials(tid) is None:
        return False
    try:

        async def _fetch(c, s):
            body = await c.cabinet_get(s)
            return body

        body = await pocketoption_sessions.call(tid, _fetch)
    except Exception as e:
        log_exception("po_cabinet.fetch_failed", e, telegram_id=tid)
        return False
    if not body.strip():
        return False
    r, d, uid = extract_balances_and_uid_from_cabinet_body(body)
    updated = False
    if r is not None or d is not None:
        await users_repo.merge_po_balance_cache(tid, real_usd=r, demo_usd=d)
        updated = True
    if uid:
        u = await users_repo.get_user(tid)
        cur = (u.settings.pocketoption_uid if u else "").strip() if u else ""
        if not cur:
            await users_repo.update_settings(tid, {"pocketoption_uid": uid})
            await affiliate_repo.merge_pocketoption_uid(tid, uid)
        updated = True
    if updated:
        log_event("po_cabinet.synced", telegram_id=tid, has_balances=r is not None or d is not None, uid=bool(uid))
    return updated


async def refresh_po_balance_cache_for_affiliate_email(email: str) -> None:
    e = (email or "").strip().lower()
    if not e or "@" not in e:
        return
    acc = await affiliate_repo.get_account_by_email(e)
    if not acc:
        return
    raw = acc.get("telegram_id")
    if raw is None:
        return
    await refresh_po_balance_cache_for_telegram(int(raw))
