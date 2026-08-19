# Lumin / 360 Crypto Eye — Owner Brief

**This is the doctrine — the rules and the *why*. For *what exists and where it
lives*, read `ARCHITECTURE.md` first: it is the one-map view of all four repos and
takes ~10 minutes. Then this brief, then `ACTIVE_CONTEXT.md`.**

> **⚠️ PHASE: PRODUCTION (LIVE).** The Lumin app is live on the Google Play
> **production** track (release 282+ as of 2026-07-16, public in the launch region,
> real installs on real devices). Closed testing is over. Real users see signals and can run
> auto-trade on their own capital. **Money-path changes** (scoring, evaluator paths,
> exit/FSM, dispatch, paid-channel routing) now ship **dark-flag-first**, where
> **dark means invisible to users and fully live to the owner** — not switched off.
> Two flags, not one: the **measurement** ships **ON** and visible in ops from day
> one; the **user-visible effect** ships **OFF** and is **activated only after owner
> sign-off** on the measured result. This supersedes the testing-phase "ship live, no
> dark flags" cadence. Safety limits (§1.4, B12, B18) were always enforced and stay
> so. See `CLAUDE.md § Project Phase`.

---

# PART I — ROLES AND OPERATING CONTRACT

## 1.1 Roles

| Role | Person |
|---|---|
| **Owner** | mkmk749278 — final authority on business direction, priorities, constraints |
| **CTE (Chief Technical Engineer)** | Claude — full business partner and system owner across all repos and sessions |

CTE holds full technical ownership of codebase, architecture, live system, roadmap, and business-chain decisions. The owner provides business intent and final authority; the CTE converts it into production-grade execution. CTE is not a code assistant.

## 1.2 CTE Operating Mandate

**Before every code change:** "How does this make signals more profitable for paid subscribers?" If the answer is unmeasurable — defer or drop.

**Always:**
- Production-grade in every decision. No temporary solutions. No shortcuts. No hiding problems.
- Think at the institute level before every change — architecture, business impact, subscriber experience, long-term maintainability.
- Act immediately on bugs and system failures — do not wait to be asked.
- Update `ACTIVE_CONTEXT.md` every session end.
- Tell the owner when a direction is technically wrong, not just technically possible.
- Read `OWNER_BRIEF.md` and `ACTIVE_CONTEXT.md` at every session start before touching any code.

## 1.3 What Requires Owner Discussion First

- New evaluator paths or scoring models
- Changes to any Business Rule (B1–B18)
- Major architecture changes spanning subsystems
- Deprecating or removing existing functionality
- Any change to paid-channel routing
- Any change to signing service / KMS / connect-time validation / blast-radius caps
- Any change to Position FSM transitions (entry, SL/TP shape, pre-TP trigger, BE shift, trail tightening)
- Regime-per-exit parameter decisions (§3.2b — design in progress, data-first)

## 1.4 Hard Limits — Never Negotiable

- Never fabricate signal performance data, prices, or win rates
- Never deploy to production without syntax check + review
- Never silence a detected problem
- Never push to `main` directly or bypass the PR workflow
- Never log a Binance API secret at any level — not even TRACE/DEBUG
- Never write a plaintext Binance secret to disk, even momentarily
- Never surface a secret in an error trace, panic message, or debug dump
- Never accept a Binance API key with withdraw permission enabled — auto-reject, no permissive mode, no admin override
- Never disable or weaken the blast-radius caps (symbol allowlist, rate limit, position cap, kill switch)
- Never let a position sit OPEN without a stop (naked-position invariant)
- Never start patching engine code at a vendor-API symptom before checking the vendor's changelog

---

# PART II — BUSINESS

## 2.1 What We Are Building

The top-level crypto signals company in every aspect. Not a side project. Not a Telegram bot.

**Lumin** is the consumer brand (app, Play Store, marketing). **360 Crypto Eye** is the signal-engine brand (Telegram channel, technical identity). Together they form a complete product: automated intelligence → subscriber trust → recurring revenue.

**The chain:** profitable signals → subscriber trust → retention → revenue → growth → reinvestment into signal quality. Every engineering decision is evaluated against this chain.

## 2.2 The Product

**A+ and B tier (65+ confidence)** are delivered **free** to the **in-app Lumin Signals feed** (full levels) and mirrored to TELEGRAM_ACTIVE_CHANNEL_ID. Sub-65 → FILTERED → dropped silently. The in-app feed is the primary surface (B1) — a standing product decision, because the app is the product and the paywall is automation, not information. **Monetization is the auto-trade paywall (B16): Assist ₹1000/mo one-tap, Auto ₹2000/mo hands-off** — not the signal information itself.

