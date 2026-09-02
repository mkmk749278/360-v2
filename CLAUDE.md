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

**Scale target (owner, 2026-09-02): 1,000 auto-trade members.** That is the number
every per-user cost is sized against, not today's handful — a Firestore read, a
Binance call or a Redis key that is free at one user and linear in members is a
bug the moment it ships, and it is invisible in every instrument until the
subscribers arrive. See **Cost Discipline** and `read.firestore_projection`.

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

**Wait ~8 minutes before checking CI here.** That is what this repo's `test` job
takes; ops is ~4 min and `lumin-app` ~16 min. Polling a check run that cannot
have finished yet burns API calls and turns one wait into six — sleep the known
duration first, *then* read the conclusion. Treat these as expected durations,
not deadlines: a job still running at the mark gets another wait, and a job that
finishes early is fine. If a repo's CI time drifts materially, update the number
here rather than re-learning it every session.

Never push to `claude/general-session-*` or harness-assigned long-lived branches. The auto-deploy on `main` ships in ~45s. **Production phase: the app is LIVE on the Play Store** — a `main` deploy reaches real users, so money-path changes ship **dark + shadow-measured + owner sign-off to activate** per § Project Phase — measurement flag ON and visible in ops, user-visible flag OFF. Off-money-path work ships normally.

---

## Shipping Onto a Live Book — the gate a money-path PR passes

Written 2026-09-02, after the day this repo would least like to repeat.
2026-09-01 landed **three** PRs on `main` — a bracket-retirement sweep, an
exchange-position reader, and an incident fix for the first of them — and the
middle of that sequence took **auto-trade down for every paid user for roughly
four hours**. Every guard in this file held except the ones nobody had written
down, and the thing that noticed was **the owner, from his phone**.

The lessons already sit in § Conventions as the incidents that bought them.
This section is the forward-looking half: the checks that run *before* a merge,
not the story told after one.

**1. Count the vendor calls and the Firestore round trips, not the actions.**
The orphan sweep's budget was named for what it *does* (cancel) and the common
production path does nothing — so it spent nothing, ran unbounded, and got the
box rate-limited off Binance. Before merging anything that loops over user
state, state the worst-case number of exchange calls, Firestore reads and
Firestore writes **per cycle** in the PR body, and spend the budget at the TOP
of the iteration so it bounds the branch that does no work. A test on the
do-nothing path is not optional: it is the path production takes.

**2. A new background loop, sweep, or reconciler ships DEFAULT OFF.** It is
armed by the owner after one watched cycle, with the counter to watch named in
the PR body. This costs a day and is the only thing that reliably keeps a
cleanup feature from spending a trading session. Corollary: **a feature that
has once cost live trades never re-arms itself on deploy** — the default is the
incident report.

**3. Name the blast radius in one sentence, in the PR body, before the design
summary.** *"If this is wrong, what stops working for a paying user, and which
switch turns it off?"* A change that cannot answer the second half is not ready
to merge. The answer is also the thing to watch after the deploy — see 4.

**4. Watch the deploy you just shipped.** The 2026-09-01 deploy was 08:07;
placements began failing ~08:30; it was reported ~12:30. Auto-deploy on `main`
takes ~45s and reaches real capital, so a money-path merge is not finished at
the merge — check the money path itself within the hour (placements, the
dispatch funnel, the breaker) and say in the session notes what you looked at.
**A green CI run is evidence about the code, never about the book.**

**5. Three merges to `main` in one day on one subsystem is the warning, not the
achievement.** Each of yesterday's three was individually defensible and the
third existed only because of the first. On a live book, prefer one change,
watched, over a sequence that outruns the evidence — and when a session has
already shipped a money-path PR, the bar for the second one that day is the
owner's, not mine.

**6. The owner is not the monitoring system.** If the only way a failure
surfaces is a screenshot from a phone, the change was unfinished — whatever its
tests said. Ship the counter, the probe, or the ops row that would have caught
it *in the same PR*, and prefer a probe keyed on the population that would be
harmed (paid users whose orders stopped) over one keyed on the subsystem that
happens to be convenient.

