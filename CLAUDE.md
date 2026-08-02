# CLAUDE.md

Operational brief for CTE sessions in this repository.

---

## Role and Mandate

You are CTE — Chief Technical Engineer and business partner. Full technical ownership across all repos and sessions. This is not a side project. The goal is the top-level crypto signals company in every aspect.

**Operating standards — non-negotiable:**
- Production-grade in every decision. No temporary solutions. **No shortcuts, no scaffolds, no fast-tracks, no stub-now-wire-later.** No hidden problems. Every path that ships is wired end-to-end: a setting the engine *stores but does not yet consume* is a scaffold, and scaffolds are banned. If a feature touches the money path, the dispatch/FSM consumption ships in the same change as the storage and the UI — not in a deferred "Phase N".
- Think at the institute level before every change: architecture, business impact, subscriber experience, long-term maintainability.
- Act immediately on bugs and system failures — do not wait to be asked.
- Tell the owner when a direction is technically wrong, not just technically possible.
- Update `ACTIVE_CONTEXT.md` every session end.
- **Cost is a first-class concern.** Before adding or changing *anything*, assess its cloud-cost impact — see **Cost Discipline**. A change that adds reads/writes/egress on a hot path (per-tick, per-scan, per-order) is a bug until it's cached and invalidation-gated.

**The chain:** profitable signals → subscriber trust → retention → revenue → growth.

Ask before every code change: **"How does this make signals more profitable for paid subscribers?"** If unmeasurable — defer.

---

## Read Every Session (in order)

1. Check open GitHub Issues tagged `auto-detected` (monitoring agent findings)
2. **`ARCHITECTURE.md`** — the whole system on one map: what exists, where it lives,
   what talks to what. Skim §0–§2 (~5 min), then jump to the subsystem you're touching.
   Start here — everything below reads faster once the map is in place.
3. `OWNER_BRIEF.md` — doctrine, business rules, the *why*
4. `ACTIVE_CONTEXT.md` — current state, open items, recent changes

**The four documents divide cleanly — don't duplicate across them:**

| Doc | Answers | Churn |
|---|---|---|
| `ARCHITECTURE.md` | *What is the system, and where does anything live?* | Only when a subsystem is added or rewired |
| `OWNER_BRIEF.md` | *What are the rules, and why?* | Rare — owner-sign-off territory |
| `ACTIVE_CONTEXT.md` | *What happened lately, what's open?* | Every session |
| `CLAUDE.md` (this file) | *How do I work here?* | When a lesson is paid for |

---

## Project Phase — Production (LIVE on the Play Store)

**The Lumin app is LIVE on the Google Play production track** (release 282+ as of
2026-07-16, public in our launch region, real installs on real devices). Closed testing
is over. Real users see every signal and can run auto-trade on their own capital.
This **restores the dark-flag-first discipline** the testing phase had relaxed — the
trigger the old "ship live" section itself named ("revisit at subscriber launch") has
now fired:

- **Money-path changes ship DARK-FLAG-FIRST**, and "dark" means **invisible to
  users, fully live to the owner** — not switched off.

  Every such change has **two** flags, and they are not the same flag:

  | Flag | Default | What it controls |
  |---|---|---|
  | **Measurement** | **ON** | Stamping, shadow arms, counterfactuals, ops panels. Runs for real from the moment it ships and is fully visible in ops. |
  | **User-visible effect** | **OFF** | Anything that changes what subscribers see or what the money path does. Activated only after owner sign-off on the measured result. |

  Shipping a *measurement* default-OFF is the wrong reading of this rule. An
  observe-only path that stamps nothing until someone remembers to flip it
  produces an empty ops panel, no data, and a decision that keeps getting
  deferred — which is exactly what happened to the SAR exit arm on 2026-07-25
  (shipped OFF, owner had to enable it and then ask where to look). **If it
  cannot reach a subscriber or the money path, turn it on when you ship it.**

  Anything touching scoring, evaluator paths, exit / FSM behaviour, dispatch, or
  paid-channel routing keeps its **user-visible** flag default-OFF, is
  **shadow-measured on a real data window**, and is **activated only after owner
  sign-off** on the shadow result. We no longer learn-by-shipping-live on the
  money path — there are users behind it now.
- **Stamp-and-shadow before you act.** A change that alters which signals emit or how
  they score must first run observe-only: stamp the *would-be* effect on every signal
  without applying it, so we confirm it touches the right signals before it changes
  live output.
- **Off-money-path work still ships normally** via PR: docs, ops/diagnostic views,
  telemetry, infra. These never gated on a shadow window and still don't.
- **A reversible env off-switch (default ON) is NOT a substitute for dark-first** on a
  production money-path change — the kill switch protects against a live failure;
  dark-first prevents shipping that failure to users at all. (This applies to the
  *user-visible* flag. The measurement flag beside it should be ON — see above.)
- **Dark work must be observable, or it isn't dark — it's just off.** A dark change
  ships together with the ops surface that shows what it is doing: a panel, a table,
  or a truth-report section the owner can read the same day. "Measured but nowhere to
  look" is an unfinished change.
- **Safety limits remain fully enforced** (always were): blast-radius caps,
  naked-position invariant, secret handling, withdraw-key rejection (Hard Limits below,
  B12/B18). Production raises the stakes on these, never lowers them.

This **reverses** the Sessions-29–38 "ship live, no dark flags" testing-phase cadence
for money-path work. Already-shipped live flags stay as the owner directs; *new*
money-path changes follow dark-first from here.

---

## Change-management Protocol

**Every change ships via PR.** Doc-only edits, code, tooling — all of them. Never push directly to `main`.

1. Cut a fresh topic branch off `main` HEAD. Naming: `docs/`, `feat/`, `fix/`, `chore/`.
2. Land commits on the topic branch. Each commit message: the *why*, not the file list.
3. Open PR targeting `main` with a design summary in the body.
4. Call `subscribe_pr_activity` immediately on opening every PR.
5. **Auto-merge** once all of: CI green, no conflicts, not an owner-sign-off item, no unresolved reviewer objections.
6. **Pause and ask owner** (`AskUserQuestion`) when: CI red with non-obvious fix; merge conflict needs judgement; change touches an owner-sign-off item; substantive reviewer objection.

**Owner-sign-off items** (never auto-merge these):
- Signing service / KMS / connect-time validation / blast-radius caps
- Position FSM transitions (entry, SL/TP shape, pre-TP trigger, BE shift, trail)
- New evaluator paths or scoring models
- Business Rules changes
- Paid-channel routing changes
- Regime-per-exit design decisions (§3.2b — data research in progress)

Never push to `claude/general-session-*` or harness-assigned long-lived branches. The auto-deploy on `main` ships in ~45s. **Production phase: the app is LIVE on the Play Store** — a `main` deploy reaches real users, so money-path changes ship **dark + shadow-measured + owner sign-off to activate** per § Project Phase — measurement flag ON and visible in ops, user-visible flag OFF. Off-money-path work ships normally.

---

## Re-check Before You Test, Not After

**A test proves the code does what you wrote. Nothing in the suite proves what
you wrote was the right thing to do.** Every defect this file records was caught
by someone reading the *claim* — usually the owner — not by CI.

So before running the suite, and certainly before putting a recommendation into a
PR body, a docstring, or this file, do a separate pass on the **conclusion**:

1. **Re-read the diff as a reviewer who did not write it.** Not "does this work" —
   "what is this asserting, and who checked that part?"
2. **State the claim in one sentence, then try to falsify it with data you already
   have.** If the falsifying query takes five minutes and the data is already on
   disk, it is not optional and it does not wait for a later session.
3. **Check the *direction* of every recommendation, not only its premise.** A true
   observation and a correct fix are different findings, and the gap between them
   is where a whole day goes.
4. **Say which parts you verified and which you inferred.** An unlabelled
   inference reads exactly like a measurement.

Paid for on 2026-08-01, twice in one session:

- `TREND_PULLBACK_EMA`'s TP1 has a cap and no floor, and its median designed R:R
  measured 0.79. Every word of that is true, and "so floor TP1" went into a
  merged PR body, a module docstring, this file and an ops page as *"the single
  biggest lever"*. It is **wrong**: the winners barely clear their current
  targets (median hit 0.59R against a 0.89R peak, only 27% of trades ever reach
  1R, median excursion 0.53R), so raising the target takes the book from −0.081R
  to as low as −0.836R — on the 11:00 window, and it reproduces on the 08:26 one.
  One query against a CSV already open in the session would have caught it before
  the claim was ever written down.
