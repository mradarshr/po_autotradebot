from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from app.db.mongo import mongo


MediaType = Literal["photo", "video"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MediaItem(BaseModel):
    key: str
    type: MediaType
    file_id: str
    updated_at: datetime = Field(default_factory=_now)
    updated_by: int | None = None


class MediaRepo:
    collection_name = "media"

    async def get_media(self, key: str) -> MediaItem | None:
        k = (key or "").strip()
        if not k:
            return None
        doc = await mongo.db[self.collection_name].find_one({"key": k})
        if doc is None:
            return None
        return MediaItem.model_validate(doc)

    async def set_media(self, *, key: str, type_: MediaType, file_id: str, updated_by: int | None) -> MediaItem:
        k = (key or "").strip()
        if not k:
            raise ValueError("key is required")
        fid = (file_id or "").strip()
        if not fid:
            raise ValueError("file_id is required")
        item = MediaItem(key=k, type=type_, file_id=fid, updated_at=_now(), updated_by=updated_by)
        await mongo.db[self.collection_name].update_one(
            {"key": k},
            {"$set": item.model_dump()},
            upsert=True,
        )
        return item

    async def clear_media(self, key: str) -> bool:
        k = (key or "").strip()
        if not k:
            return False
        res = await mongo.db[self.collection_name].delete_one({"key": k})
        return bool(res.deleted_count)

    async def list_keys(self) -> list[str]:
        cur = mongo.db[self.collection_name].find({}, {"key": 1}, sort=[("key", 1)])
        docs = await cur.to_list(length=1000)
        out: list[str] = []
        for d in docs:
            k = d.get("key")
            if isinstance(k, str) and k.strip():
                out.append(k.strip())
        return out


media_repo = MediaRepo()

