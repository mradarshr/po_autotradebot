from __future__ import annotations

import hashlib
import hmac

import pytest
from fastapi import HTTPException

from app.domain.execution import WebhookSignalIn
from app.web.webhook_guard import parse_webhook_json, verify_webhook_hmac_sha256


def test_webhook_signal_normalizes_and_validates_payload() -> None:
    s = WebhookSignalIn.model_validate(
        {
            "signal_id": "sig-001",
            "symbol": " EURUSD ",
            "direction": "UP",
            "payload": {"stake": 10.5, "expiry_seconds": 30},
        }
    )
    assert s.symbol == "eurusd"
    assert s.direction == "UP"
    assert s.payload["stake"] == 10.5


def test_webhook_signal_rejects_non_object_payload() -> None:
    with pytest.raises(ValueError):
        WebhookSignalIn.model_validate(
            {
                "signal_id": "x",
                "symbol": "eurusd",
                "direction": "DOWN",
                "payload": [],
            }
        )


def test_parse_webhook_json_accepts_object() -> None:
    assert parse_webhook_json(b' {"a": 1} ') == {"a": 1}


def test_parse_webhook_json_rejects_empty() -> None:
    with pytest.raises(HTTPException) as ei:
        parse_webhook_json(b"   ")
    assert ei.value.status_code == 400


def test_parse_webhook_json_rejects_non_object() -> None:
    with pytest.raises(HTTPException) as ei:
        parse_webhook_json(b"[1,2,3]")
    assert ei.value.status_code == 400


def test_hmac_signature_roundtrip() -> None:
    secret = "test-secret"
    body = b'{"signal_id":"1","symbol":"eurusd","direction":"UP"}'
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    assert verify_webhook_hmac_sha256(
        secret=secret, body=body, signature_header=f"sha256={digest}"
    )
    assert verify_webhook_hmac_sha256(secret=secret, body=body, signature_header=digest)


def test_observability_log_event_does_not_raise() -> None:
    from app.observability.log import log_event, log_warning

    log_event("smoke.test", foo="bar", n=1)
    log_warning("smoke.warn", x=True)


def test_detect_email_confirmation_event_label() -> None:
    from app.services.affiliate_email import detect_email_confirmation

    pats = ["email confirmation", "email_confirmation"]
    assert detect_email_confirmation("Email Confirmation", {}, pats)
    assert detect_email_confirmation("foo_email_confirmation_bar", {}, pats)
    assert not detect_email_confirmation("registration", {}, pats)


def test_detect_email_confirmation_payload_flags() -> None:
    from app.services.affiliate_email import detect_email_confirmation

    assert detect_email_confirmation("", {"email_confirmed": True}, [])
    assert detect_email_confirmation("", {"email_verified": "yes"}, [])
    assert not detect_email_confirmation("", {"email_confirmed": False}, [])


def test_trade_martingale_step_at_open_defaults() -> None:
    from datetime import datetime, timezone

    from app.domain.execution import Trade

    t = Trade(
        trade_id="tid",
        telegram_id=1,
        symbol="eurusd_otc",
        direction="UP",
        stake=1.0,
        expiry_seconds=60,
        status="opened",
        signal_source="x",
        signal_id="sig",
        created_at=datetime.now(timezone.utc),
    )
    assert t.martingale_step_at_open == 0


def test_signal_ingest_mode_gates() -> None:
    from app.repo.system import (
        normalize_signal_ingest_mode,
        strategy_ingest_allowed,
        webhook_ingest_allowed,
    )

    assert normalize_signal_ingest_mode(None) == "all"
    assert normalize_signal_ingest_mode("bogus") == "all"
    assert normalize_signal_ingest_mode("admin_only") == "admin_only"
    assert webhook_ingest_allowed("all")
    assert webhook_ingest_allowed("webhook_only")
    assert not webhook_ingest_allowed("strategy_only")
    assert not webhook_ingest_allowed("admin_only")
    assert strategy_ingest_allowed("all")
    assert strategy_ingest_allowed("strategy_only")
    assert not strategy_ingest_allowed("webhook_only")
    assert not strategy_ingest_allowed("admin_only")


