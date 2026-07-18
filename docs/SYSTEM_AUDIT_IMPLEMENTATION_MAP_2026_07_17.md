# System Audit & Full Implementation Map — 2026-07-17

**Scope:** all four repos (`360-v2` engine, `lumin-app`, `360ce-ops`, `lumin-legal`),
live runtime state (truth report @ `monitor-logs`, feature-liveness probes,
auto-detected issues), CI/CD, and cross-repo contracts.
**Method:** code-verified against `main` HEAD of every repo (engine `8a3d1af`,
app `2b12a84`, ops `22dbf6c`, legal `5cb85ef`) — not transcribed from docs.
Ruff re-run clean on engine `src/ config/` in this session.

**Verdict in one line:** the system is structurally healthy and self-monitoring
(no open PR backlog, backups fixed, breakers wired, probes paging), with **one
live open finding**: the 18th evaluator (MEAN_REVERT) still emits zero signals
— root-cause analysis below points past the S60 fix to the regime-compat hard
gate (§9, F1).

---

## 1. System topology

```
                       ┌────────────────────────────────────────────────┐
                       │ VPS (Ubuntu, Docker Compose, 24/7)             │
 Binance WS/REST ────▶ │  engine ── Redis ── api    signing_service     │
                       │     │        │       │        (Unix socket,    │
                       │  SnapshotWriter   RedisEngineFacade  KMS HSM)  │
                       └─────┼────────┼───────┼────────────────────────┘
                             │        │       └── api.luminapp.org (Cloudflare)
                             │        │                    │
      Telegram (paid mirror)◀┘        │              Lumin app (Play production,
      FCM topics alerts/signals ──────┼──────────────  org.luminapp.lumin)
                                      │
                       ops.luminapp.org (360ce-ops web + 24/7 agent + ops mobile)
                                      │
                       monitor-logs branch ◀── GitHub Actions (vps-monitor,
                       truth report, backups)   vps-liveness, vps-backup)

      lumin-legal ──▶ GitHub Pages (privacy/terms/risk/delete-account)
                      ← linked by app Settings→Legal + Play Console listing
```

- **Two engine modes** via `API_PROCESS_ISOLATED` (default `false`; **`true` live
  on VPS**): isolated = engine + api containers bridged by Redis snapshots;
  api writes per-user settings to shared SQLite (WAL), engine reads fresh at
  dispatch.
- **Deploy:** push to `main` → GitHub Actions → `deploy.sh` on VPS (~45–60 s).
  Doc-only files are `paths-ignore`'d. App: `main` push builds APK (sideload) +
  AAB (Play) and auto-creates a GitHub Release.

---

## 2. Engine (`360-v2`) — implementation map

### 2.1 Boot & runtime processes

