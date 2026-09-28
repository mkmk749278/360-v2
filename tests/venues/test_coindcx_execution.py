"""CoinDCX execution + reconciler — every invariant in execution.py's
docstring gets a test that fails if the invariant is removed.

The fake exchange answers in CoinDCX's documented shapes
(fixtures/coindcx/private_doc_examples.json): positions carry ``active_pos``
/ ``stop_loss_trigger`` / ``take_profit_trigger``; ``create_tpsl`` answers
per leg with an order or ``{"success": false, "error": ...}``.
"""
from __future__ import annotations

from tests.venues.conftest import DCX

import time
from typing import Any, Dict, List, Optional

import pytest

from src.venues.coindcx import client as C
from src.venues.coindcx import execution as E
from src.venues.coindcx import instruments as I
from src.venues.coindcx import positions as P
from src.venues.coindcx import reconciler as R

BTC = I.Instrument(
    pair="B-BTC_USDT", symbol="BTCUSDT", status="active", price_increment=0.1,
    quantity_increment=0.001, min_quantity=0.001, max_quantity=950,
    max_market_order_quantity=120, min_notional=60.0, max_leverage_long=20,
    max_leverage_short=20, exit_only=False,
    order_types=("market_order", "limit_order", "stop_market", "take_profit_market"),
)


class FakeRegistry:
    def __init__(self, price: float = 100_000.0, instrument=BTC) -> None:
        self.price = price
        self.inst = instrument

    async def instrument(self, symbol):
        return self.inst

    async def last_price(self, symbol):
        return self.price

    async def inr_per_usdt(self):
        return 102.0


class FakeExchange:
    """One user's CoinDCX futures account, in memory."""

    def __init__(self) -> None:
        self.pos: Dict[tuple, Dict[str, Any]] = {}
        self.order_log: List[Dict[str, Any]] = []
        self.calls: List[str] = []
        self.fill = True
        self.sl_refusals = 0            # create_tpsl refuses the stop this many times
        self.exit_raises = False
        self.order_raise: Optional[BaseException] = None
        self.liquidation = 0.0
        self.pending_not_flat = False

    def _row(self, pair, ccy):
        return self.pos.setdefault((pair, ccy), {
            "id": f"pos-{pair}-{ccy}", "pair": pair, "active_pos": 0.0,
            "inactive_pos_buy": 0.0, "inactive_pos_sell": 0.0, "avg_price": 0.0,
            "liquidation_price": 0.0, "take_profit_trigger": None, "stop_loss_trigger": None,
            "margin_currency_short_name": ccy, "settlement_currency_avg_price": 102.0,
        })

    # CoinDCXClient surface
    async def positions(self, *, pairs=None, margin_currencies=("USDT", "INR"), size=100):
        self.calls.append("positions")
        return [dict(r) for (pair, ccy), r in self.pos.items()
                if (not pairs or pair in pairs) and ccy in margin_currencies]

    async def update_leverage(self, *, pair, leverage, margin_currency):
        self.calls.append(f"leverage:{leverage}")

    async def market_order(self, *, pair, side, quantity, leverage, margin_currency):
        self.calls.append(f"order:{side}:{quantity}")
        if self.order_raise:
            raise self.order_raise
        oid = f"ord{len(self.order_log)}"
        self.order_log.append({"id": oid, "pair": pair, "side": side, "status": "filled",
                            "stage": "default", "avg_price": 100_000.0, "fee_amount": 0.05,
                            "margin_currency_short_name": margin_currency,
                            "updated_at": time.time() * 1000})
        if self.fill:
            r = self._row(pair, margin_currency)
            q = float(quantity)
            r["active_pos"] = q if side == "buy" else -q
            r["avg_price"] = 100_000.0
            r["liquidation_price"] = self.liquidation
        return {"id": oid, "status": "initial"}

    async def cancel_order(self, *, order_id):
        self.calls.append("cancel")

    async def create_tpsl(self, *, position_id, stop_price, take_profit_price):
        self.calls.append("tpsl")
        row = next(r for r in self.pos.values() if r["id"] == position_id)
        out: Dict[str, Any] = {}
        if self.sl_refusals > 0:
            self.sl_refusals -= 1
            out["stop_loss"] = {"success": False, "error": "Price out of range"}
        else:
            row["stop_loss_trigger"] = float(stop_price)
            out["stop_loss"] = {"id": "sl1", "stage": "tpsl_exit", "status": "untriggered"}
        if take_profit_price:
            row["take_profit_trigger"] = float(take_profit_price)
            out["take_profit"] = {"id": "tp1", "stage": "tpsl_exit", "status": "untriggered"}
        return out

    async def exit_position(self, *, position_id):
        self.calls.append("exit")
        if self.exit_raises:
            raise C.CoinDCXRejected("no", status=400, body={"message": "no"})
        row = next(r for r in self.pos.values() if r["id"] == position_id)
        side = "sell" if row["active_pos"] > 0 else "buy"
        row["active_pos"] = 0.0
        self.order_log.append({"id": f"ex{len(self.order_log)}", "pair": row["pair"], "side": side,
                            "status": "filled", "stage": "exit", "avg_price": 100_500.0,
                            "fee_amount": 0.06, "margin_currency_short_name": row["margin_currency_short_name"],
                            "updated_at": time.time() * 1000 + 10})
        return {"message": "success"}

    def trigger(self, which: str) -> None:
        """The exchange fires the stop or the target on its own."""
        row = next(r for r in self.pos.values() if r["active_pos"] != 0)
        px = row["stop_loss_trigger"] if which == "sl" else row["take_profit_trigger"]
        side = "sell" if row["active_pos"] > 0 else "buy"
        row["active_pos"] = 0.0
        self.order_log.append({"id": f"t{len(self.order_log)}", "pair": row["pair"], "side": side,
                            "status": "filled", "stage": "tpsl_exit", "stop_price": px,
                            "avg_price": px, "fee_amount": 0.06,
                            "margin_currency_short_name": row["margin_currency_short_name"],
                            "updated_at": time.time() * 1000 + 10})

    async def orders(self, *, statuses, side, margin_currencies=("USDT", "INR"), size=50):
        self.calls.append("orders")
        return [o for o in self.order_log if o["side"] == side]

    async def cancel_all_for_position(self, *, position_id):
        self.calls.append("cancel_all")