**7. Unknown is not a value, and on the money path it must never wear a
value's caption.** This file has recorded that rule for panels seven times; on
2026-09-02 it turned up on the **user's** screen. `/api/auto-trade/runtime-
status` returns `auto_trade_globally_enabled: False` and
`binance_key_connected: False` for three different worlds — the store was never
initialised in this process, the Firestore read raised, or the flag is honestly
off — and publishes no field distinguishing them, so the Lumin app tells a
subscriber *"a safety pause is active … trading resumes automatically"* and
tells a user whose key **is** connected to go and connect one. Two of those
three worlds never resume, and neither is a safety pause. **Any money-path
field a subscriber reads carries its own readability**: the value, and whether
we could observe it. Same rule as the ops caption, one repo further out, with a
paying user at the end of it.

**8. Ask which process holds the state, every time — it is not a deployment
detail.** In isolated mode `src/api/main.py` initialises the keystore and kill
switch **separately from `src/bootstrap.py`, under a stricter precondition**
(both `FIREBASE_PROJECT_ID` and `FIREBASE_SERVICE_ACCOUNT_PATH`, where the
engine needs only the project and falls back to ADC). So the api container can
be blind to Firestore while the engine trades perfectly — and every surface the
owner and the subscriber read is served by the blind one. `INDEX COLD` and the
promotion-census `{}` were this same defect on diagnostic pages; here it
reaches the app and the kill switch.

**9. A safety control that cannot be operated is a Tier-0 fault, and it fails
silently.** `POST /api/kill-switch` returns 503 when this process has no
Firestore client, so B18's *"kill switch takes effect in under 5 seconds"* is
unmeetable from the control plane with nothing red anywhere to say so. Check
that the switches can still be *thrown*, not merely read, whenever a
credential, container, or deployment-mode change lands.

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
- **Never ship a new background sweep, reconciler, or cleanup loop armed by default** — default OFF, armed by the owner after one watched cycle (2026-09-01: a default-ON sweep cost every paid user ~4h of auto-trade).
- **Never spend a loop's budget on the branch that does the work.** Spend it per item examined, before any exchange call, Firestore read, or cancel — a budget that only decrements on success is a retry storm on the path production actually takes.
- **Never render an unreadable money-path flag to a subscriber as though it were readable.** `False` because we could not ask and `False` because the answer is no are different facts; publish which one, or say nothing.
- **Never let a position sit OPEN without a stop.**
- **Never add an uncached Firestore / network read (or write) to a per-tick, per-scan, or per-order hot loop.** Cache it and gate the cache on an invalidation signal.
- **Never let a Firestore read scale with the SUBSCRIBER COUNT.** The auto-trade
  target is **1,000 members** (owner, 2026-09-02). A `collection_group` scan bills
  one read *per document returned*, and a per-user document read on a gate bills
  one per user — so both are invisible at one user and are millions of reads a day
  at the target. Answer the question from an **index document** (`control/active_uids`,
  `control/disabled_uids`), maintained by the writers and rebuilt on a slow timer.
  Before merging, read `read.firestore_projection` on the diag console: it scales
  today's measured reads to 1,000 and prices the excess.
- **Never set a cache TTL at or below the period of the loop that reads it.** That
  is not a cache, it is a rename of the read — see Cost Discipline.
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
- **Reads dominate, and the read budget is a HARD CEILING, not a bill.** Firestore's no-cost tier is **50,000 document reads/day**, resetting at midnight Pacific. Past it a project whose billing account is not in good standing gets `RESOURCE_EXHAUSTED: Quota exceeded.` — not a charge. On 2026-09-02 that allowance ran out at 00:41 UTC on **53k reads against 25 writes**, and every Firestore-backed path failed together: the keystore (so `list_active_uids` returned empty and every signal fanned out to **zero users**), the kill switch (so `POST /api/kill-switch` 503'd — the emergency stop and the thing it stops fail together), runtime tunables, and the dispatch log. **Count reads per day against 50,000 before merging anything that reads Firestore on a timer or a poll**, and read `read.firestore_reads` on the diag console rather than estimating — it counts *documents* per call site, per process, because a `collection_group` query is one call and N reads.
- **A TTL AT the period of the loop reading it is not a cache — it is a rename of the read.** This is the sharpest form of the rule below, and it is what actually spent the allowance. `MONITOR_POLL_INTERVAL` is **5.0s** and the kill-switch cache TTL was **5.0s**, so the entry expired exactly one tick before every read and *could never hit*. Three documents, none of which anybody was editing, on 2026-09-02:

  | Document | Reader | Reads/day |
  |---|---|---|
  | `kill_switch/global` | order path + trail governor | ~17,280 |
  | `kill_switch/global` *(a SECOND `.get()` on the same doc, own cache slot)* | `trade_monitor`, 5s poll | ~17,280 |
  | `control/runtime_tunables` | scanner, every cycle | ~17,280 (at the old 5s) |

  ≈ **51,840 — the entire 50,000/day allowance**, which is why it ran out at 00:41 UTC. **The end state named in this section was already the right one and nobody had built it**: `src/control_generation.py` is that Redis generation. A write bumps it; the monitor's own 5s loop MGETs four tiny integers (free, local, not Firestore) and drops the cache only when one has moved. TTLs are now **floors** (300s), and B18's five seconds is met *by construction* rather than by the accident of a reader re-asking Firestore on the same period — and met faster. Reads on those three documents fall ~60×.

- **Fold every flag on one document into ONE cached read.** `signal_expiry` had its own cache slot and `play_billing` read straight through, so four accessors could take four reads of the same document within a second. Ask of any new flag: does it live on a document something already fetches?

- **A TTL on a continuously-touched document is a spend floor, not a staleness bound.** Ask of every cache: *how often is this touched, and therefore what does the TTL cost per day?*
- **Cache the question the caller actually asked.** `/api/auto-trade/runtime-status` answered `binance_key_connected` — an existence check — by calling `get_key_blob`, fetching and discarding an encrypted secret. `has_key` caches the boolean (invalidated by every writer) and key material is still read through, because caching a secret to save reads on a path that runs a few times a day is the wrong trade in both directions.

  **The number attached to that cut was a story, and it took one grep to falsify.** It was written here as *"~8,600 reads/day from one open Trade tab"*, inferred from an assumed 10s poll — and `grep -rn "Timer.periodic" lib/` in `lumin-app` returns **no runtime-status poll at all**: the Trade tab fetches on open and on pull-to-refresh behind a 60s SWR cache. Right fix, invented figure, in a section whose own rule is *diagnose on real data first*. **An unlabelled inference reads exactly like a measurement** — and this one was published in a merged PR body the same morning.

- **The census that answers "where did the reads go" must cover every read.** The first cut instrumented **9 of 18** sites and was blind to `position_state` — which holds the two `collection_group` queries that scale with the open book — plus `dispatch_log` and `pretp_dispatcher`, the module whose uncached query wrote this whole section in #609. A census with holes points confidently at whatever it *can* see. `grep -c "_reads.record"` against `grep -c "\.get()\|\.stream()"`, per file, is the check.
- **This section said the opposite for months.** It read *"the keystore (`firestore_keystore`) and kill-switch reads are already cached (30s / 5s)"*. The keystore had **no cache at all** — the 30s was `signal_dispatch._ACTIVE_UIDS_TTL_S`, a different module — and that sentence is why nobody looked here. **A constant asserting a property it does not have, checkable in one command**, for the eighth time in these two repos, and the first time it was in the Cost Discipline section itself. Any *new* per-loop reader must be cached and invalidation-gated — see `pretp_dispatcher._default_positions_for_symbol` as the reference implementation.
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
| **Trail governor — the only module that moves a resting stop on a live position** (per-user `exit_mechanism` opt-in) | `src/execution/trail_governor.py` |
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
| Trailing-exit **arm engine** (forward-stepped in the monitor loop, dark) — historically named for SAR, now runs both mechanisms over four lanes | `src/sar_live_shadow.py` |
| The two trailing mechanisms behind that engine (Parabolic SAR · ATR-trail/Chandelier) | `src/trail_mechanisms.py` |
| ATR-trail (Chandelier) lane — ledgers + entry points for the second mechanism, delivered and dark | `src/atr_trail_live.py` |
| Per-path entry-feature stamps (observe-only, joined to the closed-signal record) | `src/entry_features.py` |
| Entry-quality gate — the consuming half of that lane (**LIVE**, per-rule ops switches) | `src/entry_quality.py` |
| Structural SL/TP1 snap — level-aware geometry at the enqueue choke point (measure ON, apply OFF + per-path allow-list) | `src/structural_snap.py` |
| Per-setup trigger timeframe — one declaration, read by the snap and by the scanner's six scoring consumers (correction dark) | `src/setup_timeframes.py` |
| Live aggressive-trade ring, fed from `@aggTrade` (Phase 2a, handover dark) | `src/live_ticks.py` |
| Footprint — buy/sell volume at each price, per bar (Phase 2b) | `src/footprint.py` |
| Live order-book depth, fed from `@depth20@500ms` (Phase 2c, handover dark) | `src/depth_book.py` |
| Layer-3 repair — order-block detector + wide FVG window (Phase 3, both dark) | `src/layer3_repair.py` |
| Structural veto — level ahead of the trade (Phase 4, measure ON / enforce OFF) | `src/structural_veto.py` |
| Standalone price-action lane — level swept + reclaimed, delta-confirmed (Phase 5, dark) | `src/price_action_lane.py` |
| Retention by delivery, shared by every measurement ledger (Phase 6) | `src/delivery_retention.py` |
| Data-intake X-ray — what we actually read from Binance (Phase 1) | `src/data_intake.py` |
| Mover ignition — which pairs get promoted, and the `!ticker@arr` meta behind it | `src/mover_ignition.py` |
| Mover retention — keep a promoted pair while it is still producing (HOLD/RELEASE/EXTEND/WARMUP) | `src/mover_retention.py` |
| Path retirement — remove a `(setup, side)` from the live feed by **diverting** it, never deleting | `src/path_retirement.py` |
| Dark → live promotion, under owner-set per-path conditions | `src/dark_promotion.py` |
| **Diagnostic catalog** — named engine reads + reversible actions, driven from ops. Never a shell | `src/diag_catalog.py` |
| **Cross-process invalidation** for the control documents — the Redis generation that replaced the 5s TTLs | `src/control_generation.py` |
| **Safety-switch bridge** — the engine end of the kill switch, so the stop is throwable when the api container is blind | `src/execution/safety_switch_bridge.py` |
| Firestore read census + cost-at-N-members projection | `src/firestore_reads.py` |
| Host resources — CPU against the cgroup **quota**, memory, disk, and the config the running process is using | `src/host_resources.py` |

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
- **A vendor can split one protocol across routed paths, and the wrong one is
  silent, not broken.** Binance serves book streams and trade streams on
  **mutually exclusive** paths — measured 2026-08-05, one stream per connection:
  `@aggTrade` / `@kline_1m` / `@markPrice` deliver on `/market/stream` and are
  silent on `/stream`; `@depth*` / `@bookTicker` are the exact inverse. Phase
  2c's depth pool inherited `/market/stream` and shipped **40 streams, 40
  silent, 0 messages, pool HEALTHY** — the handshake succeeds, PING/PONG keeps
  the socket alive, `is_healthy` stays true, and zero application-layer frames
  ever arrive. That is the 2026-05-14 multi-hour blackout signature, and the
  docstring written to fix *that* outage is what identified it: it enumerates
  the streams belonging to `/market` (kline, aggTrade, markPrice, forceOrder,
  ticker) and **depth was never in the list**. A hand-written list of what
  belongs somewhere is silent by construction on the next member — the
  `is_tradfi_perp` rule, one layer down.

  Three habits. **Exercise a vendor seam once before shipping it**: the stream
  name was taken from documentation and never connected to, and the probe that
  found this took thirty seconds. **`is_healthy` is a fact about the socket, not
  about the data** — a pool needs a per-stream delivery count before it can
  claim to be working, which is why the `depth_feed` probe keys on symbols
  *subscribed* rather than on what the store holds. And **a guard belongs where
  both facts are in scope**: the declared path and the actual streams meet only
  in the URL builder, so that is where a mismatch is named — with a *different*
  message for a mixed pool, because no single path can serve it and the fix is
  to split the pool rather than change its path.

  Corollary, and it is why this shipped at all: **dark-first is what made this
  cheap.** `DEPTH_LIVE_FOR_CONSUMERS` was off, so a completely dead feed reached
  no signal, and the ops surface that shipped in the same change surfaced it
  within minutes. A dark change without its panel would have been silently dead
  for as long as nobody looked.
- **"Sign-off to activate" is not "sign-off to implement", and reading it the
  second way defers work for nothing.** Phase 3 was described in its own program
  doc as *"dark-first with owner sign-off to activate"*, and it was queued as
  needing approval *before starting* on the reasoning that it "changes what
  emits". It does not: a dark change alters nothing, because the effect flag is
  off — that is the entire point of there being two flags. The owner corrected
  it (*"phase 3 also dark measurement right"*) and the phase shipped the same
  day. **Building the mechanism and choosing its threshold are separable, and
  only the second needs evidence** — the rule this file already carries from the
  other direction ("make it live" is a question about which rules). Before
  deferring a money-path change for sign-off, ask whether what is being deferred
  is the *measurement* or the *effect*; deferring the measurement is how an ops
  panel stays empty and a decision keeps getting postponed.
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
- **A parameter one function reads and no caller writes is #817 one layer
  down — and a comment claiming otherwise is not evidence.**
  `build_channel_signal` accepted `candle_highs/lows/closes` and ran a
  structural SL/TP1 snap behind `if candle_highs is not None`, under the
  sentence *"this snap is shared by EVERY evaluator that passes candle
  arrays"*. `grep -rn candle_highs src/` matched **only the parameter's own
  definition**. It was dead twice over: every evaluator overwrites
  `sig.stop_loss` / `sig.tp1` on the line *after* that helper returns, so the
  snapped values would have been discarded even had the arrays arrived. Nothing
  crashed, nothing was empty — the geometry was simply never level-aware, on a
  book that is 59% `MOVER_TREND_PULLBACK` (an MA stop with TPs at fixed
  1.0/1.6/2.5 R-multiples). Its **test** passed for months by hand-feeding the
  argument production never supplies, proving the fail-open worked in a branch
  nothing reached. Two habits: **pin the call site, not the import** — the new
  test parses `_enqueue_signal`'s AST and fails against the pre-fix tree — and
  when a helper is described as shared, `grep` for the argument that gates it.
- **"Where the geometry becomes true" is four rewrites later than you think.**
  Between the evaluator and the queue, `sig.stop_loss` / `sig.tp1` are rewritten
  by the noise-floor widener, `predictive.adjust_tp_sl`, the min-distance clamp
  at the top of `_enqueue_signal`, and that clamp's proportional TP rescale. A
  measurement stamped any earlier describes a stop that is not the stop — #848
  with the arithmetic removed. `_enqueue_signal`, after the clamp, is the single
  choke point every path passes through. Corollary: **when a bounded adjustment
  can breach a guard the layer above it enforces, refuse — do not re-apply the
  guard.** The snap band bottoms out at 0.7x the designed risk and can land
  inside the `max(0.8%, 1xATR)` floor; widening back to the floor books a stop
  nobody chose, so `would_breach_min_distance` is a named, counted refusal.
- **Ask which half of a measurement the record can actually answer, and refuse
  the other half by name.** The snap's TP1 arm moves *nearer only*, so
  `max_favorable_excursion_pct` settles it outright — every recorded excursion
  precedes the close, so there is no ordering ambiguity. The SL arm moves either
  way and two of its cases are **not in the record at all**: a wider stop on a
  loser (the walk ended at the stop) and a tighter stop on a winner (MFE and MAE
  carry no ordering between them). Those remove **opposite ends** of the
  distribution, so they are counted separately and never pooled — and the two
  arms are never blended, because one number over both would move with the SL
  arm's refusal rate rather than with the mechanism. Same rule as the two fills
  and the two denominators, arriving from a third direction. Related: MFE/MAE
  are updated on **mark-price ticks, not intrabar**, so every "the level was
  reached" verdict is conservative — the lane can under-count rescues and can
  never invent one, and that bias is stated rather than presented as exactness.
- **An absolute grid against a relative consumer is inert at some magnitudes and
  fine at others — stamp the granularity, don't silently fix it.**
  `find_round_numbers` steps by 0.01 below $1, which is 1% at $1 and **20% at
  $0.05**, where no round number can fall inside any plausible stop band. Much
  of the delivered book is sub-$1 movers. Making the grid scale-relative would
  change which levels exist on a threshold invented to fit this window, so the
  lane records `round_step_pct` instead and the ops page reads an all-`swing`
  source column as the grid being inert rather than as round numbers being
  unhelpful. Measure first; the fix needs its own evidence.
- **A hand-maintained per-setup map is a floor — make the miss a counted
  refusal, not a default.** The snap needs each path's *trigger* timeframe (a
  5m swing and a 15m swing are different levels), and the scanner's own
  `_get_primary_timeframe` returns the literal `"5m"` for every channel
  including the two mover paths that trade 15m. `SNAP_TF_BY_SETUP` declares it,
  a setup absent from the map is refused as `tf_unknown` rather than defaulted,
  and a test derives the required keys by parsing the evaluators' own
  `setup_class=` arguments — so tomorrow's evaluator fails CI instead of quietly
  landing in the refusal bucket forever.
- **A constant wearing a lookup's docstring is the same defect as a dead
  parameter, and it had six consumers.** `Scanner._get_primary_timeframe` was
  literally `return "5m"` under the sentence *"return the primary timeframe
  interval string for a given channel name"* — so continuation-sweep evidence
  (the 25-pt SMC dimension), the VWAP extension gate, the OI + funding gate,
  cross-timeframe volume divergence, the chart-pattern confidence bonus (the
  10-pt Patterns dimension) and the volume inputs to `score_signal_components`
  were **all** computed on 5m bars for setups that do not trade 5m. MVRTP is
  ~59% of the enqueued book and trades 15m; MVAVW / MEAN_REVERT / RANGE_FADE are
  15m, MA_CROSS is 1h, WHALE is 1m. Found while wiring the structural snap,
  which needed the same per-setup answer for a different reason — **two
  consumers of one fact is the moment to check whether the first one is real.**
  Three habits it produced:
  - **Pin the shape, not just the value.** The test parses the function's AST
    and fails if the body is a single `Return` of a `Constant`, because a future
    "simplification" back to `return "5m"` breaks six consumers and no other
    test anywhere would notice.
  - **A fallback is not a default.** An empty `setup_class` resolves to 5m —
    correct — but is counted as `unmapped`, never as agreement, so a call site
    that forgot the argument cannot hide behind a path that genuinely trades 5m.
    `declared_for` returns `None` rather than `"5m"` for the same reason.
  - **Check the correction is reachable before claiming it is a fix.** A
    timeframe the scanner never loads would make `_resolve_candles` fall
    straight back to 5m and every column would read healthy — so a test asserts
    every declared timeframe is in `SEED_TIMEFRAMES`.

  And the measurement bounds itself: the resolver's own counters run **~6× the
  signal count** (six consumers per candidate), so the per-signal fact is
  stamped once on the snap row instead and the ops panel divides by that. More
  importantly, five of the six consumers run *before* that stamp — they decide
  whether a candidate exists at all — so the census answers *how much of the
  book is affected* and is structurally incapable of answering *how much better
  it would be*. Pricing the correction needs a shadow gate chain; saying so is
  cheaper than a survivorship-biased number that looks like an answer.
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
- **A measurement that stops at its own exit cannot be read as one that did
  not.** The dark lane's `_walk` breaks at the first TP1-or-SL touch — correct
  for the row's verdict, and it makes `mfe_pct` on a TP1 row bounded by the TP1
  distance **by construction**. Asked for "max PnL before hitting SL"
  (2026-08-03), that column was sitting right there, plausibly sized, and
  structurally incapable of meaning it: it records how far the trade ran before
  its own exit, and everything after that touch was never walked. The same
  truncation is why no held-to-stop or laddered exit could be priced from the
  ledger at all. This is #848's class without the arithmetic — a figure whose
  *shape* is fine and whose *definition* is not what the reader assumes — and it
  is worse than a blank, because a blank prompts a question. **Before rendering
  a stored extremum, ask what stopped the loop that produced it.** The fix was a
  second arm over the same bars with TP1 removed (`_walk_hold`), stamped beside
  the first and never blended with it; the two peaks are different measurements
  and the ops page says so.

  Corollary — **a second arm needs its own sweep.** It exits at the stop,
  normally later than the row's own TP1, so a resolve loop keyed on `status ==
  OPEN` freezes every arm the moment its row closes: #835's shape (a measurement
  inheriting the lifetime of the thing it rides), and it would have been silent,
  because a closed row looks correctly complete. `rows_owed_verdict` covers
  either arm, the freshness stamps grade whichever one is still walking, and
  `resolution_health` watches the same population its docstring already claimed.
- **A comment asserting "this fallback only happens in tests" is a claim about
  production, and nobody had checked it.** `_build_scan_context` assembles
  `smc_data` once, then every scalp channel re-runs SMC detection with its own
  timeframe preference and rebuilds that dict from `SMCResult.as_dict()` —
  carrying the context's additions across via a **hand-written list of twelve
  key names**. `level_book_levels` and `cvd_15m` were not on it. All eight
  scalp channels take that branch unconditionally, so this was every
  evaluator, every scan, since the keys were introduced. Same "a deny-list is
  a floor" shape as `is_tradfi_perp`: the list excludes exactly the keys
  somebody already typed and is silent by construction on the next one. The
  carry is now **structural** — anything the context has that the detector
  does not produce — with an explicit override set for the keys that exist on
  both sides, and a test that derives the contract by parsing
  `_build_scan_context`'s own source so tomorrow's key is covered without
  anyone updating a list.

  **Four live evaluators had been running their pre-fix logic**, and each
  carried a sentence saying otherwise. LSR skipped its HTF POI anchor check
  entirely (§3.4a's hard-block never applied); SR_FLIP fell back to the legacy
  5m pivot detector, replaced 2026-05-17 because 43% of its signals had MFE=0;
  FAR fell back to the 5m struct-scan, replaced because 115 FAR signals ran
  39% MFE=0 at −0.72% NET/sig; DIVERGENCE_CONTINUATION used the legacy 5m CVD
  instead of the "structurally-correct" 15m read. Three of those comments said
  the absent-key branch "only triggers in tests / pre-warm". **When a
  fallback is documented as unreachable in production, go and check that it
  is** — this is the `is_tradfi_perp` rule ("name the paths it covers and
  check each one") arriving one layer down, and note FAR is the setup whose
  +0.846R dark-lane reading had already prompted a promotion request.

  Two structural notes. **`dict.get` makes absent and empty indistinguishable**,
  which is exactly why this survived: three evaluators branch on
  `is not None` to mean "the LevelBook was refreshed", and an absent key is a
  silent, permanent "no". If a sentinel distinguishes two states, something
  must be able to *observe* which one it is in. And the thing that finally
  found it was the probe fixed hours earlier: making `level_dist_r` say
  `no_levels` rather than assert "upstream is dark" turned an unactionable
  page into 4,000-of-4,000 rows with one named cause. **A probe that names its
  cause pays for itself the first time it fires.**

  Corollary — **restoring a dropped input silently redefines what depends on
  it.** `cvd_slope_aligned` had been a 5m CVD slope on every row ever stamped
  and becomes a 15m one; same column, different series, which is the thing
  `tf_name` exists to prevent. Recorded as `cvd_source` rather than
  schema-bumped, because the bump discards ~4,000 rows whose other twelve
  features are unaffected while naming the source keeps both populations
  separable. And **whether a value counts as a feature must not depend on
  where its line sits in a function**: `stack_sep_pct` is declared by
  `MOVER_TREND_PULLBACK` but was assigned *after* the missing-accounting, so
  it could never be reported dark however long it stopped computing.
  `ROW_METADATA_KEYS` names the non-features; ordering can no longer
  reclassify one.
- **A field one repo writes and no repo reads is #817 with the arrow
  reversed — and it is harder to see, because the producing side's test
  passes.** `_price_action_lane_report` shipped in #889 with a test asserting
  its own return shape (`present`, `refusals`, `refusal_share`, `evaluated`),
  which is a mock asserting your assumption back at you **one repo short of the
  reader**. Ops rendered nothing for the key, so the owner opened
  `/diagnostics/data-intake` looking for the refusal mix the PR body had
  promised him and found a page with no such card — after a session whose whole
  subject was *"dark work must be observable"*. The PR body's sentence was even
  true: `/api/data-intake` *did* carry it. **The owner reads the page, not the
  JSON**, and a claim scoped to the endpoint reads as a claim about the surface.

  Two things fell out of fixing it, and the second is the sharper one:

  - **A fixture chooses a location, and then agrees with you about it.** The
    ops fixture put the block at the payload's top level because that is where
    the reader assumed it; the engine nests it under `derived`. Every ops test
    passed against a card that would have rendered `NOT REPORTED` against the
    real engine — the `zone_distance_atr` failure with the shape right and the
    *path* wrong. A cross-repo contract test must **drive the real assembler**
    (`build_data_intake(_Engine())`) and assert the key is where it actually
    lands, including asserting it is *not* at the level you first guessed.
  - **Classification copy is not a mirror, and must not iterate its own keys.**
    Ops attaches a sentence to each refusal reason, so the temptation is to
    render `for reason in OPS_KNOWN_REASONS` — silent by construction on the
    next reason the engine adds, which is `MEASUREMENT_SUFFIXES` and the
    `is_tradfi_perp` deny-list wearing a third hat. The page iterates **the
    engine's payload** and looks the sentence up; a reason ops has never heard
    of renders under its raw name, badged `unclassified`. One writer, one
    reader, and the drift is visible instead of absent.

  Corollary: **the throttle is not a refusal, and pooling it with one inverts
  the reading.** `cooldown` means a setup *was* found and deliberately not
  stamped — positive evidence the lane fires. Bucketed with `no_sweep` it reads
  as the market being quiet when it was us throttling, which is the exact
  mistake #816 cost a session over, arriving from the display side.
- **Flush without load is worse than neither, and a ledger nobody flushes is
  worse still.** Two defects one day apart in the same two modules, both found
  by the owner reading a row count. `structural_veto.stamp` filled an in-memory
  ring and **nothing ever wrote it** — `/engine-data/structural_veto_v1.json`
  never existed, so the page measuring ~97% of the book read `UNREADABLE, 0
  stamped rows` from the day it shipped, while that same session pointed at it
  three times as the highest-value read available. Its own `flush()` carries the
  `force=True` docstring about idle lanes rendering STALE; **it had no caller**.
  That is #839 verbatim — *a docstring describing a heartbeat is not a
  heartbeat, find the caller* — and the tell was that it had no
  `measure_enabled()`, which is what the maintenance loop gates every flush on.

  Then neither structural ledger had a `load()` **at all**, so each restart began
  with an empty ring and the first flush after boot **overwrote** the file. The
  snap page read 12 rows and then 8, with a 4,000 cap and "nothing evicted"
  beside it — nothing *was* evicted; the window was destroyed. Four deploys, four
  erased windows, and a file sitting on disk made both lanes look persistent.
  Without flush the data is merely in memory and the page says so; **with flush
  and no load it is actively deleted on every deploy while the page reports a
  healthy ledger.** It also invalidated a reading published hours earlier — the
  snap's "thin evidence" was not a rare mechanism, it was a ledger being wiped,
  and the difference was invisible from inside the code.

  Restore through the ring's `restore`, never `add`: a **DELIVERED** row must
  come back protected, or Phase 6's retention silently reverts to
  evict-by-recency after the first restart — correct until then, wrong forever
  after. And the guards are derived, not listed: a module with `get_ledger()` and
  a `flush()` must have a caller in `main.py`, must define `load()`, and
  `get_ledger()` must **call** it. *Defining a method is not calling it* — pin
  the call site, not the method.
- **"Dark work must be observable" has a last hop, and it is the nav.**
  `/signals/price-action` and `/signals/structural-veto` shipped with panels,
  tests and PR bodies, and **neither was in the navigation** — reachable only by
  typing the URL, which is what the owner was reduced to after being told three
  times to open one of them. Both also set `active: "signals"`, the *Feed* tab's
  key, so the Feed pill lit up on a page that was not the feed; that is what
  looked wrong on screen before anyone read a label. Worse, the label "Price
  action" was already taken by `/signals/structural-snap` — a different
  mechanism — so the one page a reader *could* navigate to under that name was
  the wrong one. **A panel that renders perfectly on a page nobody can reach is
  exactly as useful as no panel**, and the session that produced those pages
  spent itself quoting that rule. The guard derives the requirement from the
  route decorators and parses the nav literal, because a hand-maintained nav is
  the `is_tradfi_perp` deny-list wearing a fifth hat.
- **A missing label is not a missing outcome — filter, do not purge.** Asked
  whether clearing the rows written before a stamp existed would make the data
  clearer, the answer is no: it would have taken a closed book from **74 rows to
  12**. Those rows lacked `entry_regime` and `level_source_tf` and carried a
  perfectly valid `pnl_pct`; they cannot appear in a *split* and are most of the
  *evidence*. Precision comes from n, so a purge makes an estimate smaller, not
  clearer — and the splits were already clean, because an unstamped bucket that
  is never folded into a real one cannot contaminate anything. Two corollaries:
  **a capped ring rotates the old population out on its own**, so the problem
  solves itself without anyone deciding to delete evidence; and **a purge is only
  right when a field was REDEFINED rather than added**, because then old and new
  rows disagree about what a column means. Related: when two stamps ship hours
  apart, the rows between them carry one and not the other — that middle
  population is real, and folding it into either end misdescribes exactly the
  rows a reader wonders about.
- **A docstring claiming a property IS the absence of that property, often
  enough to check every time.** `LANE_PROVENANCE_FIELDS` read *"Derived from the
  dataclass rather than typed twice — a hand-kept second list is the drift this
  repo has paid for under three different names"* — directly above a hand-kept
  second list. It had already dropped eight provenance fields once, and it would
  have silently dropped all seven layer-1 fields the next change added. The
  sentence was not a lie anyone told; it is what the author *intended* to build,
  left in place after building something else, and it then actively suppressed
  the audit because a reader who greps for hand-kept lists skips the one that
  says it is not.

  This file already carries the same shape three times — `_get_primary_timeframe`
  as a constant wearing a lookup's docstring, `build_channel_signal`'s *"shared
  by EVERY evaluator"* over a dead parameter, `flush()`'s heartbeat docstring
  with no caller. **The tell is that the property is checkable in one command**,
  and nobody ran it. Derive in the direction of the half that does not grow: the
  `Signal` contract is stable, the lane's own columns gain one per program phase,
  so the derivation subtracts the stable set rather than enumerating the growing
  one. The payoff was immediate — two existing tests that loop over the mapping
  covered seven new fields without being touched.

- **A four-layer model with three layers built is not "mostly done" — the missing
  layer can be the only one that separates the outcomes.** The price-action lane
  shipped Location, Trigger and Confirmation and no **Context**, while
  `volume_profile.py` had computed POC and the value area all along and the lane
  never imported it. A sweep + reclaim is a *failed break*, i.e. mean reversion:
  it pays in balance and traps in imbalance, and **those two states produce an
  identical layer-2/3/4 signature** — same level, same sweep, same aligned delta.
  So every stamped column looked like noise, and it genuinely was noise *for
  telling those two apart*, because the discriminating variable was not being
  recorded at all.

  The habit: when a page of measurements all read like noise, ask whether the
  thing that would discriminate is **in the data at all** before ranking what is.
  Two dead ends checked here, both worth not re-running — `rr` shows a clean
  monotonic win-rate gradient (46% → 5%) that is *mechanical*, since `rr` is
  target ÷ stop distance and a farther target must be hit less often; and
  `level_score` looks dramatic (45% → 8%) but is 0.49 rank-correlated with `rr`
  and shrinks to 35% vs 26% once `rr` is held. **Both measure the trigger, and
  the trigger was not what was failing.**

  Corollary, and it inverted the obvious fix: the program doc's diagnosis is that
  this lane has no context layer, which is true — but **eight of the ten BEATUSDT
  longs were stamped `TRENDING_UP`**, so a context layer keyed on the existing
  regime label would have *confirmed* the losing entries rather than filtered
  them. "Check the direction of every recommendation, not only its premise",
  arriving at a fix that was one field away from being shipped backwards.

- **Every exclusion this module guards is an exclusion from a population it
  already had. Ask what never entered it.** `sar_live_shadow` is the most
  carefully guarded lane in the repo — six sessions bought the anchor check, the
  per-advance replay guard, the regressed-vs-rolled-off split, the stall stamps,
  the two fills and the two denominators. Every one of them asks *did this arm
  measure honestly*, and an audit against them found nothing (2026-08-08). Then
  joining the ledger to `signal_performance.json` showed **18.4% of delivered
  trades never got an arm at all, and that slice ran −1.643%/trade at 10.7% win
  against +0.753% and 43.5% for the armed one** — 67.9% SL_HIT against 36.3%. The
  page's `+0.588%/arm` was a winner-enriched subset presented as the mechanism's
  result on our book.

  The cause is one line, and its comment is the whole lesson: `observe_signal`'s
  `_series is None` branch was a bare `continue` under *"Not counted in arm
  health: no arm exists yet, so nothing is owed a verdict."* That reasoning is
  **correct about the arm and wrong about the book**, and it protected the
  largest exclusion in the lane from ever being counted. `record_open_refusal`
  caught only the stale-anchor case, and its own docstring — *"it belongs on
  screen beside the arms it explains the absence of"* — was false: `step_health`
  had two consumers, both inside `main.py`'s probe, and grep for it across ops
  returned nothing.

  This is #815 (*key a probe on the population that would be harmed*) arriving
  one step earlier than any previous fix here: not arms owed a verdict, but
  **signals owed a measurement**. And it is #832's own rule (*what fraction of
  the population resolved, and is the unresolved part random?*) applied
  rigorously to arms that exist and never once to signals that never became
  arms. Corollary on the fix's direction, because it cuts both ways: the unarmed
  slice is SL_HIT-heavy and SAR beats the live exit on SL_HIT, so imputing it
  would make SAR look **better**. Don't — a signal is unarmed because its series
  was missing or stale, which is the same condition under which the mechanism
  could not have been computed or parked live. That is a fact about
  **deployability**, not a gap to fill with a guess.
- **The one defect shape worth naming, because it happened six times in a
  day: a seam.** Two halves that each look complete — wired but called on the
  wrong clock, written but read by nothing, set but dropped by the serializer,
  declared but never assigned, stamped but never flushed, flushed but never
  loaded, built but never linked. **None crashed, none left an empty screen**,
  and each produced a full-looking artifact describing nothing. That is why
  8,113 tests saw none of them and the owner saw all of them from a phone.
  A unit test asserts one half against itself; the seam is where nobody looks.
  **The fix is always the same shape — derive the requirement from the tree
  rather than write it in a list** — and the tell is always the same question:
  *who reads this, and does the thing that writes it run first?*
- **A guard on the inputs is not a check of the output — and the check nobody
  had run was the cheap one.** Six sessions of `sar_live_shadow` defects
  (#835/#836/#842/#846, the regressed-vs-rolled-off split, the two fills, the
  two denominators) all ask *did this arm measure honestly*, and all of them
  reason about the arm's **inputs**: is the anchor current, did the walk jump,
  are the timestamps sorted. None of them ever asked whether the level the arm
  **parked** was the level SAR actually had on those bars. That question needs
  the exchange's own candles, which is precisely what the engine's store is a
  *cache* of, so a stale bucket or a mid-walk re-seed produces an
  arithmetically perfect SAR over the wrong inputs while every guard passes.
  `scripts/reconcile_sar_arms.py` closes it: fetch the bars, rebuild the level,
  diff. Verified 2026-08-09 — the indicator is **bit-exact** against an
  independent Wilder walk over 5,400 real bars, the recorded fills reconcile on
  349 of 349 rows, and 245 of 292 `sar_flip` fills sat exactly on the parked
  level with 47 worse (gap-through) and **zero better**. Corollary that made it
  possible: **SAR forgets its seed.** Every flip resets the extreme point and
  the acceleration factor, so a walk converges regardless of where it started —
  measured at 0 disagreements from 20 bars of warmup, against 13/177 at 3. That
  is what lets a reconstruction be compared to the engine's at all, and where
  it does *not* hold the row is refused as `seed_sensitive` rather than
  reported as a mismatch.
- **A second arm inherits the first's guards only if it rides the first's
  walk.** The held-to-stop arm added to `sar_live_shadow` (max profit before the
  original stop, plus the stop-management rules) is stepped inside the *same*
  bar loop as the SAR arm rather than resolving on its own pass — so the anchor
  check, the per-advance replay guard, the regressed-vs-rolled-off split and the
  timestamp-monotonicity refusal all cover it without a line of new code. This
  is the direct application of *"a measurement lane does not need a resolver, and
  the ones that grew their own each cost a session"*: the cheapest correct arm is
  the one that reuses a walk somebody already hardened. What it does **not**
  inherit is the first arm's *lifetime* — that half is #869's corollary and had
  to be built (`owed_verdict`, progress counted on either arm, retire only when
  both are done), because the held arm exits later than the SAR flip by design.
- **The label seam, and why the render caught what sixteen tests did not.** The
  per-arm strategy state carries a rule *key*; the human-readable label lives in
  the catalog. Ops therefore rendered `be_3`, `lock1_3`, `trail2_3` at the reader
  — correct numbers under names nobody outside this file can read. Every test
  passed, because each asserted `status` / `armed` / `pnl_pct` and none asserted
  the label; the defect existed only on screen. Fixed by shipping
  `catalog_manifest()` **in the ledger**, once per file, so there is one writer
  and one reader and a rule the manifest does not describe renders badged rather
  than renamed. Two habits: **when a table's cells come from one repo and its
  headings from another, the headings are a contract too**, and *render the page
  once before calling a panel done* — this is the 2026-08-06 panel surf's lesson
  arriving during implementation instead of a week later.
- **An additive schema bump that drops its own ledger is the "flush without
  load" defect one level up — and I shipped it the same day I quoted the rule.**
  `sar_live_shadow.LEDGER_SCHEMA` went 1 → 2 to add the held-to-stop arm. The
  bump added fields and changed no existing meaning, and the constant's own
  comment said so: *"nothing is purged and every schema-1 row keeps its full
  standing in the SAR verdict."* `load()` compared `stored != CURRENT` and
  returned, so the first flush after the deploy **overwrote 371 rows** — 4 live
  arms and 367 resolved, the entire window an adoption decision reads. Nothing
  crashed; every panel rendered correctly over zero rows, which is
  indistinguishable from a quiet lane, and the file's mtime was seconds old.

  It is `LANE_PROVENANCE_FIELDS` exactly — **a docstring asserting a property
  the code beneath it does not have, checkable in one command, and nobody ran
  the command.** The tell was available before deploy: grep the loader.

  **A schema bump has two kinds with opposite correct behaviours.** *Additive*
  (fields appear, existing ones keep their meaning) — old rows are still true
  and are most of the evidence, so dropping them makes the estimate smaller
  rather than cleaner; this is *"filter, do not purge"* arriving at the
  serializer. *Redefining* (a field means something else) — old and new rows now
  disagree about what a column **is**, and there the drop is right. The two are
  not distinguishable from the schema number, so the code has to say which it
  is: `ledger_schema.accepts()` takes the additive set as a **required**
  argument, so a new ledger cannot inherit the old behaviour by forgetting — it
  must state which older schemas it reads, and `frozenset()` is a valid answer
  that somebody chose. Reading **forward** is always refused: an old build
  meeting a newer file would be guessing what a field it has never seen means.

  **Five ledgers carried the identical `!=` loader** (`sar_live_shadow`,
  `dark_emission`, `entry_features`, `structural_snap`, `structural_veto`), so
  this was not one mistake but one mistake waiting in five places for whoever
  bumped next — the `is_tradfi_perp` audit shape again. Two derived tests now
  hold the line: every schema-gated loader must declare `ADDITIVE_FROM_SCHEMAS`,
  and no module may compare a stored schema with bare inequality.

  Corollary on the cleanup, because the tempting fix is worse than the loss: an
  ops CSV export of the window survived, and **restoring from it would have been
  wrong.** It is the flattened render columns, not the rows — no nested
  `strategies`, no field the page does not show — so re-injecting it produces a
  ledger that looks recorded and is reconstructed, which is the single artifact
  `/track-record`'s own rule forbids. A destroyed window is recoverable by
  waiting; a ledger that silently mixes the two is not recoverable at all.
- **"Exactly the same" is an argument for one implementation, not two.** Asked
  for an ATR trail measured exactly as SAR is (owner, 2026-08-09), the obvious
  move is a second `*_live_shadow.py` — and it is the wrong one, because
  `sar_live_shadow` is not the SAR mechanism. It is the **arm engine**: the
  anchor-freshness refusal (#836), the per-advance replay guard (#846), the
  regressed-vs-rolled-off split, the stall stamps (#835), the
  timestamp-monotonicity refusal (#842/#844), the two fills, the two
  denominators, the held-to-stop arm and the stop rules (#869) — six sessions of
  guards, none of which is about SAR. The mechanism is *one value per bar*:
  where would the stop be parked, and may it govern yet. So the second mechanism
  added a **parameter** (`src/trail_mechanisms.py`), and the four probe bodies
  that would have been four near-copies became one factory. Four rules fell out:
  - **Each mechanism answers "may I govern" its own way.** SAR has a direction,
    so alignment is that direction agreeing with the side. A chandelier has
    none, so the equivalent question is whether the level it would park is
    already past the close. Forcing one definition would make one mechanism
    answer a question it cannot ask; `up` is therefore `None` for the chandelier
    and never `False` — "does not answer that" and "says down" are different
    facts.
  - **A path-dependent mechanism's state belongs on the ARM, not in a cache.**
    The SAR walk is a pure function of the window, so it caches per
    `(symbol, timeframe, bar)`. The chandelier's ratchet is anchored to the
    arm's own first bar, so two arms on the same symbol and bar legitimately
    hold different state — sharing a cache entry would hand the second arm the
    first one's history, which is #846 arriving through a cache instead of
    through a store and just as silent.
  - **Health lanes multiply with the mechanism, not just with delivery.** There
    are four populations now, and the rule that split `live` from `dark` applies
    identically on the mechanism axis. SAR keeps the bare `live`/`dark` keys —
    not deference to history, but because `main.py`'s probes and the ops surface
    read them, and prefixing them would silently empty a probe that then reports
    a healthy zero.
  - **Name the second mechanism's exit apart from the first's.** SAR *reverses*;
    a chandelier stop is simply *touched*. `CLOSED_TRAIL_STOP` beside
    `CLOSED_SAR_FLIP` costs nothing (the lanes never pool) and one word for two
    events is how a page stops being able to say what happened.

  And the check worth copying: ops' exit bake-off has printed **"ATR-trail
  (Chandelier)"** since long before this arm existed, so the engine adopted
  *that* definition (position-scoped ratchet from the entry bar) rather than
  TradingView's indicator-scoped one, and a shared vector pins them. Two arms
  named for the same mechanism measuring different mechanisms already cost a
  session on 2026-07-31 — and the agreement was verified by driving ops' real
  simulator, which fills at the engine's level to 1e-9.
- **An idempotence key that only advances on success is a retry storm, and the
  docstring will say otherwise.** `trail_governor._park` leaves the previous
  stop resting on a rejection and returns False — correct, and its comment
  promises *"retrying next bar"*. But the bar it retries from is
  `trail_last_bar_ms`, which is written **only after a successful park**, so the
  `same_bar` guard never engaged after a failure and the identical level went
  back to Binance on every monitor tick. Measured live on the owner's account
  2026-08-10: two governed positions, `place_failed` +24 a minute, forever,
  against an exchange that has IP-banned this box before. Nothing was unsafe —
  the position kept its designed stop throughout — which is exactly why it could
  run indefinitely without anyone noticing. **Ask of every "retry later": what
  advances the clock it is measured against, and does a failure advance it?**
  The deferral is free here for a reason worth checking before copying it: the
  level is *fixed for the bar*, so re-asking the same question of the same bar
  cannot get a different answer, and the protection is untouched while it waits.
- **A counter is not a cause on a path that talks to a vendor.** `place_failed`
  said the exchange refused and could not say what it said: -2021 (the level is
  already through the mark), -1111 (rounding), -4015 (duplicate client id) and a
  disconnected key are one integer and four different fixes. The reason existed
  the whole time — in a `log.warning`, which needs `docker exec`, while the
  owner reads the panel. Same class as *"blank needs a cause before it gets a
  caption"*, arriving on the one path that spends money, and the ops copy beside
  it made it worse by calling the state *"the safe failure"*: true about
  protection, silent about a handover that will never happen. Keep the vendor's
  own words in a bounded ring **with the unbounded count beside it**, and let
  "no code" mean *the rejection did not come from the vendor* rather than zero.
- **A store, a migration and a UI are not a wired path — the API model is, and
  `exclude_unset` deletes what it was never told about.** `exit_mechanism` shipped
  with a SQLite column, a migration and an ops control, and `AutoTradeSettings`
  never declared the field — so `model_dump(exclude_unset=True)` dropped it on
  **every** write and the setting was reachable by nothing. That is the banned
  scaffold (*"a setting the engine stores but does not yet consume"*), shipped by
  me, on the control that decides how a real position closes. The tell was not in
  the tests, which passed: it was that **the setup guide could not be written
  without inventing a step.** If documenting the feature requires a step the code
  does not have, the feature is not wired — write the guide before calling it done.
- **Which process holds the state is not a deployment detail.**
  `/internal/diag/trail-governor` assembled its X-ray in the **API** container,
  which in isolated mode cannot see the engine's in-process position index — so the
  page read `INDEX COLD` in production while the governor was working fine. Both
  sibling diags already used publish-then-read through Redis; this one was written
  as if the engine served HTTP, which is the *other* mode. `API_PROCESS_ISOLATED`
  changes what a module can observe, not merely where it runs — **before reading
  in-process state in a handler, ask which container the handler is in.**
- **A setting with two legal values must be unselectable-wrong, not merely
  validated.** The governing timeframe was typed as free text; the owner set it
  from ops and typed `5`, the store keys `"5m"`, and `set_values` validated floats
  and ints and nothing else — so the governor went **permanently inert with the
  switch reading ON**, refusing every position silently. Fixed at both ends, and
  both halves are load-bearing: `Tunable.choices` renders a `<select>` so ops
  cannot send a wrong value, and `REFUSE_BAD_TF` counts and names it at the sweep
  so a value arriving by any other route is a visible refusal rather than a
  silence. Note the half that a later session still had to pay for:
  `runtime_tunables.get()` validates nothing against `choices`, so a value stored
  *before* the fix kept being served — **the write path was refusing what the read
  path kept handing out.**
- **A setter that reads its value back still needs a READER, or the control can
  only ever show its first option.** `POST /api/admin/users/exit-mechanism`
  reads the stored value back rather than echoing the request — deliberately,
  with a docstring saying so — and `GET /api/admin/users/lookup` never carried
  the field at all. So the ops select was three hardcoded options with nothing
  selected: an account already handed to SAR rendered *"default (SL/TP FSM —
  unchanged)"* on every reload, and the owner's only evidence that his write had
  landed was a flash message that had already scrolled past (owner-caught
  2026-08-10). #817 with the arrow reversed, at the one control that decides how
  a real position closes. **A write surface is unfinished until the same page
  can show what is stored** — and the display needs three states, not two,
  because an engine that predates the field must read *not reported* rather than
  inherit the meaning of `default`.
- **A safety argument about FILLS is not an argument about ACCEPTANCE, and the
  exchange only ever tested the second one.** `trail_governor` places the new
  stop before cancelling the old one so the position is never naked, and its
  docstring justified that with `closePosition` semantics: such an order carries
  no quantity, so two resting at once cannot double-fill — the nearer level
  triggers, the position goes to zero, the other finds nothing to close. True,
  checkable, and beside the point. Binance answers a second `closePosition` stop
  in the same direction with **-4130** *"An open stop or take profit order with
  GTE and closePosition in the direction is existing"*, so the second one never
  rests at all — and by the naked-position invariant a governed position always
  has a stop resting. **The handover was impossible for every position from the
  day it shipped**, and the code was internally consistent the whole time.
  Same class as the depth-stream path (2026-08-05): *exercise a vendor seam once
  before shipping it*, and note both were found only because the ops surface
  shipped alongside. The repair keeps the ordering and changes the order
  **shape** — `reduceOnly` with the position's size — and the evidence that this
  coexists with a `closePosition` SL is **the running system**, not the docs: the
  whole TP ladder is already that shape and rests beside the SL on every live
  position. When choosing between two vendor behaviours, look for the one your
  own production book is already demonstrating.
- **When you change a property, the test asserting the old one can keep passing
  for an incidental reason.** The dark divert's safety property was *one branch*
  — `if is_dark(sig): … return` — and `dark_promotion` made it two, because a
  matching candidate now deliberately falls through to `signal_queue.put`. The
  existing guard asserted *"the dark branch must return, not fall through"* by
  searching the branch's source text for `return`, and the word was still there
  in the **other** half. So the assertion that most directly protected paid
  subscribers went green over a tree where its own sentence had become false.

  This is not a seam — both halves were written by the same change, in the same
  file, minutes apart. It is the **rot** case: an assertion outliving its
  premise at the exact moment somebody is changing the premise, which is the one
  moment nobody re-reads it, because the suite is green and the diff is the
  thing under review. The tell is cheap and worth making a habit: **when a diff
  changes an invariant, grep the suite for the invariant's old words and read
  every hit as a reviewer, not as an author.**

  Two corollaries. **Substring assertions rot silently and AST assertions do
  not** — the replacement walks the tree and pins the property that actually
  holds now (*the only path from a marked candidate to the enqueue runs through
  a promotion decision, and every other path returns*), which cannot be
  satisfied by a stray keyword. And **narrow an over-broad invariant rather than
  deleting it**: the sibling guard forbade the router from mentioning
  `dark_emission` at all, which forbids the delivery measurement and says
  nothing about the danger — the danger is the router *branching* on dark state.
  It now allows a write-only stamp from a named allow-list, asserted by AST to
  be a bare statement rather than a condition or a return value, and
  `signal_dispatch` / `push_notifications` stay absolutely forbidden. An
  invariant that blocks correct work gets deleted by whoever needs the work;
  one that states what it means survives.
- **A refusal that computes its reason and discards it is a fault with a
  docstring for an alibi.** `dark_promotion.decide` builds the full list of
  unmet conditions on every rejection — the module's own docstring says why,
  *"so the ops panel can say 'matched the gate and the session, failed the
  regime' instead of leaving the owner to guess which half of his rule is
  wrong"* — and **every caller threw it away**. The scanner's refusal branch
  calls `dark_emission.publish(sig)` with no decision; the only counter was
  `unmet:{setup_class}`, one integer over five dimensions; and
  `PromotionDecision.to_row` is reached only when the answer is YES, where
  `promotion_unmet` is `[]` by construction and no repo reads it. So the owner
  armed two rules, 610 `LIQUIDITY_SWEEP_REVERSAL` candidates were diverted in one
  truth-report window, zero were promoted, and the entire diagnostic available —
  in the engine, in the truth report and on the ops page alike — was *"2 rule(s)
  armed, 0 promoted today"*. The probe printing it called that the benign case:
  *"the market has not offered a candidate matching it"*, a claim nobody could
  check (2026-08-17).

  That is `LANE_PROVENANCE_FIELDS` for the fifth time — **a docstring asserting
  a property the code beneath it does not have, checkable in one command** — and
  the tell is the same one: grep for the field's readers.

  Three habits beyond the fix:

  - **Count the SOLE blocker, not only the marginal one.** A rule is a
    conjunction, so a candidate can fail four conditions and no single edit
    changes anything; the marginal count cannot tell that from four candidates
    each failing one. `sole_blocker` is the number that says *relax this and
    exactly this many rows promote*, and it is the only one an operator can act
    on. Keep the cap as its own dimension — a rule at its bound is working and
    throttled, a rule that never matches is misconfigured, and the cap check is
    last precisely so the two never pool.
  - **A control built from MARGINAL evidence over a CONJUNCTIVE rule needs the
    joint count, or its own honesty rules mislead.** Ops' promotions page offers
    one table per dimension, sorted by evidence, cell count printed — every rule
    this repo has, applied one dimension at a time. And the best-looking cell of
    each can intersect at zero while all of those numbers still read
    well-evidenced. Marginal tables cannot say that; only *"the rule as saved
    selects M of N"* can.
  - **Record the observed value, not just the verdict.** The census says a
    dimension refused; the near-miss ring says the row was stamped `RANGING`
    while the rule asked for `with_trend` — and both trend conditions *abstain*
    on a label naming no trend, so the rule refuses rows that look eligible. One
    sample carries that; no total does.

  Corollary, and it is the sharpest form of *which process holds the state is
  not a deployment detail*: `decide` runs in the **engine** container and the
  ops control panel is served by the **API** one, which loads the registry off
  the shared volume and has never evaluated a candidate. So `counters` was `{}`
  and every rule's `promoted_today` was `0` on that page, permanently — the
  trail-governor `INDEX COLD` defect, except that **zero is also what a
  correctly armed rule reads before it fires**, so the wrong number was
  indistinguishable from the right one and would only have started looking wrong
  once the rule began working. Publish-then-read through Redis, like the three
  sibling X-rays; `runtime_report` is split from `snapshot` so the file-backed
  half stays correct in either process.

- **A thread does not free the loop when the work holds the GIL — and the
  frequency, not the duration, is what decides whether that matters.** Moving
  the Layer-C save off `trade_monitor` with `asyncio.to_thread` genuinely
  removed ~2s x 2 from the money path at signal close. It did **not** remove the
  stall: measured at the real payload (41.7 MB), `json.dumps` in a thread takes
  1.85s and the event loop loses 1.85s of it — the C encoder holds the GIL
  throughout, so the thread moved *where* the code runs and not *whether* it
  blocks.

  Then the diagnostic built to price it inverted the conclusion. Live store:
  11,279 cells, 198,090 records, **`saves: 0` and `recorded_total: 0` since
  boot**. The store only goes dirty when a signal *closes*, so the stall happens
  at roughly the rate of closed signals — about **16 a day**, not the 120/hour
  that "every 30s when dirty" implied. Real cost, wrong order of magnitude, and
  **not** a plausible cause of the writer overruns it was being lined up
  against. *"A finding and a fix are separate deliverables"* arriving with the
  measurement contradicting the fix. Corollary: **read the counter before
  costing the operation** — duration was measurable in a sandbox and frequency
  was only ever knowable from the running engine.

- **A shell is not the way to let a surface drive the engine; a named catalog
  is.** Asked for command execution from ops (2026-08-19), the shape that ships
  is `src/diag_catalog.py`: entries selected by **key** from a registry, no
  shell, no eval, no argument interpolated into a command line. The safety
  argument is *asserted*, not written — each entry's own AST is walked for
  money-path names and for `subprocess`/`eval`, parametrised so tomorrow's entry
  is covered without editing a list, and the single dynamic import is pinned to
  a literal tuple inside its own function so a later edit cannot turn it into
  import-by-name.

  The owner's security premise is worth keeping straight because it is right
  about the threat it names and silent about this one: an IP-whitelisted,
  futures-only, no-withdraw key defeats a **stolen** key used from anywhere
  else, and says nothing about code running **on** the whitelisted host, where
  futures permission is not symbol-scoped. So the exposure arbitrary execution
  would carry is a **position**, not a withdrawal — which is exactly why the
  catalog excludes anything that can reach an order.

  Three rules fell out. **Two kinds, and the split is the whole argument**:
  `read` observes, `action` mutates something reversible and off the money path,
  and every action carries a written `effect` — one nobody had to justify is how
  a list grows past what it was approved for. **Enforce the switch where entries
  RUN**, never only where they render: hiding a button while the request still
  executes is a control in appearance only, and the endpoint is reachable by
  anything holding it. And **a switched-off entry still renders, marked OFF** —
  a vanished one reads as a broken deploy.

- **A request/response bridge already existed; the fire-and-forget one was the
  wrong sibling to copy.** The diag channel needs its answer back, so it mirrors
  the **manual-take** queue (LIST in, result under a request id, TTL) rather
  than the mode-change key beside it. It has to cross into the engine container
  at all for the reason `INDEX COLD` records: in isolated mode the API process
  cannot see the scanner, the stores or the executor, so a diagnostic assembled
  there describes the wrong process. Three properties the copy adds: the drain
  is **bounded per cycle** so a flood cannot starve the snapshot writes that
  loop exists to make; a **stale envelope is refused rather than applied** (the
  caller stopped waiting, and for an action that would apply a change whose
  requester is long gone); and a poll timeout says *"the engine did not
  answer"* rather than returning an empty result.

- **`ruff` caught what 8,648 tests could not, because no test entered the
  handler.** A missing `DIAG_POLL_TIMEOUT_SEC` import sat inside a route body
  the suite never exercises — `F821`, invisible to a green run. **The linter is
  not a formality on a codebase with handlers this thin on coverage**; run it
  before believing a passing suite.

- **Two changes in one PR can each be right and jointly wrong — and "it
  stopped" needs a window proportional to the thing's period.** #961 vectorised
  the indicators into numpy *and* resized the scan executor from the cgroup
  quota (8 -> 3 workers) on the reasoning that "threads contending for one GIL
  buy switching cost and no throughput". Each half is defensible alone. Together
  the second invalidates the first's premise: **numpy releases the GIL**, so the
  pool running exactly that work shrank 2.7x at the moment its work became
  parallelisable. Nothing in either half's own reasoning surfaces the
  interaction — **when a PR changes both a workload and the resources for it,
  state the interaction explicitly.**

  I then declared the restart loop fixed off a **51-minute window with no
  restarts**, and it returned within two hours. An autoheal loop that fires
  every ~30-60 minutes cannot be declared fixed from 51 quiet minutes; this file
  already says to wait for a fresh window before judging a change, and the
  window has to be proportional to the *period of the thing being judged*.
  **State the window beside the claim, or do not make the claim.**

  The evidence that found it is the argument for the diagnostic console:
  `_MAX_CONCURRENT_SCANS` is 20 and each scan *awaits* `run_in_executor`, so the
  `indicators` stage timer **spans a wait** — 461.7s inside a 91.15s cycle,
  ~5x concurrency of queued waiting, against **1.2 of 3.2 allotted cores**.
  Queueing with two cores idle is thread starvation; a GIL ceiling pins one
  core. Corollary worth keeping: **a stage timer that wraps an `await` measures
  waiting, not work**, so its ratio to the cycle is a concurrency reading and
  never a CPU one.

- **Three hypotheses, three refutations, one day — and the pattern was in my
  reading, not in the system.** Chasing an autoheal restart loop on 2026-08-19 I
  formed and shipped reasoning on: executor starvation (real misconfiguration,
  not the cause), mover accumulation (pairs sat at 78–79), and a new pair's
  inline REST seed (a spike arrived with the pair count flat one sample later).
  Each was formed from two or three samples and each died on the next one. Two
  separate "it is fixed" claims died the same way.

  The habit that would have prevented all five: **before naming a mechanism,
  write down the observation that would refute it, then wait for that
  observation.** It costs one sampling interval and it is the difference between
  a hypothesis and a story. When I finally did state a refutation condition in
  advance ("if a spike arrives with the pair count flat, this is dead"), the
  refuting sample arrived within the hour and cost nothing — because the claim
  had been made falsifiable *before* it was made confidently.

  Corollary on instruments, learned the same evening: **an instrument that
  travels on a starved channel cannot measure the starvation.** `in_flight_sec`
  and `in_flight_stages` ride the snapshot the writer publishes, and the writer
  shares the loop the hang starves — so they capture the early part of a hang
  and can freeze before its peak. State that limit where the number is read; a
  reader who does not know it will take a frozen value for a settled one.

- **A health check measures one quantity; make sure it is the one whose fault
  the remedy can cure.** Three sessions hunted a cause for the autoheal restart
  loop and the loop's cause was the check. `healthcheck.py` fails on the
  heartbeat file's age, autoheal restarts on that, and the file's only writer
  was the **end of a scan cycle** — so cycle wall-time and heartbeat age were
  one number, and a cycle past 120s *was* a restart however healthily the loop
  was advancing. Autoheal cures a **wedge**; a slow cycle is not a wedge, and
  the restart made it worse (every restart re-seeds ~79 pairs over REST and
  rebuilds the indicator caches cold, so the next cycle is slower than the one
  that tripped the deadline). Measured 82.4s median / 402.5s worst against that
  bound. The fix is not a wider bound — that only delays catching a real wedge —
  it is to **beat on progress** (a symbol finished) so the file answers "is the
  loop advancing" rather than "did a cycle fit in the window".

  The tell was written in the file, again: `_HEARTBEAT_MAX_AGE_SECONDS`'s own
  comment read *"Must be longer than a worst-case scan cycle"* and the value did
  not satisfy it. That is `LANE_PROVENANCE_FIELDS` for the sixth time —
  **a constant asserting a property it does not have, checkable in one
  command** — and this one cost a day of restarts.

  Three habits beyond the fix:

  - **A bound written for one branch is not a bound on the condition.** The
    2026-07-24 restart-loop guard caps autoheal at 3 attempts and covered
    **only** the never-beat-since-boot branch; a scanner that beat during
    warm-up and then went stale fell through to an unbounded fail. The
    observed behaviour proves which branch fired: had it been the bounded one,
    the loop would have self-limited inside 30 minutes instead of running all
    day. **When a guard exists and the thing it guards against is happening,
    check which branch reaches it** before looking for a new cause.
  - **Renaming what a key measures is a cross-repo change.** `heartbeat_age_sec`
    was computed from `last_cycle_at` — correct while the cycle end was the only
    writer, and a lie the moment it was not. Ops grades `/system/liveness`
    "hanging" off that key, so leaving it would have kept calling a healthy slow
    cycle a hang. Fix the field to mean its name, publish the other under its own
    name, and update the caption: *an alarming caption over a healthy subsystem
    sends the owner to debug something that works* (`/invalidations`, #7).
  - **State the refutation condition and the window before deploying.** Two
    "it is fixed" claims died within hours on 2026-08-19 because both were read
    off a window shorter than the period of the thing being judged. This one
    ships with both written down: if restarts continue at the same ~15-minute
    period, check `heartbeat_progress_writes` before forming a new theory — and
    a quiet hour proves nothing about a ~15-minute period.

- **A vendor's auto-cleanup is a property of the ORDER TYPE, and the docstring
  claimed it for the wrong one.** `order_placer.place_pretp_trail` read *"TP
  orders have `reduceOnly=true` and Binance auto-cancels reduce-only orders
  when the position is closed by another order"*, and the whole bracket-cleanup
  design rested on that sentence. Binance sweeps reduce-only orders resting on
  the **order book**; every SL and TP this engine places is an **algo** order
  (`/fapi/v1/algoOrder`, `algoType=CONDITIONAL`) sitting untriggered in the
  conditional engine, which is not swept. So *nothing* retired a bracket at a
  terminal close: `_apply_sl_fill` is the plain case — the stop fires, the
  position goes flat, and TP1/TP2/TP3 stay parked. Owner screenshot 2026-09-01:
  **Positions (0) / Open Orders → Conditional (24)**, oldest 15h old, FETUSDT
  carrying a resting Sell TP and a resting Buy TP at once.

  The tell was in Binance's own UI, which files the two under separate tabs —
  *exercise a vendor seam once before shipping it*, the depth-stream rule
  (2026-08-05) at the order layer. And the knowledge already existed in this
  repo: `close_fsm_positions_for_signal` sweeps the same set and its comment
  says the auto-cancel claim is false. It never reached the fill handlers,
  where most closes actually happen. A **seam**, in the usual shape — nothing
  crashed, nothing was empty, and a reduce-only orphan books no loss of its
  own, which is why it ran for months.

  Three habits. **Sweep at the choke point, not per handler**: the FSM now
  cancels once, keyed on `is_terminal(position.state)` after the phase
  dispatch, so a handler added later is covered without anyone remembering —
  and the attr set is *derived* from the dataclass in `position_state` rather
  than typed out a third time (two hand-kept copies already existed and
  disagreed). **Zero the id before persisting, not after**, or a crash strands
  a document claiming orders that are gone. And **keep the id on a failed
  cancel**: it is the only record that an order is still out there, and the
  reconciler reads the same fields.

- **Two surfaces on different clocks BY DESIGN still need somebody to price the
  divergence.** `SIGNAL_EXPIRY_ENABLED` went False on 2026-06-26 so signals run
  to TP or SL and never expire mid-move — deliberate, owner-decided, and its
  config comment explicitly notes *"the 2h auto-trade reconciler stale-close
  safety net is unaffected"*. Both halves were known. Nobody asked what the
  pair produces: **39 of 140 matched positions (28%) closed at 120–121 minutes**
  in the owner's 24 Aug – 1 Sep Binance history, none by a TP or a stop, with
  nothing in the window surviving past 121.4 minutes — while the signals above
  them ran a median 2.4h longer (max 46.6h). That is the app showing five
  ACTIVE signals over a Trade tab reading zero positions.

  **And the obvious fix is wrong, which is the part worth keeping.** Raising
  the ceiling so positions match signals: scoring those 39 against what their
  signal went on to do gives **15 better, 23 worse, +0.48 USD over 38 trades**.
  The backstop costs no money; it costs *coherence*, so the repair is on the
  surface (name `STALE_EXPIRY` in words on the signal card, tell the reader the
  two tabs answer different questions) and not on the number. *Check the
  direction of every recommendation, not only its premise* — the premise was
  right and the lever was somewhere else.

  Corollary: `RECONCILER_MAX_POSITION_AGE_SEC`'s comment read *"comfortably
  beyond any legitimate scalp hold … so it never clips a healthy position"*.
  It clipped 28% of them. **A constant asserting a property it does not have,
  checkable in one query against data the owner already had** — the seventh
  recurrence in these two repos, and the first where the query needed the
  *exchange's* record rather than ours. Where a claim is about what actually
  happened on the account, the engine's own ledger cannot settle it.

- **"Some signals don't trade" was 88% a working system and 12% one gate with
  a name.** Joining the delivered feed to the Binance position history over the
  same window: **140 of 159 delivered signals placed**. The 19 that did not are
  not scattered — BTC, ETH, LTC, AAVE, LINK, BCH and FF **never traded once**,
  which at a ~$10 notional is the `NotionalTooSmall` refusal
  (`_compute_qty_split` returns zeros when the LOT_SIZE floor cannot clear
  MIN_NOTIONAL even after the one-step snap-up). The engine had recorded every
  one of them with actionable copy since the path shipped. **Before diagnosing
  a fan-out, join the two ledgers and count** — the shape of the miss list is
  the diagnosis, and "some signals" turned out to name one filter and one
  setting rather than a fault.

- **Ask what the vendor is already telling you before inferring it.** The
  position card was built to show "exactly what Binance shows", and its first
  cut computed size, entry and unrealized PnL from the engine's own document
  marked with a mark price — because nobody checked what was already on the
  wire. `events.parse_event` had decoded `ACCOUNT_UPDATE` into a typed
  dataclass (signed size, entry price, unrealized PnL, margin type, isolated
  wallet) since the user-data stream shipped, and `grep` for a consumer
  returned **nothing**: `PositionFSM` no-ops it, and its docstring said
  "consumed by PR-9 reconciler" — the reconciler consumes `positionRisk` over
  REST and has never seen a stream event. Beside it,
  `_fetch_binance_positions` fetched the whole `positionRisk` row every cycle
  and kept `positionAmt`, discarding `liquidationPrice` and `leverage`, which
  exist in **no other source at all**.

  So this was not a missing feature, it was a missing *reader* — the third
  variant of this repo's commonest defect, after "written and never read" and
  "read and never written": **arriving, parsed, and dropped.** The tell is
  the cheapest one there is: a docstring naming a consumer, and a grep for
  that consumer.

  Two rules the fix carries. **Two sources for one quantity are kept apart by
  clock and by authority, not merged**: the push wins for the fields both
  carry, because a five-minute REST snapshot overwriting a live size walks the
  number backwards on screen; REST supplies only what the push cannot; and
  freshness is reported per SOURCE, since one "as of" over two clocks is a
  claim neither of them made. And **a flat frame is a fact, not an absence** —
  the exchange saying "you are out" is precisely the fact the Trade tab could
  not distinguish from "nothing was ever placed", so it is recorded with its
  timestamp and retained briefly rather than deleted.

  Corollary, found by writing the test rather than by reading the code: a
  retain window a whole class of rows never enters is not a bound. Stamping
  `flat_since` only on the open→flat TRANSITION left every position whose
  FIRST frame is flat — the ordinary case after a restart — unevictable
  forever.

- **Preventing the defect is not repairing it, and shipping only the first
  half leaves the screen the owner complained about.** The terminal-close
  sweep guarantees no NEW orphaned bracket, and said nothing about the 24
  already resting: `reconcile_user` filters to non-terminal positions, so a
  document that closed before the fix landed is never looked at again. A
  backlog is finite and historical, which makes it exactly the thing a
  one-off, converging sweep can clear — and exactly the thing that stays
  forever if nobody writes one.

  The safety argument is worth copying because it needed no new vendor
  behaviour to be verified: the sweep cancels only ids appearing BOTH on one
  of our own closed documents AND in Binance's list of open algo orders for
  that symbol. It therefore cannot reach an order we did not place, cannot act
  on a stale id, and cannot touch anything protecting a live position — and
  `None` from that fetch ("we could not ask") is kept strictly apart from an
  empty set ("Binance confirmed nothing is open"), because conflating them
  clears every id and declares a dirty account clean.

- **A budget that does not decrement on the common path is not a budget —
  and the test that only exercises the uncommon path will pass.** The orphan
  sweep's per-cycle cap was written as a CANCEL budget and spent only when an
  id came back CONFIRMED OPEN. On a real account almost every historical
  protective order has long since filled, so the id is *already gone*, takes
  that branch, and costs nothing — leaving the loop to run over all ~350 of a
  user's closed-position order-id fields: one signed `algoOpenOrders` GET per
  DISTINCT SYMBOL (this account has traded 79) plus a Firestore read and write
  per gone id, every cycle. Binance rate-limits by IP and the engine is
  whitelisted to one box, so **every subsequent order failed
  `OrderPlacementUnreachable` and auto-trade was down for hours**
  (owner-caught 2026-09-01, hours after I deployed it).

  The comment sitting directly above that cap said it existed because this
  account "has been IP-banned for hammering before". I wrote the sentence and
  the defect in the same commit.

  Three habits. **Spend the budget at the TOP of the iteration, before any
  work** — then it bounds every path, including the ones added later, rather
  than the single path whoever wrote it was picturing. **Ask which branch is
  the common one in production**, not which one the feature is named after:
  here the feature is "cancel orphans" and the common branch is "nothing to
  cancel". And **a bound needs a test on the path that does NOT do the work** —
  mine covered the cancel path only, so it passed against code that was
  unbounded in the case that actually runs.

  Corollary on the remedy: a cleanup feature that has cost live trades ships
  **default OFF** afterwards, and the default is the incident report. Nothing
  depended on it — the orphans are reduce-only conditional orders that book no
  loss of their own, and the terminal-close sweep prevents new ones regardless
  — so leaving it armed bought nothing and risked the money path twice.

- **Writing the defect down is not fixing it, and a CLAUDE.md-only PR reads
  like a fix in the log.** 2026-09-02 shipped two PRs about the kill switch
  being inoperable: ops `#198` was **33 lines of this file's sibling and zero
  lines of code**, and engine `#995` touched `kill_switch.py` for six lines of
  read-counting. Both PR bodies describe the fault precisely — *"a safety
  control that cannot be operated is a Tier-0 fault"* — and the owner's next
  screenshot was identical, because `POST /api/kill-switch` still returned 503
  and `src/api/main.py` still gated on a stricter precondition than
  `bootstrap.py`. The session that wrote §9 of *Shipping Onto a Live Book*
  spent itself writing §9.

  This file exists to stop a lesson being re-learned; it is not where a fault
  gets repaired. **When a session diagnoses a live fault, the deliverable is
  the code — the entry here is the receipt, and shipping only the receipt is
  worse than shipping nothing**, because the next reader finds the defect
  already documented and assumes it was handled. Two habits: a doc-only PR
  about a *live* fault names, in its own body, the PR that carries the fix; and
  when a session ends with a fault still live, that goes at the TOP of
  `ACTIVE_CONTEXT.md` as open, never in the past tense.

