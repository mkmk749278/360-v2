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
2. **Pre-TP is the primary exit; TP1 is the bonus tail.** Most signals partially close at the pre-TP threshold (banking real profit on the user-configured fraction, minimum 30% per B17). The residual rides toward TP1 with SL ratcheted to breakeven and tight thesis-broken invalidation. Hold ~5–60 min. We don't hold through reversals.
3. **Capital preservation outranks TP chasing.** A full SL hit costs ~7.9% on margin at 10×; a banked partial + BE exit on the residual costs ~−0.5% even if the residual flatlines. The asymmetry is decisive — see `OWNER_BRIEF §3.2a`.
4. **Quality > quantity, but quantity matters.** Subscribers churn from silence.
5. **Soft penalties over hard blocks.** Hard blocks throw away signals the scoring tier could correctly classify. Reserve hard blocks for structural-impossibility checkpoints only (invalid SL geometry, missing data, regime-pattern incompatibility).

## Structure Detection Doctrine — "HTF Structure, LTF Entry" (2026-05-17)

**HTF (1H/4H) identifies the structure; LTF (5m) refines the entry timing only.** A 5m candle never identifies structure — it identifies *when* to enter the structure already identified at HTF. Any evaluator that reads structural meaning from a 5m candle is misusing 5m as if it were noise-free higher-TF data.

See `OWNER_BRIEF §3.4a` for the per-concern detection/entry mapping. Tape-driven paths (WHALE / LIQUIDATION_REVERSAL / FUNDING_EXTREME) are exempt — they read structure from realtime order flow, not from candle structure.

Existing infrastructure to consume: `src/level_book.py` (1d/4h/1h pivots + VP zones), `src/structure_state.py` (bull-leg/bear-leg per TF), `src/volume_profile.py` (POC + VAH/VAL), `_classify_htf_trend()` in `src/channels/scalp.py`. The doctrine makes consumption of these mandatory for structure detection across every non-tape-driven evaluator.

## Server-side execution doctrine (2026-05-18 — architecture decided; stack live 2026-05-18; completeness gaps documented 2026-05-26)

**Lumin executes Binance Futures orders server-side from the engine VPS, not from the user's device.** The mobile lifecycle (iOS suspends ~30s, Android variable) cannot meet the sub-second reaction requirement that pre-TP partial close + BE shift impose (§3.2a doctrine), and Binance's late-2023 IP-whitelist requirement on Futures-trade-enabled keys made mobile per-device whitelisting structurally unusable. Both problems converge on the same answer: order execution lives on the engine VPS.

**Custody model is non-custodial of funds, custodial of trade-authorisation keys only.** See `OWNER_BRIEF §3.9` for the full doctrine and `OWNER_BRIEF B18` for the non-negotiable rules.

**The non-negotiables when working in this area:**

- The plaintext Binance API secret must only ever materialise inside the **signing service** process memory, for the duration of one signing operation, and must never be: written to disk (even momentarily), logged at any level, returned to the engine workers, passed across any IPC boundary other than the Unix socket to the signing service, or surfaced in error traces / panics / debug dumps.
- The signing service is the **only** module that calls `KMS.Decrypt`. Engine workers, scanners, monitors, routers — none of them have KMS IAM access. If you're writing code outside `src/security/signing_service/` and you need to sign a Binance request, call the signing service over the Unix socket — never reach for the KEK directly.
- The connect-time validation (`/api/binance/connect`) **must** reject keys where any of these are not true: `enableWithdrawals=false`, `enableFutures=true`, `ipRestrict=true` AND the engine VPS IP is on the whitelist. No permissive mode, no "warn and continue" mode, no admin override. This is the foundation of the entire blast-radius story.
- The blast-radius caps (symbol allowlist, per-user rate limit, per-user position cap, global kill switch) are the operative defence if the engine VPS is rooted — without them, the security story collapses. Never disable them, never expand them silently, never let a single user bypass them.
- The Position FSM is **the** business-value layer. Pre-TP partial close + BE shift (§3.2a) is what turns a doctrinally net-losing path into a net-positive one. Changes to the FSM transitions (entry → SL/TP placement, pre-TP threshold trigger, BE shift on TP1 fill, trail tightening) require owner sign-off; this is the same gating as changes to confidence scoring.
- **Order-type doctrine (2026-06-01, OWNER_BRIEF §3.10):** profit-taking (pre-TP / TP1 / TP2) is placed as **reduce-only LIMIT** orders that rest on Binance's book — maker fills, **no slippage**. MARKET orders are reserved for entry and for protection / thesis-broken exits (SL, invalidation, expiry). The per-user dials — `threshold_pct` (resolve_pretp_threshold_uid), `grab_fraction` (resolve_grab_fraction_uid), `invalidation_mode` (resolve_invalidation_mode_uid) — select Profile A (full close at threshold) / B (partial + residual) / C (ride native bracket). `grab_fraction = 1.0` skips the residual TP bracket.

