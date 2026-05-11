# 360 CE Ops — Diagnostic Dashboard Design

**Status:** Plan complete 2026-05-11. Build not started. Lives in a separate repo (`github.com/mkmk749278/360ce-ops`) which is **not yet accessible to MCP tooling** — the build resumes in a fresh session after the repo is added to the access list at session boot.

**See also:** `OWNER_BRIEF.md §3.1` and Part V infrastructure table (system context), `ACTIVE_CONTEXT.md § Queued — 360 CE Ops diagnostic dashboard` (current state and decisions).

---

## Goal

Replace the SSH + Telegram + `curl` combo currently required to access diagnostic surfaces with a single browser-based view of the engine's truth report, per-signal scoring decomposition, and on-demand `diag_*` scripts. Owner's stated need (verbatim):

> *"this app should help us to interact with engine to diagnose errors, signal quality, deep level analysis of signals … what's our truth report and diag command doing, and all useful things to us, and that you should access directly."*

## Form factor — web dashboard, not mobile APK

Diagnostic content — confidence-component decomposition, MFE/TP1 ratio tables, per-pair rolling stats, PROTECTIVE/PREMATURE/NEUTRAL classification histograms, geometry-vs-reality dumps — is table- and chart-heavy. Phone screen is the wrong substrate. Mobile-responsive layout so the owner can still hit it from phone if needed.

Trade-off vs. the originally-considered Flutter APK: no launcher icon, accessed via URL. If a launcher icon proves essential later, the dashboard can be wrapped in a thin Flutter WebView shell — but starting with web removes ~80% of the scaffolding work and matches owner's *"whatever stack, just do the job"* answer.

## Architecture

```
┌─────────────────────────┐         ┌──────────────────────┐
│  Browser (owner only)   │ HTTPS   │  ops.luminapp.org    │
│  Phone or desktop       ├────────▶│  (Caddy/Nginx)       │
└─────────────────────────┘         └──────────┬───────────┘
                                               │
                                    ┌──────────▼───────────┐
                                    │  360 CE Ops          │
                                    │  Python + FastAPI    │
                                    │  + Jinja2 + HTMX     │
                                    │  (Docker service)    │
                                    └──┬──────┬─────────┬──┘
                                       │      │         │
                            read-only ─┘      │         └─ HTTPS
                            volume mount      │            (live)
                                       │      │            │
                              ┌────────▼─┐  ┌─▼──────┐  ┌──▼────────┐
                              │ engine   │  │monitor-│  │ engine    │
                              │ data/    │  │logs    │  │ /api/*    │
                              │ *.json   │  │branch  │  │ (REST)    │
                              └──────────┘  └────────┘  └───────────┘
                              signal_       truth_       pulse,
                              performance   snapshot     signals,
                              invalidation  signals_     positions,
                              signal_       last100      auto-mode
                              history       dispatch_
                                            log
```

**Auth.** Single-password gate at `/login`, comparing against the engine's existing `API_AUTH_TOKEN` env var. Successful login sets an HttpOnly session cookie. Owner-only.

**Deploy.** New `docker-compose` service alongside the engine on the same VPS, behind the existing reverse proxy. Auto-deploy via GitHub Actions on push to `main`.

**No engine code changes required for MVP.** The ops app is a pure read-side consumer of artifacts the engine already produces.

## Tech stack

| Layer | Choice | Rationale |
|---|---|---|
| Backend | Python 3.11+, FastAPI | Same async model as engine; lightest framework for templated routes |
| Templates | Jinja2, server-rendered | Zero JS build step |
| Interactivity | HTMX + sparing Alpine.js | Partial swaps over CDN-served JS; no npm, no webpack |
| Engine API client | `httpx` | Async, matches FastAPI |
| Volume reads | Direct JSON file reads on read-only mount | No DB, no intermediate cache |
| `monitor-logs` reads | Shallow `git clone` on a 60s timer | Already the canonical source |
| Diag execution | `docker exec engine python /app/scripts/diag_*.py` | Reuses existing scripts; no duplication |
| Charts (later) | Server-rendered SVG via matplotlib, or Chart.js via CDN | MVP is table-only |

