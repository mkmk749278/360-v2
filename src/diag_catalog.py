"""A NAMED catalog of engine diagnostics and safe actions — never a shell.

Owner, 2026-08-19: *"what amount send commands to vps from ops, then you can
directly interact with engine send commands accordingly fix problems"*.

The answer is a catalog, not a command line, and the reason is specific rather
than general caution. The owner's own security argument is that the Binance key
is IP-whitelisted to this box, futures-only, and cannot withdraw — which is
correct against a **stolen** key used from anywhere else, and does not apply to
code executing *on* the whitelisted host. Futures permission is not
symbol-scoped either. So arbitrary execution here does not risk a withdrawal; it
risks a position. A fixed catalog with no shell, no eval and no interpolated
arguments is what keeps a leaked read-only code to disclosure and disruption.

**Two kinds, and the split is the whole safety argument:**

* ``read`` — observes and returns. No mutation, anywhere.
* ``action`` — mutates something **reversible and off the money path**: flush a
  measurement ledger, drop a rebuildable cache, force a snapshot publish,
  re-seed one symbol's candles from REST.

**What is deliberately absent, and must stay absent.** Nothing here places,
cancels or modifies an order; reads a key or any secret; touches the kill
switch, auto-execution mode, position FSM or per-user settings; or writes
anything a subscriber sees. Those live in ``/control`` behind the owner's own
login with a PRG confirm and an audit row, and that is not an accident of
layering — it is the audit trail. ``tests/test_diag_catalog.py`` asserts the
absence structurally rather than trusting this paragraph.

Every entry fails open with a NAMED reason: a diagnostic that raises must not
take down the loop it is describing, and "could not read" must never render as
a zero.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from src.utils import get_logger

log = get_logger(__name__)

#: Substrings that may never appear in an entry key. Not a security control on
#: their own — the catalog is an allow-list, which is the control — but a
#: tripwire for the next person adding an entry, asserted in the test suite.
FORBIDDEN_IN_KEY = ("order", "key", "secret", "withdraw", "kill", "mode", "close")


@dataclass
class Entry:
    key: str
    label: str
    kind: str                      # "read" | "action"
    summary: str
    fn: Callable[["Ctx"], Dict[str, Any]]
    #: What this changes, in the operator's words. Empty for a read — and the
    #: test asserts every action has one, because "reversible" is a claim
    #: somebody has to have written down and be accountable for.
    effect: str = ""
    needs: List[str] = field(default_factory=list)


@dataclass
class Ctx:
    """Everything an entry may touch, passed in rather than imported.

    Entries take the engine through this object so a missing collaborator is a
    named refusal rather than an AttributeError halfway through a mutation.
    """
    engine: Any
    args: Dict[str, Any]

    def need(self, *path: str) -> Any:
        obj = self.engine
        for part in path:
            obj = getattr(obj, part, None)
            if obj is None:
                raise LookupError(f"engine has no {'.'.join(path)}")
        return obj


def actions_enabled() -> bool:
    """Read the switch at CALL time, never at import.

    A module-level snapshot would freeze whatever the process booted with, and
    the point of the switch is that the owner can close the action half without
    a redeploy.
    """
    from config import DIAG_ACTIONS_ENABLED

    return bool(DIAG_ACTIONS_ENABLED)


_REGISTRY: Dict[str, Entry] = {}


def register(entry: Entry) -> None:
    if entry.key in _REGISTRY:
        raise ValueError(f"duplicate diag catalog key: {entry.key}")
    _REGISTRY[entry.key] = entry


def catalog() -> List[Dict[str, Any]]:
    """The catalog as data, for ops to render. One writer, one reader.

    Ops never keeps its own list of what exists — that is the drifting-mirror
    defect this system has paid for under several names. A page renders what
    this returns, and an entry ops has never heard of still appears.
    """
    on = actions_enabled()
    return [
        {"key": e.key, "label": e.label, "kind": e.kind,
         "summary": e.summary, "effect": e.effect, "needs": e.needs,
         # Rendered so a switched-off action reads as OFF rather than as
         # missing: "not on offer" and "not available today" have different
         # next moves, and a vanished entry looks like a deploy problem.
         "enabled": True if e.kind == "read" else on}
        for e in sorted(_REGISTRY.values(), key=lambda e: (e.kind != "read", e.key))
    ]


def run(key: str, engine: Any, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute one catalog entry by name. Unknown names are refused, not guessed."""
    entry = _REGISTRY.get(key)
    if entry is None:
        return {"ok": False, "key": key, "error": "unknown catalog entry",
                "known": sorted(_REGISTRY)}
    # The action switch is enforced HERE, at the only place an entry can run —
    # never only where the list is rendered. A control that hides a button and
    # still honours the request is a control in appearance only, and this path
    # is reachable by anything holding the endpoint.
    if entry.kind == "action" and not actions_enabled():
        return {"ok": False, "key": key, "kind": entry.kind, "label": entry.label,
                "error": "actions are switched off (DIAG_ACTIONS_ENABLED=false)",
                "result": {}}
    t0 = time.perf_counter()
    try:
        payload = entry.fn(Ctx(engine=engine, args=dict(args or {})))
        ok, err = True, ""
    except LookupError as exc:          # a collaborator this process does not have
        payload, ok, err = {}, False, f"unavailable: {exc}"
    except Exception as exc:            # noqa: BLE001 — reported, never raised at the loop
        log.exception("diag catalog entry {} failed", key)
        payload, ok, err = {}, False, f"{type(exc).__name__}: {exc}"
    return {
        "ok": ok, "key": key, "kind": entry.kind, "label": entry.label,
        "error": err, "result": payload,
        "took_sec": round(time.perf_counter() - t0, 3),
        "ran_at": time.time(),
    }


