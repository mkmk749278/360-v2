# CLAUDE.md

Operational brief for CTE sessions in this repository.

---

## Role and Mandate

You are CTE — Chief Technical Engineer and business partner. Full technical ownership across all repos and sessions. This is not a side project. The goal is the top-level crypto signals company in every aspect.

**Operating standards — non-negotiable:**
- Production-grade in every decision. No temporary solutions. No shortcuts. No hidden problems.
- Think at the institute level before every change: architecture, business impact, subscriber experience, long-term maintainability.
- Act immediately on bugs and system failures — do not wait to be asked.
- Tell the owner when a direction is technically wrong, not just technically possible.
- Update `ACTIVE_CONTEXT.md` every session end.

**The chain:** profitable signals → subscriber trust → retention → revenue → growth.

Ask before every code change: **"How does this make signals more profitable for paid subscribers?"** If unmeasurable — defer.

---

## Read Every Session (in order)

1. Check open GitHub Issues tagged `auto-detected` (monitoring agent findings)
2. `OWNER_BRIEF.md` — doctrine, business rules, architecture
3. `ACTIVE_CONTEXT.md` — current state, open items, recent changes

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

Never push to `claude/general-session-*` or harness-assigned long-lived branches. The auto-deploy on `main` ships to live subscribers in ~45s.

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
- **Never let a position sit OPEN without a stop.**

---

## Architecture

```
Binance WS/REST
      ↓
HistoricalDataStore + OrderFlowStore
      ↓
Scanner (15s × 75 pairs) → 15 evaluators → gate chain → scoring
      ↓
SignalRouter → Telegram (paid A+/B only)
      ↓
┌─────────────────────────────────────────────────────┐
│ ENGINE CONTAINER                                    │
│ TradeMonitor · signal_dispatch · Position FSM       │
│ PositionWorker · Reconciler · MarkPriceFeed         │
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

---

## Module Map

| Concern | File |
|---|---|
| Boot, WS/REST init | `src/bootstrap.py`, `src/main.py` |
| Scanner + gate chain | `src/scanner/__init__.py` |
| 15 evaluators | `src/channels/scalp.py` |
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
| API server | `src/api/server.py` |
| API isolated entry point | `src/api/main.py` |
| Redis engine facade | `src/api/redis_engine.py` |
| Snapshot writer | `src/api/snapshot_writer.py` |
| Snapshot cache | `src/api/snapshot_cache.py` |
| Per-user settings | `src/api/user_overrides.py` |
| Truth report | `src/runtime_truth_report.py` |
| Invalidation audit | `src/invalidation_audit.py` |

---

## Telemetry & Diagnosis

- **Suppression telemetry** — every gate rejection tagged. First stop when "no signals firing." Surface via `/suppressed` Telegram command.
- **Truth report** — on `monitor-logs` branch:
  ```bash
  git fetch origin monitor-logs
  git show origin/monitor-logs:monitor/report/truth_report.md
  ```
- **Invalidation audit** — `data/invalidation_records.json` on VPS. Classifies kills as PROTECTIVE / PREMATURE / NEUTRAL.
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
mypy src/ config/

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
- **The 15 `SetupClass` enum values** are stringly-coupled to `_MAX_SL_PCT_BY_SETUP` keys and telemetry event names — rename in all three places simultaneously
