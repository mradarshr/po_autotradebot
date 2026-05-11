from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import quote, urlparse

from app.config import Settings, get_settings
from app.integrations.pocketoption.errors import PocketOptionHttpError
from app.integrations.pocketoption.http import HttpClient
from app.integrations.pocketoption.jsonpath import get_by_dotted_path


def _authorization_from_login_json(body: bytes, settings: Settings) -> dict[str, str]:
    """
    Many gateways return JWT / session id in JSON (not only Set-Cookie). Map that to
    Authorization so GET profile/balance can authenticate.
    """
    try:
        data = json.loads(body.decode("utf-8") or "{}")
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}

    token: str | None = None
    path = settings.po_login_token_json_path.strip()
    if path:
        raw = get_by_dotted_path(data, path)
        if raw is not None and str(raw).strip():
            token = str(raw).strip()
    else:
        for key in ("access_token", "accessToken", "token", "auth_token", "jwt", "id_token"):
            v = data.get(key)
            if isinstance(v, str) and v.strip():
                token = v.strip()
                break
        if not token:
            for nest in ("data", "result", "user", "auth", "account"):
                sub = data.get(nest)
                if isinstance(sub, dict):
                    for key in ("access_token", "accessToken", "token", "jwt"):
                        v = sub.get(key)
                        if isinstance(v, str) and v.strip():
                            token = v.strip()
                            break
                if token:
                    break

    if not token:
        return {}

    low = token.lower()
    if low.startswith("bearer ") or low.startswith("basic "):
        return {"Authorization": token}

    prefix = settings.po_login_authorization_prefix
    if prefix is None:
        prefix = "Bearer "
    pfx = str(prefix)
    if not pfx.strip():
        return {"Authorization": token}
    sep = "" if pfx.endswith(" ") else " "
    return {"Authorization": f"{pfx}{sep}{token}"}


def _reject_public_website_login_url(url: str, settings: Settings) -> None:
    """
    Block accidental use of the marketing / SPA login URL (e.g. https://pocketoption.com/en/login).
    That endpoint serves HTML for browsers; server-side POSTs from Heroku often time out or are blocked.
    The bot needs a JSON API base from your integration or proxy, not the public site.
    """
    if settings.po_allow_public_web_login:
        return
    try:
        parsed = urlparse(url)
    except Exception:
        return
    host = (parsed.netloc or "").lower()
    if "@" in host:
        host = host.rsplit("@", 1)[-1]
    if ":" in host:
        host = host.split(":", 1)[0]
    path = (parsed.path or "").lower()

    if host.endswith("pocketoption.com") and not host.startswith("api."):
        # Typical mistaken config: website locale login, not REST.
        if "/en/login" in path or path.rstrip("/") in ("/login", "/en/login", "/signin"):
            raise ValueError(
                "PO_API_BASE_URL + PO_LOGIN_PATH must point to a JSON login API, not the public "
                f"website page ({url}). Use the API host from your broker/gateway docs (or your own proxy), "
                "not https://pocketoption.com/.../login — that URL is for browsers and usually fails from servers."
            )
        if "/en/" in path and path.endswith("/login"):
            raise ValueError(
                "PO_API_BASE_URL + PO_LOGIN_PATH look like a public locale login path, not an API. "
                f"Full URL was: {url}. Set an API base (e.g. https://api…/v1) and login path from your integration."
            )


@dataclass(frozen=True)
class PocketOptionSession:
    cookies: dict[str, str]
    headers: dict[str, str]