# ---------------------------------------------------------------------------
# READ entries — observe and return. No mutation anywhere below this line.
# ---------------------------------------------------------------------------

def _scan_executor(ctx: Ctx) -> Dict[str, Any]:
    """Is the scan executor queued, and can its workers actually run?

    The engine breached a 120s deadline on 2026-08-19 while using 1.2 of a 3.2
    core quota. Capacity was not the constraint, and the two candidates —
    GIL-bound Python across the workers, or I/O waits inside a timed stage —
    are told apart by whether work is QUEUED while cores sit idle.
    """
    ex = ctx.need("_scanner", "_scan_executor")
    q = getattr(ex, "_work_queue", None)
    threads = getattr(ex, "_threads", None)
    return {
        "max_workers": getattr(ex, "_max_workers", None),
        "threads_alive": sum(1 for t in (threads or []) if t.is_alive()) if threads else None,
        "queue_depth": q.qsize() if q is not None else None,
        "note": (
            "queue_depth persistently > 0 with CPU well under quota is the "
            "GIL-bound signature; a shallow queue with long stages points at I/O"
        ),
    }


def _firestore_reads(ctx: Ctx) -> Dict[str, Any]:
    """Which call sites are spending the Firestore daily read allowance.

    Documents, not calls — Firestore bills per document returned, so a
    collection-group query is not one read.  ``per_day`` extrapolates from this
    process's uptime against the 50,000/day no-cost quota that ran out at
    00:41 UTC on 2026-09-02 and took auto-trade down for every user.

    Reports which PROCESS it describes: in isolated mode the engine and the api
    container keep separate counters, and the api one serves every surface the
    owner reads.
    """
    from src import firestore_reads as _fsr

    return _fsr.snapshot()


