# Handoff — Autonomous Regime-Adaptive Strategy Portfolio

**Branch:** `claude/signals-volume-quality-pjep8o` (repo `mkmk749278/360-v2`).
**Status:** Phase 1 foundation partly landed; the rest is specified below in build order.
**Owner directive that started this:** signals volume too low → don't just tighten gates
(low volume ≠ quality) → build a self-driving, regime-adaptive portfolio: many strategies
running in parallel in shadow on real data, viewable in ops, with an **autonomous
allocator** that switches/weights strategies by market context. One-person shop → it must
be autonomous and self-maintaining.

---

## The non-negotiable rail (CLAUDE.md)
- **Phase 1 is off the money path** — everything so far only *measures* (stamps observe-only
  fields, records shadow outcomes). It changes **no** live signal output.
- **Money-path pieces ship dark-first:** default-OFF flag + shadow-stamped + owner sign-off
  to activate (scoring/SL-TP shape/routing).
- **Cost discipline:** no new network/Firestore reads on the scanner/tick hot path. Stamps
  are O(1) in-memory; persistence is batched onto existing periodic loops.
- **Safety envelope always on:** blast-radius caps, kill switch, naked-position invariant.
- **Fail-open:** a stamp/measurement error must never change control flow.

---

## ✅ DONE and pushed

### Commit `7476996` — Layer A market-context engine + edge matrix
- **`src/market_context.py`** — pure, fail-neutral engine producing the `MarketContext`
  vector: `session` (Asia/London/NY/OVERLAP/OFF + weekend), `phase` (Wyckoff:
  MARKUP/MARKDOWN/ACCUMULATION/DISTRIBUTION/RANGE/QUIET/VOLATILE), `volatility`,
  `funding`, `rotation` (BTC-led proxy from `btc_state`). Exposes `context_key()` (the
  composite key the edge matrix + allocator route on) and `as_signal_fields()`.
- **`src/channels/base.py`** — `Signal` gains `mc_*` fields (observe-only stamp target).
- **`config/__init__.py`** — `MARKET_CONTEXT_ENABLED` (default ON, off money path).
- **`src/scanner/__init__.py`** — imports `build_market_context`; stamps the vector on
  every signal inside `_prepare_signal`, **right after the `BTC_STATE_ENABLED` block**
  (all inputs already warm → zero new reads). Gated by `MARKET_CONTEXT_ENABLED`.
- **`src/strategy_edge.py`** — `StrategyEdgeStore`: rolling per-`(strategy, context_key)`
  outcome store, Wilson-bounded edge in R, `matrix()` for ops, KEEP/verdict bands.
  Mirrors `CohortEdgeStore` persistence (writes only on outcome resolution). Module
  singleton `get_strategy_edge_store()`.
- Tests: `tests/test_market_context.py` (19), `tests/test_strategy_edge.py` (7).

### Commit `a02baff` — Layer C shadow ledger (Suppression Quality Audit)
- **`src/suppression_audit.py`** — stamps post-scoring suppressed candidates' geometry
  into a bounded in-memory buffer (O(1), no I/O), forward-measures TP1-before-SL against
  real candles, classifies WOULD_WIN/WOULD_LOSE/WOULD_EXPIRE, and computes per-gate
  EV-in-R + **KEEP/TUNE/DROP** verdict (`compute_gate_suppression_metrics`). Doubles as
  the shadow-ledger feed for the edge matrix via an `on_classified` hook
  (`candidate_outcome()` → `StrategyOutcome`). Singleton `get_store()`, helper
  `stamp_candidate(...)`. Env: `SUPPRESSION_AUDIT_*`.
- Tests: `tests/test_suppression_audit.py` (16). **All 42 new tests green; ruff clean.**

---

## 🔧 REMAINING WORK (in build order)

### 1. Wire Layer C end-to-end — *next immediate step* (off money path)
Everything below reuses modules already built.

**a. Scanner stamps at the 8 post-scoring suppression points** (`src/scanner/__init__.py`).
Add one helper `Scanner._stamp_suppressed_candidate(self, sig, gate_name)` that calls
`suppression_audit.stamp_candidate(gate_name=..., symbol=sig.symbol, channel=sig.channel,
setup_class=sig.setup_class, side=sig.direction.value, entry=sig.entry,
stop_loss=sig.stop_loss, tp1=sig.tp1, confidence=sig.confidence,
context_key=getattr(sig,'mc_context_key',''), regime=sig.entry_regime,
valid_for_minutes=getattr(sig,'valid_for_minutes',0))`, gated by a new
`SUPPRESSION_AUDIT_ENABLED` config flag (default True). Call it **immediately before**
each suppression `return`, at these gates (all have geometry already):
  - `_prepare_signal`: **QUIET_SCALP_BLOCK** reject, and the **confidence / component-floor**
    reject (`decision="filtered"`).
  - `_enqueue_signal` (each already writes an `enqueue_stage:*` counter): `active_dup`
    (only the real-suppress branch, NOT the shadow branch), `dispatch_cooldown`,
    `data_stale`, `dispatch_staleness`, `level_still_in_play`, `regime_kill`.
  - **Do NOT** stamp pre-scoring rejects (basic_filters etc.) — no tradeable geometry.