async def _nosleep(_s):
    return None


@pytest.fixture()
def env(monkeypatch):
    accounts: Dict[str, FakeExchange] = {}

    def account(uid: str) -> FakeExchange:
        return accounts.setdefault(uid, FakeExchange())

    fx = account("u1")
    store = P.CoinDCXPositionStore(":memory:")
    reg = FakeRegistry()
    ex = E.CoinDCXExecutor(store=store, registry=reg, client_factory=account,
                           sleep=_nosleep, fill_wait_s=1.0)
    ex.accounts = accounts  # type: ignore[attr-defined]
    monkeypatch.setattr(E, "_record_breaker", lambda uid, exc: None)
    return fx, store, reg, ex


def _open_kwargs(**over):
    kw = dict(uid="u1", signal_id="S1", symbol="BTCUSDT", direction="LONG",
              entry=100_000.0, sl=98_000.0, tp1=103_000.0, notional_usdt=100.0,
              margin_currency="INR", leverage=10.0)
    kw.update(over)
    return kw


# ------------------------------------------------------------ plan_entry


def _plan(**over):
    kw = dict(instrument=BTC, symbol="BTCUSDT", direction="LONG", entry=100_000.0,
              sl=98_000.0, tp1=103_000.0, live_price=100_000.0, notional_usdt=100.0,
              requested_leverage=10.0, max_gap_pct=2.5, liquidation_stop_multiple=2.0)
    kw.update(over)
    return E.plan_entry(**kw)