class PocketOptionClient:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def _url(self, path: str) -> str:
        settings = get_settings()
        base = settings.po_api_base_url.rstrip("/")
        p = path.strip()
        if not base or not p:
            raise ValueError("pocketoption api base url and paths must be configured")
        if not p.startswith("/"):
            p = "/" + p
        return base + p

    async def login(self, email: str, password: str) -> PocketOptionSession:
        settings = get_settings()
        url = self._url(settings.po_login_path)
        _reject_public_website_login_url(url, settings)
        login_json: dict[str, Any] = {
            (settings.po_login_email_field.strip() or "email"): email,
            (settings.po_login_password_field.strip() or "password"): password,
        }
        extra_raw = settings.po_login_body_extra_json.strip()
        if extra_raw:
            try:
                extra = json.loads(extra_raw)
                if isinstance(extra, dict):
                    login_json = {**extra, **login_json}
            except Exception:
                pass
        resp = await self._http.request("POST", url, json=login_json)
        if resp.status < 200 or resp.status >= 300:
            raise PocketOptionHttpError(op="login", status=resp.status, body=resp.body)
        cookies: dict[str, str] = dict(resp.response_cookies)
        if not cookies:
            set_cookie = resp.headers.get("Set-Cookie")
            if set_cookie:
                parts = set_cookie.split(";")
                if parts and "=" in parts[0]:
                    k, v = parts[0].split("=", 1)
                    cookies[k.strip()] = v.strip()
        headers: dict[str, str] = {"Content-Type": "application/json"}
        headers.update(_authorization_from_login_json(resp.body, settings))
        return PocketOptionSession(cookies=cookies, headers=headers)

    async def profile(self, session: PocketOptionSession) -> dict[str, Any]:
        settings = get_settings()
        url = self._url(settings.po_profile_path)
        resp = await self._http.request("GET", url, headers=session.headers, cookies=session.cookies)
        if resp.status < 200 or resp.status >= 300:
            raise PocketOptionHttpError(op="profile", status=resp.status, body=resp.body)
        return json.loads(resp.body.decode("utf-8") or "{}")

    async def cabinet_get(self, session: PocketOptionSession) -> bytes:
        """GET cabinet page (HTML or JSON) for embedded balance / uid data."""
        settings = get_settings()
        path = settings.po_cabinet_path.strip()
        if not path:
            return b""
        url = self._url(path)
        hdrs = dict(session.headers)
        hdrs.setdefault("Accept", "text/html,application/json;q=0.9,*/*;q=0.8")
        resp = await self._http.request("GET", url, headers=hdrs, cookies=session.cookies)
        if resp.status < 200 or resp.status >= 300:
            raise PocketOptionHttpError(op="cabinet", status=resp.status, body=resp.body)
        return resp.body

    async def balance(self, session: PocketOptionSession) -> dict[str, Any]:
        settings = get_settings()
        path = settings.po_balance_path.strip()
        if not path:
            # No dedicated balance route — callers may use profile payload instead.
            return {}
        url = self._url(path)
        resp = await self._http.request("GET", url, headers=session.headers, cookies=session.cookies)
        if resp.status < 200 or resp.status >= 300:
            raise PocketOptionHttpError(op="balance", status=resp.status, body=resp.body)
        return json.loads(resp.body.decode("utf-8") or "{}")

    async def place_trade(
        self,
        session: PocketOptionSession,
        *,
        asset_id: str,
        amount: float,
        direction: Literal["UP", "DOWN"],
        expiry_seconds: int,
    ) -> tuple[dict[str, Any], str | None]:
        settings = get_settings()
        path = settings.po_place_trade_path.strip()
        if not path:
            raise ValueError("PO_PLACE_TRADE_PATH is not configured")

        dir_val = (
            settings.po_trade_direction_up if direction == "UP" else settings.po_trade_direction_down
        )
        body: dict[str, Any] = {
            settings.po_trade_field_asset_id.strip() or "asset_id": asset_id,
            settings.po_trade_field_amount.strip() or "amount": amount,
            settings.po_trade_field_direction.strip() or "direction": dir_val,
            settings.po_trade_field_expiry.strip() or "expiry_seconds": int(expiry_seconds),
        }

        extra_raw = settings.po_trade_body_extra_json.strip()
        if extra_raw:
            try:
                extra = json.loads(extra_raw)
                if isinstance(extra, dict):
                    body = {**extra, **body}
            except Exception:
                pass

        url = self._url(path)
        resp = await self._http.request("POST", url, headers=session.headers, cookies=session.cookies, json=body)
        parsed: dict[str, Any]
        try:
            parsed = json.loads(resp.body.decode("utf-8") or "{}")
        except Exception:
            parsed = {}

        if resp.status < 200 or resp.status >= 300:
            raise PocketOptionHttpError(op="place_trade", status=resp.status, body=resp.body)

        broker_id: str | None = None
        id_path = settings.po_trade_response_broker_id_path.strip()
        if id_path:
            raw = get_by_dotted_path(parsed, id_path)
            if raw is not None and str(raw).strip():
                broker_id = str(raw).strip()

        return parsed, broker_id

    async def trade_result(self, session: PocketOptionSession, broker_trade_id: str) -> dict[str, Any]:
        settings = get_settings()
        tmpl = settings.po_trade_result_path_template.strip()
        if not tmpl or "{id}" not in tmpl:
            raise ValueError("PO_TRADE_RESULT_PATH_TEMPLATE must contain {id}")
        safe_id = quote(str(broker_trade_id), safe="")
        path = tmpl.replace("{id}", safe_id)
        url = self._url(path)
        method = (settings.po_trade_result_http_method or "GET").strip().upper()
        if method == "POST":
            body = None
            post_raw = settings.po_trade_result_post_json.strip()
            if post_raw:
                try:
                    body = json.loads(post_raw.replace("{id}", safe_id))
                except Exception:
                    body = None
            resp = await self._http.request(
                "POST", url, headers=session.headers, cookies=session.cookies, json=body
            )
        else:
            resp = await self._http.request("GET", url, headers=session.headers, cookies=session.cookies)
        try:
            parsed = json.loads(resp.body.decode("utf-8") or "{}")
        except Exception:
            parsed = {}
        if resp.status < 200 or resp.status >= 300:
            raise PocketOptionHttpError(op="trade_result", status=resp.status, body=resp.body)
        if not isinstance(parsed, dict):
            return {}
        return parsed

    async def fetch_assets_list(self, session: PocketOptionSession) -> Any:
        """
        GET configured assets/instruments list (shape varies by PO gateway).
        Set PO_ASSETS_LIST_PATH in env, e.g. /api/v1/cabinet/assets
        """
        settings = get_settings()
        path = settings.po_assets_list_path.strip()
        if not path:
            raise ValueError("PO_ASSETS_LIST_PATH is not configured")
        url = self._url(path)
        resp = await self._http.request("GET", url, headers=session.headers, cookies=session.cookies)
        if resp.status < 200 or resp.status >= 300:
            raise PocketOptionHttpError(op="assets_list", status=resp.status, body=resp.body)
        try:
            return json.loads(resp.body.decode("utf-8") or "null")
        except Exception:
            return None