**b. Classify loop** — piggyback the existing `_invalidation_audit_loop` in `src/main.py`
(~5-min cadence, already has an in-memory `fetch_ohlc_since` closure over
`data_store.get_candles`). After the invalidation calls, add:
```python
from src import suppression_audit as _sa
from src.strategy_edge import get_strategy_edge_store, StrategyOutcome
def _feed_edge(rec):
    o = _sa.candidate_outcome(rec)
    if o:
        get_strategy_edge_store().record(StrategyOutcome(
            strategy=rec["setup_class"], context_key=rec["context_key"],
            side=rec["side"], won=o["won"], pnl_pct=o["pnl_pct"],
            r_multiple=o["r_multiple"], mfe_pct=o["mfe_pct"]))
_sa.get_store().classify_pending(fetch_ohlc_since=fetch_ohlc_since, on_classified=_feed_edge)
```
No new task, no new reads.

**c. Truth report** — `src/runtime_truth_report.py`: add `summarize_suppression_audit()`
+ a `## Suppression Quality Audit` section (per-gate WOULD_WIN%/EV/KEEP-TUNE-DROP,
mirroring the existing Invalidation per-rule ablation), and a `## Strategy×Context Edge
Matrix` section from `StrategyEdgeStore.matrix()`. Wire `scripts/build_truth_report.py`
to load `data/suppressed_candidates.json` + `data/strategy_edge_store.json`.

**d. Tests** — scanner integration (stamp fires on suppress, not on emit; active_dup
shadow branch stamps nothing); truth-report render.

### 2. Layer B — strategy portfolio interface (off money path)
Registry mapping each `setup_class` → context-affinity tags (which phases/sessions it's
built for). Strategy identity already flows via `setup_class`; keep evaluator geometry
untouched (B7). Consumed by the allocator + ops.

### 3. Layer F v1 — ops observability (repo `mkmk749278/360ce-ops`)
New HTMX page/partials: current **context vector**, **Strategy×Context edge matrix**,
per-strategy shadow PnL, suppression KEEP/TUNE/DROP. Expose via a new engine API endpoint
(`src/api/server.py`, returns `market_context` + `strategy_edge_store.matrix()` +
suppression metrics) OR read the data-volume JSON (`/engine-data`). Follow ops conventions
(`app/data_sources/`, `tojson` fallback, owner-auth).

### 4. Cross-cutting
- **Telegram→app decouple** (`src/signal_router.py` ~922–1029): move
  `push_signal_published` + `dispatch_signal_to_active_users` **out from under** the
  `if not delivered: return` Telegram guard, so app/FCM + per-user execution fire
  regardless of Telegram. App is primary surface (B1). **Owner-sign-off (routing).**
- **Register knobs** in `src/runtime_tunables.py`: `MARKET_CONTEXT_ENABLED`,
  `SUPPRESSION_AUDIT_ENABLED`, edge thresholds, + key volume knobs (QUIET penalty
  multiplier, dispatch/global cooldowns, min-confidence) for live ops control.

### 5. Layer D — autonomous allocator, recommendation mode (money path, OFF)
`src/strategy_allocator.py`: read current `MarketContext` × `StrategyEdgeStore` → decide
active strategies + weights; **logs "would-allocate", changes nothing live**. Safety
envelope math (per-strategy live cap, max concurrent, single owner master-arm). Observe
in ops before arming.

### 6. Phase 3 — new strategies + ATR/structure stop geometry (dark)
- New strategy units (enter shadow immediately, appear in the matrix): **range-fade
  (VAH/VAL)**, **funding/basis**, **mean-reversion**, **cascade-reversal**.
- **ATR/structure stop geometry** as a selectable geometry policy (stop beyond the
  liquidity pool = `max(structure level, ATR×mult)`, size scaled to hold dollar-risk
  constant via the existing `risk_scale` hook in `signal_dispatch`). A/B vs fixed-% per
  strategy in shadow. **Owner-sign-off (SL/TP shape).** Stamp the would-be stop on every
  signal first. — *This is the single biggest edge lever (see the Crypto Market Doctrine:
  our 0.8% stop sits inside a mid-cap's 15m noise band).*

### 7. Phase 4 — arm autonomy
Owner flips master-arm; allocator promotes/weights/demotes strategies live **within the
safety envelope**, auto-demoting on edge decay; kill switch overrides.

---

## Run / verify in a fresh session
```bash
# fresh clone has NO python deps — install once:
pip install -r requirements.txt --ignore-installed PyJWT
pip install pytest
# new-module tests:
python -m pytest tests/test_market_context.py tests/test_strategy_edge.py tests/test_suppression_audit.py -q
# full suite / lint:
python -m pytest tests/ -x --ignore=tests/test_deployment.py -q
ruff check src/ config/
python -c "import src.scanner; print('scanner import OK')"
```

## Companion reference docs (context for the "why")
- **Crypto Market Doctrine** (market phases, tiers, sessions, microstructure, how
  institutions actually make money, why fixed-% stops die) — delivered to owner in
  session; fold into `OWNER_BRIEF.md` as a doctrine section during WS0.
- **Signal-volume diagnosis** (three-stage funnel, every gate + knob, the three
  cross-cutting findings) — the evidence base for §1 and §4.
- Approved architecture plan: the 6-layer design (Layers A–F) this doc executes.

## Invariants to preserve on resume
Observe-only in Phase 1 · dark-first for money-path · no hot-path I/O · fail-open stamps ·
safety envelope always on · evaluator geometry ownership (B7) · commit author email
`noreply@anthropic.com` (already configured on the branch).