def test_plan_sizes_down_and_caps_leverage_by_stop_distance() -> None:
    p = _plan()
    assert isinstance(p, E.EntryPlan)
    assert p.qty == 0.001 and p.qty_str == "0.001"
    # stop 2% away, liquidation must be >= 2 stops away → at most 25x; user asked 10
    assert p.leverage == 10
    wide = _plan(sl=95_000.0, requested_leverage=20.0)  # 5% stop → floor(1/(2*.05)) = 10
    assert wide.leverage == 10


@pytest.mark.parametrize("over,reason", [
    (dict(instrument=None), "instrument_unavailable"),
    (dict(live_price=None), "price_unavailable"),
    (dict(live_price=104_000.0), "entry_gap"),
    (dict(live_price=97_900.0, max_gap_pct=5), "levels_crossed"),
    (dict(sl=40_000.0, entry=100_000.0), "stop_too_wide"),
    (dict(notional_usdt=20.0), "below_min_notional"),
])
def test_plan_refusals_are_named(over, reason) -> None:
    r = _plan(**over)
    assert isinstance(r, E.Refusal) and r.reason == reason


def test_plan_short_levels() -> None:
    p = _plan(direction="SHORT", sl=102_000.0, tp1=97_000.0)
    assert isinstance(p, E.EntryPlan) and p.side == "sell"
    assert isinstance(_plan(direction="SHORT", sl=98_000.0, tp1=103_000.0), E.Refusal)


# ------------------------------------------------------------- open path


async def test_happy_path_places_stop_and_target_after_fill(env) -> None:
    fx, store, _, ex = env
    out = await ex.open_position(**_open_kwargs())
    assert out["outcome"] == "placed"
    rec = store.get("u1", "S1")
    assert rec.state == P.OPEN and rec.sl_resting and rec.tp_resting
    assert rec.position_id and rec.entry_filled == 100_000.0 and rec.margin_currency == "INR"
    # leverage is set before the order, the stop only after the fill
    assert fx.calls.index("leverage:10") < fx.calls.index("order:buy:0.001") < fx.calls.index("tpsl")


async def test_never_twice_second_dispatch_sends_nothing(env) -> None:
    fx, _, _, ex = env
    await ex.open_position(**_open_kwargs())
    n = len([c for c in fx.calls if c.startswith("order")])
    out = await ex.open_position(**_open_kwargs())
    assert out["reject_class"] == "AlreadyActive"
    assert len([c for c in fx.calls if c.startswith("order")]) == n


async def test_never_merged_refuses_a_pair_the_user_holds(env) -> None:
    fx, store, _, ex = env
    fx._row("B-BTC_USDT", "INR")["active_pos"] = 0.5
    out = await ex.open_position(**_open_kwargs())
    assert out["reject_class"] == "PairNotFlat"
    assert not any(c.startswith("order") for c in fx.calls)
    assert store.get("u1", "S1") is None


async def test_never_naked_stop_refused_twice_exits_at_market(env) -> None:
    fx, store, _, ex = env
    fx.sl_refusals = 2
    out = await ex.open_position(**_open_kwargs())
    assert out["outcome"] == "rejected"
    rec = store.get("u1", "S1")
    assert rec.state == P.CLOSED and "exit" in fx.calls
    assert fx.pos[("B-BTC_USDT", "INR")]["active_pos"] == 0.0


async def test_stop_refused_once_then_placed_stays_open(env) -> None:
    fx, store, _, ex = env
    fx.sl_refusals = 1
    out = await ex.open_position(**_open_kwargs())
    assert out["outcome"] == "placed"
    assert store.get("u1", "S1").sl_resting and "exit" not in fx.calls


async def test_liquidation_inside_stop_exits_immediately(env) -> None:
    fx, store, _, ex = env
    fx.liquidation = 98_500.0   # above the 98,000 stop on a long
    await ex.open_position(**_open_kwargs())
    rec = store.get("u1", "S1")
    assert rec.state == P.CLOSED and rec.close_reason == E.CLOSE_LIQUIDATION_INSIDE_STOP
    assert "tpsl" not in fx.calls