**Reuse:** import `src/performance_tracker.py` reducers directly rather than re-implementing rolling stats. Either vendor the file as a local package or pip-install the engine as a dependency.

## MVP scope

### First slice (recommended for first build)

| Route | Purpose | Data source |
|---|---|---|
| `/` | Pulse: engine health, auto-mode, breaker, last-signal time, WS status, recent dispatch count | `/api/pulse`, `/api/auto-mode`, `monitor/raw/heartbeat.txt` |
| `/truth` | Truth report viewer — structured sections (channel funnel, regime distribution, TP hit rates, invalidation summary, confidence-gate decisions, free-channel posts, pre-TP fires, WS outages). Link to raw markdown and JSON. | `monitor-logs` branch: `truth_report.md`, `truth_snapshot.json`, `window_comparison.json` |
| `/signals` | Signal table: last 100 completed + live in-flight. Filters: setup_class, terminal status, channel, regime. Sort by confidence/PnL/duration. | `signals_last100.json` + live `/api/signals` |
| `/signals/{id}` | **"Why did this score 0.62"** view. Sections: market context (regime/session/spread/vol), confidence breakdown (pre_ai / post_ai / soft-penalty stack), geometry (entry/SL/TP1-3, MFE, MAE, MFE/TP1 ratio), timeline (created → dispatched → first touches → terminal), invalidation classification + kill reason | join of `signal_performance.json` + `invalidation_records.json` + `signal_history.json` |

Polling cadence: HTMX `hx-trigger="every 30s"` for pulse/signals; longer (5 min) for truth-report sections. No WebSockets for MVP.

### Second slice (deferred)

| Route | Purpose | Data source |
|---|---|---|
| `/diag/geometry` | On-demand run of `scripts/diag_geometry_vs_reality.py` with form params (limit, setup_class). Renders sortable output table. | `docker exec engine python /app/scripts/diag_geometry_vs_reality.py ...` |
| `/invalidations` | PROTECTIVE / PREMATURE / NEUTRAL histogram grouped by `kill_reason_family` × `setup_class`. Drill into individual records. | `invalidation_records.json` |
| `/performance` | Per-pair rolling stats (7d / 30d / all-time): win rate, avg PnL, max DD, consistency. Per-regime / per-session breakdowns. TP1/TP2/TP3 progression. | `signal_performance.json` reduced via `performance_tracker.py` |

### Out of MVP scope

- **Writes** (auto-mode flip, breaker, settings) — owner's framing was diagnostic-first; control stays in Telegram until the dashboard earns trust.
- **Multi-operator access** — owner-only via single password.
- **Charts beyond tables** — defer until tables prove the data model.

## File layout (planned, in `360ce-ops` repo)

```
360ce-ops/
├── app/
│   ├── main.py                    # FastAPI app + session middleware
│   ├── auth.py                    # API_AUTH_TOKEN password gate, session cookie
│   ├── routes/
│   │   ├── pulse.py
│   │   ├── truth.py
│   │   ├── signals.py
│   │   ├── signal_detail.py
│   │   ├── diag.py                # second slice
│   │   ├── invalidations.py       # second slice
│   │   └── performance.py         # second slice
│   ├── data_sources/
│   │   ├── engine_api.py          # httpx client for /api/*
│   │   ├── data_volume.py         # read mounted /engine-data/*.json
│   │   ├── monitor_logs.py        # shallow-clone monitor-logs branch on timer
│   │   └── diag_runner.py         # docker-exec wrapper for diag_*.py
│   ├── templates/                 # Jinja2 (base.html + per-route)
│   └── static/
│       ├── htmx.min.js
│       ├── alpine.min.js
│       └── style.css
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/deploy.yml   # build + push image, SSH-restart VPS
```

## Files referenced from `360-v2` (read-only)