def _firestore_projection(ctx: Ctx) -> Dict[str, Any]:
    """What today's reads cost at the 1,000-member auto-trade target.

    Every per-user read is invisible at one user.  ``worker_manager``'s roster
    scan cost 1,440 reads a day on this account and 1.44 MILLION at the target,
    and nothing in the console, the bill or the census said so — a cost model
    that only describes today cannot stop the bill it exists to stop.

    Arithmetic on a measurement, not a measurement.  Each site is marked
    ``scales_with_members`` from what the CODE does, and an unrecognised site is
    assumed to scale, which is the safe direction: a flat site wrongly scaled
    overstates a bill somebody then checks, while a per-user site wrongly called
    flat is invisible until the subscribers arrive.

    ``current_members`` defaults to 1.  Pass the real connected-key count for a
    reading that is not an upper bound.
    """
    from src import firestore_reads as _fsr

    try:
        members = int(ctx.args.get("members") or _fsr.TARGET_MEMBERS)
    except (TypeError, ValueError):
        members = _fsr.TARGET_MEMBERS
    try:
        current = int(ctx.args.get("current_members") or 1)
    except (TypeError, ValueError):
        current = 1
    return _fsr.project(members=members, current_members=current)


def _control_generation(ctx: Ctx) -> Dict[str, Any]:
    """Is the cross-process invalidation channel alive?

    The three control documents are no longer re-read on a TTL; a write bumps a
    Redis generation and every reader drops its cache on the next tick.  That
    makes a dead channel invisible in the ordinary case — the defensive TTL
    still converges, just minutes late — so the counters are the only thing
    that can say the kill switch is converging on the slow path.

    ``bumps`` climbing with ``polls`` at zero means the readers are not
    listening; ``poll_failures`` climbing means Redis is refusing, and every
    flip is then bounded by the TTL rather than by the tick.
    """
    from src import control_generation as _gen

    return _gen.stats()


