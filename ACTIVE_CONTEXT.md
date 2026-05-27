# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## In-session checkpoint 2026-05-26 (session 6) — 9-PR roadmap COMPLETE (C pending sign-off)

### Status

All non-sign-off roadmap PRs shipped and merged. Full audit:

| PR | Title | PR # | Status |
|---|---|---|---|
| **A** | Wire Reconciler as asyncio task + worker_manager register/unregister | #505 | ✅ merged |
| **B** | Enforce per-user position cap at order placement | #504 | ✅ merged |
| **C** | Pre-TP as native Binance LIMIT at dispatch (FSM transition) | — | ⏳ awaiting owner sign-off |
| **D** | Wire MarkPriceFeed + PretpDispatcher as live asyncio tasks | #506 | ✅ merged |
| **E** | Per-user grab fraction end-to-end | — | ✅ verified already wired |
| **F** | Per-user pre-TP regime + setup allowlists at dispatch | #508 | ✅ merged |
| **G** | Per-user invalidation mode stored on Position at dispatch | #509 | ✅ merged |
| **H** | Trade tab: per-user live Firestore positions | — | ✅ verified already implemented |
| **I** | Separate per-user Recent Activity from engine-wide signals | — | ✅ verified already implemented |

### What PR-F wired (merged #508)

`resolve_pretp_allowlists_uid()` added to `user_overrides.py`. `_one_user()` in `signal_dispatch` resolves the user's `user_pretp_settings.regime_allowlist` + `setup_allowlist`. If signal's regime or setup_class isn't in the user's allowlist, `user_grab_fraction` is zeroed → `pretp_controller` returns qty=0 → pre-TP marked SKIPPED. Position still opens with SL/TP. `dispatch_signal_to_active_users` extended with `regime_label` and `setup_class` params; `signal_router.py` passes `signal.entry_regime` / `signal.setup_class`.

### What PR-G wired (merged #509)

`resolve_invalidation_mode_uid()` added to `user_overrides.py`. Reads `user_invalidation_settings.mode` (loose/standard/tight) per firebase_uid. `_one_user()` resolves per-user mode and passes `invalidation_mode=user_invalidation_mode` to `place_signal()`. Stored on `Position.invalidation_mode` (persisted to Firestore). Enforcement scope: `trade_monitor._check_invalidation()` remains engine-wide today (Signal book has no per-user uid context). The per-user mode on Position is the data plumbing for when per-user soft-invalidation enforcement lands.

### PR-H / PR-I — verified already implemented

Inspection of `lumin-app/lib/features/trade/trade_page.dart` confirms the Live tab already renders:
- `_ServerPositionsCard` sourced from `watchAutoTradePositions()` → `GET /api/auto-trade/positions` (per-user, Firestore-backed)
- `_RecentDispatchEventsCard` sourced from `watchRecentDispatchEvents()` → `GET /api/auto-trade/recent-events` (per-user, dispatch_log)
- `_ActivityCard` sourced from `data.activity` (engine-wide signal stream) — distinct from per-user dispatch events

The separation is clean. Both per-user surfaces are gated on `hasBinanceKey` (only shown once the user has connected a key). No code change needed.

### Only remaining item: PR-C (owner sign-off)

**PR-C (pre-TP native LIMIT):** replace the current 5s-poll + MARKET-chase approach with a REDUCE_ONLY LIMIT order placed at `pre_tp_trigger_price` at `place_signal()` time alongside SL and TP orders. Binance holds it passively; fill arrives via User Data Stream; FSM `_apply_pretp_fill()` handles it. Zero poll lag, maker pricing, works during engine downtime, fully per-user by construction.

Requires owner sign-off per CLAUDE.md (FSM transition change). Ping owner to approve or reject.

**Pre-existing test failure (unrelated to our PRs):**
`tests/test_websocket_and_formatting.py::TestHealthCheckLoopForceClose::test_force_close_after_threshold_window` — was failing on `c3411a4` (pre-session main); not caused by our changes.

---

## In-session checkpoint 2026-05-26 (session 5) — PRs A/B/D merged; roadmap continuing

### Status

Three execution-completeness PRs shipped and merged this session:

| PR | Title | Status |
|---|---|---|
| #505 (PR-A) | Wire Reconciler as asyncio task + register/unregister in worker_manager | **merged** |
| #504 (PR-B) | Enforce per-user position cap at order placement | **merged** |
| #506 (PR-D) | Wire MarkPriceFeed + PretpDispatcher as live asyncio tasks | **merged** |

**What's now live (previously broken):**
- Reconciler runs as a 60s-interval asyncio task; `register_user` / `unregister_user` called by worker_manager on worker start/stop. Manual Binance closes now detected within 60s.
- MarkPriceFeed runs as a public WS task (`!markPrice@arr@1s`); PretpDispatcher wired to it. FSM calls `track(symbol)` on OPEN transition, `untrack(symbol)` on all CLOSED transitions. Mark-price-driven pre-TP now active.
- Position cap (`assert_position_cap`) enforced at dispatch time in `signal_dispatch._one_user()`. Cap exceeded → `PositionCapExceeded` recorded in dispatch log.

**Verified already wired (PR-E investigation):**
- Per-user grab fraction: `signal_dispatch._one_user()` calls `resolve_grab_fraction_uid(uid)` → stored in `Position.pretp_fraction` → `pretp_controller` reads it per tick. End-to-end complete, no change needed.

### Remaining roadmap

| PR | Phase | Title | Sign-off? | Status |
|---|---|---|---|---|
| **C** | Pre-TP arch | Pre-TP as native Binance LIMIT at dispatch | **Yes — FSM transition** | Awaiting owner sign-off |
| **F** | Settings | Wire per-user pre-TP regime + setup allowlists at dispatch | No | Next |
| **G** | Settings | Wire per-user invalidation mode (loose/standard/tight) | No | After F |
| **H** | App display | Trade tab: per-user live positions from Firestore | No | lumin-app repo |
| **I** | App display | Separate per-user Recent Activity from engine-wide signals | No | lumin-app repo |

**Pre-existing test failure (unrelated to our PRs):**
`tests/test_websocket_and_formatting.py::TestHealthCheckLoopForceClose::test_force_close_after_threshold_window` — was failing on `c3411a4` (pre-session main); not caused by our changes.

---

## In-session checkpoint 2026-05-26 (session 4) — Execution completeness audit + 9-PR roadmap

### What triggered this

Deep audit of both repos was requested after owner observed pre-TP not firing on ZEREBRO SHORT at +0.51–0.60%. Investigation revealed the pre-TP miss was a symptom of a much broader gap: the entire server-side execution stack has a large class of components that are **built but not wired** and **per-user settings that are stored but never read**.

### Audit summary — built but not wired

| Component | File | Gap |
|---|---|---|
| **Reconciler** | `src/execution/reconciler.py` | Instantiated in main.py but never started as an asyncio task. `register_user` / `unregister_user` never called by worker_manager. Manual Binance closes undetected at runtime. |
| **MarkPriceFeed** | `src/execution/mark_price_feed.py` | Fully implemented, never instantiated. Pre-TP fires from 5s candle poll only. |
| **PretpDispatcher** | `src/execution/pretp_dispatcher.py` | Fully implemented, never instantiated. Tick-driven pre-TP entirely dead code. |
| **Position cap** | `src/execution/tripwires.py` | `assert_position_cap()` defined, zero callsites in the execution path. $500 default works as soft cap by accident, not enforcement. |

### Audit summary — per-user settings stored but engine ignores

| Setting | Stored | Consumed |
|---|---|---|
| Pre-TP grab fraction (app slider → `user_pretp_settings`) | ✅ SQLite | ❌ TradeMonitor path uses engine-wide config constant. FSM path uses `pos.pretp_fraction` from `resolve_grab_fraction_uid()` — source table needs verification. |
| Pre-TP regime allowlist | ✅ SQLite | ❌ Engine reads engine-wide JSON config |
| Pre-TP setup allowlist | ✅ SQLite | ❌ Never read anywhere in codebase |
| Pre-TP protect_manual_entries | ✅ SQLite | ❌ No read path exists anywhere |
| Invalidation mode (loose/standard/tight) | ✅ SQLite | ❌ Engine uses `INVALIDATION_MODE_DEFAULT` for all users |
| Invalidation advanced knobs | ✅ SQLite | ❌ Never read |

### Audit summary — app display gaps

| Display | Actual source | Gap |
|---|---|---|
| Trade tab open positions | Engine-wide paper book | Per-user live Binance positions not shown |
| Signal PnL (+0.41%) | `(mark_price − signal_entry) / signal_entry` | Not per-user fill price; two users with different slippage see identical % |
| Recent Activity | Engine-wide signals + per-user dispatch events, conflated | No clear separation in UI |

### Pre-TP architecture finding (separate from wiring gaps)

The current approach — poll 5s → detect via 1m candle → place MARKET — has three compounding problems on fast movers:
1. Up to 5s poll lag (window closed before detection)
2. Candle-based detection (up to 1 full candle behind mark price)
3. MARKET order chases thin books (slippage on ZEREBRO-class pairs)

**Better approach (design approved this session):** place a REDUCE_ONLY LIMIT order at `pre_tp_trigger_price` at signal dispatch time, alongside the SL and TP orders. Binance holds it passively. Fill arrives via User Data Stream (already wired per-user). FSM `_apply_pretp_fill()` handler already exists and handles it. Zero poll lag, maker pricing, works during engine downtime, fully per-user by construction.

This requires owner sign-off (FSM transition change, per CLAUDE.md).

### 9-PR roadmap

| PR | Phase | Title | Sign-off? | Status |
|---|---|---|---|---|
| **A** | Safety | Wire reconciler: bootstrap task + worker_manager register/unregister | No | ✅ merged #505 |
| **B** | Safety | Enforce per-user position cap at order placement | No | ✅ merged #504 |
| **C** | Pre-TP arch | Pre-TP as native Binance LIMIT at dispatch | **Yes** | Awaiting sign-off |
| **D** | Pre-TP arch | Wire MarkPriceFeed + PretpDispatcher | No | ✅ merged #506 |
| **E** | Settings | Grab fraction end-to-end | No | ✅ already wired |
| **F** | Settings | Wire per-user pre-TP regime + setup allowlists | No | Next |
| **G** | Settings | Wire per-user invalidation mode (loose/standard/tight) | No | Queued |
| **H** | App display | Trade tab: per-user live Firestore positions | No | lumin-app |
| **I** | App display | Per-user Recent Activity vs engine-wide signals | No | lumin-app |

### Owner decision needed

**PR C (pre-TP native LIMIT):** approve the FSM change? The key question is: at `place_signal()` time, should the FSM also place a REDUCE_ONLY LIMIT order at the pre-TP threshold price for `qty × pretp_fraction`? This replaces the current 5s-poll + MARKET-chase path for all FSM (server-side auto-trade) users.

---

## In-session checkpoint 2026-05-26 (session 3) — EIGENUSDT SL silent-skip root cause fixed (PR #500)

### Incident

EIGENUSDT LONG signal sat at −3.30% for 35+ minutes with no SL action. Owner-reported screenshot; diagnosed and fixed in this session.

### Root cause (two compounding guards)

1. **`_candle_extremes` returning (0, 0)** when no 1m candle data existed for the symbol. The existing guard `if _c_low > 0` correctly blocked false-positive SL triggers on missing data, but also silently skipped the entire SL check — leaving the signal unprotected when candle data was unavailable.

2. **`indicators is None` early return in `_check_invalidation` placed BEFORE the adverse-excursion block.** When `get_indicators()` returned `None` (which also happens when candle data is absent), the function returned `None` immediately — silently skipping adverse-excursion invalidation that only needs `sig.current_price` to function.

Together: no candle data → both the SL check and the adverse-excursion check silently no-op → signal can slide indefinitely past SL with no action.

### Fix (PR #500 — merged)

Three changes to `src/trade_monitor.py`:

1. **Adverse-excursion block moved before `if indicators is None: return None`** — now fires even when candle data is absent, using only `sig.current_price`.
2. **Mark-price SL backstop** added: when `_c_low <= 0 or _c_high <= 0` (no candle data), SL is checked directly against `sig.current_price` (mark price). Logs a WARNING to make the fallback path visible in prod logs.
3. **TP3 rounding residual routed to TP2** (bug found during testing): even with `_TP3_FRACTION=0.00`, the LOT_SIZE floor residual (e.g. 0.001 BTC) was going into `tp3`, causing the FSM to place a spurious TP3 order. Fixed in `_compute_qty_split`: residual now goes to `tp2` when `_TP3_FRACTION <= 0.0`.

### Tests updated

- `test_binance_fetch_failure_skips_cycle` — updated from asserting old broken behavior (`len(persisted) == 1`) to correct behavior (`len(persisted) == 0`).
- `test_qty_split_at_typical_btc_price` — TP2 fraction assertion updated 0.40 → 0.70; added `assert tp3 == 0.0`.
- `test_tp_min_notional_no_consolidation_for_large_positions` — updated to assert `tp3 == 0.0`.
- `test_scalp_signal_below_180s_not_triggered` — renamed to `test_scalp_signal_below_min_lifespan_not_triggered`; age changed 100s → 10s (360_SCALP actual min lifespan is 30s, not 180s as test originally assumed).

### PRs shipped this session

| PR | Repo | Subject | Status |
|---|---|---|---|
| #500 | 360-v2 | fix(trade_monitor): SL/invalidation silent skip when candle data missing — EIGENUSDT −3.30% root cause | **merged** |

### PRs still open from prior sessions

| PR | Repo | Subject | Status |
|---|---|---|---|
| #498 | 360-v2 | P1: reconciler returns None on Binance error; mark-price dispatch task GC fix; deprecated `get_event_loop()`; kill-switch cache race | **open** |
| #76 | lumin-app | P1: mounted guard in delete-account controller; mounted guard in TradePage._resubscribe; `_livePrices` cleared on filter change | **open** |

### Next-session queue

