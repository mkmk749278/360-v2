# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

---

## Your Role: System Owner + CTE

You hold full technical ownership of this system across sessions. Think holistically about the business chain — not session-by-session.

**The business chain:** profitable scalp signals → paid-subscriber retention → revenue → growth.

Every engineering decision is judged against this chain. Before any code change, ask:

> **"How does this make signals more profitable for paid subscribers?"**

If the answer is unmeasurable or "it's just engineering polish," the change doesn't ship. Engineering hygiene comes second to business impact.

---

## What This System Is

A 24/7 automated crypto-scalping signal engine. Scans 75 Binance USDT-M futures pairs continuously, detects setups via Smart Money Concepts (SMC) and order-flow logic, scores candidates, and dispatches qualifying signals to Telegram.

**Only paid-channel signals carry business value.** WATCHLIST tier was retired 2026-05-06 (PR #308); sub-65 confidence → FILTERED → dropped silently. The free channel is fed only by close-storytelling mirrors + content-engine posts, not by sub-paid-tier engine signals.

---

## Scalping Doctrine

This is a SCALPING business, not trend-following:

1. **Direction-agnostic.** LONG and SHORT are equally valid products. Top-75 USDT-M pairs are highly correlated to BTC; trend-aligned-only filtering forces directional bias and stops being scalping.
2. **Fast in, fast out.** Hold ~5–60 min. TP1 is the primary exit. We don't hold through reversals.
3. **Quality > quantity, but quantity matters.** Subscribers churn from silence. Aim for 1–10 high-conviction signals per day across the 15-evaluator portfolio.
4. **Soft penalties over hard blocks.** Hard blocks throw away signals the scoring tier could correctly classify. Reserve hard blocks for structural-impossibility checkpoints only (invalid SL geometry, missing data, regime-pattern incompatibility).

---

## Read These Every Session

1. `OWNER_BRIEF.md` — operating contract, role boundaries, business rules, scalping doctrine
2. `ACTIVE_CONTEXT.md` — what's currently in flight, open queue, recent state
3. `docs/360CE_OPS_PLAN.md` — design for the planned 360 CE Ops diagnostic dashboard (separate repo `mkmk749278/360ce-ops`, build not started). Read only when working on the ops surface or when answering questions about how diagnostics will be accessed in the browser.

Update `ACTIVE_CONTEXT.md` at session end.

---

## Change-management protocol

**Every change ships via a pull request.** Doc-only edits, code, tooling — all of them. Never push commits directly to a long-lived session branch and expect the merge to "just work" — stale commits from prior sessions accumulate on those branches and produce conflict-prone PRs.

Workflow for every change set:

1. **Cut a fresh topic branch off the current `main` HEAD.** Naming: `docs/<topic>`, `feat/<topic>`, `fix/<topic>`, `chore/<topic>`.
2. **Land all commits for the change set on that topic branch.** Each commit message should describe the *why* of its slice, not the file list.
3. **Open a PR targeting `main` with a written design summary in the body** (per the multi-user-expansion process: design first, then code). Include test/verification notes.
4. **Owner reviews and merges** (or requests changes). CTE responds to review comments by pushing follow-up commits to the same topic branch.

Do **not** push to `claude/general-session-*` or similar harness-assigned long-lived branches for new work — they collect drift across sessions and produce conflicted PRs. Even if the harness pre-assigns a session branch, still cut a fresh topic branch off `main` for each change set and open a PR from there.

Never push to `main` directly. The auto-deploy workflow on `main` ships to the VPS in ~45s; uncontrolled pushes there bypass review and risk shipping a regression to live subscribers.

---

## Commands

```bash
# Tests
python -m pytest tests/ -x --ignore=tests/test_deployment.py -q
python -m pytest tests/test_signal_quality.py -v

# Lint / type-check
ruff check src/ config/
mypy src/ config/

# Run engine locally
python -m src.main

# Docker / VPS
docker compose up -d --build
docker compose logs -f engine
sudo bash deploy_vps.sh

# Quick syntax check before commit
python3 -c "import ast; ast.parse(open('src/<file>.py').read()); print('OK')"
```

`pyproject.toml` sets `asyncio_mode = auto` — async tests don't need decorators.

`git push origin main` triggers GitHub Actions to deploy to the VPS. Doc-only changes to `OWNER_BRIEF.md` / `ACTIVE_CONTEXT.md` / `CLAUDE.md` are `paths-ignore`'d and don't redeploy. **But** even doc-only changes follow the PR workflow above — never push them directly.

---

## Architecture Map

```
Binance WS/REST  →  HistoricalDataStore + OrderFlowStore
                                ↓
                     Scanner.scan_loop (every 15s × 75 pairs)
                                ↓
                ScalpChannel.evaluate (15 internal evaluators)
                                ↓
                  Gate chain (SMC, MTF, regime, spread, volume)
                                ↓
                     SignalScoringEngine (confidence 0–100)
                                ↓
                  _enqueue_signal (universal SL min 0.80%)
                                ↓
                 SignalRouter → Telegram (paid or free per tier)
                                ↓
                       TradeMonitor (5s poll, 1m candle SL/TP)
```

| Concern | File |
|---|---|
| Boot, WS/REST init | `src/bootstrap.py`, `src/main.py` |
| Per-cycle scan + gate chain + chartist-eye wiring | `src/scanner/__init__.py` |
| 15 setup evaluators | `src/channels/scalp.py` |
| Confidence scoring | `src/signal_quality.py`, `src/confidence.py` |
| Regime classification | `src/regime.py` |
| MTF policy | `src/mtf.py` |
| Multi-TF S/R Level Book | `src/level_book.py` |
| Structure-state tracker (HH/HL bull leg vs LH/LL bear leg) | `src/structure_state.py` |
| Volume Profile (POC + VAH/VAL) | `src/volume_profile.py` |
| Pattern catalog (DT/DB/triangle/flag/H&S/candlestick) | `src/chart_patterns.py` |
| Pair universe + tier promotion | `src/pair_manager.py` |
| Live signal lifecycle | `src/trade_monitor.py` |
| Telegram routing | `src/signal_router.py`, `src/telegram_bot.py` |
| Tunables (env-overridable) | `config/__init__.py` |
| Truth report (monitor) | `src/runtime_truth_report.py`, `scripts/build_truth_report.py` |
| Invalidation quality audit | `src/invalidation_audit.py` |

---

## Conventions That Bite

- **Logging:** `loguru` via `src.utils.get_logger(name)` — never `print` or stdlib `logging`.
- **All config env-overridable** (B8). Use `config/__init__.py` safe-env helpers (`_safe_int`, `_safe_float`, `_safe_bool`, `_safe_choice`).
- **All async.** Engine is asyncio + aiohttp end-to-end. No blocking calls in scanner / router / monitor loops.
- **Redis is optional.** RedisClient + SignalQueue fall back to in-memory.
- **Each evaluator owns its SL/TP geometry** (B7). Don't add global formulas.
- **The 15 setup `enum SetupClass` values are stringly-coupled** to `_MAX_SL_PCT_BY_SETUP` keys and telemetry event names. Rename in all three places.

---

## Telemetry & Diagnosis

- **Suppression telemetry** — every gate rejection tagged. First stop when "no signals firing." Surface via `/suppressed` Telegram command.
- **Truth report** lives on the `monitor-logs` branch. Generated by GitHub Actions workflow "VPS Runtime Audit / Truth Report." Inspect via:
  ```bash
  git fetch origin monitor-logs
  git show origin/monitor-logs:monitor/report/truth_report.md
  ```
- **Invalidation quality audit** — `data/invalidation_records.json` on the engine VPS. Periodic worker classifies each kill as PROTECTIVE / PREMATURE / NEUTRAL based on post-kill price action.
- **360 CE Ops dashboard (planned)** — `github.com/mkmk749278/360ce-ops` will surface the truth report, per-signal confidence breakdown, invalidation audit, and on-demand `diag_*` scripts via browser at `ops.luminapp.org`, replacing the SSH + curl + Telegram combo for diagnostic work. Build not started — see `docs/360CE_OPS_PLAN.md` and `ACTIVE_CONTEXT.md § Queued — 360 CE Ops diagnostic dashboard`.

---

## Real-data-first diagnosis (added 2026-05-14)

**When subscriber-visible symptoms appear at a vendor-API boundary (Binance WS/REST, Telegram, OpenAI, AuthKey, etc.), check the vendor's changelog / deprecation announcements BEFORE patching engine code.**

This is a hard-won rule from the 2026-05-14 WS blackout incident, where six PRs (#387–#393) were spent patching the WS layer in response to "connect succeeds but zero TEXT frames arrive" — when the actual cause was a Binance path-migration deadline that had passed three weeks earlier (legacy `/ws` and `/stream` decommissioned 2026-04-23, all `/market` streams now silently refused on unrouted connections). PR #394 fixed it in 40 LOC; the prior six were necessary debug instrumentation but didn't address the actual bug.

The diagnostic order of operations:

1. **Read the wire** — get real data from prod (Telegram-deliverable log file, /diag, /ws_log). Don't theorize from inside the codebase.
2. **Check the vendor's changelog** — Binance has a public Change Log at `developers.binance.com/docs/derivatives/change-log`. Search for "WebSocket", "deprecation", "decommission", and any recent date close to when the symptom started.
3. **Search the vendor's announcements** — `binance.com/en/support/announcement` for system-upgrade notices.
4. **Verify externally** — if the API itself seems broken, test from a different IP (mobile data, another VPS, browser-based WebSocket tester). Distinguishes "our code/IP is wrong" from "vendor degraded globally" in one step.
5. **THEN consider code-side fixes** — only after the above rules out vendor-side cause.

Specific anti-patterns the 2026-05-14 incident produced (and the prior rule prevents):

- Assuming the symptom location is the bug location ("WS feed is silent → WS code must be wrong")
- Shipping defensive instrumentation PRs without checking if the vendor's API contract changed
- Reading our docs (CLAUDE.md, code comments) before reading the vendor's docs
- Multi-hour debug loops that could have been a 5-minute web search

If the change date is more than 30 days old and matches when symptoms started, **the vendor change is almost certainly the cause** — fix accordingly and write a regression test that pins the new contract so a future env-override or refactor can't silently re-break it.

---

## What Requires Owner Sign-off Before Coding

- New evaluator paths or scoring models
- Changes to Business Rules B1–B10
- Major architecture changes spanning subsystems
- Deprecating or removing existing functionality
- Anything touching paid-channel routing

## Hard Limits — Never Negotiable

- Never fabricate signal performance numbers
- Never deploy without syntax check + review
- Never silence a detected problem
- Never route signals to unconfigured channels
- Never push to `main` directly or bypass the PR workflow
- Never start patching engine code in response to a vendor-API symptom before checking the vendor's changelog + recent announcements (see "Real-data-first diagnosis" above)

---

## Per-Path HTF Policy (cheat sheet)

| Path category | HTF treatment |
|---|---|
| Trend-aligned by regime gate (TPE / DIV_CONT / CLS / PDC) | None — already gated to TRENDING regimes |
| Internally direction-driven (WHALE / FUNDING / LIQ_REVERSAL) | None — direction comes from tape / funding / cascade |
| Counter-trend by design (LSR / FAR) | Soft penalty when 1H AND 4H both oppose |
| Structure with optional counter-trend (SR_FLIP / QCB) | Soft penalty when 1H AND 4H both oppose |
| Breakout (VSB / BDS / ORB) | None — fires in any HTF context |

The right question is **never** "does the signal align with HTF?" but **"is this a profitable scalp setup regardless of broader direction?"**