> **Correction 2026-07-25 (owner): Telegram is NOT banned in India — it works.**
> This brief previously used "Telegram is banned in-region" as the *reason* for the
> in-app-first architecture (B1) and for retiring the Telegram payment path (B16).
> That premise was false. **The rules themselves are unchanged** — the owner
> reaffirmed the current architecture on 2026-07-25 — but they now stand as product
> decisions rather than as consequences of a ban. Telegram is a working, reachable
> mirror channel. Do not re-derive any product, routing, or payment choice from the
> old premise.

The free channel is fed only by storytelling mirrors (signal-result posts as social proof) and content-engine outputs. Never by sub-paid-tier engine signals.

**What counts as success:**
- High-conviction signals hitting TP at a profitable net-of-fees rate
- 1–10 paid signals/day — empty app = churned subscriber
- Honest SL outcomes posted with the same visual weight as TP wins
- Zero subscriber-visible drama (silent expiries, duplicates, broken alerts)
- Growing subscriber base trusting the system with real capital

## 2.3 Fee Reality — The Central Problem

At 10× leverage on Binance USDT-M futures, round-trip fees ≈ **0.7% of margin**. A signal closing at "neutral" raw price move is a **0.7% net loss** to the subscriber. This is not an edge case — it is the structural reason most signal channels lose money for subscribers despite a positive raw signal win-rate.

**Fee-aware design is non-negotiable (B11).** Every threshold, gate, scoring band, and exit parameter must account for this. A signal that "nearly worked" is a net loss.

**How we solve it (Session 34 — exit machinery removed from the default path):**
- TP1-full exit: close 100% at TP1 via a reduce-only LIMIT (maker fill, zero slippage), against a fixed SL. The Profit-Lab proved this beats the pre-TP+invalidation machinery by +19.14% on 494 live signals.
- Reduce-only LIMIT order on profit-taking: no slippage, maker fill (unchanged doctrine — the *profit* leg is always a resting LIMIT).
- SL geometry: sized so the reward/risk ratio after fees remains positive (B7). This is now the *primary* fee defence — the old pre-TP-bank / invalidation overlay is opt-in only (B17), because the data showed it gave back more than it saved.
- ⚠️ Even with TP1-full the book is still slightly net-negative (−6.65%) — the remaining gap is entry quality + fees, the next lever.

---

# PART III — THE SYSTEM

## 3.1 What 360 Crypto Eye Is

24/7 automated signal engine. Scans 75 Binance USDT-M futures pairs every 15 seconds, detects scalp setups via Smart Money Concepts (SMC) and order-flow logic, scores via a multi-component pipeline, delivers A+/B signals to the in-app Lumin feed (primary surface, B1) with a Telegram mirror, and executes server-side Binance trades on behalf of auto-trade subscribers.

**Repos:**
| Repo | Purpose |
|---|---|
| `github.com/mkmk749278/360-v2` | Engine (this repo) |
| `github.com/mkmk749278/lumin-app` | Android consumer app |
| `github.com/mkmk749278/360ce-ops` | Web ops dashboard (`ops.luminapp.org`) |
| `github.com/mkmk749278/lumin-legal` | Legal docs (GitHub Pages) |

## 3.2 Scalping Doctrine

1. **Direction-agnostic.** LONG and SHORT are equally valid products. Trend-aligned-only filtering forces directional bias — that is trend-following, not scalping.
2. **TP1-full is the default exit (Session 34, 2026-06-24). TP1 or SL — nothing in between.** Close 100% of the position at TP1 against a *fixed* SL; no pre-TP partial, no SL→BE ratchet, no invalidation kill. *Why this reversed the old "pre-TP is the primary exit" doctrine:* the live Profit-Lab on 494 signals (`ops.luminapp.org/profit`) showed the engine's real pre-TP + invalidation exits NET **−25.79%** while a plain TP1-full exit nets **−6.65%** on the *same* signals — a **+19.14%** edge. Every simulated simple exit beat the machinery; TP1-full beat it most. The exit logic, not the entries, was giving back the edge. Pre-TP banking and invalidation modes survive as **per-user opt-ins** (B17), but the engine default is now TP1-full.
3. **Capital preservation = the fixed SL, sized for positive R:R after fees.** Full SL hit ≈ 7.9% on margin at 10×; the defence against it is *entry quality + SL geometry* (B7), not a mid-trade exit overlay that the data showed bleeds the winners. Honest caveat: TP1-full is still slightly net-negative (−6.65%) — it stops most of the bleed but the residual gap is entry quality + fees, not the exit.
4. **Quantity matters.** Subscribers churn from silence. 1–10 paid signals/day is the target.
5. **Soft penalties over hard blocks.** Hard blocks discard signals the scoring tier could correctly classify. Reserve hard blocks for structural impossibility only.

### 3.2a Capital Preservation and Order-Type Doctrine

