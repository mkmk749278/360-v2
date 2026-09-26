"""The request bodies the Lumin app sends to money-write routes — engine side.

The app pins what it WRITES in ``lumin-app/test/data/money_write_contract_test.dart``
with these same field sets. Neither repo's CI can see the other, so each side
pins the shared vector against its own code: renaming a field here fails this
file, renaming it in the app fails that one, and a drift between the two
literals is a diff a reviewer reads (2026-09-26 test-suite audit).

Why these routes: ``PUT /api/settings/user/auto-trade`` reads its body with
``model_dump(exclude_unset=True)``, so a key the model does not declare is
dropped SILENTLY — the ``exit_mechanism`` scaffold (CLAUDE.md, 2026-08-10) —
and the take / close / manual-trade bodies are pydantic models, where a rename
is a 422 on a live order.
"""
from __future__ import annotations

from src.api.close_position_route import ClosePositionRequest
from src.api.manual_trade_route import ManualTradeRequest
from src.api.schemas import AutoModeChangeRequest, AutoTradeSettings
from src.api.take_signal_route import TakeSignalRequest

#: Keys the app can send on the per-user settings PUT (its ``toJsonPartial``).
APP_AUTO_TRADE_SETTINGS_KEYS = {
    "leverage_cap",
    "max_concurrent_positions",
    "mode",
    "notional_usd",
    "paper_path_preference",
    "paper_regime_preference",
    "paper_symbol_preference",
    "path_preference",
    "position_size_pct",
    "regime_preference",
    "symbol_preference",
}

#: Set from ops, never from the app — the one engine field the app lacks.
OPS_ONLY_AUTO_TRADE_SETTINGS_KEYS = {"exit_mechanism"}

APP_MANUAL_TRADE_KEYS = {
    "ref_id", "symbol", "direction", "entry_type", "entry_price",
    "sl_price", "tp_prices", "valid_for_minutes",
}


def test_every_settings_key_the_app_sends_is_declared() -> None:
    declared = set(AutoTradeSettings.model_fields)
    assert APP_AUTO_TRADE_SETTINGS_KEYS <= declared, (
        "the app sends a key this model does not declare — exclude_unset drops "
        f"it without a word: {sorted(APP_AUTO_TRADE_SETTINGS_KEYS - declared)}"
    )
    assert declared == APP_AUTO_TRADE_SETTINGS_KEYS | OPS_ONLY_AUTO_TRADE_SETTINGS_KEYS, (
        "a new settings field: add it to the app's toJsonPartial (and its "
        "contract test), or to OPS_ONLY_AUTO_TRADE_SETTINGS_KEYS with a reason"
    )


def test_an_untouched_field_is_not_a_clear() -> None:
    """The app omits untouched pickers; the engine must read an omitted key as
    'leave it', and an explicit null as 'clear it'. Both halves are what make
    a mode-only save safe for the user's symbol filter."""
    only_mode = AutoTradeSettings.model_validate({"mode": "paper"})
    assert only_mode.model_dump(exclude_unset=True) == {"mode": "paper"}
    cleared = AutoTradeSettings.model_validate({"symbol_preference": None})
    assert cleared.model_dump(exclude_unset=True) == {"symbol_preference": None}


def test_the_manual_trade_body_matches_the_app() -> None:
    assert set(ManualTradeRequest.model_fields) == APP_MANUAL_TRADE_KEYS
    req = ManualTradeRequest.model_validate({
        "ref_id": "alert-1", "symbol": "ETHUSDT", "direction": "SHORT",
        "entry_type": "limit", "entry_price": 2500.5, "sl_price": 2550.0,
        "tp_prices": [2450.0, 2400.0], "valid_for_minutes": 30,
    })
    assert req.tp_prices == [2450.0, 2400.0]


def test_take_close_and_auto_mode_bodies() -> None:
    assert set(TakeSignalRequest.model_fields) == {"signal_id"}
    assert set(ClosePositionRequest.model_fields) == {"signal_id"}
    assert set(AutoModeChangeRequest.model_fields) == {"mode"}
