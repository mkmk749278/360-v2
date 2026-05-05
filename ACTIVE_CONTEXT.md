# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## Current Phase

**Two parallel tracks:**

1. **Engine — data-driven tuning.** Per-path entry-quality audit complete under the scalping doctrine (`OWNER_BRIEF.md` §3.2). All 14 evaluators reviewed; doctrine-corrections shipped. Next changes are gated on empirical data from the Phase 1 invalidation audit and the runtime truth report — no further structural per-path work without measurable business-chain justification.

2. **Lumin app + backend wiring — live.** v0.0.7 ships the full Pulse / Signals / Trade pages on real engine data via FastAPI + anonymous JWT. VPS reverse-proxy + cert at `https://api.luminapp.org`. v0.0.8 cosmetic + UX-honesty patch staged. Next major: v0.1.0 settings persistence + Telegram-auth (architecture brief pending owner sign-off).

---

## What's Currently Working

### Engine
- **Engine** healthy, scanning 75 pairs continuously, deploying via GitHub Actions
- **Monitor** runtime truth report on `monitor-logs` branch — regime distribution, gate metrics, confidence component breakdown, soft-penalty per-type breakdown, scoring-engine-dimension breakdown, pre-TP fire stats, free-channel post attribution, invalidation quality audit
- **Risk-component scoring** calibrated for scalp R-multiples (max credit at 2.0R)
- **Regime classifier** BB-width VOLATILE threshold at 8.0% (env-overridable)
- **HTF mismatch policy** soft penalty (not hard block) on SR_FLIP / QCB / FAR
- **QUIET-block doctrine** uniform 65 paid-tier floor — no scrap-routing exempts
- **Universal 0.80% SL floor** plus per-setup caps active
- **Invalidation quality audit** classifying every kill as PROTECTIVE / PREMATURE / NEUTRAL post-30-min
- **Counter-trend Regime-neutral baseline** (LSR / FAR) — `_REGIME_NEUTRAL_SETUPS` frozenset gives 14.0 baseline in non-affinity regimes (avoids HTF-soft-penalty + Regime-score double penalty)
- **Kill Zone disabled on 360_SCALP** (`_CHANNEL_GATE_PROFILE["360_SCALP"]["kill_zone"] = False` — `src/scanner/__init__.py:437`). Auxiliary `360_SCALP_*` channels keep KZ pending per-channel data
- **Pre-TP grab Phase A** live in production (`PRE_TP_ENABLED=true`). ATR-adaptive threshold with fee floor; truth-report instrumentation populated (1 fire observed post-deploy: TPE @ +2.80% net @10x via static-fallback)
- **Auto-trade Phase A1+A2+A3 complete:** PaperOrderManager (15 tests), RiskManager 6 gates (23 tests), PositionReconciler (21 tests). Live `OrderManager` is real CCXT-backed (not stubbed). All env-overridable. `/automode` Telegram command for runtime mode flips without redeploy (14 tests)
- **Macro watchdog Phase 1+2a+2b+5:** HIGH/CRITICAL events to free channel, BTC big-move alerts, BTC/ETH 1h regime-shift alert, paid signal-close storytelling mirror

### Subsystems present in code but historically under-documented
- **DynamicTierManager** (`src/tier_manager.py` + `DYNAMIC_TIER_*` env vars) — dynamic pair-tier promotion based on liquidity / volume
- **ContentScheduler** (`src/content_scheduler.py`) — daily briefings, weekly scoreboard, performance reports to free channel
- **TradeObserver** — captures full trade lifecycle for AI-digest content
- **FreeWatchService + RadarAlert** — watch creation via `_handle_radar_candidate`; resolved on paid signal

### Lumin app + API
- **VPS API rolled out** at `https://api.luminapp.org` — nginx reverse-proxy, Let's Encrypt cert, rate-limited 60 r/min, owner ran `setup-vps-api.sh` 2026-05-04
- **API endpoints live (11 total):** `/api/health`, `/api/auth/anonymous`, `/api/auth/refresh`, `/api/pulse`, `/api/signals`, `/api/signals/{id}`, `/api/positions`, `/api/activity`, `/api/auto-mode` GET/POST, `/api/agents`. Anonymous-JWT auth on every protected endpoint; static-bearer escape hatch for owner debug behind `API_ALLOW_STATIC_TOKEN`
- **Lumin v0.0.7 shipped:** Pulse / Signals / Trade pages on FutureBuilder against live repo. Pull-to-refresh + skeleton + error/Retry view. Trade mode toggle hits `/api/auto-mode` POST and refreshes. Default mode is Live; Mock is offline fallback
- **Lumin v0.0.6 shipped:** anonymous JWT auto-auth. First launch mints device-bound JWT via `/api/auth/anonymous`, encrypted at-rest in `flutter_secure_storage`, transparent silent refresh + 401 wipe-and-remint. Zero manual token UX. Pure-stdlib HS256 on engine side (dropped PyJWT dep)
- **Lumin v0.0.5–v0.0.1 shipped earlier:** repo + theme + 5-tab nav + 14-agent grid + mock dashboards + 7 settings drill-downs + repository pattern + AppConfigScope