Pre-TP fires a **real partial close** via a REDUCE-ONLY LIMIT order placed at dispatch time. Binance holds it passively; when price reaches the threshold, the order fills at maker price — zero slippage. The residual gets SL ratcheted to entry. The banked partial is locked before the position can revert.

**Order-type doctrine (non-negotiable):**

| Purpose | Order type | Reason |
|---|---|---|
| Entry | MARKET | Get in; slippage acceptable at entry |
| Pre-TP / TP1 / TP2 | **REDUCE-ONLY LIMIT** | Rests on Binance book — maker fill, zero slippage, works if engine blips |
| SL / invalidation / expiry | MARKET (reduce-only / closePosition) | Protection needs guaranteed fill now |

Profit is only ever taken via resting LIMITs. MARKET is reserved for protection and thesis-broken exits.

### 3.2b Regime-Per-Exit Doctrine (in design — 2026-06-03)

**Current state:** pre-TP threshold, grab fraction, invalidation mode, SL geometry, and TP ladder are applied uniformly regardless of market regime at signal entry. This is structurally wrong — a trend-aligned signal in TRENDING_DOWN deserves a different exit profile than a counter-trend scalp in RANGING.

**Agreed direction (data research in progress before any implementation):**

| Bucket | Pre-TP | Grab fraction | Invalidation | TP ladder |
|---|---|---|---|---|
| Trend-aligned (LONG/TREND_UP or SHORT/TREND_DOWN) | High threshold or OFF | Small — let it run | Loose | Full ladder + potential trailing runner past TP2 |
| Counter-trend | Low threshold, bank fast | Large | Tight | TP1 only |
| RANGING | Mid threshold at boundary | Standard | Standard | TP at opposite boundary |
| VOLATILE | Low threshold, bank fast | Large | Tight | TP1 only |
| QUIET | ATR-scaled low threshold | Standard | Standard | TP1 — the original pre-TP doctrine case |

**Invariant:** the entry regime (`entry_regime`) is already stamped on every signal and passed to dispatch. Mid-trade regime flips never tighten an existing position — entry regime locks the structure. The only live-regime action permitted is an upgrade (ranging → trending breakout confirmation → release the cap).

**Implementation gate:** data-first. The truth report + invalidation audit must be sliced by `entry_regime` before any parameter values are decided. Research on how top channels handle regime-aware exits is in progress. Owner sign-off on the full matrix required before any FSM code changes.

## 3.3 Structure Detection Doctrine — "HTF Structure, LTF Entry"

**HTF (1H/4H) identifies structure. LTF (5m) refines entry timing only.**

A 5m candle never identifies structure — it identifies *when* to enter the structure confirmed at HTF. Any evaluator reading structural meaning from 5m candles is treating noise as signal.

Tape-driven paths (WHALE / LIQUIDATION_REVERSAL / FUNDING_EXTREME) are exempt — they read structure from realtime order flow, not candle structure.

Infrastructure: `src/level_book.py` (1d/4h/1h pivots + VP zones), `src/structure_state.py` (BULL_LEG/BEAR_LEG/RANGE per TF), `src/volume_profile.py` (POC + VAH/VAL), `_classify_htf_trend()` in `src/channels/scalp.py`.

## 3.4 Per-Path HTF Policy

| Path category | HTF treatment |
|---|---|
| Trend-aligned by regime gate (TPE / DIV_CONT / CLS / PDC) | None — already gated to TRENDING regimes |
| Tape-driven (WHALE / FUNDING / LIQ_REVERSAL) | None — direction from tape |
| Counter-trend (LSR / FAR) | Soft penalty when 1H AND 4H both oppose |
| Structure (SR_FLIP / QCB) | Soft penalty when 1H AND 4H both oppose |
| Breakout (VSB / BDS / ORB) | None — fires in any HTF context |

The question is never *"does the signal align with HTF?"* but *"is this a profitable scalp setup regardless of broader direction?"*

## 3.5 The 19 Signal Evaluators (17 live, 2 disabled)

*Corrected 2026-07-25: this table said "15" and was missing four paths that have
been generating for weeks. The count here now matches `_evaluate_*` in
`src/channels/scalp.py` and the `EVAL::*` rows in the truth report — both 19.*

