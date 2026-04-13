# Free-Channel Watch Lifecycle Audit — 2026-04-13

## 1. Executive summary

The repository currently has a real lifecycle system only for actual `Signal` objects. Free-channel `market_watch` posts are live, but they are scheduler-driven commentary with no tracked state, no persistence, and no follow-up path. `radar_alert` is only partially implemented: formatter/prompt support exists and scanner-side `_radar_scores` are populated for soft-disabled channels, but no runtime publisher or resolver was found in production code.

As a result, the system cannot later answer what happened after “ETHUSDT at a key level” or similar free-channel watch-style posts. The narrowest strong fix is to keep `market_watch` commentary-only, and implement a dedicated tracked lifecycle only for `radar_alert`-style free watches.

---

## 2. Verified current behavior

### `market_watch`

- Triggered by the silence-breaker scheduler after prolonged posting inactivity during active hours.
- Generated through the content engine and posted directly to the free Telegram channel as plain text.
- Carries lightweight context only: `time_utc`, `regime`, `btc_price`, `btc_1h_change_pct`, `hours_since_signal`, `key_level`, and `symbol`.
- The engine context currently hardcodes `key_level` to `"—"` and `hours_since_signal` to `0`, so the message framing can imply a meaningful watched level without any real tracked level behind it.
- No persistence, no ID, no state transition, no later resolver.

### `radar_alert`

- Prompt and formatter support exist.
- Scanner performs a radar evaluation pass for soft-disabled channels and records best candidates into `_radar_scores`.
- `_radar_scores` entries currently carry only `symbol`, `confidence`, `bias`, `setup_name`, and `waiting_for`.
- No production code path was found that consumes `_radar_scores`, calls `generate_content("radar_alert", ...)`, or posts radar alerts at runtime.
- No persistence, no expiry, no resolution, no follow-up.

### Other free-channel watch/commentary-style output

- Morning brief, London open, NY open, EOD wrap, and weekly card are scheduled commentary/summary content, not watch objects.
- Free-channel condensed signal previews and winning highlights do exist, but those are attached to actual paid-channel `Signal` lifecycle events, not commentary watches.

### Actual tracked lifecycle that already exists

- `SignalRouter` persists live paid-channel signals to Redis.
- `TradeMonitor` resolves those signals through TP/SL/invalidation/expiry.
- Free channel currently receives only limited downstream outcomes from real signals: condensed previews, TP2+/TP3 highlights, and recap/scoreboard posts.

---

## 3. Exact code path trace

### `market_watch`

1. `Bootstrap` starts `engine._content_scheduler.run()`  
   - `/home/runner/work/360-v2/360-v2/src/bootstrap.py:224-237`
2. `ContentScheduler._check_silence_breaker()` fires `market_watch` after `SILENCE_BREAKER_HOURS`  
   - `/home/runner/work/360-v2/360-v2/src/scheduler.py:125-140`
3. `_run_task("market_watch", ["free"])` calls `content_engine.generate_market_watch()`  
   - `/home/runner/work/360-v2/360-v2/src/scheduler.py:142-173`
   - `/home/runner/work/360-v2/360-v2/src/content_engine.py:244-247`
4. `_build_market_watch_context()` builds render context  
   - `/home/runner/work/360-v2/360-v2/src/content_engine.py:341-353`
5. `main._get_engine_context()` supplies base values, currently including `key_level="—"` and `hours_since_signal=0`  
   - `/home/runner/work/360-v2/360-v2/src/main.py:320-381`
6. `formatter.format_market_watch()` renders phrases like:
   - `📍 {symbol} at a key level.`
   - `Watching.`
   - `📡 Quiet market. Patience.`
   - `/home/runner/work/360-v2/360-v2/src/formatter.py:438-472`
7. `TelegramBot.post_to_free_channel()` sends the final text to `TELEGRAM_FREE_CHANNEL_ID`  
   - `/home/runner/work/360-v2/360-v2/src/telegram_bot.py:138-148`

### `radar_alert`

1. Scanner initializes `_radar_scores` as an in-memory dict  
   - `/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:597-600`
2. During `_scan_symbol`, scanner runs a radar evaluation pass for soft-disabled channels only  
   - `/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:3135-3176`
3. For candidates above `RADAR_ALERT_MIN_CONFIDENCE`, scanner writes:
   - `symbol`
   - `confidence`
   - `bias`
   - `setup_name`
   - `waiting_for`
   - `/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:3163-3175`
4. `main._get_scanner_context()` exposes `_radar_scores` as `channel_scores`  
   - `/home/runner/work/360-v2/360-v2/src/main.py:383-388`