- **A safety control needs a path that survives the container it is served
  from.** `POST /api/kill-switch` had exactly one implementation: read the
  Firestore client in the process serving the route, 503 if there is none. In
  isolated mode that process is the **api** container, so a credentials or
  deploy change there makes the emergency stop inoperable while the engine
  places orders normally with a perfectly good client — which is the state the
  owner was in, with the ops page reporting it in the typeface it uses for
  footnotes.

  The precondition is fixed (`api/main.py` now mirrors `bootstrap.py` exactly,
  pinned by a test that compares the two guard sets on the **AST**, because the
  failure was one token stricter in one of two places). But the fix that
  matters is that the flip now **falls back to the engine over Redis**
  (`src/execution/safety_switch_bridge.py`), so the api container going blind
  can no longer take the stop with it. Four properties worth copying:
  - **A switch NAME, never a command**, mapped by a literal dispatch table a
    reviewer can read — and a test derives the accepted set from that table's
    own AST, because a name the queue accepts and the table does not handle is
    a silent no-op *reported as applied* on an emergency stop.
  - **BRPOP, not the SnapshotWriter's 15s cycle.** An emergency stop must not
    wait on a telemetry loop; blocking server-side costs nothing while idle.
  - **The stale window is TIGHTER than the diagnostic channel's** (30s vs 60s).
    An operator who gave up waiting has taken another action; applying their
    flip minutes later, from an engine that has just come back, is worse than
    refusing it.
  - **No feature flag.** A flag on the emergency stop is a switch that can turn
    the switch off. What it may do is bounded by the dispatch table instead,
    and the absence of a gate is asserted by walking bootstrap's enclosing
    conditions — a substring check would have been satisfied by the take
    consumer's flag sitting six lines above it.

  Corollary, and it is `initialised`'s whole problem: **"can I read it" and
  "can I throw it" are different questions and a page must grade the button on
  the second.** `KillSwitchState.throwable` is published apart from
  `availability`, because a switch that is un-readable here and perfectly
  throwable via the engine renders as broken under the old boolean.

