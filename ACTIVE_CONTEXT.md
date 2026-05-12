# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## Current Phase

**Signal-quality batch shipped (2026-05-11) — 5 PRs that should transform subscriber experience.** Truth report this morning showed engine emitting 2 pairs/day (DOGE + Q), 10+ identical QUSDT carbon-copies at deterministic -0.10358%, 0% TP1 hit rate, and 7+ silent evaluators. Owner's clear position: **not ready for tester invites in current state.** A coordinated 5-PR batch addresses the dominant problems:

1. **PR #359 — Data-staleness gate.** Reject dispatch when the symbol's 1m kline is older than `MAX_KLINE_STALENESS_SEC` (180s default). Catches frozen-feed pairs (QUSDT-class) before they emit deterministic-loss carbon copies. New `HistoricalDataStore.last_kline_age_seconds()` accessor; `_is_kline_data_fresh()` gate in `_prepare_signal`.
2. **PR #360 — Structure-readiness gate.** Restrict structure-based evaluators (SR_FLIP / FAR / QCB / TPE / DIV_CONT / CLS / PDC / MA_CROSS / STANDARD) on pairs without aged multi-TF history. Threshold `MIN_1D_LEVELS_FOR_STRUCTURE_PATHS=5` from LevelBook. New `_YOUNG_PAIR_EVALUATORS` allowlist (6 paths: VSB, BDS, ORB, WHALE, LIQ_REVERSAL, FUNDING) for freshly-promoted pairs. Wired next to the existing mover-restriction.
3. **PR #361 — WHALE_MOMENTUM calibration.** `whale_alert` was 99.92% momentum_reject. `WHALE_TRADE_USD_THRESHOLD` 1M → 250k ($1M was BTC-calibrated, 99.9th-percentile across alts; 250k is ~95th percentile — frequent but still a "size" signal). `VOLUME_DELTA_SPIKE_MULTIPLIER` 2.0 → 1.3 (env-overridable for the first time). Target: 0/day → 3-8/day tape-driven emissions.
4. **PR #362 — MA_CROSS_TREND_SHIFT wake-up.** Bug in PR #318 integration: `_detect_cross` read full EMA arrays (`ind["ema21"]`) but live indicator API only stored scalar `*_last` values, and `ema50` was missing entirely. Live API now exposes scalar `*_prev` + `*_last` pairs for ema21/50/200. The 15th evaluator finally executes its cross logic after never firing since PR #318.
5. **PR #363 — VSB/BDS breakout geometry.** Three flaws: 5-candle search window (25 min) too narrow for fast vertical moves; `highs[-26:-6]` swing reference contaminated by recent rally; 0.75% pullback cap rejects deeper retests common in strong trends. Calibrated: search 5→12 candles, reference `[-26:-6]`→`[-50:-15]`, pullback cap 0.75%→1.5%. Mirror-image for BDS. Target: VSB+BDS combined 0/day → 5-12/day.

**Expected post-deploy emission profile:**
- Structure family (SR_FLIP / FAR / QCB): cleaned up — 5-15/day real signals (was 15-50/day mostly bug-driven)
- Tape (WHALE_MOMENTUM): 3-8/day (was 0)
- Specialist (MA_CROSS): 2-8/day (was 0)
- Breakout (VSB / BDS): 5-12/day (was 0)
- Trend-aligned (TPE / DIV_CONT / CLS / PDC): unchanged — next investigation
- **Total**: ~15-43/day across 4+ families instead of ~5-15/day monoculture

**Pending 24h observation cycle on:**
- TP1 hit rates from waking paths (first measurable on non-bug-polluted data)
- Subscriber-visible diversity (multiple pairs and families emitting)
- Suppression counters: `data_stale:{setup_class}`, `young_pair_restriction:{symbol}`, `dispatch_cooldown:*` should all be visible in the next truth report

**Tester invites still BLOCKED** until post-deploy data confirms real signals (not bug-driven, not carbon-copies, real TP1 outcomes).