def test_is_tradable_otc_only(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services import assets as assets_mod

    class S:
        trade_otc_only = True
        po_otc_assets_db_enabled = False
        optional_po_asset_map_json = staticmethod(
            lambda: '{"good":{"id":"1","otc":true,"payout":92},"bad":{"id":"2","otc":false,"payout":92},"bare":"3"}'
        )

    monkeypatch.setattr(assets_mod, "get_settings", lambda: S())
    cat = assets_mod.AssetCatalog()
    assert cat.is_tradable("good", min_payout_percent=90.0, require_otc=True)[0]
    assert cat.is_tradable("good", min_payout_percent=93.0, require_otc=True) == (False, "payout_below_threshold")
    assert cat.is_tradable("bad", min_payout_percent=90.0, require_otc=True) == (False, "not_otc")
    assert cat.is_tradable("bare", min_payout_percent=None, require_otc=True) == (False, "otc_unknown")


def test_deposit_token_brackets() -> None:
    from types import SimpleNamespace

    from app.services.token_deposit import deposit_tokens_for_amount

    s = SimpleNamespace(
        token_deposit_min_usd=20.0,
        token_bracket_low_grant=15,
        token_bracket_high_min_usd=100.0,
        token_bracket_high_per_dollar=1.0,
    )
    assert deposit_tokens_for_amount(19, s) == 0
    assert deposit_tokens_for_amount(50, s) == 15
    assert deposit_tokens_for_amount(99, s) == 15
    assert deposit_tokens_for_amount(100, s) == 100
    assert deposit_tokens_for_amount(150, s) == 150


def test_martingale_multipliers_and_stake() -> None:
    from datetime import datetime, timezone

    from app.domain.types import User, UserSettings
    from app.services.martingale import effective_stake_for_step, multipliers_list, stake_for_trade

    st = UserSettings(
        stake=10.0,
        martingale_enabled=True,
        martingale_max_levels=7,
        martingale_multipliers_csv="1,2,3",
    )
    assert multipliers_list(st)[:3] == [1.0, 2.0, 3.0]
    assert effective_stake_for_step(10.0, 0, st) == 10.0
    assert effective_stake_for_step(10.0, 5, st) >= 10.0  # capped index uses last mult * padding

    u = User(
        telegram_id=1,
        created_at=datetime.now(timezone.utc),
        martingale_step=2,
        settings=st,
    )
    assert stake_for_trade(u) == 30.0


def test_extract_real_demo_nested_live_practice_keys() -> None:
    from app.services.po_balance_parse import extract_real_demo_usd

    payload = {"nested": {"userWallet": {"liveBalance": 77.25, "practiceBalance": 10000.0}}}
    r, d = extract_real_demo_usd(payload)
    assert r == 77.25
    assert d == 10000.0


def test_cabinet_body_parses_next_data_balances() -> None:
    from app.services.po_cabinet_parse import extract_balances_and_uid_from_cabinet_body

    html = (
        '<script id="__NEXT_DATA__" type="application/json">'
        '{"demo_balance":1000.5,"real_balance":42}'
        "</script>"
    )
    r, d, _uid = extract_balances_and_uid_from_cabinet_body(html.encode())
    assert r == 42.0
    assert d == 1000.5


def test_cabinet_raw_json_live_practice_regex() -> None:
    from app.services.po_cabinet_parse import extract_balances_and_uid_from_cabinet_body

    raw = '{"x":1,"liveBalance":12.5,"practiceBalance":888}'
    r, d, _u = extract_balances_and_uid_from_cabinet_body(raw.encode())
    assert r == 12.5
    assert d == 888.0


def test_reject_public_pocketoption_website_login_url() -> None:
    from app.config import Settings
    from app.integrations.pocketoption.client import _reject_public_website_login_url

    assert Settings.model_fields["po_allow_public_web_login"].default is True

    s = Settings(po_allow_public_web_login=False)
    with pytest.raises(ValueError, match="JSON login API"):
        _reject_public_website_login_url("https://pocketoption.com/en/login", s)
    s_opt = Settings(po_allow_public_web_login=True)
    _reject_public_website_login_url("https://pocketoption.com/en/login", s_opt)
    # Real API-style hosts should not raise
    _reject_public_website_login_url("https://api.example.com/v1/auth/login", s)
