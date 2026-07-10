# Autonomous Ops — the self-supervising stack

*Shipped 2026-07-10 (Session 48). Owner directive: "I'm only the one handling
all this project, one can't observe all — autonomous system needs self checks,
self heal-up, self restart."*

The system supervises itself in layers. Each layer catches what the layer
below missed, and each can **act**, not just observe. Detection targets:
container crash → seconds; wedge/freeze → ~1 minute with auto-restart;
whole-VPS death → ~5 minutes to the owner's phone.

```
Layer 5  healthchecks.io dead-man     catches: the whole box died          → phone
Layer 4  Telegram paging              catches: "a human IS needed"         → phone, minutes
Layer 3  watchdog container           catches: invariant breaches          → page/restart/kill-switch
Layer 2  autoheal container           catches: unhealthy-but-running       → restart
Layer 1  deep healthchecks            makes wedges DETECTABLE              → health status
Layer 0  host self-maintenance        prevents: OOM, disk-full, reboots    → boring by design
```

---

## Authority doctrine — non-negotiable

The autonomous machinery may take **risk-reducing actions only**:

* page the owner, restart a wedged container, prune disk, **ENGAGE** the
  kill switch.
* It must **never** take an action that increases exposure: it never
  disengages the kill switch, never resets a circuit breaker, never
  re-enables auto-trade, never widens any cap. Recovery of *trading* is
  always the owner, through ops.

Why this is safe: the engine boots **fail-closed** (auto-trade disabled until
the Firestore flag says otherwise) and every open position's SL/TP rests as
real orders **on Binance** — so a restart, or a full halt, always leaves users
*more* protected, never less. An autonomous system that can only make the
system safer cannot be turned against it by its own bug.
(`tests/test_watchdog.py::TestKillSwitchActuator::test_watchdog_has_no_disengage_code_path`
asserts the no-disengage property at the source level.)

---

## Layer 1 — deep healthchecks (docker-compose.yml)

| Container | Probe | Catches |
|---|---|---|
| engine | `healthcheck.py`: process up **and** scanner heartbeat < 120s | crashed *and wedged* scan loop |
| api | HTTP GET `/api/health` round-trip | hung event loop, not just dead process |
| redis | `redis-cli ping` | wedged redis |
| signing | socket exists (created only after KMS+Firestore init) | failed custody boot |
| watchdog | own heartbeat file < 300s | wedged supervisor |

A protective breaker halt does NOT trip the engine probe — the scanner
publishes its heartbeat every cycle *including while halted*, so autoheal
never "fixes" an intentional halt.

## Layer 2 — autoheal (`360scalp-v2-autoheal`)

`willfarrell/autoheal:1.2.0` (pinned), watching the `autoheal=true` label on
engine/api/redis/signing. Docker's `restart:always` only covers *exits*;
autoheal restarts containers whose healthcheck flipped to `unhealthy` —
the Session 44/45/46 "alive but frozen" class. `network_mode: none`; its only
interface is the local Docker socket. The watchdog is deliberately NOT
autoheal-labeled: one supervisor stays outside the blast radius of the
machinery it supervises.

## Layer 3 — watchdog (`scripts/watchdog.py`, `360scalp-v2-watchdog`)

Every `WATCHDOG_INTERVAL_SEC` (60s) it checks, pages, and remediates:

| Check | Detection | Action ladder |
|---|---|---|
| Container states | down / unhealthy | page (autoheal owns first-line restart) |
| Scanner heartbeat | stale > `WATCHDOG_HEARTBEAT_STALE_SEC` (900s) with container up | page + engine restart (budgeted) |
| **Pricing freshness (audit F-07)** | open position `blind` (stale 1m kline AND no mark price) | page immediately; restart engine if blind > `WATCHDOG_BLIND_ESCALATION_SEC` (600s) — a boot re-seeds all active symbols (the manual MVLLUSDT fix, automated) |
| Publisher freshness | `pricing_freshness.json` itself > 600s old | page (a monitor that stops measuring is F-09 again) |
| Circuit breaker | trip transition | page (redundant with the engine's own alert BY DESIGN — this one survives a broken engine alert path). Never resets it |
| Disk | > 85% page; > 92% | prune dangling images + stopped containers + build cache, page with MB reclaimed |
| Memory | MemAvailable < 10% | page (earlyoom is the actuator, layer 0) |
| Escalation | engine restart budget (3/h) exhausted, still broken | **ENGAGE kill switch** via API owner token + CRITICAL page |
| Dead-man | every loop | ping `HEALTHCHECKS_PING_URL` |

Paging dedupe: one page per finding key per `WATCHDOG_PAGE_COOLDOWN_SEC`
(30 min), plus a one-shot ✅ recovery page when a key clears. Every page and
action is appended to `data/watchdog_audit.jsonl`. Cross-loop state
(`data/watchdog_state.json`) survives watchdog restarts, so budgets and open
episodes aren't reset by a redeploy.

**Env (all optional, defaults shown):**

```
WATCHDOG_INTERVAL_SEC=60
WATCHDOG_PAGE_COOLDOWN_SEC=1800
WATCHDOG_HEARTBEAT_STALE_SEC=900
WATCHDOG_BLIND_ESCALATION_SEC=600
WATCHDOG_DISK_WARN_PCT=85  WATCHDOG_DISK_CRIT_PCT=92  WATCHDOG_MEM_WARN_PCT=10
WATCHDOG_RESTART_ENABLED=true          # engine auto-restart on confirmed wedge
WATCHDOG_MAX_ENGINE_RESTARTS_PER_HOUR=3
WATCHDOG_KILLSWITCH_ENABLED=true       # engage-only escalation
HEALTHCHECKS_PING_URL=                 # layer-5 dead-man (unset = skip)
ALERT_TELEGRAM_BOT_TOKEN=              # falls back to TELEGRAM_BOT_TOKEN
ALERT_TELEGRAM_CHAT_ID=                # falls back to TELEGRAM_ADMIN_CHAT_ID
```

The engine side feeds the F-07 check via `data/pricing_freshness.json`,
published every `PRICING_FRESHNESS_PUBLISH_SEC` (30s) by the trade monitor —
local-disk write, off the per-tick hot path, no cloud reads (Cost Discipline
clean).

## Layer 4 — Telegram paging

Telegram is operational in-region again (owner confirmation 2026-07-10), so
it is the paging channel everywhere:

* **In-engine events** (tripwires, breaker, kill switch): already paged via
  `src/execution/telegram_alerts.py` — unchanged (these ride the engine's
  signal bot by design; they share its rate-limit budget deliberately).
* **Watchdog + workflows**: `scripts/notify_telegram.py` (stdlib-only,
  never raises, never leaks the token). CLI-callable for ad-hoc host use.
* **Dedicated alert bot (recommended):** set `ALERT_TELEGRAM_BOT_TOKEN` +
  `ALERT_TELEGRAM_CHAT_ID` to use a *separate* bot for watchdog/workflow
  pages. Wins over the fallbacks (`TELEGRAM_BOT_TOKEN` /
  `TELEGRAM_ADMIN_CHAT_ID`) when set. Why separate: paging never competes
  with signal delivery for the bot's rate budget, a leaked alert token
  can't post into the paid signal channels, and alerts land in their own
  chat with their own notification sound. Setup: @BotFather → new bot →
  token; send the bot one message (bots can't DM first); get your chat id
  from `https://api.telegram.org/bot<token>/getUpdates`.
* **GitHub workflows**: `vps-liveness.yml` (problems AND recovery) and
  `vps-backup.yml` (failure) page in addition to filing the auto-detected
  issue. The issue remains the durable morning-review record; the page is
  the minutes-level channel.

## Layer 5 — external dead-man's switch

Everything above dies with the box. Two independent pingers hit
[healthchecks.io](https://healthchecks.io) (free tier):

* the watchdog, at the end of every healthy loop (proves Docker + watchdog);
* a host cron every 5 minutes (proves the box, independent of Docker) —
  installed by `deploy/host/setup_host.sh`.

When pings stop, healthchecks.io pushes to the owner's phone (its own app
and/or its Telegram integration). This also breaks the GitHub-only vendor
coupling flagged in audit F-20.

## Layer 0 — host self-maintenance (`deploy/host/setup_host.sh`)

Idempotent, run as root, re-run on change: 2G swap + swappiness 10 ·
earlyoom (avoids dockerd/sshd/signing; prefers big python/redis) ·
unattended security upgrades · fail2ban (sshd) · ufw (deny inbound except
OpenSSH/80/443; `SKIP_UFW=1` to skip) · `360scalp.service` systemd unit
(stack up after host reboot, via `deploy.sh` so boot and deploy can't
drift) · nightly image/build-cache prune + journal vacuum · the host
dead-man cron. Covers audit S-7 (hardening as code).

---

## Rollout checklist (owner)

1. **GitHub secrets** (repo → Settings → Secrets → Actions): add
   `ALERT_TELEGRAM_BOT_TOKEN` + `ALERT_TELEGRAM_CHAT_ID` (dedicated alert
   bot, recommended) — or `TELEGRAM_BOT_TOKEN` + `TELEGRAM_ADMIN_CHAT_ID`
   to reuse the engine's bot. Without either pair the workflows behave
   exactly as before (issues only).
2. **VPS `.env`**: same choice — add `ALERT_TELEGRAM_BOT_TOKEN` +
   `ALERT_TELEGRAM_CHAT_ID` for the dedicated bot, or leave unset to page
   via the engine bot + admin chat.
3. **healthchecks.io**: create two checks (free) — "watchdog loop"
   (period 5 min / grace 5 min) and "host cron" (period 5 min) — put the
   first URL in `.env` as `HEALTHCHECKS_PING_URL`, pass the second to
   `setup_host.sh`. Install the healthchecks Android app or wire its
   Telegram integration.
4. **Deploy**: `bash deploy.sh` — autoheal + watchdog come up with the
   stack. Expect a "🤖 WATCHDOG" boot line in the alert chat within ~2 min
   (send a test: `docker exec 360scalp-v2-watchdog python scripts/notify_telegram.py "test page"`).
5. **Host layer**: `sudo REPO_DIR=$(pwd) HEALTHCHECKS_HOST_PING_URL=... bash deploy/host/setup_host.sh`.
6. **Drill it once** (15 min, do this — an untested pager is a hope, not a
   system): `docker pause 360scalp-v2-engine` → within ~2 min the engine
   goes unhealthy, autoheal restarts it, and your phone gets a page;
   `docker unpause` if needed. Then stop the host cron for 15 min and
   confirm healthchecks.io pages.

## What this does NOT change

No money-path behaviour: scoring, dispatch, FSM, exits are untouched. The
pricing-freshness publisher is observe-only telemetry. The watchdog acts on
container lifecycle and the kill switch only — both risk-reducing, both
audited, both paged.
