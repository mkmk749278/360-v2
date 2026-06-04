# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## Session 18 checkpoint 2026-06-04 — monitoring agent live + scan latency fixed (64s → ~3s)

### What shipped this session (6 PRs merged to `main`)

| PR | Repo | What | Type |
|---|---|---|---|
| #583 | 360-v2 | `/internal/diag/tasks` endpoint (owner-tier) | feat, auto-merged |
| #584 | 360-v2 | Engine task census published to Redis (D2 re-enable) | feat, auto-merged |
| #585 | 360-v2 | Signing-client 16 MiB socket read buffer (reconciler overflow fix) | fix, auto-merged |
| #586 | 360-v2 | Per-stage scan timing instrumentation | feat, auto-merged |
| #587 | 360-v2 | SMC result cache + indicator fingerprint (insufficient — see #588) | fix, auto-merged |
| #588 | 360-v2 | Per-timeframe indicator caching (the real scan-latency fix) | fix, auto-merged |
| #6/#7/#9/#10 | 360ce-ops | Monitoring agent deployed (Tier 0 + Tier 2 healthchecks.io) | feat, merged |

### Monitoring agent (360ce-ops) — fully operational

24/7 monitoring agent deployed as a separate Docker container (`360ce-ops-agent`) on the VPS.

**Architecture:**
- **Tier 0** — 7 deterministic detectors polling every 60s, paging Telegram on money-path failures
- **Tier 2** — healthchecks.io dead-man switch (Period=1min, Grace=2min), green since 08:02

**Active detectors:**

| ID | Name | Fires when |
|---|---|---|
| D1 | NakedPositionDetector | Position with `entry>0`, valid symbol, `stop_loss≤0` for >1 cycle |
| D2 | BackgroundTaskDetector | Any of `trade_monitor / reconciler / mark_price_feed / funding_exit_watcher` absent from task census |
| D3 | AutoModeDisabledDetector | `auto_mode=false` for >15 min |
| D4 | StaleSnapshotDetector | Engine snapshot not updated in >90s |
| D6 | BinanceKeyMissingDetector | Binance key disconnected |
| D7 | PositionCountAnomalyDetector | Open position count changes by >5 in one cycle |
| D8 | RedisIdleDetector | `snapshot:tickers` Redis key idle >120s |

**False positives eliminated:**
- D1: requires `symbol != ""` and `entry > 0.0` — ignores Redis-facade signal-tracking placeholders
- D2: empty census (unavailable) treated as `[]` skip, not "all dead"
- D5 (heartbeat_stale): removed entirely — file mtimes don't correlate with scan cycles

**Known limitation (D1):** reads `sig.stop_loss` geometry, cannot detect the real case (valid SL price, Binance stop order not yet confirmed). Proper fix requires engine to publish `sl_order_id` per position to Redis snapshot. Tracked as follow-up.

### PR #585 — reconciler positionRisk overflow (confirmed fixed)

Root cause: `asyncio.open_unix_connection` default 64 KiB `readline` limit raised
`ValueError: Separator is not found, and chunk exceed the limit` when
`/fapi/v2/positionRisk` returned >64 KiB of JSON (all symbols, no filter).
Fix: raised `_SOCKET_READ_LIMIT` to 16 MiB. Confirmed working — empty grep for
`Separator is not found` in VPS logs post-deploy.

### Scan latency — root cause + fix (#587 then #588), CONFIRMED FIXED

**Production timing that drove the work (`smc_indicators` summed / cycle wall-clock):**
```
{'smc_indicators': 758.51, ...}  cycle=71.8s
{'smc_indicators': 866.61, ...}  cycle=75.3s
```

**Two distinct bugs, fixed across two PRs:**

