# LIVE SIGNAL EXPRESSION INVESTIGATION — 360_SCALP (Code-Path Audit)

- **Date:** 2026-04-14
- **Repository:** `mkmk749278/360-v2`
- **Branch investigated:** `main`
- **Model used:** GPT-5.3-CODEX
- **Scope statement:** Deep code-path audit of current `360_SCALP` live signal expression quality, lifecycle correctness, routing semantics, and governance alignment, with explicit separation of hard bugs vs policy mismatch vs architecture-quality concerns.

## 1) Executive summary

1. **WATCHLIST is not informational-only in current runtime.** For `360_SCALP`, WATCHLIST candidates (50–64) can be fully routed, posted to the active paid channel, inserted into `router._active_signals`, and processed by `TradeMonitor` like real trades (`src/scanner/__init__.py:2942-2953`, `src/signal_router.py:628-647,746`, `src/main.py:152-157`, `src/trade_monitor.py:367-403,537+`).
2. **This conflicts with doctrine in `OWNER_BRIEF.md`**, which explicitly states WATCHLIST should be “post to free channel only” (`OWNER_BRIEF.md:467-474`).
3. **Low-confidence admission is currently too permissive for lifecycle pollution** because WATCHLIST short-circuits before downstream component-floor checks and router min-confidence enforcement (for `360_SCALP` WATCHLIST) (`src/scanner/__init__.py:2942-2959`, `src/signal_router.py:628-639`).
4. **Duplicate lifecycle posting is plausibly caused by missing lifecycle idempotency guards**, plus multi-poster semantics for close events (status update + AI close summary on SL/TP3) (`src/trade_monitor.py:638-650,691-694,751-754,957-1009`).
5. **There is also an expiry double-poster path**: monitor expiry post and router safety-net expiry post can both fire (`src/trade_monitor.py:552-560` vs `src/scanner/__init__.py:853-856` + `src/signal_router.py:1109-1140`).
6. **Setup-family weakness concentration is structurally plausible**: `SR_FLIP_RETEST` and `CONTINUATION_LIQUIDITY_SWEEP` intentionally convert several gates to soft penalties; `TREND_PULLBACK_EMA` applies a base confidence lift and no comparable soft-penalty stack in-path (`src/channels/scalp.py:619-764,1746-2005,2544-2783`).

## 2) What is confirmed vs unconfirmed

### Confirmed

- WATCHLIST `360_SCALP` can enter active trade lifecycle machinery.
- WATCHLIST routing behavior is inconsistent with OWNER tier table (free-only doctrine).
- Lifecycle posting has **no explicit event idempotency layer** in `TradeMonitor`.
- SL/TP3 have two outbound posts by design (event update + AI “signal closed” post).
- Expiry can be posted by both monitor and router cleanup paths.
- Setup telemetry hooks exist to audit family concentration (`_setup_eval_counts`, `_setup_emit_counts`, `_scoring_tier_counters`).

### Unconfirmed from code alone

- Exact live proportion of `TREND_PULLBACK_EMA` / `SR_FLIP_RETEST` / `CONTINUATION_LIQUIDITY_SWEEP` in current VPS output.
- Whether observed duplicate INVALIDATED/SL events were caused by dual loop/process reality vs message-shape confusion.

(Instrumentation exists; this is observable via monitor logs and existing counters.)

## 3) WATCHLIST lifecycle truth

### Where WATCHLIST candidates are created

- Tier classification: `classify_signal_tier()` returns WATCHLIST for 50–64 (`src/scanner/__init__.py:383-402`).
- In `_prepare_signal()`, after scoring/penalties, tier is reclassified (`src/scanner/__init__.py:2743-2745`).
- WATCHLIST short-circuit accepts scalp-family candidates and returns them for enqueue (`src/scanner/__init__.py:2942-2953`).

### How they are formatted/routed

- Telegram formatting routes WATCHLIST to lightweight watchlist template (`src/telegram_bot.py:311-313,514-531`).
- Router processes queue items uniformly; for `360_SCALP` WATCHLIST it bypasses min-confidence floor (`src/signal_router.py:628-639`).
- Routing target is still channel map for `signal.channel`; all scalp channels map to `TELEGRAM_ACTIVE_CHANNEL_ID` (`config/__init__.py:770-791`, `src/signal_router.py:664-683`).

