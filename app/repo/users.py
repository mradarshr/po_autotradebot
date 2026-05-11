from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError

from app.db.mongo import mongo
from app.domain.types import Event, User, UserSettings


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _coerce_float(v: object) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).strip())
    except Exception:
        return None


_log = logging.getLogger("app")


class UsersRepo:
    def _repair_user_document(self, raw: dict[str, Any]) -> User:
        """Best-effort repair for legacy or partially-invalid Mongo user documents."""
        tid = int(raw["telegram_id"])
        try:
            st = UserSettings.model_validate(raw.get("settings") or {})
        except ValidationError:
            st = UserSettings()
        created = raw.get("created_at")
        if not isinstance(created, datetime):
            created = _now()
        try:
            mg = int(raw.get("martingale_step") or 0)
        except Exception:
            mg = 0
        mg = max(0, min(mg, 999))
        u_raw, f_raw = raw.get("username"), raw.get("first_name")
        username_val = None if u_raw is None else str(u_raw)
        first_val = None if f_raw is None else str(f_raw)
        return User(
            telegram_id=tid,
            username=username_val,
            first_name=first_val,
            created_at=created,
            blocked=bool(raw.get("blocked", False)),
            settings=st,
            martingale_step=mg,
            po_real_balance_usd=_coerce_float(raw.get("po_real_balance_usd")),
            po_demo_balance_usd=_coerce_float(raw.get("po_demo_balance_usd")),
            po_real_balance_updated_at=raw.get("po_real_balance_updated_at")
            if isinstance(raw.get("po_real_balance_updated_at"), datetime)
            else None,
        )

    async def _user_from_doc(self, doc: dict[str, Any]) -> User:
        try:
            return User.model_validate(doc)
        except ValidationError:
            user = self._repair_user_document(doc)
            await mongo.db.users.replace_one({"telegram_id": user.telegram_id}, user.model_dump())
            _log.warning("repaired invalid users document telegram_id=%s", user.telegram_id)
            return user

    async def ensure_user(self, telegram_id: int, username: str | None, first_name: str | None) -> User:
        doc = await mongo.db.users.find_one({"telegram_id": telegram_id})
        if doc is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                created_at=_now(),
                blocked=False,
                settings=UserSettings(),
            )
            await mongo.db.users.insert_one(user.model_dump())
            await self._event(
                "user_created",
                telegram_id,
                {"username": username, "first_name": first_name},
            )
            return user

        if doc.get("username") != username or doc.get("first_name") != first_name:
            await mongo.db.users.update_one(
                {"telegram_id": telegram_id},
                {"$set": {"username": username, "first_name": first_name}},
            )
            await self._event("user_updated", telegram_id, {"username": username, "first_name": first_name})
            doc = await mongo.db.users.find_one({"telegram_id": telegram_id})
            if doc is None:
                raise RuntimeError(f"user row missing after profile update telegram_id={telegram_id}")

        return await self._user_from_doc(doc)

    async def get_user(self, telegram_id: int) -> User | None:
        doc = await mongo.db.users.find_one({"telegram_id": telegram_id})
        if doc is None:
            return None
        return await self._user_from_doc(doc)

    async def set_blocked(self, telegram_id: int, blocked: bool) -> bool:
        res = await mongo.db.users.update_one({"telegram_id": telegram_id}, {"$set": {"blocked": blocked}})
        if res.matched_count == 0:
            return False
        await self._event("user_blocked" if blocked else "user_unblocked", telegram_id, {})
        return True

    async def update_settings(self, telegram_id: int, patch: dict[str, Any]) -> User | None:
        user = await self.get_user(telegram_id)
        if user is None:
            return None
        settings = user.settings.model_copy(update=patch)
        await mongo.db.users.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"settings": settings.model_dump()}},
        )
        await self._event("settings_updated", telegram_id, patch)
        return await self.get_user(telegram_id)

    async def set_martingale_step(self, telegram_id: int, step: int) -> None:
        step = max(0, int(step))
        await mongo.db.users.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"martingale_step": step}},
        )

    async def set_trading_enabled(self, telegram_id: int, enabled: bool) -> bool:
        res = await mongo.db.users.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"settings.trading_enabled": enabled}},
        )
        if res.matched_count == 0:
            return False
        await self._event("trading_enabled" if enabled else "trading_disabled", telegram_id, {})
        return True

    async def list_users(self, limit: int = 50) -> list[User]:
        cur = mongo.db.users.find({}, sort=[("created_at", -1)], limit=limit)
        docs = await cur.to_list(length=limit)
        out: list[User] = []
        for d in docs:
            if not isinstance(d, dict):
                continue
            try:
                out.append(await self._user_from_doc(d))
            except Exception:
                continue
        return out

    async def update_po_balance_cache(
        self,
        telegram_id: int,
        *,
        real_usd: float | None,
        demo_usd: float | None,
    ) -> None:
        await mongo.db.users.update_one(
            {"telegram_id": int(telegram_id)},
            {
                "$set": {
                    "po_real_balance_usd": real_usd,
                    "po_demo_balance_usd": demo_usd,
                    "po_real_balance_updated_at": _now(),
                }
            },
        )

    async def merge_po_balance_cache(
        self,
        telegram_id: int,
        *,
        real_usd: float | None = None,
        demo_usd: float | None = None,
    ) -> None:
        """Update only balance fields that are not None (keeps the other side intact)."""
        u = await self.get_user(telegram_id)
        r = real_usd if real_usd is not None else (u.po_real_balance_usd if u else None)
        d = demo_usd if demo_usd is not None else (u.po_demo_balance_usd if u else None)
        await self.update_po_balance_cache(telegram_id, real_usd=r, demo_usd=d)

    async def list_telegram_ids(self, *, include_blocked: bool = False) -> list[int]:
        q: dict[str, Any] = {}
        if not include_blocked:
            q["blocked"] = False
        cur = mongo.db.users.find(q, projection={"_id": 0, "telegram_id": 1})
        docs = await cur.to_list(length=None)
        out: list[int] = []
        for d in docs:
            try:
                out.append(int(d.get("telegram_id")))
            except Exception:
                continue
        return out

    async def _event(self, type_: str, telegram_id: int, payload: dict[str, Any]) -> None:
        event = Event(type=type_, telegram_id=telegram_id, created_at=_now(), payload=payload)
        await mongo.db.events.insert_one(event.model_dump())


users_repo = UsersRepo()

