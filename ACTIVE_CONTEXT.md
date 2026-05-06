# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## Current Phase

**App-era doctrine reset is in flight.** Owner direction (2026-05-06): "now we fully concentrate on app… too many signals are also lost trust on us; Pre-TP is our New strategy in industry so arrange this carefully with this we get more win rate; analyse the invalidation system, in my view it's actually protecting Signals with minimal risk… analyse all things finalise the plan."

The reset reframes "more gates → fewer signals" (correct for Telegram-only era) as wrong for app-era because empty app = dead app, and Pre-TP grab + invalidation audit are now the safety net that justifies looser gates upstream. Three PRs shipped today execute the first phase of that reset:

1. **PR #308 — WATCHLIST tier removed entirely.** Engine no longer routes sub-paid-tier signals anywhere. Free channel is fed only by close-storytelling mirrors + content-engine. Sub-65 → FILTERED, dropped silently. B5 retired.
2. **PR #309 — Wrong-regime blocks dropped from WHALE/VSB/BDS.** §3.4 already said these paths shouldn't be regime-gated; the code disagreed. Truth report shows ~45% of cycles are QUIET — recovers a meaningful slice for these three paths. Thesis gates still enforce structural validity in any regime.
3. **PR #310 — QCB `volume_div` modulator tightened 0.60 → 0.20.** Compression IS volume divergence; at 0.60 the modulator was a no-op in QUIET (1.08× base after the 1.8× regime mult). 0.20 brings effective QUIET weight to ~0.36× base.

**Hard structural gates and scoring tiers are unchanged.** The reset removes redundant or doctrinally-backward gates, not the quality bar at routing.

**Still pending in the master plan:** PR-4 (top-emitter softening — SR_FLIP / FAR / LSR), PR-5 (TPE softening), PR-6 (scanner gates: cross_asset hard→soft, MTF hard→soft), PR-7 (DIV_CONT / CLS / PDC / FUNDING). All deferred until PRs #308–#310 land in production and one truth-report cycle confirms direction.

---

## What's Currently Working

