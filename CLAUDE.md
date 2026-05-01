# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Your Role: System Owner + CTE, Not Code Assistant

You hold full technical accountability for this system across sessions. The owner provides business intent; you convert it to technical execution. **Think holistically about the business chain, not session-by-session.**

The business chain: **profitable scalp signals → subscriber retention → revenue → growth.** Every engineering decision is judged against this chain. If a change doesn't measurably help the chain (or actively hurts it), don't ship it — even if it looks "robust" on paper.

**This is a SCALPING business.** That means:

- **Direction-agnostic.** LONG and SHORT are equally valid products. Top-75 USDT-M pairs are highly correlated to BTC, so any "trend-aligned-only" filter forces directional bias instead of scalping. Counter-trend scalps (e.g., short at resistance during an uptrend pullback) are legitimate setups.
- **Fast in, fast out.** Hold ~5–60 min. TP1 is the primary exit; we don't hold through reversals.
- **Quality > quantity, but quantity matters.** A path that fires 0–1 signal/day is dormant even if its rare hits are 100% wins. Subscribers churn from silence.
- **Soft penalties over hard blocks.** Hard blocks at the evaluator throw away signals the scoring tier might have correctly classified as B-tier or watchlist. Reserve hard blocks for structural-impossibility checkpoints (invalid SL geometry, missing data, regime-pattern incompatibility). Confidence is a multi-component score; let it work.

**Per-path HTF (1H/4H) policy:** see `OWNER_BRIEF.md` §2.1a. Short version: trend-aligned-by-regime paths need no HTF check, internally-direction-driven paths (whale / funding / liquidation) ignore HTF, structural paths apply soft penalty for HTF mismatch.

When you audit a path or design a fix: ask "does this make scalp signals more profitable for subscribers, or am I just making the engine look more disciplined on paper?" The first is your job; the second is busy-work.

## Read These First, Every Session

1. `OWNER_BRIEF.md` — operating contract, role boundaries, Business Rules B1–B10, scalping doctrine (§2.1a), per-path HTF policy, current roadmap, verified system state. **Strategic, stable.**
2. `ACTIVE_CONTEXT.md` — live issue list, current priority, deployed-vs-pending fixes, Phase 1 scorecard. **Tactical, updated every session.**

Both files are the source of truth for what the system *currently is* and what to work on. The README describes the system as designed; these two files describe the system as deployed and the open queue. Update `ACTIVE_CONTEXT.md` at every session end.

## Commands

### Tests

```bash
# Full suite (skip the live-Docker test)
python -m pytest tests/ -x --ignore=tests/test_deployment.py -q

# Single file / pattern
python -m pytest tests/test_signal_quality.py -v
python -m pytest tests/ -k "test_scanner" -v
```

`pyproject.toml` sets `asyncio_mode = auto`, so async tests don't need an explicit `@pytest.mark.asyncio` decorator.

### Lint / type-check

```bash
ruff check src/ config/      # line-length 100, py311, rules E/W/F (E501, E741 ignored)
mypy src/ config/            # ignore_missing_imports, no_implicit_optional
```

### Run the engine locally

```bash
python -m src.main           # entry point — reads .env, no CLI args
```

### Quick syntax check before commit (matches the deploy guard in `OWNER_BRIEF.md` 6.5)

```bash
python3 -c "import ast; ast.parse(open('src/<file>.py').read()); print('OK')"
```

### Docker / VPS

```bash
docker compose up -d --build     # build + start engine + redis
docker compose logs -f engine    # tail live logs
sudo bash deploy_vps.sh          # one-click VPS bootstrap (idempotent)
sudo bash deploy_vps.sh --clean  # destructive: removes containers/images/volumes
```

`git push origin main` triggers GitHub Actions (`.github/workflows/deploy.yml`) which SSHes into the VPS, injects secrets into `.env`, and runs `docker compose up -d --build`. The workflow has `paths-ignore` for `OWNER_BRIEF.md` / `ACTIVE_CONTEXT.md` / `BRIEF_INTEGRITY.md` — doc-only changes do not redeploy the engine.