async def test_rejected_entry_records_and_places_nothing_else(env) -> None:
    fx, store, _, ex = env
    fx.order_raise = C.CoinDCXRejected("x", status=400, body={"message": "Insufficient funds"})
    out = await ex.open_position(**_open_kwargs())
    assert out["reject_class"] == "InsufficientMargin"
    assert store.get("u1", "S1").state == P.REJECTED
    assert "tpsl" not in fx.calls


async def test_manual_take_after_a_refusal_is_a_fresh_attempt(env) -> None:
    # Owner, 2026-09-28: a refused CoinDCX attempt left a REJECTED row and
    # every later Take answered "already sent" with nothing on the account.
    fx, store, _, ex = env
    fx.order_raise = C.CoinDCXRejected("x", status=400, body={"message": "Insufficient funds"})
    await ex.open_position(**_open_kwargs())
    assert store.get("u1", "S1").state == P.REJECTED
    fx.order_raise = None
    out = await ex.open_position(**_open_kwargs(source="manual_take"))
    assert out["outcome"] == "placed"
    assert store.get("u1", "S1").state == P.OPEN
    assert len([c for c in fx.calls if c.startswith("order")]) == 2


async def test_auto_fanout_never_retries_a_refusal_and_says_why(env) -> None:
    fx, store, _, ex = env
    fx.order_raise = C.CoinDCXRejected("x", status=400, body={"message": "Insufficient funds"})
    await ex.open_position(**_open_kwargs())
    fx.order_raise = None
    out = await ex.open_position(**_open_kwargs())   # source="auto"
    assert out["reject_class"] == "AlreadyHandled"
    assert "nothing was placed" in out["reject_detail"]
    assert "already sent" not in out["reject_detail"]
    assert len([c for c in fx.calls if c.startswith("order")]) == 1


async def test_manual_take_never_retries_a_live_or_finished_record(env) -> None:
    fx, store, _, ex = env
    await ex.open_position(**_open_kwargs())
    out = await ex.open_position(**_open_kwargs(source="manual_take"))
    assert out["reject_class"] == "AlreadyActive" and "already open" in out["reject_detail"]
    rec = store.get("u1", "S1")
    rec.state = P.ENTRY_UNCERTAIN
    store.put(rec)
    out = await ex.open_position(**_open_kwargs(source="manual_take"))
    assert out["reject_class"] == "AlreadyActive" and "being confirmed" in out["reject_detail"]
    rec.state = P.CLOSED
    store.put(rec)
    out = await ex.open_position(**_open_kwargs(source="manual_take"))
    assert out["reject_class"] == "AlreadyHandled" and "has closed" in out["reject_detail"]
    assert len([c for c in fx.calls if c.startswith("order")]) == 1


def test_reclaim_rejected_only_replaces_a_rejected_row() -> None:
    store = P.CoinDCXPositionStore(":memory:")
    base = dict(uid="u", signal_id="s", symbol="BTCUSDT", pair="B-BTC_USDT", side="LONG",
                margin_currency="USDT", leverage=5.0, qty=0.001, entry_target=1.0,
                sl_price=0.9, tp_price=1.1, notional_usdt=10.0)
    assert store.reclaim_rejected(P.CoinDCXPosition(state=P.PENDING, **base)) is False
    store.put(P.CoinDCXPosition(state=P.OPEN, **base))
    assert store.reclaim_rejected(P.CoinDCXPosition(state=P.PENDING, **base)) is False
    assert store.get("u", "s").state == P.OPEN
    store.put(P.CoinDCXPosition(state=P.REJECTED, **base))
    assert store.reclaim_rejected(P.CoinDCXPosition(state=P.PENDING, **base)) is True
    assert store.get("u", "s").state == P.PENDING


async def test_unknown_entry_outcome_is_left_for_the_reconciler(env) -> None:
    fx, store, _, ex = env
    fx.order_raise = C.CoinDCXUnreachable("timeout")
    out = await ex.open_position(**_open_kwargs())
    assert out["reject_class"] == "EntryUncertain"
    assert store.get("u1", "S1").state == P.ENTRY_UNCERTAIN


