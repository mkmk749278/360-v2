"""CoinDCX real-account self-test — the go-live gate the owner runs.

CoinDCX documents no testnet, and three behaviours our design depends on are
not stated in its documentation (``docs/COINDCX_VENUE_PLAN_2026_09_27.md``
§6).  This runs them on the owner's own account at the minimum size and
records what the exchange actually did, step by step:

1.  the key signs and reads the futures wallet;
2.  the instrument resolves and is tradable;
3.  the pair is flat (we never test on a pair the owner holds);
4.  leverage can be set on a pair with no position;
5.  a minimum market entry fills and appears as a position;
6.  **a position-level stop AND target can rest together** (``create_tpsl``);
7.  the exchange reports both triggers on the position;
8.  the market exit flattens the position;
9.  whether CoinDCX cancels the position's stop/target by itself on exit
    (recorded, not graded);
10. **after our cleanup, no stop/target order is left resting** — the
    question a missing reduce-only flag makes load-bearing.

It never runs on its own: the owner starts it from ops, and it refuses unless
the owner-only allow-list names this uid.  Cost is one minimum-size round trip
(about 6 USDT notional; fees are cents).  The report is written to
``data/coindcx_self_test.json`` so ops can render it after the request ends.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional

from src.utils import get_logger
from src.venues.coindcx import client as _client
from src.venues.coindcx import execution as _ex
from src.venues.coindcx import instruments as _inst

log = get_logger("venues.coindcx.self_test")

REPORT_PATH = os.getenv("COINDCX_SELF_TEST_REPORT", "data/coindcx_self_test.json")
_DEFAULT_SYMBOL = "DOGEUSDT"


class _Report:
    def __init__(self, uid: str, symbol: str, margin: str) -> None:
        self.data: Dict[str, Any] = {
            "uid": uid, "symbol": symbol, "margin_currency": margin,
            "started_at": time.time(), "steps": [], "verdict": "running",
        }

    def step(self, name: str, ok: bool, **observed: Any) -> bool:
        self.data["steps"].append({"step": name, "ok": bool(ok), **observed})
        return ok

    def finish(self, verdict: str) -> Dict[str, Any]:
        self.data["verdict"] = verdict
        self.data["finished_at"] = time.time()
        return self.data


def _write(report: Dict[str, Any]) -> None:
    try:
        os.makedirs(os.path.dirname(REPORT_PATH) or ".", exist_ok=True)
        tmp = REPORT_PATH + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(report, fh, default=str, indent=1)
        os.replace(tmp, REPORT_PATH)
    except Exception:  # pragma: no cover
        log.exception("coindcx self-test: report write failed")


def _untriggered_for(orders: List[Dict[str, Any]], pair: str) -> List[Dict[str, Any]]:
    return [
        o for o in orders
        if o.get("pair") == pair and str(o.get("status") or "").lower() in ("untriggered", "open")
    ]


async def run(
    uid: str,
    *,
    symbol: str = _DEFAULT_SYMBOL,
    margin_currency: str = "USDT",
    client: Optional[_client.CoinDCXClient] = None,
    registry: Optional[_inst.InstrumentRegistry] = None,
    sleep=asyncio.sleep,
) -> Dict[str, Any]:
    """Run the checklist and return (and persist) the report.  Never raises."""
    from src.venues.coindcx import dispatch as _dcx

    symbol = (symbol or _DEFAULT_SYMBOL).upper()
    margin_currency = (margin_currency or "USDT").upper()
    rep = _Report(uid, symbol, margin_currency)
    allowed = _dcx._allowed_uids()
    if not allowed or uid not in allowed:
        rep.step("owner_allow_list", False,
                 detail="Set COINDCX_EXECUTION_ALLOWED_UIDS to the owner's uid first.")
        out = rep.finish("refused")
        _write(out)
        return out
    client = client or _client.CoinDCXClient(uid)
    registry = registry or _inst.get_registry()
    try:
        out = await _run(rep, client, registry, symbol, margin_currency, sleep)
    except Exception as exc:  # noqa: BLE001
        log.exception("coindcx self-test crashed")
        rep.step("crashed", False, error=f"{type(exc).__name__}: {exc}")
        out = rep.finish("error")
    _write(out)
    return out


async def _run(rep, client, registry, symbol, margin, sleep) -> Dict[str, Any]:
    # 1 — key
    try:
        wallets = await client.wallets()
        rep.step("key_reads_wallet", True, wallets=[
            {"ccy": w.get("currency_short_name"), "balance": w.get("balance")} for w in wallets
        ])
    except Exception as exc:  # noqa: BLE001
        rep.step("key_reads_wallet", False, error=str(exc))
        return rep.finish("fail")

    # 2 — instrument + price
    inst = await registry.instrument(symbol)
    price = await registry.last_price(symbol)
    if not rep.step("instrument_tradable", bool(inst and inst.refusal() is None and price),
                    pair=getattr(inst, "pair", None), refusal=inst.refusal() if inst else "none",
                    price=price, min_notional=getattr(inst, "min_notional", None)):
        return rep.finish("fail")

    # 3 — pair flat
    rows = await client.positions(pairs=[inst.pair], margin_currencies=(margin,))
    row = _ex.position_row(rows, inst.pair, margin)
    if not rep.step("pair_flat", _ex.row_is_flat(row), row=row):
        return rep.finish("fail")

    # 4 — leverage
    try:
        await client.update_leverage(pair=inst.pair, leverage=2, margin_currency=margin)
        rep.step("set_leverage", True, leverage=2)
    except Exception as exc:  # noqa: BLE001
        rep.step("set_leverage", False, error=str(exc))
        return rep.finish("fail")

    # 5 — minimum entry (just above both minimums)
    need = max(inst.min_notional * 1.15, inst.min_quantity * price * 1.15)
    qty = _inst.round_qty_down(need / price + inst.quantity_increment, inst.quantity_increment)
    try:
        order = await client.market_order(
            pair=inst.pair, side="buy",
            quantity=_inst.format_number(qty, inst.quantity_increment),
            leverage=2, margin_currency=margin,
        )
        rep.step("entry_accepted", True, order_id=order.get("id"), status=order.get("status"), qty=qty)
    except Exception as exc:  # noqa: BLE001
        rep.step("entry_accepted", False, error=str(exc))
        return rep.finish("fail")
    pos_row = None
    for _ in range(20):
        rows = await client.positions(pairs=[inst.pair], margin_currencies=(margin,))
        pos_row = _ex.position_row(rows, inst.pair, margin)
        if pos_row and _ex._num(pos_row.get("active_pos")) > 0:
            break
        await sleep(0.5)
    filled = bool(pos_row and _ex._num(pos_row.get("active_pos")) > 0)
    rep.step("entry_filled", filled, position=pos_row)
    if not filled or pos_row is None:
        return rep.finish("fail")
    position_id = str(pos_row.get("id"))
    avg = _ex._num(pos_row.get("avg_price")) or price

    verdict = "pass"
    # 6 — stop AND target together
    sl = _inst.round_price(avg * 0.97, inst.price_increment)
    tp = _inst.round_price(avg * 1.03, inst.price_increment)
    try:
        res = await client.create_tpsl(
            position_id=position_id,
            stop_price=_inst.format_number(sl, inst.price_increment),
            take_profit_price=_inst.format_number(tp, inst.price_increment),
        )
        sl_ok, sl_id, sl_err = _client.tpsl_leg(res, "stop_loss")
        tp_ok, tp_id, tp_err = _client.tpsl_leg(res, "take_profit")
        if not rep.step("stop_and_target_rest_together", sl_ok and tp_ok,
                        stop=(sl_ok, sl_id, sl_err), target=(tp_ok, tp_id, tp_err), raw=res):
            verdict = "fail"
    except Exception as exc:  # noqa: BLE001
        rep.step("stop_and_target_rest_together", False, error=str(exc))
        verdict = "fail"

    # 7 — the exchange reports both triggers
    rows = await client.positions(pairs=[inst.pair], margin_currencies=(margin,))
    row = _ex.position_row(rows, inst.pair, margin) or {}
    if not rep.step(
        "triggers_reported_on_position",
        _ex._num(row.get("stop_loss_trigger")) > 0 and _ex._num(row.get("take_profit_trigger")) > 0,
        stop_loss_trigger=row.get("stop_loss_trigger"),
        take_profit_trigger=row.get("take_profit_trigger"),
        liquidation_price=row.get("liquidation_price"),
    ):
        verdict = "fail"
    try:
        resting_before = _untriggered_for(
            await client.orders(statuses="untriggered,open", side="sell",
                                margin_currencies=(margin,)), inst.pair)
        rep.step("resting_orders_before_exit", True,
                 orders=[{k: o.get(k) for k in ("id", "order_type", "stage", "stop_price", "status")}
                         for o in resting_before])
    except Exception as exc:  # noqa: BLE001
        rep.step("resting_orders_before_exit", False, error=str(exc))

    # 8 — exit flattens
    try:
        await client.exit_position(position_id=position_id)
    except Exception as exc:  # noqa: BLE001
        rep.step("exit_accepted", False, error=str(exc))
        return rep.finish("fail_position_left_open")
    flat = False
    for _ in range(20):
        rows = await client.positions(pairs=[inst.pair], margin_currencies=(margin,))
        r = _ex.position_row(rows, inst.pair, margin)
        if r is None or _ex._num(r.get("active_pos")) == 0:
            flat = True
            break
        await sleep(0.5)
    if not rep.step("exit_flattens", flat):
        return rep.finish("fail_position_left_open")

    # 9 — does CoinDCX cancel the position's stop/target on exit by itself?
    #     Recorded as a fact, not graded: the executor cancels everything
    #     resting for the position after every close either way (step 10).
    await sleep(1.0)
    leftover = _untriggered_for(
        await client.orders(statuses="untriggered,open", side="sell", margin_currencies=(margin,)),
        inst.pair,
    )
    rep.step("exchange_auto_cancels_on_exit", True, auto_cancelled=not leftover,
             leftover=[{k: o.get(k) for k in ("id", "order_type", "stage", "stop_price")}
                       for o in leftover])

    # 10 — our cleanup, then the gate: nothing may rest against a flat pair.
    try:
        await client.cancel_all_for_position(position_id=position_id)
        rep.step("cleanup", True)
    except Exception as exc:  # noqa: BLE001
        rep.step("cleanup", False, error=str(exc))
    await sleep(1.0)
    after = _untriggered_for(
        await client.orders(statuses="untriggered,open", side="sell", margin_currencies=(margin,)),
        inst.pair,
    )
    if not rep.step("no_order_left_after_cleanup", not after,
                    leftover=[{k: o.get(k) for k in ("id", "order_type", "stage")} for o in after]):
        verdict = "fail"
    return rep.finish(verdict)
