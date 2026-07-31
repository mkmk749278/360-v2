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
- **Never hand-write a collaborator's return shape in a test — drive the real
  collaborator.** A mock whose keys you chose cannot verify a contract you got
  wrong; it asserts your assumption back at you and goes green over dead code.
  `classify_pending`'s guard read `exit_reason` where a trail classifier returns
  `trail_exit_reason`, so every early classification was silently discarded —
  and the tests passed, because they mocked the classifier with the invented key
  (2026-07-26, #798). Where a seam must be faked, fake it from the real
  producer's output, and **verify a fix by reverting it**: if the new test does
  not fail against the old code, it is not testing the fix.