async def test_refusal_before_order_writes_no_record(env) -> None:
    _, store, reg, ex = env
    reg.price = 104_000.0
    out = await ex.open_position(**_open_kwargs())
    assert out["reject_class"] == "PriceGapTooLarge"
    assert store.get("u1", "S1") is None


# ------------------------------------------------------------ close path


async def test_user_close_exits_and_records_exit_price_and_pnl(env) -> None:
    fx, store, _, ex = env
    await ex.open_position(**_open_kwargs())
    out = await ex.close_position("u1", "S1", reason="USER_CLOSE")
    assert out["outcome"] == "closed"
    rec = store.get("u1", "S1")
    assert rec.state == P.CLOSED and rec.close_reason == E.CLOSE_EXIT
    assert rec.exit_price == 100_500.0
    assert rec.realized_pnl_usdt == pytest.approx(0.5)   # 500 * 0.001
    assert rec.fees_usdt == pytest.approx(0.11)
    assert "cancel_all" in fx.calls
    assert rec.to_api()["realized_pnl_inr"] == pytest.approx(51.0)


async def test_backstop_close_racing_exchange_target_is_labelled_tp1(env) -> None:
    fx, store, _, ex = env
    await ex.open_position(**_open_kwargs())
    fx.trigger("tp")          # CoinDCX's own target fires first …
    fx.exit_raises = True     # … so our backstop exit is refused
    await ex.close_position("u1", "S1", reason="full_tp_hit")
    rec = store.get("u1", "S1")
    assert rec.state == P.CLOSED and rec.close_reason == E.CLOSE_TP1


async def test_failed_exit_on_live_position_stays_open_for_retry(env) -> None:
    fx, store, _, ex = env
    await ex.open_position(**_open_kwargs())
    fx.exit_raises = True
    out = await ex.close_position("u1", "S1", reason="USER_CLOSE")
    assert out["reject_class"] == "ExitPending"
    assert store.get("u1", "S1").state == P.OPEN


# ------------------------------------------------------------- reconciler


async def test_reconciler_finalises_exchange_stop_as_sl(env) -> None:
    fx, store, _, ex = env
    await ex.open_position(**_open_kwargs())
    fx.trigger("sl")
    await R.CoinDCXReconciler(ex).cycle()
    rec = store.get("u1", "S1")
    assert rec.state == P.CLOSED and rec.close_reason == E.CLOSE_SL
    assert rec.realized_pnl_usdt == pytest.approx(-2.0)


async def test_reconciler_repairs_a_missing_stop(env) -> None:
    fx, store, _, ex = env
    await ex.open_position(**_open_kwargs())
    fx.pos[("B-BTC_USDT", "INR")]["stop_loss_trigger"] = None   # stop vanished
    n = fx.calls.count("tpsl")
    await R.CoinDCXReconciler(ex).cycle()
    assert fx.calls.count("tpsl") == n + 1
    assert store.get("u1", "S1").sl_resting


async def test_reconciler_age_cap_exits(env, monkeypatch) -> None:
    fx, store, _, ex = env
    await ex.open_position(**_open_kwargs())
    import config
    monkeypatch.setattr(config, "COINDCX_MAX_POSITION_AGE_SEC", 60)
    await R.CoinDCXReconciler(ex).cycle(now=time.time() + 120)
    assert store.get("u1", "S1").close_reason == E.CLOSE_AGE_CAP


async def test_reconciler_adopts_or_retires_uncertain_entries(env) -> None:
    fx, store, _, ex = env
    fx2 = ex._client_factory("u2")
    fx2.order_raise = C.CoinDCXUnreachable("timeout")
    fx2.fill = False
    fx.order_raise = C.CoinDCXUnreachable("timeout")
    await ex.open_position(**_open_kwargs())
    fx.order_raise = None
    # the exchange did open it after all → adopted and protected
    fx._row("B-BTC_USDT", "INR").update(active_pos=0.001, avg_price=100_000.0)
    await R.CoinDCXReconciler(ex).cycle()
    rec = store.get("u1", "S1")
    assert rec.state == P.OPEN and rec.sl_resting

    await ex.open_position(**_open_kwargs(uid="u2", signal_id="S2"))
    assert store.get("u2", "S2").state == P.ENTRY_UNCERTAIN
    # nothing ever appears on the exchange for u2; age the record past grace
    aged = store.get("u2", "S2")
    aged.created_at = time.time() - 1000
    store.put(aged)
    await R.CoinDCXReconciler(ex).cycle()
    assert store.get("u2", "S2").state == P.REJECTED