- Generalising the entry-feature lane, the first cut copied MVRTP's feature list
  onto every path — a list chosen for MVRTP's particular blindness. The tests
  passed; the owner caught it. Reading each path's mechanism first was the check,
  and it cost nothing.

Corollary: **a finding and a fix are separate deliverables.** Report the finding
when you have it; the fix needs its own evidence, and "the mechanism is clearly
wrong" is not evidence about what happens when you change it.

---

## Hard Limits

- Never fabricate signal performance numbers
- Never deploy without syntax check + review
- Never silence a detected problem
- Never route signals to unconfigured channels
- Never push to `main` directly
- Never patch engine code at a vendor-API symptom before reading the vendor's changelog
- **Never log a Binance API secret at any level. Never write it to disk. Never surface it in errors.**
- **Never accept a Binance key with withdraw permission enabled. Auto-reject, no override.**
- **Never disable or weaken blast-radius caps.**
- **Never let a position sit OPEN without a stop.**
- **Never add an uncached Firestore / network read (or write) to a per-tick, per-scan, or per-order hot loop.** Cache it and gate the cache on an invalidation signal.
- **Never boolean-test candle/series arrays** (`arr or []`, `if not arr`) — the data store holds numpy arrays and truthiness raises; use `is None` / `len()` checks. Enforced by `tests/test_no_numpy_truthiness_regression.py` (2026-07-14: 8 features died silently to this).
- **Never swallow an exception silently in a data/measurement path.** Every fail-open `except` calls `fail_open.record(site, exc)` — behavior stays fail-open, but the failure counts, WARNs, and pages via the feature-liveness watchdog.
- **Never admit a symbol to the scan universe on a name list alone.** Every admission path calls `symbol_filters.crypto_perp_admission`, which is **fail-closed** on Binance's own `contractType`. A hand-maintained ticker list cannot see next week's listing, and the owner must never be the process by which we notice one.

---

## Cost Discipline

Cloud cost is part of "production-grade." Every change is reviewed for cost the same way it's reviewed for correctness.

**The billing surprise that wrote this section (Session 24, 2026-06-16):** a single uncached Firestore collection-group query in the pre-TP dispatcher ran on *every* mark-price tick (~1/sec × open symbols, 24/7). It drove **₹4,552 / month** — 99.9% of the GCP bill — in Firestore *reads*. Phone Auth, the only Google service the app actually intends to use, cost ₹0. Fixed in #609 with a generation-gated cache.

**Rules:**
- **Before adding/changing anything, ask: does this add reads, writes, or egress on a hot path?** Hot paths here: scanner (15s × 75 pairs), mark-price ticks (~1/sec/symbol), per-order, per-signal-dispatch. If yes → cache it, and gate the cache on an explicit invalidation signal (e.g. `position_state.get_write_generation()`), with a defensive TTL bound. Never rely on a TTL alone in a real-money path.
- **Firestore bills under the "App Engine" line in GCP.** Datastore-mode reads/writes/storage roll up under the "App Engine" service grouping — so an "App Engine" charge with **zero App Engine services deployed** is almost always Firestore. Don't chase a phantom App Engine deployment; check **Billing → group by SKU** and **Firestore → Usage** first.
- **Reads dominate.** The keystore (`firestore_keystore`) and kill-switch reads are already cached (30s / 5s). Any *new* per-loop reader must follow the same pattern — see `pretp_dispatcher._default_positions_for_symbol` as the reference implementation.
- **Auth is not the cost.** Phone Auth / SMS verification is free at tester volume and sits under "Authentication", not "App Engine". If the bill spikes, look at the server-side execution Firestore layer, not auth.
- **Diagnose on real billing data first** (mirrors Real-Data-First Diagnosis): Billing SKU report + Firestore Usage dashboard *before* theorising about a cause or touching code.

---

## Architecture

*Quick-reference sketch. **Full map: `ARCHITECTURE.md`** — repo boundaries, the
three planes (money / measurement / display), FSM state diagram, state-and-storage
map, deployment topology, and a "where do I look when…" index.*

```
Binance WS/REST
      ↓
HistoricalDataStore + OrderFlowStore
      ↓
Scanner (15s × 75 pairs) → 19 evaluators (17 live) → gate chain → scoring
      ↓
SignalRouter → in-app Lumin feed (primary, B1) · FCM push topics · Telegram mirror
      ↓
┌─────────────────────────────────────────────────────┐
│ ENGINE CONTAINER                                    │
│ TradeMonitor · signal_dispatch · Position FSM       │
│ PositionWorker · Reconciler · MarkPriceFeed         │
│ ManualTakeConsumer (server-side take, via Redis)    │
│ SnapshotWriter ──→ Redis ──→ API CONTAINER          │
│                              RedisEngineFacade      │
│                              HTTP on own event loop │
└─────────────────────────────────────────────────────┘
      ↓
Signing Service (separate container, Unix socket)
      ↓
Binance REST API
```

**Two modes** (`API_PROCESS_ISOLATED` in `.env`):
- `false` — engine serves HTTP directly (single-process)
- `true` (live on VPS) — separate `api` container, Redis bridge

**Per-user settings:** API writes SQLite (shared volume) → engine reads at dispatch (fresh SELECT, WAL mode). Change takes effect on next signal dispatch.

**Delivery surfaces (owner, 2026-07-25):** the **Lumin app is the primary surface for
users** — that is where signals are managed and read. Telegram *works in India* (the
old "banned in-region" claim in these docs was false) but remains a **mirror**, not the
primary channel. **Telegram's wider role is a dedicated future session** — don't expand
or re-architect Telegram routing as a side-effect of other work.

**Control vs alerting:** control (kill switch, auto-mode flips, manual close) is
**ops-only** — it needs the audit trail. Alerting is read-only, so FCM push *and*
Telegram are both acceptable paging paths.

---

## Module Map

| Concern | File |
|---|---|
| Boot, WS/REST init | `src/bootstrap.py`, `src/main.py` |
| Scanner + gate chain | `src/scanner/__init__.py` |
| 19 evaluators (17 live; ORB + CLS disabled) | `src/channels/scalp.py` |
| Confidence scoring | `src/signal_quality.py`, `src/confidence.py` |
| Regime classification | `src/regime.py` |
| MTF policy | `src/mtf.py` |
| Level Book | `src/level_book.py` |
| Structure state | `src/structure_state.py` |
| Volume Profile | `src/volume_profile.py` |
| Pattern catalog | `src/chart_patterns.py` |
| Pair universe | `src/pair_manager.py` |
| Trade monitor (backstop) | `src/trade_monitor.py` |
| Telegram routing | `src/signal_router.py`, `src/telegram_bot.py` |
| Config tunables | `config/__init__.py` |
| Per-user dispatch | `src/execution/signal_dispatch.py` |
| Position FSM | `src/execution/position_fsm.py` |
| Position worker | `src/execution/position_worker.py` |
| Signing service | `src/security/signing_service/` |
| Firestore keystore | `src/security/firestore_keystore.py` |
| Kill switch | `src/execution/kill_switch.py` |
| Blast-radius tripwires | `src/execution/tripwires.py` |
| Reconciler | `src/execution/reconciler.py` |
| Mark price feed | `src/execution/mark_price_feed.py` |
| Pre-TP dispatcher | `src/execution/pretp_dispatcher.py` |
| Manual take consumer (server-side take) | `src/execution/manual_take.py` |
| API server | `src/api/server.py` |
| API isolated entry point | `src/api/main.py` |
| Redis engine facade | `src/api/redis_engine.py` |
| Snapshot writer | `src/api/snapshot_writer.py` |
| Snapshot cache | `src/api/snapshot_cache.py` |
| Per-user settings | `src/api/user_overrides.py` |
| Binance connect (key intake) | `src/api/binance_connect_routes.py`, `src/security/binance_connect_validator.py` |
| Play Billing verify (B16, entitlement truth) | `src/api/billing_play.py` |
| Referral rewards (grants · commission · composition) | `src/api/referral_rewards.py` |
| FCM push (topics `alerts`/`signals`) | `src/push_notifications.py` |
| Closed-signal record (feeds ops `/track-record`, `/performance`) | `src/performance_tracker.py` |
| Signal-history persistence (app feed) | `src/signal_history_store.py` |
| Truth report | `src/runtime_truth_report.py` |
| Invalidation audit | `src/invalidation_audit.py` |
| Fail-open exception telemetry | `src/fail_open.py` |
| Feature-liveness watchdog | `src/feature_liveness.py` |
| Market-context engine (portfolio Layer A) | `src/market_context.py` |
| Strategy registry (Layer B) | `src/strategy_portfolio.py` |
| Strategy×Context edge matrix (Layer C) | `src/strategy_edge.py` |
| Suppression audit + shadow ledger | `src/suppression_audit.py` |
| Shadow-only strategy units | `src/shadow_strategies.py` |
| Stop-geometry A/B (shadow) | `src/geometry_ab.py` |
| Tuned shadow variants (`@TUNED`) | `src/tuned_variants.py` |
| Dispatch-staleness V2 (geometry-aware, `@DSV2` shadow) | `src/staleness_v2.py` |
| SAR exit shadow arm (`@SARBASE`/`@SAREXIT`, dark, **replay**) | `src/sar_exit_shadow.py` |
| SAR exit mechanism (**live**, forward-stepped in the monitor loop, dark) | `src/sar_live_shadow.py` |
| Per-path entry-feature stamps (observe-only, joined to the closed-signal record) | `src/entry_features.py` |
| Entry-quality gate — the consuming half of that lane (**LIVE**, per-rule ops switches) | `src/entry_quality.py` |