| Concern | Module | Notes |
|---|---|---|
| Boot, WS/REST init | `src/bootstrap.py`, `src/main.py` | launches runtime tasks incl. API (single-process mode) |
| Isolated API entry | `src/api/main.py` | inits Firebase Admin, keystore, kill switch, tunables, **KMS (`_maybe_init_kms`, #736)** |
| WS management | `src/websocket_manager.py` | ~300 streams; reconnect/backoff/listenKey lifecycle; **gap-refill after reconnect (#732)** |
| Data stores | `src/historical_data.py` (numpy arrays — never boolean-test), `src/order_flow.py` | 6 TFs OHLC, OI, CVD, funding, liquidations |
| Pair universe | `src/pair_manager.py` | 75 USDT-M pairs, dynamic promotion (mover ignition `src/mover_ignition.py`) |
| Runtime tunables | `src/runtime_tunables.py` | Firestore-backed, 5 s TTL, **stale-serve + single-flight refresh thread** (post-S55 wedge fix) |
| Watchdog / healthcheck | `scripts/watchdog.py`, `healthcheck.py` | boot-grace 600 s, StartedAt-floored heartbeat ages, cooldown-gated escalation pages |

### 2.2 Signal generation path (order is the code path)

1. **Scanner** — `src/scanner/__init__.py`, 15 s × 75 pairs.
2. **18 evaluators** — `src/channels/scalp.py` (`_evaluate_*`), each owns SL/TP
   geometry (B7). Under default config **scalp.py is the only paid-signal
   generator** (aux channels: divergence pilot-only ON, cvd/vwap/supertrend/
   ichimoku/orderblock disabled, fvg/orderblock radar-only).
3. **classify_setup** (`src/signal_quality.py`) — channel-compat +
   **regime-compat hard gate** vs `MarketState` (STRONG_TREND / WEAK_TREND /
   CLEAN_RANGE / DIRTY_RANGE / BREAKOUT_EXPANSION / VOLATILE_UNSUITABLE).
   Self-classifying setups keep evaluator identity.
4. **execution_quality_check** (`src/signal_quality.py`) — per-setup trigger +
   max-extension (MEAN_REVERT fade branch + 5.0 ATR cap since #732).
5. **MTF confluence gate** — regime-keyed min-score, family caps
   (`mean_reversion` 0.30 … `compression` 0.25), §3.4 doctrine-exempt set
   (tape-driven + breakout + mover setups are never MTF-hard-vetoed).
6. **Longs-regime gate** (15 m regime; shorts not gated) and
   **RANGING-low-ADX family block** (trend/breakout/continuation/orderflow +
   fail-closed `other`; `htf_trend_aligned` + mover setups exempt).
7. **Soft-penalty gates** (per-channel profile; KZ **disabled** on all scalp
   channels by doctrine): VWAP overextension, OI flip, cross-asset, spoof,
   volume-CVD divergence, cluster suppression, SYM_DIR, **BTC_DIR (shadow —
   `BTC_DIR_PENALTY_APPLY=false`, would-fires logged)**.
8. **SignalScoringEngine** — dimensions SMC / Regime / Volume / Indicators /
   Patterns / MTF (+ thesis adj). Chartist-eye inputs: `level_book.py`,
   `structure_state.py`, `volume_profile.py`, `chart_patterns.py`. Bonus caps:
   confluence ≤9, structure-align 3 (sub-50 can't reach 65 on bonuses).
9. **Confidence gate** — 65 paid floor (A+ 80–100, B 65–79, FILTERED dropped);
   `quiet_scalp_min_confidence` floor in QUIET.
10. **Enqueue** — universal SL min 0.80%, dedup/cooldown (B4), cluster caps.
11. **SignalRouter** (`src/signal_router.py`) → Telegram paid mirror
    (in-app feed is the primary surface, B1) + FCM topics via
    `src/push_notifications.py`.

**The 18 evaluators — live status (truth-report window ending 2026-07-17):**

| Evaluator | Status | Emitted (window) |
|---|---|---:|
| SR_FLIP_RETEST | live (LONG side `SR_FLIP_LONG_ENABLED=false`) | 64 |
| DIVERGENCE_CONTINUATION | live | 19 |
| FAILED_AUCTION_RECLAIM | live | 18 |
| QUIET_COMPRESSION_BREAK | live | 16 |
| MOVER_TREND_PULLBACK | live (measured −0.29R; `@TUNED` shadow arm measuring) | 13 |
| LIQUIDITY_SWEEP_REVERSAL | live | 12 |
| BREAKDOWN_SHORT | live | 3 |
| TREND_PULLBACK_EMA | live | 3 |
| MOVER_AVWAP_SCALP | live (measured loser; `@TUNED` arm measuring) | 1 |
| MA_CROSS_TREND_SHIFT | live, low-rate | 0 |
| FUNDING_EXTREME_SIGNAL | live — generates, 172/214 gate-killed | 0 |
| LIQUIDATION_REVERSAL | live — generates, 32/32 gate-killed | 0 |
| POST_DISPLACEMENT_CONTINUATION | live, low-rate | 0 |
| VOLUME_SURGE_BREAKOUT | live (measured loser; `@TUNED` arm measuring) | 0 |
| WHALE_MOMENTUM | live, non-generating this window (momentum thresholds) | 0 |
| **MEAN_REVERT** | **⛔ 0 emissions ever — open finding F1 (§9)** | 0 |
| OPENING_RANGE_BREAKOUT | **flag-disabled** (`feature_disabled`) | 0 |
| CONTINUATION_LIQUIDITY_SWEEP | **merged into LSR** (`cls_disabled_merged_into_lsr`) | 0 |

### 2.3 Execution stack (server-side auto-trade)

Dispatch order in `src/execution/signal_dispatch.py::_one_user` — silent-skip
gates **before** any dispatch_log row: mode → tier entitlement (B16,
`AUTO_TRADE_TIER_GATE_ENABLED=true`, fail-closed, read-time `paid_until`
downgrade) → auto-pause → path preference → regime preference. The app's
runtime-status endpoint mirrors the *full* conjunction since #736 (armed card
can no longer lie).

| Component | Module | Key invariants |
|---|---|---|
| Position FSM | `execution/position_fsm.py` | Entry MARKET; profit legs REDUCE-ONLY LIMIT; SL MARKET. Default profile **D: TP1-full** (`TP1_CLOSE_FRACTION=1.0`, pre-TP off, invalidation loose). Naked-position invariant: SL placement failure → force-close. |
| Position worker | `execution/position_worker.py` | User Data Stream, sub-100 ms transitions; boot dedup (#730) |
| Pre-TP dispatcher | `execution/pretp_dispatcher.py` | opt-in only (`PRE_TP_ENABLED=false`); generation-gated cache (the ₹4,552 lesson); all three failure paths share `_protect_residual_final` (#730) |
| Funding exit watcher | `execution/funding_exit_watcher.py` | re-fire suppression post-close (#730) |
| Reconciler | `execution/reconciler.py` | 60 s diff; force-close > 2 h; **order-side healing re-places lost stops** (algoOpenOrders-aware, #730) |
| Tripwires / breakers | `execution/tripwires.py` | **wired live since #730**; only `OrderPlacementError` counts; `-2019`, `-4411` excluded (`_BINANCE_USER_SETUP_CODES`, #740); per-user trip → disable_user, global trip → kill switch |
| Kill switch | `execution/kill_switch.py` | owner-only disengage; ops Control is the operator surface |
| Manual take | `execution/manual_take.py` + `api/take_signal_route.py` | **DARK — `AUTO_TRADE_MANUAL_TAKE_ENABLED=false`**, awaiting owner `.env` activation. Redis BRPOP consumer, `(uid, signal_id)` dup guard fails closed, stale-envelope refusal > 60 s, tier gate at `can_assist`. Signals only (alerts lack SL/TP geometry — B7 follow-up). |
| Signing service | `security/signing_service/` | separate container, Unix socket; only place plaintext secret exists |
| Key custody | `security/firestore_keystore.py`, `security/kms_client.py`, `security/binance_connect_validator.py` | KMS envelope encryption; connect-time: withdraw-permission auto-reject, Futures required, VPS IP whitelist; 30 s read cache. Connect is never tier-gated (owner rule, S61). |
| Billing truth | `api/billing_play.py`, `api/play_purchases.py` | Play `purchaseToken` verify + acknowledge + RTDN; `UserStore.tier` + `paid_until` = entitlement source of truth |

### 2.4 API surface (57 routes, FastAPI, three-credential auth)

Auth: static owner Bearer (`API_AUTH_TOKEN`) → Firebase ID token → legacy HS256
JWT (transition window). Grouped:

- **Auth:** `/api/auth/{anonymous,refresh,request-otp,verify-otp,telegram-otp/{issue,verify}}`
- **Feed/read:** `/api/{pulse,pulse/tickers,signals,signals/{id},alerts,agents,pairs,positions,trades,activity,profile,account,health,tunables,region,signal-expiry}`
- **Auto-trade:** `/api/auto-trade/{take,positions,recent-events,runtime-status,user-status}`, `/api/auto-mode{,/resume-mine,/paper/*}`, `/api/auto-trade-global`, `/api/kill-switch`
- **Settings:** `/api/settings/{auto-trade,pretp,user/auto-trade,user/invalidation,user/pretp,user/symbol-management}`
- **Billing:** `/api/billing/play/{verify,enabled,rtdn,rtdn/{secret}}`, `/internal/billing/grant`
- **Keys:** `/api/binance/connect{,/info,/status}`
- **Admin/diag:** `/api/admin/{grant-tier,reset-signals,users/lookup}`, `/internal/diag/{positions,position_counters,tasks}`, `/api/{referral/*,pnl/history}`

### 2.5 Measurement & self-defence layer (all live-ON)

| Feature | Module | Flag (default) |
|---|---|---|
| Fail-open telemetry | `src/fail_open.py` | always on — every data-path `except` records |
| Feature-liveness watchdog | `src/feature_liveness.py` | `FEATURE_LIVENESS_ENABLED=true` — 10 probes, pages via `vps-liveness.yml` → Telegram + auto-detected issue |
| Suppression audit + shadow ledger | `src/suppression_audit.py` | `SUPPRESSION_AUDIT_ENABLED=true` |
| Strategy×context edge matrix | `src/strategy_edge.py` | on; one save/cycle via `to_thread` (post-S55) |
| Shadow strategy units | `src/shadow_strategies.py` | `SHADOW_STRATEGIES_ENABLED=true` (MEAN_REVERT control arm) |
| Stop-geometry A/B | `src/geometry_ab.py` | `GEOMETRY_AB_ENABLED=true` (observe-only; ATR leads 5/6) |
| `@TUNED` shadow variants | `src/tuned_variants.py` | `TUNED_VARIANTS_ENABLED=true` (MAS + VSB arms, observe-only) |
| Market context / allocator | `src/market_context.py`, `src/strategy_allocator.py` | on (`ALLOCATOR_RECOMMEND_ENABLED=true`, recommend-only) |
| Truth report | `src/runtime_truth_report.py` + `scripts/build_truth_report.py` | `monitor-logs` branch, cumulative counters |
| Invalidation audit | `src/invalidation_audit.py` | PROTECTIVE/PREMATURE/NEUTRAL classes |
| Dark-flag shadow telemetry | — | `DARK_FLAG_SHADOW_TELEMETRY=true` |

### 2.6 Flag register (money-path relevant, code-verified defaults)

**Dark / default-OFF (awaiting data or owner activation):**
`AUTO_TRADE_MANUAL_TAKE_ENABLED=false` (owner activation pending) ·
`BTC_DIR_PENALTY_APPLY=false` (shadow-logging) ·
`PRE_TP_ENABLED=false` (per-user opt-in only, B17) ·
`INVALIDATION_BTC_CORRELATION_ENABLED=false` ·
`BTC_STATE_HAIRCUT_ENABLED=false` · `FSM_LIMIT_ENTRY_ENABLED=false` ·
`SIGNAL_EXPIRY_ENABLED=false` (verify VPS env vs B9 expiry-notification rule) ·
`SR_FLIP_LONG_ENABLED=false` · `SR_FLIP_MOMENTUM_GRACE_ENABLED=false` ·
`SR_FLIP_PRETP_R_SCALING_ENABLED=false` · `LSR_PRETP_R_SCALING_ENABLED=false` ·
`LSR_SL_TIGHTEN_ENABLED=false` · `CONFIDENCE_LOG_ENABLED=false`

**Zombie-by-flag (one env flip from live — KEEP per S59):**
`CORNIX_FORMAT_ENABLED=false` · `FEEDBACK_LOOP_ENABLED=false`

**Live-ON gates of note:** `AUTO_TRADE_TIER_GATE_ENABLED=true` (fail-closed) ·
`MEAN_REVERT_LIVE=true` (runtime tunable = instant off-switch) ·
`MOVER_*_ENABLED=true` family · `CT_LONG/SHORT_MACRO_GATE_ENABLED=true` ·
`NOISE_FLOOR_STOPS_ENABLED=true` · `COHORT_EDGE_GATE_ENABLED=true` ·
`LOSS_STREAK_ESCALATION_ENABLED=true` · `ACTIVE_DUP_GUARD_ENABLED=true` ·
`MTF_DOCTRINE_BYPASS_ENABLED=true` · `MTF_LONGS_REGIME_GATE_ENABLED=true`

### 2.7 Dead-code register (S59 owner decision: REPORT ONLY, unchanged)

Zero live importers: `src/scanner_core.py`, `src/cvd.py`, `src/macro_blackout.py`,
`src/pair_analysis_report.py` + `src/pair_anomaly_detector.py`, `src/simulation/`,
config `OPENAI_MIN_CONFIDENCE_THRESHOLD` / `OPENAI_HOT_PATH_BYPASS_CHANNELS`,
zombie radar wiring (`on_radar_candidate` handler unreachable).
Reserved enum values: `RANGE_REJECTION`, `EXHAUSTION_FADE` (unemitted).

---

## 3. Lumin app (`lumin-app`) — implementation map

**Boot:** edge-to-edge UI → Firebase init → legacy-JWT cleanup →
`NotificationService.init` (never throws) → `AppConfig.load` (live-by-default
fail-safe) → Welcome → Consent (18+/risk/not-advice, version-bump re-show) →
Firebase phone-OTP `AuthGate` (+ `EngineMetadataStore` hydration, #126) →
`RegionGate` (soft-fail-open) → `NavShell`.

| Area | Files | Notes |
|---|---|---|
| Repository seam | `data/repository.dart` (`MockRepository`/`HttpRepository`), `data/api_client.dart` | single seam; 401 single-force-refresh, 5xx retry, tolerant older-engine defaults |
| Auth + entitlement | `data/auth_service.dart`, `data/engine_metadata_store.dart`, `data/play_billing_service.dart` | Firebase Auth; entitlement survives restart via per-UID display cache + background `/api/profile` refresh; **engine verdict is the only entitlement truth** |
| Client-side Binance path | `data/binance_client.dart`, `data/binance_keys_service.dart`, `data/order_executor.dart`, `data/order_log.dart` | device-signed HMAC; keys per-user in `flutter_secure_storage` (`binance.user.<id>`), corrupt-blob wipe; engine never sees them |
| Server-side path | `data/server_side_execution_models.dart` | engine-connected key (KMS, IP-whitelisted); server take via `POST /api/auto-trade/take` |
| Error humanizing | `data/take_error_mapper.dart` + `DispatchEventTranslation` | one copy source; `sanitizeEngineDetail` blocks UIDs/engine vocabulary; -4411 → "accept Futures agreement" |
| Tabs | Pulse (`features/pulse/`), Signals (`features/signals/`), Charts (`features/charts/` — WebView + vendored Lightweight Charts, Binance public klines), Trade (`features/trade/` — `LiveStatusCard` + pure `resolveLiveStatus`, per-user feed, Auto/One-tap source tags), Menu (`features/settings/`) |
| Settings pages | auto-trade, pre-TP, invalidation, eligibility/symbol prefs, server-side execution, subscription (CURRENT PLAN + Play manage deep-link), profile, notifications, ToS, about, referral | per-user dials consumed by engine at dispatch |
| Distribution | `app/distribution.dart` — compile-time `LUMIN_DISTRIBUTION` | `sideload` (updater ON) / `play` (updater inert, `REQUEST_INSTALL_PACKAGES` stripped) |
| Updater | `data/update_service.dart`, `features/update/update_banner.dart` | GitHub Releases; silent-failure contract |
| Push | `data/notification_service.dart` | FCM topics `alerts`/`signals`; foreground → SnackBars |
| CI | `.github/workflows/build-apk.yml` | regenerates `android/` via `flutter create` + idempotent patches; R8 full; obfuscated + symbol maps; release-signing verified; APK+AAB attached to auto-release |

**No `android/` directory is checked in — native config changes are edits to
the workflow patch steps.** Tests: 294 (S63 green), mirroring `lib/` under `test/`.

---

## 4. 360 CE Ops (`360ce-ops`) — implementation map

Three deliverables; owner-only; **control plane** for the engine (Telegram
banned in-region).

| Deliverable | Surface | Notes |
|---|---|---|
| Web dashboard + control | `app/` FastAPI+HTMX @ `ops.luminapp.org` | routes: pulse (incl. feature-liveness card), signals + drill-down, positions, invalidations, pairs, performance, profit (free-run + exit-sim), strategy_lab (edge matrix), truth, users, alerts, control (auto-mode flips, kill switch, **Play-billing toggle #65**), diag, data_export, raw_edge, audit_status |
| 24/7 monitoring agent | `app/agent/` (own container, 60 s cycle) | pure-function Tier-0 detectors (naked position, signing down, engine/Redis stale…); Redis-backed alert FSM; pages via FCM (`app/fcm.py` httpx+google-auth, disabled-safe) to `app/device_registry.py`; healthchecks.io heartbeat |
| Native ops mobile app | `mobile/` Flutter over `/api/v1` | ops-issued hashed app-tokens (`app/app_tokens.py`, revoke-all = lost-phone switch); engine owner Bearer never ships in APK; widget-level confirm gates on kill-switch/LIVE |

Control doctrine (verified in routes): owner-gated engine endpoints only,
audited (`app/audit.py`, best-effort), PRG + confirm, engine is source of truth
(read-back after every write), no direct mutation of engine data/Redis/SQLite.
Auth: `OPS_AUTH_TOKEN` password + optional TOTP (`app/totp.py`).
Tests: 378 web + 45 mobile (S63 green). CI: `ci.yml`, `deploy.yml` (~60 s),
`mobile-apk.yml` (scaffolding generated, `mobile/android/` not committed).

---

## 5. Legal (`lumin-legal`)

`privacy.md`, `terms.md` (two-tier B16 model), `risk.md`, `delete-account.md`,
`index.md` → GitHub Pages via `static.yml`. Load-bearing for Play Console +
`lib/data/legal_urls.dart`. Never rename/delete published paths; substantive
changes are owner-sign-off.

---

## 6. Cross-repo contracts

| Contract | Producer → Consumer | Mechanism |
|---|---|---|
| Auth | app → engine | Firebase ID token Bearer (static owner token for ops/CI; legacy HS256 in transition) |
| Entitlement (B16) | Play → engine → app | `purchaseToken` → `/api/billing/play/verify` (+RTDN) → `users.tier`/`paid_until`; dispatch tier gate fail-closed; app renders, never derives |
| Signals feed | engine → app/ops | `/api/signals` (`is_open` is engine truth); JSON models default-tolerant of older engines |
| Per-user exit dials | app → api → engine | `/api/settings/user/*` → SQLite (shared volume, WAL) → fresh SELECT at dispatch |
| Server take | app → api → engine | `POST /api/auto-trade/take` → Redis `snapshot:cmd:take` → `ManualTakeConsumer` (dark flag) |
| Push | engine → app | FCM topics `alerts`/`signals` (no token registry); ops has its own device registry |
| Ops control | ops → engine | owner-gated HTTP endpoints only (kill switch, auto-mode, billing toggle) |
| Monitoring | engine → GitHub → ops | `monitor-logs` branch (truth report), auto-detected issues, feature-liveness manifest |
| Legal | legal → app/Play | fixed GitHub Pages URLs in `legal_urls.dart` + Play listing |

---

## 7. CI/CD & scheduled operations

| Repo | Workflows |
|---|---|
| 360-v2 | `ci.yml` (pytest + coverage summary), `deploy.yml` (main → VPS), `vps-backup.yml` (nightly encrypted; #714 fixed by #725, closed 2026-07-13), `vps-liveness.yml` (hourly probe → Telegram page + auto-detected issue), `vps-monitor.yml` (truth report → monitor-logs) |
| lumin-app | `build-apk.yml` (APK+AAB, release-sign verify, auto-release), `print-fingerprints.yml` |
| 360ce-ops | `ci.yml`, `deploy.yml`, `mobile-apk.yml` |
| lumin-legal | `static.yml` (Pages) |

---

## 8. Current health snapshot (2026-07-17)

- **Runtime:** healthy — heartbeat fresh, circuit breaker healthy, 2–4 open
  signals, pricing sources fresh, paper books consistent (today's probe output,
  #739 thread).
- **Feature liveness:** 10 probes, **1 alerting** (`mean_revert_emission` — F1).
- **Tests (last green, S63):** engine 6,732 · app 294 · ops 378 web + 45 mobile.
  Ruff re-run clean this session; mypy baseline ~102 (don't add).
- **PR queue:** zero open PRs in all four repos; S61–S63 work all merged incl.
  both owner-sign-off items (#736 KMS init, #740 -4411 breaker exclusion).
- **Backups:** nightly encrypted backup healthy since #725.
- **Auto-detected issues open:** exactly one — #739 (F1 below).

---

## 9. Audit findings (this session)

### F1 — HIGH (live, open #739): MEAN_REVERT has never emitted; the S60 fix was necessary but not sufficient

Evidence chain (all code/data-verified today):

1. `mean_revert_emission` probe has paged hourly all day: thousands of
   detections per window, `emitted_total=0` (monotonic — zero emissions ever,
   including ~24 h *after* #732 deployed the execution-gate fade branch, which
   is confirmed present in live `main`).
2. Truth report funnel: `MEAN_REVERT | 15,410 generated | 15,410 gated |
   0 emitted` — and **no MEAN_REVERT row in either confidence table**: every
   candidate dies in the pre-scoring gate chain, never reaching the scorer.
   (So this is *not* the §3.6a mis-scoring class — it's an upstream hard gate.)
3. Two kill sites reject at the `gated` stage with **no reason tag**
   (`_reject("gated", None)` at `scanner/__init__.py:5713` and `:5718`):
   `classify_setup` compat and `execution_quality_check`. The funnel
   classification shows "(none)" — invisible by construction.
4. **Prime structural suspect:** `REGIME_SETUP_COMPATIBILITY`
   (`signal_quality.py`) lists MEAN_REVERT under **CLEAN_RANGE and DIRTY_RANGE
   only** (of six MarketStates). The evaluator's own trigger is a ≥2.5σ 15 m
   over-extension — precisely the move that tends to flip the state classifier
   *out* of the range states (into BREAKOUT_EXPANSION / VOLATILE_UNSUITABLE /
   trend) at classification time. The trigger is anti-correlated with its own
   compat map → a deterministic-in-practice 100 % kill that no execution-gate
   fix can unblock. FUNDING_EXTREME (172/214 gated, 0 emitted) and
   LIQUIDATION_REVERSAL (32/32) show the same signature and share the same
   range-heavy compat rows — worth reading in the same window.

**Recommended sequence (not implemented in this session — money path):**
1. Ship reason-tagged funnel telemetry for the two silent `gated` rejects
   (which gate + `MarketState` at rejection). Off money path — ships normally.
2. Read one real VPS window to confirm the compat-map hypothesis (vs residual
   execution-gate misses).
3. If confirmed: the fix is a compat-map extension (or a MarketState-aware
   exemption for statistical setups whose trigger *is* the dislocation). That
   changes which signals emit → **dark-first + owner sign-off** per Project
   Phase. The shadow control arm (SHADOW_MEAN_REVERT, +0.63R KEEP, n=156
   rollup) remains the measuring stick for what the gate chain is costing.

### F2 — MEDIUM (telemetry gap): `gated`-stage rejects are reasonless
**[IMPLEMENTED 2026-07-18, same branch]**

The exact gap that delayed F1's diagnosis: setup-compat and execution-quality
rejections log at DEBUG and increment a reasonless funnel counter. Every other
rejection layer (evaluator no-signal reasons, MTF, confidence, soft penalties,
suppression audit) is reason-tagged. Closing this is the step-1 fix in F1 and
benefits all 18 paths permanently.
*Shipped:* both kill sites now record `gate_reject:setup_compat:{channel|
regime_<MarketState>}` / `gate_reject:execution:{trigger_not_confirmed|
overextended}` funnel stages; the truth report gained a "Pre-scoring gate
rejects" section naming the MarketState each candidate was rejected under —
one real window after deploy answers F1's compat-map question directly.

### F4 — HIGH (found 2026-07-18, owner screenshots): the documented
`/enable_user` operator verb never existed **[IMPLEMENTED, same branch]**

`kill_switch.enable_user()` had **zero operator-facing callers** — no Telegram
command, no endpoint, no ops surface — despite the S59/S62 runbooks naming
`/enable_user` as the recovery verb. A breaker-tripped paying subscriber
stayed disabled forever ("Paused by a safety check — email support", with
support having no switch). *Shipped:* owner-gated
`POST /api/admin/users/auto-trade-enable` (phone or firebase_uid, enable or
audited manual disable, Firestore read-back), beside `grant-tier`. Ops-UI
button in 360ce-ops is the follow-up.

### F5 — MEDIUM (found 2026-07-18, owner screenshots): "Watching 0 symbols"
— isolated-api allowlist display bug **[IMPLEMENTED, same branch]**

Same container class as the KMS bug (#736): `_load_symbol_allowlist()` in the
api container has no PairManager singleton and the env default is unset, so
`/api/auto-trade/runtime-status` reported an empty allowlist and every armed
user rendered "Watching 0 symbols". Display-only (real gating runs
engine-side). *Shipped:* the route now falls back to the engine-published
pairs snapshot (regular + mover-promoted) with the per-user preference
intersection applied on top; env hard-narrow still wins.

### F3 — LOW (verify on VPS): `SIGNAL_EXPIRY_ENABLED` defaults `false` in code

B9 requires expired signals to post a notification. Expiry handling exists in
TradeMonitor paths; this specific flag's live value on the VPS `.env` should be
confirmed the next time someone is on the box — flagging as a checklist item,
not a defect claim.

### Clean checks (re-verified or confirmed current this session)

Ruff clean on `src/ config/`; no open PRs; no unmerged owner-sign-off items;
backup pipeline healthy; breakers wired (post-#730) with -2019/-4411 exclusions
(post-#740); KMS initialised in both entry points (post-#736); entitlement
persistence + status truthfulness shipped (post-#126/#736); dead-code register
unchanged from S59 (report-only stands).

---

## 10. Outstanding owner actions (carried, still open)

1. **#739 / F1** — approve the telemetry step (ships normally), then the
   compat-map decision after a measured window (dark-first + sign-off).
2. **VPS runbook (S61)** — confirm which silent dispatch gate holds the
   owner's primary account (`users.tier` / `paid_until` /
   `user_auto_trade_settings` row), fix via admin grant flow.
3. **-4411 subscriber (S62)** — user accepts Binance Futures TradFi-Perps
   agreement → operator breaker reset + `kill_switch.enable_user(<uid>)`.
4. **Manual take activation** — `AUTO_TRADE_MANUAL_TAKE_ENABLED=true` in VPS
   `.env` + `bash deploy.sh` when ready.
5. **Alert-take server-side** — needs SL/TP geometry-synthesis design (B7,
   owner-sign-off) before the alert sheet can leave the client-side path.
6. **Assist↔Auto proration** — proper `ChangeSubscriptionParam` flow
   (currently routed to Play manage).
7. **Data reads due:** `dispatch_staleness` re-read next window (verdict
   flip-flopping); geometry A/B application design (~1 week more data);
   `@TUNED` MAS/VSB arms vs live rows once samples classify; BTC_DIR shadow
   review → flip `btc_dir_penalty_apply`.
8. **dispatch_log retention policy** — Firestore subcollection grows unbounded
   (~500 KB/user/day; free-tier today).