async def test_reconciler_budget_is_spent_per_user_examined(env, monkeypatch) -> None:
    fx, store, _, ex = env
    import config
    monkeypatch.setattr(config, "COINDCX_RECONCILE_MAX_USERS_PER_CYCLE", 2)
    for i in range(5):  # five users, all healthy — the do-nothing branch
        store.put(P.CoinDCXPosition(uid=f"u{i}", signal_id="X", symbol="BTCUSDT",
                                    pair="B-BTC_USDT", side="LONG", state=P.OPEN,
                                    margin_currency="USDT", leverage=5, qty=0.001,
                                    entry_target=1, sl_price=1, tp_price=2,
                                    position_id="p", opened_at=time.time()))
    rec = R.CoinDCXReconciler(ex)
    out = await rec.cycle()
    calls = sum(a.calls.count("positions") for a in ex.accounts.values())
    assert out["users"] == 2 and calls == 2


async def test_reconciler_makes_no_call_without_live_records(env) -> None:
    fx, _, _, ex = env
    await R.CoinDCXReconciler(ex).cycle()
    assert fx.calls == []


async def test_reconciler_never_touches_a_position_it_did_not_open(env) -> None:
    fx, store, _, ex = env
    await ex.open_position(**_open_kwargs())
    fx._row("B-ETH_USDT", "USDT")["active_pos"] = 3.0   # the user's own trade
    before = [c for c in fx.calls if c in ("exit", "tpsl")]
    rec = R.CoinDCXReconciler(ex)
    await rec.cycle()
    assert [c for c in fx.calls if c in ("exit", "tpsl")] == before
    assert rec.stats["orphans_seen"] == 1


# ------------------------------------------------------------- tpsl parse


def test_tpsl_leg_parses_documented_partial_answer() -> None:
    import json
    from pathlib import Path

    ex = json.loads((Path(__file__).parent / "fixtures/coindcx/private_doc_examples.json").read_text())
    res = ex["create_tpsl_partial"]
    assert C.tpsl_leg(res, "stop_loss")[0] is True
    ok, _, err = C.tpsl_leg(res, "take_profit")
    assert ok is False and err == "TP already exists"


# -------------------------------------------------------------- self-test


async def test_self_test_refuses_unless_owner_allow_listed(monkeypatch, tmp_path) -> None:
    import config
    from src.venues.coindcx import self_test as ST

    monkeypatch.setattr(ST, "REPORT_PATH", str(tmp_path / "r.json"))
    DCX["coindcx_execution_allowed_uids"] = ""
    fx = FakeExchange()
    rep = await ST.run("owner", client=fx, registry=FakeRegistry(), sleep=_nosleep)
    assert rep["verdict"] == "refused" and fx.calls == []


async def test_self_test_full_run_ends_flat_and_writes_report(monkeypatch, tmp_path) -> None:
    import json

    import config
    from src.venues.coindcx import self_test as ST

    monkeypatch.setattr(ST, "REPORT_PATH", str(tmp_path / "r.json"))
    DCX["coindcx_execution_allowed_uids"] = "owner"
    fx = FakeExchange()

    async def wallets():
        return [{"currency_short_name": "USDT", "balance": "100"}]

    fx.wallets = wallets  # type: ignore[attr-defined]
    rep = await ST.run("owner", symbol="BTCUSDT", client=fx,
                       registry=FakeRegistry(), sleep=_nosleep)
    steps = {s["step"]: s["ok"] for s in rep["steps"]}
    assert rep["verdict"] == "pass", rep
    assert steps["stop_and_target_rest_together"] and steps["exit_flattens"]
    assert steps["no_order_left_after_cleanup"]
    assert all(r["active_pos"] == 0 for r in fx.pos.values())
    assert json.loads((tmp_path / "r.json").read_text())["verdict"] == "pass"


