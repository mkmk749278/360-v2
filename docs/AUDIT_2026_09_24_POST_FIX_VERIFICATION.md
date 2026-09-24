# Post-Fix Verification Audit — 2026-09-24

Adversarial re-check of the 2026-09-23 audit (Session 153) and the fixes that
followed it: engine #1042–#1052, lumin-app #160–#162. Every claim below
carries its evidence class, because an unlabelled inference reads exactly
like a measurement:

- **[code]** read in the tree at the SHAs below, with file:line
- **[measured]** produced during this audit from live or public data
- **[recorded]** measured by an earlier session and written in
  `ACTIVE_CONTEXT.md`; not re-measured here
- **[inferred]** follows from code or data but was not observed happening
- **[not verifiable here]** needs the ops guest console, GCP, or the VPS

Trees audited: `360-v2@3a74830`, `lumin-app@0be43b1`,
`360ce-ops@47dac42`, `lumin-legal@1099d86`.

**What this audit could not reach.** No ops guest code, no GCP console, no VPS
shell. `read.firestore_projection`, `read.dispatch_funnel`, `read.ai_governor`
and `/track-record/trades.csv` were therefore not read. What *was* reachable:
the engine's unauthenticated `/api/track-record` and
`/api/track-record/signals` (1,678 delivered closed signals, 26 Jul → 24 Sep
03:19 UTC), `/api/billing/web/config`, Binance's public kline archive, the live
web app (headless Chromium), and GitHub issues and Actions history.

---

## 1. Scorecard