- Merge PR #498 (engine stability) and PR #76 (app crash fixes)
- Monitor post-deployment: verify EIGENUSDT signal (or similar zero-candle-data case) is closed within next 5s poll cycle after PR #500 deployment
- Reconciler order-divergence detection (P2 — audit flag from PR #498 work): FSM doesn't detect externally-cancelled SL/TP orders ("Order in FSM but not in Binance → cancelled externally; clear the order id" — docstring promise, never implemented)
- Pull next truth-report window to validate TP2-only exit structure after TP3 removal

---

## In-session checkpoint 2026-05-26 (session 2) — Pre-launch stability sweep + TP3 removal

### Direction

Owner directive: remove TP3, concentrate on stability for public launch (14-day testing window underway). Exit structure is now: **pre-TP** (30–50%) → **TP1** (30%) → **TP2** (70% of remainder). No TP3.

### PRs shipped this session

| PR | Repo | Subject | Status |
|---|---|---|---|
| #497 | 360-v2 | TP3 removed: `_TP3_FRACTION=0.00`, `_TP2_FRACTION=0.70`; FSM guard skips zero-qty leg | merged |
| #496 | 360-v2 | Three pre-launch stability bugs: `self._telegram` AttributeError in signal_router; `get_event_loop()` + silent task failure in worker_manager; unguarded `put_position` in position_fsm | merged |
| #75 | lumin-app | TextEditingController leak in auto_trade_settings_page; remove chart placeholder from signal detail | merged |
| #498 | 360-v2 | P1: reconciler empty-dict marks all positions CLOSED on Binance error; P1: mark-price dispatch tasks GC'd before completion; deprecated `get_event_loop()` in circuit_breaker + signal_router; kill-switch cache invalidation race | **open** |
| #76 | lumin-app | P1: mounted guard in delete-confirmation controller listener; defensive mounted guard in TradePage._resubscribe; _livePrices map cleared on filter change | **open** |

### Engine bugs fixed (P1)

**reconciler.py — all positions marked CLOSED on Binance error (P1)**
`_fetch_binance_positions` returned `{}` on any error (network, 429, 503). `_diff_and_heal` treated `{}` as "user has no open positions" → every non-terminal FSM position transitioned to `CLOSED` / reason=MANUAL. A single network blip during the 60s reconcile cycle orphaned every user's positions. Fixed: return `None` on error; `reconcile_user` skips the diff when `None`.

**mark_price_feed.py — dispatch tasks GC'd before completion (P1)**
`asyncio.create_task()` without holding a reference registers the task only in the event loop's WeakSet. Python docs: "Save a reference to create_task result to avoid a task disappearing mid-execution." Slow Firestore subscribers (~200ms) could be cancelled before completing the pre-TP threshold check. Fixed: module-level `_background_tasks` set with `done_callback` self-removal.

### Engine bugs fixed (P2)

**circuit_breaker.py, signal_router.py — `asyncio.get_event_loop()` deprecated**
Deprecated in Python 3.10; raises RuntimeError in 3.12 inside a running loop. Changed to `asyncio.get_running_loop()` with RuntimeError catch.

**kill_switch.py — cache invalidated after Firestore write**
~100ms window between Firestore write and cache invalidation allowed concurrent readers to observe stale "not engaged" state after the kill switch was flipped. Cache now invalidated under lock BEFORE the Firestore write.

### App bugs fixed

**settings_page.dart** — `setState` in TextEditingController listener without mounted check → crash if dialog dismissed while typing.

**trade_page.dart** — `_resubscribe()` called `setState` without mounted guard.

**signals_page.dart** — `_livePrices` map accumulated stale symbols across filter switches without pruning. Fixed: map cleared in `_setFilter()`.

### Next-session queue

- Merge and validate PRs #498 (engine) and #76 (app) in prod
- Pull next truth-report window to validate TP2-only exit structure: check if any signals that previously would have reached TP3 are now captured by TP2 (expected: TP2 absorbs the tail cleanly)
- Consider whether the post-pre-TP residual gap warrants an explicit TP2 order for the 20% residual (currently protected only by BE-SL + invalidation)
- Continue reconciler order-divergence detection (PR #498 audit flag P2: FSM doesn't detect externally-cancelled SL/TP orders)

---

## In-session checkpoint 2026-05-26 — Grab fraction wiring + FET pre-TP close fix + invalidation tightening

Three PRs shipped this session, all merged.

### PRs shipped

| PR | Subject | Status |
|---|---|---|
| #490 | Tighten invalidation gates + SL cap: `360_SCALP` min age 600→120s, adverse-excursion fraction 0.70→0.55, min-age 600→120s, default mode standard→tight, SL cap 1.20→1.00 across all 8 evaluators | merged |
| #491 | Fix FET pre-TP close gap: FSM partial close path wired into `trade_monitor._check_pre_tp_grab`; LOT_SIZE rounding via `round_qty`; MIN_NOTIONAL guard with full-position fallback for small wallets ($10 USDT) | merged |
| #493 | Wire per-user grab fraction into FSM pre-TP partial close: `resolve_grab_fraction_uid()` added; `place_signal()` now stamps `pos.pretp_fraction` from user's Firestore setting at entry time; `close_fsm_partial_for_signal()` uses `pos.pretp_fraction` instead of engine config constant | merged |

### What was broken (grab fraction — PR #493)

The Pre-TP grab fraction slider in the app (`PUT /api/settings/user/pretp → grab_fraction`) was stored in `user_pretp_settings` but never read by the FSM execution path. Every user got 50% (engine default `PRE_TP_GRAB_FRACTION`) regardless of their slider value. Three-layer fix:

1. Added `resolve_grab_fraction_uid(firebase_uid, default)` to `src/api/user_overrides.py` — same soft-fail pattern as `resolve_notional_usd`, clamped to B17 [0.30, 1.00]
2. `signal_dispatch._dispatch_one_user()` now fetches grab fraction before `place_signal()` → stamps `position.pretp_fraction` with the user's configured value
3. `close_fsm_partial_for_signal()` uses `pos.pretp_fraction` (per-position) instead of the caller's engine-config `fraction`

### What was broken (FET pre-TP — PR #491)

Three-layer failure for 10 USDT positions:
- CCXT `close_partial` was a no-op for FSM users (not tracked in `_open_quantities`)
- FSM path not wired into `trade_monitor._check_pre_tp_grab` at all
- MIN_NOTIONAL: 50% of 10 USDT FET = ~$4.80 < $5 Binance floor → -4164

All three fixed: FSM close path added; LOT_SIZE rounding via `round_qty()`; MIN_NOTIONAL guard upgrades to full-position close when partial fails the floor.

### Test suite state

5145 passed, 63 skipped, 49 xfailed after all three PRs.

### Next-session queue

- Monitor pre-TP execution in prod: verify grab fraction slider at 100% actually closes full position on next signal
- Validate invalidation tightening (PR #490) against next truth-report window: PREMATURE rate should not exceed ~25% of kills; if it does, raise `INVALIDATION_ADVERSE_EXCURSION_FRACTION` back toward 0.65
- Open PRs from prior sessions: check status of any carry-over items from 2026-05-23 session

---

## In-session checkpoint 2026-05-23 — Truth-report deep-dive → 3 PRs shipped (signal scoring + per-user paper view)

Two-cycle work driven by the 2026-05-23 per-signal audit on the last 100 closed signals plus a bug report on paper-mode visibility.

### Audit findings (per-signal, 100 closed signals over 19.6h)

- **Only 1/100 hit TP1.** 18.9% reached TP1-distance MFE but exited via pre-TP grab or invalidation. 9 signals expired in profit at avg +1.39% — would have been TP wins if TP1 distance was closer.
- **Confidence non-monotonic.** 75-80 confidence band has 64.3% SL rate vs 45% at 65-70 — higher score = worse outcomes (anti-predictive at top end).
- **AI/feedback layer net-negative.** Raised-by-AI cohort (avg +3.4 pts) has 47% SL rate vs 40% flat/lowered.
- **Symbol concentration extreme.** Top-5 winning symbols (FARTCOIN, JTO, FIL, ENA, PLAY) carried +12.19% of net wins — 51% of signal volume, 100% of net positive.
- **Macro context confirms structural compression.** BTC IV at 7-month low; BTC dominance ~60%; "selective bull run" concentrated in narrative sectors.

### PRs shipped this session

| PR | Subject | Status |
|---|---|---|
| #476 | `FEEDBACK_LOOP_ENABLED=false` (default off); QUIET TPs compressed 0.9× → 0.6× via `TP_QUIET_COMPRESSION_FACTOR` | merged |
| #477 | +2pt narrative-pair bonus (FARTCOIN/JTO/FIL/ENA/PLAY); per-symbol regime telemetry in truth report | merged |
| (this PR) | Per-user paper-mode view via subscription windows; fixes fresh-account leak of operator's prior paper trades | open |

### Per-user paper-mode view — bug fix design

**Bug:** Fresh user signs up + enables paper mode → sees operator's prior paper trades. Root cause: `pnl_history.json` and `paper_trades.sqlite` are engine-wide shared state; `PUT /api/settings/user/auto-trade` only wrote a per-user mode preference without isolating visibility.

**Fix shape:** Subscription-windows pattern (rejected alternatives: hard per-user storage duplication, which would scale O(signals × users) without changing the underlying single-engine simulation; user-callable global reset, which would just shift the bug).

- New table `user_paper_subscriptions` (id, user_id, started_at, ended_at) in `user_overrides.py`
- `PUT /api/settings/user/auto-trade` opens a subscription on mode-transition-to-paper; closes on transition-away
- `GET /api/trades` filters the engine ledger by the caller's subscription windows (sum-of-windows semantics)
- New `POST /api/auto-mode/paper/reset-mine` (user-callable, no operator dep) carves a truly fresh window — deletes prior windows so closed-window admit doesn't defeat the "start fresh" promise
- Engine writes unchanged (PaperOrderManager still writes one shared ledger)

**Doctrine alignment:** Phase-2.5 bridge. True per-user portfolio simulation (per-user PaperOrderManager instances with per-user position sizing) is a Phase-3 prerequisite that lands with the per-user FSM workers. The subscription-windows pattern composes cleanly with that future architecture — when each user has their own simulator, the windows become the per-user instance's lifetime.

### Open follow-ups (not in this session)

- Symbol-class taxonomy: heuristic narrative detection (A2) vs newer-listings dampener (D1). Defer until A1 has 1-2 truth-report cycles of measurement.
- Per-user `/api/pnl/history` filtering. Currently `/api/trades` is filtered; `/api/pnl/history` still reads the engine-wide ledger. Same pattern would apply via `pnl_history_for_user` helper already shipped in this PR.
- Phase 3 per-user FSM workers (per server-side execution doctrine).

### Next-cycle validation

Per-signal data should be re-pulled in ~24h to validate this session's changes:
- Avg PnL/signal trending from +0.073% toward +0.20%
- 75-80 confidence SL rate dropping below 60%
- Top-5 narrative pairs hold/grow share of net wins
- `per_symbol_regime_distribution` populated; tokenized stocks (CRCL/MU/INTC/CL/EWY) confirmed 90%+ in QUIET (validates the "no stock-side filter needed" thesis)
- Total signal count stays above 80/24h (subscriber-retention floor)

---

## In-session checkpoint 2026-05-21 — SESSION END (Play Store LIVE in Closed Testing; speed + onboarding polish landed; Firebase Phone Auth fixed)

**App is live.** Lumin is published to the Play Store Closed Testing track at `https://play.google.com/store/apps/details?id=org.luminapp.lumin`. Owner has a working tester opt-in URL; the only block to Production is the 14-day continuous-opt-in clock + 12+ tester count.

### Workstream — Play Store submission execution

Day 2 of the launch arc: yesterday's prep (20 merged PRs from 2026-05-20) was paste-ready; today's job was getting the AAB through the Play Console form pipeline + reacting to each rejection until the submission landed.

| Hurdle | Resolution |
|---|---|
| Financial features declaration triggered UK/EU licensing block when "Cryptocurrency exchange" was ticked | Un-declared crypto-exchange; kept only "Financial advice". Same pattern Cornix / 3Commas use. UK/EU stay open without licensing. |
| Photo / video / audio permissions auto-merged into AAB by transitive Flutter deps (open_filex / permission_handler) | **PR lumin-app #57** — workflow step strips REQUEST_INSTALL_PACKAGES + adds ``tools:node="remove"`` for 6 media permissions on AAB build only. Sideload APK unchanged (in-app updater still works). Resulting AAB ships INTERNET + POST_NOTIFICATIONS only. |
| Play Console refused the REQUEST_INSTALL_PACKAGES declaration form (mandatory YouTube demo video) | Stripped the permission entirely via the same #57 step rather than fight the form. |
| Version code 148 rejected after Internal Testing upload | Empty-commit trigger → build 149 with new version code → uploaded to Closed Testing successfully. |
| Tester instructions field 500-char cap | Rewrote from 1354 → 446 chars. |
| Firebase Phone Auth: "Invalid app info in play_integrity_token" on Play install | Play re-signs uploaded AABs with its own key; Firebase had only the upload-key SHA. Added **Play app-signing SHA-1 + SHA-256** to Firebase Console (4 fingerprints total now). Owner pasted; propagation ~5-10 min. |

### Workstream — perceived-latency optimisation

Owner-flagged that the app felt laggy compared to Binance/Telegram, particularly for Indian users hitting the EU VPS (~250-400ms RTT). Two-front fix:

| Layer | PR / change | Effect |
|---|---|---|
| Server | Cloudflare CDN in front of api.luminapp.org (free tier, proxied A record, SSL/TLS Full mode) | Cuts API RTT from ~400ms to ~50ms for Indian users via the Mumbai edge. Verified live (`country_code: IN`, `source: cf-header`). |
| App | **PR lumin-app #58** — SWR cache prewarm on sign-in | Fires PulseBundle + TradeEngineSnapshot + RegionInfo fetches in microtasks the moment the user becomes authenticated. First tab switch after sign-in renders synchronously from cache instead of waiting on a cold network round-trip. |

The bigger geographic win — moving the VPS from Europe to Mumbai/Bangalore — is queued but not blocking; Cloudflare absorbs the worst of the latency in the meantime.

### Workstream — onboarding polish (owner feedback)

| Layer | PR / change |
|---|---|
| App | **PR lumin-app #59** — three-stage first-run flow: WelcomePage (brand intro + value-prop + Get Started) → WelcomeConsentPage (3-checkbox legal ack, unchanged) → AuthGate. Welcome is one-shot per device; consent re-shows on version bump. Doctrine pinned in tests: a consent-version bump must NOT re-show welcome. |
| App | Phone signin page copy: "Sign in" → "Sign in or sign up" + clarified subtitle. Same Firebase Phone OTP flow handles both new + returning users; the copy now matches the mechanics. |

### Adjacent infrastructure shipped (this session)

* **mkmk749278/lumin-legal** GitHub Pages now live at `https://mkmk749278.github.io/lumin-legal/{privacy,terms,risk,delete-account}`. Workflow switched from Static HTML → Deploy from a branch so Jekyll renders the markdown into proper HTML. Linked from the Play Console listing.
* Cloudflare DNS / SSL / proxied A record live for api.luminapp.org. Owner manages the zone.

### Owner remaining workload to v1 Production

1. Wait ~5-10 min for the Firebase SHA propagation; retry phone OTP from the Play install to confirm the auth fix.
2. Once CI builds 150 (auto-triggered by #59 merge), download the AAB from Actions artifacts and upload as a new release on the Closed Testing track. Release notes (under 500 chars): "Smoother first launch: new welcome page with feature overview; clearer 'sign in or sign up' flow; faster tab switches after sign-in (background cache prewarm); cleaner permission footprint — only network + notifications."
3. Recruit 12+ testers via personal network + r/AlphaAndBetaUsers + Telegram tester-swap groups (templates in `docs/PLAYSTORE_TESTER_RECRUITMENT.md`).
4. 14-day continuous-opt-in clock starts when the 12th tester opts in (mandatory for post Nov-2023 personal accounts; not skippable).
5. Promote to Production → 3-7 day Google review → live worldwide.

### Decision queue for next session

* Truth-report 2026-05-21+ validation of: (a) DIV_CONT misalign-penalty enrolment expansion candidates (TPE / CLS / PDC / SR_FLIP / QCB), (b) adverse-excursion EV trajectory.
* Closed Testing first-tester opt-in metrics — count + conversion rate from DM'd candidates.
* App build 150 verification: install fresh from Play, confirm welcome page → consent → phone OTP → main shell works end-to-end on the Play-signed AAB.
* Decision on VPS migration EU → Mumbai/Bangalore once tester traffic gives a real latency baseline (Cloudflare buys time; migration is the structural fix).

---

## In-session checkpoint 2026-05-20 — SESSION END (20 PRs merged: capital-preservation stack + complete Play Store launch prep)

**Massive session.** Two distinct workstreams shipped in parallel: (1) the truth-report Priority-A+B capital-preservation work, (2) the full Play Store launch prep from research → plan → 8 code PRs → 4 paste-ready docs.

### Workstream 1 — Capital preservation (Priority A + B from truth report) — all MERGED

| PR | What | Why |
|---|---|---|
| 360-v2 #461 | Per-user dispatch event log + ``GET /api/auto-trade/recent-events`` | Surface every order-placement attempt to the app so users see *why* a signal didn't open |
| 360-v2 #462 | tzinfo crash fix + 2 pre-existing test fixes | Snapshot API 5xx fix; suite 5025-passing |
| lumin-app #48 | Recent Activity card with plain-English Binance error translations | -2019 / -2014 / -1111 / typed-exception → human text |
| 360-v2 #463 | DIV_CONT structure-misalign penalty (-15 / -10 vs 4h leg) | Priority-A from truth report — 30% SL rate on DIV_CONT closed signals (n=10) |
| 360-v2 #464 | Adverse-excursion invalidation rule (0.70×SL_dist + momentum-not-confirming) | Priority-B — catches the full-SL pattern existing 3 rules miss; saves ~2.4% margin per kill |
| lumin-app #49 | Recent Activity pull-to-refresh wiring fix | Owner-reported "still showing old binance activity" |
| 360-v2 #465 | Per-user notional override (notional_usd column + dispatch wiring) | Owner has $20.50 USD wallet → -2019 on $500 default; can now set $50 |
| lumin-app #50 | Position notional slider on Auto-trade Settings page | App-side for #465 |

### Workstream 2 — Play Store launch prep — all MERGED

| PR | What |
|---|---|
| 360-v2 #466 | Deep research + execution plan (docs/PLAYSTORE_RESEARCH_2026-05-20.md + docs/PLAYSTORE_PLAN.md) — verdict: publishable, ~3 weeks v1 |
| lumin-app #51 | A1+A2 — first-run consent gate (age 18+ + risk + not-advice) |
| lumin-app #52 | A7 — vocabulary audit (dropped iOS reader-app jargon) |
| 360-v2 #467 | E2 — ``GET /api/region`` endpoint with CF-IPCountry header reading + soft-fail open |
| lumin-app #53 | A6 — RegionGate widget wrapping auto-trade entry points |
| 360-v2 #468 | E1 — ``DELETE /api/account`` with orchestrated blob→row→cache flow + typed failure tags |
| lumin-app #54 | A5 — Settings → Legal section (Privacy / ToS / Risk URLs via url_launcher) |
| lumin-app #55 | A4-partial — Settings → Delete account UI with type-DELETE confirmation |
| lumin-app #56 | AAB build pipeline alongside existing APK output |
| 360-v2 #469 | docs/PLAYSTORE_LISTING_COPY.md — every Play Console paste-ready field |
| 360-v2 #470 | docs/PLAYSTORE_VISUAL_ASSETS.md — Canva recipe for icon + feature graphic + 4 screenshots |
| 360-v2 #471 | docs/PLAYSTORE_TESTER_RECRUITMENT.md — Telegram DM templates for 12+ tester recruitment |

### Adjacent infrastructure shipped (owner-side, this session)

* **mkmk749278/lumin-legal** repo created + populated with index.md + privacy.md + terms.md + risk.md (drafted in chat, pasted by owner). GitHub Pages live at https://mkmk749278.github.io/lumin-legal/ via "GitHub Actions" source + Static HTML workflow.
* Owner's personal Play Console account verified (PAN + Aadhaar). Post Nov-2023 → 14-day Closed Testing gate applies.

### Final stats

* **Engine tests:** 5093 passing (was 5025 — +68 new)
* **Lumin tests:** 106 passing (was 79 — +27 new)
* **Engine PRs merged this session:** 11 (#461–#471 minus #463 → 466 sequence: 8 code PRs + 3 docs PRs in 360-v2)
* **Lumin PRs merged this session:** 9 (#48–#56)
* **Total PRs merged:** 20

### Capital-preservation impact stack — now live end-to-end

Four layers working together to keep small-wallet users profitable:

1. **DIV_CONT structure-misalign penalty** (#463) — filters marginal kept-signals against 4h structural leg
2. **Adverse-excursion invalidation** (#464) — exits at 0.70×SL when momentum/regime/EMA all nominally intact but price still grinding to SL
3. **Per-user notional override** (#465) — small wallets size to fit their margin budget
4. **Dispatch event log + Recent Activity card** (#461, #48) — when something does reject, plain-English reason

### Owner remaining workload to v1 Production listing

* Build Canva icon + feature graphic (~30 min) per `docs/PLAYSTORE_VISUAL_ASSETS.md`
* Take 4 phone screenshots (~20 min) per same doc's framing guide
* Play Console paste session (~30 min) using `docs/PLAYSTORE_LISTING_COPY.md` verbatim
* Trigger one lumin-app main push → download AAB from Actions artifacts → upload to Closed Testing
* DM 12+ paid Telegram subscribers using `docs/PLAYSTORE_TESTER_RECRUITMENT.md` templates
* 14-day continuous opt-in wait (mandatory for post Nov-2023 personal accounts)
* Promote to Production + 3-7 day Google review
* **Production live: ~3-4 weeks wall-clock**

### Decision queue for next session

* Validate the misalign-penalty enrolment after one truth-report window (next run 2026-05-21 or similar) — expand from `DIVERGENCE_CONTINUATION` to other in `_STRUCTURE_ALIGN_PATHS` showing same asymmetric-quality pattern (TPE, CLS, PDC, SR_FLIP, QCB)
* Validate adverse-excursion EV after one truth-report window — if PREMATURE > 25% raise `INVALIDATION_ADVERSE_EXCURSION_FRACTION` to 0.80; if < 10% consider tightening to 0.65
* Open queue item dropped earlier: E3 (engine reads lumin-legal URLs for Telegram welcome message) — DEFERRED, the `LegalUrls` constants in lumin-app PR #54 already serve as cross-app source of truth for the launch
* Closed Testing first-tester opt-in metrics — count + diagnose if conversion below ~60% of DM'd candidates

---

## Queued — Play Store Phase 0–3 (decision queued 2026-05-20; SOLO realities applied)

Research + plan PR landing this session. **Build pending owner sign-off** of the solo-operator decision queue at the bottom of `docs/PLAYSTORE_PLAN.md`.

**One-line verdict:** publishable to Play Store by a solo developer with no entity, ~3 weeks for v1 (signals-viewer only) — account already verified ✓ — +2–3 weeks for v2 (auto-execute as feature update). Cornix / 3Commas / Bitsgap / Pionex / WunderTrading all live on Play (entities, but the policy doesn't require entity-based licensing for our launch geos). India NOT on the 15-jurisdiction crypto-custody licensing list.

**Account status (2026-05-20):** owner has a verified personal Play Console account, created ~7–10 days back. Verification step DONE (saves ~3 days off Phase 0). Account is post Nov 13, 2023 → mandatory 14-day Closed Testing gate with 12+ testers applies before Production promotion (NOT skippable).

**KEY STRATEGIC SHIFT — phase the app:**

* **v1 Play submission:** signals-viewer only. No API-key connection, no auto-execute. Purely an information app surfacing the Telegram-channel signals + Recent Activity history. First-attempt Production approval likelihood: ~85–90% (vs. ~50–60% for full auto-execute on day one).
* **v2 feature update:** add API-key connection + auto-execute, ~4–8 weeks after v1 is live + stable. Feature updates get much lighter review than initial submissions.

**Solo realities applied (vs. original ambition plan):**

* **DROPPED:** FIU-IND lawyer engagement (no budget) — accept the regulatory gray area, Cornix precedent applies, launch UK+EU first
* **DROPPED:** Designer for store assets — Canva free tier + GIMP + in-app screenshots
* **SIMPLIFIED:** Legal docs via TermsFeed/FreePrivacyPolicy generators + Claude-drafted custom paragraphs for the API-key + KMS-encryption specifics + Risk Disclosure (Cornix-style, self-written, ~500 words)
* **SIMPLIFIED:** Hosting via GitHub Pages or Vercel free tier — domain nice but not blocking
* **TESTERS:** Owner recruits 12+ from existing paid Telegram subscriber base

**Total owner budget:** ~$25 (Play Console one-time fee). Total owner workload to v1 Closed Testing: ~11–12 hours active work over ~7 days plus passive waiting.

**v1 code work (8 PRs, ~5–7 days serial):**

| Repo | PR | Scope |
|---|---|---|
| lumin-app | A1 | 18+ age confirmation gate |
| lumin-app | A2 | First-run risk disclosure modal |
| lumin-app | A4-partial | In-app account deletion (no API-key revocation in v1 — that's v2) |
| lumin-app | A5 | Settings → ToS / Privacy / Risk URLs |
| lumin-app | A6 | Region-block enforcement |
| lumin-app | A7 | Copy vocabulary audit |
| lumin-app | feature-flag | Hide existing connect-page / auto-trade UI from v1 build |
| 360-v2 | E1 | DELETE /api/account endpoint |
| 360-v2 | E2 | GET /api/region for client region-check |
| 360-v2 | E3 | Standardised user-facing copy module |

**v2 code work (deferred until v1 is live):** A3 (prominent disclosure pre-API-entry), A4-full (API-key revocation in account deletion), A8 (inline privacy notice on data inputs).

**Owner decision queue (sign-off needed before Phase 0 starts):**

1. Approve the solo + phased plan?
2. Confirm hosting target — GitHub Pages on a `lumin-legal` repo, or Vercel free tier on `360-v2`?
3. Confirm tester recruitment path — DM 12+ existing paid Telegram subscribers, or wider opt-in via Telegram channel announcement?

---

## Queued — Play Store Phase 0–3 (original, "with team + budget" plan — superseded by solo reality above)

Research + plan PR landing this session. **Build pending owner sign-off** of the decision queue at the bottom of `docs/PLAYSTORE_PLAN.md`.

**One-line verdict:** publishable to Play Store. ~6–10 weeks from "decision to ship" to Production listing in India + UK + EU. Same pattern as Cornix / 3Commas / Bitsgap / Pionex / WunderTrading (all live). India NOT on the 15-jurisdiction crypto-custody licensing list; our non-custodial model is explicitly excluded from the Oct 2025 policy.

**Read the artefacts:**

1. `docs/PLAYSTORE_RESEARCH_2026-05-20.md` — full policy + competitor research (anchored to URLs)
2. `docs/PLAYSTORE_PLAN.md` — execution plan: decisions taken, per-row PR breakdown, phased timeline, risk register, decision queue

**Decisions baked in (this PR):**

* Vocabulary discipline: "signal" / "automation" / "strategy execution"; never "advice" / "guaranteed" / specific yield or leverage numbers
* Subscription billing: OFF-PLAY (Telegram channel content consumed outside app — fits Play Billing carve-out)
* Launch geo: India + UK + EU; exclude US / China / Bangladesh
* Account type: personal ($25, PAN + Aadhaar verification; no D-U-N-S needed)
* Financial Features Declaration: over-declare BOTH "Cryptocurrency exchange" AND "Financial advice" with explanatory free-text
* Data Safety: over-declare API key under BOTH Personal Info AND Financial Info

**Code work needed (8 app PRs + 3 backend PRs, ~12–20 days serial / 7–10 days parallel):**

| Repo | PR | Scope |
|---|---|---|
| lumin-app | A1 | 18+ age confirmation gate |
| lumin-app | A2 | First-run risk disclosure modal |
| lumin-app | A3 | Prominent disclosure screen before API-key entry |
| lumin-app | A4 | In-app account & API-key deletion flow |
| lumin-app | A5 | Settings → ToS / Privacy / Risk URLs |
| lumin-app | A6 | Region-block enforcement (US / China / Bangladesh) |
| lumin-app | A7 | Copy vocabulary audit |
| lumin-app | A8 | Inline privacy-policy notice on data inputs |
| 360-v2 | E1 | DELETE /api/account endpoint |
| 360-v2 | E2 | GET /api/region for client region-check |
| 360-v2 | E3 | Standardised user-facing copy module |

**Non-code work (parallel track, owner-side):**

* Open Play Console + India personal account verification
* Reserve + host legal pages (lumin.app/legal/{privacy,terms,risk})
* Draft Privacy Policy + ToS + Risk Disclosure (Cornix-style risk language)
* Store listing copy + assets (icon, feature graphic, 4–6 screenshots)
* Recruit 12+ Closed Testing testers (mandatory 14-day continuous opt-in for personal accounts)
* Engage Indian crypto-VDA lawyer for FIU-IND registration opinion (separate from Play; not a blocker for UK/EU launch)

**Top risks:**

1. Reviewer classifies us as "in-scope crypto exchange" → pre-empt with declaration free-text + Cornix precedent
2. FIU-IND enforcement against signal/bot services in India (low today, medium 12-month horizon) → legal opinion before India Production
3. Store copy reads as "guaranteed returns" → strict vocabulary audit (A7)
4. US accidentally enabled → triple region block (client + server + Play Console exclude)

**Owner decision queue (sign-off needed before Phase 0 starts):**

1. Approve the plan?
2. Confirm `lumin.app` domain availability or alternative
3. FIU-IND lawyer engagement — budget approval
4. Designer engagement for store assets — budget approval
5. Closed-testing tester recruitment path

---

## In-session checkpoint 2026-05-20 — Dispatch event log + DIV_CONT structure-misalign penalty shipped; adverse-excursion invalidation in flight

**Shipped (merged to main, deployed):**

1. **PR #461** — engine-side dispatch event log (`src/execution/dispatch_log.py`) + `GET /api/auto-trade/recent-events`.  Per-user Firestore subcollection captures every order-placement attempt (placed + rejected) with Binance code/msg + typed exception class.  Soft-fails on Firestore errors — never blocks the FSM path.
2. **PR #462** — fixed two pre-existing test_commands failures + `_minutes_since` AttributeError when snapshot timestamps arrive as strings (was 5xx'ing snapshot endpoints intermittently).  Suite now 5025-passing.
3. **lumin-app PR #48** — Trade-tab Recent Activity card consuming the new endpoint with plain-English translations of Binance error codes (-2019 margin insufficient, -2014 IP whitelist, -1111 precision, etc.) + engine-class translations (SymbolNotInUserPreference, GlobalKillSwitchActiveError, etc.).  Severity-coloured chips: success/userAction/transient/system.

**In flight — DIV_CONT structure-misalignment penalty:**

Truth-report 2026-05-20 analysis identified DIVERGENCE_CONTINUATION as the single suspicious-degradation path:

* avg PnL delta **-0.30** window-over-window (only path with notable negative trend)
* SL rate **30%** on n=10 (highest of all active paths; norm is 4-9%)
* Confidence gate filters only **5%** of eval-passing DIV_CONTs (vs 22-36% on other paths) — gate does almost no work
* Hypothesis: marginal kept-signals are DIV_CONTs entering against the 4h structural leg with no HTF-structure penalty to suppress them

**The fix:** add a symmetric counterpart to the existing `_STRUCTURE_ALIGN_BONUS` block in scanner.  When the 4h structure is `BULL_LEG`/`BEAR_LEG` with confidence ≥ `LEG_DOMINANCE_THRESHOLD` and **opposes** signal direction, apply `_STRUCTURE_MISALIGN_PENALTY` (default 5.0, env-overridable).  Enrolment is via `_STRUCTURE_MISALIGN_PATHS = frozenset({"DIVERGENCE_CONTINUATION"})` — narrow blast-radius; other paths can be added once a window's worth of telemetry validates the penalty's behaviour.

* 9 new tests cover: long-in-bear-leg + short-in-bull-leg penalty, aligned no-double-counting, RANGE exempt, below-threshold exempt, unenrolled path never penalised, no-structure exempt, enrolment pin (test fails on enrolment changes), magnitude bounds (2.0-10.0).
* Magnitude calibration: kept DIV_CONT avg final = 72.11 (gap -7.11 below threshold).  +5 brings marginal kept-signals (final 65-70) below threshold while leaving high-conviction signals (final 70+) safely above.

**Caveat — sample size:** the original observation is based on n=10 closed DIV_CONT signals.  Recommend monitoring the next truth-report window for: (a) DIV_CONT emit count drop, (b) SL rate trajectory, (c) avg PnL trajectory.  If emit count drops to zero, the penalty is too aggressive and should be re-tuned via `STRUCTURE_MISALIGN_PENALTY` env (B8).

**Doctrine compliance:**

* B5 — soft penalty, not hard block.
* OWNER_BRIEF §3.4a "HTF Structure, LTF Entry" — uses existing `structure_state.py` infrastructure as the doctrine mandates.
* B8 — env-overridable.
* "New evaluator paths or scoring models requires owner sign-off" — owner approved by saying "proceed" after the design summary in this session.

**Also shipped (4th PR in same session):** adverse-excursion invalidation rule (`src/trade_monitor.py`) — the truth-report Priority B follow-up.  Catches the full-SL pattern that `momentum_loss` / `regime_shift` / `ema_crossover` all miss: price grinding from entry → SL with momentum, regime, and EMA structure all intact the whole way down.

* Fires when: age ≥ 600s (matches existing scalp baseline) AND adverse excursion ≥ 70% of SL distance AND momentum not strongly confirming AND pre-TP hasn't fired AND not in TP1_HIT/TP2_HIT.
* Magnitude: 0.70 default saves ~30% of SL distance per kill (≈ 2.4% on margin at 10× vs full SL ~7.9%).
* Env-overridable: `INVALIDATION_ADVERSE_EXCURSION_FRACTION` (raise to 0.80 if next window shows > 25% PREMATURE classification; set to 1.0 to disable).
* New `adverse_excursion` family token in `categorise_kill_reason` — substring-ordering pin: must check `"adverse excursion"` BEFORE `"momentum"` substrings (the diagnostic message contains both).
* 9 new invalidation tests + 2 new categorise tests.  Next truth-report window will auto-classify this rule's kills as PROTECTIVE / PREMATURE / NEUTRAL via the existing ablation framework — if EV/kill < -0.20R after 20+ kills, raise the threshold or disable.

**Owner-decision queue for next session:**
* Validate the misalign-penalty enrolment after one truth-report window (expand from `DIVERGENCE_CONTINUATION` to other in `_STRUCTURE_ALIGN_PATHS` showing same asymmetric-quality pattern: TPE, CLS, PDC, SR_FLIP, QCB).
* Validate adverse-excursion EV after one truth-report window.  If PREMATURE > 25% → raise fraction to 0.80; if < 10% → consider tightening to 0.65.

---

## In-session checkpoint 2026-05-18 — Server-side execution: 14-PR roadmap SHIPPED + stack live end-to-end

**Session outcome: the entire 14-PR server-side execution roadmap landed in one day** (PRs #430, #432–#440, #441 on the engine + lumin-app #39, #40, #41, #42 on the app), plus three small wiring follow-ups (#442 safety-gate wiring into FSM, #443 bootstrap init, #444 user-status endpoint + lumin-app #42 banner UI).  The stack is now LIVE end-to-end per OWNER_BRIEF §3.9 + B18:

* B18 custody model: encrypted keys with KMS-backed signing service.
* §3.2a doctrine: pre-TP partial close + BE shift via mark-price feed → REDUCE_ONLY MARKET + BE-shifted SL.
* Blast-radius caps (#431 defaults): 5 tripwires + global enable flag + kill switch + circuit breakers.
* Operator surface: Telegram alerts on every tripwire trip; flip Firestore flags to engage/disengage.
* User surface: connect UI + 2FA TOTP gate + ToS click-through + Trade-tab disabled banner.

Default state on fresh deploy: ``auto_trade_globally_enabled = False`` — NO user can auto-trade until the operator flips the Firestore flag.  This is the operative #431 no-staged-beta safety floor in action.

### What still needs to happen before the first real subscriber can auto-trade

| Operational item | Notes |
|---|---|
| Deploy the merged code to the engine VPS | The auto-deploy on push-to-main has already shipped all the merged PRs; verify on the VPS that `src/security/` + `src/execution/` + `src/api/auto_trade_status_routes.py` are present |
| Provision the GCP plumbing per ``docs/server-side-execution-setup.md`` | KMS keyring + key + IAM grants + Firestore Security Rules deploy via ``firebase deploy --only firestore:rules`` |
| Set engine env vars: ``GCP_KMS_PROJECT_ID``, ``GCP_KMS_LOCATION``, ``GCP_KMS_KEYRING``, ``GCP_KMS_KEY_NAME``, ``ENGINE_VPS_PUBLIC_IP``, ``TRIPWIRE_SYMBOL_ALLOWLIST`` (comma-separated symbols) | Each guards a subsystem — missing any one fails-soft (subsystem offline, log line at boot) per the wrapped init in bootstrap.py |
| Run the signing service as a systemd unit under user ``lumin-signer`` | ``python -m src.security.signing_service`` — receives the same GCP env vars |
| **Operator action**: flip ``kill_switch/global.auto_trade_globally_enabled = true`` in Firestore | After this, any user who has completed the connect flow (2FA + ToS + Binance key) can auto-trade |
| Optional v1: apply for Binance Link / Fast API partnership (per #431 resolved decision 4) | Better UX long-term but not blocking |

### Follow-ups intentionally deferred from this session

| Item | Notes |
|---|---|
| MarkPriceFeed + Reconciler background-task launchers in bootstrap.py | Both modules ship (PR-9 / #439); they need an asyncio.create_task wired in bootstrap, deferred until first beta user is ready |
| Per-user PositionWorker lifecycle manager | Needs a worker-manager that watches the user roster + starts/stops accordingly; deferred for the same reason |
| Telegram bot operator commands (``/enable_global``, ``/disable_user``, ``/reset_global_breaker``, etc.) | Firestore direct edit works for v1; bot commands are operator-UX polish |
| Disconnect-key button on the connect page (Lumin) | Operator can delete the Firestore doc manually for now |
| QR code rendering for the otpauth:// URI on the 2FA page | Manual paste into authenticator works for MVP |
| Firestore sync of ToS acceptance (cross-device + IP / audit metadata) | Per-device SharedPreferences works for v1; the doctrinal trail is in the audit field on the user doc when we Firestore-sync |
| Firebase emulator integration tests for connect + 2FA + ToS flows | Out of scope for this session; would benefit existing auth flows too — separate test-infra PR |
| Server-side enforcement of 2FA + ToS acceptance on ``/api/binance/connect`` | Client-side gate is operative today; server-side enforcement is next-layer hardening |
| ToS revision-history viewer | Polish; current acceptance just stores the version |

These are operational polish on top of a working stack, not correctness gaps.

### Operative truth: the doctrine is implementable end-to-end

The whole point of the 14-PR roadmap was to make the §3.2a doctrine actually fire in production — banking +2.5% net @ 10× on most signals via pre-TP partial close + BE shift, asymmetrically defeating SL hits.  Before today, the doctrine was implemented engine-side (truth report shows 99 pre-TP fires) but ONLY in the engine's paper trader — real users with auto-trade enabled but phone-asleep MISSED most pre-TP fires.  After today, server-side execution restores doctrinal compliance for every paid subscriber regardless of phone state.

Direct business chain impact (per CLAUDE.md §VI gate): paid-subscriber retention → revenue retention → growth runway.

### Test surface delivered

* Engine: **287 tests** across `tests/execution/` (157) + `tests/security/` (123) + `tests/api/test_binance_connect_routes.py` + `tests/api/test_auto_trade_status_routes.py` (7) — all passing.
* Lumin: 8 new TosService tests; the rest of the surface is exercised via the engine's contract tests (76 tests on /api/binance/connect alone).

---

## In-session checkpoint 2026-05-18 — Server-side execution: architecture decided, 14-PR roadmap landed (original entry, kept for the in-progress design context)

**Driver:** owner-flagged that Binance now requires IP whitelist on any Futures-trade-enabled API key (policy tightened late 2023). Mobile-IP rotation + WiFi changes make per-device whitelisting unusable; subscribers cannot enable auto-trade without either (a) running a personal VPN with static exit IP, or (b) Lumin moving order execution server-side. Compounded by the structural blocker that pre-TP partial close + BE shift requires sub-second reaction to TP1 fills, which Binance does not support as a native order chain — so an always-on watcher is mandatory for the doctrine to function. The mobile lifecycle (iOS suspends ~30s, Android variable) cannot meet that requirement.

**Decision:** ship server-side execution. Engine VPS holds users' encrypted Binance API keys, signs and places trades from a fixed IP, runs per-user Position FSM workers consuming Binance User Data Stream for sub-100ms reaction to fills. Industry-validated — every commercial 24/7 peer (3Commas, Cornix, Bitsgap, WunderTrading, Coinrule, Cryptohopper) made the same call. The 3Commas Dec-2022 breach validates the approach when implemented with separation of DB access from decryption authority — the class-action allegation is "any employee with webserver access could view sensitive API data," i.e. lack of separation, not weakness of encryption math. Coinrule's published per-user-DEK + segregated-KEK pattern + 3Commas' post-breach Sign Center signing-service boundary are the patterns Lumin adopts.

**Solo-scaled — what we skip vs the enterprise template:** no Cloud HSM (Cloud KMS sufficient), no separate VPC for signing service (separate Python process on the engine VPS, isolated by Linux user + Unix socket), no SOC 2 / audit-log retention machinery (plain log file + Telegram alert), no cyber-insurance (replaced by hard caps + small beta + honest ToS), no MiCA/CFTC legal opinion (geoblock US, operate as personal project per industry peers' early-stage pattern). Adds ~$5/mo (Cloud KMS only) on top of existing VPS.

### Threat model — what each defense protects against (the doctrine in one table)

| Attack | Defense | Residual risk |
|---|---|---|
| User's phone stolen | Firebase ID-token expires 1h; biometric required to unlock app; 2FA mandatory on auto-trade enable | ~1h trading window, capped by per-user position size + symbol allowlist |
| Firestore breach (cloud) | Ciphertext + encrypted DEKs only at rest; KEK in Cloud KMS, no Firestore reader can call KMS | Attacker has bytes, cannot sign anything |
| Engine VPS rooted | KMS audit log on every decrypt; **withdrawals disabled on every key, validated at connect (no exceptions)**; symbol allowlist + per-user rate limit + per-user position cap | Attacker can trash positions while session alive; cannot drain wallets, cannot trade outside Lumin's signal symbols |
| Binance API key leaked (Lumin-side) | Mandatory IP whitelist on Binance key = engine VPS IP only | Key unusable from any IP except engine VPS |
| Insider abuse (future contractor) | All raw-secret access mediated by signing service with audit log; symbol allowlist + position caps apply equally to insiders | Solo today; future-proofs the model |

### Concrete architecture (Hybrid: Firebase/GCP managed + engine VPS for always-on)

```
┌─── Firebase / GCP (managed) ───┐    ┌──────── Engine VPS ─────────┐
│ • Firebase Auth (identity)     │    │ • Existing signal engine    │
│ • Firestore (encrypted blobs)  │◄───┤ • NEW: signing service      │
│ • Cloud KMS (KEK, HSM-isolated)│    │   (separate process, Unix   │
│   - service account: Decrypt    │    │    socket, no DB read)      │
│     only, audit-logged          │    │ • NEW: per-user Position    │
└────────────────────────────────┘    │   FSM workers (asyncio)     │
                                       │ • NEW: Binance User Data    │
                                       │   Stream consumer per user  │
                                       │ • Fixed egress IP → users   │
                                       │   whitelist this on Binance │
                                       └─────────────────────────────┘
```

Reaction-time budget for TP1-hit → BE-SL placed: ~60-100ms total (WS event ~5-20ms + FSM transition + signing-service Unix-socket call ~1ms + KMS Decrypt cached ~30ms + Binance order POST 20-50ms RTT). Comfortably sub-second.

### 14-PR roadmap (owner-approval-gated for the doctrine slices; the rest are CTE scope)

| # | PR | Days | Owner-touch? | Status |
|---|---|---:|---|---|
| 1 | Firebase Admin SDK + Cloud KMS integration on engine VPS (scaffolding only — KMS client wrapper, envelope crypto helpers, deps) | 2 | No — pure scaffolding | ✅ shipped 2026-05-18 (#430) |
| 2 | `/api/binance/connect` endpoint + Binance permission validation (withdraw=false, futures=true, IP=engine_vps_ip) | 2 | **Yes** — paid-channel-adjacent | ✅ shipped 2026-05-18 |
| 3 | Firestore schema + per-user DEK provisioning + security rules locking user out of own `binance_key` subcollection | 1 | No | ✅ shipped 2026-05-18 |
| 4 | Signing service (separate Python process, Unix socket, KMS Decrypt, AES-GCM, plaintext wipe) | 3 | **Yes** — security-critical, B12-adjacent | ✅ shipped 2026-05-18 |
| 5 | Per-user worker scaffold + Binance User Data Stream WS consumer | 3 | No — read-only listener | ✅ shipped 2026-05-18 |
| 6 | Position FSM: entry placement + native SL/multi-TP (Binance "split target" — up to 4 TP legs natively) + state transitions | 3 | **Yes** — touches B12 | ✅ shipped 2026-05-18 |
| 7 | Pre-TP partial close + BE shift + reduce-only order flow (the doctrine-critical slice — §3.2a in action) | 2 | **Yes** — B17 + doctrine | ✅ shipped 2026-05-18 |
| 8 | Anomaly tripwires: symbol allowlist, per-user rate limit, per-user position cap | 1 | **Yes** — B12 blast-radius caps | ✅ shipped 2026-05-18 |
| 9 | Reconciliation loop (60s per-user Binance state vs FSM diff + self-heal) + permission-drift detector | 1 | No | ✅ shipped 2026-05-18 |
| 10 | Lumin-app: connect-flow UI + IP-whitelist modal + position view via Firestore realtime listener | 3 | No | ✅ shipped 2026-05-18 |
| 11 | Kill switch (Firestore doc + worker check, halts all order placement within 5s) + Telegram alerts on tripwire fires | 1 | No | ✅ shipped 2026-05-18 |
| 12 | 2FA enrollment requirement for auto-trade enable (Firebase TOTP) | 1 | **Yes** — gates B12-adjacent surface | ✅ shipped 2026-05-18 |
| 13 | ToS + click-through opt-in (records `accepted_at` / `user_agent` / `ip` / `tos_version` in Firestore) | 1 | **Yes** — substitutes legal opinion per solo-scale doctrine | ✅ shipped 2026-05-18 |
| 14 | Beta gating: per-user position cap + cohort flag in Firestore | 1 | **Yes** — controls who gets access | ✅ shipped 2026-05-18 |
| **Total** | | **~25 working days ≈ 5-6 weeks solo with AI** | | |

### Beta rollout (blast-radius cap while the system bakes)

| Stage | Users | Max position | Symbols | Min duration before next stage |
|---|---:|---:|---|---|
| 1 | You only | $20 | 1 (ETH or BTC) | 1 week |
| 2 | 5 trusted | $100 | Full allowlist | 2 weeks |
| 3 | 20 | $500 | Full | 4 weeks |
| 4 | 100 | $1000 | Full | After 1 month clean |
| 5 | Open beta | $2000 default (user-configurable) | Full | After 2 months clean |

### Resolved owner-decisions (2026-05-18, post-PR-1 merge)

| # | Decision | Resolution | Notes |
|---|---|---|---|
| 1 | Geographic restriction | **Geoblock US** | Implemented in PR-2 connect-flow (Firebase claims check) + sign-up flow. Defends against the 3Commas N.D. Cal. litigation vector. |
| 2 | Withdraw permission policy | **Auto-reject keys with withdraw enabled** | Hard-coded in PR-2's connect-flow validator (`B18` non-negotiable). No permissive mode, no admin override. |
| 3 | Single-region vs multi-region egress IPs | **Single-region for v1** | Engine VPS IP is the single whitelist target. Multi-region failover deferred until subscriber volume justifies the GCP NAT-gateway cost. |
| 4 | Binance Link / Fast API partnership | **Apply now (solo individual)** | Application submitted as a solo individual without a registered entity. Binance Link's program docs require KYB + min-volume showing; solo applications **may be declined** but submitting puts us in the queue and we can re-apply with an entity later. Does NOT block v1 — IP-whitelist path proceeds in parallel. |
| 5 | Beta cohort / staged rollout | **OWNER OVERRIDE — ship to all users at once, no staged beta** | Owner explicit decision 2026-05-18 after CTE recommendation for compressed (24h-stage-1-then-open) rollout. **The blast-radius caps (B18, see strengthened defaults below) become the ONLY safety net.** This is a doctrinal override of `B12` "paper mode is the only acceptable runtime when [safety controls] are not in place" — recorded here per `CLAUDE.md § Hard Limits` "never silence a detected problem." |
| 6 | Pre-TP partial close fraction default | **50% (engine default per B17)** | Server-side FSM uses the same default the existing PaperOrderManager uses; users can override per the B17 30% floor / 100% ceiling. |

### Strengthened blast-radius defaults (compensating for the no-beta override)

Since beta-staging is gone, the **default** values for the B18 blast-radius caps tighten:

| Cap | Original beta-stage default | **Revised solo-launch default** | Why |
|---|---|---|---|
| Per-user position cap | $500 (Stage 3) → $1000 (Stage 4) → $2000 (Stage 5 open) | **$500 user-configurable up to $2000** | Conservative default; users opt UP, not DOWN. A FSM bug fires within $500 per user not $2000. |
| Symbol allowlist | Lumin signal-channel symbols | **Unchanged** — only signal-channel symbols | Already maximally restrictive. |
| Per-user rate limit | 10 orders/min, 50/hour | **5 orders/min, 30/hour** | Tighter than originally specced; doctrinally a real signal-driven user rarely needs more. |
| Global engine kill switch | Telegram-flippable | **Unchanged** — but ALWAYS-on monitoring | Reachable in <5s from Telegram bot. |
| **NEW** Global circuit breaker (added 2026-05-18 to compensate for no-beta) | n/a | **Engine auto-disables auto-trade engine-wide if >10 orders are rejected by Binance with `-2014`/`-2015`/`-4046`/`-2010` errors in a 60s window.** Re-enable requires manual Telegram command. | Catches: FSM bug that fires wrong-permission orders for every user; KMS outage that breaks signing for every user; symbol-allowlist drift. Independent tripwire layer. |
| **NEW** Per-user circuit breaker | n/a | **User auto-disabled (not engine-wide) if >3 of their orders are rejected within 5 minutes.** Telegram alert + user must reconnect. | Catches: one user's Binance key permissions changed underneath us; key revoked; account suspended at Binance. Bounded blast to one user. |

These two new circuit breakers add ~200 LOC to PR-8 (anomaly tripwires) and absorb most of the safety the staged beta was providing. Not a complete substitute (a coordinated FSM logic bug still fires up to 10 wrong orders before the global breaker trips), but the minimum responsible defence given the owner's no-staged-beta decision.

### Updated 14-PR slice ordering after owner-decisions

PR-14 (beta cohort gating) is downgraded to a **kill-switch + global-enable-flag** shape — no per-cohort logic, just `auto_trade_globally_enabled: bool` in Firestore plus the two new circuit breakers above. Effort: 1 day → unchanged.

All other PRs unchanged.

### Why this section exists

Future sessions / future-CTE need to see the explicit doctrine-override decision (#5) so we don't quietly re-introduce staged-beta thinking later, and so any post-mortem on a launch-day incident has the clear record of "owner was advised, owner decided" — not "CTE shipped recklessly."

### What ships before owner sign-off vs after

- **CTE-scope, can ship now:** PRs 1, 3, 5, 9, 10, 11 (scaffolding, schema, WS listener, reconciliation, app UI, kill switch). None touch order-placement logic; none change the production paid-channel signal flow. Total: ~11 days.
- **Owner sign-off required:** PRs 2, 4, 6, 7, 8, 12, 13, 14. These either touch the security boundary, the order-placement chain, the doctrine-critical pre-TP/BE flow, or the user-facing access controls. Total: ~14 days.

The plan above lets us ship the foundation (KMS plumbing, schema, WS consumer, app shell, kill switch) while the owner reviews the security-critical / B12-adjacent pieces in design form.

### Why this advances the business chain (the test from CLAUDE.md)

The doctrine's profit engine is pre-TP partial close (§3.2a — banking +2.5% net @ 10× on ~50% of signals turns a doctrinally net-losing path into a net-positive one). Today, real users with auto-trade enabled but phone-asleep MISS most pre-TP fires; we have zero telemetry on this gap. Server-side execution restores doctrinal compliance for every subscriber, eliminates the mobile-IP-whitelist UX dead-end, and unblocks the paid-tier growth path that requires "set and forget" execution. Direct business chain impact: **paid-subscriber retention** (auto-trade actually works as advertised) → **revenue retention** → **growth runway**.

---

## In-session checkpoint 2026-05-17 — 654-signal forensic + per-path structural audit (analysis only, no code yet)

**Owner-driven deep audit triggered by /stats reporting 286 signals in ~20h at 0.3% decisive-TP rate.** Pulled 36 historical `monitor-logs` snapshots, deduped on `signal_id` → 654 unique closed signals over 2026-04-21 to 2026-05-17. All analysis below at this scale, all NET% at 10× / 0.7% round-trip fee per B11.

### Aggregate truth (n=654)

- Mean PnL raw: **−0.022%**
- Mean NET on margin: **−0.92%**
- 479 (73.2%) signals net-negative for subscribers after fees
- 25 (3.8%) FULL_TP_HIT + PROFIT_LOCKED combined
- Pre-AI mean 72.4 → Post-AI 77.6 (AI delta +5.23) → Final 73.2 (penalties net −4.4)
- Engine direction-call quality: **41.1% MFE=0** (engine called direction; price never moved that way); **67.9% never reached pre-TP floor of 0.20% favorable**

### Per-path performance + direction-call quality (n=654)

| Setup | N | NET margin | Win% | MFE=0 | Verdict |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 249 | −0.50% | 3.6% | **42.6%** | Marginal — thesis sound on 15m+, noisy on 5m |
| QUIET_COMPRESSION_BREAK | 135 | −1.11% | 1.5% | 39.3% | R:R 1.3 cannot fund a 40-50% strategy; literature requires 3:1 |
| FAILED_AUCTION_RECLAIM | 115 | −0.72% | 6.1% | 39.1% | **Misnamed.** 5m "auction" = stop hunt. Real failed-auction is DAILY pattern |
| LIQUIDITY_SWEEP_REVERSAL | 89 | −1.13% | 5.6% | **23.6%** | **Best direction-caller.** Thesis sound; needs HTF POI anchoring |
| TREND_PULLBACK_EMA | 36 | −1.51% | 5.6% | **77.8%** | EMA pullback structurally fails on 5m (mean-reversion in trend) |
| DIVERGENCE_CONTINUATION | 19 | −3.27% | 0.0% | 63.2% | CVD-div + short TF + trending — fights both literature warnings |
| CONTINUATION_LIQUIDITY_SWEEP | 9 | −2.36% | 0.0% | 44.4% | Redundant against LSR; trend constraint adds nothing |

**Not a single emitting path is net-positive at scale.** Per-path forensic was confused by 100-sample noise (LSR appeared positive there; at 654-scale it's −1.13%).

### Per-confidence-band (scoring weakly predictive, with one anomaly)

| Band | N | NET margin |
|---|---:|---:|
| 65-69 | 258 | −1.49% |
| 70-74 | 176 | −0.94% |
| 75-79 | 69 | −0.44% |
| 80-84 | 125 | **+0.03%** (only break-even band) |
| 85-100 | 26 | −0.87% |

Scoring discriminates progressively below 80; 80-84 is the only break-even cohort; 85+ falls back (small sample, also 38.5% SL rate).

### AI confidence layer (n=654)

| AI delta | N | NET margin |
|---|---:|---:|
| (−∞, −1) | 32 | −1.80% |
| [−1, +1) | 144 | −0.60% |
| [+1, +4) | 176 | −0.61% |
| [+4, +8) | 109 | −0.36% |
| **[+8, +15)** | **177** | **−1.90%** |
| [+15, +100) | 16 | +1.69% |

The +8-15 lift band is the largest cohort and the worst-performing. AI mis-boosts moderate candidates.

### Pair concentration (44 of 65 pairs with ≥3 signals net-negative)

Worst losers needing blacklist extension beyond current SIREN/TON/VVV: **ENAUSDT (−6.51%, n=12), BNBUSDT (−4.74%, n=25), LABUSDT (−3.17%, n=11), BZUSDT (−2.49%, n=11), SAHARAUSDT (−4.83%, n=5), TAOUSDT (−1.94%, n=12), SUIUSDT (−2.31%, n=17)**.

**DUSDT B4 violation discovered:** 22 identical-fingerprint QCB SHORT signals in window (all conf 74.83, all PnL −0.1752%, all MFE 0). Cooldown not deduping.

### Time-of-day at scale

00-07 UTC + 18 UTC are the loss windows (all sub-−1.5% net). 12, 14, 17 UTC are the profitable hours. PR #303 KZ-removal lost real edge in dead-zone hours — needs per-hour soft penalty, not legacy KZ revival.

### Per-path structural audit vs current crypto-scalping reality (web-researched 2026-05-17)

Universal economics:
- Taker fees @ 10×: 92% win-rate break-even at R:R 1:1; 57% break-even at R:R 1.3:1; 33% at R:R 3:1
- Maker fees @ 10×: 57% break-even at R:R 1:1 (free 35-point gain we don't surface to subscribers)
- Realistic well-tuned scalping: 3-6% monthly. We're at −0.92% NET per signal × 25/day = subscriber loses ~3% margin/day.

Per-path code-vs-reality (each evaluator read in `src/channels/scalp.py`):

1. **SR_FLIP_RETEST** (line 2611). 41-candle "swing levels" = 3h local extrema, not real structure. 5m S/R retest is below the 15m noise threshold per literature. SCALAR_FALLBACK +5 penalty already exists in code = engine knows ~30% of "levels" are guesses. R:R 1.27.
2. **QUIET_COMPRESSION_BREAK** (line 3268). BB squeeze breakout: real-world 40-50% win, needs 3:1 R:R for positive EV. We ship R:R 1.30 — mathematically cannot profit. Code explicitly removed volume confirmation citing unit-mismatch but never replaced the doctrinal need.
3. **FAILED_AUCTION_RECLAIM** (line 4399). Real failed-auction is Market Profile concept on DAILY/4H ("revisits in 5-6 days, 75% of cases"). Our 5m + 7-bar auction window is a stop-hunt pattern, not a failed auction. R:R floor 1.0 (`_FAR_MIN_RR = 1.0`) makes the math impossible. **Path is misnamed and miscalibrated.**
4. **LIQUIDITY_SWEEP_REVERSAL** (line 915, `_evaluate_standard`). **The only structurally-correct path.** SMC sweep+MSS matches institutional doctrine. 24% MFE=0 (best). Issue: fires on ANY 5m sweep, not just sweeps **at HTF POI**. LevelBook infra already exists to add this gate.
5. **TREND_PULLBACK_EMA** (line 1203). EMA pullback is a mean-reversion thesis on trending data. EMAs are lagging — by the time price touches EMA21 on 5m, the impulse is exhausted. 78% MFE=0 confirms.
6. **DIVERGENCE_CONTINUATION** (line 3473). Hidden CVD divergence on 5m in TRENDING regime — fights both literature warnings (short-TF CVD-div noisy; CVD-div in strong trend fails). 63% MFE=0.

Structural cross-cuts:
- **Correlation collapse:** Altcoin Season Index = 37 (BTC-leaning) → alt-BTC correlation 0.85+. Our 75-pair scan is effectively 5+ duplicate BTC bets per BTC move, masquerading as independent signals.
- **R:R ceiling on every emitting path is below break-even at our actual win rates.** Geometry assumes 50-60% win; we deliver 3-6%.
- **Regime classified on 5m** — likely confounded. A "QUIET" 5m inside a 1H trend is noise within trend, not real quiet market.

### Proposed plan tiers (awaiting owner sign-off — touches scoring, paths, paid-channel routing per §1.3)

| Tier | Action | Owner-touch? |
|---|---|---|
| 1 | Disable TPE, DIV_CONT, CLS via env flags (structurally broken paths) | **Yes** — deprecation per §1.3 |
| 2 | Raise R:R floors: FAR 1.0→2.0, SR_FLIP 1.2→1.5, LSR 1.5→1.8, QCB 1.3→2.0 | Per-evaluator B7 — CTE scope, flag if any look owner-touch |
| 3 | Add HTF POI anchoring to LSR (LevelBook gate) | **Yes** — scoring change |
| 4 | Extend `SCAN_SYMBOL_BLACKLIST`: ENA, BNB, LAB, BZ, TAO. Env-only | No — env update |
| 5 | Document maker-order discount to subscribers (92% → 57% break-even) | No — doc only |
| 6 | Regime classifier on 15m/1H (parked) | Yes — major architecture |

Tier 1+2 alone is expected to drop signal volume by ~30-40% but cut net-losing emissions in half. App surface stays alive.

**Next investigation queued in this session:** Pre-TP grab + invalidation kill effects on net PnL — is the safety net actually protecting from full SL? On what criteria? Reality check.

---

## Current Phase

**End-of-day 2026-05-16 — Firebase auth migration shipped (engine + Android), paper-trade visibility shipped with two latent paper-broker bugs squashed (`qty=0` open positions, daily-resetting equity), and a definitive pair-bleed diagnosis ruled out the movers path and placed all current PnL bleed on Path-1 SMC evaluators against specific top-75 pairs.** Two-day arc (2026-05-15 → 2026-05-16) covering identity-stack migration, subscriber-visible paper-trader honesty, and an env-only blacklist of three confirmed-bad pairs while the architectural fix (learned per-pair penalty) is queued. Paired follow-up PRs (engine `/close-all` + Lumin Trade-tab UX) dispatched in this session and currently in flight.

### 1. Firebase auth migration — engine + Android (PRs #397, #398, #399, #400 / Lumin #20, #21, #22)

Replaces the bespoke Telegram-OTP + phone-OTP + admin-token chain with Firebase as the identity issuer. Owner motivation: collapse the three-provider auth stack (LogOnly + WhatsApp + AWS-SNS-SMS, plus the @LuminProBot DM path) into one provider that subscribers already trust via Google sign-in, and get Apple-equivalent identity guarantees on Android without per-country SMS DLT paperwork. Telegram-DM OTP remains as an opt-in upgrade per B13.

| PR | Title | Slice |
|---|---|---|
| #397 | docs: firebase auth migration design (engine) | Design summary first — endpoint contract, claims shape, migration path for existing user-id JWTs |
| #398 | feat: Firebase auth migration (engine implementation) | `FirebaseTokenVerifier`, `/api/auth/firebase/verify` endpoint, `firebase_uid` column on `users`, JWT-mint flow re-pointed |
| #399 | fix(users): move firebase_uid index creation out of _SCHEMA_SQL | First-boot migration crash — index DDL inside `CREATE TABLE` SQL is invalid SQLite; moved to a separate `CREATE INDEX IF NOT EXISTS` step |
| #400 | fix(api): add missing /api/auth/telegram-otp/issue endpoint | Phase-1 testers still on Telegram-OTP path were 404ing; restored the endpoint the Firebase migration accidentally clipped |
| Lumin #20 | design: Firebase auth migration (Android, web later) | Android-first design, web deferred |
| Lumin #21 | feat: Firebase auth migration (Android implementation) | `firebase_auth` Flutter package, Google sign-in flow, ID token → `/api/auth/firebase/verify` → user-id JWT cached in secure storage |
| Lumin #22 | fix(ci): patch build.gradle.kts so release builds use the release keystore | Release APKs had been signed with the debug keystore — broke Firebase's SHA-1 fingerprint pinning until the CI patch landed |

Migration discipline followed: design PR (#397, #20) merged BEFORE code PR (#398, #21). The three follow-up hotfixes (#399, #400, #22) were caught within hours of first deploy — no subscriber-visible auth failures in production.

### 2. Paper-trade visibility — PR #401 + Lumin #23

The Lumin Trade tab now surfaces per-trade history with leverage, position-size %, ROI%-on-margin, fees, and net PnL — the Binance-style record card subscribers asked for. Built on top of two latent paper-broker bugs the screenshot diagnostic surfaced mid-build:

**Bug A — paper open positions had `qty=0` across the board.** Visible in the 2026-05-16 screenshot: 5 open positions (SIRENUSDT, BCHUSDT, SUIUSDT, etc.) all rendered as `qty 0.0 @ <entry>` with `+$0.00` PnL even when price moved favorably (BCHUSDT was at +0.28% favorable). Root cause in `PaperOrderManager._compute_quantity`: degenerate inputs (`entry_price <= 0` or depleted `_available_equity`) returned `MAX_POSITION_USD / 1e-12` — an astronomical qty that downstream rounding flattened to zero on high-priced symbols. Post-fix funnels every degenerate path through an explicit `return 0.0` + parent-method skip with a `qty_zero_guard` telemetry counter.

**Bug B — paper equity resetting daily, not cumulative.** Screenshot showed `Equity: $999.63` while `Paper total since boot: -$11.97` and `Today's P&L: -$0.37`. Math: `$1000 - $0.37 = $999.63`, not the cumulative `$1000 + (-$11.97) = $988.03`. Root cause in `RiskManager._current_equity = starting_equity + daily_realised_pnl_usd` — only today's bucket was carried. Fix added `PaperOrderManager.current_equity_usd` property as broker-side truth (`starting + cumulative since boot`) with persistence through `_persist_paper_pnl_state` so the figure survives restarts. The engine's `get_auto_execution_status` now reads from here in paper mode.

**The feature itself** (PR #401):
- New `src/auto_trade/trade_records.py` SQLite store — one row per signal, snapshots leverage + position-size % at open, computes ROI%-on-margin at close
- `GET /api/trades?mode=paper&limit=&offset=&include_open=` — paginated, fail-soft on SQLite IO errors (returns empty page instead of 500)
- `POST /api/auto-mode/paper/reset` — owner-only, refuses while open positions exist (B12 lifecycle guard), zeros cumulative PnL, wipes daily buckets, archives per-trade rows to a timestamped table
- Bot `/stats` reworked to read from `performance_tracker_honest.py` (per-trade rollups from the new store) — no more discrepancy between Telegram `/stats` and the app's Today's P&L card
- Lumin #23 wires the Paper sub-tab: paginated list view with Binance-style cards (side badge + ROI pill + 4-col stats grid + close-reason label), tap → detail page, "Reset balance" in the AppBar overflow

### 3. Pair-bleed diagnosis + SCAN_SYMBOL_BLACKLIST env update (2026-05-16)

Owner asked: *"are promoted-pairs causing more negative impact on PnL, or what?"* Investigation went deep enough to settle the question definitively.

**Two scan paths confirmed in code (not just PR descriptions):**

| Path | Source | Universe | Allowed evaluators | Count |
|---|---|---|---|---|
| Path 1 (standard) | `pair_manager.refresh_top50_futures` (90s refresh) | Top-75 USDT-M futures by 24h volume | All 15 (on structurally-aged pairs) or `_YOUNG_PAIR_EVALUATORS` (on young pairs) | 15 or 6 |
| Path 2 (movers) | `scanner._update_movers_promotion` (per scan cycle, PR #233) | `|24h Δ| ≥ 15%` AND `volume ≥ $5M` AND NOT in top-75; 5-cycle TTL; skipped if spread > 0.5% | `_mover_evaluators = {VSB, BDS}` — supersedes young-pair restriction | 2 |

Restriction is enforced at the evaluator-loop level (`src/channels/scalp.py:846-877`) with a hard `continue` — not a soft scoring layer. The other 13 evaluators never see mover-promoted pairs.

**Definitive PnL-attribution data (last-100 sample):**

| Volume tier within top-75 | Pairs in sample | Signals | Σ PnL | Avg/signal | SL-touch rate |
|---|---|---|---|---|---|
| Mega-cap (>$500M) | 3 | 6 | -0.461% | -0.077% | 50% |
| Large-cap ($150-500M) | 5 | 13 | -0.394% | -0.030% | 38% |
| Mid-cap ($50-150M) | 30 | 68 | -0.307% | -0.005% | 47% |
| Smaller ($10-50M) | 8 | 13 | +0.019% | +0.001% | 69% |

This **contradicted** the "smaller/newer/volatile = more loss" hypothesis. Mega-caps had the WORST avg/signal at -0.077%. Smaller-caps had the HIGHEST SL-touch rate (69%) but the BEST avg PnL (+0.001%). Volume tier doesn't predict outcome — **specific pairs do**.

**MFE=0% (structural smoking gun):** 15/100 signals had zero favorable excursion at any point in their lifetime — engine called a direction and price never moved that way. By pair: SIRENUSDT 3/3 (100% misread), TONUSDT 2/6 (33%), then 1 each for FFUSDT, POLYXUSDT, TAOUSDT, LABUSDT, ICPUSDT, UBUSDT, UNIUSDT, SWARMSUSDT, NEARUSDT, BNBUSDT.

**Path-2 attribution:** VSB generated 852 / emitted 1; BDS generated 1513 / emitted 1. Zero in the 100-sample. Movers path is not contributing meaningfully to the bleed despite PR #363's widening — gates downstream still filtering hard.

**Env-only blacklist applied** (no code PR — `SCAN_SYMBOL_BLACKLIST` env var updated on the VPS and engine restarted):

```
Before: XAUTUSDT,PAXGUSDT,MMTUSDT,KOMAUSDT,STOUSDT
After:  XAUTUSDT,PAXGUSDT,MMTUSDT,KOMAUSDT,STOUSDT,SIRENUSDT,TONUSDT,VVVUSDT
```

These are top-75 pairs whose Path-1 SMC signals were the worst losers in the sample. Existing open positions on SIRENUSDT (and any other newly-blacklisted) will close naturally — blacklist only prevents NEW signals.

### 4. Architectural follow-up queued — learned per-pair penalty (the right structural fix)

The manual blacklist is the polishing-stage move. The actual fix is **option 3**: keep a rolling EMA of (PnL, SL rate) per pair and apply a confidence penalty proportional to recent negative performance. Auto-de-promotes underperforming pairs without manual blacklisting — same idea as `_PAIR_BLACKLIST` but data-driven and self-correcting. Two other options considered and rejected for this slot:

1. **Two-criteria sort** (rank by `volume_24h × order_book_depth_USD` or `volume × N-day-stability`) — filters launch-pumps but doesn't help with established-pair misreads
2. **Pair age gate** (require ≥N days listed before entering scan universe) — `young_pair_restriction` machinery already exists, just not strict enough; would help with truly-new pairs but not BCH/SUI/BNB-class established misreads

**Queue position:** sits behind Phase 4 (per-user PnL ledger, B12 daily-loss gap) and `deploy.yml` concurrency block. Owner sign-off required before coding because it touches scoring (per OWNER_BRIEF §1.3).

### 5. In flight (this session) — Trade-tab UX redesign + paper `/close-all`

Follow-up #1 from the previous queue is being executed in this session as a paired PR. The trigger: the reset flow is practically unreachable today because almost every paper subscriber has open positions, and PR #401's `/reset` deliberately refuses while positions are open (B12 lifecycle guard, mirroring the live-mode `/reset_full` doctrine of never orphaning broker state).

**Engine — PR #403 `feat/paper-close-all-positions` (open, non-draft, awaiting CI):**
- New `PaperOrderManager.close_all_open_positions(reason="user_close_all") -> dict` (`src/paper_order_manager.py`) — snapshot-iterates `_positions.keys()`, builds a `types.SimpleNamespace(signal_id, symbol, current_price=position.entry, stop_loss=0.0)` per position, calls `self.close_full(..., reason=reason, current_price=position.entry)` for a zero-move fill, tracks `closed_count` + summed delta of `_realised_pnl_total`, logs a single `paper_close_all: closed N open paper positions (reason=...)` marker
- New endpoint `POST /api/auto-mode/paper/close-all` (`src/api/paper_trade_routes.py`); new `PaperCloseAllResponse` Pydantic model (`src/api/schemas.py`) — `{ok, closed_count, realised_pnl_total}`; auth + wiring mirror the `/reset` endpoint (**owner-only** via `Depends(owner_required)`)
- Tests in `tests/test_paper_close_all.py` — 5 broker-level cases (happy-path 3-positions, empty-book idempotency, double-call idempotency, mutation-during-iteration safety, custom-reason propagation) + 4 HTTP cases (owner-required 403, happy-path via real `PaperOrderManager`, empty-book, idempotent double-call)
- **Realised-PnL is not strictly zero per position** — `close_full` applies taker exit fee + entry-fee share when `"tp" not in reason.lower()`, so `"user_close_all"` pays fees. Tests assert `realised_pnl_total <= 0` within `abs=10.0` of zero, not strictly zero. Behaviourally correct (subscriber pays real fees on a real Binance flatten too); document if this becomes confusing in the app
- **Deliberately scoped narrow:** `/reset` endpoint and `/reset_full` Telegram handler stay unchanged. Doctrine: paper book is in-memory simulation, but reset preservation matches live-broker safety; users get a separate explicit flatten action instead of bundling
- **Auth question carried forward:** `/reset` is owner-only, so `/close-all` mirrors that. But the user-facing motivation is "subscribers should be able to flatten their own paper book" — and there is only one global engine-side paper book, owner-controlled. If subscribers are meant to have per-user paper books, that's a Phase 4-style architectural follow-up (paired with per-user PnL ledger), not a one-line auth swap

**Lumin — branch `fix/auto-mode-above-subtabs` (dispatched in this session):**
- Currently dispatched with the **"hoist auto-execution mode card above the Live|Paper sub-tab strip"** design — keeps the tri-state Off/Paper/Live card but moves it above the sub-tab strip so the duplicate "Paper" UI semantic collision is resolved (sub-tab Paper = view filter; mode card Paper = engine global setting)
- **Discrepancy with queued design — next session needs to reconcile.** The original queued direction from this arc was *"split the tri-state mode into two per-tab on/off toggles"* (one Off/On toggle on the Live sub-tab body, a separate Off/On toggle on the Paper sub-tab body). The in-flight PR is doing hoist-above-subtabs instead. Both designs resolve the semantic collision; the split-toggle version more cleanly separates engine state from view filter. Accept hoist-above (smaller diff, ships faster) or rework to split-toggle (closer to the design summary) — owner call
- **Also still open:** `fetchTrades` Paper sub-tab passes `include_open=true` so the Paper sub-tab shows open positions instead of "No paper trades yet" — NOT included in the in-flight PR; queue as a separate small follow-up
- **Also still open:** wire a "Close all positions" button consuming engine's new `/close-all` endpoint into the Paper sub-tab so reset becomes reachable from the app — NOT included in the in-flight PR; queue as a separate follow-up that consumes the engine endpoint after both PRs merge

### Open follow-ups / next-session queue (priority order)

1. **Land + reconcile the in-flight pair.** Engine PR #403 (`feat/paper-close-all-positions`) and Lumin `fix/auto-mode-above-subtabs` are both open as non-draft PRs by this session. Verify the engine PR, then decide on the Lumin design (hoist vs split-toggle per §5). On the engine PR specifically: confirm the owner-only auth choice is intended (mirrors `/reset`; subscriber-self-flatten requires a per-user paper-book architecture, not just an auth swap).
2. **App-side wire to `/close-all`.** Once engine merges, add a "Close all positions" button on Lumin Paper sub-tab consuming `POST /api/auto-mode/paper/close-all` — this is the user-visible loop that lets reset actually be reachable.
3. **Paper sub-tab `include_open` fix.** Add `include_open=true` to `fetchTrades` so the Paper sub-tab shows open positions instead of the empty state.
4. **Verify Lumin Paper sub-tab end-to-end in production** — qty-zero, cumulative equity, reset gating, close-all loop.
5. **`deploy.yml` concurrency block** (5 LOC PR) — prevents the triple-merge cascade from 2026-05-13.
6. ~~Cleanup duplicate logger configure (`src/utils.py` + `src/logger.py`)~~ — **shipped** as `e05a5fb` (PR #405, 2026-05-16). Sink config consolidated in `src/logger.py` as the single configurer; `src/utils.py` re-exports the loguru handles and keeps the `_LoguroBridge` formatting wrapper, so all 127 `from src.utils import get_logger` call sites are unchanged. The 2026-05-14 dual-configure import-order race (which produced the `/ws_log` "exists but empty" symptom) is eliminated; the regression test pinning the hotfix invariant still passes unchanged because the unified architecture naturally satisfies it.
7. **Forensic on #380 boot failure** → CI smoke test design (`docker compose up engine → curl /api/health` in 60s).
8. **Path-2 emission watch** — PR #363 widened VSB/BDS gates 2026-05-11 but truth-report still shows ~1 emission across both. After the blacklist + 1-2 weeks of additional data, re-check whether the widening delivered or whether Path 2 needs another pass.
9. **Learned per-pair penalty (option 3)** — architectural fix for the per-pair PnL bleed; owner sign-off required before coding.
10. **Phase 4 — per-user PnL ledger** — closes B12 daily-loss-kill-switch gap; unblocks honest per-user PnL on the Lumin Trade tab.
11. **Per-symbol exposure cap** — paired with Phase 3c position view; B12 gap.
12. **Android foreground service** for true backgrounded auto-trade (Phase 3.5).
13. **Shared LIVE-flip confirmation modal helper** — duplicated between Trade tab and Auto-trade settings page.

### VPS state after this arc

- Engine running on PR #401 code with the new SQLite per-trade store + reset endpoint + qty-zero guard + cumulative-equity property
- `SCAN_SYMBOL_BLACKLIST` env extended with SIREN/TON/VVV; existing positions on those pairs will close naturally
- Firebase verifier wired; both Firebase ID tokens and legacy phone-OTP user-id JWTs accepted during cutover (deprecation of legacy path is post-Phase-4)
- Auto-trade gates from 2026-05-13 arc unchanged (concurrent-position cap, reduce-only stops, leverage ≤ 30×); B12 still has the two known gaps (daily-loss kill switch, per-symbol exposure cap)

---

## Previous Phase — 2026-05-14 (WS blackout post-mortem + Real-data-first diagnostic rule)

**End-of-day 2026-05-14 — multi-hour WS blackout traced to a Binance path-migration deadline; new "real-data-first" diagnostic rule added to CLAUDE.md.** This session spent most of its hours on a single bug chain that turned out to be a vendor-API change we missed, plus a few hours of operational work on yesterday's #380 fallout. Recovered by end of day. Engine receiving 57K+ TEXT frames in 3 min post-fix.

### 1. Engine emission-blackout root cause: Binance `/market/` routed path (PR #394)

Binance Futures decommissioned legacy WebSocket paths (`/ws`, `/stream`) on 2026-04-23 per the 2023-12-15 "Important WebSocket Change Notice." Connections without a routed path (`/public`, `/market`, `/private`) silently refuse to forward `/market` streams — TCP+WS handshake succeeds, PING/PONG keeps the connection alive, but zero application-layer frames ever arrive. All streams this engine subscribes to (`@kline_*`, `@forceOrder`) belong to `/market`.

We discovered this only after burning six prior PRs trying to fix the symptom from the codebase. The actual fix:

- New URL form: `wss://fstream.binance.com/market/stream?streams=<s1>/<s2>/...`
- `WebSocketManager._build_combined_stream_url` normalises any pre-2026-04-23 legacy suffix (`/ws`, `/stream`, `/market/ws`) back to the documented `/market/stream` form, so env drift can't silently re-break this.
- 10-test coverage in `TestBuildCombinedStreamUrl` includes a pinning test on the config defaults so a future revert can't slip through.

**Result:** 09:46-09:51 UTC trace pull post-deploy shows:
- `stream_summary conn=0 active=200/200 silent=0 never_seen=0 msg_types=TEXT=57070` (in ~3 min)
- `stream_summary conn=1 active=100/100 silent=0 never_seen=0 msg_types=TEXT=14051`
- `futures_liq active=10-14/75` (forceOrder only fires on real liquidations — `never_seen` for symbols with no recent liq is expected; growing as more pairs see liquidations)
- "No silent alert since boot" (owner-confirmed)
- Engine resuming signal emission

### 2. Six prior PRs that found real bugs along the way (but not THE bug)

Necessary debug instrumentation that surfaced the data needed to find the actual root cause:

| PR | Bug fixed | Why it didn't fix the blackout |
|---|---|---|
| #387 | Dormant spot WS scaffolding | Hygiene — spot manager was a no-op already; cleanup made code clearer for the bug-hunt |
| #388 | URL form `/ws/s1/s2/...` (path-component concat) | Right direction (combined-stream), wrong endpoint — `/stream` is also legacy post-2026-04-23 |
| #389 + #390 | WS trace log to file + `/ws_log` Telegram pull + duplicate-logger-configure sink-survival hotfix | Made the bug visible — without the trace, we'd still be guessing |
| #391 | Defensive URL normalization | Framework was correct; just normalising to the wrong target path |
| #392 + (regression test in same PR) | `_health_check_loop` was defined but never scheduled — PR #386 + #389 features were dead in prod | Made `stream_summary` actually fire, surfaced `never_seen=ALL` pattern |
| #393 | Raw-message sampling + BINARY/gzip frame handler + per-msg-type counts | Confirmed `msg_types=(none)` — definitive proof no application data of any type was arriving |
| **#394** | **`/market/` routed path** | **Actual root cause — the API path change.** |

The chain wasn't wasted work — each PR's instrumentation gave us the next layer of evidence. But six PRs could have been one if we'd checked Binance's changelog first.

### 3. Yesterday's #380 fallout + Lumin position-state desync (PRs #382, #385)

Started the day recovering yesterday's auto-trade VPS-proxy revert (#382). Then surfaced a position-state desync where Lumin app showed positions ACTIVE that had clearly hit SL on Binance — same root WS bug, but visible to users via the Trade tab. Shipped:

- **PR #382** (revert #380) — engine recovered from 24h boot kill (~30s after merge auto-deployed). 90% of the work was diagnostic; revert itself was 5 lines.
- **PR #385** (`/internal/diag/positions`) — engine-side endpoint surfacing `(signal_id, symbol, status, stored SL, candle_1m_high/low, candle_1m_age_sec, sl_breach_distance_pct)` per active signal. Owner-tier auth, defensive at builder + endpoint level. Designed to be consumed by the 360 CE Ops dashboard `/positions` view (queued).
- 360 CE Ops PR #3 (companion dashboard view) — opened in `360ce-ops` repo, not yet merged.

### 4. New diagnostic rule added to CLAUDE.md: "Real-data-first diagnosis"

The owner-flagged lesson from this session: **when subscriber-visible symptoms appear at a vendor-API boundary, check the vendor's changelog / deprecation announcements BEFORE patching engine code.** Codified in a new dedicated CLAUDE.md section between "Telemetry & Diagnosis" and "What Requires Owner Sign-off," with a corresponding line added to "Hard Limits — Never Negotiable":

> Never start patching engine code in response to a vendor-API symptom before checking the vendor's changelog + recent announcements.

Specific diagnostic order of operations in the new section:

1. Read the wire (real data from prod via Telegram-deliverable log / diag)
2. Check vendor changelog (`developers.binance.com/docs/derivatives/change-log` etc.)
3. Search vendor announcements (`binance.com/en/support/announcement`)
4. Verify externally (different IP / browser-based tester) — distinguishes "our code/IP wrong" from "vendor degraded globally"
5. THEN consider code-side fixes

This rule retroactively explains why this session's debug loop was so long: every step assumed the bug was in our code because that's where the symptoms appeared. The rule prevents the next session from repeating the loop.

### Telemetry / observability now in place (carried forward as live tooling)

- `/internal/diag/positions` endpoint (PR #385) — operator X-ray of TradeMonitor's view of every active signal
- `logs/ws_trace.log` with dedicated loguru sink (PR #389 + #390 hotfix) — captures every WS lifecycle event tagged `<WS:LABEL>` with `connect_start`, `connect_success`, `connect_fail`, `first_data`, `subscribe_ack`, `subscribe_error`, `close_received`, `error_received`, `watchdog_force_close`, `health_force_close`, `per_symbol_force_close`, `stream_summary`, `raw_sample`
- `/ws_log` Telegram command (PR #389) — pulls the trace file as a Telegram document; `/ws_log <N>` for last N lines
- `_health_check_loop` actually scheduled (PR #392) — per-symbol staleness + msg-rate force-close + periodic `stream_summary` now run for real
- BINARY/gzip frame handler (PR #393) — defensive against future Binance binary-encoded variants

These survived the incident and are valuable steady-state. Don't rip them out.

### Open follow-ups / next-session queue (priority order)

1. **Verify Lumin Trade tab shows clean state** — after #394's data flow resumed, positions should now update correctly. Owner to confirm visually.
2. **`deploy.yml` concurrency block** (5 LOC PR) — prevents the triple-merge cascade we hit yesterday on PR #383/#384/#385.
3. **Cleanup duplicate logger configure** — both `src/utils.py` and `src/logger.py` call `_loguru_logger.remove()`; PR #390 hotfixed the immediate bug but unification is queued.
4. **Forensic on #380 boot failure** — what specifically about the auto-trade-VPS-proxy PR killed engine boot. Informs CI smoke test design.
5. **CI smoke test for engine boot** — `docker compose up engine → curl /api/health → assert 200` in 60s. Would have caught #380 in CI; informed by #4.
6. ~~`360 CE Ops` PR #3 merge~~ — **merged** as `e78fea4` (2026-05-14). Signals "Created" column + `/positions` diag view consuming `/internal/diag/positions` are live in the dashboard.

Week 2 backlog (architectural):

- Split `trade_monitor.py` (1656 LOC god-object) into `monitor/poll.py` + `monitor/evaluate.py` + `monitor/lifecycle.py`
- Reorganize `src/` into subpackages (`signal/`, `lifecycle/`, `observability/`, `exchange/`)
- Establish PR discipline rules: ≤500 LOC, smoke test required, "what regresses if this breaks" line in every body

VPS state after this session:

- Engine running on PR #394 code (post-2026-04-23 routed-path URL form)
- All 300 kline streams active across 2 connections (200/100 split)
- forceOrder streams progressively populating `stream_data_ts` as liquidations occur
- `.env` may still contain pre-2026-04-23 legacy values for `BINANCE_*_WS_BASE`; the code normaliser handles this and logs a one-shot warning on each manager. Update `.env` to silence:
  ```
  BINANCE_FUTURES_WS_BASE=wss://fstream.binance.com/market/stream
  BINANCE_WS_BASE=wss://stream.binance.com:9443/market/stream
  ```

---

## Previous Phase — 2026-05-13 (per-user expansion Phase 1–3c + Lumin-is-consumer-only architectural shift)

A ~12 PR arc across `360-v2` + `lumin-app` shipped between the 2026-05-12 emission-blackout recovery and the 2026-05-14 WS blackout. This section closes the documentation gap — it wasn't recorded in real time because the WS-blackout fire-drill took the next session's bandwidth.

### Engine side (per-user data foundations)

| PR | Title | What it ships |
|---|---|---|
| #367 | Phase 1 — profile schema + signup-routing signal | Adds `display_name / country_code / timezone / currency / terms_accepted_at / onboarded_at` columns to `users`. Token responses gain `needs_onboarding: bool`. New `GET /api/profile` + partial `PUT /api/profile`. Owner row bootstrapped pre-onboarded; existing rows → NULL → routed through SignupPage on next signin. `_make_user_claims_dep` helper reused by every per-user endpoint. |
| #368 | Phase 2 — per-user pretp + auto-trade override store | New SQLite tables `user_pretp_settings` + `user_auto_trade_settings` (PK user_id, all override columns nullable = "use engine default"). New endpoints `GET/PUT /api/settings/user/pretp` + `GET/PUT /api/settings/user/auto-trade`. Parallel to (not replacing) the engine-wide `user_settings` store — engine signal-evaluation behaviour is bit-identical. `leverage_cap` clamped to B12's 30× at store layer. `mode=live` on the per-user endpoint deliberately does NOT touch engine-global state. |
| #379 | Level rearm state-machine fix | (Carried — small fix during this arc, separate from per-user expansion.) |
| #381 | LSR exempt from trend hard gate + evaluator funnel in `/diag` | LSR is counter-trend by design; the trend-family hard gate was over-blocking. Funnel surface in `/diag` adds the per-evaluator visibility that drove this fix. |

### Lumin app side (per-user UX + first-real-money execution)

| PR | Phase | What it ships |
|---|---|---|
| #11 | tier-gate writes | App-side companion to engine #355 / #356. Hides Save (rather than disables) on `/settings/pretp` + `/settings/auto-trade` when `tier != owner`. New `OwnerOnlyBanner`. Engine 403 remains the source-of-truth backstop. |
| #12 | Phase 1 | Country auto-detect (ISO-3166 table, regional-indicator emoji flags, no asset dep) → PhoneSignInPage chip → SignupPage routing fork on `needs_onboarding` from token response. New `Profile` dataclass + `GET/PUT /api/profile` wiring in repository. |
| #13 | Phase 2 | Per-user Auto-trade + Pre-TP pages re-pointed at `/api/settings/user/*`. New owner-only **Engine defaults** page for engine-wide config. Honest "Saved — takes effect Phase 3" banner under per-user pages until execution wires through. |
| #14 | Phase 3a | Per-user Binance API keys management. New `BinanceClient` (Futures HMAC-SHA256 REST), `BinanceKeysService` (`flutter_secure_storage`, per-user namespaced, `binance.user.<id>`). Test→Save gate, clock-skew sanity pre-check, friendly error mapping (-2014/-2015/-1022/-1021). |
| #15 | Phase 3b-1 | Manual "Take signal" → entry + reduce-only SL + reduce-only TP1 triplet. `OrderExecutor.placeFromSignal` sizes from `position_size_pct × leverage_cap`, rounds per symbol filters. Idempotency × 3 layers (app `OrderLog`, broker `newClientOrderId=lumin-<id>-entry`, Confirm-button disable). B12 leverage clamp + reduce-only stops + minQty/minNotional pre-flight. |
| #16 | Phase 3b-2 | `AutoTradeWatcher` — 15s poll, fires ACTIVE signals when user's mode is `paper`/`live`. Real-money confirmation modal on LIVE flip. Sticky AUTO LIVE / PAPER / PAUSED banner above NavShell with kill switch. One-firing-per-tick throttle. `AppLifecycleState.paused` stops watcher (Android foreground service deferred to Phase 3.5). |
| #17 | Trade-tab mode fix | Bugfix: Trade tab Off/Paper/Live pills were still calling engine-wide `/api/auto-mode` (owner-gated 403). Re-pointed at per-user `/api/settings/user/auto-trade`. LIVE-flip confirmation modal now gated on both entry points. |
| #18 | Lumin = consumer-only | **Architectural pivot.** Stripped all operator chrome: admin-token signin panel, anonymous-skip debug, LUMIN BACKEND card, /api/health Test connection, Engine-defaults page, Agents settings, Risk-gates page, dead Appearance/Language stubs, `OwnerOnlyBanner` (unused after this strip). Added Profile settings page + top-level Sign out entry. Settings surface after cleanup: AUTO-TRADE (Auto-trade + Pre-TP + Binance) + ACCOUNT (Profile + Subscription + About + Sign out). Owner now signs into Lumin via phone OTP like every tester. **Operator surfaces relocate to 360 CE Ops dashboard + a planned separate "ops APK"** (not yet built — design summary filed). |
| #19 | Phase 3c | Trade tab renders **live Binance positions** (real `BinancePosition` data class + signed `getOpenPositions()`) when user has keys connected; engine paper view stays as fallback when no keys / fetch errors. `_ModePnlCard` relabels to "ENGINE PAPER P&L (not yours)" until Phase 4 per-user PnL. **Concurrent-position cap enforcement** — one-liner guard in `AutoTradeWatcher._fireOne` using the existing `getAccount` call (no new round-trip). |

### 360 CE Ops dashboard

- **PR #3 merged** (2026-05-14, `e78fea4`) — Signals page "Created" column now populates (engine surfaces creation time as `timestamp`, not `created_at`; normalizer fixed). New `/positions` route consuming engine `/internal/diag/positions` (PR #385), with per-row risk classification (`sl_breached` / `feed_stale` / `ok`) sorted urgent-first. +25 new tests, 32 passing.

### Doctrinal implications

**Lumin is now strictly consumer-only.** OWNER_BRIEF B15 ("Lumin = consumer app brand") shifted from naming-only to behaviourally enforced via #18. The operator workflow is now:

| Surface | Pre-#18 | Post-#18 |
|---|---|---|
| Engine auto-mode flip (off/paper/live) | Lumin Trade tab + Settings → Auto-trade | 360 CE Ops (not yet wired — see follow-up) + Telegram `/automode` |
| Engine-wide pre-TP config | Lumin Settings → Engine defaults | 360 CE Ops (not yet wired) + env vars / Telegram |
| Agents toggle, Risk gates | Lumin Settings | 360 CE Ops (not yet wired) |
| Admin-token signin | Lumin PhoneSignInPage | Removed entirely — owner uses phone OTP in Lumin like every user |
| Mock/Live data-source toggle | Lumin API keys page | Removed — only live |
| Per-user Auto-trade / Pre-TP / Binance keys | Lumin Settings | **Unchanged** — these are subscriber-facing |

**B12 status after #15/#16/#19** (auto-trade safety checklist — `OWNER_BRIEF.md`):

| Gate | Status |
|---|---|
| Leverage cap ≤ 30× | ✅ enforced (`clamp(1, 30)` in `OrderExecutor`; engine PR #368 also clamps at store layer) |
| Reduce-only SL / TP | ✅ enforced (`closePosition=true` on SL, `reduceOnly=true` on TP) |
| Concurrent-position cap | ✅ enforced (Phase 3c, honest count from Binance `getAccount`) |
| Idempotency (no double-fire) | ✅ × 3 layers (app log + broker `newClientOrderId` + UI disable / one-per-tick throttle) |
| Restart reconciliation | ✅ engine-side (`PositionReconciler`); app-side relies on Binance state being canonical |
| Daily-loss kill switch | ❌ **GAP** — needs per-user PnL ledger (Phase 4) |
| Per-symbol exposure cap | ❌ **GAP** — explicit owner trade-off for v0 (closed-beta cohort mitigates via small `position_size_pct`) |
| Structured order audit log | ✅ `OrderLog` (per-user, 200 entries, secure storage) |

Until the two gaps close, paid-subscriber LIVE-mode autonomy is acceptable only with conservative settings (`position_size_pct ≤ 1%`, `leverage_cap ≤ 3x`, `max_concurrent_positions ≤ 1–2`). The real-money confirmation modal makes this trade-off owner-visible at the moment of opt-in.

### Open follow-ups from this arc (carried forward)

1. **Ops APK / web ops surface for engine-wide controls** — design summary filed at the bottom of `lumin-app` PR #18. Engine auto-mode flip, agents toggle, risk gates, monitor-logs viewer need a home. 360 CE Ops dashboard already covers read-only diagnostics; writes are a separate question (CLAUDE.md hard limit: "No writes to engine state from this dashboard"). Owner decision needed on whether to broaden 360 CE Ops' scope or ship a separate ops APK.
2. **Phase 4 — per-user PnL ledger** — closes the daily-loss kill-switch gap (B12) and lets `_ModePnlCard` show the user's own P&L instead of the engine paper trader's.
3. **Per-symbol exposure cap** — paired with Phase 3c position view; same data source, separate guard.
4. **Android foreground service** for true auto-trade autonomy when app is backgrounded (Phase 3.5).
5. **Shared LIVE-flip confirmation modal helper** — currently duplicated between Trade tab and Auto-trade settings page (called out in #17 description).

---

## Previous Phase

**End-of-day 2026-05-12 — engine recovered from 24h blackout, Telegram OTP shipped, identity-flow doctrine pivoted.** This session ran ~12 hours and resolved three things in sequence:

### 1. Engine emission-blackout: diagnosed → fixed → live (PRs #373 + #374)

Yesterday's signal-quality 5-PR batch (#359–#363) introduced a regression that wasn't visible until today's truth-report fetch revealed `kept=2159` for SR_FLIP_RETEST with `Emitted=0`. The data-staleness gate from PR #359 (`_is_kline_data_fresh`) was fail-CLOSED on `age is None`, and `_last_kline_update_ts` is stamped only inside `update_candle` — called only from live WS frame handlers. After every restart there's a window where REST-seeded candles populate the store but no WS frame has stamped a timestamp yet. Combined with a separate WS-handshake bug (silent connections at boot until the 903s watchdog fires), this killed every dispatch attempt for ~15 minutes per restart cycle, accumulating to 24h+ silence.

Diagnostic chain:

- **PR #373 — Dispatch-funnel instrumentation.** Added `enqueue_stage:{stage}:{setup_class}` counters at every rejection point in `_enqueue_signal` + at successful queue.put. Promoted the global directional cooldown skip from DEBUG → INFO. Added new `--- DISPATCH FUNNEL (per setup_class) ---` section in `/diag` that aggregates the counters into a per-evaluator table.
- The very first `/diag` post-PR-#373 made `data_stale` the dominant column for SR_FLIP_RETEST — and the WS health card showed `sec_since_last_msg=704s` ≈ entire uptime. Smoking gun.
- **PR #374 — Data-staleness gate fail-open on `age is None`.** Doctrinal fix matching `_is_pair_structurally_aged` (which fails-open on missing accessor). The QUSDT-class detection that PR #359 was designed for is preserved by the `age > MAX_KLINE_STALENESS_SEC` branch, which still hard-blocks once a single live frame has been observed.

Within minutes of PR #374 auto-deploy → owner confirmed signals flowing again.

### 2. OTP delivery: Telegram bot DM shipped + critical schema bug squashed (PRs #N1 + #N2)

Tonight's pivot to a viable OTP path. The Twilio/WhatsApp/AWS-SNS detour hit walls — Meta business verification needs documents the owner doesn't have (no GST/Pvt Ltd registration), AWS SNS to Indian numbers needs DLT registration (3–7 days), Twilio WhatsApp production sender needs Meta-verified business. All slow paths.

- **PR #N1 — `TelegramOtpProvider` (engine).** Sends OTPs as Markdown-formatted DMs via the existing `@LuminProBot` instance, looked up by `phone_e164` in UserStore → `telegram_chat_id`. Missing chat_id returns `UNSUPPORTED_CHANNEL` so the chain falls through to fallback. Aligns with the existing PR #356 infrastructure (UserStore, OtpStore, billing webhook).
- **PR #N2 — `OtpRequestResponse` literal hotfix.** The response Pydantic schema's `channel_used: Literal["whatsapp", "sms", "log"]` rejected `"telegram"` at validation time, causing 500s after the DM had already shipped. One-line fix.

End-to-end test confirmed: OTP `691981` arrived in owner's `@LuminProBot` DM within ~2 seconds. App login flow validated.

VPS state after this session:
- `OTP_PRIMARY_CHANNEL=telegram`, `OTP_FALLBACK_CHANNEL=log`
- `OWNER_PHONE_E164=+919618579123` (bootstraps user_id=1)
- `users` table has owner row with `telegram_chat_id=710718010` (manually set; auto-bind handler is the next task)

### 3. Identity-flow doctrine: pivot from B13-strict to phone+SMS-primary + Telegram-optional

Original OWNER_BRIEF B13 declared Telegram-only ("No email, no password, no SMS auth"). That was viable when the assumption was "all our users have Telegram" — true for a Telegram-channel-fed closed beta. False once Lumin is a real consumer app where a chunk of users won't have Telegram installed (~5-15% of even crypto-aware audiences).

Doctrinal call this session (CTE, owner-confirmed): **flip B13 to phone+SMS primary, Telegram bot as opt-in upgrade.**

- Primary: phone → SMS OTP. Any user, any phone, no prerequisites. Via AuthKey.io (Indian DLT-registered provider) at ~₹0.13/SMS.
- Opt-in upgrade: from app Settings, user can bind their Telegram chat_id via `@LuminProBot` `/start <phone>` deep link. Future codes route via the (free) Telegram DM instead of (paid) SMS.
- Identity primitive remains `telegram_user_id` for paid-tier features per B16 (billing webhook, signal routing, ops console access).
- OWNER_BRIEF B13 amended in this same docs PR.

### Tomorrow / queued

| Task | Notes |
|---|---|
| AuthKey.io signup + DLT template submission | Owner side, ~20 min + ~24h DLT clearance |
| `AuthKeyOtpProvider` engine PR | CTE, ~80-line provider class + env vars + tests |
| `@LuminProBot` `/start <phone>` bind handler | CTE, ~30 lines in the bot dispatch path |
| App-side: channel-hint UI + "Bind Telegram for free codes" Settings entry | CTE via lumin-app installer PR |
| Rotate leaked `TELEGRAM_BOT_TOKEN` | Owner — token appeared in chat transcript today; rotate via @BotFather `/revoke` before bed |

### Still pending from earlier in the session (carried)

- WS silent-at-boot investigation + watchdog timeout drop (15min → 3min, env-overridable). Lower priority now that PR #374's fail-open absorbs the impact, but root cause unidentified.
- `signal_history.json` vs `signal_performance.json` sync gap surfaced today (app showed 1 closed signal, `/stats` showed 2). PR #305 backfills at boot; needs continuous reconciliation.
- `dispatch_cooldown` persistence across restarts blocked at least one fresh paid signal today. Default 30min may be too long for current low-emission state; env-override or `/reset_cooldown` Telegram command worth considering.
- Multi-strategy-confluence direction-clash silent skip (instrumentation hole identified during today's diagnostic). Adding `enqueue_stage:confluence_dir_clash` counter is a small follow-up.

### Tester invites

**Still blocked** pending: (a) AuthKey SMS in production so non-owner phones can sign up self-service; (b) 24h observation of post-#374 emission rate to confirm signals are landing reliably; (c) `/start` bind command so testers can opt-in to Telegram OTP and ongoing bot features.

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
- **Lumin Phase 1+2+3a+3b+3c shipped (2026-05-13):**
  - **Phase 1 (#12):** Country auto-detect chip on PhoneSignInPage; SignupPage routing fork on `needs_onboarding` from token response (engine #367). Owner pre-onboarded; existing testers see SignupPage once.
  - **Phase 2 (#13):** Per-user Auto-trade + Pre-TP pages re-pointed at `/api/settings/user/*` (engine #368). Owner-only Engine-defaults page (relocated to ops surface in #18).
  - **Phase 3a (#14):** Per-user Binance API keys in `flutter_secure_storage` (namespaced `binance.user.<id>`). Test→Save gate. Friendly error mapping for Binance error codes. Clock-skew pre-check.
  - **Phase 3b-1 (#15):** Manual "Take signal" places entry + reduce-only SL + reduce-only TP1 triplet against user's Binance account. Idempotency × 3 layers. B12 leverage clamp + minQty pre-flight.
  - **Phase 3b-2 (#16):** `AutoTradeWatcher` polls `/api/signals` every 15s and autonomously fires ACTIVE signals when user's per-user `mode` ∈ {`paper`, `live`}. Sticky AUTO banner + kill switch. Real-money confirmation modal on LIVE flip. One-firing-per-tick throttle. Watcher pauses on `AppLifecycleState.paused`.
  - **Phase 3c (#19):** Trade tab shows real Binance positions when keys connected; engine paper view stays as fallback. `_ModePnlCard` honestly labelled "ENGINE PAPER P&L (not yours)" until Phase 4. **Concurrent-position cap enforced** in `AutoTradeWatcher._fireOne` using Binance's `getAccount().openPositionCount`.
  - **Lumin = consumer-only (#18):** All operator chrome stripped from Lumin (admin-token signin, Engine-defaults page, Agents settings, Risk-gates page, `/api/health` Test, Mock/Live toggle, OwnerOnlyBanner). Owner signs into Lumin via phone OTP like every tester. Operator surfaces relocate to **360 CE Ops dashboard + planned ops APK**.
- **Lumin app v0.0.22+22** (current — Phase 3c shipped).

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
| #321 | Wire VolumeProfile + StructureTracker into scoring stack | ✅ merged |

### Day 3 — 360 CE Ops *(2026-05-11/12)*
| PR | Title | Status |
|---|---|---|
| 360ce-ops #1 | Bootstrap 360 CE Ops — full MVP (pulse + truth + signals + diag + invalidations + performance) | ✅ merged |
| 360ce-ops #2 | CI hotfix: remove `secrets` from step-level `if:` | ✅ merged |
| #371 | Docs: 360 CE Ops shipped (companion to 360ce-ops PRs) | ✅ merged |
| #372 | Docs: 360 CE Ops live at ops.luminapp.org | ✅ merged |

### Day 4 — Emission-blackout recovery + Telegram OTP *(2026-05-12)*
| PR | Title | Status |
|---|---|---|
| #373 | Instrument `_enqueue_signal` with `enqueue_stage` counters + per-path `/diag` funnel | ✅ merged |
| #374 | Fail-open data-staleness gate when no kline timestamp stamped yet | ✅ merged |
| #376 (`#N1`) | `TelegramOtpProvider` — OWNER_BRIEF B13 alignment + B13 amendment scope | ✅ merged |
| #377 (`#N2`) | `OtpRequestResponse` literal hotfix (allow "telegram") | ✅ merged |

### Day 5 — Per-user expansion Phase 1–3c + Lumin consumer-only shift *(2026-05-13)*

Engine (`360-v2`):

| PR | Title | Status |
|---|---|---|
| #367 | Phase 1 — profile schema + `needs_onboarding` signal + GET/PUT `/api/profile` | ✅ merged |
| #368 | Phase 2 — per-user pretp + auto-trade override store + `/api/settings/user/*` | ✅ merged |
| #379 | Level rearm state-machine fix | ✅ merged |
| #381 | LSR exempt from trend hard gate + evaluator funnel in `/diag` | ✅ merged |

Lumin app (`lumin-app`):

| PR | Title | Status |
|---|---|---|
| #11 | Tier-gate write controls — hide Save + read-only form for non-owner | ✅ merged |
| #12 | Phase 1 — country auto-detect + signup routing on `needs_onboarding` | ✅ merged |
| #13 | Phase 2 — per-user settings + owner Engine-defaults page | ✅ merged |
| #14 | Phase 3a — per-user Binance keys management + Test connection | ✅ merged |
| #15 | Phase 3b-1 — manual Take-signal order placement (entry + reduce-only SL/TP1) | ✅ merged |
| #16 | Phase 3b-2 — autonomous order placement on signal arrival + AUTO banner kill switch | ✅ merged |
| #17 | Trade-tab mode toggle writes per-user (fixes 403) | ✅ merged |
| #18 | Strip operator chrome — Lumin is consumer-only | ✅ merged |
| #19 | Phase 3c — live Binance positions + concurrent-position cap enforcement | ✅ merged |

### Day 6 — 2026-05-14 WS blackout *(documented in "Current Phase" at top of this file)*

| PR | Title | Status |
|---|---|---|
| #382 | Revert PR #380 — auto-trade VPS proxy boot-failure recovery | ✅ merged |
| #383/#384/#385 | `/internal/diag/positions` endpoint (triple-merge cascade — bug informing the deploy.yml concurrency follow-up) | ✅ merged |
| #386 | Drop futures staleness 15→5 + msg-rate watchdog + per-symbol staleness | ✅ merged |
| #387 | Rip dormant spot WebSocket scaffolding (futures-only engine) | ✅ merged |
| #388 | Use Binance-doc-compliant combined-stream URL format | ✅ merged (but path was still legacy — see #394) |
| #389 + #390 | WS trace log + `/ws_log` Telegram pull + sink-survival hotfix | ✅ merged |
| #391 | Normalize WS base URL to `/stream` | ✅ merged (still wrong path — see #394) |
| #392 | Start `_health_check_loop` — was defined but never scheduled | ✅ merged |
| #393 | Raw msg sample + BINARY frame handler + msg-type counts in `stream_summary` | ✅ merged |
| #394 | **Use `/market/` routed path — Binance decommissioned legacy `/ws` and `/stream` on 2026-04-23** | ✅ merged (actual fix) |
| #395 | Docs — WS blackout post-mortem + Real-data-first diagnostic rule in CLAUDE.md | ✅ merged |

360 CE Ops (`360ce-ops`):

| PR | Title | Status |
|---|---|---|
| #3 | Signals timestamps + `/positions` diag view consuming `/internal/diag/positions` | ✅ merged 2026-05-14 |

End-of-session test count: **>3978 passed**, 0 failures, 0 regressions.

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
- **Operator surface after Lumin consumer-only shift (#18)** — the engine auto-mode flip, engine-wide pre-TP config, agents toggles, risk-gates page, monitor-logs viewer, admin-token signin no longer live in Lumin. Choices: (a) broaden 360 CE Ops dashboard to add a thin write-surface (against its current "no writes" hard limit — see `360ce-ops/CLAUDE.md`); (b) ship a separate **ops APK** with the operator-only chrome; (c) keep operator flows on Telegram bot commands + env vars + SSH for now. Cost / latency / risk trade-off; design summary started in `lumin-app` PR #18 follow-up but not yet PR'd.

### Auto-trade B12 gaps (per-user)
- **Daily-loss kill switch** — blocked on Phase 4 (per-user PnL ledger). Until Phase 4, paid LIVE-mode autonomy is acceptable only with conservative settings; the LIVE-flip confirmation modal in app PR #16 makes this trade-off owner-visible at opt-in time.
- **Per-symbol exposure cap** — explicit owner trade-off for v0 closed-beta (cohort of 5 mitigates via small `position_size_pct`). Pair with Phase 3c position data; same source, separate guard.
- **Android foreground service** for auto-trade autonomy when app backgrounded — currently `AppLifecycleState.paused` stops the watcher and the AUTO banner flips to AUTO PAUSED. Phase 3.5 target.
- **Shared LIVE-flip confirmation modal helper** — currently duplicated between Trade tab (`trade_page.dart`) and Auto-trade settings page (`auto_trade_settings_page.dart`) per `lumin-app` PR #17. Small follow-up to avoid copy drift.

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
| Paper order manager (close_full + add_dca_entry + close_all_open_positions) | `src/paper_order_manager.py` |
| Pre-TP threshold + trigger-price stamping | `src/pre_tp_stamping.py` |
| Signal-history persistence | `src/signal_history_store.py` |
| Signal-history backfill + reconciliation | `src/signal_history_backfill.py` |
| Truth report parser | `src/runtime_truth_report.py` |
| Invalidation audit | `src/invalidation_audit.py` |
| API server + auth | `src/api/server.py`, `src/api/auth.py` |
| API snapshot adapters | `src/api/snapshot.py` |
| Paper-trade API routes (`/api/trades`, `/api/auto-mode/paper/reset`, `/api/auto-mode/paper/close-all` in-flight) | `src/api/paper_trade_routes.py` |
| Paper-trade SQLite store | `src/auto_trade/trade_records.py` |
| Macro watchdog | `src/macro_watchdog.py` |

### Lumin app
| Concern | File |
|---|---|
| App shell + nav | `lib/main.dart`, `lib/app/nav_shell.dart` |
| HTTP client + auth | `lib/data/api_client.dart`, `lib/data/auth_service.dart` |
| Repository abstraction | `lib/data/repository.dart` (includes `Profile` + per-user settings methods from Phase 1+2) |
| Config + InheritedWidget | `lib/data/app_config.dart` (exposes `userId`, `tier`, `autoTradeWatcher` singleton) |
| Country codes table | `lib/data/country_codes.dart` (Phase 1) |
| Binance client (signed Futures REST) | `lib/data/binance_client.dart` (Phase 3a/3b/3c — includes `BinancePosition`, `getOpenPositions`, `createMarketOrder`, `createStopOrder`, `BinanceSymbolFilters.roundQty/roundPrice`) |
| Per-user Binance keys (encrypted) | `lib/data/binance_keys_service.dart` (Phase 3a — `flutter_secure_storage`, per-user namespace) |
| Order executor (entry + SL + TP1) | `lib/data/order_executor.dart` (Phase 3b-1) |
| Per-user signal → broker order log | `lib/data/order_log.dart` (Phase 3b-1 — idempotency layer) |
| Auto-trade watcher (autonomous order placement) | `lib/data/auto_trade_watcher.dart` (Phase 3b-2 — polls signals, fires triplet, AUTO banner state) |
| Auto-trade sticky banner | `lib/features/auto_trade/auto_trade_indicator.dart` (Phase 3b-2) |
| Format helpers | `lib/shared/format.dart` (added v0.0.9) |
| Trade tab (Live | Paper sub-tabs; auto-mode card hoist in-flight) | `lib/features/trade/trade_page.dart` |
| Paper trades list + detail | `lib/features/trade/paper_trades_page.dart`, `lib/features/trade/paper_trade_detail_page.dart` |
| Pages | `lib/features/{pulse,signals,trade,settings,auth,update,auto_trade}/` |
| Theme + tokens | `lib/theme.dart`, `lib/shared/tokens.dart` |
| Shared widgets | `lib/shared/widgets/` (PreviewBadge, LuminCard, StatPill — `OwnerOnlyBanner` deleted in #18 with operator chrome strip) |

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