async def test_self_test_stops_before_any_order_when_the_futures_wallet_is_empty(
        monkeypatch, tmp_path) -> None:
    """The owner's first real run: wallets=[] and then "Insufficient funds"
    from the ORDER.  An empty wallet must fail on the funds step, with the
    amount to move, and place nothing."""
    from src.venues.coindcx import self_test as ST

    monkeypatch.setattr(ST, "REPORT_PATH", str(tmp_path / "r.json"))
    DCX["coindcx_execution_allowed_uids"] = "owner"
    fx = FakeExchange()

    async def wallets():
        return []

    fx.wallets = wallets  # type: ignore[attr-defined]
    rep = await ST.run("owner", symbol="BTCUSDT", client=fx, registry=FakeRegistry(), sleep=_nosleep)
    steps = {s["step"]: s for s in rep["steps"]}
    assert rep["verdict"] == "fail"
    assert steps["funds_available"]["ok"] is False
    assert "FUTURES wallet" in steps["funds_available"]["detail"]
    assert not any(c.startswith(("order", "market")) for c in fx.calls), fx.calls
    assert "entry_accepted" not in steps


async def test_self_test_funds_check_reads_the_chosen_margin_currency(monkeypatch, tmp_path) -> None:
    """USDT in the wallet does not fund an INR-margin test."""
    from src.venues.coindcx import self_test as ST

    monkeypatch.setattr(ST, "REPORT_PATH", str(tmp_path / "r.json"))
    DCX["coindcx_execution_allowed_uids"] = "owner"
    fx = FakeExchange()

    async def wallets():
        return [{"currency_short_name": "USDT", "balance": "1000"}]

    fx.wallets = wallets  # type: ignore[attr-defined]
    rep = await ST.run("owner", symbol="BTCUSDT", margin_currency="INR", client=fx,
                       registry=FakeRegistry(), sleep=_nosleep)
    step = next(s for s in rep["steps"] if s["step"] == "funds_available")
    assert step["ok"] is False and step["margin_currency"] == "INR"
    assert step["required"] > 0 and step["balance"] == 0


async def test_self_test_names_an_unreadable_inr_rate_instead_of_crashing(monkeypatch, tmp_path) -> None:
    from src.venues.coindcx import self_test as ST

    monkeypatch.setattr(ST, "REPORT_PATH", str(tmp_path / "r.json"))
    DCX["coindcx_execution_allowed_uids"] = "owner"
    fx = FakeExchange()
    reg = FakeRegistry()

    async def wallets():
        return [{"currency_short_name": "INR", "balance": "50000"}]

    fx.wallets = wallets  # type: ignore[attr-defined]

    async def no_rate():
        return None

    reg.inr_per_usdt = no_rate  # type: ignore[method-assign]
    rep = await ST.run("owner", symbol="BTCUSDT", margin_currency="INR", client=fx,
                       registry=reg, sleep=_nosleep)
    assert rep["verdict"] == "fail"
    step = rep["steps"][-1]
    assert step["step"] == "funds_available" and step["required"] is None
    assert "conversion price" in step["detail"]


async def test_self_test_refuses_a_pair_the_owner_holds(monkeypatch, tmp_path) -> None:
    import config
    from src.venues.coindcx import self_test as ST

    monkeypatch.setattr(ST, "REPORT_PATH", str(tmp_path / "r.json"))
    DCX["coindcx_execution_allowed_uids"] = "owner"
    fx = FakeExchange()
    fx._row("B-BTC_USDT", "USDT")["active_pos"] = 1.0

    async def wallets():
        return []

    fx.wallets = wallets  # type: ignore[attr-defined]
    rep = await ST.run("owner", symbol="BTCUSDT", client=fx, registry=FakeRegistry(), sleep=_nosleep)
    assert rep["verdict"] == "fail" and not any(c.startswith("order") for c in fx.calls)