- `src/api/server.py` — REST endpoints the dashboard calls
- `src/runtime_truth_report.py` — section extractors; mirror its schema in the truth viewer
- `src/invalidation_audit.py` — classification semantics + record schema for `/invalidations`
- `src/performance_tracker.py` — rolling-stat reducers to import (don't re-implement)
- `scripts/build_truth_report.py` — orchestrator; useful to mirror section ordering
- `scripts/diag_geometry_vs_reality.py` — shelled out from `/diag/geometry`
- `.github/workflows/vps-monitor.yml` — defines when truth-report artifacts refresh
- `monitor-logs` branch — `monitor/report/{truth_report.md, truth_snapshot.json, signals_last100.json, dispatch_log.json, window_comparison.json}`, `monitor/raw/heartbeat.txt`
- `data/{signal_performance, invalidation_records, signal_history}.json` — mounted read-only into ops container

## Verification plan (when built)

1. **Local dev.** `docker compose up` brings up the ops dashboard pointed at a captured snapshot of `monitor-logs` and the engine's `data/` directory. Login gate works, each page loads without 500s.
2. **Read-side correctness.** Open `/signals/<known_id>` for a signal whose Telegram-bot numbers are known. Confidence breakdown, MFE, kill reason, classification all match the engine's stored values.
3. **`/diag/geometry`.** Triggered from the UI with `--limit 50 --path SR_FLIP_RETEST`, output matches running the script by hand inside the engine container.
4. **Truth report freshness.** Trigger `.github/workflows/vps-monitor.yml`, wait for artifacts on `monitor-logs`, refresh `/truth` — new snapshot appears within one polling interval.
5. **Auth.** Log out → all routes redirect to `/login`; bad password rejected; correct password (matching `API_AUTH_TOKEN`) issues session cookie.
6. **Deploy.** Push to `main`, GitHub Action builds, pushes image, SSH-restarts the VPS container, `ops.luminapp.org` returns HTTP 200 with the new build.
7. **Owner UAT.** Walk owner through a real diagnostic scenario ("why did signal X die premature?"); the dashboard answer should match what SSH + Telegram would reach, in 2× the time.

## Owner decisions captured (this session)

| Question | Answer |
|---|---|
| App name | **360 CE Ops** (engine-brand, per OWNER_BRIEF §B15) |
| Repo | `github.com/mkmk749278/360ce-ops` — separate repo, not subdirectory of `360-v2` |
| Stack | Stack-agnostic per owner — *"whatever it is, this app should help us diagnose errors, signal quality, deep-level analysis"*. Chose web + Python + FastAPI + Jinja2 + HTMX for diagnostic-table fitness and zero build complexity. |
| First-build scope | Owner accepted CTE recommendation: ship first slice (pulse + truth + signals + signal_detail) before second slice. Validates all four data sources end-to-end before broadening. |
| Deploy | Owner accepted CTE recommendation: include the GitHub Actions deploy workflow on day one. Owner is mobile-first and shouldn't SSH to ship updates. |
| Auth | Reuse `API_AUTH_TOKEN` (owner static token). No multi-user. |

## How to resume in a new session

1. **Add `mkmk749278/360ce-ops` to the MCP-tool repo-access list at session boot.** The repo selector only appears at session start; mid-session edits aren't possible. After this is done, MCP `mcp__github__*` calls against `360ce-ops` will succeed.
2. Re-read this plan + `ACTIVE_CONTEXT.md § Queued — 360 CE Ops diagnostic dashboard`.
3. Confirm with owner: first slice only (recommended) or full MVP in one push.
4. Bootstrap the new repo, scaffold the FastAPI app, wire the four data sources, ship first slice.
5. Add Caddy/Nginx route for `ops.luminapp.org`, mount engine `data/` read-only into the ops container, set `API_AUTH_TOKEN` env on the ops service, register the `monitor-logs` shallow clone timer, run an end-to-end smoke from the verification plan above.