**Next-priority threads (queued, NOT started — wait for data):**
- PDC (`POST_DISPLACEMENT_CONTINUATION`) — same `breakout_not_found` pattern (610k attempts), same fix likely applies. After 24h of PR #363 observation.
- Trend-family upstream filter audit (CLS / DIV_CONT / TPE — choked by shared `regime_blocked` + `ema_alignment_reject` cascade with identical counts across all four). Bigger investigation, needs evidence-based design.
- ORB (`feature_disabled`) — owner decision per OWNER_BRIEF §1.3: rebuild with proper session-anchored range logic, or delete.
- 4h indicator loop (so MA_CROSS primary 4h EMA50/200 path lights up). Memory cost vs signal-quality trade-off; observe MA_CROSS 1h emissions first.

---

## Shipped + Deployed — 360 CE Ops *(build 2026-05-11, first deploy 2026-05-12)*

**Status:** Live at https://ops.luminapp.org. Owner-confirmed login success on first deploy.

Built same session as the morning's signal-quality 5-PR batch, while the engine sat in its 24h post-#359..#363 observation window. Both slices of the original plan landed in one push: pulse + truth + signals + signal_detail (first slice) and diag + invalidations + performance (second slice). Initial PRs: #1 (full MVP) + #2 (CI hotfix).

**Why it shipped now.** The repo became accessible to MCP tooling this session — exactly the precondition `docs/360CE_OPS_PLAN.md § "How to resume in a new session"` was waiting on. Owner picked "full MVP" when asked which thread to work this session.

