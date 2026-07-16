"""Per-user PositionWorker lifecycle manager — the PR-11 worker manager.

Starts one PositionWorker per active live-mode user at engine boot,
wiring PositionFSM.handle_event as the ORDER_TRADE_UPDATE handler so
entry fills, SL hits, TP hits, and pre-TP fills all advance the FSM
in real time.

Also runs a **startup reconciliation** before each worker starts:
queries Binance positionRisk to detect any PENDING positions whose
entries filled while the engine was down (i.e. during the previous
reboot window).  Without this, those positions are stuck in PENDING
forever because the ORDER_TRADE_UPDATE fill event was never replayed.

Loops every 60s so a user who connects their Binance key after boot
gets a worker within one minute — no engine restart needed.

Doctrine note: wiring PositionFSM to PositionWorker activates the
BE-shift path (§3.2a).  Without this wiring, pre-TP fires via
trade_monitor but the SL is never moved to breakeven — the "near-zero
loss on residual" guarantee from the doctrine doesn't hold.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from src.utils import get_logger
from . import position_state as _ps
from .position_fsm import PositionFSM
from .position_worker import PositionWorker

log = get_logger("execution.worker_manager")

# Registry: firebase_uid → (worker, task).  Checked before double-starting.
_workers: Dict[str, Tuple[PositionWorker, asyncio.Task]] = {}

# In-flight reconcile+start tasks per uid (2026-07-16 audit).  A slow
# startup reconcile (Binance positionRisk) can outlive the 60s tick;
# without this guard the next tick scheduled a SECOND _reconcile_and_start
# for the same uid → two PositionWorkers / two user-data streams.  Also
# provides the strong reference that keeps the boot task from being
# garbage-collected mid-flight.
_boot_tasks: Dict[str, asyncio.Task] = {}


# ---------------------------------------------------------------------------
# Startup reconciliation
# ---------------------------------------------------------------------------


async def startup_reconcile_pending(firebase_uid: str) -> None:
    """Advance PENDING FSM positions that already filled on Binance.

    Queries ``GET /fapi/v2/positionRisk`` for the user.  For each
    PENDING FSM position where Binance reports a non-zero position
    amount for that symbol, the entry market order filled during the
    engine's downtime — advance the FSM to OPEN (or PRE_TP_FIRED if
    trade_monitor already fired the pre-TP close via the signal path).

    Soft-fail: any error is logged but does not prevent the worker
    from starting.  The reconciler's periodic 60s diff will catch
    further divergence.
    """
    if not _ps.is_initialised():
        return

    try:
        positions = _ps.list_positions_for_user(firebase_uid)
    except Exception as exc:
        log.warning(
            "worker_manager.reconcile: list_positions failed uid={} exc={}",
            firebase_uid, exc,
        )
        return

    pending = [p for p in positions if p.state == _ps.PositionState.PENDING]
    if not pending:
        return

    from src.security.signing_service import client as _sc
    client = _sc.SigningClient()
    try:
        resp = await client.binance_signed_get(
            firebase_uid=firebase_uid,
            base="futures",
            path="/fapi/v2/positionRisk",
        )
    except Exception as exc:
        log.warning(
            "worker_manager.reconcile: positionRisk request failed uid={} exc={}",
            firebase_uid, exc,
        )
        return

    if not resp.ok:
        log.warning(
            "worker_manager.reconcile: positionRisk error uid={} code={}",
            firebase_uid, resp.error_code,
        )
        return

    # Build symbol → positionAmt map from Binance response.
    binance_amts: Dict[str, float] = {}
    body = resp.binance_body or []
    if isinstance(body, list):
        for entry in body:
            if not isinstance(entry, dict):
                continue
            sym = str(entry.get("symbol", "")).upper()
            try:
                amt = float(entry.get("positionAmt", "0"))
            except (TypeError, ValueError):
                continue
            if sym:
                binance_amts[sym] = amt

    now = datetime.now(timezone.utc)
    for pos in pending:
        amt = binance_amts.get(pos.symbol.upper(), 0.0)
        if abs(amt) < 1e-9:
            # Entry not yet filled on Binance — leave PENDING.
            continue

        # Entry filled while engine was down.  Advance FSM.
        pos.filled_qty = abs(amt)
        # If trade_monitor already fired the pre-TP close (via
        # close_fsm_partial_for_signal which doesn't require OPEN state),
        # set PRE_TP_FIRED; otherwise OPEN.
        new_state = (
            _ps.PositionState.PRE_TP_FIRED
            if pos.pretp_fired
            else _ps.PositionState.OPEN
        )
        pos.state = new_state
        pos.last_event_at = now
        try:
            _ps.put_position(pos)
            log.info(
                "worker_manager.reconcile: PENDING→{} uid={} signal_id={} "
                "symbol={} qty={}",
                new_state.value, firebase_uid, pos.signal_id,
                pos.symbol, pos.filled_qty,
            )
        except Exception as exc:
            log.warning(
                "worker_manager.reconcile: put_position failed uid={} "
                "signal_id={} exc={}",
                firebase_uid, pos.signal_id, exc,
            )


# ---------------------------------------------------------------------------
# Worker lifecycle
# ---------------------------------------------------------------------------


async def start_user_worker(firebase_uid: str) -> Optional[asyncio.Task]:
    """Start a PositionWorker wired to PositionFSM for this user.

    Idempotent: if a worker is already running (task not done), returns
    without creating a second one.  Returns the asyncio.Task, or None if
    the worker was already running.
    """
    existing = _workers.get(firebase_uid)
    if existing is not None:
        _, task = existing
        if not task.done():
            return None  # already running

    fsm = PositionFSM(firebase_uid)
    worker = PositionWorker(firebase_uid, handler=fsm.handle_event)
    task = asyncio.create_task(
        worker.run(),
        name=f"position_worker_{firebase_uid[:12]}",
    )
    _workers[firebase_uid] = (worker, task)
    log.info("worker_manager: started PositionWorker uid={}", firebase_uid)

    from src.execution import reconciler as _rec_mod
    rec = _rec_mod.get_instance()
    if rec is not None:
        await rec.register_user(firebase_uid)

    return task


# ---------------------------------------------------------------------------
# Boot-time + ongoing loop
# ---------------------------------------------------------------------------


async def start_workers_for_active_users() -> None:
    """Background loop — start/maintain PositionWorkers for live-mode users.

    At boot:
    1. Waits 5s for Firestore/signing service to warm up after engine init.
    2. Lists all users with a connected Binance key.
    3. Filters to ``mode == "live"``.
    4. For each new user: runs startup reconciliation then starts worker.

    Then loops every 60s so newly-connected users get a worker without
    an engine restart.  Crashed workers (task.done()) are restarted on
    the next loop iteration.
    """
    # Small boot delay so Firestore + signing service connections settle.
    await asyncio.sleep(5)

    while True:
        try:
            _tick()
        except Exception:
            log.exception("worker_manager: unhandled error in loop")
        await asyncio.sleep(60)


def _tick() -> None:
    """Synchronous body of the per-60s loop.  Separated for testability."""
    from src.security import firestore_keystore as _fk
    from src.api.user_overrides import resolve_user_mode_uid

    if not _fk.is_initialised():
        return

    uids = _fk.list_active_uids()
    for uid in uids:
        try:
            mode = resolve_user_mode_uid(uid)
            if mode not in ("live", "both"):
                continue
        except Exception as exc:
            log.debug("worker_manager: mode lookup failed uid={} exc={}", uid, exc)
            continue

        existing = _workers.get(uid)
        if existing is not None and not existing[1].done():
            continue  # running fine

        boot = _boot_tasks.get(uid)
        if boot is not None and not boot.done():
            continue  # reconcile+start already in flight — don't double-boot

        # New user or crashed worker — schedule reconcile + start.
        task = asyncio.get_running_loop().create_task(
            _reconcile_and_start(uid),
            name=f"wm_boot_{uid[:12]}",
        )
        _boot_tasks[uid] = task
        task.add_done_callback(
            lambda t, _uid=uid: _boot_tasks.pop(_uid, None)
            if _boot_tasks.get(_uid) is t else None
        )


async def _reconcile_and_start(firebase_uid: str) -> None:
    """Run startup reconciliation then start the worker."""
    try:
        await startup_reconcile_pending(firebase_uid)
        await start_user_worker(firebase_uid)
    except Exception:
        log.exception(
            "worker_manager: _reconcile_and_start failed uid={}",
            firebase_uid,
        )


# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------


async def stop_all_workers() -> None:
    """Signal every running worker to stop.  Called on engine shutdown."""
    from src.execution import reconciler as _rec_mod
    rec = _rec_mod.get_instance()
    for uid, (worker, task) in list(_workers.items()):
        try:
            await worker.stop()
        except Exception:
            pass
        if rec is not None:
            try:
                await rec.unregister_user(uid)
            except Exception:
                pass
    log.info("worker_manager: stop_all_workers called ({} workers)", len(_workers))