5. Rendering support exists:
   - `content_engine.generate_content("radar_alert", ...)`
   - `formatter.format_radar_alert(...)`
   - `/home/runner/work/360-v2/360-v2/src/content_engine.py:120-205`
   - `/home/runner/work/360-v2/360-v2/src/formatter.py:169-255`
6. No production runtime caller was found in `src/` that consumes `_get_scanner_context()` or posts radar alerts.

### Other relevant free-channel paths

- Free condensed signal previews:  
  `/home/runner/work/360-v2/360-v2/src/signal_router.py:816-890`
- Free winning highlights from real signals:  
  `/home/runner/work/360-v2/360-v2/src/main.py:265-269`  
  `/home/runner/work/360-v2/360-v2/src/trade_monitor.py:681-705`  
  `/home/runner/work/360-v2/360-v2/src/signal_router.py:746-785`
- Paid-channel signal lifecycle persistence and monitoring:  
  `/home/runner/work/360-v2/360-v2/src/signal_router.py:236-327,675-686`  
  `/home/runner/work/360-v2/360-v2/src/trade_monitor.py:537-673`

---

## 4. Root cause of missing follow-up

The missing follow-up is caused by two different repository realities:

### A. `market_watch` is commentary, not a tracked watch object

- It is created by a silence-breaker scheduler, not by a watch-state subsystem.
- It posts plain text only.
- No watch ID/state object is created.
- No persistence is performed.
- No monitor loop exists to resolve it later.

### B. `radar_alert` is incomplete end-to-end

- Scanner-side candidate collection exists.
- Production posting does not.
- No watch persistence model exists.
- No expiry/invalidation doctrine is implemented.
- No component matches later paid signals back to prior free radar watches.

### Repo-specific concrete causes

- `_radar_scores` is keyed by channel name, not by watch instance.
- `_radar_scores` is in-memory only.
- `RADAR_CHANNEL_ENABLED`, `RADAR_PER_SYMBOL_COOLDOWN_SECONDS`, and `RADAR_MAX_PER_HOUR` are configured but unused in production `src/` wiring.
- No `src/radar_channel.py` file exists despite tests referring to it historically.
- Free-channel routing today is biased toward:
  - commentary posts
  - initial preview posts
  - positive highlights
  rather than full watch-state resolution.

---

## 5. Recommended doctrine

### `market_watch`

**Recommendation: remain commentary-only.**

Reason:

- Its prompt explicitly describes it as structure commentary with no signal yet.
- It is tied to silence-breaking, not to a specific candidate setup object.
- Forcing lifecycle semantics onto every quiet-market/free-commentary post would create noisy, artificial follow-ups.

Possible later refinement:

- Soften wording when no real `key_level` exists, but do not turn `market_watch` into a tracked object in the first fix.

### `radar_alert`

**Recommendation: become a tracked free-watch object.**

Reason:

- Its semantics are specific enough to imply a future outcome.
- It already carries bias/setup/waiting-for/confidence fields.
- It naturally maps to a later answer: did this evolve into a real setup or not?

### Outcome doctrine for `radar_alert`

Support in the first narrow implementation:

- **rolled_into_paid_signal**
- **expired / no trigger**

Add only if scanner context becomes strong enough:

- **invalidated**

Do **not** force in first PR:

- broad generic **confirmed** messaging if the real operational event is simply “it became a paid signal”

### Other message types

- Scheduled free-channel commentary (`morning_brief`, `london_open`, `ny_open`, `eod_wrap`, `weekly_card`) should remain commentary/summary only.
- Paid `WATCHLIST` tier signals are a different product object and should not be conflated with free commentary watches.

---

## 6. Implementation plan

### Strongest narrow path

1. Leave `market_watch` unchanged as commentary-only.
2. Implement tracked lifecycle for `radar_alert` only.
3. Add a small dedicated free-watch model/service rather than overloading `Signal`.

### Proposed design

#### New watch-state model

Add a dedicated model, for example:

- `watch_id`
- `symbol`
- `source_channel`
- `bias`
- `setup_name`
- `waiting_for`
- `confidence`
- `watched_level` (optional)
- `created_at`
- `expires_at`
- `status`
- `posted_to_free`
- `resolved_at`

This should be separate from `Signal`, because radar alerts are not executable trades and should not inherit TP/SL semantics.

#### Persistence choice

Use Redis if available, following the same architectural pattern as `SignalRouter` persistence.

Why:

- The repo already uses Redis for persisted signal state.
- Watch lifecycle should survive restarts.
- In-memory only would reintroduce silent loss of outstanding radar watches.

#### Triggering follow-up status

Implement a small watch service that:

- creates/persists a watch when a radar candidate is actually posted
- periodically checks for expiry
- resolves an open watch as `rolled_into_paid_signal` when a real paid `Signal` is later posted and matches:
  - same symbol
  - compatible bias/direction
  - compatible source/setup key
  - within watch TTL

#### Expiry behavior

- Set a bounded TTL, likely short intraday.
- When TTL passes with no matched paid signal, post one free-channel follow-up indicating the watch expired / did not trigger.

#### Avoiding duplicate or stale updates

- Dedupe key should likely be `(symbol, source_channel, bias, setup_name)`.
- Allow only one open watch per dedupe key.
- Do not repost the same open watch repeatedly unless:
  - confidence materially improves, or
  - prior watch is already terminal.
- Terminal statuses must be idempotent to prevent duplicate follow-ups.

#### Free-channel interaction with paid-channel real signals

- If a paid signal fires from a matching setup, resolve the radar watch to `rolled_into_paid_signal`.
- The free follow-up should acknowledge outcome without leaking premium entry/TP/SL details.
- Do not mirror the full paid signal lifecycle into free in the first PR.

---

## 7. Files likely involved

### Existing files

- `/home/runner/work/360-v2/360-v2/src/scanner/__init__.py`
  - enrich radar candidate data
  - hand off candidates to a real watch service

- `/home/runner/work/360-v2/360-v2/src/main.py`
  - instantiate and wire the watch service
  - connect paid-signal posting to watch resolution

- `/home/runner/work/360-v2/360-v2/src/content_engine.py`
  - add a real `generate_radar_alert()` wrapper if desired
  - optionally add follow-up generation helpers

- `/home/runner/work/360-v2/360-v2/src/formatter.py`
  - add deterministic free-channel follow-up formatting for:
    - rolled into paid signal
    - expired / no trigger

- `/home/runner/work/360-v2/360-v2/src/telegram_bot.py`
  - likely only reused for posting helpers

- `/home/runner/work/360-v2/360-v2/config/__init__.py`
  - add watch TTL / dedupe / follow-up config

### Likely new file

- `/home/runner/work/360-v2/360-v2/src/free_watch_service.py`
  or
- `/home/runner/work/360-v2/360-v2/src/radar_channel.py`

The new module should own watch lifecycle responsibilities instead of scattering them across scheduler/scanner/router code.

---

## 8. Test plan

### Unit tests

- radar candidate above threshold creates a new watch object
- duplicate candidate does not create a duplicate open watch
- watch state persists/restores via Redis
- expiry posts exactly one follow-up
- matching paid signal resolves exactly one open radar watch
- `market_watch` still creates no tracked watch state

### Integration tests

- scanner radar candidate -> free watch post -> later paid signal -> free resolution post
- scanner radar candidate -> no later paid signal -> expiry follow-up
- restart/resume with Redis-preserved open watches

### Regression tests

- silence-breaker `market_watch` behavior unchanged
- condensed free-signal previews unchanged
- free TP2+/TP3 highlight flow unchanged
- paid-channel signal lifecycle unchanged

---

## 9. Risks / scope traps

### Must avoid

- turning all “watching” or “quiet market” text into tracked lifecycle objects
- overloading `Signal` to represent radar watches
- building broad content-rewrite logic in the first PR
- leaking premium signal details in free-channel radar resolution posts

### Specific technical traps

- `_radar_scores` is currently channel-scoped and in-memory; building lifecycle directly on top of it without a new model will be brittle
- `invalidated` follow-up may be low-quality unless scanner exports a concrete watched level or invalidation doctrine
- free-channel noise risk rises quickly if expiry windows and dedupe rules are not strict

### Scope discipline

#### Must-fix now

- end-to-end tracked lifecycle for actual `radar_alert` posts
- persistence of open radar watches
- terminal follow-up for at least:
  - `rolled_into_paid_signal`
  - `expired / no trigger`

#### Nice-to-have later

- explicit `invalidated` outcome
- better `watched_level` extraction
- softer `market_watch` wording when `key_level` is unavailable

#### Do not change in the first PR

- broad rewrite of all free-channel content
- free mirroring of the full paid trade lifecycle
- conversion of `market_watch` into a tracked stateful subsystem

---

## 10. Recommended next PR title

**Implement tracked radar alert lifecycle for free channel; keep market_watch commentary-only**