**What's live:**
- `https://ops.luminapp.org` — nginx (Let's Encrypt cert via certbot, expires 2026-08-10, auto-renew scheduled), proxying to `127.0.0.1:8088`
- Container `360ce-ops` from `ghcr.io/mkmk749278/360ce-ops:latest`, alongside the engine on the same VPS
- Auto-deploy: push to `360ce-ops` `main` → pytest → buildx → push to GHCR → SSH-deploy to VPS → `git pull && docker compose pull && docker compose up -d`
- Auth: starlette session cookie behind single-password gate using engine's `API_AUTH_TOKEN`
- Data sources wired:
  - Live engine REST `/api/*` via httpx
  - Engine `data/` mounted read-only via the named Docker volume `360-v2_360scalp-v2-data` (not a bind-mount path — see Lessons below)
  - `monitor-logs` branch artifacts via `raw.githubusercontent.com`, in-memory TTL cache (60s default)
  - `docker exec 360scalp-v2-engine ...` for on-demand `diag_*.py` (allow-listed script names, shell-metachar rejection)
- Routes live: `/`, `/truth`, `/truth/raw.{md,json}`, `/signals`, `/signals/{id}`, `/diag/geometry`, `/invalidations`, `/performance`, `/login`, `/logout`, `/healthz`

**What it deliberately does NOT include** (per plan §"Out of MVP scope"):
- No writes to engine state — control stays in Telegram + Lumin app
- No multi-operator access — single owner password
- No charts beyond tables for MVP
- No engine code changes
- Custom per-section truth-report renderers deferred — for MVP every section dumps as JSON; iterate once usage shows which views earn their layout cost

**Open follow-ups (post first-deploy):**
- Replace the `docker.sock` mount with an engine-side `/internal/diag/*` endpoint. Acceptable today because access is owner-only behind the password gate, but the socket grants root-equivalent host access — a sharp edge to remove before any access broadens beyond owner.
- Custom-rendered truth-report sections (path funnel, regime distribution, invalidation audit) once dashboard usage shows which views earn their layout cost.
- Lumin-app side: link to `ops.luminapp.org` from a settings/admin page once tester invites unblock and the dashboard has accumulated a usage trail worth showcasing.
- `performance_tracker.py` import path — currently duplicated reducer logic locally. If the engine ever publishes pre-reduced rolling stats via the API, ops should pivot to consume those rather than re-reducing from `signal_performance.json`.

**Lessons captured (worth reading before similar work):**

1. **GitHub Actions `secrets` context is not allowed in step-level `if:` expressions.** PR #1 had `if: ${{ secrets.VPS_HOST != '' }}` as a "skip-deploy-before-secrets-are-set" guard; GH Actions rejected the workflow at parse time across every run. The blessed pattern is to expose the secret in a job-level `env:` block (where `secrets` IS allowed) and check `env.X` in the `if:`. Direct usage in `if:` is a parse error. Fixed in PR #2; would have been caught by `actionlint` pre-push.
2. **Engine data lives in a Docker named volume, not a bind path.** First docker-compose used `${ENGINE_DATA_HOST_PATH:-/opt/engine/data}` as a bind mount — wrong, the engine's `data/` is in the named volume `360-v2_360scalp-v2-data` (project-prefixed by `docker-compose`). Sibling-container access should reference the named external volume, not the internal `/var/lib/docker/volumes/.../_data` host path. Fixed mid-deploy by switching the compose to `external: true` + `name: ${ENGINE_DATA_VOLUME:-360-v2_360scalp-v2-data}`.

**Full plan (still valid as design reference):** `docs/360CE_OPS_PLAN.md` (this repo).

---

## Previous Phase — Multi-user expansion + APK auto-update *(2026-05-10, shipped)*

Five PRs across both repos converted engine + app from owner-only to closed-beta-ready multi-user, plus eliminated the manual APK flash loop:
* PR #355 (engine) — Owner-tier write lock
* PR #356 (engine) — Phone OTP + user-id JWTs + billing webhook
* PR #8 (app) — Phone-OTP signin gate
* PR #9 (app) — Admin-token signin bypass for owner
* PR #10 (app) — In-app APK update via GitHub Releases poll

Multi-user infra is feature-complete; tester onboarding deferred until signal quality clears the post-#363 observation cycle.

---

**Multi-user expansion + APK auto-update shipped (2026-05-10).** Five PRs across both repos converted the engine + app from owner-only to a closed-beta-ready multi-user system, plus eliminated the manual APK flash loop:

1. **PR #355 (engine) — Owner-tier write lock.** PUT `/api/settings/pretp`, PUT `/api/settings/auto-trade`, POST `/api/auto-mode` now require `OWNER_TIER`. Anonymous / all-access / paid / free JWTs read-only; static `API_AUTH_TOKEN` bypass continues to grant owner.
2. **PR #356 (engine) — Phone OTP + user-id JWTs + billing webhook.** SQLite-backed `UserStore` (phone, tier, paid_until, telegram_chat_id), `OtpStore` (in-memory, 5-min TTL, 3 issues/hour/phone, 5 attempts/code), provider chain (LogOnly + WhatsApp + SNS-SMS), HMAC-verified `POST /internal/billing/grant` for `@LuminProBot` integration. Owner bootstrapped to `user_id=1` from `OWNER_PHONE_E164` env. JWTs gain optional `paid_until` claim alongside `exp`.
3. **PR #8 (app) — Phone-OTP signin gate on first launch.** PhoneSignInPage → OtpEntryPage → user-id JWT in secure storage. `_AuthGate` first-frame router replaces direct NavShell mount. ApiKeysSettingsPage test-connection switched to `/api/health` (works pre-signin); "Reset connection" → "Sign out" routing back to PhoneSignInPage.
4. **PR #9 (app) — Admin-token signin bypass for owner.** Collapsible "Sign in with admin token (owner)" panel on PhoneSignInPage. `AuthService.signInWithAdminToken` validates the static token against `/api/pulse`, persists with 1-year cached expiry. Owner skips OTP-from-logs entirely.
5. **PR #10 (app) — In-app APK update via GitHub Releases poll.** CI workflow auto-creates `v{run_number}` Release on every push to main with the signed APK attached (`contents: write` permission added). Banner above NavShell polls `releases/latest`, compares against `PackageInfo.buildNumber`, downloads via Dio, hands to Android's package installer via `open_filex`. `REQUEST_INSTALL_PACKAGES` injected at CI manifest-injection step. Manual download/unzip/uninstall/install loop is gone.

**Auth model in production:**
- **Owner**: static `API_AUTH_TOKEN` via the admin-token signin panel — `tier=owner`, no OTP delivery needed.
- **Testers (5)**: phone-OTP via `LogOnlyOtpProvider`. Owner reads OTP from engine logs (one-time per tester onboarding) and forwards. After first verify, JWT cached 7 days. WhatsApp / SNS providers wired but inactive — flip env when Meta Business Verification clears.
- **Billing**: `@LuminProBot` POSTs HMAC-signed grants to `/internal/billing/grant` to flip user tier; engine never handles payment directly.

**Phase 3 (per-user data scoping) deferred per plan** — ship 2–3 weeks after Phase 2 stable across the closed-beta cohort. Premature today.

**Process locked-in (per plan):** every PR after the multi-user-expansion plan landed includes a written design summary in the PR description before code review. Owner approves design, then code. The five PRs above all followed this rule.

---

## Previous Phase — Chartist-eye roadmap *(2026-05-06, still under observation)*

**Chartist-eye roadmap shipped in full (2026-05-06 evening).** Following the morning's app-era doctrine reset (PRs #308–#311), the owner asked: *"how can we improve real S/R, structure, MA crossovers — what humans do — without manual effort?"*

The answer was a programmatic "world model" every evaluator can consult: persistent multi-TF S/R levels with confluence scoring, structural leg classification, volume profile, a discrete MA-cross emitter, and continuation/reversal patterns. Eight PRs executed the design:

1. **PR #314 — Top-emitter OI softening.** LSR/SR_FLIP/FAR were over-suppressed by the OI gate (91–100% of soft-penalty stack). Path-aware modulators added.
2. **PR #315 — LevelBook infrastructure.** Multi-TF S/R levels (1d/4h/1h swing pivots + round numbers), scored by touches/age/timeframe, top 60 retained per symbol.
3. **PR #316 — Confluence bonus wired.** When entry sits in a band where ≥2 distinct LevelBook zones cluster, a soft-penalty bonus fires (2→3, 3→6, 4+→9).
4. **PR #317 — StructureTracker infrastructure.** Per (symbol, tf) classification of HH/HL bull leg vs LH/LL bear leg vs RANGE.
5. **PR #318 — MA_CROSS_TREND_SHIFT 15th evaluator.** Discrete EMA50/200 (4h) or EMA21/50 (1h) crossover trigger. 24h cooldown per (symbol, direction). Specialist role.
6. **PR #319 — VolumeProfile lite infrastructure.** POC + Value Area High/Low per symbol; in_value_area / is_near_poc / is_at_value_edge helpers.
7. **PR #320 — Pattern catalog completion.** Bull flag + bear flag added; pre-existing H&S detector wired into `detect_patterns` dispatch; confidence-bonus mapping extended.
8. **PR #321 — Wiring follow-up.** VolumeProfile POC/VAH/VAL injected into LevelBook so confluence scoring picks them up automatically. Structure-alignment bonus (+3 pts) wired for TPE/DIV_CONT/CLS/PDC when entry direction matches the 4h leg.

**Magnitude bounded.** Combined `confluence + structure_align` max lift is ~12 pts. Calibration: a sub-50 candidate cannot reach paid (65) by chartist-eye lift alone — it only nudges borderline B-tier candidates over the threshold. **Hard structural gates and scoring tiers untouched.**

**Pending only one truth-report cycle of observation.** Then: act on whatever the data shows. No pre-committed next phase — the chartist-eye roadmap is feature-complete.

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
- **Top-emitter OI softening** (PR #314) — LSR `oi=0.30`, FAR `oi=0.30`, SR_FLIP `oi=0.50`. Recovers borderline B-tier candidates that were being dropped by a single gate.
- **WATCHLIST tier removed** (PR #308) — sub-65 → FILTERED, dropped silently; free channel fed only by storytelling mirrors + content-engine
- **QUIET-block doctrine** uniform 65 paid-tier floor — no scrap-routing exempts
- **Chartist-eye world model** (PRs #314–#321) — multi-TF LevelBook with VP + round-number injection, StructureTracker on 4h, VolumeProfile (POC/VAH/VAL), MA_CROSS_TREND_SHIFT 15th evaluator, bull/bear flag + H&S patterns. Wired into `_prepare_signal` as bounded soft-penalty bonuses (`CONFLUENCE×N` ≤ 9 pts, `STRUCT_ALIGN` 3 pts). Combined max lift ~12 pts; cannot lift sub-50 candidate to paid alone.
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
- **API endpoints (15 total):** `/api/health`, `/api/auth/anonymous`, `/api/auth/refresh`, `/api/auth/request-otp`, `/api/auth/verify-otp`, `/api/pulse`, `/api/signals` (with optional `?status=&setup_class=`), `/api/signals/{id}`, `/api/positions`, `/api/activity` (with optional `?setup_class=`), `/api/auto-mode` GET/POST, `/api/agents`, `/api/settings/pretp` GET/PUT, `/api/settings/auto-trade` GET/PUT, `/internal/billing/grant` (HMAC-verified server-to-server). `SignalDetail` carries `pre_tp_threshold_pct` + `pre_tp_trigger_price` for the app to display
- **Phone-OTP + user-id JWT auth** (PR #356, 2026-05-10): SQLite-backed `UserStore` (phone, tier, paid_until, telegram_chat_id), `OtpStore` (5-min TTL, 3 issues/hour/phone, 5 attempts/code), provider chain (LogOnly default — closed beta — with WhatsApp + AWS-SNS-SMS fallbacks awaiting Meta verification). Owner bootstrapped to `user_id=1` from `OWNER_PHONE_E164` env. Static `API_AUTH_TOKEN` bypass continues to grant `tier=owner` for tooling.
- **Owner-tier write lock** (PR #355, 2026-05-10): PUT `/api/settings/*` and POST `/api/auto-mode` require `OWNER_TIER`; other tiers read-only.
- **`@LuminProBot` billing webhook** (PR #356): `POST /internal/billing/grant {phone, tier, paid_until_iso}` + HMAC-SHA256 verification on the raw body. Bot updates user tier when subscription state changes; engine never handles payment.
- **Lumin v0.0.9 shipped:** Pulse / Signals / Trade pages on real engine data; per-agent drill-down (bottom sheet with stats card + 10 most-recent signals filtered by `setupClass`); Signals tab status sub-filters (TP / SL / Invalidated / Expired) when "Closed" is active; new `lib/shared/format.dart` pure-Dart price/PnL/pct/age helpers
- **Lumin Phase 2 app shipped (2026-05-10):** PhoneSignInPage / OtpEntryPage replace anonymous-mint-on-first-launch (PR #8); admin-token signin bypass for owner (PR #9); in-app APK update banner via GitHub Releases poll (PR #10) — every push to main produces a `v{run_number}` Release; banner downloads + hands to Android installer. Manual flash loop eliminated.

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

### Day 2 — app-era doctrine reset
| PR | Title | Status |
|---|---|---|
| #307 | Close broker + compute P&L + archive on signal expiry | ✅ merged |
| #308 | Remove WATCHLIST tier entirely (engine + tests + telegram_bot) | ✅ merged |
| #309 | Drop wrong-regime blocks from WHALE/VSB/BDS (per §3.4) | ✅ merged |
| #310 | Tighten QCB volume_div modulator 0.60 → 0.20 | ✅ merged |
| #311 | Doc: app-era doctrine reset | ✅ merged |
| #312 | `/reset_full` clears all signal-data stores atomically | ✅ merged |
| #313 | Backfill TP2/TP3 from `dispatch_log.json` + boot reconciliation | ✅ merged |

### Day 2 — chartist-eye roadmap
| PR | Title | Status |
|---|---|---|
| #314 | Top-emitter OI softening (LSR/SR_FLIP/FAR) | ✅ merged |
| #315 | LevelBook infrastructure (multi-TF S/R + round numbers) | ✅ merged |
| #316 | Wire LevelBook confluence into soft-penalty stack | ✅ merged |
| #317 | StructureTracker (HH/HL bull leg vs LH/LL bear leg) | ✅ merged |
| #318 | MA_CROSS_TREND_SHIFT 15th evaluator | ✅ merged |
| #319 | VolumeProfile (POC + VAH/VAL) | ✅ merged |
| #320 | Pattern catalog: bull/bear flag + wire H&S | ✅ merged |
| #321 | Wire VolumeProfile + StructureTracker into scoring stack | 🟡 open |

End-of-session test count: **3978 passed**, 0 failures, 0 regressions.

---

## Open Queue

### Awaiting truth-report observation cycle
The chartist-eye roadmap is feature-complete. Before queuing more changes, watch one truth-report cycle (~1 hr post-#321 merge) for:
- `CONFLUENCE×N` flags appearing in `soft_gate_flags` for some fraction of signals
- `STRUCT_ALIGN:BULL_LEG` / `STRUCT_ALIGN:BEAR_LEG` flags on TPE/DIV_CONT/CLS/PDC paid-tier signals
- `MA_CROSS_TREND_SHIFT` attempts ticking each cycle, ~1-3 actual signals/day
- Borderline B-tier candidates near multi-TF level + VP zones lifted to paid; **no** sub-50 candidate reaching paid by chartist-eye lift alone (regression guard)
- Invalidation audit ratio (PROTECTIVE / PREMATURE / NEUTRAL) stays net-protective across all paths
- `VOLUME_SURGE_BREAKOUT` / `BREAKDOWN_SHORT` / `WHALE_MOMENTUM` rejection mix shifts away from `regime_blocked` toward thesis-driven reasons

### Originally-deferred items, still valid
- **TPE softening.** Truth report (pre-roadmap) showed ~80% of TPE attempts blocked by `regime_blocked`. With STRUCT_ALIGN bonus now wired for TPE, observe whether this changes before further softening the regime gate.
- **Scanner gates conversion.** `cross_asset` hard→soft and MTF hard→soft, where the structural-impossibility condition isn't met. Both still hard-blocking signals the scoring tier could correctly classify.
- **DIV_CONT / CLS / PDC / FUNDING per-path audit.** Same THESIS-vs-FILTER classification used in PRs #309/#310.

### Held — investigation paused
- **SR_FLIP_RETEST 0% win rate, paid-volume drought.** Pre-roadmap data showed bulk filtering at sub-paid threshold. With OI modulation (PR #314) + confluence bonus (#316) + structure-align bonus (#321), the paid-tier rate is the new headline metric to watch. If still 0% wins after observation, the path's thesis itself needs revisiting — not its scoring.
- **OI-flip on remaining trend paths (DIV_CONT 100%).** PR #314 covered top emitters only. DIV_CONT may need the same modulation if structure-align bonus doesn't lift enough.

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
- **Lumin app-side: disable Save buttons when user is not owner** — engine returns 403 today on settings PUT for non-owner JWTs (PR #355); the app shows a toast on the rejected save instead of hiding the button. Cosmetic only (engine 403 is the source of truth) but worth a small follow-up once tester invites scale beyond 5
- **Verify auto-release pipeline post-PR-#10** — first push to lumin-app/main after merge (commit `bd66765`) should produce GitHub Release `v{run_number}` with attached APK. If the release doesn't appear within ~20min of the CI run, check repo Settings → Actions → General → Workflow permissions (must allow `contents: write`)

### Signal-quality follow-ups (queued, post-2026-05-11 observation cycle)
- **PDC `breakout_not_found` fix** — `POST_DISPLACEMENT_CONTINUATION` has same rejection pattern as VSB/BDS pre-#363 (610k attempts). Same widened-window + pushed-reference fix likely applies. Defer until VSB/BDS observation data confirms the approach
- **Trend-family upstream filter audit** — CLS / DIV_CONT / TPE / PDC all killed by shared cascade: `basic_filters_failed ≈ 417k`, `ema_alignment_reject ≈ 425k`, `regime_blocked ≈ 357k` (identical counts → single upstream gate killing 4 paths at once). Needs evidence-based investigation, not a knob tune
- **Investigate `breakout_not_found` on PDC** — same shape as VSB/BDS; same fix likely
- **4h indicator loop** — add `4h` to `_build_scan_context`'s indicator dict so MA_CROSS primary 4h EMA50/200 detection path lights up (only 1h fallback works today post-#362). Memory cost vs signal-quality trade-off; observe MA_CROSS 1h emissions first
- **ORB rebuild or delete decision** (owner per OWNER_BRIEF §1.3) — `feature_disabled` today; in the breakout family but inert

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
4. **Always via a PR.** Fresh topic branch off `main`, design-summary body, no direct pushes to long-lived session branches. See `CLAUDE.md § Change-management protocol`.

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
| 15 evaluators | `src/channels/scalp.py` |
| Confidence scoring | `src/signal_quality.py` |
| Regime classifier | `src/regime.py` |
| Scanner gate chain + `_CHANNEL_GATE_PROFILE` + chartist-eye wiring | `src/scanner/__init__.py` |
| **LevelBook** (multi-TF S/R + round numbers + VP injection) | `src/level_book.py` |
| **StructureTracker** (HH/HL bull leg vs LH/LL bear leg) | `src/structure_state.py` |
| **VolumeProfile** (POC + VAH/VAL) | `src/volume_profile.py` |
| Pattern catalog (DT/DB/triangle/flag/H&S/candlestick) | `src/chart_patterns.py` |
| Confluence detector (cross-strategy multi-channel) | `src/confluence_detector.py` |
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
