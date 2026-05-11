from __future__ import annotations

import asyncio
import logging

from app.config import get_settings
from app.services.otc_assets_sync import sync_otc_assets_from_pocketoption

logger = logging.getLogger(__name__)


class OtcAssetsWorker:
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

    async def _run(self) -> None:
        s = get_settings()
        interval = max(300.0, float(s.po_assets_refresh_interval_seconds))
        # First run soon after startup
        first = True
        while not self._stop.is_set():
            if get_settings().po_assets_list_path.strip():
                try:
                    await sync_otc_assets_from_pocketoption()
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception("otc assets worker tick failed")
            if first:
                first = False
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=15.0)
                except asyncio.TimeoutError:
                    pass
                continue
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=interval)
            except asyncio.TimeoutError:
                pass


otc_assets_worker = OtcAssetsWorker()