---

## Open Queue

### Pending data
- **TP1 ATR cap re-derivation** (1.8R / 2.5R / uncapped on SR_FLIP / FUNDING / DIV_CONT / CLS) — wait for Phase 1 invalidation audit data on TP1 hit rates per setup × ATR-bucket.
- **VSB / BDS generated-but-not-emitted** — diagnosed against latest truth report (1.77M attempts window):
  - VSB: 647 generated → 314 reach scoring → 0 emit, 0 watchlist. All 314 filtered at `min_confidence`. Avg final 46.78 vs threshold 80 (gap 33). Even un-penalised, would still land 19 below paid B-tier.
  - BDS: 1 generated total — structurally silent. Funnel rejects 99.999% upstream (`regime_blocked` 38%, `breakout_not_found` 37%). Not a scoring problem.
- **FAR `STRONG_TREND` regime block** — empirical conjecture ("low edge") rather than structural impossibility. Could be soft penalty per doctrine; needs win-rate data.
- **LSR hard 1H MTF reject in TRENDING/VOLATILE** — narrow filter (both 1H EMA AND RSI must oppose). Could be soft per doctrine; revisit if data shows it's blocking 65+ paid candidates.

### Held — investigation paused per owner direction
- **SR_FLIP_RETEST 0% win rate, worsening PnL.** Truth report flags as top concern. 5 closed signals, avg PnL −0.17%, window-over-window delta −0.21. 12,557 emissions all WATCHLIST tier; only 68 cleared paid min_confidence. Resume when Owner directs.
- **OI-flip soft-penalty doctrine audit.** With KZ disabled on `360_SCALP`, OI flip is now the dominant soft-penalty bottleneck — DIV_CONT filtered: 100% of penalty from OI; FAR: 91%; LSR: 100%; SR_FLIP kept: 100%. Same KZ-style question: is OI flip a 24/7-crypto-doctrine gate or inherited noise? Held.

### Pending owner decision
- **OPENING_RANGE_BREAKOUT** — currently `feature_disabled` (`scalp.py:2337`). Rebuild with proper session-anchored range logic, or delete the path entirely. Not a CTE call.
- **v0.1.0 settings-persistence architecture** — five decisions awaiting owner sign-off (see "v0.1.0 design brief" below). Major-architecture per OWNER_BRIEF §1.3, blocking implementation.

### In flight
- **Lumin v0.0.8 — cosmetic + UX honesty fixes (staged on `claude/session-setup-7YaUl`).**
  - API keys page: `PreviewBadge` was unconditional, now hidden when `_liveMode` is true (matches all other pages' pattern). Stale "Preview — sample data" banner was contradicting the page's own green-OK Test connection result.
  - About page: `_version` 0.0.4 → 0.0.8, `_build` `'preview-mock'` → `'live'`. Hardcoded constants had drifted across three releases (long-term: read from pubspec via `package_info_plus` in v0.1.0).
  - Pulse regime card: `'X.X% of cycles'` → `'X.X% trending'`. Field is `regimePctTrending` (% of cycles in TRENDING regime); pairing with current-regime label produced reads like "RANGING / 0.0% of cycles" — semantically wrong even when mathematically correct.
  - Signals empty state: in Live mode shows "Engine is scanning 75 pairs. New paid signals appear here when they fire." instead of "Pull down to refresh." — so paid subscribers seeing zero signals don't conclude the app is broken (the truth-report-flagged paid-volume drought is the real cause, but the page should communicate honestly while that's worked).
  - Installer: `tools/lumin-v008.sh` — surgical sed/awk patches (no full-file rewrites), idempotent, verified via dry-run.

### v0.1.0 design brief — settings persistence + Telegram-auth (awaiting sign-off)

**Problem:** All 5 settings pages (auto-trade / pre-TP / risk gates / agents / etc.) currently show "Saved (session only — backend wiring pending)" — UI-only. Subscriber toggles their per-evaluator agent off, restarts, it's back on. Worse than incomplete: misleading. Also blocks B16 subscription gating because there's no authenticated user identity.