- **Read and write must branch on the SAME predicate.** My first cut of
  `_kill_switch_state` decided its world from `availability()` while
  `kill_switch_set` decided from `is_initialised()`. Two accessors answering
  one question is how a page describes a world the button is not in — the
  defect this entire change was repairing, reintroduced one layer up in the fix
  for it, and caught only because an existing test patched the two separately.

- **A test that pins a COUNT catches what a review cannot.**
  `worker_manager._tick` called an uncached `collection_group` scan **once a
  minute** for months, in a repo with a Cost Discipline section, because
  nothing anywhere counted it: at one connected user it is 1,440 reads a day
  and looks free, and at the 1,000-member target it is **1.44 million**, thirty
  times the allowance, to notice a new subscriber. Reading that line tells you
  nothing; asserting `docs_returned == 1` over a thousand-member roster tells
  you everything. Every read on a per-user path now has a test that counts
  documents the way Firestore bills them.

  And the first test written against the new invalidation channel found a live
  defect in it before the code ever ran: an ABSENT Redis key was skipped rather
  than read as generation zero, so on a fresh or flushed Redis the first poll
  recorded nothing, the first bump moved 0→1, and the poll after it saw a first
  sighting and declined to invalidate. **The first kill-switch flip after a
  Redis restart would have been swallowed** — silently, because the defensive
  TTL converges minutes later and nothing looks broken.

- **An index over a safety gate needs a rebuild, and its failure direction is
  the design.** `auto_trade_disabled` is now mirrored onto one document so the
  gate costs one read instead of one per member. Two things make that
  admissible rather than clever: the per-user field stays the **record of
  record** (it carries the reason and the timestamp) with the mirror rebuilt
  from a real query on a slow timer, so a write that bypasses `disable_user`
  cannot hide forever; and **a mirror that was never written must not read as
  "nobody is disabled"** — an absent document, or one whose list field is
  missing, falls back to the per-user read it replaced. Reading the first as
  the second would silently un-disable every tripped user. Same rule for the
  key roster, where an empty answer means every signal fans out to zero users,
  which is the 2026-09-02 blackout signature exactly.

  Corollary on ordering: `disable_user` writes the durable field first and the
  index second; `enable_user` does the reverse. **Both orderings fail toward
  the user staying disabled**, which is the safe direction, and that is the
  reason they differ rather than an inconsistency.