| # | Setup Class | Family | Direction source |
|---|---|---|---|
| 1 | LIQUIDITY_SWEEP_REVERSAL | Reversal | Sweep object + EMA (evaluator `standard`) |
| 2 | WHALE_MOMENTUM | Order-flow | Tick imbalance |
| 3 | TREND_PULLBACK_EMA | Trend continuation | Regime / EMA stack |
| 4 | LIQUIDATION_REVERSAL | Reversal | Cascade sign |
| 5 | VOLUME_SURGE_BREAKOUT | Breakout | Price vs swing high |
| 6 | BREAKDOWN_SHORT | Breakout | Price vs swing low |
| 7 | OPENING_RANGE_BREAKOUT | Session breakout | Price vs range — **disabled** (`feature_disabled`) |
| 8 | SR_FLIP_RETEST | Structure | Breakout direction |
| 9 | FUNDING_EXTREME_SIGNAL | Order-flow | Funding sign (contrarian) |
| 10 | QUIET_COMPRESSION_BREAK | Quiet specialist | Price vs Bollinger band |
| 11 | DIVERGENCE_CONTINUATION | Trend continuation | Regime / EMA |
| 12 | CONTINUATION_LIQUIDITY_SWEEP | Trend continuation | EMA alignment — **disabled** (merged into LSR) |
| 13 | POST_DISPLACEMENT_CONTINUATION | Breakout continuation | EMA alignment |
| 14 | FAILED_AUCTION_RECLAIM | Structure reclaim | Failed-auction side |
| 15 | MA_CROSS_TREND_SHIFT | Discrete trend-shift | EMA50/200 4h or EMA21/50 1h crossover |
| 16 | MOVER_TREND_PULLBACK | Mover continuation | Mover run + pullback |
| 17 | MOVER_AVWAP_SCALP | Mover mean-revert | Anchored VWAP |
| 18 | MEAN_REVERT | Counter-trend fade | Stretch from 20-bar mean |
| 19 | RANGE_FADE | Counter-trend fade | Range edge vs mid |

Each evaluator lives in `src/channels/scalp.py` as `_evaluate_<name>` and owns its SL/TP geometry (B7).

## 3.6 Confidence Tiers and Routing

| Tier | Score | Routing |
|---|---|---|
| A+ | 80–100 | In-app Lumin feed (primary, B1) + Telegram mirror |
| B | 65–79 | In-app Lumin feed (primary, B1) + Telegram mirror |
| FILTERED | < 65 | Dropped silently |

*Corrected 2026-07-25: this table said "Paid channel", which contradicted B1/B16
— signals and full levels are **free**; the paywall is automation, not
information. **The app is the primary surface for users; Telegram is a mirror.**
Telegram's wider role is a separate owner session — do not expand it here.*

### 3.6a Scoring Doctrine — "Score a setup on the evidence that defines it"

The composite scorer's per-dimension scores (regime, volume, …) must reflect what makes *that* setup valid — not a one-size-fits-all default that punishes a setup for its own defining trait. A setup penalised on the wrong evidence never clears the 65 floor, so it generates but never emits, and looks "dead" when it is in fact mis-scored.