| # | Target | Baseline (23 Sep) | Now | Status |
|---|---|---|---|---|
| 1 | Monitor-loop `get_position` reads | 102,882/day at 1 member | 0 reads/tick while the index is active [code]; 106/day [recorded 23 Sep, 1.8h uptime] | **VERIFIED FIXED** |
| 2 | Project-wide Firestore read visibility | engine census only | Still engine-only. Signing-container and api-container reads are counted in memory nobody reads; the budget probe averages over process uptime rather than the Pacific-midnight quota day [code] | **PARTIAL** |
| 3 | Reads per live member per day at 1,000 | — | Floor ≈ 48 from listenKey keepalives, plus ~2,880 per member holding a position (reconciler), plus 288 per open position (index resync); all but the last invisible to the census [code, inferred] | **UNRESOLVED** — the `<5` target is unreachable by design |
| 4 | Silent exception on the invalidation path | `log.debug` | Per-uid fallback now `fail_open.record`; the caller still swallows with `log.debug` (`trade_monitor.py:2199`). 520 debug-only/silent handlers engine-wide [code] | **PARTIAL** |
| 5 | Active-key roster on a Firestore failure | — | A failed scan returns `[]` and the rebuild **persists an empty roster**: fan-out to zero users for up to 30 min [code] | **REGRESSION (latent, new)** |
| 6 | Live-position index resync | — | Lock-free scan in a worker thread, then wholesale replace: writes landing mid-scan are lost for ≤300s [code] | **NEW (latent)** |
| 7 | Naked-position invariant on engine closes | — | Stops are cancelled **before** the market close, the doc is marked CLOSED **even if the close fails**, and the reconciler never re-reads a CLOSED doc [code] | **NEW — Tier-0 (latent)** |
| 8 | Signing service under fan-out | — | Blocking Firestore + KMS calls on its event loop; unbounded `gather` fan-out; 12s client timeout; an entry that times out client-side can still fill with no position doc and no stop [code, inferred] | **NEW — Tier-0 at scale** |
| 9 | #988 "Position is open" on closed trades | endpoints empty in prod | Engine publishes each user's book to Redis (#1048); app renders "can't confirm" on `unavailable` (#162) [code] | **VERIFIED FIXED** (code; live not observed here) |
| 10 | Kill switch without Firestore | 503 when api blind (fixed 2 Sep) | Operator engage still requires a Firestore **write** (no local latch). The global breaker does hold an in-memory latch [code] | **PARTIAL** |
| 11 | `MOVER_AVWAP_SCALP` SHORT | retirement candidate | **Not retired**: absent from `DEFAULT_RETIRED`; 3 delivered after the audit [measured] | **UNRESOLVED** |
| 12 | Net edge after entry drift | +0.115%/trade (9–23 Sep, n=687) [recorded] | Same 687 rows read +0.369% net at book prices → implied drift **25.4 bps** (was 22.6) [measured + recorded]. 7d book net +0.185% ⇒ ≈ −0.07% rebased [inferred] | **UNRESOLVED** |
| 13 | MVRTP share / direction | 59% post-diversification | 63% / 65% / 62% (7/14/30d); book 77% LONG [measured] | **UNRESOLVED** |
| 14 | #1026 chronic probes | 4 chronic, streaks 396–469 | `ai_governor_blind` cleared (#1047). `edge_reconciliation` (+0.64R, streak 68), `tuned_variants` (108 non-stamps, streak 56) and `entry_feature_inputs` (streak 15) are still firing in #1046, thresholds unchanged [measured] | **PARTIAL** |
| 15 | Clean liveness runs | failing since 9 Sep | 1 success in the last 40 runs (23 Sep 10:55); 4 failures since. The "hourly" cron actually runs every 3–5h [measured] | **UNRESOLVED** |
| 16 | `session_quality` over its cap | 70/200 vs cap 0.35, held back | No code change. Over-cap pages only as one line of the aggregate issue; its current state is not visible from here [code] | **UNRESOLVED** (owner) |
| 17 | Governor context | 200/200 blind | Wired. The "book" is **top-of-book L1 only** (`depth_quality: top_of_book_only`), not ±1% L2 depth. 6 of 15 post-boot verdicts still book-blind [code, recorded] | **PARTIAL** |
| 18 | Governor latency and timeouts | — | Timeout is 20s, not 1.5s. The call is spawned off-loop and fails open to "no verdict". Latency of the last 100 calls needs `read.ai_governor` | **NOT VERIFIABLE HERE** |
| 19 | Web cold boot | 3.1–4.2s, blank navy | Branded splash paints at 0.59–0.70s. Flutter's first frame is unchanged at 3.4–3.8s under baseline conditions; 5.1–5.8s on emulated 4G; 8.2–8.7s at 4× CPU [measured] | **PARTIAL** |
| 20 | `en-US@posix` locale | RangeError, blank | **Still `RangeError: Incorrect locale information provided`** on the live site. The splash's 20s "Reload" link reloads into the same crash, and the boot guard never sees the error [measured] | **UNRESOLVED** |
| 21 | Consent checkbox contrast | ~1.2:1 | 3.76:1 on `bgCard` [measured]. Passes WCAG 1.4.11 for controls (3:1); 4.5:1 is the threshold for text, not controls | **VERIFIED FIXED** |
| 22 | "No runaway losses" | present | Removed. The replacement, "Every open trade is placed with a stop-loss on Binance" (`welcome_page.dart:440`), discloses no gap or slippage risk and is absolute where #7 and `user_owned` entry-only takes are not [code] | **PARTIAL** |
| 23 | Rebuild scope in the big pages | 2,727 / 2,353 lines | 2,723 / 2,438 lines. `setState` counts unchanged (14 / 12). Feed price ticks go through per-symbol `ValueNotifier`s [code] | **PARTIAL** |
| 24 | Polling while hidden or backgrounded | 5s poll always | The feed is gated on `TickerMode` and lifecycle. The detail sheet runs its own ungated 5s timer that calls `setState` on the whole sheet (`signals_page.dart:1515`) [code] | **PARTIAL** |
| 25 | Sub-11px font sizes | 103 | 0 [measured] — but still 644 hard-coded literals across 20 sizes, and only 11 `textTheme` references | **FIXED** (floor) / **UNRESOLVED** (tokens) |
| 26 | Raw exceptions shown to users | ~10 pages | 28 raw `$e` sites in 17 files, including phone sign-in, OTP, profile, Play-billing verification and the crypto checkout; plus 12 `${e.message}` sites [code] | **PARTIAL** |
| 27 | Live auto-trade users | 0 placed, all paper | Not re-read; the last reading is 23 Sep [recorded] | **UNRESOLVED** |
| 28 | Dual-rail billing in the Terms | legal review pending | The crypto rail is live (`/api/billing/web/config`: $15 / $25 per 30 days, `test_mode:false`) [measured]. The Terms (updated 25 Jul) describe Google Play Billing only [code] | **UNRESOLVED** |
| 29 | Public performance claim | — | The unauthenticated `/api/track-record` publishes book-price results (+0.21%/trade net over 30d) with no disclosure of the ~25 bps/trade entry bias [measured] | **NEW risk** |