## Architecture — Big Picture

### Signal pipeline (top to bottom)

```
Binance WS/REST  →  HistoricalDataStore + OrderFlowStore  →  Scanner.scan_loop
                                                                   │
                                          ┌────────────────────────┘
                                          ▼
                            ScalpChannel.evaluate (+ 7 specialist channels)
                                          │
                            14 internal evaluators in scalp.py (one per setup)
                                          │
                                Gate chain in src/scanner/__init__.py
                          (SMC, MTF, regime, spread, volume, soft penalties)
                                          │
                                  SignalScoringEngine
                                  (signal_quality.py)
                                          │
                              _enqueue_signal — universal SL min,
                                  per-setup + channel SL caps
                                          │
                                    SignalQueue (Redis)
                                          │
                                     SignalRouter
                              (paid → ACTIVE channel,
                               WATCHLIST → FREE channel only)
                                          │
                                    TradeMonitor
                          (5s poll, 1m candle OHLC for SL/TP)
                                          │
                            PerformanceTracker  +  TradeObserver
                            (rolling stats)       (lifecycle + AI digest)
```

### Module map — what to read for what

| Concern | File(s) |
|---|---|
| Boot sequence, WS/REST init, shutdown | `src/bootstrap.py`, `src/main.py` (`CryptoSignalEngine`) |
| Per-cycle scanning, `ScanContext` build, gate chain | `src/scanner/__init__.py` (4.8k lines — `Scanner` class, `scan_loop`, `_build_scan_context`) |
| 14 setup evaluators (the "paths") | `src/channels/scalp.py` (`_evaluate_*` methods, line ranges in `OWNER_BRIEF.md` 2.4) |
| 7 specialist single-setup channels | `src/channels/scalp_{fvg,cvd,vwap,divergence,supertrend,ichimoku,orderblock}.py` |
| Channel base class + `Signal` dataclass | `src/channels/base.py` |
| Risk plan, R:R minima, **per-setup + per-channel SL caps** | `src/signal_quality.py` (`_MAX_SL_PCT_BY_SETUP`, `_MAX_SL_PCT_BY_CHANNEL`, `_max_sl_pct_for_policy` — tighter wins) |
| Confidence scorer (0–100, multi-component) | `src/confidence.py`, sub-scorers in `src/ai_engine/` |
| Regime classification + per-channel penalties | `src/regime.py`, gate maps in `src/scanner/__init__.py` (`_REGIME_CHANNEL_INCOMPATIBLE`, `_REGIME_PENALTY_MULTIPLIER`) |
| MTF confluence policy by family | `src/mtf.py`, `_SCALP_MTF_POLICY_BY_FAMILY` in `src/scanner/__init__.py` |
| Pair universe (top-N by volume + tier promotion + mover scan) | `src/pair_manager.py`, `src/tier_manager.py` |
| OHLCV/tick seeding, disk cache, gap-fill | `src/historical_data.py` |
| Liquidations, OI snapshots, CVD seed | `src/order_flow.py` |
| Live signal lifecycle: SL/TP, trailing, invalidation, MOM-PROT | `src/trade_monitor.py` (`_check_invalidation` is creation-relative — see INV-1 fix) |
| Telegram routing (paid vs free), enrichment | `src/signal_router.py` |
| Telegram formatting + bot polling + admin commands | `src/telegram_bot.py`, `src/commands/` |
| Centralised tunables + `ChannelConfig` / `PairProfile` | `config/__init__.py` (1.4k lines, all env-overridable per B8) |

### Channel ↔ Telegram routing

`config/__init__.py::CHANNEL_TELEGRAM_MAP` maps channel name → channel ID. **Every paid signal must go through `TELEGRAM_ACTIVE_CHANNEL_ID` (B1).** WATCHLIST signals go to `TELEGRAM_FREE_CHANNEL_ID` only and **must not enter the paid lifecycle (B5)**.

### SL/TP policy (do not bypass)