def test_status_snapshot_writes_without_exchange_calls(tmp_path, monkeypatch) -> None:
    import json

    monkeypatch.setattr(R, "STATUS_PATH", str(tmp_path / "s.json"))
    store = P.CoinDCXPositionStore(":memory:")
    P.set_store_for_test(store)
    try:
        R.write_status_file(R.CoinDCXReconciler())
    finally:
        P.set_store_for_test(None)
    snap = json.loads((tmp_path / "s.json").read_text())
    assert snap["execution_enabled"] is False
    assert "positions" in snap and "reconciler" in snap


# ------------------------------------------------- ops contract vector
#
# 360ce-ops `tests/fixtures_coindcx.json` is a byte-identical copy of the
# file below: the status file and the self-test report exactly as this engine
# writes them.  Ops renders its CoinDCX page from both, and a fixture ops
# wrote by hand would choose a shape and then agree with itself about it
# (`zone_distance_atr`, the price-action lane card).  Regenerate with
# `COINDCX_WRITE_OPS_VECTOR=1 pytest tests/venues/test_coindcx_execution.py -k ops_contract`.

def _stable(o: Any) -> Any:
    """Clock-valued keys → a marker; the contract is keys and types."""
    clock = {"written_at", "started_at", "finished_at", "last_cycle_at",
             "pairs_age_s", "prices_age_s"}
    if isinstance(o, dict):
        return {k: ("<clock>" if k in clock and o[k] is not None else _stable(v))
                for k, v in o.items()}
    if isinstance(o, list):
        return [_stable(v) for v in o]
    return o


async def test_ops_contract_vector_is_what_the_engine_writes(monkeypatch, tmp_path) -> None:
    import json
    import os
    from pathlib import Path

    import config
    from src.venues.coindcx import self_test as ST

    monkeypatch.setattr(R, "STATUS_PATH", str(tmp_path / "s.json"))
    monkeypatch.setattr(ST, "REPORT_PATH", str(tmp_path / "r.json"))
    DCX["coindcx_execution_allowed_uids"] = "owner"
    # Module-global counters carry state from earlier tests; the vector must
    # not depend on test order.
    from collections import Counter

    from src.venues.coindcx import dispatch as D

    monkeypatch.setattr(E, "_counters", {})
    monkeypatch.setattr(D, "_TOTALS", Counter())
    monkeypatch.setattr(I, "_REGISTRY", I.InstrumentRegistry())
    store = P.CoinDCXPositionStore(":memory:")
    P.set_store_for_test(store)
    try:
        store.put(P.CoinDCXPosition(uid="owner", signal_id="S1", symbol="BTCUSDT",
                                    pair="B-BTC_USDT", side="LONG", state=P.CLOSED,
                                    margin_currency="INR", leverage=5, qty=0.001,
                                    entry_target=1, sl_price=1, tp_price=2, close_reason="TP1"))
        rec = R.CoinDCXReconciler()
        await rec.cycle(now=1.0)
    finally:
        P.set_store_for_test(None)
    fx = FakeExchange()

    async def wallets():
        return [{"currency_short_name": "USDT", "balance": "100"}]

    fx.wallets = wallets  # type: ignore[attr-defined]
    await ST.run("owner", symbol="BTCUSDT", client=fx, registry=FakeRegistry(), sleep=_nosleep)
    vector = {
        "status": _stable(json.loads((tmp_path / "s.json").read_text())),
        "self_test_pass": _stable(json.loads((tmp_path / "r.json").read_text())),
    }
    text = json.dumps(vector, indent=2, sort_keys=True) + "\n"
    path = Path(__file__).parent / "fixtures" / "coindcx" / "ops_contract.json"
    if os.environ.get("COINDCX_WRITE_OPS_VECTOR") == "1":
        path.write_text(text)
    assert path.read_text() == text, (
        "the CoinDCX status file / self-test report changed shape — regenerate "
        "and update 360ce-ops' tests/fixtures_coindcx.json + reducer together")
