from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ReturnDocument

from app.db.mongo import mongo
from app.domain.execution import Trade


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TradesRepo:
    async def create(self, t: Trade) -> None:
        await mongo.db.trades.insert_one(t.model_dump())

    async def update(self, trade_id: str, patch: dict[str, Any]) -> None:
        await mongo.db.trades.update_one({"trade_id": trade_id}, {"$set": patch})

    async def list_recent_for_user(self, telegram_id: int, limit: int = 20) -> list[Trade]:
        cur = mongo.db.trades.find({"telegram_id": telegram_id}, sort=[("created_at", -1)], limit=limit)
        docs = await cur.to_list(length=limit)
        return [Trade.model_validate(d) for d in docs]

    async def get_by_trade_id(self, trade_id: str) -> Trade | None:
        tid = (trade_id or "").strip()
        if not tid:
            return None
        doc = await mongo.db.trades.find_one({"trade_id": tid})
        if doc is None:
            return None
        return Trade.model_validate(doc)

    async def stats_since(self, telegram_id: int, since: datetime) -> tuple[int, float]:
        pipeline = [
            {"$match": {"telegram_id": telegram_id, "created_at": {"$gte": since}, "status": "settled"}},
            {"$group": {"_id": None, "count": {"$sum": 1}, "pnl": {"$sum": "$pnl"}}},
        ]
        res = await mongo.db.trades.aggregate(pipeline).to_list(length=1)
        if not res:
            return 0, 0.0
        return int(res[0].get("count") or 0), float(res[0].get("pnl") or 0.0)

    async def sum_stake_since(self, telegram_id: int, since: datetime) -> float:
        pipeline = [
            {"$match": {"telegram_id": telegram_id, "created_at": {"$gte": since}}},
            {"$group": {"_id": None, "total": {"$sum": "$stake"}}},
        ]
        res = await mongo.db.trades.aggregate(pipeline).to_list(length=1)
        if not res:
            return 0.0
        return float(res[0].get("total") or 0.0)

    async def last_settled_results(self, telegram_id: int, limit: int) -> list[float]:
        if limit <= 0:
            return []
        cur = mongo.db.trades.find(
            {"telegram_id": telegram_id, "status": "settled"},
            sort=[("created_at", -1)],
            limit=limit,
            projection={"pnl": 1},
        )
        docs = await cur.to_list(length=limit)
        out = []
        for d in docs:
            try:
                out.append(float(d.get("pnl")))
            except Exception:
                continue
        return out

    async def last_settled_pnls(self, telegram_id: int, limit: int) -> list[float]:
        """
        Same as last_settled_results, but returns PnL list for clarity at call sites.
        """
        return await self.last_settled_results(telegram_id, limit)

    async def last_settled_pnls_session(
        self,
        telegram_id: int,
        max_trades: int,
        *,
        exclude_martingale_recovery: bool,
    ) -> list[float]:
        if max_trades <= 0:
            return []
        cap = max_trades * 200 if exclude_martingale_recovery else max_trades
        cur = mongo.db.trades.find(
            {"telegram_id": telegram_id, "status": "settled"},
            sort=[("created_at", -1)],
            limit=max(1, cap),
            projection={"pnl": 1, "martingale_step_at_open": 1},
        )
        docs = await cur.to_list(length=cap)
        out: list[float] = []
        for d in docs:
            if exclude_martingale_recovery:
                raw = d.get("martingale_step_at_open")
                if raw is not None and int(raw) > 0:
                    continue
            try:
                out.append(float(d.get("pnl")))
            except Exception:
                continue
            if len(out) >= max_trades:
                break
        return out

    async def settled_count_and_pnl(self, telegram_id: int, broker: str) -> tuple[int, float]:
        """Settled trades count and cumulative PnL for a broker (e.g. pocketoption vs simulated)."""
        pipeline = [
            {
                "$match": {
                    "telegram_id": telegram_id,
                    "status": "settled",
                    "broker": broker,
                }
            },
            {"$group": {"_id": None, "c": {"$sum": 1}, "p": {"$sum": {"$ifNull": ["$pnl", 0.0]}}}},
        ]
        res = await mongo.db.trades.aggregate(pipeline).to_list(length=1)
        if not res:
            return 0, 0.0
        return int(res[0].get("c") or 0), float(res[0].get("p") or 0.0)

    async def claim_one_due_for_settlement(self, now: datetime) -> Trade | None:
        candidate = await mongo.db.trades.find_one(
            {"status": {"$in": ["opened", "created"]}, "expiry_at": {"$lte": now}},
            sort=[("expiry_at", 1)],
        )
        if candidate is None:
            return None
        tid = str(candidate.get("trade_id") or "")
        if not tid:
            return None
        updated = await mongo.db.trades.find_one_and_update(
            {"trade_id": tid, "status": {"$in": ["opened", "created"]}},
            {"$set": {"status": "settling"}},
            return_document=ReturnDocument.AFTER,
        )
        if updated is None:
            return None
        return Trade.model_validate(updated)


trades_repo = TradesRepo()