---

## 2. Root-cause verification

### 2.1 Firestore read path (section 1A)

**Call graph [code].** `trade_monitor.py:1143` `_check_per_user_invalidation`
→ `signal_dispatch.py:2092` `get_fsm_positions_for_signal` →
`position_state.py:879` `index_live_positions_for_signal`. The index is a
process-local dict (`position_state.py:519`), maintained write-through inside
`put_position` / `delete_position` under an `RLock`
(`position_state.py:993-1002`, `1035-1038`). A terminal write evicts. There is
no generation gate on this read; the generation counter serves other caches.
With the index active, the path makes **zero Firestore calls per tick** for
paper users and users without a position. The only I/O is the roster:
`_active_uids` (30s TTL) → `_read_roster` (300s TTL, invalidated by Redis
generation), i.e. ~288 reads/day flat.

**Holes.**
1. *The caller still swallows.* `trade_monitor.py:2197-2205` catches
   everything `get_fsm_positions_for_signal` raises — including
   `_active_uids()` and a quota refusal on the roster — with `log.debug`.
   The `fail_open` routing added in #1042 covers only the per-uid fallback.
2. *The roster persists an empty list on failure (latent regression).*
   `_scan_active_uids` returns `[]` on any exception
   (`firestore_keystore.py:494-496`). Both `list_active_uids`
   (`:517-523`) and the 30-minute `rebuild_active_roster` loop
   (`:455-463`, `bootstrap.py:655-667`, `CONTROL_INDEX_REBUILD_SEC=1800`)
   then call `_write_roster(uids)`, which writes `[]` and bumps the
   generation. On 2 Sep the pattern was reads refused while writes still
   succeeded (53k reads against 25 writes), which is the exact case where
   this lands: every process then serves "nobody is keyed" until the next
   successful rebuild. The docstring calls an empty write "a real answer about
   a project with no connected keys". A failed scan is not that answer.
   `auto_dispatch` detects the empty roster only after 5 fan-outs and a
   3-cycle streak.
3. *Resync can lose writes.* `resync_index` (`position_state.py:817-857`) runs
   via `asyncio.to_thread` (`bootstrap.py:624`). Its scan is lock-free, and it
   then **replaces** `_index` wholesale. `enable_position_index` merges live
   writes on top; `resync_index` does not. A position opened during the scan
   is invisible to the pre-TP dispatcher, the trail governor and tight
   invalidation for up to 300s. A position closed during the scan can come
   back as OPEN.
4. *The census cannot see the largest future consumer.* Every signed Binance
   call runs `get_key_blob` (one Firestore read) and a KMS Decrypt
   **inside the signing container** (`signing_service/handler.py:150,168`).
   That container's `_reads` counters are never published, so
   `/system/firestore`, `read.firestore_projection` and
   `firestore_read_budget` all exclude them. The same is true of the api
   container. `budget_health` (`firestore_reads.py:263-290`) also
   extrapolates over process uptime; the quota is a Pacific-midnight day.
5. *No transaction locks* [code]: there is no `transaction` anywhere in
   `src/`. The real contention is event-loop blocking. `put_position` is a
   synchronous Firestore `.set()` called directly from async FSM code
   (e.g. `position_fsm.py:1477,1582`), so each write stalls the monitor, the
   mark feed and the fan-out while it runs.

**Rate [recorded].** 1,445 reads/day total, engine process only, 1 member, at
23 Sep 13:48 UTC with 6,503s of uptime. It was not re-read here, and GCP
Cloud Monitoring was not reachable.

### 2.2 FSM invariants (section 1B)

**States [code]** (`position_state.py:63-116`): `PENDING_ENTRY`, `PENDING`,
`OPEN`, `PRE_TP_FIRED`, `TP1_HIT`, `TP2_HIT`, `TRAILING`, `CLOSED`,
`CANCELLED_NO_FILL`. The spec's `SUBMITTED / FILLED / STOP_PLACED` do not
exist. Nor does a transition table. `position_state.py:69` says "Allowed
transitions are pinned in `position_fsm`", but `handle_event`
(`position_fsm.py:292-440`) dispatches on the order phase and guards only
`is_terminal`. The terminal-close orphan sweep (`position_fsm.py:418-423`) is
correct for exchange-driven fills.

