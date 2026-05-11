from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from app.db.mongo import mongo

if TYPE_CHECKING:
    from app.services.po_assets_normalize import NormalizedOtcAsset


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OtcAssetsRepo:
    async def replace_from_normalized(
        self,
        items: list["NormalizedOtcAsset"],
        *,
        source: str = "pocketoption",
    ) -> int:
        """
        Upsert normalized OTC rows. Returns count written.
        """
        if not items:
            return 0
        n = 0
        for it in items:
            sym = str(it.symbol).strip().lower()
            aid = str(it.asset_id).strip()
            if not sym or not aid:
                continue
            payout = it.payout_percent
            doc: dict[str, Any] = {
                "symbol": sym,
                "asset_id": aid,
                "payout_percent": float(payout) if payout is not None else None,
                "is_open": bool(it.is_open),
                "is_otc": True,
                "source": source,
                "updated_at": _now(),
            }
            await mongo.db.otc_assets.update_one(
                {"symbol": sym},
                {"$set": doc},
                upsert=True,
            )
            n += 1
        return n

    async def list_all_otc(self) -> list[dict[str, Any]]:
        cur = mongo.db.otc_assets.find({"is_otc": True}, projection={"_id": 0})
        docs = await cur.to_list(length=None)
        return [d for d in docs if isinstance(d, dict)]

    async def list_otc_symbols(self) -> list[str]:
        docs = await self.list_all_otc()
        return sorted({str(d.get("symbol") or "").strip().lower() for d in docs if d.get("symbol")})

    async def list_otc_symbols_for_ws(
        self,
        *,
        limit: int = 0,
        open_only: bool = True,
        min_payout_percent: float | None = None,
    ) -> list[str]:
        """
        Symbols to subscribe on the quote WS: OTC, optionally open-only and payout floor,
        sorted by payout (desc) then symbol. limit<=0 means no cap.
        """
        filt: dict[str, Any] = {"is_otc": True}
        if open_only:
            filt["is_open"] = True
        if min_payout_percent is not None and float(min_payout_percent) > 0:
            filt["payout_percent"] = {"$gte": float(min_payout_percent)}

        cur = mongo.db.otc_assets.find(
            filt,
            projection={"symbol": 1, "_id": 0},
            sort=[("payout_percent", -1), ("symbol", 1)],
        )
        cap = int(limit) if int(limit) > 0 else 0
        if cap:
            cur = cur.limit(cap)
            docs = await cur.to_list(length=cap)
        else:
            docs = await cur.to_list(length=None)
        out: list[str] = []
        seen: set[str] = set()
        for d in docs:
            if not isinstance(d, dict):
                continue
            sym = str(d.get("symbol") or "").strip().lower()
            if not sym or sym in seen:
                continue
            seen.add(sym)
            out.append(sym)
        return out

    async def count_otc(self) -> int:
        return int(await mongo.db.otc_assets.count_documents({"is_otc": True}))


otc_assets_repo = OtcAssetsRepo()
