from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from app.config import get_settings
from app.db.mongo import mongo
from app.repo.affiliate import affiliate_repo
from app.services.pocketoption_auth import pocketoption_auth
from app.services.po_balance_parse import extract_real_demo_usd

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BalanceWorker:
    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> None:
        if self._task is not None:
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._stop.set()
        t = self._task
        self._task = None
        await t

    async def _list_signed_in_ids(self) -> list[int]:
        cur = mongo.db.credentials.find({}, projection={"_id": 0, "telegram_id": 1})
        docs = await cur.to_list(length=None)
        out: list[int] = []
        for d in docs:
            try:
                out.append(int(d.get("telegram_id")))
            except Exception:
                continue
        return out

    async def _store_balance(
        self,
        telegram_id: int,
        real_usd: float | None,
        demo_usd: float | None,
        *,
        update_value: bool,
    ) -> None:
        patch: dict[str, Any] = {"po_real_balance_updated_at": _now()}
        if update_value:
            patch["po_real_balance_usd"] = float(real_usd) if real_usd is not None else None
            patch["po_demo_balance_usd"] = float(demo_usd) if demo_usd is not None else None
        await mongo.db.users.update_one({"telegram_id": int(telegram_id)}, {"$set": patch})

    async def _fetch_balances(self, telegram_id: int) -> tuple[float | None, float | None]:
        payload = await pocketoption_auth.balance(telegram_id)
        return extract_real_demo_usd(payload)

    async def _run(self) -> None:
        s = get_settings()
        interval = max(60.0, float(s.po_balance_refresh_interval_seconds))
        per_user_timeout = max(1.0, float(s.po_balance_refresh_per_user_timeout_seconds))
        while not self._stop.is_set():
            try:
                ids = await self._list_signed_in_ids()
                if not get_settings().pocketoption_balance_path_configured():
                    ids = []
                for tid in ids:
                    if self._stop.is_set():
                        break
                    if get_settings().affiliate_gate_required:
                        ok, _ = await affiliate_repo.is_trading_allowed(tid)
                        if not ok:
                            continue
                    try:
                        r, d = await asyncio.wait_for(self._fetch_balances(tid), timeout=per_user_timeout)
                        await self._store_balance(tid, r, d, update_value=True)
                    except asyncio.TimeoutError:
                        # Keep previous value; just bump timestamp.
                        try:
                            await self._store_balance(tid, None, None, update_value=False)
                        except Exception:
                            pass
                    except Exception:
                        # Keep worker alive; avoid spamming logs per-user.
                        try:
                            await self._store_balance(tid, None, None, update_value=False)
                        except Exception:
                            pass
                        continue
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("balance worker tick failed")

            try:
                await asyncio.wait_for(self._stop.wait(), timeout=interval)
            except asyncio.TimeoutError:
                pass


balance_worker = BalanceWorker()

