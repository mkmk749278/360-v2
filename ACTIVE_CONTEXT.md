# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## Current Phase

**End-of-day 2026-05-16 — Firebase auth migration shipped (engine + Android), paper-trade visibility shipped with two latent paper-broker bugs squashed (`qty=0` open positions, daily-resetting equity), and a definitive pair-bleed diagnosis ruled out the movers path and placed all current PnL bleed on Path-1 SMC evaluators against specific top-75 pairs.** Two-day arc (2026-05-15 → 2026-05-16) covering identity-stack migration, subscriber-visible paper-trader honesty, and an env-only blacklist of three confirmed-bad pairs while the architectural fix (learned per-pair penalty) is queued.

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

### Open follow-ups / next-session queue (priority order)

1. **Trade-tab UX redesign** — Live sub-tab still shows the redundant Off/Paper/Live mode toggle alongside the new Live|Paper sub-tab strip; Paper sub-tab shows "No paper trades yet" because `fetchTrades` doesn't pass `include_open`; reset is practically unreachable because there are almost always open positions. Owner-confirmed direction: split the tri-state mode into two per-tab on/off toggles + add a `POST /api/auto-mode/paper/close-all` so reset is reachable. Engine + Lumin PR pair queued for this session.
2. **Verify Lumin Paper sub-tab in production** — once the close-all + dual-toggle PRs ship, confirm reset/qty-zero/cumulative-equity fixes look right end-to-end
3. **`deploy.yml` concurrency block** (5 LOC PR) — prevents the triple-merge cascade from 2026-05-13
4. **Cleanup duplicate logger configure** (`src/utils.py` + `src/logger.py`) — PR #390 hotfixed; unification queued
5. **Forensic on #380 boot failure** → CI smoke test design (`docker compose up engine → curl /api/health` in 60s)
6. **Path-2 emission watch** — PR #363 widened VSB/BDS gates 2026-05-11 but truth-report still shows ~1 emission across both. After the blacklist + 1-2 weeks of additional data, re-check whether the widening delivered or whether Path 2 needs another pass
7. **Learned per-pair penalty (option 3)** — architectural fix for the per-pair PnL bleed; owner sign-off required before coding
8. **Phase 4 — per-user PnL ledger** — closes B12 daily-loss-kill-switch gap; unblocks honest per-user PnL on the Lumin Trade tab
9. **Per-symbol exposure cap** — paired with Phase 3c position view; B12 gap
10. **Android foreground service** for true backgrounded auto-trade (Phase 3.5)
11. **Shared LIVE-flip confirmation modal helper** — duplicated between Trade tab and Auto-trade settings page

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