def _edge_store_internals(ctx: Ctx) -> Dict[str, Any]:
    """What is actually inside an edge-store cell, and what does it cost to write?

    Measured 2026-08-19: the file is ~39 MB over ~11,261 cells, so the average
    cell is ~3.5 KB — about 7x a synthetic cell of 50 floats. Serialising it
    holds the GIL for ~1.85s, and `asyncio.to_thread` does not free the loop for
    that, so payload size is the direct lever. This says where the bytes are.
    """
    from src.strategy_edge import get_strategy_edge_store

    store = get_strategy_edge_store()
    with getattr(store, "_lock"):
        records = dict(getattr(store, "_records"))
    lens = sorted((len(v) for v in records.values()), reverse=True)
    biggest = sorted(records.items(), key=lambda kv: -len(kv[1]))[:10]
    return {
        "cells": len(records),
        "records_total": sum(lens),
        "window": getattr(store, "_window", None),
        "cell_len_max": lens[0] if lens else 0,
        "cell_len_median": lens[len(lens) // 2] if lens else 0,
        "cells_at_window": sum(1 for n in lens if n >= (getattr(store, "_window", 0) or 0)),
        "biggest_cells": [{"cell": " | ".join(map(str, k)), "records": len(v)} for k, v in biggest],
        "flush_health": store.flush_health(),
    }


def _candle_census(ctx: Ctx) -> Dict[str, Any]:
    """Per-timeframe bucket census, and how many sit at the 1,000-bar cap.

    A capped bucket used to serve frozen indicators forever; the content key
    fixed that, and this is how much of the book was ever exposed.
    """
    from src.historical_data import _MAX_CANDLES_PER_BUCKET as cap

    store = ctx.need("data_store")
    data = getattr(store, "_data", None) or getattr(store, "data", None)
    if data is None:
        raise LookupError("data store exposes no bucket map")
    per_tf: Dict[str, Dict[str, int]] = {}
    for _symbol, tfs in dict(data).items():
        for tf, cd in dict(tfs).items():
            closes = cd.get("close") if isinstance(cd, dict) else None
            n = len(closes) if closes is not None else 0
            row = per_tf.setdefault(str(tf), {"buckets": 0, "at_cap": 0, "empty": 0})
            row["buckets"] += 1
            if n >= cap:
                row["at_cap"] += 1
            if n == 0:
                row["empty"] += 1
    return {"bucket_cap": cap, "per_timeframe": per_tf}


def _loop_snapshot(ctx: Ctx) -> Dict[str, Any]:
    """Scan-cycle, writer, edge-store and host counters in one read."""
    from src.api.snapshot_writer import _host_resources, _loop_health

    return {"loop_health": _loop_health(ctx.engine), "host_resources": _host_resources()}


def _ai_governor(ctx: Ctx) -> Dict[str, Any]:
    """The AI Trade Governor's live state — bounds, budgets, arms and refusals.

    Read from the ENGINE process on purpose. The api container has never
    evaluated a candidate and cannot see the arms or the position index, so a
    version of this assembled there would report a healthy zero
    (`INDEX COLD`, and the promotion census before it).
    """
    from src.execution import ai_governor as _aig

    return _aig.build_diag()


def _fail_open(ctx: Ctx) -> Dict[str, Any]:
    """Every fail-open exception site and its count — the silent-failure ledger."""
    from src import fail_open

    snap = getattr(fail_open, "snapshot", None)
    if not callable(snap):
        raise LookupError("fail_open exposes no snapshot()")
    return {"sites": snap()}


def _asyncio_tasks(ctx: Ctx) -> Dict[str, Any]:
    """Which engine tasks exist, and which have died.

    A task that raised and was never awaited disappears silently; the loop keeps
    running with one of its legs gone.
    """
    import asyncio

    try:
        tasks = asyncio.all_tasks()
    except RuntimeError as exc:
        raise LookupError(f"no running loop in this process: {exc}") from exc
    rows = []
    for t in tasks:
        rows.append({
            "name": t.get_name(),
            "done": t.done(),
            "cancelled": t.cancelled() if t.done() else False,
        })
    return {"count": len(rows), "tasks": sorted(rows, key=lambda r: r["name"])}


def _dispatch_funnel(ctx: Ctx) -> Dict[str, Any]:
    """Where every delivered signal went, per user, since boot.

    Owner, 2026-08-31: *"seems to be every signal is not trading in binance
    don't know why some hit trading"*. Both fan-outs have counted their own
    outcomes all along and neither published the breakdown anywhere: the
    live one's ``dispatch_totals()`` had a single consumer — a blackout
    probe whose healthy message printed ``attempts`` and ``fanouts`` and
    neither the placed count nor the skip reasons — and the paper one had no
    counters at all until this change.

    Reads two module-level dicts. Touches no order, no key and no position.
    """
    from src.execution import paper_book_registry as _paper
    from src.execution import signal_dispatch as _live

    live = _live.dispatch_totals()
    paper = _paper.paper_dispatch_totals()
    _boot = getattr(ctx.engine, "_boot_time", 0.0)

    def _split(totals: Dict[str, float], prefix: str) -> Dict[str, float]:
        return {
            k.split(":", 1)[1]: v
            for k, v in totals.items()
            if k.startswith(prefix) and v > 0
        }

    live_attempts = float(live.get("attempts_total", 0.0))
    live_placed = float(live.get("placed_total", 0.0))
    return {
        # Counters are monotonic SINCE BOOT and reset on every restart, so a
        # small number here is a young process rather than a quiet tape. The
        # uptime is beside them because reading one without the other is how
        # a restart reads as a blackout.
        "uptime_sec": round(
            max(0.0, time.monotonic() - float(_boot or 0.0)) if _boot else 0.0,
            1,
        ),
        "live": {
            "fanouts": float(live.get("fanouts_total", 0.0)),
            "fanouts_with_users": float(
                live.get("fanouts_with_users_total", 0.0)
            ),
            "fanouts_empty_roster": float(
                live.get("fanouts_empty_roster_total", 0.0)
            ),
            "placed": live_placed,
            "rejected": live_attempts - live_placed,
            # Skipped users never reach the order path, so they write no
            # per-user row and are invisible to the app's activity card for
            # every reason except the two per-signal preferences. This is
            # the only place the account-level ones are counted at all.
            "skipped": float(live.get("skipped_total", 0.0)),
            "skip_reasons": _split(live, "skip:"),
            "reject_classes": _split(live, "rejected:"),
        },
        "paper": {
            "fanouts": float(paper.get("fanouts_total", 0.0)),
            "fanouts_with_users": float(
                paper.get("fanouts_with_users_total", 0.0)
            ),
            "considered": float(paper.get("considered_total", 0.0)),
            "opened": float(paper.get("opened_total", 0.0)),
            "skipped": float(paper.get("skipped_total", 0.0)),
            "skip_reasons": _split(paper, "skip:"),
            "reject_classes": _split(paper, "rejected:"),
        },
        "note": (
            "live.skipped counts users the dispatcher declined BEFORE the "
            "order path; only path_pref and regime_pref persist a per-user "
            "row (the account-level ones would be one Firestore write per "
            "fan-out per non-live user forever). paper.fanouts stays at 0 "
            "unless the engine-wide auto-execution mode is 'paper' — the "
            "per-user paper books are that mode's order manager, so a mode "
            "change stops them without stopping live dispatch."
        ),
    }


for _e in (
    Entry("read.scan_executor", "Scan executor queue", "read",
          "Worker count, live threads and queued work — tells a GIL-bound loop "
          "from an I/O-bound one.", _scan_executor),
    Entry("read.firestore_reads", "Firestore read census", "read",
          "Document reads per call site against the 50k/day no-cost quota — "
          "which loop is spending the allowance, and in which process.",
          _firestore_reads),
    Entry("read.firestore_projection", "Firestore cost at 1,000 members", "read",
          "Today's measured reads scaled to the auto-trade target, split into "
          "the sites that grow with subscribers and the ones that do not, "
          "against the 50k/day free allowance.", _firestore_projection),
    Entry("read.control_generation", "Control invalidation channel", "read",
          "Bumps, polls and failures on the Redis generation that replaced the "
          "5s TTLs — says whether a kill-switch flip converges on the tick or "
          "on the slow defensive bound.", _control_generation),
    Entry("read.ai_governor", "AI Trade Governor", "read",
          "Arms, verdict mix, refusals by name, spend against the daily cap, "
          "and whether the panic arm's position ceiling is set — it refuses "
          "while that is zero. Carries `blindness` (how much context the recent "
          "verdicts actually had, book and flow counted apart because their "
          "fixes differ) and `scorecard` (every thesis graded against the "
          "closed-signal record, per arm, with the MAINTAIN baseline beside it "
          "and no blended figure).", _ai_governor),
    Entry("read.edge_store", "Edge store internals", "read",
          "Cell count, record counts and the biggest cells — where the 39 MB "
          "of serialisation cost lives.", _edge_store_internals),
    Entry("read.candle_census", "Candle bucket census", "read",
          "Buckets per timeframe and how many sit at the 1,000-bar cap.",
          _candle_census),
    Entry("read.loop", "Loop + host counters", "read",
          "Scan cycle, snapshot writer, edge store and CPU-against-quota in one "
          "read.", _loop_snapshot),
    Entry("read.fail_open", "Fail-open sites", "read",
          "Every swallowed exception site and its count.", _fail_open),
    Entry("read.tasks", "Asyncio task census", "read",
          "Engine tasks, and which have finished or been cancelled.",
          _asyncio_tasks),
    Entry("read.dispatch_funnel", "Signal → order funnel", "read",
          "Per delivered signal, how many users got an order placed, how "
          "many were rejected and how many were skipped before the order "
          "path — with the reasons, for both the live and paper fan-outs.",
          _dispatch_funnel),
):
    register(_e)


# ---------------------------------------------------------------------------
# ACTION entries — each mutates something REVERSIBLE and off the money path.
#
# The bar for adding one: if it fails at the worst possible moment, the engine
# recomputes or re-fetches what it lost and no position, order, key or
# subscriber-visible value is touched. Anything that cannot clear that bar
# belongs in /control behind the owner's login, not here.
# ---------------------------------------------------------------------------

def _flush_ledgers(ctx: Ctx) -> Dict[str, Any]:
    """Force every measurement ledger to persist now.

    Reversible in the only sense that matters: it writes what is already in
    memory. The failure mode it repairs is the one this system has paid for
    twice — a ledger stamped and never flushed, reading UNREADABLE on a page
    the owner was told to check.
    """
    out: Dict[str, Any] = {}
    modules = (
        "sar_live_shadow", "dark_emission", "entry_features",
        "structural_snap", "structural_veto", "atr_trail_live",
        "price_action_lane",
    )
    for name in modules:
        try:
            mod = __import__(f"src.{name}", fromlist=["get_ledger"])
            getter = getattr(mod, "get_ledger", None)
            if not callable(getter):
                out[name] = "no get_ledger()"
                continue
            ledger = getter()
            flush = getattr(ledger, "flush", None)
            if not callable(flush):
                out[name] = "no flush()"
                continue
            try:
                flush(force=True)
            except TypeError:
                flush()
            out[name] = "flushed"
        except Exception as exc:  # noqa: BLE001 — one ledger must not stop the rest
            out[name] = f"{type(exc).__name__}: {exc}"
    return {"ledgers": out}


def _flush_edge_store(ctx: Ctx) -> Dict[str, Any]:
    """Persist the Layer-C edge store if it is dirty.

    Writes in-memory state to disk. Costs ~1.85s of event loop at the current
    payload size, so it is an explicit action rather than something a page does
    on render.
    """
    from src.strategy_edge import get_strategy_edge_store

    store = get_strategy_edge_store()
    before = store.flush_health()
    store.flush_if_dirty()
    return {"before": before, "after": store.flush_health()}


def _drop_indicator_cache(ctx: Ctx) -> Dict[str, Any]:
    """Drop the indicator and SMC caches. They rebuild on the next scan.

    Pure recomputation: the caches hold derived values only, so the cost is one
    slower cycle and the benefit is a clean read when a cache key is suspected.
    """
    scanner = ctx.need("_scanner")
    dropped = {}
    for attr in ("_indicator_cache", "_smc_cache"):
        cache = getattr(scanner, attr, None)
        if cache is None:
            dropped[attr] = "absent"
            continue
        dropped[attr] = len(cache)
        cache.clear()
    return {"dropped": dropped,
            "note": "derived values only — the next scan recomputes them"}


def _reseed_symbol(ctx: Ctx) -> Dict[str, Any]:
    """Re-fetch one symbol's candles from Binance REST.

    Repairs the frozen-series class this system has hit repeatedly on rotated-out
    movers. Bounded to ONE symbol per call by construction: a whole-universe
    re-seed is a rate-limit event against an exchange that has IP-banned this box
    before, so it is not on offer here at any argument.
    """
    symbol = str(ctx.args.get("symbol") or "").upper().strip()
    if not symbol or not symbol.isalnum():
        return {"refused": "a single alphanumeric symbol is required",
                "given": ctx.args.get("symbol")}
    store = ctx.need("data_store")
    seed = getattr(store, "seed_symbol", None)
    if not callable(seed):
        raise LookupError("data store exposes no seed_symbol()")
    return {"symbol": symbol, "queued": True,
            "note": "seed_symbol invoked; the next scan reads the refreshed bucket",
            "result": str(seed(symbol))[:400]}


for _e in (
    Entry("action.flush_ledgers", "Flush measurement ledgers", "action",
          "Force every measurement ledger to persist what it holds in memory.",
          _flush_ledgers,
          effect="Writes in-memory ledger rows to disk. Nothing is deleted; a "
                 "ledger already flushed is unchanged."),
    Entry("action.flush_edge_store", "Flush the edge store", "action",
          "Persist Layer C if dirty.", _flush_edge_store,
          effect="Writes in-memory cells to disk and costs ~2s of event loop at "
                 "current size. No cell is dropped."),
    Entry("action.drop_indicator_cache", "Drop indicator + SMC caches", "action",
          "Clear derived caches so the next scan recomputes them.",
          _drop_indicator_cache,
          effect="Discards derived values only. The next scan cycle runs slower "
                 "and rebuilds them; no stored data is lost."),
    Entry("action.reseed_symbol", "Re-seed one symbol's candles", "action",
          "REST re-fetch for a single symbol whose series has frozen.",
          _reseed_symbol,
          effect="One REST call for one symbol, replacing that bucket with fresh "
                 "bars. Bounded to one symbol; no universe-wide re-seed exists.",
          needs=["symbol"]),
):
    register(_e)