1. **SMC never cached** (#587) — `smc_detector.detect` ran fresh every cycle even though
   sweeps / FVGs / orderblocks are deterministic on completed candles. Added `_smc_cache`
   keyed on closed 5m+ candle counts. **This part worked.**

2. **Indicator cache used one whole-dict fingerprint including 1m** (#587 got this wrong;
   #588 fixed it). A new 1m candle closes ~every cycle, so the combined fingerprint
   changed every cycle and invalidated indicators for ALL 7 timeframes — 5m..1w were
   recomputed needlessly. #587 showed **no improvement in prod** (541-822s) because the
   single timing bucket lumped SMC + indicators, masking the working SMC cache.

**#588 fix (the real win):** indicator cache keyed PER TIMEFRAME — `symbol → {tf: (len, ind)}`.
Only timeframes whose candle count changed recompute. 1m recomputes every cycle (scalping
needs the live bar); 5m..1w hit ~95%. Telemetry split into separate `smc` / `indicators`
buckets to make it self-verifying.

**Confirmed in production (post-#588):**
```
cycle=2.5–5.7s   {'indicators': 0.0, 'smc': 0.0}            ← most cycles, fully cached
cycle=12.4s      {'indicators': 97.1, 'smc': 0.0}           ← 1m candle closed
cycle=16.0s      {'indicators': 136.4, 'smc': 45.6}         ← 1m + 5m closed
```
**Cycle wall-clock 64s → ~3s typical, ~16s worst-case** (at candle boundaries). `smc` is
0 on every cycle except 5m closes — proving the #587 SMC cache was working all along.

**Telemetry silenced:** `SCAN_STAGE_TIMING_ENABLED=false` written to VPS `/root/360-v2/.env`.
NOT yet applied (engine env is baked at container creation; deploy is `paths-ignore` for
`.env`/docs). **Takes effect on the next code deploy** — until then the timing line still
logs every ~3s. Deferred deliberately to keep the telemetry through high-volatility
conditions for confidence.

### Open items (priority order)

1. **Telemetry auto-silences on next code deploy** — `SCAN_STAGE_TIMING_ENABLED=false`
   already in `/root/360-v2/.env`; the next PR-to-main deploy recreates the engine and
   applies it. No action needed unless the ~3s log cadence becomes a problem sooner
   (then `docker compose --profile isolated up -d --no-deps --force-recreate engine`).
2. **D1 NakedPositionDetector upgrade** — currently geometry-only (`stop_loss≤0`).
   Real naked-position detection (Binance stop order not placed) requires engine to
   publish `sl_order_id` per position in the Redis snapshot. Design needed.
3. **Verify regime-per-exit live** (PR #578) — `place_trailing_stop_market`/`trail_sl`
   in engine logs on TRENDING-aligned exits; `entry_regime`/`atr_value_at_entry`
   non-empty on dispatched positions; clean RANGING/QUIET market-closes.
4. **Verify funding-exit watcher live** (PR #581) — grep `funding_exit_watcher: exiting`;
   confirm `get_funding_info` populated near a settlement cycle.

---

## Session 17 checkpoint 2026-06-04 — regime-per-exit FSM + signing healthcheck + funding-exit watcher

### What shipped this session (5 PRs merged to `main`)

| PR | What | Type |
|---|---|---|
| #577 | Hurst gate + ATR trail width + multi-TF regime stamp | merged |
| #578 | Regime-per-exit FSM (TRAIL/VOLATILE/CANCEL) | owner sign-off, merged |
| #579 | ACTIVE_CONTEXT correction | docs, auto-merged |
| #580 | Signing service Docker healthcheck fix | ops, auto-merged |
| #581 | Funding-exit watcher (real funding data) | owner sign-off (delegated), merged |

#### PR #580 — signing container healthcheck (`c7c9081`)

`360scalp-v2-signing` shared the engine image whose Dockerfile HEALTHCHECK checks
for a `src.main` process + scanner heartbeat — neither exist in the signing
container, so it reported `unhealthy` after the 180s grace period despite serving
correctly. Fixed with a `healthcheck:` override in `docker-compose.yml`:
`test -S /app/sock/signing.sock` (socket created after KMS+Firestore init; stale
sockets unlinked on startup). **The long-standing "signing unhealthy" open item is
now resolved** — verify `docker ps` shows healthy after next redeploy.

#### PR #581 — funding-exit watcher (`2e99d7d`)

Exits positions that would PAY material funding within the pre-funding window.
Research (Binance docs) drove two key design choices:
- **Funding interval is not always 8h** (4h/8h/1h per pair) → read the real
  `nextFundingTime` per symbol from the mark-price stream.
- **The mark-price stream already carries `r` + `T`** — `MarkPriceFeed` was
  discarding them. Now captured via `get_funding_info(symbol)`.

Exit rule: `next_funding − now ≤ PRE_FUNDING_EXIT_WINDOW_SEC` (120s) AND paying
side AND `|rate| ≥ PRE_FUNDING_MIN_RATE` (0.05%). TRAILING positions skipped.
`close_reason="FUNDING_EXIT"`. Disable with `PRE_FUNDING_EXIT_WINDOW_SEC=0`.

#### Regime-per-exit FSM (PR #578) — full implementation

Owner-approved exit matrix (§3.2b):

| Post-pre-TP regime | Exit path |
|---|---|
| TRENDING + 15m confirm + aligned | **TRAIL** — Binance native `TRAILING_STOP_MARKET` |
| TRENDING (any condition mismatched) | **CANCEL** — immediate market close |
| RANGING / QUIET | **CANCEL** — immediate market close |
| VOLATILE | **VOLATILE** — tighten static SL by 20% |

Bugs fixed bundled:
1. `_apply_close_fill` — "close" phase fills were silently ignored (no dispatch table entry)
2. `_apply_tp2_fill` — when `tp3_qty == 0`, FSM was stranding in TP2_HIT forever

---

## Session 16 checkpoint 2026-06-03 — monitor watchdog + signing service aiohttp fix

**360-v2 PR #573** merged to main:

1. **`src/bootstrap.py` — `_resilient_monitor_loop` watchdog** — wraps `TradeMonitor.start()`
   in a self-healing loop; 5s backoff on exit, cleans up on normal `stop()`.
2. **`src/security/signing_service/server.py` — aiohttp chunk limit** raised from 8 KB
   to 64 KB. Fixes Reconciler WARNING on large `positionRisk` responses.

---

## Session 14 checkpoint 2026-06-03 — isolation cutover LIVE + post-cutover bug sweep

`API_PROCESS_ISOLATED=true` live on VPS. Engine runs `SnapshotWriter` only; separate
`api` container serves HTTP via `RedisEngineFacade`. Scanner-contention symptom resolved.

PRs #565 / #567 / #568 / #569 all merged. Three root causes fixed:
1. Missing `API_PROCESS_ISOLATED` in VPS `.env` → SnapshotWriter never started
2. Missing `init_keystore()` in api container → Binance key always ❌
3. Missing `init_kill_switch()` in api container → engine-wide enabled always ❌

**Policy adopted (owner standing authorisation, 2026-06-03):** CTE auto-merges PRs
once CI green / no conflicts / not an owner-sign-off item.