**Five decisions for owner:**
1. **Identity model.** Anonymous device JWT (settings die on reinstall, no cross-device) vs authenticated Telegram-bot JWT (B13-aligned, on-ramp to B16). **Recommend authenticated.**
2. **Storage backend.** SQLite at `data/settings.db`. Atomic writes, file-based, no extra service. **Recommend yes.**
3. **Settings ceiling.** Env-var defines absolute upper bound; subscriber can tighten but never loosen. Critical for B12 auto-trade safety. **Recommend yes, universal.**
4. **Per-agent toggle endpoint.** `POST /api/agents/{setup_class}/toggle` separate from generic settings — most-clicked surface, optimistic UX. **Recommend yes.**
5. **Scope.** Full bundle in v0.1.0 (settings + Telegram-auth) vs incremental (settings first, auth in v0.1.1). **Recommend full** — incremental ships with the same anonymous-device-key problem.

**Estimated work:** 3–5 days end-to-end. New: `src/api/settings.py`, `src/api/auth_telegram.py`, `src/auth/telegram_login.py`, `src/settings_store.py`. Hot-apply read-throughs in `RiskManager` / `trade_monitor` / `scanner`. Flutter: 6 new repo methods, new Telegram-login page, all 5 settings pages switched from session-only to repository-backed with optimistic save + 422-rollback.

### Free-channel content rollout (in progress)

**Phase 1 — Macro events to free channel** ✅ shipped (HIGH/CRITICAL only)
**Phase 2a — BTC big-move alert** ✅ shipped (≥3% / ≥5%, 1h cooldown)
**Phase 2b — BTC/ETH regime-shift alert** ✅ shipped (1h EMA21 cross, 4h cooldown)
**Phase 2 (still open) — additional event triggers** — BTC dominance ±2% (needs extra data source)
**Phase 3 — Charts attached to scheduled posts** — `src/chart_renderer.py` using mplfinance; attached to morning brief / EOD wrap / event-driven alerts
**Phase 4 — Coin spotlights** — top mover / breakout watch daily posts with charts
**Phase 5 — Signal-close storytelling** ✅ shipped (TP3 / SL mirror to free channel with `📣 Paid Signal Result` header)

### Pre-TP grab — Phase A ✅ shipped + ENABLED in production
- `TradeMonitor._check_pre_tp_grab` fires on ATR-adaptive threshold within 30 min, non-trending regime, non-breakout setup
- Resolved threshold = `max(PRE_TP_FEE_FLOOR_PCT, PRE_TP_ATR_MULTIPLIER × atr_pct)`
- Falls back to static `PRE_TP_THRESHOLD_PCT` (0.35%) when ATR unavailable
- Symbolic + breakeven SL — no broker partial; subscriber sees the message and chooses
- Posts to active + free channels with raw and net-of-fees math at 10x
- Free-channel post emits `free_channel_post source=pre_tp` for truth-report attribution
- Setup blacklist: VSB / BDS / ORB; Regime allowlist: QUIET / RANGING / VOLATILE
- 27 tests in `tests/test_pre_tp_grab.py`
- Truth-report instrumentation: `## Pre-TP grab fire stats` section (1 fire observed post-deploy)

---

## Latest truth-report observations (informational)

From the most recent monitor cycle (data ~4.6h pre-restart; engine "Up 27m" at owner's last screenshot):
- **Paid-tier emissions are effectively zero** in the window — only 1 TPE paid signal (final 80.50, threshold 80.00, marginal). Doctrine §2.3 target = 1–10 paid/day; below floor.
- **SR_FLIP**: 12,557 watchlist emissions, 5 closed, 0% win rate, avg PnL −0.17%, getting worse
- **Regime mix**: QUIET 46.3% / TRENDING_UP 32.9% / VOLATILE 20.2% / TRENDING_DOWN 0.6% / RANGING 0.1% — QUIET-heavy market explains paid-volume drag
- **Free-channel pipeline**: 8 posts in window (regime_shift × 6, signal_close × 1, pre_tp × 1) — all rollout phases firing
- **Invalidation audit**: 5 PROTECTIVE / 0 PREMATURE / 5 NEUTRAL — net-helping, don't tighten

These observations remain gated behind owner direction on the SR_FLIP / OI-gate investigation hold above.

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

---

## Key Files

### Engine
| Concern | File |
|---|---|
| 14 evaluators | `src/channels/scalp.py` |
| Confidence scoring | `src/signal_quality.py` |
| Regime classifier | `src/regime.py` |
| Scanner gate chain + `_CHANNEL_GATE_PROFILE` | `src/scanner/__init__.py` |
| Trade lifecycle + pre-TP | `src/trade_monitor.py` |
| Auto-trade subsystem | `src/auto_trade/` (paper, risk, reconciler) |
| Live order manager | `src/order_manager.py` |
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
