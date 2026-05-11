from __future__ import annotations

from dataclasses import dataclass, field

import aiohttp

from app.config import get_settings


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    """Cookies set by the server (merged into subsequent requests by the client)."""
    response_cookies: dict[str, str] = field(default_factory=dict)


class HttpClient:
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        if self._session is not None:
            return
        total = float(get_settings().po_http_timeout_seconds)
        total = max(5.0, min(120.0, total))
        connect = min(30.0, max(5.0, total * 0.35))
        timeout = aiohttp.ClientTimeout(total=total, connect=connect, sock_connect=connect)
        self._session = aiohttp.ClientSession(timeout=timeout)

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
        self._session = None

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict | None = None,
        data: dict | None = None,
        cookies: dict[str, str] | None = None,
    ) -> HttpResponse:
        if self._session is None:
            raise RuntimeError("http client not started")
        merged: dict[str, str] = {}
        ua = (get_settings().po_http_user_agent or "").strip()
        if ua:
            merged["User-Agent"] = ua
        if headers:
            merged.update(headers)

        async with self._session.request(
            method,
            url,
            headers=merged or None,
            json=json,
            data=data,
            cookies=cookies,
        ) as resp:
            body = await resp.read()
            response_cookies: dict[str, str] = {}
            try:
                for key, morsel in resp.cookies.items():
                    response_cookies[str(key)] = str(morsel.value)
            except Exception:
                pass
            return HttpResponse(
                status=resp.status,
                headers=dict(resp.headers),
                body=body,
                response_cookies=response_cookies,
            )