**Code module locations (all built and live as of 2026-05-18; wiring gaps closed 2026-05-26):**

| Concern | File | Running? |
|---|---|---|
| Cloud KMS client wrapper | `src/security/kms_client.py` | ✅ (when GCP env set) |
| AES-GCM envelope crypto helpers | `src/security/envelope_crypto.py` | ✅ |
| Firestore Admin SDK init + per-user key blob CRUD | `src/security/firestore_keystore.py` | ✅ (when Firebase env set) |
| Signing service (separate Python process, Unix socket server) | `src/security/signing_service/` | ✅ |
| Binance permission/whitelist validator | `src/security/binance_connect_validator.py` | ✅ |
| Per-user Position FSM worker | `src/execution/position_worker.py` | ✅ (per-user, conditional on Firebase) |
| Position FSM state machine | `src/execution/position_fsm.py` | ✅ |
| Binance User Data Stream consumer | `src/execution/user_data_stream.py` | ✅ (inside position_worker) |
| Anomaly tripwires (symbol allowlist, rate limit, position cap) | `src/execution/tripwires.py` | ✅ (position cap enforced at dispatch — PR #504) |
| Reconciliation loop | `src/execution/reconciler.py` | ✅ **wired — PR #505** (asyncio task + worker_manager register/unregister) |
| Kill switch (Firestore-doc-driven) | `src/execution/kill_switch.py` | ✅ |
| Mark price feed (Binance `!markPrice@arr@1s`) | `src/execution/mark_price_feed.py` | ✅ **wired — PR #506** (asyncio task + singleton) |
| Pre-TP tick dispatcher | `src/execution/pretp_dispatcher.py` | ✅ **wired — PR #506** (singleton; FSM calls track/untrack) |

**Remaining gaps (6-PR roadmap):** see `OWNER_BRIEF §3.10` and `ACTIVE_CONTEXT.md` for current status.

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
4. **Subscribe to the PR's activity and drive it to merge** (owner standing authorisation, 2026-06-03). On opening every PR, call `subscribe_pr_activity` so CI results and review comments wake the session. **Auto-merge without waiting for per-PR owner confirmation once *all* of these hold:** CI is green, there are no merge conflicts, the change is **not** in the "What Requires Owner Sign-off Before Coding" list below, and no reviewer has raised an unresolved objection. Respond to review comments by pushing follow-up commits to the same branch.

   **Pause and ask the owner (via `AskUserQuestion`) instead of merging when any of these is true:** CI is red and the fix is non-obvious or out of scope; a merge conflict needs a judgement call; the change touches an owner-sign-off item (signing service / KMS / connect-time validation / blast-radius caps / Position FSM transitions / paid-channel routing / new evaluators or scoring / Business Rules); or a reviewer raises a substantive objection. Auto-merge is for the routine majority — it is **not** a licence to self-approve the gated changes.

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
              ┌──────────────────────────────────────────────┐
              │  TradeMonitor (5s poll, 1m candle SL/TP/pre-TP)   │  ← engine-wide
              │  signal_dispatch → per-user FSM (entry + orders)   │  ← per-user
              │  PositionWorker (User Data Stream, FSM transitions) │  ← per-user
              │  Reconciler (60s diff — wired PR #505)              │  ← per-engine
              └──────────────────────────────────────────────┘
```

**Two parallel SL/TP paths for server-side auto-trade users:**
- **Native Binance orders** (SL stop-market + TP1/TP2 limit) placed at entry → fills arrive via User Data Stream → FSM advances state. This is the primary path.
- **TradeMonitor 5s poll** acts as backstop for cases where native orders are absent or candle data shows breach. Mark-price SL backstop (PR #500) covers no-candle-data scenarios.

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
| Live signal lifecycle (engine-wide backstop) | `src/trade_monitor.py` |
| Telegram routing | `src/signal_router.py`, `src/telegram_bot.py` |
| Tunables (env-overridable) | `config/__init__.py` |
| Truth report (monitor) | `src/runtime_truth_report.py`, `scripts/build_truth_report.py` |
| Invalidation quality audit | `src/invalidation_audit.py` |
| Server-side execution stack (live 2026-05-18; gaps documented 2026-05-26) | `src/security/` + `src/execution/` |

### Lumin app distribution (2026-05-21)

The companion app (`github.com/mkmk749278/lumin-app`, package `org.luminapp.lumin`) is live on the Play Store Closed Testing track. CI builds the AAB on every push to `main` and **strips REQUEST_INSTALL_PACKAGES + 6 transitive media permissions on the AAB path only** — the sideload APK retains them for the in-app updater. Mobile clients hit the engine through Cloudflare (`api.luminapp.org`) which terminates SSL, sets `CF-IPCountry`, and caches what it can; the engine consumes `CF-IPCountry` on `GET /api/region` for the auto-trade region gate. Firebase Phone Auth needs both the upload-key SHA and the Play app-signing SHA on the Firebase project — Play re-signs the uploaded AAB, so a missing Play SHA produces `Invalid app info in play_integrity_token` only on Play installs, never on sideload.

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
- Changes to Business Rules B1–B10 (or B12 / B17 / B18 — auto-trade safety, pre-TP, server-side custody)
- Major architecture changes spanning subsystems
- Deprecating or removing existing functionality
- Anything touching paid-channel routing
- Any change to the signing service / KMS integration / connect-time validation / blast-radius caps (per B18 + `Server-side execution doctrine` above)
- Any change to Position FSM transitions (entry placement, native SL/TP shape, pre-TP trigger threshold, BE shift on TP1 fill, trail tightening)

## Hard Limits — Never Negotiable

- Never fabricate signal performance numbers
- Never deploy without syntax check + review
- Never silence a detected problem
- Never route signals to unconfigured channels
- Never push to `main` directly or bypass the PR workflow
- Never start patching engine code in response to a vendor-API symptom before checking the vendor's changelog + recent announcements (see "Real-data-first diagnosis" above)
- **Never log a Binance API secret, even at TRACE/DEBUG level. Never write a plaintext secret to disk, even momentarily. Never return a plaintext secret from any function outside the signing service. Never include a secret in an error trace, panic message, exception attribute, or debug dump.**
- **Never accept a Binance API key at connect time that has withdraw permission enabled.** Auto-reject with a specific error directing the user to disable withdraw on the Binance key page and retry. No permissive mode, no admin override.
- **Never disable or weaken the blast-radius caps** (symbol allowlist, per-user rate limit, per-user position cap, global kill switch). These are what bound damage if the engine VPS is rooted. Expanding a per-user cap is owner-sign-off; disabling the symbol allowlist is never.
- **Never let a position sit OPEN without a stop** (naked-position invariant, 2026-06-01). If the SL fails to place at entry, `place_signal` force-closes the entry at market rather than leave it uncovered; the reconciler force-closes any position open past `RECONCILER_MAX_POSITION_AGE_SEC`. Don't revert these to "best-effort / surface and continue" — that was the JTOUSDT 5h09m failure mode.

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