Recurring failure mode (Session 27–28, PRs #618–#621): an evaluator's entry/gate doctrine was corrected, but the matching change at the **scoring layer** was missed, so the scorer kept docking the setup for the very pattern that defines it. Three concrete instances, all fixed by aligning the score with the setup's thesis:

- **Volume on surge/pullback setups** (VSB/BDS, TREND_PULLBACK_EMA): the *entry* candle is low-volume **by design** (dead-cat bounce / quiet pullback). Don't score volume off the entry candle — score it off the validated breakout candle (`breakout_volume_ratio`), or floor it at neutral. (#618, #619)
- **Regime on transition/continuation setups** (MA_CROSS_TREND_SHIFT, VSB/BDS): a setup that fires *at* a regime turn reads RANGING/QUIET on the entry-TF label at entry. Floor it at neutral (14) instead of the non-affinity 8 — don't penalise it for firing at the turn. (#618, #619)
- **Regime must be judged on the trend's timeframe, not the entry's** (TREND_PULLBACK_EMA): trend is HTF-defined, entry is LTF-timed (§3.3). When an evaluator confirms the trend on the HTF (e.g. 1H EMA21/50), the scorer credits full regime affinity via the `htf_trend_aligned` flag rather than scoring the noisy 5m pullback label. (#621)

**Corollary — filters beat parameter-tuning** (#620, MA-cross research): for crossover/trend setups, a higher-timeframe trend-alignment *filter* improves real-money results far more than tuning the EMA periods. Crypto ranges ~60% of the time, so an unfiltered cross whipsaws regardless of which periods you pick. Don't chase "the best EMA pair"; gate the cross on HTF agreement.

## 3.7 Architecture — Signal Flow

```
Binance WebSocket (300 streams)
        ↓
HistoricalDataStore + OrderFlowStore
(candle OHLC 6 TFs, OI, CVD, funding, liquidations)
        ↓
Scanner — every 15s × 75 pairs
        ↓
ScalpChannel.evaluate() — 19 evaluators per pair (17 live)
        ↓
Gate chain (SMC, MTF, regime, spread, volume)
        ↓
Chartist-eye stack (LevelBook + VolumeProfile + StructureTracker)
        ↓
SignalScoringEngine — confidence 0–100
        ↓
_enqueue_signal (universal SL min 0.80%)
        ↓
SignalRouter → in-app Lumin feed (primary) + Telegram mirror
        ↓
┌──────────────────────────────────────────────────────────────┐
│  TradeMonitor (5s poll backstop)                             │
│  signal_dispatch → per-user Position FSM                     │
│  PositionWorker (User Data Stream, sub-100ms FSM transitions)│
│  Reconciler (60s diff, force-close stale positions)          │
│  Mark price feed + Pre-TP dispatcher (tick-driven)           │
└──────────────────────────────────────────────────────────────┘
        ↓
Signing Service (Unix socket, separate container)
        ↓
Binance REST API
```

## 3.8 API/Engine Process Isolation (live 2026-06-02)

**Two-container split** controlled by `API_PROCESS_ISOLATED` in `.env`:

| Container | Responsibility |
|---|---|
| `engine` | Scanner, FSM workers, TradeMonitor, SnapshotWriter (writes state to Redis every cycle). Does NOT serve HTTP. |
| `api` | HTTP server on its own event loop. `RedisEngineFacade` reads Redis snapshots. Writes user settings to shared SQLite. Mode-flip commands queue to Redis. |
| `redis` | Bridge between containers. Engine writes `snapshot:*` keys; API reads them. |
| `signing_service` | Separate process + Unix socket. Only place plaintext Binance API secret exists. |

**Per-user settings flow:** app → API writes SQLite → engine reads SQLite at dispatch (fresh SELECT, WAL mode, shared volume). No caching in workers. Change in app takes effect on next signal dispatch.

## 3.9 Execution Model

**Server-side, non-custodial of funds, custodial of trade-authorisation keys.**

**Execution profiles (per-user, selectable from app). Engine default = D (Session 34):**

| Profile | `grab_fraction` | Behaviour |
|---|---|---|
| **D — TP1-full (DEFAULT)** | **0** + `invalidation_mode=loose` + `TP1_CLOSE_FRACTION=1.0` | **Close 100% at TP1 against a fixed SL. No pre-TP, no SL→BE, no invalidation. The default exit.** |
| A — close all at threshold | 1.0 | Full-qty pre-TP LIMIT at entry. No TP bracket. (Opt-in.) |
| B — bank partial, ride residual | 0.30–0.99 | Partial pre-TP LIMIT + TP ladder. SL→BE on pre-TP fill. (Opt-in.) |
| C — ride native bracket | 0 / `invalidation_mode=loose` + a ladder split | Multi-leg TP ladder. Engine invalidation does not interfere. (Opt-in — restore a ladder via `TP{1,2}_CLOSE_FRACTION`.) |

**Per-user dials (all consumed at dispatch, fresh read per signal):**
- `threshold_pct` — pre-TP trigger (0.10–1.00% raw from entry)
- `grab_fraction` — fraction closed at pre-TP (30%–100%)
- `invalidation_mode` — loose / standard / tight (engine default: **loose**, `INVALIDATION_MODE_DEFAULT`)
- `notional_usd` — position size

**Blast-radius caps (see B18 — non-negotiable):** symbol allowlist, per-user rate limit, per-user position cap, global kill switch, global + per-user circuit breakers.

**Naked-position invariant:** a position never sits OPEN without a stop. SL placement failure → FSM force-closes at market. Reconciler force-closes anything open past `RECONCILER_MAX_POSITION_AGE_SEC` (2h).

## 3.10 Chartist-Eye World Model

Shared scoring infrastructure — purely a scoring layer, never invents a setup.

| Component | Module | Role |
|---|---|---|
| LevelBook | `src/level_book.py` | Multi-TF S/R (1d/4h/1h pivots + VP zones). Top 60 per symbol. 1h refresh TTL. |
| StructureTracker | `src/structure_state.py` | BULL_LEG / BEAR_LEG / RANGE per (symbol, TF). 30min TTL. |
| VolumeProfile | `src/volume_profile.py` | POC + VAH/VAL. POC/VAH/VAL feed LevelBook for confluence scoring. |
| Pattern catalog | `src/chart_patterns.py` | Flags, DT/DB, triangles, H&S, candlestick zoo. ±3 pts bonus. |

Soft-penalty bonus magnitudes bounded: confluence ≤9 pts, structure-align 3 pts. A sub-50 candidate cannot reach paid (65) by scoring bonuses alone.

## 3.11 The Autonomous Portfolio / Strategy Lab (Layers A–G) — LIVE

*Added 2026-07-25. Built across Sessions 53–77 and running in production, but this
brief had no description of it at all — the single largest documentation gap in the
system. Design-of-record: `docs/PLAN_AUTONOMOUS_PORTFOLIO.md`,
`docs/PLAN_AUTONOMOUS_EMISSION.md`, `docs/PLAN_AUTONOMOUS_EMISSION_CONTROLLER.md`,
`docs/AUTONOMOUS_SYSTEM_AUDIT_AND_REMEDIATION.md` (W1–W7).*

**The thesis.** A confidence score alone cannot decide emission, because edge lives in
`session × regime × strategy` cells, not in a global number. The portfolio measures
every strategy in every market context on real data, and lets that measurement — not
opinion, and not a human checking daily — decide what emits.

| Layer | Module | Role | State |
|---|---|---|---|
| **A — Market context** | `src/market_context.py` | Global BTC-anchored vector (session / phase / volatility / funding / rotation) → `context_key`, published each 5-min cycle | LIVE |
| **B — Strategy registry** | `src/strategy_portfolio.py` | Context-affinity tags per SetupClass + shadow units; `is_context_aligned()` | LIVE |
| **C — Edge matrix** | `src/strategy_edge.py` | Every strategy × context measured on real data, provenance-split (emitted / suppressed / shadow), Wilson lower-bounded. **Everything routes on this.** | LIVE |
| **C→consumer — Emission policy** | `src/context_emission_policy.py` | Per-(strategy × context) confidence floor from the matrix: STRONG → relax toward the quality anchor, POSITIVE → half-relax, **NEGATIVE → hard-suppress**, cold/thin → global floor unchanged | **LIVE** (S69, owner-directed) |
| **D — Allocator** | `src/strategy_allocator.py` | What it *would* activate now and at what weight, inside the safety envelope (≤6 concurrent, ≤0.35 each) | **Recommendation-only — consumed by nothing.** Phase-4 master-arm never armed |
| **G — Emission controller** | `src/emission_controller.py` + `_store.py` | Closed loop: reads gate verdicts + matrix and moves the policy's per-strategy knobs itself, inside a bounded envelope, **no human in the loop** | **LIVE** (S72b) |

**What feeds the matrix**

- **Suppression audit / shadow ledger** (`src/suppression_audit.py`) — every
  post-scoring gate-suppressed candidate is stamped with full geometry and
  forward-measured on real candles (WOULD_WIN / WOULD_LOSE / WOULD_EXPIRE), giving a
  per-gate **KEEP / TUNE / DROP** verdict. This is how a gate earns its place.
- **Shadow strategy units** (`src/shadow_strategies.py`) — 4 units with no path to the
  signal queue, measured as if they were live.
- **Counterfactual measurement arms** — `@FIXED`/`@ATR` (stop geometry),
  `@TUNED` (tuned recipes), `@DSV2`/`@GOV` (dispatch rescues),
  `@SARBASE`/`@SAREXIT` (exit method). **These are evidence, never strategies** — they
  are stamped from the same candidates as the real rows and must be excluded from any
  per-strategy rollup or the candidate is double-counted.

**Cost-aware R (W1/W2, Session 76) — the correction that mattered most.** Every R —
counterfactual, shadow *and* realized — used to be measured **gross**: wins at full
R-to-TP1, losses at exactly −1.0R, no fees/funding/slippage, while the fields were
*labelled* net. The harvested gross edge (~+0.08R) was smaller than the per-trade cost
drag never subtracted (~0.15–0.25R), so the dashboards read positive while the book was
net-negative, and the emission policy steered on a cost-free fantasy. `src/trade_costs.py`
now nets both seams; `reconcile_matrix()` + the `edge_reconciliation` liveness probe
validate the cost constants in flight.

**Where to read it:** ops **Strategy Lab** (`/strategy-lab`) and the truth report's
Suppression Quality Audit / Edge Matrix / shadow-arm sections.

**Standing cautions — read before acting on any number here**

1. **Counterfactuals are optimistic.** They free-run to TP1; live trades get killed
   earlier. Measured at ~**0.38R** on MOVER_TREND_PULLBACK. Discount accordingly — the
   `edge_reconciliation` probe exists to keep that number honest.
2. **A fresh window is required after any scoring/cost change.** Per-cell windows roll;
   verdicts stay stale until they refill. Do not retire or promote a strategy on a
   window that predates the change.
3. **Zero emissions is not automatically a fault.** A path fully gated because its
   counterfactuals measure negative is correctly gated (RANGE_FADE: −0.98R, 3% win).
   A path fully gated with *positive* counterfactuals is costing money. The emission
   liveness probes distinguish these (`feature_liveness.gated_path_verdict`).
4. **The allocator is still recommendation-only.** Nothing consumes its weights;
   arming it is an owner decision that has never been taken.

---

# PART IV — BUSINESS RULES

| # | Rule |
|---|---|
| B1 | **Signals are delivered in-app, free, in full.** The Lumin **Signals** feed (direction, setup, confidence, **entry/SL/TP**, analysis — all free) is the primary delivery channel — a product decision: the app is the product surface, and the paywall is **automation, not information** (B16). Free users see and can manually act on every signal; paid tiers automate placement. The Telegram channel (TELEGRAM_ACTIVE_CHANNEL_ID) remains a single optional mirror — never more than one channel, no duplicate routing. *(2026-07-25: the old justification "because Telegram is banned in-region" was factually wrong — Telegram works in India. The rule is unchanged and owner-reaffirmed; only the false premise is removed.)* |
| B2 | Zero manual effort at runtime — everything self-manages |
| B3 | SL hits posted honestly — same visual weight as TP wins |
| B4 | No duplicate signals on same symbol within cooldown window |
| B5 | *(Retired — WATCHLIST tier removed. Free channel fed by storytelling mirrors only.)* |
| B6 | System must survive Binance API degradation gracefully |
| B7 | Every evaluator owns its SL/TP calculation — no shared universal formulas |
| B8 | All config values must be env-var overridable |
| B9 | **No silent disappearances.** An expired signal must be surfaced — primarily in the in-app Lumin feed (B1), mirrored to Telegram. The rule is the honesty, not the channel. |
| B10 | Discuss and agree before building major architecture changes |
| B11 | **Net-of-fees economics.** At 10× leverage, round-trip fee ≈ 0.7% of margin. Every threshold, gate, and scoring band must be fee-aware. A neutral close is a net loss to the subscriber. |
| B12 | **Auto-trade safety.** No live execution without: daily-loss kill switch, concurrent-position cap, per-symbol exposure cap, leverage cap (≤30×), restart reconciliation, structured order audit log. Paper-book reset refuses while open positions exist — flattening is a separate explicit action. |
| B13 | **Identity.** Firebase Phone Auth (primary, universal). Google Sign-In on Android. Telegram OTP as opt-in upgrade for DM features. No email, no password. |
| B14 | Build constraint. All build/deploy paths work via VPS + GitHub Actions. No local Android Studio required. |
| B15 | **Brand.** Lumin = consumer app brand. 360 Crypto Eye = engine + signal-source brand. Telegram channel never renames. App About page always credits 360 Crypto Eye. |
| B16 | **Revenue — Google Play Billing, two-tier auto-trade model.** Signals + **entry/SL/TP levels + analysis are FREE.** The paywall is on **trade automation**, sold as two monthly Play subscriptions: **Assist (`lumin_assist_monthly`, ₹1000/mo)** — one-tap "take trade" (the app places the order client-side on the user's own Binance keys); **Auto (`lumin_auto_monthly`, ₹2000/mo)** — hands-off server-side auto-execution. Tier hierarchy `free < assist < auto`. The Telegram-bot payment path is **retired** — Google Play Billing is the payment rail for this app. *(2026-07-25: retirement previously attributed to "Telegram banned in-region", which was false. The retirement stands as an owner decision; only the wrong reason is removed — no new rationale is asserted here.)* Because the paid feature is *automation software functionality* (executed on the user's own keys — Lumin never custodies funds), it is presented as an app feature, NOT "investment advice"; the **Financial features declaration** applies and the framing is load-bearing. **Entitlement is server-side and is the source of truth:** the app sends the Play `purchaseToken` → engine verifies against the Google Play Developer API (`purchases.subscriptionsv2`), acknowledges, and sets `UserStore.tier` (`assist`/`auto`) + `paid_until`; **RTDN** keeps renewals/cancellations/holds/expiries live. **The money-path gate lives in `signal_dispatch`: hands-off execution runs only for `auto` users** (`AUTO_TRADE_TIER_GATE_ENABLED`, default ON, fail-closed). Assist is gated client-side (one-tap UI). SA key via env only (never logged/committed). ⚠️ Charging for automated crypto execution carries Play financial-services scrutiny + possible Indian regulatory exposure — owner to keep legal sanity-check current. |
| B17 | **Per-user exit controls.** *Session-34 default flip: the engine default is now TP1-full + fixed SL — pre-TP and invalidation are OFF by default and survive only as per-user opt-ins.* Pre-TP grab fraction: 0% (engine default — disabled) or 30%–100% if a user opts in. Pre-TP threshold: 0.10–1.00% raw. Invalidation mode: loose (engine default — TP/SL only, no thesis kill) / standard / tight. TP-ladder split env-overridable via `TP{1,2,3}_CLOSE_FRACTION` (default 1.0/0.0/0.0 = TP1-full). All stored in `user_pretp_settings` + `user_invalidation_settings`; NULL = engine default (now no-pre-TP / loose). `grab_fraction=1.0` = full close at the pre-TP threshold; `grab_fraction=0` = no pre-TP (default). Regime-per-exit extension in design (§3.2b). |
| B18 | **Server-side execution custody.** Non-custodial of funds; custodial of trade-authorisation keys only. Connect-time validation: withdraw permission disabled (auto-reject if enabled — no permissive mode), Futures enabled, IP whitelist set to engine VPS IP. Plaintext API secret materialises only in signing service process memory for one request — never logged, never written to disk. Master key in Cloud KMS HSM; engine has Decrypt IAM only. Blast-radius caps (non-negotiable): symbol allowlist (auto-tracks PairManager universe), per-user rate limit (10 orders/min, 50/hr), per-user position cap ($500 default), global kill switch (operated from the ops control plane — owner-gated, audited, PRG-confirmed), global circuit breaker (>10 rejections/60s → auto-disable), per-user circuit breaker (>3 rejections/5min → auto-disable user). Any change to signing service / KMS / connect-time validation / blast-radius caps / circuit-breaker thresholds requires owner sign-off. |

---

# PART V — INFRASTRUCTURE

| Component | Detail |
|---|---|
| VPS | Ubuntu, Docker Compose, 24/7 runtime |
| Stack | Python 3.11+, asyncio, aiohttp, Redis, Binance WS/REST |
| Containers | `engine`, `api` (isolated mode), `redis`, `signing_service` |
| Deploy | `git push` to `main` → GitHub Actions → `bash deploy.sh` → VPS ~45s. Doc-only changes (`OWNER_BRIEF.md`, `ACTIVE_CONTEXT.md`, `CLAUDE.md`) are `paths-ignore`'d and do not trigger redeploy. |
| Monitor | GitHub Actions "VPS Runtime Audit / Truth Report" → `monitor-logs` branch |
| 24/7 Agent | Autonomous monitoring agent (in design — §5.1). Watches engine health, detects anomalies, files GitHub Issues for CTE review. |
| Signal delivery | **In-app Lumin Signals feed (primary, B1)**; Telegram channel is a single optional mirror. Free Telegram channel carries storytelling mirrors only — never engine signals. |
| Lumin app | **Play Store PRODUCTION track — LIVE** (release 282+ as of 2026-07-16, public in launch region) — package `org.luminapp.lumin`. AAB built by CI on every `main` push. API via Cloudflare (`api.luminapp.org`, SSL, Mumbai edge). |
| Ops dashboard | `github.com/mkmk749278/360ce-ops` → `ops.luminapp.org`. Live. **Engine control plane since 2026-06-20** — kill switch, auto-mode flips, manual close — all owner-gated, audited and PRG-confirmed, plus the diagnostic surfaces (API, data volume, monitor-logs, diag scripts). Two tiers: **owner** (password + TOTP, everything) and a **read-only guest** (2026-08-06) holding a short-lived owner-minted code, revoked per request. The guest tier sees the measurement and diagnostic pages and no control plane, no subscriber data, no raw volume — and since 2026-08-19 may issue exactly **one** write: running a named entry from the engine's diagnostic catalog, which by construction cannot reach an order, a key, the kill switch, auto mode, the FSM or per-user settings. Full argument: `docs/READ_ONLY_ACCESS.md` in that repo. |
| Legal | `github.com/mkmk749278/lumin-legal` → GitHub Pages. Source-of-truth for Play Console + in-app legal links. |

## 5.1 24/7 Autonomous Monitoring Agent (**LIVE** — built and running)

*Corrected 2026-07-25: this section said "in design" long after the agent shipped. It runs as its own container in `360ce-ops` (`app/agent/`, `python -m app.agent.runner`, 60s poll cycle) with a Redis-backed dedup/escalation FSM, and it files the `auto-detected` issues this brief tells you to read at session start (e.g. #781).*

An always-on agent that autonomously monitors the live system and files findings for CTE review:

**Checks:**
- Container health (all containers running? signing service healthy?)
- Redis snapshot key freshness (`snapshot:*` keys within TTL)
- Signal fire rate (last 24h count within expected range — silence or flood both anomalies)
- Position FSM state distribution (too many OPEN positions = potential stuck-position bug)
- Engine API health endpoint
- Error log scanning (crash patterns, repeated Binance errors, FSM transitions)
- Deploy health (last successful deploy, last CI run)

**On anomaly:** creates a GitHub Issue tagged `auto-detected` + `severity:low/medium/high` with structured findings. High-severity pages the owner immediately via **FCM push** (Telegram notifier retained in code as a parallel alert path — alerting is read-only, so both are fine; *control* stays ops-only for the audit trail).

**CTE session protocol:** at every session start, check open `auto-detected` GitHub Issues before reading ACTIVE_CONTEXT.

---

# PART VI — BEFORE EVERY PR

Ask: **"How does this change make signals more profitable for paid subscribers?"**

If unmeasurable — defer. If measurable (win rate, signal volume, R:R, fewer subscriber-visible failures, lower fee erosion) — investigate, implement, test, ship.

Mechanics: `CLAUDE.md § Change-management Protocol`.
