from __future__ import annotations

import logging

from app.config import get_settings
from app.repo.credentials import credentials_repo
from app.repo.otc_assets import otc_assets_repo
from app.services.assets import reload_po_otc_cache_from_db
from app.services.po_assets_normalize import normalize_otc_assets_from_payload
from app.services.pocketoption_sessions import pocketoption_sessions

logger = logging.getLogger(__name__)


async def _pick_refresh_telegram_id() -> int | None:
    s = get_settings()
    tid = int(s.po_assets_refresh_telegram_id or 0)
    if tid > 0:
        if await credentials_repo.has_credentials(tid):
            return tid
        logger.warning("po_assets_refresh_telegram_id set but no credentials for that user")
    return await credentials_repo.first_telegram_id_with_credentials()


async def sync_otc_assets_from_pocketoption() -> int:
    """
    Fetch assets list via PO API (authenticated), normalize OTC rows, upsert Mongo,
    refresh in-memory catalog for resolve().
    """
    path = get_settings().po_assets_list_path.strip()
    if not path:
        logger.debug("po_assets_list_path empty; skip OTC sync")
        return 0
    tid = await _pick_refresh_telegram_id()
    if tid is None:
        logger.warning("OTC asset sync skipped: no credentials in DB")
        return 0
    try:
        raw = await pocketoption_sessions.call(
            tid,
            lambda c, s: c.fetch_assets_list(s),
            retry_on_auth_failure=True,
        )
    except Exception as e:
        logger.warning("OTC asset fetch failed: %s", type(e).__name__)
        return 0
    if raw is None:
        return 0
    norm = normalize_otc_assets_from_payload(raw)
    if not norm:
        logger.warning(
            "OTC asset sync: API returned no recognizable OTC rows (check PO_ASSETS_LIST_PATH / response shape)"
        )
        return 0
    n = await otc_assets_repo.replace_from_normalized(norm)
    await reload_po_otc_cache_from_db()
    logger.info("OTC asset sync: stored %s instruments", n)
    return n