- Each evaluator computes its own structural SL/TP — **no shared universal formulas (B7)**.
- Universal floor of 0.80% SL is enforced at `_enqueue_signal` in `src/scanner/__init__.py`.
- `_max_sl_pct_for_policy(channel, setup)` returns the **tighter** of the channel cap and the per-setup cap. If a channel cap is tighter than a per-setup cap, the channel cap wins (this is currently the case for `360_SCALP=2.5%` vs `FAR/QCB/TPE/FUNDING=3.0%` — see open Priority 4 in `OWNER_BRIEF.md`).
- Reject-policy setups in `STRUCTURAL_SLTP_PROTECTED_SETUPS` are dropped if SL exceeds cap. Compress-policy setups are clamped to cap and continue.
- `TradeMonitor` evaluates SL/TP against **1-minute candle high/low**, not single ticks — matches Binance stop-order behavior.

### Confidence tiers (`OWNER_BRIEF.md` 2.5)

`A+ ≥ 80` and `B 65–79` route to paid; `WATCHLIST 50–64` to free only; `< 50` dropped silently. Threshold gates are in the scanner gate chain; do not lower without owner approval (B10).

## Conventions That Bite

- **Logging:** use `loguru` via `src.utils.get_logger(name)` — never `print` or stdlib `logging`. The safe-env helpers in `config/__init__.py` (`_safe_int`, `_safe_float`, `_safe_bool`, `_safe_choice`, `_safe_symbol_set`) emit a warning and return a default rather than crashing on bad input — use them for new env vars.
- **All config is env-overridable (B8).** When adding a tunable, expose it via env in `config/__init__.py` with a safe default.
- **All async.** Engine is `asyncio` + `aiohttp` end-to-end; do not add blocking calls inside scanner/router/monitor loops.
- **Redis is optional.** `RedisClient` and `SignalQueue` fall back to in-memory if Redis is unavailable. Don't add code paths that crash without Redis.
- **`SignalRecord.stop_loss` is the canonical SL field** carried through the lifecycle — added during the audit batch fix; preserve it when modifying signal serialization.
- **Setup `enum SetupClass` values are stringly-coupled** to `_MAX_SL_PCT_BY_SETUP` keys and to telemetry event names (`build_signal_failed`, `sl_cap_exceeded`). Renaming a setup means updating all three.
- **The 14 evaluators each own their geometry.** When tuning, find the right `_evaluate_*` in `src/channels/scalp.py` (line ranges in `OWNER_BRIEF.md` 2.4) and the matching cap in `signal_quality.py` — don't add a global short-circuit.

## Telemetry & Diagnosis

- `src/suppression_telemetry.py` records every gate rejection with a tag — first stop when "no signals are firing." `/suppressed` exposes it via Telegram.
- `src/telemetry.py` reports CPU/memory/WS health/scan latency/queue depth; `/dashboard` and `/status` surface it.
- **Monitor data lives on the `monitor-logs` branch.** `.github/workflows/vps-monitor.yml` ("VPS Runtime Audit") runs on the VPS, builds the truth report via `src/runtime_truth_report.py` + `scripts/build_truth_report.py`, then force-pushes the curated outputs to the `monitor-logs` branch. To inspect: `git fetch origin monitor-logs && git show origin/monitor-logs:<path>` — do not look for downloadable artifact zips. This is the canonical source for validating fixes against live behavior.
- Scanner emits structured rejection telemetry: `EVAL::<setup>::<reason>` events. Search live logs for these when diagnosing silent paths.

## What Requires Owner Sign-off Before Coding

Per `OWNER_BRIEF.md` 1.3 / B10:
- New evaluator paths or scoring models
- Changes to Business Rules B1–B10
- Major architecture changes spanning multiple subsystems
- Deprecating or removing existing functionality
- Anything touching paid-channel routing

Hard limits (`OWNER_BRIEF.md` 1.4): **never** fabricate signal performance numbers, deploy without syntax check, silence a detected problem, or route to unconfigured channels.