### Engine
- **Engine** healthy, scanning 75 pairs continuously, deploying via GitHub Actions
- **Monitor** runtime truth report on `monitor-logs` branch — regime distribution, gate metrics, confidence component breakdown, soft-penalty per-type breakdown, scoring-engine-dimension breakdown, pre-TP fire stats, free-channel post attribution, invalidation quality audit
- **Risk-component scoring** calibrated for scalp R-multiples (max credit at 2.0R)
- **Regime classifier** BB-width VOLATILE threshold at 8.0% (env-overridable)
- **HTF mismatch policy** soft penalty (not hard block) on SR_FLIP / QCB / FAR
- **WHALE / VSB / BDS regime gates removed** (PR #309) — these paths now fire in any regime when thesis gates pass; matches §3.4 doctrine
- **QCB `volume_div` modulator tightened** to 0.20 (PR #310) — effective QUIET weight ~0.36× base
- **WATCHLIST tier removed** (PR #308) — sub-65 → FILTERED, dropped silently; free channel fed only by storytelling mirrors + content-engine
- **QUIET-block doctrine** uniform 65 paid-tier floor — no scrap-routing exempts
- **Universal 0.80% SL floor** plus per-setup caps active
- **Invalidation quality audit** classifying every kill as PROTECTIVE / PREMATURE / NEUTRAL post-30-min
- **Counter-trend Regime-neutral baseline** (LSR / FAR) — `_REGIME_NEUTRAL_SETUPS` frozenset gives 14.0 baseline in non-affinity regimes (avoids HTF-soft-penalty + Regime-score double penalty)
- **Kill Zone disabled on all 8 SCALP-family channels** (`360_SCALP` + 7 auxiliaries) — PR #303. Reversible per channel via `_CHANNEL_GATE_PROFILE` in `src/scanner/__init__.py:435-444`
- **Pre-TP grab Phase A** live in production (`PRE_TP_ENABLED=true`). Threshold + trigger price now stamped at dispatch (B11) — Telegram post shows the actual trigger price instead of the static floor; auto-trade fires deterministically against the locked target rather than a moving ATR-recompute. PR #301
- **Auto-trade Phase A1+A2+A3 complete:** PaperOrderManager (15 tests), RiskManager 6 gates (23 tests), PositionReconciler (21 tests). Live `OrderManager` is real CCXT-backed (not stubbed). All env-overridable. `/automode` Telegram command for runtime mode flips without redeploy
- **Auto-trade non-TP close + DCA execution** (PR #302): every SL_HIT / INVALIDATED / EXPIRED / CANCELLED path now closes the broker in lockstep with engine state via `order_manager.close_full(reason=…)`. DCA Entry-2 reaches the broker via `order_manager.add_dca_entry(signal)` — additional qty = `existing × (weight_2/weight_1)` so weighted-avg-entry at the broker matches engine's avg_entry. Risk-gate-checked at DCA time
- **`_signal_history` persistence** (PR #299) — `data/signal_history.json`, atomic flush on terminal-state archive, capped at 500 entries; survives engine restarts. Plus first-boot **backfill** from `signal_performance.json` + `invalidation_records.json` (PR #304) and **self-healing reconciliation** (PR #305) that runs every boot to repair INVALIDATED status against the audit log
- **Macro watchdog Phase 1+2a+2b+5:** HIGH/CRITICAL events to free channel, BTC big-move alerts, BTC/ETH 1h regime-shift alert, paid signal-close storytelling mirror

### Subsystems present in code
- **DynamicTierManager** (`src/tier_manager.py` + `DYNAMIC_TIER_*` env vars) — dynamic pair-tier promotion based on liquidity / volume
- **ContentScheduler** (`src/scheduler.py`) — daily briefings, weekly scoreboard, performance reports to free channel
- **TradeObserver** — captures full trade lifecycle for AI-digest content
- **FreeWatchService + RadarAlert** — watch creation via `_handle_radar_candidate`; resolved on paid signal

### API + Lumin app
- **VPS API live** at `https://api.luminapp.org` — nginx reverse-proxy, Let's Encrypt cert, rate-limited 60 r/min
- **API endpoints (11 total):** `/api/health`, `/api/auth/anonymous`, `/api/auth/refresh`, `/api/pulse`, `/api/signals` (with optional `?status=&setup_class=`), `/api/signals/{id}`, `/api/positions`, `/api/activity` (with optional `?setup_class=`), `/api/auto-mode` GET/POST, `/api/agents` (per-evaluator stats with telemetry counters + 24h lifecycle counters: closed_today / tp_hits / sl_hits / invalidated / last_signal_age_minutes). `SignalDetail` carries `pre_tp_threshold_pct` + `pre_tp_trigger_price` for the app to display
- **Anonymous-JWT auth** on every protected endpoint; static-bearer escape hatch for owner debug behind `API_ALLOW_STATIC_TOKEN`. Pure-stdlib HS256 (no PyJWT dep)
- **Lumin v0.0.9 shipped:** Pulse / Signals / Trade pages on real engine data; per-agent drill-down (bottom sheet with stats card + 10 most-recent signals filtered by `setupClass`); Signals tab status sub-filters (TP / SL / Invalidated / Expired) when "Closed" is active; new `lib/shared/format.dart` pure-Dart price/PnL/pct/age helpers (used in Signals page; Pulse + Trade retrofit deferred to v0.0.10)
- **Lumin app file pipeline** — installer scripts (`tools/lumin-v00X.sh`) live in this repo; owner runs them from Termux on phone via `curl ...lumin-vXXX.sh | bash` → push → GitHub Actions builds signed APK

---

## Recent PRs

### Day 1 (data-integrity layer + engine hygiene)
| PR | Title | Status |
|---|---|---|
| #298 | Lumin v0.0.8 cosmetic + UX honesty fixes + ACTIVE_CONTEXT refresh | ✅ merged |
| #299 | Persist signal history + per-evaluator filter + agent lifecycle stats | ✅ merged |
| #300 | Lumin v0.0.9 installer — per-agent drill-down + status sub-filters | ✅ merged |
| #301 | Pre-TP stamp resolved threshold + trigger price at dispatch (B11) | ✅ merged |
| #302 | Auto-close broker on non-TP exits + push DCA Entry-2 to broker | ✅ merged |
| #303 | Disable Kill Zone gate on all SCALP-family channels | ✅ merged |
| #304 | Backfill `_signal_history` from PerformanceTracker + InvalidationAudit | ✅ merged |
| #305 | Correct INVALIDATED status everywhere it's persisted | ✅ merged |
| #306 | End-of-session doc refresh (2026-05-05) | ✅ merged |

### Day 2 (app-era doctrine reset)
| PR | Title | Status |
|---|---|---|
| #307 | Close broker + compute P&L + archive on signal expiry | ✅ merged |
| #308 | Remove WATCHLIST tier entirely (engine + tests + telegram_bot) | 🟡 open |
| #309 | Drop wrong-regime blocks from WHALE/VSB/BDS (per §3.4) | 🟡 open |
| #310 | Tighten QCB volume_div modulator 0.60 → 0.20 | 🟡 open |

End-of-session test count: **3792 passed**, 0 failures, 0 regressions.

---

## Open Queue

### Master plan — remaining PRs (deferred until #308–#310 land + 1 truth-report cycle)
- **PR-4: Top-emitter softening (SR_FLIP / FAR / LSR).** Convert remaining hard rejection paths to scoring-tier soft penalties where doctrine permits. SR_FLIP especially — currently top emitter but bulk filtered at sub-paid threshold; with WATCHLIST removed those are now silent drops, so the path either earns paid tier or contributes nothing.
- **PR-5: TPE softening.** Truth report shows ~80% of TPE attempts blocked by `regime_blocked` (1.3M of 1.6M). TPE is regime-aligned by definition (trend-pullback) so the gate is structurally compatible — but the strictness needs an audit against the SOLUSDT-style "beautifully oscillating EMA pullback" cases the owner flagged.
- **PR-6: Scanner gates conversion.** `cross_asset` hard→soft and MTF hard→soft, where the structural-impossibility condition isn't met. Both are currently hard-blocking signals the scoring tier could correctly classify.
- **PR-7: Remaining evaluators (DIV_CONT / CLS / PDC / FUNDING).** Per-path audit applying the same THESIS-vs-FILTER classification used in PRs #309/#310.

### Held — investigation paused
- **SR_FLIP_RETEST 0% win rate, paid-volume drought.** Backfilled history confirms: most closes are small-pct invalidations or breakevens, **zero TP hits** visible in the recent terminal set. SR_FLIP was previously the dominant emitter but mostly WATCHLIST-tier; with WATCHLIST removed (PR #308) those are now silent drops. PR-4 is the next bite.
- **OI-flip soft-penalty doctrine audit.** With KZ uniformly disabled, OI flip is the dominant soft-penalty bottleneck — DIV_CONT 100% / FAR 91% / LSR 100% / SR_FLIP 100% of penalty from OI. Same KZ-style question: 24/7-crypto-doctrine gate or inherited noise?

### Pending data
- **TP1 ATR cap re-derivation** (1.8R / 2.5R / uncapped on SR_FLIP / FUNDING / DIV_CONT / CLS) — wait for Phase 1 invalidation audit data on TP1 hit rates per setup × ATR-bucket
- **VSB / BDS generated-but-not-emitted** — VSB candidates land 19 below paid B-tier even un-penalised; BDS structurally silent (regime_blocked dominant). Diagnosed; no scoring fix would help
- **FAR `STRONG_TREND` regime block** — empirical conjecture, not structural impossibility. Could be soft penalty per doctrine; needs win-rate data
- **LSR hard 1H MTF reject in TRENDING/VOLATILE** — narrow filter, barely fires per recent telemetry. Could be soft per doctrine

### Pending owner decision
- **OPENING_RANGE_BREAKOUT** — currently `feature_disabled` (`scalp.py:2337`). Rebuild with proper session-anchored range logic, or delete. Not a CTE call
- **v0.1.0 settings-persistence architecture** — five decisions awaiting owner sign-off (Telegram-bot auth, SQLite storage, env-ceiling validator, per-agent toggle endpoint, scope). Major-architecture per OWNER_BRIEF §1.3

### Pending small follow-ups
- **Lumin v0.0.10 polish** — retrofit `format.dart` helpers (`formatPrice` / `formatPnl` / `formatPct` / `formatAge`) into Pulse + Trade pages. Small installer
- **Reconciler default flip** — `RECONCILER_AUTO_CLOSE_ORPHANS=true` so the periodic 5-min sweep auto-closes any broker position the engine forgot to. Belt-and-braces for any future code path that misses a `close_full` call. ~5-line PR
- **Historical perf JSON cleanup (optional)** — pre-merge invalidations stay labelled `"CLOSED"` in `data/signal_performance.json` itself (PR #305 fixes the user-visible signal_history but not the perf JSON). One-shot migration if owner wants the truth-report win-rate stats also corrected for the historical set

### Free-channel content rollout
**Phase 1 — Macro events to free channel** ✅ shipped (HIGH/CRITICAL only)
**Phase 2a — BTC big-move alert** ✅ shipped (≥3% / ≥5%, 1h cooldown)
**Phase 2b — BTC/ETH regime-shift alert** ✅ shipped (1h EMA21 cross, 4h cooldown)
**Phase 2 (still open) — additional event triggers** — BTC dominance ±2% (needs extra data source)
**Phase 3 — Charts attached to scheduled posts** — `src/chart_renderer.py` using mplfinance; attached to morning brief / EOD wrap / event-driven alerts
**Phase 4 — Coin spotlights** — top mover / breakout watch daily posts with charts
**Phase 5 — Signal-close storytelling** ✅ shipped (TP3 / SL mirror to free channel with `📣 Paid Signal Result` header)

### Pre-TP grab — Phase A ✅ shipped + ENABLED in production
- `TradeMonitor._check_pre_tp_grab` fires on ATR-adaptive threshold within 30 min, non-trending regime, non-breakout setup
- **Threshold + trigger price stamped at dispatch** (PR #301) — `pre_tp_threshold_pct` + `pre_tp_trigger_price` on `Signal` dataclass; `stamp_pre_tp` invoked from `Scanner._enqueue_signal` after universal SL-floor adjustment; `trade_monitor` prefers stamped values, backfills if missing (legacy in-flight signals)
- Falls back to static `PRE_TP_THRESHOLD_PCT` (0.35%) when ATR unavailable
- Symbolic + breakeven SL — no broker partial; subscriber sees the message and chooses
- Posts to active + free channels with raw and net-of-fees math at 10x
- Free-channel post emits `free_channel_post source=pre_tp` for truth-report attribution
- Setup blacklist: VSB / BDS / ORB; Regime allowlist: QUIET / RANGING / VOLATILE
- Telegram post shows: `⚡ Pre-TP @ 2,374.74 (+0.20% raw, ≥+1.3% net @ 10x) → SL → breakeven (auto)`
- 27 base + 21 stamping + 4 telegram render tests

---

## Session-end snapshot from owner's app screenshots (post-PR-#304 deploy)

After backfill ran the app showed real historical data:
- Pulse Recent signals card populated (ETHUSDT, XAUUSDT, SKYAIUSDT)
- Signals All / Closed views populated with 4 historical entries
- Closed → SL sub-filter showed BASEDUSDT 8d ago, MOVRUSDT 10d ago
- Closed → Invalidated **was empty (BUG)** because pre-PR-#305 the perf records mis-labelled invalidations as "CLOSED" → fixed in PR #305
- Agent drill-down populated: Architect (9h ago), Reclaimer (8d), Coil Hunter (3d), Counter-Puncher (never fired)
- Trade activity log populated

After PR #305's reconciliation runs on the next boot, the Closed → Invalidated sub-filter should populate with the same historical signals that currently show as "CLOSED" in the All view.

---

## Working Pattern

For any future code change:
1. Ask: **"how does this make signals more profitable for paid subscribers?"**
2. If answer is unmeasurable, "engineering hygiene," or speculative — **defer or drop**.
3. If answer is measurable (win rate, signal volume, R:R, time-to-resolution, fewer subscriber-visible failures), proceed: investigate, implement, test, document, ship.

For Lumin app changes:
1. All app dev happens in Termux on owner's phone — no Android Studio.
2. Installer scripts (`tools/lumin-v00X.sh`) live in **360-v2 engine repo** (this repo), curl'd from raw GitHub on phone, bashed in `~/lumin-app`. Each installer must be Termux-safe (bash + GNU sed/awk only).
3. Surgical patches preferred over full-file replacements when the change is localised — survives forward edits and fails loud on drift.
4. Every installer bumps `pubspec.yaml` version + commits with descriptive message; `git push` triggers GitHub Actions APK build with signed-when-keystore-set release.

For data correctness:
1. **Don't optimise based on `outcome_label`** without checking whether it's been corrected by `reconcile_invalidation_status`. Pre-PR-#305 perf records label every invalidation `"CLOSED"`. Truth-report parsing of those records is similarly biased.
2. Persistence is at three layers: in-memory `_signal_history` (App-API source) → `data/signal_history.json` (engine-restart durability) → `data/signal_performance.json` + `data/invalidation_records.json` (canonical history sources, used for backfill + reconcile). Treat invalidation_records as the truth-source for INVALIDATED.

---

## Key Files

### Engine
| Concern | File |
|---|---|
| 14 evaluators | `src/channels/scalp.py` |
| Confidence scoring | `src/signal_quality.py` |
| Regime classifier | `src/regime.py` |
| Scanner gate chain + `_CHANNEL_GATE_PROFILE` | `src/scanner/__init__.py` |
| Trade lifecycle + pre-TP + broker close on non-TP exits | `src/trade_monitor.py` |
| Auto-trade subsystem | `src/auto_trade/` (paper, risk, reconciler) |
| Live order manager (close_full + add_dca_entry) | `src/order_manager.py` |
| Paper order manager (close_full + add_dca_entry) | `src/paper_order_manager.py` |
| Pre-TP threshold + trigger-price stamping | `src/pre_tp_stamping.py` |
| Signal-history persistence | `src/signal_history_store.py` |
| Signal-history backfill + reconciliation | `src/signal_history_backfill.py` |
| Truth report parser | `src/runtime_truth_report.py` |
| Invalidation audit | `src/invalidation_audit.py` |
| API server + auth | `src/api/server.py`, `src/api/auth.py` |
| API snapshot adapters | `src/api/snapshot.py` |
| Macro watchdog | `src/macro_watchdog.py` |

### Lumin app
| Concern | File |
|---|---|
| App shell + nav | `lib/main.dart`, `lib/app/nav_shell.dart` |
| HTTP client + auth | `lib/data/api_client.dart`, `lib/data/auth_service.dart` |
| Repository abstraction | `lib/data/repository.dart` |
| Config + InheritedWidget | `lib/data/app_config.dart` |
| Format helpers | `lib/shared/format.dart` (added v0.0.9) |
| Pages | `lib/features/{pulse,signals,trade,agents,settings}/` |
| Theme + tokens | `lib/theme.dart`, `lib/shared/tokens.dart` |
| Shared widgets | `lib/shared/widgets/` (PreviewBadge, LuminCard, StatPill) |

### Installers (in 360-v2)
| Version | Installer |
|---|---|
| v0.0.1–v0.0.4 | `tools/lumin-bootstrap.sh`, `tools/lumin-tabnav.sh`, `tools/lumin-v003.sh`, `tools/lumin-v004.sh` |
| v0.0.5 | `tools/lumin-v005.sh` (backend wiring + repo pattern) |
| v0.0.6 | `tools/lumin-v006.sh` (anonymous JWT auto-auth) |
| v0.0.7 | `tools/lumin-v007.sh` (Pulse/Signals/Trade live data) |
| v0.0.8 | `tools/lumin-v008.sh` (cosmetic + UX honesty) |
| v0.0.9 | `tools/lumin-v009.sh` (per-agent drill-down + status sub-filters) |
| VPS API rollout | `tools/setup-vps-api.sh` |

---

## Reference: HTF Policy Cheat Sheet

| Path category | HTF treatment |
|---|---|
| Trend-aligned by regime gate (TPE / DIV_CONT / CLS / PDC) | None |
| Internally direction-driven (WHALE / FUNDING / LIQ_REVERSAL) | None |
| Counter-trend by design (LSR / FAR) | Soft penalty when 1H AND 4H both oppose |
| Structure with optional counter-trend (SR_FLIP / QCB) | Soft penalty when 1H AND 4H both oppose |
| Breakout (VSB / BDS / ORB) | None |