### Whether/how they become tracked active signals

- They are not “converted later”; they are already full `Signal` objects.
- After delivery, router always inserts into `_active_signals` (`src/signal_router.py:746`).
- Monitor consumes `router.active_signals` (`src/main.py:152-157`) and evaluates all signals without WATCHLIST exclusion (`src/trade_monitor.py:367-403,537+`).
- Router pulse loop explicitly skips WATCHLIST, confirming WATCHLIST may exist in active set (`src/signal_router.py:354-362`).

### Explicit answers

- **Is WATCHLIST just informational preview?** **No (for current `360_SCALP` runtime behavior).**
- **Can WATCHLIST become full active/tracked signals?** **Yes.**
- **Where/conditions?** Scanner WATCHLIST acceptance (`50–64`, scalp family) + router WATCHLIST min-conf bypass (only `360_SCALP`) + normal active registration (`src/scanner/__init__.py:2942-2953`; `src/signal_router.py:628-639,746`).
- **Correct under doctrine?** **No** vs OWNER tier table (“WATCHLIST → free only”) (`OWNER_BRIEF.md:467-474`).

## 4) Duplicate posting root cause

### All lifecycle post paths

- **Invalidation:** `_post_update("🔄 INVALIDATED...")` (`src/trade_monitor.py:657-669`).
- **SL / stop-style exits:** `_post_update(outcome_event)` + `_post_signal_closed(is_tp=False)` (`src/trade_monitor.py:634-650`).
- **TP updates:** TP1/TP2 updates (`src/trade_monitor.py:696-716,756-775`).
- **Final TP close:** `_post_update("FULL TP HIT")` + `_post_signal_closed(is_tp=True)` (`src/trade_monitor.py:677-695,737-755`).
- **Expiry updates:** monitor expiry post (`src/trade_monitor.py:552-560`) and router expiry notifier (`src/signal_router.py:1081-1140`, called from scanner/router loops: `src/scanner/__init__.py:853-856`, `src/signal_router.py:455-458`).

### Idempotency state

- No dedicated per-signal lifecycle-event dedupe ledger in monitor (no event key / no posted-state check).
- No explicit guard in `_evaluate_signal()` to short-circuit already-terminal statuses before posting again.

### Most likely causes

1. **By-design dual-post close semantics** (status post + AI close post) can look like duplicates for SL/TP3.
2. **Missing idempotency guard** allows duplicate terminal event posts if monitor loops overlap or duplicated processes evaluate same signal.
3. **Expiry has two separate posting components** (monitor + router cleanup), enabling real duplicate expiry messages.

### Smallest correct fix

1. Add **terminal-event idempotency guard** in `TradeMonitor` (per `signal_id` + terminal event type), checked before posting.
2. Add early short-circuit in `_evaluate_signal()` for already-terminal statuses.
3. Make `TradeMonitor.start()` idempotent (no second loop if already running).
4. Normalize close messaging policy: either keep dual-post but make second post explicitly “extended recap”, or gate it behind config to prevent duplicate-appearance complaints.

## 5) Confidence/tier/routing truth

- Tier model: A+ (80+), B (65–79), WATCHLIST (50–64) (`src/scanner/__init__.py:383-402`).
- `360_SCALP` min confidence set to 65 (`config/__init__.py:569-583`).
- WATCHLIST acceptance occurs before component floor gate (`src/scanner/__init__.py:2942-2959`).
- Router bypasses min-confidence for WATCHLIST only on `360_SCALP` (`src/signal_router.py:628-639`).
- Result: low-confidence 52–64 can enter active tracking too easily for `360_SCALP`.

**Mismatch:** OWNER doctrine says WATCHLIST should go free-only (`OWNER_BRIEF.md:467-474`), but implementation routes to active paid channel map and active monitor lifecycle.

## 6) Setup-family quality findings

### Telemetry availability

- Setup evaluation/emission counters: `_setup_eval_counts`, `_setup_emit_counts` logged every 100 cycles (`src/scanner/__init__.py:546-549,1173-1182`).
- Scoring-tier-by-setup counters: `_scoring_tier_counters` (`src/scanner/__init__.py:551+,1184-1191,2696-2705`).
- Suppression counters by reason and setup path also exist (`src/scanner/__init__.py:1071-1076,2696-2716`).

