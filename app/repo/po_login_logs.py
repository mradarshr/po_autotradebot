from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.mongo import mongo


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PoLoginLogsRepo:
    async def append(
        self,
        *,
        telegram_id: int,
        ok: bool,
        error_type: str | None = None,
        detail: str | None = None,
        http_status: int | None = None,
        op: str | None = None,
    ) -> None:
        doc: dict[str, Any] = {
            "telegram_id": int(telegram_id),
            "ok": bool(ok),
            "created_at": _now(),
        }
        if error_type:
            doc["error_type"] = str(error_type)[:120]
        if detail:
            doc["detail"] = str(detail)[:2000]
        if http_status is not None:
            doc["http_status"] = int(http_status)
        if op:
            doc["op"] = str(op)[:80]
        await mongo.db.po_login_logs.insert_one(doc)

    async def recent_for_telegram(self, telegram_id: int, limit: int = 5) -> list[dict[str, Any]]:
        lim = max(1, min(20, int(limit)))
        cur = mongo.db.po_login_logs.find(
            {"telegram_id": int(telegram_id)},
            sort=[("created_at", -1)],
            limit=lim,
        )
        docs = await cur.to_list(length=lim)
        return [dict(d) for d in docs]


po_login_logs_repo = PoLoginLogsRepo()
