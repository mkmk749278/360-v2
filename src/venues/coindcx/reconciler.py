"""CoinDCX reconciler — the exchange is the truth; our records follow it.

Every ``COINDCX_RECONCILE_INTERVAL_SEC`` (and immediately when the private
stream nudges a user), for each user holding a live CoinDCX record:

* one ``positions`` call for the user's whole account (both margin
  currencies) — the only call made when nothing has changed;
* a record whose pair is now flat is finalised with the exchange's own exit
  order (reason, price, fees);
* a live position without a resting stop gets one (or is exited — never
  naked);
* ``PENDING`` / ``ENTRY_UNCERTAIN`` records are adopted if the exchange holds
  the position, retired as ``REJECTED`` if it stays flat past a grace period;
* a position older than ``COINDCX_MAX_POSITION_AGE_SEC`` is exited, the same
  cap the Binance reconciler applies, so a CoinDCX subscriber's trade lives
  exactly as long as a Binance subscriber's on the same signal;
* exchange positions with **no** record of ours are never touched — they are
  the user's own trades.  (They used to be "counted as orphans", off one
  page of an unfiltered list; that count described a page, not the account,
  and is gone.)
* the exchange is asked only about the user's own live pairs, and a filled
  record whose row does not come back is UNKNOWN — counted as
  ``row_missing`` and left alone, never finalised (HBARUSDT, 2026-09-28).

Cost discipline: calls are made only for users with a live record, and the
per-cycle budget (``COINDCX_RECONCILE_MAX_USERS_PER_CYCLE``) is spent per user
**examined, before any call**, so it bounds the branch that finds nothing to
do — the branch production takes almost every cycle (CLAUDE.md, 2026-09-01).
With no live records the loop makes no call at all.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

from src.utils import get_logger
from src.venues.coindcx import execution as _ex
from src.venues.coindcx import positions as _pos

log = get_logger("venues.coindcx.reconciler")

#: A PENDING / ENTRY_UNCERTAIN record whose pair is still flat after this long
#: is retired: the entry never became a position.
UNRESOLVED_GRACE_S = 90.0
#: The same, when the exchange returned NO row for the pair at all.  Absence
#: is not evidence of flat (the HBARUSDT rule); a pair never traded before may
#: legitimately have no row, so the record is still retired eventually — but
#: only after long enough that a real position would have shown up.
UNRESOLVED_ABSENT_GRACE_S = 900.0


class CoinDCXReconciler:
    def __init__(self, executor: Optional[_ex.CoinDCXExecutor] = None) -> None:
        self._executor = executor
        self._nudged: set = set()
        self._wake = asyncio.Event()
        self._cursor = 0
        self.stats: Dict[str, Any] = defaultdict(int)
        self.last_cycle_at: Optional[float] = None
        self.last_cycle_users = 0

    @property
    def executor(self) -> _ex.CoinDCXExecutor:
        return self._executor or _ex.get_executor()

    def nudge(self, uid: str) -> None:
        """Ask for ``uid`` to be reconciled now (stream event)."""
        self._nudged.add(uid)
        self._wake.set()

    async def run(self) -> None:
        from config import COINDCX_RECONCILE_INTERVAL_SEC

        log.info("CoinDCX reconciler started (every {}s)", COINDCX_RECONCILE_INTERVAL_SEC)
        while True:
            try:
                await asyncio.wait_for(self._wake.wait(), timeout=COINDCX_RECONCILE_INTERVAL_SEC)
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                raise
            self._wake.clear()
            try:
                await self.cycle()
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                self.stats["cycle_crashed"] += 1
                log.exception("CoinDCX reconciler cycle crashed")
                _ex._fail_open("coindcx.reconciler.cycle", exc)

    async def cycle(self, *, now: Optional[float] = None) -> Dict[str, Any]:
        from config import COINDCX_RECONCILE_MAX_USERS_PER_CYCLE

        now = time.time() if now is None else now
        live = await asyncio.to_thread(self.executor.store.live_positions)
        by_uid: Dict[str, List[_pos.CoinDCXPosition]] = defaultdict(list)
        for p in live:
            by_uid[p.uid].append(p)
        uids = sorted(by_uid)
        # Nudged users first, then round-robin through the rest.
        nudged = [u for u in uids if u in self._nudged]
        self._nudged.difference_update(nudged)
        rest = [u for u in uids if u not in nudged]
        if rest:
            k = self._cursor % len(rest)
            rest = rest[k:] + rest[:k]
        order = nudged + rest
        budget = max(1, int(COINDCX_RECONCILE_MAX_USERS_PER_CYCLE))
        examined = 0
        for uid in order:
            if examined >= budget:
                self.stats["budget_exhausted"] += 1
                break
            examined += 1  # spent before any call (the do-nothing branch too)
            self._cursor += 1
            try:
                await self.reconcile_user(uid, by_uid[uid], now=now)
            except Exception as exc:  # noqa: BLE001 — one user never stops the rest
                self.stats["user_failed"] += 1
                log.warning("CoinDCX reconcile uid={} failed: {}", uid, exc)
        self.last_cycle_at = now
        self.last_cycle_users = examined
        self.stats["cycles"] += 1
        await asyncio.to_thread(write_status_file, self)
        return {"users": examined, "live_records": len(live)}

    async def reconcile_user(
        self, uid: str, records: List[_pos.CoinDCXPosition], *, now: float,
    ) -> None:
        from config import COINDCX_MAX_POSITION_AGE_SEC

        ex = self.executor
        client = ex._client_factory(uid)
        # Ask for THIS user's live pairs, never "the account".  CoinDCX's
        # positions list is paged (page/size) and carries a row for every pair
        # ever traded, so an unfiltered page-1-of-100 can simply not contain a
        # live pair — and the loop below used to read that absence as FLAT,
        # finalise the record and cancel_all_for_position: the stop removed
        # from a live position, which then sat naked with its record closed
        # and nothing left to re-protect it (owner, HBARUSDT 2026-09-28).
        pairs = sorted({r.pair for r in records})
        currencies = tuple(sorted({r.margin_currency for r in records})) or ("USDT", "INR")
        try:
            rows = await client.positions(
                pairs=pairs, margin_currencies=currencies,
                size=max(10, 2 * len(pairs) * len(currencies)),
            )
        except Exception as exc:  # noqa: BLE001
            self.stats["positions_failed"] += 1
            log.info("CoinDCX reconcile uid={} positions failed: {}", uid, exc)
            return
        self.stats["users_checked"] += 1
        for rec in records:
            prow = _ex.position_row(rows, rec.pair, rec.margin_currency)
            if prow is None and rec.state not in (_pos.PENDING, _pos.ENTRY_UNCERTAIN):
                # Absent is UNKNOWN, not flat.  Finalising here cancels the
                # resting stop of a position that may be live, so a filled
                # record whose row we could not see is left exactly as it is
                # and counted; the next cycle asks again.
                self.stats["row_missing"] += 1
                log.warning(
                    "CoinDCX reconcile uid={} {} {}: no position row returned — "
                    "left untouched", uid, rec.pair, rec.margin_currency,
                )
                continue
            active = _ex._num((prow or {}).get("active_pos"))
            async with ex._lock(uid):
                fresh = await asyncio.to_thread(ex.store.get, uid, rec.signal_id)
                if fresh is None or not fresh.live:
                    continue
                rec = fresh

                if rec.state in (_pos.PENDING, _pos.ENTRY_UNCERTAIN):
                    if active != 0 and (active > 0) == (rec.side == "LONG"):
                        ex._apply_fill(rec, prow or {})
                        await ex._put(rec)
                        self.stats["entries_adopted"] += 1
                        await ex.protect(rec, client=client)
                        await ex.honour_close_request(rec, client)
                    elif now - rec.created_at > (
                        UNRESOLVED_GRACE_S if prow is not None else UNRESOLVED_ABSENT_GRACE_S
                    ):
                        # A returned flat row is evidence the entry never
                        # opened.  An ABSENT row is not (HBARUSDT): retiring
                        # on it abandons a position that may be live and
                        # naked, so absence waits far longer and is counted
                        # apart.
                        if prow is None:
                            self.stats["entries_retired_row_absent"] += 1
                        ex.forget_close_request(uid, rec.signal_id)
                        rec.state = _pos.REJECTED
                        rec.closed_at = now
                        rec.last_error = (rec.last_error + " | no position after grace").strip(" |")
                        await ex._put(rec)
                        self.stats["entries_retired"] += 1
                    continue

                if active == 0:
                    await ex.finalize_closed(
                        rec, client,
                        forced_reason=rec.close_reason if rec.state == _pos.CLOSING else None,
                    )
                    self.stats["closes_finalised"] += 1
                    continue

                # Live on the exchange.  The exchange's own triggers are the
                # evidence the stop rests — not our flag.
                sl_trigger = _ex._num((prow or {}).get("stop_loss_trigger"))
                tp_trigger = _ex._num((prow or {}).get("take_profit_trigger"))
                rec.sl_resting = sl_trigger > 0
                rec.tp_resting = tp_trigger > 0
                liq = _ex._num((prow or {}).get("liquidation_price"))
                if liq > 0:
                    rec.liquidation_price = liq

                opened = rec.opened_at or rec.created_at
                if now - opened > COINDCX_MAX_POSITION_AGE_SEC:
                    self.stats["age_cap_exits"] += 1
                    await ex._exit(rec, client, _ex.CLOSE_AGE_CAP,
                                   note=f"older than {COINDCX_MAX_POSITION_AGE_SEC}s")
                    continue
                if rec.state == _pos.CLOSING:
                    await ex._exit(rec, client, rec.close_reason or _ex.CLOSE_EXIT,
                                   note="retrying exit")
                    continue
                if not rec.sl_resting or not rec.tp_resting:
                    self.stats["protection_repairs"] += 1
                    await ex.protect(rec, client=client)
                    continue
                await ex._put(rec)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "last_cycle_at": self.last_cycle_at,
            "last_cycle_users": self.last_cycle_users,
            "stats": dict(self.stats),
        }


STATUS_PATH = os.getenv("COINDCX_STATUS_FILE", "data/coindcx_status.json")
_stream_manager: Any = None


def set_stream_manager(mgr: Any) -> None:
    global _stream_manager
    _stream_manager = mgr


def status_snapshot(rec: Optional["CoinDCXReconciler"] = None) -> Dict[str, Any]:
    """Everything ops needs to grade the venue, from THIS (engine) process."""
    from config import COINDCX_RECONCILE_INTERVAL_SEC, COINDCX_STREAM_ENABLED
    from src.venues.coindcx import dispatch as _dcx
    from src.venues.coindcx import instruments as _inst

    allowed = _dcx._allowed_uids()
    try:
        store = _pos.get_store().summary()
    except Exception as exc:  # noqa: BLE001
        store = {"error": type(exc).__name__}
    return {
        "written_at": time.time(),
        # The cadence travels with the artifact, so ops grades staleness on
        # the engine's own clock instead of inventing a bound (the /truth
        # defect, 2026-08-18).
        "reconcile_interval_sec": float(COINDCX_RECONCILE_INTERVAL_SEC),
        "execution_enabled": _dcx.execution_enabled(),
        "allow_list": {"active": allowed is not None, "size": len(allowed or ())},
        "open_to_all": allowed is None,
        "stream_enabled": bool(COINDCX_STREAM_ENABLED),
        "positions": store,
        "reconciler": (rec or get_reconciler()).snapshot(),
        "executor": _ex.counters(),
        "dispatch": _dcx.totals(),
        "instruments": _inst.get_registry().snapshot(),
        "stream": _stream_manager.snapshot() if _stream_manager is not None else None,
    }


def write_status_file(rec: Optional["CoinDCXReconciler"] = None) -> None:
    try:
        snap = status_snapshot(rec)
        os.makedirs(os.path.dirname(STATUS_PATH) or ".", exist_ok=True)
        tmp = STATUS_PATH + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(snap, fh, default=str)
        os.replace(tmp, STATUS_PATH)
    except Exception as exc:  # noqa: BLE001 — status is observability, never money
        _ex._fail_open("coindcx.reconciler.status_file", exc)


_RECONCILER: Optional[CoinDCXReconciler] = None


def get_reconciler() -> CoinDCXReconciler:
    global _RECONCILER
    if _RECONCILER is None:
        _RECONCILER = CoinDCXReconciler()
    return _RECONCILER


def set_reconciler_for_test(rec: Optional[CoinDCXReconciler]) -> None:
    global _RECONCILER
    _RECONCILER = rec