### Family-level code findings

- **TREND_PULLBACK_EMA**: strict trend/EMA/proximity/RSI/rejection/SMC support hard gates, but then +8 confidence bump and no in-path soft penalty stack (`src/channels/scalp.py:619-764`).
- **SR_FLIP_RETEST**: multiple formerly hard checks now soft penalties (proximity, wick, RSI, FVG/OB in fast regimes), plus +8 pre-score annotation (`src/channels/scalp.py:1746-2005`).
- **CONTINUATION_LIQUIDITY_SWEEP**: several weak-quality conditions are soft-penalized (RSI borderline, no FVG/OB, sweep recency) not hard-rejected (`src/channels/scalp.py:2559-2563,2675-2685,2779-2783`).

### Interpretation

- Structural gating is present, but `SR_FLIP_RETEST` and `CLS` intentionally allow borderline quality through soft penalties.
- Combined with WATCHLIST lifecycle admission, weak variants can still become tracked outcomes, which can inflate fast invalidation/SL sequences.

## 7) Governance mismatches

1. **WATCHLIST routing mismatch**
   - Doctrine: WATCHLIST free-only (`OWNER_BRIEF.md:467-474`).
   - Code: WATCHLIST `360_SCALP` goes through paid channel map and active lifecycle (`config/__init__.py:770-791`; `src/signal_router.py:664-683,746`; `src/trade_monitor.py:367+`).

2. **Comment-code mismatch in scanner WATCHLIST block**
   - Comment says “clear entry/SL/TP for zone-alert-only format,” but branch only populates context and returns signal; no clearing occurs (`src/scanner/__init__.py:2951-2953`).

3. **ACTIVE_CONTEXT wording drift**
   - Says WATCHLIST handling is “preserved as intended downstream” (`docs/ACTIVE_CONTEXT.md:48`) while OWNER doctrine still states free-only action.

## 8) Immediate bugs to fix now

1. **Lifecycle idempotency bug (terminal events):** add event dedupe and terminal-status short-circuit in `TradeMonitor`.
2. **Expiry duplicate source:** consolidate expiry ownership (monitor-only or router-only), not both.
3. **WATCHLIST governance bug:** enforce free-only routing for WATCHLIST per OWNER doctrine (or explicitly amend doctrine if policy changed). Right now policy and runtime diverge.
4. **Scanner WATCHLIST comment-code mismatch:** either implement level-clearing behavior or correct misleading comment.

## 9) Best next PR recommendation (ranked)

### PR-1 (highest): **Lifecycle idempotency and duplicate-post hardening**

Why first:
- Directly addresses visible production symptom (duplicate INVALIDATED/SL-style outputs).
- Smallest high-confidence patch surface in `trade_monitor.py` (+ possible single router expiry ownership adjustment).
- Low policy risk, high correctness gain.

### PR-2: **WATCHLIST routing/lifecycle policy alignment**

Why second:
- Fixes core governance contradiction and low-quality lifecycle pollution.
- Requires explicit product decision if doctrine changed after PR-18; implementation should follow agreed policy (free-only vs paid-but-untracked vs paid-and-tracked).

### PR-3: **Family-specific quality tightening (targeted, evidence-gated)**

Why third:
- Should be driven by telemetry after policy and lifecycle correctness are fixed.
- Candidate focus: `SR_FLIP_RETEST` and `CONTINUATION_LIQUIDITY_SWEEP` soft-penalty boundaries; avoid broad threshold loosening/tightening without fresh evidence.

## 10) Deferred items that should NOT be changed yet

1. Global confidence threshold overhauls.
2. Broad MTF gate redesign without fresh post-fix telemetry.
3. Major evaluator rewrites for the three setup families before lifecycle/policy bugs are corrected.
4. Cross-system architecture redesign (queue/router/monitor) when current failures are solvable by narrow idempotency + policy-alignment fixes.

---

## Appendix A — Validation baseline during this audit

- `python3 -m ruff check .` → fails with pre-existing repository-wide lint issues (unrelated to this doc-only change).
- `python3 -m pytest -q` → fails with many pre-existing test failures (unrelated to this doc-only change).

These failures were present in baseline validation and were not modified in this investigation task.