**Tier-0 finding: engine-initiated closes can leave a naked position.**
Both `close_fsm_positions_for_signal` (`signal_dispatch.py:1998-2077`) and
`close_single_fsm_position` (`:2177-2240`) do the same four things in order:
1. cancel **every** protective algo order, stop included;
2. place a reduce-only MARKET close;
3. on any failure other than `-2022` (signing timeout, `-1003`, network), log
   an error and carry on;
4. set `state = CLOSED` and persist, "regardless of whether the MARKET order
   succeeded" (`:2065-2070`).

The comment claims "an engine restart / reconciler will catch any remaining
Binance state drift". It will not. `reconcile_user` keeps only non-terminal
FSM docs and returns before fetching Binance when none are left
(`reconciler.py:259-267`). It never walks Binance positions that lack a live
FSM doc. The ops `NakedPositionDetector` reads the signal's SL price, not
per-user stop orders (`360ce-ops/app/agent/detectors.py:72-86`, its own
LIMITATION note). The outcome is a position open on Binance with **no stop,
no manager and no page**. The app would also show it as "Closed on Binance",
because that headline comes from the FSM state.

This path runs on `invalidated` / `expired` / `cancelled` / monitor
`sl_hit`, and on tight-mode early kills. Latent while nobody trades live.

**Tier-0 at scale: entry timeouts.**
- `place_signal` places the MARKET entry (`position_fsm.py:1488`) **before**
  it persists the position (`:1582`).
- `_submit_order` (`order_placer.py:798-813`) does not handle
  `asyncio.TimeoutError`, and the signing client's timeout is 12s
  (`client.py:51`).
- The signing service does a blocking Firestore read and a blocking KMS
  Decrypt inside `async handle_request`, so concurrent requests serialise.
- The fan-out is an unbounded `asyncio.gather` over every user
  (`signal_dispatch.py:1554`).

Put together: at a few hundred live users, requests queue past 12s. The
client gives up, but the service keeps processing requests already in the
socket, so orders still reach Binance. The resulting fill carries a Lumin
`clientOrderId` with no position doc. The FSM logs "event for unknown
position" and returns (`position_fsm.py:343-353`), and nothing places a stop.
A 500ms KMS stall now delays every queued request. [inferred from code; not
load-tested]

**Invalidation during placement [inferred, low probability].** `place_signal`
awaits between SL and each TP. A tight-mode kill that lands in that window
closes the position, and `place_signal` then keeps laying TP/SL orders
against it. Those orders are never swept, because the sweep runs only in the
event handler.

**#988 [code].** The root cause was neither a stale Dart stream nor an FSM
status mismatch. It was two things:
- *A modelling bug.* The row copy was hard-coded present tense on an
  append-only placement record.
- *A process-scope bug.* The api container never initialises
  `position_state`, so both endpoints returned empty in production.

