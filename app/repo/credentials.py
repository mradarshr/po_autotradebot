from __future__ import annotations

from datetime import datetime, timezone

from app.config import get_settings
from app.db.mongo import mongo
from app.observability.log import log_warning
from app.security.crypto import decrypt_text, encrypt_text


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CredentialsRepo:
    async def set_credentials(self, telegram_id: int, email: str, password: str) -> None:
        settings = get_settings()
        master_key = settings.require_master_key()
        doc = {
            "telegram_id": telegram_id,
            "email": email,
            "password_enc": encrypt_text(master_key, password),
            "updated_at": _now(),
        }
        await mongo.db.credentials.update_one({"telegram_id": telegram_id}, {"$set": doc}, upsert=True)

    async def delete_credentials(self, telegram_id: int) -> None:
        await mongo.db.credentials.delete_one({"telegram_id": telegram_id})
        await mongo.db.sessions.delete_one({"telegram_id": telegram_id})

    async def has_credentials(self, telegram_id: int) -> bool:
        doc = await mongo.db.credentials.find_one({"telegram_id": int(telegram_id)}, projection={"_id": 1})
        return doc is not None

    async def get_credentials(self, telegram_id: int) -> tuple[str, str] | None:
        doc = await mongo.db.credentials.find_one({"telegram_id": telegram_id})
        if doc is None:
            return None
        try:
            settings = get_settings()
            master_key = settings.require_master_key()
            email = str(doc.get("email") or "")
            enc = str(doc.get("password_enc") or "")
            if not email or not enc:
                return None
            password = decrypt_text(master_key, enc)
            if not password:
                return None
            return email, password
        except Exception as exc:
            log_warning(
                "credentials_load_failed",
                telegram_id=int(telegram_id),
                exc=type(exc).__name__,
                hint="check MASTER_KEY matches the key used when credentials were saved",
            )
            return None

    async def save_session(self, telegram_id: int, cookies: dict[str, str], headers: dict[str, str]) -> None:
        doc = {"telegram_id": telegram_id, "cookies": cookies, "headers": headers, "updated_at": _now()}
        await mongo.db.sessions.update_one({"telegram_id": telegram_id}, {"$set": doc}, upsert=True)

    async def first_telegram_id_with_credentials(self) -> int | None:
        doc = await mongo.db.credentials.find_one({}, projection={"_id": 0, "telegram_id": 1})
        if doc is None:
            return None
        try:
            return int(doc.get("telegram_id"))
        except Exception:
            return None

    async def get_session(self, telegram_id: int) -> tuple[dict[str, str], dict[str, str]] | None:
        doc = await mongo.db.sessions.find_one({"telegram_id": telegram_id})
        if doc is None:
            return None
        cookies = doc.get("cookies") or {}
        headers = doc.get("headers") or {}
        if not isinstance(cookies, dict) or not isinstance(headers, dict):
            return None
        return {str(k): str(v) for k, v in cookies.items()}, {str(k): str(v) for k, v in headers.items()}


credentials_repo = CredentialsRepo()