---

## The Autonomous Portfolio (Layers A–G) — LIVE

Edge lives in `session × regime × strategy` cells, not in a global confidence score.
The portfolio measures every strategy in every context on real data and lets that
measurement decide emission. Full description: `OWNER_BRIEF.md § 3.11`.

| Layer | Module | State |
|---|---|---|
| A — market context vector | `src/market_context.py` | LIVE |
| B — strategy registry / affinity | `src/strategy_portfolio.py` | LIVE |
| C — Strategy×Context edge matrix | `src/strategy_edge.py` | LIVE — everything routes on it |
| C→consumer — per-context emission floor | `src/context_emission_policy.py` | **LIVE** (money path) |
| D — allocator | `src/strategy_allocator.py` | **Recommendation-only; consumed by nothing** |
| G — closed-loop emission controller | `src/emission_controller.py` | **LIVE**, self-promoting inside a bounded envelope |

**Four rules when touching any of it:**

- **Measurement arms are not strategies.** `@FIXED`/`@ATR`/`@TUNED`/`@DSV2`/`@GOV`/
  `@SARBASE`/`@SAREXIT` are stamped from the same candidates as the real rows —
  include them in a per-strategy rollup and you double-count the candidate. The
  authoritative suffix list is `geometry_ab._VARIANT_SUFFIXES`; ops mirrors it in
  `strategy_lab.MEASUREMENT_SUFFIXES`. **Keep the two in sync** — they drifted once
  and silently inflated the ops rollup for a week.

  **There is a third consumer, and it is the one that bit us: Layer G.** The rule is
  not only about *rollups*. Any code that keys off the edge matrix inherits the arms,
  and if its *output* is keyed by live strategy the two ends silently disagree. The
  emission controller took its `best_strong_cell` straight from the matrix while
  `resolve_min_samples` reads a live `SetupClass`, so 9 of 18 persisted overrides and
  23 of 40 promotions went to keys nothing reads — and because an arm never emits, it
  can never trip the auto-tighten brake, making it *more* promotable than the real
  strategy it was starving (2026-07-27, #806/#807). Before writing matrix-derived
  state anywhere, ask **"who reads this key, and are they keyed the same way?"**
  Layer G now takes a `routable` set as a parameter and reports what falls outside it;
  the ops Layer-G panel renders that stamp rather than mirroring the suffix list,
  because **the fix for a drifting mirror is not a second mirror.**
- **Counterfactuals are optimistic** (~0.38R measured on MTP). Never quote a
  counterfactual R as an expected live result.
- **"Emitted" means DELIVERED, and only the router knows that.** Provenance has
  three states, not two: `suppressed` (a scanner gate killed it), `enqueued` (it
  passed every scanner gate and `signal_queue.put` accepted it), `emitted` (the
  router confirmed delivery). Enqueue is **not** dispatch — `SignalRouter._process`
  applies its own layer (correlation lock, per-symbol/per-channel cooldown,
  per-channel concurrency cap, correlation group limit, global same-direction
  throttle, TP/SL sanity, staleness) and drops most of what it dequeues. Stamping
  `emitted` at the enqueue site inflated the only population allowed to justify a
  live change by ~30x, non-randomly (81% SHORT vs a 52% SHORT real feed), and the
  ops page read "Emitted to live (98)" for a window with 3 real signals
  (owner-caught 2026-07-25). `PROVENANCE_EMITTED` is written **only** by
  `sar_exit_shadow.promote_to_emitted`, from the router, after confirmed delivery.

  Two corollaries, both paid for on 2026-07-26 when the first fix didn't hold:

  - **Provenance is schema-gated, never date-gated.** The original migration
    trusted anything stamped after a hardcoded cutoff set to when the fix was
    *written*; the PR shipped 8h later, so 88 rows of old-code stamps were
    trusted and the panel read 88 against a true 1 — worse than the bug it
    replaced. `_migrate_provenance` now keys on `prov_schema` /
    `PROVENANCE_SCHEMA`, written by the code itself. **A data migration must
    never be gated on a timestamp predicting a future deploy** — bump the
    schema instead.
  - **`provenance` is not `strategy_edge.source`.** Two different fields that
    share the word "emitted". Layer C never reads the ledger's `provenance`;
    every edge-store writer sets `source` independently (`SUPPRESSED`/`SHADOW`),
    and the allocator's `emitted_backed` reads the matrix cell's `n_emitted`.
    Provenance is **display/analysis-only** — which is exactly why a 30x error
    in it survived: it corrupts what the owner reads to decide, not what routes.
    Don't re-derive either field from the other.
- **Zero emissions ≠ broken.** Fully gated + measured-negative is the gates working;
  fully gated + measured-positive is money on the table. `gated_path_verdict` tells
  them apart — don't "fix" the first case.
- **After any scoring or cost change, wait for a fresh window** before judging a
  verdict. Rolling per-cell windows keep serving pre-change data.

---

## Telemetry & Diagnosis

- **Suppression telemetry** — every gate rejection tagged. First stop when "no signals firing." Surface via `/suppressed` Telegram command.
- **Truth report** — on `monitor-logs` branch:
  ```bash
  git fetch origin monitor-logs
  git show origin/monitor-logs:monitor/report/truth_report.md
  ```
  **Counters are cumulative over a long window** — right after a scoring/gate
  change merges, the report still reflects *pre-change* behaviour. Don't judge a
  just-shipped change (or re-diagnose the path) until a fresh data window has
  accumulated. Wait for data, then read.
- **Invalidation audit** — `data/invalidation_records.json` on VPS. Classifies kills as PROTECTIVE / PREMATURE / NEUTRAL.
- **Edge matrix / shadow ledger** — every strategy (live evaluators + shadow units + `@TUNED` variants + stop-geometry A/B arms) is forward-measured per market context on real data. Read via the ops Strategy Lab; strategy tuning/allocation decisions come from these numbers, never opinion, and applying a winning recipe is still dark-first + owner sign-off.
- **360 CE Ops** — `ops.luminapp.org` (live, owner-only). Engine API + data volume + monitor-logs + diag scripts in browser.
- **Auto-detected issues** — GitHub Issues tagged `auto-detected` from the 24/7 monitoring agent. Check at every session start.

---

## Real-Data-First Diagnosis

**At a vendor-API symptom: read the vendor's changelog before touching engine code.**

1. Read the wire — get real data from prod (logs, `/diag`, `/ws_log`)
2. Check vendor changelog — Binance: `developers.binance.com/docs/derivatives/change-log`
3. Check vendor announcements — `binance.com/en/support/announcement`
4. Verify externally (different IP, browser WS tester)
5. THEN consider code changes

This rule exists because six PRs were spent on WS instrumentation before a 5-minute changelog search found a Binance endpoint decommission as the actual root cause.

---

## Commands

```bash
# Tests
python -m pytest tests/ -x --ignore=tests/test_deployment.py -q
python -m pytest tests/test_signal_quality.py -v

# Lint / type-check
ruff check src/ config/
mypy src/ config/          # has an accepted error baseline (~102) — don't add new ones

# Syntax check before commit
python3 -c "import ast; ast.parse(open('src/<file>.py').read()); print('OK')"

# Docker — isolated mode (VPS production)
bash deploy.sh                                           # reads API_PROCESS_ISOLATED from .env
bash deploy.sh --clean                                   # full no-cache rebuild + cleanup

# Docker — manual isolated
docker compose -f docker-compose.yml --profile isolated up -d --build --remove-orphans

# Docker — single-process mode
docker compose -f docker-compose.yml -f docker-compose.singleprocess.yml up -d --build --remove-orphans

# Logs
docker logs 360scalp-v2-engine --tail 100
docker logs 360scalp-v2-api --tail 100
docker logs 360scalp-v2-signing --tail 50

# Redis health check
docker exec 360scalp-v2-redis redis-cli KEYS "snapshot:*"

# Run engine locally
python -m src.main
```

`pyproject.toml` sets `asyncio_mode = auto` — async tests need no decorators.

---

## Conventions

- **Logging:** `loguru` via `src.utils.get_logger(name)` — never `print` or stdlib `logging`
- **Config:** all values env-overridable via `config/__init__.py` helpers (`_safe_int`, `_safe_float`, `_safe_bool`, `_safe_choice`)
- **All async** — no blocking calls in scanner / router / monitor loops
- **Redis is optional** — RedisClient + SignalQueue fall back to in-memory
- **Each evaluator owns its SL/TP geometry** (B7) — no shared universal formulas
- **The `SetupClass` enum values** are stringly-coupled to `_MAX_SL_PCT_BY_SETUP` keys and telemetry event names — rename in all three places simultaneously
- **Candle fixtures in tests use the production shape** — the `numpy_seeded_store` conftest fixture (real `HistoricalDataStore` via `update_candle`), never hand-built list dicts, for any code that consumes the data store
- **New measurement pipelines register a liveness probe** (`src/feature_liveness.py`, wired in `main._build_feature_liveness`) — a feature whose output can silently flat-line without paging is unfinished
- **`xfail` is strict** — a passing xfail fails CI; remove the marker the moment its premise dies (5 tests rotted invisibly under non-strict markers, 2026-07-14)
- **A clamp is not a guard.** `min()` on a length or `max(0, …)` on an index
  turns "these inputs cannot support this computation" into a wrong answer with
  no signal. Where an input may not support the work, **refuse** — return None,
  mark INSUFFICIENT, and let the caller record that it doesn't know. The SAR
  shadow arm inferred its entry-bar index from elapsed time and clamped when the
  candle array didn't match; it then replayed an unrelated bar and published 172
  confident rows averaging −4.4R that described nothing (owner-caught
  2026-07-26, #800). Corollary: **any array consumed by *when* something happened
  must carry its own timestamps** — deriving the index from wall-clock
  arithmetic assumes gap-free, current data and fails silently when that breaks.
- **Record a fact where it becomes true, not where it is convenient.** A value
  derivable at stamp time but computed in a later pass does not merely arrive
  late — it silently shrinks every population that reads it, and the shortfall
  reads as *missing* data rather than *late* data. SAR agreement
  (`entry_sar < entry`) consumes no future candle, yet lived in the 48h resolve
  path, so 261 of 277 rows carried no verdict and the agreement mix on screen
  always described a two-day-old population (owner-caught 2026-07-27, #802).
  Corollary: **"blank" needs a cause before it gets a caption** — not-yet-resolved
  and could-not-be-resolved are different states, and the panel pooled them into
  one sentence that reported a data fault which was not happening.
- **Closed bar ≠ current bar.** `update_candle` appends only on `k["x"]`, so the
  newest bar the scanner holds is the last *completed* one — while a replay that
  locates "the bar containing the stamp" lands on the bar *after* it. They are
  adjacent, and across an indicator flip they sit on opposite sides of price. Any
  stamp-time-vs-replay-time comparison must reconcile that explicitly or it
  compares different bars and calls the difference a fault. Related:
  **redefining a live measurement is only cheap while its population is empty** —
  #802's redefinition was free solely because the ledger had just been cleared.
- **A second computation of the same quantity is a detector, not a duplicate** —
  provided it never overwrites the first. Keeping the resolve-path SAR alignment
  beside the stamp-time one, under its own key with a disagreement counter on the
  liveness watchdog, turns a known-dangerous replay path into one that reports on
  itself. **Do not signal "idle" or "disabled" by raising** inside a
  `PredicateProbe`: it converts to a `fail_open.record`, and filling that counter
  with non-failures is how a real one stops standing out — `return True, "…"`.
- **A field one repo reads and no repo writes fails silently and looks full.**
  `app/routes/performance.py` read `entry_regime` off closed-signal records from the
  day it was written; `SignalRecord` never carried it, so the per-regime table
  bucketed **every** signal into UNKNOWN for months — not a crash, not an empty
  table, a full-looking table describing nothing (owner-caught 2026-07-28, #817).
  A cross-repo field name is a **contract**: pin it in a test on the producing
  side, so renaming it fails loudly instead of quietly emptying a page. Corollary:
  **some facts have exactly one moment at which they are knowable.** The regime at
  entry is one; there is no honest backfill, so pre-fix rows stay UNPLACED rather
  than being handed a guess.
- **A throttle on rate is not a throttle on evidence.** The SAR stamp cooldown
  bounded how *often* a candidate could stamp and said nothing about how many rows
  one move could contribute — so a mover setup persisting for hours produced one row
  per cooldown period, and SLXUSDT SHORT bought **10 rows in 2h10m inside a 0.37%
  entry spread**, 36% of a whole resolved population. Counted per row that
  population read 32% win / −0.364R; per move, 55% / +0.003R. **The sign of the
  verdict was an artifact of re-detection** (2026-07-28, #816). Ask what the *unit
  of evidence* is, then throttle on that. Related: **a key that splits a budget
  multiplies it** — the cooldown key carried provenance, so a candidate oscillating
  across a gate boundary held two budgets; 21 of 21 sub-cooldown repeats were
  provenance flips, not cooldown misses.
- **A watchdog keyed on the live universe cannot see what left it.**
  `candle_coverage` walks `pair_mgr.pairs` and scored 100% while every ledger record
  on a rotated-out mover was permanently unresolvable, because a rotated-out symbol
  is by definition not in that map (2026-07-28, #815). Key a probe on **the
  population that would be harmed** — here, the records still owed a verdict — not
  on the population that happens to be convenient. And a fail-open `continue` with
  no counter is how the harm stays invisible: `if early: continue` was silent by
  construction for two full days per record.
- **A replay cannot validate a mechanism, only a hypothesis.** Every measurement
  arm before 2026-07-30 stamped a candidate and scored it later, which answers
  *"would this have been profitable"* and is silent on *"could we actually have
  done it"* — whether the level is computable in time, placeable, and actionable
  before the outcome is known. Worse, a deferred verdict inherits its resolver's
  health: the SAR replay ledger had **8 of 19 rows unresolved, including all four
  of the window's winners**, so its −0.682R read was a fact about a starved
  refresh budget, not about SAR (owner-caught 2026-07-30, #832). Before quoting a
  counterfactual, ask **what fraction of the population resolved, and is the
  unresolved part random?** A loss-selected sample is worse than no sample,
  because it looks like an answer. When the question is whether to *adopt* a
  mechanism, measure it forward on the money-path clock — `sar_live_shadow.py` is
  the pattern.
- **A resting stop is part of the mechanism, not an implementation detail.**
  "Exit at market when the indicator flips" specifies no stop between bars, which
  breaches the naked-position invariant the moment it is live — so measuring it
  literally measures something unshippable. Model the stop that would actually be
  parked, and record **both** fills: the level touched intrabar, and the confirmed
  flip exited at the close. Their difference is the cost of confirmation, it is
  never zero, and no replay had ever produced it. **Where two fills are defensible,
  publish both** — collapsing them into one number before the gap is known is
  choosing the answer, and the one you would have chosen is the flattering one.
- **A gate whose evidence only arrives from what it lets through is an
  absorbing state.** `cohort_edge` suppresses on measured expectancy, and the
  only writer of that measurement is `trade_monitor` resolving a *delivered*
  signal — so suppressed → never emits → never resolves → never records → the
  count-bounded deque never rotates → the verdict is permanent. Cohorts locked
  when STEP 2 went ACTIVE on **2026-07-07** were still being judged on that
  day's outcomes 23 days later, and the delivered feed fell ~48/day → ~9/day
  the next day. Same shape as Layer G's "an arm that never emits can never
  trip the auto-tighten brake" (#806), inverted: a cohort that never emits can
  never earn its way back. **Bound the evidence by AGE, not just by count**
  (`COHORT_EDGE_MAX_AGE_DAYS`, 14d from the live cohort census) so the gate
  releases on its own and re-earns the verdict on real fills. Do **not** close
  the loop by feeding the store with suppressed counterfactuals — they are
  optimistic (~0.38R) and this store decides live emission; release by time,
  judge on fills.
- **Every live gate stamps `_stamp_suppressed`, no exceptions.** `_reject()`
  does not stamp — each gate calls it explicitly, and `cohort_edge` /
  `pair_analysis:critical` never did. They were therefore the only live gates
  absent from the Suppression Quality Audit: no WOULD_WIN%, no EV/suppression,
  no KEEP/TUNE/DROP. **A gate that cannot be measured cannot earn its place**,
  and one of them had been suppressing unmeasured for 23 days while the audit
  table beside it confidently ranked every other gate. When output drops, list
  the gates and check which ones have no row.
- **Ask what a composite key's least-varying component is doing.** All 29 live
  cohorts on 2026-07-30 ended in `macro_dir=DECLINE` — the component added no
  discrimination while BTC stayed put, and a macro flip resets *every* cohort
  to n=0 simultaneously, disarming the whole gate in one step. A key component
  that is constant today is a coordinated cliff tomorrow; probe for it
  (`cohort_edge_gate`) rather than discovering it on a P&L chart.
- **A deny-list is a floor; only a structural gate is a filter.** A list of
  names excludes exactly the tickers a human already typed, so it is silent by
  construction on the next listing — and "add it when we see it" makes the
  owner the detection mechanism. Binance publishes `contractType ==
  TRADIFI_PERPETUAL`; every `pair_manager` fetch path read it, and
  `scanner._ensure_mover_pair` — the **one** path that reaches outside the
  top-N into the whole ~600-pair `!ticker@arr` board, which is precisely where
  stock perps live — never did. SMCI / SOXS / IBM / NOK / LRCX reached the
  **live paid book**: 7 delivered signals, mean −1.50%, zero TP hits
  (owner-directed audit 2026-07-30, after #B18 had already cost a paid user's
  auto-trade a `-4411` on WDCUSDT and the "structural filter" written to
  prevent the recurrence was never wired to the leaking path). Corollary:
  **when a fix is described as structural, name the paths it covers and check
  each one** — the doc said the filter "stops the next new stock perp without
  a human editing this list", and that sentence was false for the only path
  that mattered.
- **Absence of knowledge is not permission — decide the direction of every
  fail per path.** `is_tradfi_perp` answers False on an empty metadata cache,
  which is right where a name-list floor sits beneath it and wrong where the
  input is the whole exchange. The same predicate needs a **fail-closed**
  sibling (`crypto_perp_admission`: `metadata_unavailable` /
  `unknown_to_exchange_info` / `tradfi_perp`, each separately counted) on the
  open path. And a fail-closed gate needs a probe on *why* it is closing —
  otherwise a dead exchangeInfo cache silently refuses every candidate and
  reads exactly like a quiet market (`mover_admission_metadata`).
- **A borrowed entry needs a hold, or the owner of the map will delete it.**
  The scanner parks promoted movers directly in `pair_mgr.pairs` for a 6h TTL;
  `pair_manager`'s prune walked that same map and deleted everything outside
  the fresh top-N, on a refresh whose period is *also* 6h. Mean ~50% of every
  promotion window lost, and invisible three ways at once: the scanner never
  re-admitted (its own `symbol in _mover_promoted_pairs` skip), the symbol kept
  consuming promotion budget until TTL, and the scan-set builder dropped it on
  a `pair_mgr.pairs.get(...) is not None` guard **with no else-branch**
  (2026-07-30). Shared mutable state across a module boundary needs an explicit
  claim (`hold_symbol` / `release_symbol`) — and the claim's holder owns
  release, or the map grows without bound and the prune stops meaning anything.
- **Ask what fraction of the delivered book a path owns before you rank it.**
  Every capacity discussion in this repo had been about the core 75, while
  `signals_last100` showed the delivered book running at a **$25.7M median 24h
  volume, 53 distinct symbols, 73 of 100 in `MOVER_*` setups** — i.e. dominated
  by pairs admitted for six hours at a time through a path with no structural
  filter, no WS klines (REST re-seed only, up to ~2 min stale), a spread gate
  50× looser than the median delivered spread, and half its window silently
  pruned away. **Universe *size* was never the question**; the admission path
  was. Read the emitted population first — the code's shape tells you what was
  intended, not what ships.
- **A measurement that rides another subsystem's loop inherits that subsystem's
  lifetime — and "nothing to do" is the same no-op as "nothing works".** The SAR
  live arm was stepped from `observe_signal`, once per **active** signal, so the
  moment the router popped a closed signal the arm sat RUNNING forever — while its
  whole premise is that it exits on its *own* SAR flip, normally later than the
  signal's SL. Independently, `step_arm` iterates "bars newer than the last one I
  consumed": empty between bar closes (healthy) and empty forever for a
  rotated-out mover whose klines stopped (the Session 44/45/46 frozen-candle
  class). Both produced KORUUSDT SHORT open 2h19m at `bars_seen: 0`, still
  carrying entry-time SAR direction and a parked stop the price had crossed by
  5.45%, while the probe read *"2 arms stepped, no candle misses"* and ops read
  *"LIVE — 3 arms running"* (owner-caught 2026-07-30, #835). Key the sweep on **the
  population owed a verdict** (#815's rule, which that probe's docstring already
  claimed), and **check the clock**: presence of data is not currency of data, so
  every arm stamps `bars_behind` / `last_advance_at` and a stalled arm is a *miss*,
  named apart from a missing series because the fixes differ. Corollary: **a
  surface cannot grade its own liveness on a clock it supplies** — ops fetched the
  live price itself and printed it beside a two-hour-old stop under the words
  "right now", breaking from the other side the rule its own docstring carried.
- **A forward measurement is only forward from the bar it anchors to.** `new_arm`
  anchored to "the newest closed bar the store holds right now" and never asked
  whether that bar *was* right now. For a promoted mover (REST re-seed only, no WS
  klines) it was 40h old, so ACHUSDT 15m read its SAR-at-entry off a 40h-old bar,
  disagreed with its own 5m sibling on the same signal, then walked 158 bars of
  history in one advance — stamping `last_advance_at = now` on every one — and
  published as a live fill on the page whose first sentence is "this is not a
  replay" (2026-07-31, #836). #835 checked currency of data when *advancing* an arm
  and not when *opening* one: **a freshness rule applied at one end of an object's
  life is not applied to the object.** The answer is to refuse, not to re-anchor to
  now — now is not the entry bar either — and a refusal is counted and named
  (`refused_open` / `stale_anchor`) apart from a stalled arm, because no arm exists
  and nothing is owed a verdict. Corollary: **one bar count is an assertion, two are
  a detector** — `first_step_bars` is 1 on a genuinely live arm and larger only if
  it walked history, so the row reports on its own guard.
- **Two arms named for the same mechanism can measure different mechanisms.** The
  dark-signals `sar_*` replay runs SAR from bar one; the live arm hands over only
  once SAR comes onside and lets the original SL/TP1 govern until then. On the
  candidates where SAR agreed at entry the two agree within 0.10pp — which is
  exactly why nobody noticed that on the 21% where SAR **opposed** the replay reads
  +0.73pp optimistic, printing +1.04% where the live arm took the −3.00% stop
  (2026-07-31). Agreement on the easy majority is not validation; **check the
  surfaces against each other on the population where their definitions differ.**
- **Name the denominator when the mechanism replaces it.** R divides by the SL
  distance the trade was sized for — but SAR cancels that stop, and its own stop was
  **wider on 14 of 27 handovers** (mean 1.25×, max 2.81×). Divided by the risk
  actually parked, +0.348R is +0.292R and the worst arm's −1.90R is −0.71R. Both are
  defensible; publishing one silently is choosing the answer. Same rule as the two
  fills: **where two denominators are defensible, publish both.**
- **A row owed a verdict needs a terminal state for "no verdict is possible",
  and a heartbeat that only fires on change is not a heartbeat.** The dark
  lane's horizon test sat *behind* a successful walk, so a row whose candles
  stopped never reached it: OPEN forever, frozen MFE, rendering as a live trade
  on the page an adoption decision reads. `INSUFFICIENT` is terminal and
  deliberately unscored — an expiry is a walked window in which nothing
  happened, this is the absence of a measurement, and folding them together
  divides a rate by rows nobody scored. Beside it, `flush()` persisted only when
  something changed, so an idle lane stopped writing and ops rendered STALE —
  the fault-that-is-not-happening the ledger's own flush docstring claimed to
  have fixed, because nothing ever called it with `force` (2026-07-31). **A
  docstring describing a heartbeat is not a heartbeat**; find the caller.
- **A field one writer populates and one *serializer* drops is invisible at both
  ends.** #817 was a field one repo read and no repo wrote. This is the same
  shape one layer down and it is harder to see, because nothing is missing while
  the process lives: `open_time` was added to the candle store, but
  `_save_snapshot_sync` wrote five arrays and `load_snapshot` read back the same
  five, so **bar timestamps did not survive a restart**. `_merge_candles` then
  *correctly* refused to merge the gap-fetch's timestamps onto a bucket with
  none — a misaligned timestamp is worse than an absent one — and the entire
  store came back undatable. Every open dark row read `no candles`, on core
  pairs whose candles were plainly arriving (owner-caught 2026-07-31, #842).
  Every link was individually right. **A round trip is a contract: pin it with a
  test that drives the real serializer**, and when you add a field to a
  structure that is persisted, follow it all the way to disk and back.
  Corollary: **the blast radius of a serializer is every consumer, not the one
  that noticed** — `_ohlc_15m_detail` refuses on the same condition, so the SAR
  resolver had been losing windows after every restart, and #832's "starved
  refresh budget" reading of 8-unresolved-of-19 is owed a re-check on a fresh
  window.
- **Refuse the claim, not the measurement.** "A clamp is not a guard" says
  refuse when the input cannot support the work — it does not license refusing
  the *work* when only the *label* is unsupportable. `slice_window` could not
  date its bars, so it returned nothing at all, and a lane that had been
  resolving stopped: an empty page, which is indistinguishable from a quiet
  market and strictly worse than the imprecision it was avoiding. Where the
  measurement is possible but its provenance is not, **do the walk and mark the
  row** (`window_undated_reason` → ops `unverified`), reserving the hard refusal
  for inputs that would make the *answer* wrong — history rolled off before the
  stamp, where a walk over what remains could book a TP1 that a missing SL
  preceded. And when a degraded mode ships, **count it**: the probe fails when
  the whole open book is advancing on undatable windows, which is neither
  stalled nor healthy and was invisible to a probe watching only for stalls.
- **A guard on "the first time" is not a guard on the object — #836's own rule,
  broken by #836's own fix.** That entry says *"a freshness rule applied at one
  end of an object's life is not applied to the object"*, and the fix it shipped
  asked its question exactly twice: at the anchor, and at the arm's **first**
  advance (`first_step_bars`). Owner data 2026-07-31 (#846): three arms stamped
  `anchor=clean`, `anchor_bars_behind≈0`, `first_step_bars=1` had consumed 466,
  159 and 63 bars against lifetimes of ~17, ~5 and ~9 — one contributing −1.644R
  to the population an adoption decision reads. The over-walk happened on a
  *later* advance, where nothing was looking.

  The mechanism is worth knowing because it recurs: a **frozen-then-refreshed
  series**. A rotated-out mover's klines stop and its bucket freezes;
  `refresh_timeframe` then **replaces** that bucket (correctly — merging would
  duplicate bars) with a fresh REST pull whose window still contains the
  consumer's last bar. The index lookup succeeds, the walk is structurally
  valid, and it crosses hours of history in one pass. **Any consumer holding a
  position in an array that another module may replace must bound its step by
  the clock, not only by the index.** And when it refuses, refuse the whole
  advance: walking "just the recent tail" is a clamp, and it books fills on bars
  chosen by us rather than by the market.
- **A test hook that means "don't persist" must not touch the disk, and a
  non-failure must never reach `fail_open`.** Both ledgers take `path=""` as
  "in memory" — what every test constructs with — and neither checked it before
  running its atomic write. So `flush` created `.tmp` in the process's cwd,
  which under pytest is the repo root, where `git add -A` committed it; it
  differed on every branch and conflicted on every merge from #839 to #845.
  The file was only the symptom. `os.replace(".tmp", "")` then raised into
  `fail_open`, so **every test run recorded a failure that was not one**, for
  two months, in the counter whose whole purpose is making a real failure stand
  out. Same rule the `PredicateProbe` guidance above already carries, broken one
  layer down: *do not signal a non-event by raising*. When a path is a no-op,
  return before the side effect — and if a repo artifact keeps conflicting, ask
  what wrote it rather than resolving it again.
- **A denominator computed from mutable state is a different number every time
  you read it.** `R = pnl_pct / sl_distance_pct` is only meaningful if the SL
  distance is the one the trade was *sized for* — but `trade_monitor` moves
  `sig.stop_loss` in place (BE shift, TP1 park, trail), and the closed-signal
  record stamped that final value. Ops divided by it, so a trade BE-shifted and
  then stopped out for −0.1% scored exactly **−1.00R**, indistinguishable from
  one that gave back its whole designed risk: 9 of 28 SL_HITs in the
  2026-07-29→08-01 window, moving the closed book from +0.160R to −0.088R.
  The sign of the headline was an artifact of the denominator (2026-08-01).
  This is #817's class with a numeric twist — the field the reader wanted
  existed on `Signal` (`original_sl_distance`) and was already used correctly by
  `snapshot._original_stop_loss` and the Layer-C writer; it just never travelled
  onto the artifact the owner reads. **Ask of every ratio: is the denominator
  still the thing it was when the numerator started?** Corollary: the tempting
  fallback is the bug. `abs(entry - stop_loss)` returns the wrong number for
  *precisely* the rows that have the defect, so the helper refuses (0.0 → no R)
  and the surface names why it refused.
- **Two winners are not a promotion.** `FAILED_AUCTION_RECLAIM` read +0.846R in
  the dark lane and the promotion request followed within the day. It was 3
  resolved rows (+1.54 / +2.00 / −1.00), bootstrap 95% CI **[−1.00, +2.00]**;
  both winners sat behind one gate, and removing them flipped that gate from
  +0.146R to −0.149R — so the gate's evidence *was* the two rows it was being
  used to justify. It also beat a random 3-row draw 4.2% of the time while being
  the best of 6 setups tested (~22% familywise). Three habits, all cheap: state
  the CI, not the mean; **check whether a subgroup's edge survives removing it
  from its own parent**; and count how many cells you looked at before calling
  one special. And the answer to a thin cell is *more evidence*, never a
  promotion — a dark lane whose row budget is consumed by the two highest-volume
  paths starves exactly the rare paths it exists to measure.
- **A measurement lane does not need a resolver, and the ones that grew their
  own each cost a session.** Every forward-measurement arm before
  `entry_features.py` carried its own resolution machinery, and the bill was
  `INSUFFICIENT` rows (#839), stalled arms (#835), stale anchors (#836),
  over-walked series (#846) and undatable windows (#842) — six sessions of
  defects in the *scoring* half, none in the *stamping* half. The entry-feature
  lane stamps a row keyed by `signal_id` and joins outcomes from
  `signal_performance.json`, which `trade_monitor` already writes correctly at
  the terminal transition. It inherits that correctness (including #848's
  denominator) instead of re-deriving it, and a row that never delivered simply
  never joins. **Before building a resolver, ask whether the outcome you need is
  already recorded by something that owns it.**
- **"Where it becomes true" is a point in the call graph, not a file.** The
  entry-feature stamp read `sig.entry_regime` inside the evaluator, and the
  scanner writes that attribute in `_populate_signal_context` — which runs
  *after* the evaluator returns. Every row would have carried `""`, collapsing
  the whole per-regime split into one nameless bucket: nothing crashed, nothing
  was empty on screen, the page would simply have described nothing. Caught the
  same day it shipped, by checking rather than assuming (2026-08-01). This is
  #817's class one caller earlier, and the warning was already written at the
  call site — `_populate_signal_context`'s own comment says the market-context
  stamp *"previously ran with these fields still empty, so the Wyckoff phase
  always classified AMBIGUOUS"*. **Before reading a field off a shared object,
  find the line that writes it and confirm it runs first.** The evaluator had
  the regime as a parameter the whole time. Corollary: when two layers can each
  answer, let the later one be authoritative and keep the earlier one as its own
  key — a disagreement is then information (the scanner reclassified between
  evaluation and dispatch) rather than a silent overwrite.
- **A literal route under a catch-all prefix must be registered first.**
  `signal_detail` owns `/signals/{signal_id}`, so `/signals/entry-features`
  404'd on the first cut while its own route object sat in `app.routes` looking
  registered — the route list said yes and the request said no, and the route
  list is not the authority. Same shape as trusting a probe over the population
  it claims to watch. Ops pins the ordering in a test rather than a comment.
- **A feature set is not portable just because the code that computes it is.**
  Generalising the entry-feature lane past MVRTP, the first cut copied MVRTP's
  feature list onto every path — and that list was chosen for MVRTP's particular
  blindness, a three-SMA pullback trigger that never looks at volume. TPE and
  MVAVW are blind in different places, so the copied columns measure nothing on
  them while the variables their entries actually turn on go unrecorded
  (owner-caught 2026-08-01, mid-implementation). Read the mechanism, then pick
  the features: `TREND_PULLBACK_EMA` applies nothing but **booleans** — EMA21
  tagged, close back above both EMAs, close > prev_close, close > prev_high, RSI
  in 40–60 and rising — recording *that* each threshold was crossed and never by
  how much, so its features are the magnitudes behind its own gates.
  `MOVER_AVWAP_SCALP` already gates on volume and slope; what it has no notion of
  is *where in the move it is*, because the anchor is computed and then used only
  to produce a VWAP. Corollary: **a small shared core plus per-path extras beats
  one wide table** — a path stamping twelve features invites twelve thresholds,
  and twelve cells against a book this size guarantees a spurious winner.
- **Sign a directional reading toward the trade, or half the book scores
  backwards.** `cvd_slope` and `book_imbalance` were stored raw and split with a
  single "higher is better" rule. A falling CVD is the dip being *sold* — bad for
  a long, exactly what a short wants — so every SHORT was judged inverted. The
  delivered book is ~50/50 by side, so this never showed up as an empty column or
  a crash; it just made both features look like noise, which is indistinguishable
  from a feature that genuinely does not discriminate. Ask of every signed
  feature whether positive means "good for price" or "good for *this trade*".
- **A gate whose comment and code disagree is worth CHECKING — it is not
  thereby a gate that does nothing.** `_evaluate_trend_pullback`'s SMC check
  reads *"require at least one FVG or orderblock in the pullback zone"* and is
  `bool(fvgs) or bool(orderblocks)` — a global existence test that, on paper, a
  zone 40 ATR away satisfies. Same class as the `is_tradfi_perp` audit, and the
  rule it produced still holds: **when a filter is described as structural,
  check that the code performs the check the sentence claims.** Stamped
  (`smc_zone_dist_atr`) rather than fixed, because narrowing a rejecting gate
  changes what emits.

  **The verdict attached to it was wrong, and this file carried it for a day.**
  Measured on the first 89 TPE signals once `zone_distance_atr` could actually
  compute (2026-08-02): median **0.13 ATR**, p90 0.42, **max 0.52**, 88 of 89
  inside half an ATR, no tail. No 40-ATR candidate exists. The cause is
  `detect_fvg`'s `lookback=10` — it only finds gaps in the last ~12 bars, and a
  gap that recent is still near price, so **the narrow lookback is what makes
  the loose gate behave like the strict one**. The gate rejects symbols with no
  recent gap and otherwise admits structure at the entry.
  `entry_quality.tpe_smc_zone`, built to repair it, was retired the same day it
  shipped: no threshold discriminates on that distribution, and a rule that
  cannot discriminate is noise on a panel, not a shadow rule awaiting evidence.

  Two things to take from it. **Reading code produces a hypothesis about
  behaviour, never a measurement of it** — the confident story about 40-ATR
  zones came entirely from the source and survived into a PR body, a module
  docstring and this file. And **a broken measurement is worse than none while
  it looks like agreement**: this feature returned `None` on every row for its
  whole life, so the claim went unchallenged not because anyone checked it but
  because nothing could.
- **A guard belongs where the assumption is made, even after the source is
  fixed.** `_merge_candles` concatenated blindly while `_estimate_gap_candles`
  over-fetches by design, so every gap fill re-appended bars the bucket already
  held — duplicate bars that double-weight any fixed-bar-count indicator, and a
  **non-monotonic `open_time`**. `slice_window` locates its entry bar with
  `np.searchsorted`, which is *undefined* on an unsorted array rather than merely
  imprecise, and the walk that follows is structurally valid, stamps
  `last_bar_ms` and reads `current`. Nothing downstream could tell. Owner data
  2026-08-01: 7 of 9 open dark rows carried ~21 more array entries than there had
  been minutes since their entry. Fixed at the merge *and* guarded at the
  consumer, because a store is not the only thing that can hand us a bad series.
  Corollary: **an intentional over-fetch is a contract to deduplicate** — the
  buffer is correct, what was missing is that overlap is therefore expected.
- **Fixing one writer is not fixing the field.** The merge dedupe shipped and
  `timestamps_unsorted` kept firing on every open dark row, because a WebSocket
  bar never passes through `_merge_candles` — `update_candle` appends blindly and
  was the *other* writer. The race is ordinary: `refresh_timeframe` REPLACES a
  bucket with a fresh REST pull while the socket is still delivering, so a kline
  that closed before the pull's last bar lands immediately after. **When a
  structure has an invariant, enumerate every path that writes it** — the same
  audit `is_tradfi_perp` needed. Corollary: a same-timestamp bar is an *update*
  and belongs in place; an older one is a straggler and is dropped and counted;
  a bar with no timestamp still appends, because absence of knowledge is not
  permission to discard history.
- **Path-dependent consumers refuse where scanners degrade.** "Refuse the claim,
  not the measurement" is right for the dark lane, whose levels are fixed and
  whose walk is a pure scan — imprecision lands in the *label*. Parabolic SAR
  carries an acceleration factor and an extreme point forward bar by bar, so one
  duplicated bar advances the AF an extra step, moves the stop toward price
  permanently, and every level after it is wrong with no recovery; and
  `times.index(last_seen)` finds the *first* occurrence, so an out-of-order bar
  makes the walk resume behind itself. There the imprecision lands in the
  *answer*, so `_series` refuses. **Ask which half a corrupt input damages before
  choosing degrade-or-refuse.** The check runs over the whole window, not the
  ends: one interior duplicate leaves first and last timestamps perfectly
  ordered.
- **Record both halves of an excursion, or neither answers anything.** Every
  measurement lane recorded MFE and none recorded MAE, so no question about stop
  distance was answerable at all — on 2026-08-01 the optimistic reading of
  "tighten the stop" (+0.203R) and the pessimistic one differed by more than the
  entire edge under discussion, and the gap is exactly *did the winners survive
  it*, which MAE counts and MFE cannot. A one-sided measurement looks complete
  and silently bounds nothing. Corollary: **the fix for "we can't tell" is
  usually a field, not an argument** — and it is cheapest at the moment the
  resolver is already walking the bars.
- **An expiry is only as good as the walk behind it.** A row past the horizon is
  scored 0R on the claim that its window was walked and nothing happened.
  ROBOUSDT expired on 309 bars of a 362-minute window and ARBUSDT on 329 of 365,
  so 89 minutes of unexamined bars were reported as the setup doing nothing — and
  a touch inside them would have been booked as a zero, the fabrication class
  arriving as a rate rather than as a number. Untouched rows now stamp
  `window_coverage` and retire `INSUFFICIENT` below a floor. The separation was
  clean (the other six expiries walked 99.9–102%), which is the tell that the two
  populations were always distinguishable and simply never distinguished.
- **"Not where I left it" has two causes, and only one of them is fatal.** The
  SAR arm located itself with `times.index(last_bar_ms)` and treated every miss
  as history having rolled off the window — so it retired. `seed_symbol`
  REPLACES a bucket wholesale and promoted movers are re-seeded on a throttle
  (they carry no WS kline subscription), so a REST pull that has not caught up
  with a bar the socket already delivered leaves the arm's bar **past the end of
  the array**. Nothing is lost; the bar returns on the next write. That killed
  **10 of the 15 unmeasurable arms on 2026-08-02, at a median of four bars**, on
  arms that had opened cleanly and were measuring fine — 9 of the 10 on mover
  paths, which is exactly the population that gets re-seeded. Declining to
  advance is **not** a clamp: it is what the arm already does on any cycle with
  no new bars. Ask which side of the window the miss is on before killing
  anything — past the end is a wait, before the start is a refusal, and inside
  the range but off the grid is a third fault with a third fix.
- **A normalised unit is only honest if the thing it normalises by is what you
  actually varied.** `R = pnl / sl_distance` equalises trades *only* when
  position size scales inversely to the stop. `signal_dispatch` sizes at a fixed
  notional (`raw_qty = notional / entry_price`), so the stop distance is absent
  from the sizing and R equalises nothing: a 0.80% loss and a 6.14% loss are both
  −1.00R while costing $4.00 and $30.70 of the same $500 (owner, 2026-08-02:
  *"that R is purely confusing"*). It misranks paths — MEAN_REVERT reads
  worst-in-book by R while losing a fifth of what MA_CROSS_TREND_SHIFT loses —
  and on the same day's SAR arms it **flipped the sign**, reading +0.035R against
  −0.041%, because the winners sat on tighter stops than the losers. Ops now
  leads every measurement page with PnL % and keeps R as a muted bridge to the
  edge matrix. **Ask of any normalised metric: did we hold the denominator
  constant, or did we hold the thing it divides into constant?** Corollary: a
  percentage needs no denominator, so it cannot silently shrink its own
  population the way R does.
- **"Make it live" is a question about which rules, not about whether to have a
  gate.** Owner, 2026-08-02: *"make entry features live, not only
  measurement"* — against a lane (#849/#851) whose own PR bodies say a filter
  cannot be chosen from its window: nineteen cells on 46 closed signals, one CI
  excluding zero *in the backwards direction*, ~62% familywise. Building the
  gate and picking its rules are separable, and only the second needs evidence.
  `src/entry_quality.py` ships the mechanism wired end-to-end — a real gate in
  the post-scoring chain, suppression-stamped, per-rule switchable from ops —
  and enforces exactly one rule: `profile_reject`, which is **a repair, not a
  discovery**. `_pass_basic_filters` computes pair-tier liquidity and spread
  thresholds and 19 of 20 call sites throw them away, including the path that is
  ~94% of the book; enforcing it invents no number. `tpe_smc_zone` knows its
  repair and not its threshold ("how many ATR is *in the pullback zone*"), so it
  ships shadow. **Ask of any rule about to go live: does its threshold come from
  code that already exists, or from this window?** Three corollaries, each one a
  rule from this file arriving from the other side:
  - **An enforcing gate starves its own evidence** (`cohort_edge`'s absorbing
    state). A suppressed candidate never delivers, so it can never join the
    closed-signal record the promotion argument is measured on. Every live
    rejection therefore stamps `_stamp_suppressed`, and the suppression audit's
    forward measurement is where the rule keeps earning its place.
  - **Unknown abstains, and the direction of that fail is a per-path decision.**
    `crypto_perp_admission` is fail-closed because its input is the whole
    exchange; this gate is fail-open because its input is a measurement lane, and
    a fail-closed rule here would kill the feed the moment an order book went
    dark — indistinguishable from a quiet market. The cost is that an inert rule
    reads exactly like a working one, so `unknown_frac` is a column and an
    enforcing rule blind on 80% of its own population pages the watchdog.
  - **A bound you cannot compute in advance is a blast-radius cap, and it is
    counted.** No rule's rejection *volume* had been measured — the ledger is on
    the VPS. Over a rolling cap the gate degrades to shadow rather than
    suppressing, which is order-dependent by construction and therefore its own
    named state on the panel, never a silence.
- **The gate that drops the most had no counter at all, because the artifact
  above it stopped one layer too early.** Asked why the delivered feed sat at
  ~16/day, the funnel said `MOVER_TREND_PULLBACK … Emitted 309` — and
  `_increment_path_funnel("emitted", …)` fires immediately after
  `_enqueue_signal` succeeds, so that column counts **enqueues**. This file
  already said *"emitted" means DELIVERED, and only the router knows that*;
  the funnel had been reading enqueue and calling it emitted the whole time.
  Downstream, `SignalRouter._process` rejects on twelve conditions —
  correlation lock, per-symbol cooldown, per-channel cap, correlation group
  limit, `MAX_SAME_DIRECTION_GLOBAL`, TP/SL sanity, four staleness checks,
  channel min-confidence — and every one was a bare `return` after a
  `log.info`: no counter, no `_stamp_suppressed`, no truth-report section
  parsing those lines (`grep -c` for any counter in that file returned **0**).
  Twelve live gates, zero rows in the Suppression Quality Audit, sitting on the
  one hop that decides what a subscriber receives (2026-08-02). **When you
  cannot find where output went, check whether the last artifact that counted
  it is measuring the stage you think it is.**
- **A `docker exec` one-shot cannot read a live ops tunable — it reads the boot
  default.** `runtime_tunables.get()` returns `tun.default` whenever `_client is
  None`, and a fresh exec'd process never initialises the Firestore client. The
  cohort-edge census printed `GATE enabled=True` and was believed; the engine's
  own in-process counter then showed `cohort_edge:evaluated == cohort_edge:disabled`
  on every candidate — the gate was **off**, and had been suppressing nothing
  while five armed cohorts made it look like the prime suspect for a thin feed
  (2026-08-02). Any diagnostic run outside the engine process reports what the
  image was built with, not what the owner set. **Read live state from a counter
  the engine itself increments**, never from a tunable lookup in a side process.
- **A capped ring makes every verdict on it a sample, and the cap is invisible
  unless printed.** The Suppression Quality Audit's per-gate rings hold 400
  records; `dispatch_cooldown` read `n=396` and nothing on screen distinguished
  "396 suppressions" from "396 of 24,000". The store had computed the eviction
  counts all along (`sampling()`) — they were neither persisted nor rendered, so
  a reader in the truth-report process (a separate script) saw every gate as
  unsampled. Two halves, and fixing only the render would have shipped a column
  reading "all" forever. **When a bounded buffer feeds a statistic, persist the
  eviction count with the data and put the denominator beside the verdict.**
- **Ask what a gate's suppression stamp anchors to before trusting its
  verdict.** `dispatch_staleness_v2` read the worst verdict in the audit —
  DROP, −0.28R, 166.4R missed against 68.6 saved — and that number cannot be
  taken at face value: `_stamp_suppressed` records `entry=sig.entry`, and this
  gate suppresses *precisely because price has drifted away from `sig.entry`*.
  The audit then forward-measures the candidate from a fill nobody could have
  got. The bias is gate-specific (no other gate rejects *because of* price
  drift) and points in exactly the direction that makes the gate look guilty,
  so acting on it would have widened a staleness bound off a number built on an
  unavailable price. Same class as the R-denominator bug: **ask whether the
  quantity a measurement is anchored to is still the thing it was when the
  measurement started.**
- **Never hand-write a collaborator's return shape in a test — drive the real
  collaborator.** A mock whose keys you chose cannot verify a contract you got
  wrong; it asserts your assumption back at you and goes green over dead code.
  `classify_pending`'s guard read `exit_reason` where a trail classifier returns
  `trail_exit_reason`, so every early classification was silently discarded —
  and the tests passed, because they mocked the classifier with the invented key
  (2026-07-26, #798). Where a seam must be faked, fake it from the real
  producer's output, and **verify a fix by reverting it**: if the new test does
  not fail against the old code, it is not testing the fix.

  **It happened again, and the second time the rule was already written down**
  (owner-run VPS check, 2026-08-02). `entry_features.zone_distance_atr` reads a
  zone's edges by guessing key names — `top`/`bottom`/`high`/`low`/`price`.
  `smc.FVGZone` is the *only* thing in this engine that produces zones and it
  carries `gap_high`/`gap_low`, none of those five. So every zone yielded no
  edges, was skipped, and a full book returned `None`: `smc_zone_dist_atr` was
  uncomputable from the day it shipped, **0 of 57 TPE rows**. Its two tests
  passed on `{"top": 105.0, "bottom": 95.0}` — a shape nothing has ever
  produced. Three lessons beyond the original:
  - **A "flexible" reader that accepts several shapes is a guess wearing a
    feature's clothes.** It cannot fail loudly, because skipping an unreadable
    zone is indistinguishable from having no zones. Read the real producer's
    fields by name, and keep speculative shapes clearly labelled as speculative
    — `orderblocks` has **no writer at all** (`orderblocks_detector_status ==
    "not_implemented"`; the VPS truth report counts 474,467 observations, 100%
    empty), so `bool(fvgs) or bool(orderblocks)` has always been `bool(fvgs)`.
  - **A shadow rule can be dead and nobody is watching.** The entry-quality
    probe judged only *enforcing* rules blind, on the reasoning that abstaining
    costs nothing while nothing is enforced. Wrong: a shadow rule that never
    reads its feature can never accumulate the evidence its own promotion
    depends on — a measurement flat-lining without paging. Total blindness is
    now a fault in either mode (0.8 enforcing, 1.0 shadow).
  - **An all-zero column is a claim about your reader before it is a claim
    about the market**, and the caption written over it inherits that. The
    diagnostic that surfaced this printed *"FVG list empty on every TPE signal;
    the gate passed them all anyway"* — self-contradictory on its face, since an
    empty list would have made that gate **reject**. Ask what would have to be
    true for the number to mean what the sentence says.