It is fixed by `3f9ea77`/`d011235` (#1048: `snapshot:user_positions` plus a
90s `…:meta` liveness key, with a three-state reader in
`redis_engine.py:786-827`) and lumin-app `0be43b1` (#162). Live evidence
(the meta counters and a Trade tab holding an open position) was not
observed here.

**Kill switch [code].**
- `engage_global` (`kill_switch.py:333-350`) invalidates its cache, then
  writes Firestore. If the write fails it raises, and nothing changes locally.
- Order admission reads the cached doc, and a read failure raises and refuses
  the order (`kill_switch.py:274-286`). Reads being down therefore fails
  closed; writes being down leaves the switch unthrowable.
- The Redis bridge (`safety_switch_bridge.py`) routes the flip to the engine,
  but that ends in the same Firestore write.
- The automatic global breaker keeps an in-memory `_tripped` latch
  (`tripwires.py:539`) that refuses orders even if persisting the trip fails.
  The operator switch has no equivalent.

**Signing and KMS jitter [code].** There is no fallback, DEK cache or retry
budget, only the 12s client timeout, and every signed call pays a Firestore
read plus a KMS round trip.

### 2.3 Quant (section 2)

Data: 1,678 delivered closed signals from the public `/api/track-record/signals`
[measured]. These are **book prices** (the stamped entry), not the tape.

| Window | n | gross | net (−0.07%) | win | PF | Σ net | max DD (Σ%) |
|---|---|---|---|---|---|---|---|
| 7d | 287 | +0.255% | +0.185% | 36.2% | 1.19 | +53.0% | −21.3% |
| 14d | 664 | +0.434% | +0.364% | 36.6% | 1.34 | +241.5% | −48.7% |
| 30d | 1,238 | +0.278% | +0.208% | 33.7% | 1.19 | +257.4% | −69.1% |

**Drift decomposition.** On the same 687-row window the Session-153 rebase
used (9 Sep → 23 Sep 10:00):

    gross +0.439% − drift 0.254% − fee 0.070% = +0.115% net

The drift is implied as book minus rebased; the 0.115% rebased figure is
[recorded], not re-measured. It is up from 22.6 bps on the 30 days to 6 Sep.
If 25 bps holds, the 7d book (+0.255% gross) is ≈ −0.07% rebased and the 30d
book is ≈ −0.05% [inferred]. Rebasing directly needs dispatch timestamps,
which the public endpoint does not carry.

**MVAVW SHORT.**
- **Not retired** in code (`path_retirement.py:69-72`, `config:1131`).
- **Delivered after the audit:** PUMPUSDT 10:22, TRUMPUSDT 14:07 and TAOUSDT
  15:49 on 23 Sep, all TP1 [measured].
- 60d: n=78 across 53 symbols; mean net −0.468%; win 24.4%; PF 0.60;
  Σ −36.5%; max DD −50.1%.
- Symbol-clustered bootstrap (10k): CI **[−0.977, +0.005]** at 60d and
  [−1.017, +0.029] at 30d.
- On book prices the upper bound now touches zero because of three winners
  on one day. Rebased by the ~0.25% drift, it would stay negative [inferred].
- The dark lane consumes no order-rate budget and resolves from the in-memory
  store (`main.py:1938`). A retired path still costs its full scan work,
  because it is diverted at the enqueue site.

**Concentration.**
- MVRTP is 62–65% of delivered trades across windows, and the book is
  **77% LONG**.
- Daily correlation with BTC returns is weak: +0.02 for the whole book;
  LONG trades net +0.28% / +0.37% / +0.50% on down / flat / up BTC days.
- Intraday, 14 hour×direction buckets had ≥3 trades that all hit SL. All
  were LONG, together −107% against +257% book net over 30d. Stop-outs
  cluster on the long side [measured; close time is a proxy for exposure].

### 2.4 Telemetry and governor (section 3)

**#1026 → #1046.** #1026 was auto-closed by the one clean run (`vps-liveness.yml`
closes on recovery), and #1046 reopened 4h25m later.

- `ai_governor_blind` was actually fixed by `0263044`: the getters are wired,
  and the probe is unchanged (≥95% fully blind in the last 50). It is absent
  from the three alerts after 15:20.
- `edge_reconciliation` has had no code change. MEAN_REVERT's
  realised-minus-counterfactual moved +0.43R → +0.64R, so the emission policy
  is steering that path on a counterfactual that is **too pessimistic**.
- `tuned_variants` has had no code change; `atr_arm_uncomputable` grew
  13 → 108.
- `entry_feature_inputs` has had no code change. `campaign_prev_won` is
  `first_leg` by construction on a campaign's first leg, which is arguably a
  probe-definition defect rather than a data one.
- Seven `PredicateProbe`s return **healthy** when they themselves throw
  (`main.py:3535, 3628, 3693, 3802, 3885, 3945, 4070`).

**Governor.**
- Provider `google`, model `gemini-3.7-flash`, 20s timeout
  (`config:4755-4859`), spawned with `create_task`, apply OFF.
- The book imbalance comes from the bookTicker snapshot: one level per side
  (`scanner/__init__.py:3939-3947`), with `DEPTH_LIVE_FOR_CONSUMERS=false`.
  L2 ±1% depth is **not** in the prompt.
- CVD is the 15m-preferred slope.
- `macro_moved` is never passed, so that re-review trigger cannot fire (open,
  owner).

### 2.5 Mobile (section 4)

**Measured on `app.luminapp.org`.** Headless Chromium 1194, 393×851 @2.75,
cold cache:

| Condition | Branded splash (FCP) | Flutter first frame |
|---|---|---|
| No throttle (baseline conditions) | 0.59–0.64s | 3.44–3.84s (n=3) |
| 9 Mbps / 60ms RTT | 0.63–0.70s | 5.06–5.84s (n=2) |
| + 4× CPU | 0.63–0.70s | 8.22–8.75s (n=3) |

The web splash fixed the *perception*; boot time is unchanged. Android is
branded natively by CI (`build-apk.yml:107-141`) but was not measured (no
emulator).

**`en-US@posix`.** The live site throws `RangeError: Incorrect locale
information provided` before `runApp`, outside `_boot`'s `try`. The user sees
the branded splash, then after 20s "Lumin is taking longer than usual to
start. Reload", and Reload reproduces the crash. The app uses no `intl`
itself (grep); the throw is in the Flutter/web locale bootstrap.

**Other findings.**
- The polling, font and exception findings are the #24–#26 rows of the
  scorecard.
- `'Could not save: $e'` is in the very sheet whose timer is ungated
  (`signals_page.dart:1569`).

### 2.6 Commercial and legal (section 5)

- **Dispatch.** Nobody is live [recorded 23 Sep]. The `auto_dispatch` probe
  now calls all-paper healthy, correctly, and says "No user is on live".
  #989 (mode `both` rejected by every read schema) is still open.
- **Billing.**
  - The crypto rail is web-only (`kDistribution == web`), which is
    Play-compliant.
  - It is live at $15 / $25 per 30 days.
  - Terms §4 (`terms.md:52-54`) specifies Play Billing only: auto-renewal,
    cancellation through Play, Play refunds. The crypto rail's price,
    renewal model and refund policy appear nowhere.
  - Price parity: ₹1,000 ≈ $11–12, so Assist costs ~27% more on USDT.
- **Posture.** The Terms and Risk pages hold "informational only, NOT
  personalised investment advice" and "individual developer, not regulated".
  Three claims need review against that posture:
  - The onboarding line "AI analysts score each signal" (`welcome_page.dart:345`)
    describes a deterministic scorer; the only LLM lane is measurement-only.
  - "High-probability setups" sits over a 34% win rate.
  - The public track record at book prices (#29) is the number marketing
    would quote.

---

## 3. Blockers to broad rollout or marketing spend

1. **Engine-initiated close can strand a naked position** (2.2). Fix
   before any user goes live. Options:
   - close first and cancel after confirmation;
   - re-place the stop when the close fails;
   - keep the doc non-terminal until Binance confirms flat.
   All of these are FSM changes and need owner sign-off.
2. **Entry timeout → unmanaged fill**, plus signing-service serialisation and
   an unbounded fan-out (2.2). Needed before tens of live users:
   - persist `PENDING` before the entry;
   - bound fan-out concurrency;
   - move Firestore and KMS off the signing loop, or cache DEKs;
   - reconcile Binance positions that have no FSM doc.
3. **Roster rebuild writes an empty roster on a failed scan** (2.1).
   Distinguish failure from empty, the way `_roster_apply` already does.
4. **Firestore budget is structurally incompatible with 1,000 live members
   under a 50k/day ceiling**, and the census cannot see signing-container
   or api-container reads (2.1).
5. **Edge is not established.** Rebased net is ≈ 0 or negative on recent
   windows [inferred]; MVAVW SHORT is still delivered; the public track
   record overstates by ~25 bps/trade. **Do not spend on marketing that
   quotes this number.**
6. **Legal:** the Terms do not cover the live USDT rail. "AI analysts" and
   "high-probability" copy needs review.
7. **App:** the posix-locale crash, and raw exceptions on sign-in, OTP and
   billing screens.
8. **Monitoring:**
   - three chronic probes untouched;
   - the "hourly" watch runs every 3–5h;
   - seven probes read healthy when they crash;
   - nothing detects a Binance position without a live FSM doc.

## 4. Owner decisions this audit needs

- Sign-off to fix blockers 1–2 (FSM and dispatch: owner-sign-off class).
- Retire `MOVER_AVWAP_SCALP:SHORT` (runtime `retired_paths`, no deploy).
- A guest code, to re-read the Firestore projection, the dispatch funnel and
  governor latency live.
- Whether the public track record should publish rebased (tape) figures
  beside the book figures.
