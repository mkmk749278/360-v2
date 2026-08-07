# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## 🟢 SESSION 115 2026-08-07 — the price-action lane had three of its four layers

Engine #897, ops #150 / #151. The owner read the lane's page and asked two
questions that turned out to be the same question: *"this is huge raw data … we
don't get clarity"* and *"how can we sort out good signals"*.

### The answer was structural, not statistical

**§1 of the program doc defines price action as a FOUR-layer read, and the lane
had three.** Location (LevelBook), Trigger (sweep + reclaim) and Confirmation
(footprint delta) shipped in #886. **Layer 1 — Context — never did**, while
`src/volume_profile.py` had computed POC and the value area since long before the
lane existed and the lane never imported it.

Why layer 1 and not a better filter: a sweep + reclaim is a **failed break**, so
it is a mean-reversion trade. It pays in **balance** (price rotating inside a
value area, rejected at the edge, returning toward POC) and traps in
**imbalance** (value accepted away from the area, so each failed break is a pause
before continuation). Those two states produce an **identical layer-2/3/4
signature** — same level, same sweep, same aligned delta. Nothing already stamped
could separate them, which is why every column on that page read like noise.

`vp_entry_zone` / `vp_level_zone` / `vp_poc_room_pct` (signed toward the trade) /
`vp_value_width_pct` + raw POC/VAH/VAL, on the emit path, applied to nothing.
Verified live within minutes: PUMPUSDT LONG below POC reads `+0.631%` where a raw
distance would read negative — the `cvd_slope` error avoided rather than paid for.

### The empirical case, and what it cost to state it correctly

BEATUSDT whipsawed 24% and the lane bought reclaimed support **ten times** through
it for ten losses. The worst nine form **one 4.5h run worth −85.71%** against a
whole-book net of −78.25% — remove it and the book reads **+7.46%**. *The sign of
`NO EDGE DETECTED` was one episode.*

**Eight of those ten were stamped `TRENDING_UP`.** So the scanner's regime label
is *not* a usable layer 1 for this, and "add a context layer" keyed on it would
have **confirmed** the losing entries rather than filtered them. That correction
was made mid-session, before it reached a PR body — the first read had been "the
lane bought into a downtrend it could see", which the stamps disprove.

### Two column-ranking dead ends, checked so nobody re-runs them

* **`rr`** — win rate 46% → 32% → 24% → 5% across quartiles, monotonic, survives
  removing BEATUSDT, and **mechanical**: `rr` *is* target ÷ stop distance, so a
  farther target must be hit less often. Expectancy does not follow it, and
  "filter to low rr" is the `TREND_PULLBACK_EMA` TP1 mistake this file already
  carries.
* **`level_score`** — 45% → 8% headline, but 0.49 rank-correlated with `rr`; hold
  `rr` in [1.5, 3.0] and it shrinks to 35% vs 26%. Mostly the same geometry.

Both measure the *trigger*. The trigger was not what was failing.

### Three ops defects the same read turned up (#150)

* **80 flat expiries reported as losses.** The engine scores `EXPIRED` at 0.00%;
  `losses = n_closed - wins` swept every zero in, so the page read `115W / 347L`
  where the book was `115W / 267L / 80 flat` — 25% against 30% on the rows that
  resolved to a level. Both denominators published now.
* **The concentration panel could not see the concentration that decided the
  verdict.** Its `symbol · side · entry` key is right for one sweep re-stamped at
  one price and **structurally blind to a moving symbol** — a trend hands out a
  new entry every time, so it read `1.12 rows/move` and *"largest single move =
  1.0% of all rows"* over the BEATUSDT run. An episode panel now sits beside it.
  #816 arriving at the display side.
* **Two sentences had outlived their data** — *"whole closed book is under 50
  rows"* above 462, *"expected to be almost all unstamped today"* above 16%.

### Seams closed on the way

* **`LANE_PROVENANCE_FIELDS` carried the sentence *"derived from the dataclass
  rather than typed twice — a hand-kept second list is the drift this repo has
  paid for under three different names"* directly above a hand-kept second
  list.** It had already dropped eight fields once (Session 114) and would have
  dropped all seven layer-1 fields. Now genuinely derived from
  `dataclasses.fields(LaneSignal)` minus the Signal contract — the half that does
  not grow — with a test asserting every field lands in one set or the other.
  The two existing tests that loop over it covered the new fields for free.
* **The lane probe watched refusals only**, so a volume profile returning `None`
  on every row would have flat-lined the whole split invisibly — an empty column
  reads as *"not enough rows yet"*, which is exactly what a dead stamp hides
  behind. `layer1_stamped` / `layer1_blind` are counted on the emit path and the
  probe fails when the lane has emitted and stamped none of it.

### Open, and deliberately not acted on

* **`EMIT_COOLDOWN_S`'s comment still claims "one move, one row".** BEATUSDT
  disproves it — ten rows, one whipsaw — because a per-symbol 30-minute timer
  bounds how *often* a symbol stamps and says nothing about how many rows one
  continuous move contributes. Changing the key or the duration alters what the
  lane stamps, and picking a new one off this window is the move this file
  forbids. Needs a session with fresh evidence.
* **The shadow rule `balance_only` is half fitted.** "Inside the value area" is
  the value area's own 70%-of-volume definition and predates the lane; *which*
  layer-1 conditions to combine was chosen while looking at this book. The owner
  asked for it knowing that; the page says so. **Its first number is a hypothesis
  this window generated, not one it tested** — re-earn it on rows stamped after
  2026-08-07.
* **Watch `level_zone`.** The first three stamped rows all read `interior`. If
  that persists, the swept levels are not value boundaries at all — a finding
  about the LevelBook against the value area, not about the rule.

---

## 🟢 SESSION 114 2026-08-06 — Phase 5 shipped, and then six seams were found under it

Eleven engine PRs (#886–#894) and six ops PRs (#139–#144). **One of them added a
feature. The rest repaired seams in work shipped earlier the same day**, and
every one was found by the owner reading a screen, not by 8,113 tests.

### What shipped

| # | Change |
|---|---|
| #886 | Phase 5 — the standalone price-action lane |
| #887 / ops #139 | the snap ledger counted re-detections, not evidence |
| #889 / #890 | the lane was evaluated hourly; its census was surfaced nowhere |
| ops #140 | the data-intake refusal card the engine had been writing into a void |
| #891 | eight provenance fields dropped by the serializer; a throttle that died on restart |
| #892 / ops #142 | layer 1 stamped — the lane had no notion of trend |
| ops #143 | two of this session's own pages were not in the nav |
| #893 | nothing ever flushed the structural-veto ledger |
| #894 | both structural ledgers flushed and never loaded |
| ops #144 | filter the book by stamp, and export it |

### The one shape, six times

Every defect this session was a **seam**: two halves that each looked complete.

| defect | one half | the other |
|---|---|---|
| lane call site | wired | called hourly, not per scan |
| lane census | written | read by nothing |
| provenance | set on the signal | dropped by the serializer |
| emit throttle | in memory | ledger on disk — every deploy re-armed it |
| layer 1 | declared on the dataclass | never assigned |
| veto ledger | stamped | never flushed |
| both structural ledgers | flushed | never loaded — each deploy erased them |
| two ops pages | built and tested | not in the nav |

None crashed. None left an empty screen. Each produced a **full-looking artifact
describing nothing** — which is why the suite could not see any of them and the
owner could see all of them.

**Every one now has a derived guard** — the requirement is computed from the tree
rather than written in a list, so the next instance fails CI:

* `tests/test_nav.py` — every registered `/signals/` page must be linked, no two
  labels or active keys may collide, and every destination is driven as a real
  request.
* `tests/test_ledger_flush_wiring.py` — a module with `get_ledger()` and a
  `flush()` must have a caller in `main.py`, must define `load()`, and
  `get_ledger()` must **call** it. Defining a method is not calling it.
* `test_the_payload_key_is_the_one_ops_reads` — drives the real assembler and
  asserts where the key lands, *including that it is not where I first guessed*.
* `test_the_scanner_passes_the_regime_it_already_computed` — pins the call site
  by AST, not the parameter.

### The two that cost the most

**The veto measured nothing for a day.** `structural_veto.stamp` was wired
correctly at the enqueue choke point and filled an in-memory ring;
`/engine-data/structural_veto_v1.json` never existed. Its own `flush()` carries
the `force=True` docstring about idle lanes rendering STALE — **and had no
caller**. #839's rule verbatim: a docstring describing a heartbeat is not a
heartbeat. It is the surface measuring ~97% of the book, and this session
pointed at it three times as the highest-value read available.

**Flush without load is worse than neither.** Neither structural ledger had a
`load()` at all, so each restart began with an empty ring and the first flush
after boot **overwrote** the file. The snap page read 12 rows and then 8 with a
4,000 cap and "nothing evicted" beside it — nothing *was* evicted; the window was
destroyed. Four deploys, four erased windows, while a file on disk made both
lanes look persistent. It also invalidated a reading published earlier the same
day: the snap's "thin evidence" was not a rare mechanism, it was a ledger being
wiped.

### What the data now says

* **Depth is alive and reproduces.** Two independent windows: 14/40 and 15/40
  sign flips, mean |Δ| 0.483 and 0.444, top-1 saturated near ±1 while top-20 sits
  near zero. Membership changes between windows — a stable rate with unstable
  membership is what a coin flip looks like. Still instantaneous snapshots.
* **Phase 3's primitives bound themselves small.** Order blocks would flip
  `bool(fvgs) or bool(orderblocks)` on **43 of 777** detections (5.5%); the wide
  FVG window would admit **40 of 777** (5.1%). Both are ~5% levers.
* **92% of the book is scored on the wrong chart** — 11 of 12 censused signals
  would move off 5m. Deterministic, not statistical: it is a census of which
  paths trade which timeframe. It still cannot say *how much better*.
* **The lane has no edge on the rows so far.** 60 closed at 15.0% win, Wilson
  [8.1%, 26.1%], **−1.097% per signal net**. Its own `MIN_RR = 1.2` floor needs
  45.5% to break even; the interval has never approached it across four windows.
  Rows per move **1.09**, so this is not a re-detection artefact.

### The one cell worth watching, and why it is not a finding

`round` levels read 55% win / +1.047% over 11 closed rows while every swing
timeframe sits at 0%. Interesting because it cuts *against* the program doc,
which treats round numbers as the weaker generator. **CI [28%, 79%], best of 16
cells drawn.** It cannot be acted on. If it survives to ~40 closed rows still
clearing 45.5%, that is the first real finding this lane has produced.

### Decisions taken

* **Do not purge the unstamped rows.** Clearing would have taken the closed book
  from 74 to 12 — those rows are missing *labels*, not *outcomes*, and precision
  comes from n. A filter (ops #144) gives the clean read without deleting
  evidence, and the capped ring rotates them out on its own.
* **Do not choose `MIN_RR` from this window.** It is a well-shaped lever — it
  filters and moves no target, so the TPE trap does not apply — but 45 closed
  rows cannot supply the number.
* **Do not tighten the lane before reading the veto.** §5 of the program says
  application 6 answers "does structure carry information on this book" on 97% of
  it in days, and calls that a precondition for the standalone lane being worth
  building. It has been the right answer all session and I reached for the lane's
  own thin window twice before taking it.

### Verify after this deploy

1. **`unstamped` counts must stop growing** — 81 on layer 1, 70 on the level
   split. They are frozen by definition; if either climbs, a stamp is not wiring.
2. **`/signals/structural-veto` joined count.** Stamped rows climb with the
   enqueued book (~300/day); joined rows only arrive as delivered signals close
   (~16/day). **Still 0 in 24h means the join itself is broken** — that would be
   the seventh instance of this session's shape.
3. **Snap and veto row counts must survive a restart.** They never have. A count
   that drops across a deploy means #894 did not take.
4. **Rows per move stays near 1.00** on `/signals/price-action`. Above 1.5 and
   badged `concentrated` means the cooldown rehydrate regressed.

### Still open

**Phase 7** (the verdict surface) is the only phase left, and applications 1, 3
and 5 of §5 are unbuilt. All seven effect flags remain OFF and every one waits on
a data window rather than on engineering — and **tomorrow is the first window any
of them has ever had**, because until #894 no window survived a deploy.

`SETUP_TF_CORRECTION_LIVE` is the odd one out: a **bug fix**, not a mechanism.
Pricing it needs a shadow gate chain, not a data window, and that is its own
change.

---

## 🟢 SESSION 113 2026-08-05 — the price-action program, Phases 0 → 6

*(Sections below record 0→2c as first written; 2c's repair, and Phases 6, 4 and 3,
are recorded here.)*

### The depth feed shipped silent, and the ops page caught it in minutes

`FUTURES_DEPTH`: **40 streams, 40 silent, 0 messages, 0/40 books fresh** — while
the pool read **HEALTHY** and the aggTrade pool beside it on identical config had
0 silent.

**Binance serves book streams and trade streams on MUTUALLY EXCLUSIVE routed
paths.** Measured against the live vendor, one stream per connection, 5s each:

| stream | `/market/stream` | `/stream` |
|---|---|---|
| `@aggTrade` · `@kline_1m` · `@markPrice` | **OK** | silent |
| `@bookTicker` · `@depth` · `@depth<N>` | silent | **OK** |

`@depth20@500ms` was not the wrong name and 500ms was not the wrong speed — every
depth variant including the bare `@depth` is silent on `/market/stream`.
`WebSocketManager` hardcoded that path for every pool **and** stripped any suffix
from `.env`, so it was not fixable by config. Fixed in #880: per-pool routed path,
plus a guard that logs loudly when a pool's declared path cannot serve its streams
(a *mixed* pool gets a different message — that needs splitting, not repathing).

This is the **2026-05-14 blackout class**, and the docstring written to fix that
outage is what gave it away: it enumerates the `/market` streams — kline,
aggTrade, markPrice, forceOrder, ticker — and **depth was never in the list**.
Wrong path = handshake succeeds, PING/PONG keeps it alive, `is_healthy` stays
true, zero frames arrive.

**It shipped because the stream-name format was taken from knowledge and never
exercised.** The Real-Data-First rule says read the wire first; it was applied
only after the owner surfaced the symptom. Dark-first limited the damage —
`DEPTH_LIVE_FOR_CONSUMERS` was off, so nothing reached a signal.

### Depth, once alive, says something loud

First window: **14 of 40 sign flips**, mean |Δ| 0.483. The `top-1` column is
saturated near ±1 (+0.994, +0.991, −0.961) while `top-20` sits near zero (−0.045,
−0.043, +0.044). That is the signature of a one-level "imbalance" being a coin
flip — whichever side happens to hold the larger order at the touch — against a
book that is close to balanced. **Not yet a verdict**: one instantaneous snapshot
of 40 symbols, and COTIUSDT flips the other way, so it is not a one-directional
bias. Needs hours before `DEPTH_LIVE_FOR_CONSUMERS`.

### Phase 6 — retention by delivery (#881)

The rings hold 4,000 rows, evict oldest-first, and are filled by enqueues of which
**~0.5% deliver**. So a ring fills ~32h after deploy and then every re-detection
of a high-volume path evicts a row that might have carried a verdict —
preferentially destroying the rare population to make room for the common one,
invisibly, because the ledger stays exactly full.

Two rings now: pending evicts oldest-first (correct — cheap evidence), delivered
cannot be evicted by a pending row. Delivered is still bounded, but an eviction
*there* is counted under its own name and logged at ERROR, because it means the
retention policy itself is losing verdicts. `delivered` is a field **on the row**,
so it survives the JSON round trip — held only in the ring it would be correct
until the first restart and then silently back to evict-by-recency with a
full-looking ledger (#842's class).

One policy, not one per lane: `structural_snap` and `entry_features` had identical
rings, and the program says the rule applies to Phase 5 "from the start".

### Phase 4 — the structural veto (#882)

Every enqueued signal now carries the distance to the nearest **opposing** level
(ATR and %), whether it falls **between entry and TP1**, that level's score and
age, and the value-area position. Signed toward the trade throughout.

The gate is real and suppression-stamped, and enforces **exactly one** rule:
`target_behind_level`. Chosen because **its threshold comes from no window** — not
"closer than N ATR" but "the target cannot be reached without breaking a level",
which is arithmetic on values the signal already carries. Distance rules need an
N, and an N taken from the window it is judged on is what `tpe_smc_zone` was
retired for. Those ship as stamps.

Why this before the standalone lane: structurally-*triggered* paths are **0.62%**
of the book, none delivered. The veto is measurable against ~97% of the book from
day one.

### Phase 3 — layer 3 repaired, dark (this change)

`orderblocks` had **no writer** (474,467 observations, 100% empty), so eight
`bool(fvgs) or bool(orderblocks)` gates have always been `bool(fvgs)` alone. And
`detect_fvg` sees twelve bars — which is what makes a deliberately loose gate
behave like a strict one (median zone distance 0.13 ATR, max 0.52, no tail).

Both **widen a rejecting gate**, so both are dark — and dark means the detector
**runs for real** while the gates behave **byte-identically**:

* the order-block detector's output lands on `orderblocks_measured`, never
  `orderblocks`. Assigning it to the live key would ship the *effect* — eight
  gates passing candidates they reject today with nothing measured behind it;
* FVG detection runs **once at the wide window** and the live list is that result
  filtered by index — **proved byte-identical** to `detect_fvg(lookback=10)`
  across 300 random series, because "equivalent" is not enough when the
  alternative is silently changing emission on deploy;
* the gate comment was corrected to say what it checks, rather than the gate.

**The census bounds itself on screen**: these gates reject *pre-scoring*, so the
candidates a wider window would admit have no row and no outcome. It answers *how
much of the book would change* and is structurally incapable of answering *how
much better it would be*.

### Open — every flag is waiting on data, none on engineering

| Flag | Default | What it hands over |
|---|---|---|
| `TICKS_LIVE_FOR_CONSUMERS` | OFF | five consumers, seed snapshot → live ticks. Drift grows with uptime, so an early read **understates** it |
| `DEPTH_LIVE_FOR_CONSUMERS` | OFF | four consumers, one quote → twenty levels. Read the **sign-flip** count first |
| `STRUCTURAL_VETO_ENFORCE` (+ paths) | OFF | `target_behind_level` |
| `ORDERBLOCKS_LIVE` | OFF | eight gates gain a second real condition |
| `FVG_WIDE_LIVE` | OFF | eight gates see 60 bars instead of 12 |

Remaining: **Phase 5** (standalone lane — gated on Phase 4's answer) and
**Phase 7** (verdict surface — worth waiting until 4 has data, since an empty
verdict page is the thing this program keeps warning about).

### Verify after the next deploy (priority order)

Every one of these distinguishes *running* from *shipped*, which is the whole
lesson of the depth pool reading HEALTHY with 40/40 streams silent. **A lane that
cannot be confirmed alive is not dark — it is off, and nobody knows.**

1. **`/diagnostics/data-intake` → depth card.** Expect ~40/40 books fresh and
   messages climbing. `0 accepted` with a HEALTHY pool means a routed-path
   regression — check `_routed_path` before anything else.
2. **Same page → primitive census.** `orderblocks` should read `measured_dark`
   with a non-zero would-flip count, and `fvg_lookback_wide` should show
   `live=10 measured=60`. `not_implemented` there means Phase 3 did not deploy;
   `measure_disabled` means the tunable is off.
3. **`/signals/structural-veto`.** Rows accumulate immediately; the *joined*
   count only grows as signals deliver and close, so an empty splits table on
   day one is expected and is **not** a fault.
4. **Feature-liveness probes** — `depth_feed`, `structural_veto_lane`,
   `footprint_bars`, `aggtrade_feed`. Each abstains cleanly when its tunable is
   off rather than paging, so a silent watchdog here means healthy *or*
   disabled, and the census rows above are what separate the two.
5. **Retention counters** on `/signals/structural-veto`. `evicted_delivered`
   must stay **0**. Non-zero means the retention policy is losing exactly the
   population it exists to keep, and the delivered cap needs raising.

### Do not do these without new evidence

* **Do not flip any of the five flags on the first window.** Depth's 14/40
  sign-flip read is one instantaneous snapshot of 40 symbols; the veto's splits
  need delivered rows, which arrive at ~16/day.
* **Do not read the Phase 3 census as "how much better".** It is structurally a
  *how much would change* number — those gates reject pre-scoring, so the
  candidates a wider window would admit have no outcome anywhere.
* **Do not "fix" an empty veto splits table.** No joined rows yet is the quiet
  case, and the row count beside it is what tells them apart.

---

## 🟢 SESSION 113 (as first written) — Phases 0 → 2c

`docs/PRICE_ACTION_PROGRAM.md` is the design of record: what price action is,
what we actually read from Binance, and a seven-phase build. Written before any
code, with every fact labelled **[verified]** / **[documented]** / **[inferred]**.

**The framing that governs the whole thing:** a controlled test of 54 mechanical
SMC rule variants over 2.5M bars produced a best win rate of 56.3% and **zero
profitable variants after costs**, and our own book already loses ~10× its edge
to fees. So the program builds the **measurement** before the signal, and the
missing **data layer** before the measurement — and it is instrumented to be able
to return "no edge", which is a supported outcome rather than a failure.

### Shipped this session

| Phase | What | PR |
|---|---|---|
| 0 | weight accounting made enforceable | #874 |
| 1 | `/diagnostics/data-intake` — the X-ray | #875 · ops #133 |
| 2a | subscribe the trade feed that already had a handler | #876/#877 · ops #134 |
| 2b | the footprint — volume at price, per bar | #878 · ops #135 |
| 2c | the resting side of the book — depth | #879 · ops #136 |

### The audit's four findings, none of which failed

* **`data_store.ticks` was a seed-time REST snapshot** and five call sites read
  it as live, including a `$500k cumulative tick volume` gate. A complete
  `trade` handler, the store, its cap and the gate telemetry all existed — and
  **nothing subscribed the stream**. Fixed in 2a.
* **`orderblocks` has never had a writer**, so every
  `bool(fvgs) or bool(orderblocks)` is `bool(fvgs)` alone. Phase 3.
* **`detect_fvg` sees twelve bars**, which is what makes a deliberately loose
  gate behave like a strict one. Phase 3.
* **The order book was one bid and one ask**, and *four* consumers were written
  for a book: the OBI execution gate (its own `OBI_DEFAULT_LEVELS` is **20**,
  against a one-element list), `entry_features.book_imbalance`, the WHALE OBI
  check, and the AI predictor's 0.25-weighted score. Fixed in 2c.

Every one is a **provenance** fault — the right shape, from somewhere other than
where the consumer assumes. None raises, which is why they survived, and why
Phase 1 built the page before anything else changed.

### Phase 0's third defect was the interesting one

The first cut of the weight audit only saw calls whose endpoint was a **string
literal** — and the fix that merged `fetch_recent_trades`'s two branches into one
call with a `path` variable therefore made *the very call site the module exists
for* invisible to its own audit. **Restoring `weight=1` left the suite green.**
A check that looks like coverage, stops seeing its subject the moment the subject
is refactored, and reports success — produced inside the change meant to prevent
exactly that. *Verify a fix by reverting it*; the first revert passing was the
finding.

### Phase 2c — four decisions against the program document

* **Partial depth, never the diff stream.** A diff consumer that misses a resync
  **does not fail — it drifts**, and keeps answering with confident wrong
  numbers. Every partial message is a complete top-N snapshot, so a drop costs
  one interval and cannot corrupt state.
* **500ms, not the document's 100ms.** Every consumer reads at scan cadence or
  at dispatch; 100ms is ~150× fresher than the fastest reader at 5× the messages.
* **Silence is a fault here and is not one on aggTrade.** Depth publishes on a
  fixed clock, so a silent symbol is a stopped feed, never a quiet market. The
  bound is derived from the configured speed, and the probe is keyed on symbols
  **subscribed** — a dead feed leaves its snapshots behind, so counting what the
  store *holds* reads healthy while nothing arrives (#815's shape).
* **It is money-path, and §8 had it in the wrong column** — §6's own text says it
  replaces `top_of_book_only` for the evaluator paths, which is the sentence that
  puts 2a in the money-path column. Two sentences of one document disagreed.
  Corrected; 2c ships dark-first.

### Open — the flags waiting on a data window, not an opinion

Both are **measurement ON / effect OFF**, and both need the owner to read the
disagreement on `/diagnostics/data-intake` before flipping:

* **`TICKS_LIVE_FOR_CONSUMERS`** (2a) — hands five consumers from the seed-time
  snapshot to the live series. The drift panel sizes the error, and it is a
  function of uptime, so a page read minutes after a deploy **understates** it.
* **`DEPTH_LIVE_FOR_CONSUMERS`** (2c) — hands four consumers from one quote to
  twenty levels, one of them the *final* gate before dispatch. Read the **sign
  flip** count first: `book_imbalance` is signed toward the trade so its sign
  *is* the reading, while the OBI gate compares a fraction to 0.65 — the two are
  harmed by different things, which is why they are counted separately.

### Next, in the program's order

Phase 3 (repair layer 3 — order blocks, FVG lookback; both change what emits, so
dark + sign-off), then **Phase 4, the structural veto** — the one with leverage,
because it needs no new signal and is testable on the whole delivered book from
the day it ships. **Phase 6 (retention by delivery, not recency) has no
dependencies and should land before Phase 4's ledger fills** — the structural-snap
ledger reaches its 4,000-row cap ~32h after deploy, after which every
re-detection evicts a row that might have carried a verdict.

---

## 🟢 SESSION 112 2026-08-04 — "are we using price action?" → the snap that never ran

Owner asked what price action is and whether the engine uses it. The audit, then
the wiring.

### The audit answer

Three layers, three different answers:

| Layer | Verdict |
|---|---|
| **Trigger** — does a signal fire | Mostly **no**. ~82% of the enqueued book is MA/indicator-triggered |
| **Score** — confidence once it fires | **Yes** — SMC sweeps/MSS carry 25 of 100 pts, and MVRTP's kept rows average 19.3 of them |
| **Geometry** — where SL and TP go | **Almost none**, and the one piece built for it was dead code |

* `MOVER_TREND_PULLBACK` is **362 of 615** enqueued (59%) and is three SMAs plus
  one ATR; TPs are fixed 1.0/1.6/2.5 R-multiples. Add MVAVW/QCB/TPE/MEAN_REVERT/
  DIVCONT/MA_CROSS → **505 (82%)**. Structurally-triggered paths (SR_FLIP 55,
  FAR 30, LSR 21) are **106 (17%)**.
* The **pattern engine barely moves anything**: `_score_patterns` returns 5.0 as
  the no-pattern neutral out of 10, and MVRTP's kept rows average **5.85** — 1,525
  lines of `chart_patterns.py` shifting the dominant path by under one point.
* `orderblocks` still has **no writer** (`not_implemented`, 100% empty), so every
  `bool(fvgs) or bool(orderblocks)` has always been `bool(fvgs)` — already known,
  re-confirmed.
* The aux SMC channels (`ScalpFVGChannel`, `ScalpOrderblockChannel`,
  `ScalpDivergenceChannel`) are registered in `main.py:316` and have **no rows at
  all** in the funnel — zero generation in the window. Not investigated further.

### The finding, and the fix

`structural_levels.py` has held a level-aware SL/TP1 snap since it was written,
and `build_channel_signal` **called it** — behind `if candle_highs is not None`,
which **no caller in the engine has ever satisfied**, under the comment *"this
snap is shared by EVERY evaluator that passes candle arrays"*. Dead twice over:
every evaluator overwrites `sig.stop_loss` / `sig.tp1` on the next line. Its test
passed for months by hand-feeding the argument production never supplies.

Wired in `src/structural_snap.py` at `Scanner._enqueue_signal`, after the
min-distance clamp — geometry is rewritten four times between the evaluator and
there. **Measure ON, apply OFF**, plus a per-path allow-list so one flip cannot
move 19 paths on evidence from the one that is most of the book. Bounds: the stop
moves at most ±30% of designed risk, TP1 moves **nearer only**. Ops:
`/signals/structural-snap`.

### Open — needs a data window, not an opinion

* **Nothing has been measured yet.** The ledger is empty until this deploys.
  The TP1 arm is fully decidable from MFE; the SL arm has two named undecidable
  classes that remove opposite ends of the distribution. Read the decidable
  fraction before any delta, and do not expect the arms to be comparable.
* **How often can the snap even fire?** The band is relative to the *designed
  risk*: a 3% stop searches 2.1–3.9% from entry, while a quiet 20-bar window's
  swings sit well inside 1%. Pinned as a test (`test_a_swing_nearer_than_the_band_is_not_a_candidate`)
  because the tempting move on seeing a book full of `unchanged` is to widen the
  band, which would be a threshold invented to fit a window.
* `round_step_pct` stamped rather than fixed — the round grid is 20% wide below
  ~$0.10 and therefore inert on much of the mover book.

### The second defect, fixed in the same branch

`_get_primary_timeframe` was `return "5m"` for **every** channel, and it is read
by **six** money-path consumers, not one: continuation-sweep evidence (25-pt SMC
dimension), the VWAP extension gate, the OI + funding gate, cross-timeframe
volume divergence, the chart-pattern confidence bonus (10-pt Patterns dimension),
and the volume inputs to the composite score. All six were reading 5m bars for
setups that trade 15m / 1h / 1m.

`src/setup_timeframes.py` is now the single declaration (the snap re-exports it,
same object). The correction is **dark** — `setup_tf_correction_live` off,
`_get_primary_timeframe` returns 5m byte-identically — while the per-signal
census runs from deploy. Ops panel on `/signals/structural-snap`.

**The census bounds itself and says so on screen:** five of the six consumers run
*before* the stamp exists, so they decide whether a candidate is in the ledger at
all. It answers *how much of the book is affected*, never *how much better it
would be*. Pricing the correction needs a shadow gate chain — a separate change,
not attempted here.

### Not done, deliberately
* `_evaluate_trend_pullback`'s SMC gate comment-vs-code gap is unchanged (already
  measured and closed out 2026-08-02).

---

## 🟢 SESSION 111 2026-08-04 — two surfaces that describe suppressed candidates, and they are disjoint

Owner asked for LSR / FAR / MOVER_AVWAP_SCALP next, and supplied the dark-feed
export (292 rows, 2026-07-31 → 08-04, resolve age 4.7s — current).

### What the three paths actually say

* **LSR and FAR are unreadable, and the dark feed proves it rather than
  inferring it.** The 2026-08-03 16:16 ``_build_scan_context`` fix (#108) changed
  both evaluators — LSR had been skipping its HTF POI anchor check, FAR falling
  back to the 5m struct-scan. Of their decided dark rows, **14 of 15 (LSR) and 21
  of 21 (FAR) predate it**; the edge matrix agrees at 98% pre-fix. LSR's apparent
  +0.585% is n=15, CI **[−0.311, +1.404]**, and halves to +0.292% on removing two
  rows. Re-read in a week; today both surfaces describe dead code.
* **MVAVW is the one with a valid sample** — 111 dark rows, unaffected by that
  fix: **40.6% win, −0.121%, CI [−0.72, +0.48]** over 101 scored. Its dominant
  blocked gate ``execution:overextended`` reads −0.174% on n=100. Flat noise;
  the gate is not costing anything. (My earlier −0.38R read off the matrix
  overstated it — see the cap below.)
* **The clearest result in the file**: ``setup_compat:regime_STRONG_TREND`` —
  n=30, 16.7% win, **−1.201%, CI [−1.81, −0.53]**, the only gate whose CI
  excludes zero. Emphatically correct.
* Entry timing matches MVRTP on every path: losers' median peak +0.22→+0.56%,
  winners' median heat 0.33–0.50%. Binary and fast is engine-wide, not one path.

### The mistake, and it is mine

I read the ``mean_revert_emission`` alert (+0.50R, *"the gating is COSTING us"*)
against the dark lane's −0.66% and reported a contradiction with a
recommendation to check the alert before acting on it. **There is no
contradiction.** ``suppression_audit.feeds_edge_matrix`` returns False for every
pre-scoring reject, and **every one of the six dark gates is pre-scoring**
(``setup_compat:*`` / ``execution:*``). The two populations are **disjoint by
construction** — a path can read positive on the matrix and negative in the dark
feed while both are correct, because they are not measuring the same candidates.

Nothing on either surface said so. The exclusion lives in one docstring on the
producing side; both readers describe themselves as *"gate-blocked
counterfactuals"*.

### What shipped (engine #872)

* **The edge matrix now states its denominator.** Every cell is a
  ``deque(maxlen=50)`` and **1,569 of 8,538 were pinned at the cap**, so ``n``
  was ``min(seen, 50)`` and a saturated cell is a rolling most-recent-50 window
  beside sparse cells that are all-time. Evictions are now counted at the moment
  they happen, **persisted** (a counter resetting on deploy reports every cell
  unsampled afterwards), and published as ``n_evicted`` / ``n_seen`` /
  ``sampled`` on the cell and ``held of seen`` in the truth report. The counts
  ride in a reserved ``__evicted__`` key, not an envelope, so a rollback loses
  the counts rather than the store.
* **Both surfaces name their population.** The truth report's edge-matrix
  section says post-scoring-only, names the dark lane as where the pre-scoring
  rejects are measured, and says the two are disjoint. ``gated_path_verdict``
  carries the same words into every probe that reads it, including
  *"confirm the output is actually being stopped post-scoring before loosening
  anything"*.

Deliberately **not** shipped: emission probes for LSR / FAR / MVAVW. They would
need per-path detection counters the evaluators do not have, and
``gated_path_verdict`` reads the post-scoring matrix while these three die
pre-scoring — the probe would inherit exactly the stage mismatch this session
was about. Worth doing once the verdict can read the right population.

### The thing worth remembering

**Two surfaces that describe "suppressed candidates" in the same words can
partition the candidates between them.** The rule already in this file — *"check
the surfaces against each other on the population where their definitions
differ"* — assumes the populations overlap. When they are disjoint, agreement is
impossible and disagreement is not evidence of anything. Before comparing two
measurements, **ask whether either could ever have contained the other's rows**;
and a surface whose population is a subset must say which subset, on the surface,
not in the docstring of the function that filters it.

---

## 🟢 SESSION 110 2026-08-04 — MVRTP is the book, and it is ~2.4 points of win rate short

Owner: *"analyse all the mover trend pullback path signals, and why still lot
hitting SL — entry timing, structural, sessions, exit methodology."*

**91 of the last 100 delivered signals are `MOVER_TREND_PULLBACK`**, so "why is
this path losing" and "why is the product losing" are currently the same
question. The window (2026-07-28 -> 08-04): 29 wins at +4.72% avg, 42 full stops
at -3.46% avg, 20 scratches, **-9.57% total / -0.105% per trade**. Payoff is
1.36:1, so break-even needs **43.2%** including a 0.07% round trip; the path
delivers **40.8%** of decided trades. It is marginally short, not broken — which
reframes every lever below.

### What the data says (verified, not inferred)

* **Entry timing is binary and fast.** Winners' median drawdown is **0.02%** —
  they never go negative. Losers' median peak is **0.33%**; 11 of 42 never went
  green at all, 25 of 42 never cleared 0.5%, and the median full stop dies **30
  minutes** (two 15m bars) after dispatch. The losses are wrong on arrival, not
  shaken out. Corollary: because winners never approach their stop, stop *width*
  only changes the size of the losses.
* **The clock is the biggest single split.** Asia / off-hours / any weekend: 50
  trades, 18.0% win, **-59.14%**. Weekday London/Overlap/NY: 41 trades, 48.8%
  win, **+49.58%**. Permutation p=0.0013, CIs disjoint, and it replicates on the
  15k-row edge matrix where Asia and off-hours are the only negative sessions.
  Not a cherry-picked cell: `classify_session` already scores this (ASIA 0.45,
  OFF_HOURS 0.30, x0.6 weekend) and **no emission decision has ever read it**.
* **Direction is a confound, not a finding.** SHORT looks awful (-24.43%) but
  p=0.093 and the CI spans zero; Asia *longs* alone lose -23.79% while
  prime-window shorts are +6.19%. Act on the clock, not the side.
* **The exit is working.** Winners capture a median **91.7% of their peak**, and
  TP1 sits about where these moves actually top out. There is no case for moving
  it — see #870's own lesson on TPE. The one leak: 20 trades (22%) ran a median
  2.6% into profit and closed for 0.00% or -0.10% on the BE ratchet.
* **Confidence does not discriminate here.** 80+ scored 29.7% win / -8.03%;
  70-75 scored 43.5% / +7.60%. Winners average 77.71 against losers' 78.08. With
  n=91 that is "no evidence of discrimination", not "inverted" — but the gate
  filters 2,441 and keeps 11,180 on that score.

### The defect: every MVRTP stop ships tighter than the one its TP ladder was built from

**46 of 46** signals in the 2026-08-04 dispatch log — structural **4.13%** median
against **3.09%** shipped, ratio 1.21-1.37. `predictive_ai.adjust_tp_sl` rescales
the SL *distance*, and `_PREDICTIVE_SLTP_BYPASS_SETUPS` — the hand-maintained
list of "structurally-protected paths" — contains eleven low-volume setups and
**neither mover path**, i.e. not the ~94% of the delivered book. The list predates
them and nobody added them: the deny-list-is-a-floor shape again.

It was invisible because the closed record kept only the structural figure, under
a name that reads like the shipped one, so every R on every ops surface divides
by a stop the trade never had. Finding it took a dispatch-log diff by hand.

**The obvious fix does not survive checking.** Of 19 stopped trades with a usable
stamp, **10 would have hit the wider stop anyway**; only 5 died in the band
between the two. Widening back makes those 10 losses bigger to rescue at most a
handful — so this ships as *visibility*, and the bypass-list decision is the
owner's with data in hand. Finding and fix are separate deliverables.

### What shipped (engine #871) — measurement ON, enforcement OFF

* `session_quality` is now a **core entry feature** on every path (plus `session`
  / `is_weekend` as metadata), stamped in `capture()` off the same clock as
  `stamped_at` and injectable via `now_ts` so the suite cannot drift.
* `sep_15m_pct` is stamped for MVRTP — the 15m term of `max(15m, 1H fan)`, so the
  ledger can finally say *which* term carried a candidate past the mover floor.
* Two `entry_quality` rules, **both shadow**: `session_quality` (< 0.8, exactly
  "weekday London/Overlap/NY" on the engine's existing scale) and
  `mover_stack_15m` (< `MOVER_TP_MIN_STACK_SEP_PCT`, the path's own floor applied
  to the 15m term alone). Neither is a repair of a filter the engine already
  applies, so neither enforces; ops switches auto-register from the registry.
* `shipped_sl_distance_pct` travels onto the closed record beside
  `sl_distance_pct_at_entry`, and a new truth-report section renders designed vs
  shipped per setup — with unstamped rows **excluded and counted apart**, because
  0.0 means unknown and never "no override".

### The thing worth remembering

**A normalised figure can be honest and still describe a stop nobody placed.**
#848 fixed the denominator against a stop that had been *moved after entry*; this
is the same class one stage earlier — a stop moved *before* entry, between the
evaluator and the wire, by a list that simply never learned about the path that
became the whole book. When two stages may rewrite a value, record both ends: the
gap is the measurement.

---

## 🟢 SESSION 109 2026-08-03 — the dark lane could not answer "how much was on the table", by construction

Owner, against `/signals/dark-live`: *"implement same like live features in dark
feed — max PnL before hitting SL, and same exit strategies like Held to stop in
dark feed too."*

Neither was answerable, and the reason was not a missing column. `_walk` stops at
the **first** TP1-or-SL touch, so on a row that closed at TP1 the recorded
`mfe_pct` is bounded by the TP1 distance *by construction* — it says how far the
trade ran before its own exit and is structurally silent on how far it was going
to run. Everything after that touch was never walked, which is the same reason no
held-to-stop or laddered exit could be priced from this ledger.

Rendering that column under the words "max profit" would have produced a number
that is always about right and never means what it says: the truncated-measurement
class, and a close cousin of the R-denominator bug (#848) — a figure whose *shape*
is fine and whose *definition* is not what the reader assumes.

### What shipped (engine #869 + ops #127)

A **second arm** per dark row: the same bars walked with TP1 removed, exiting only
at the original stop or at the six-hour horizon (`dark_emission._walk_hold`). It
never touches `status` / `pnl_pct` / `r_multiple`. It records the peak before the
stop bar, the same peak including it, the drawdown on the way to that peak, and
the highest ladder level reached before the stop — plus `tp2`/`tp3`, which the
ledger had never stamped, so no ladder leg could be priced.

Ops (`app/data_sources/dark_exit_sim.py`) prices the **Profit tab's own catalog**
off those stamps — same keys, same labels, a test asserting they stay in sync —
and `/signals/dark-live` grew two panels: max PnL before the stop per path, and
every exit method against the row's own exit on one shared population, net of a
fee charged to the baseline as well.

### The thing worth remembering

**A second arm needs its own sweep.** The held arm exits at the stop, normally
*later* than the row's own TP1, so a resolve loop keyed on `status == OPEN` would
have frozen every arm at the moment its row closed — #835's shape exactly, a
measurement inheriting the lifetime of the thing it rides. The population is now
"owed a verdict on either arm", the freshness stamps grade whichever arm is still
walking, and `resolution_health` watches the same set, so a frozen arm on a closed
row pages instead of quietly rendering as a result.

### Watch

Rows written before this deploy carry no `hold_status` at all. They are their own
bucket on screen — not a zero — and rows still inside the six-hour horizon backfill
themselves on the next resolve cycles; older ones retire unmeasured, which is
correct and is counted rather than hidden.

---

## 🟢 SESSION 108 2026-08-03 — the alert named its cause, and the cause was four live evaluators

The probe fixed in #866 fired once more and answered the question it had been
unable to ask: `level_dist_r` absent on **4,000 of 4,000 rows across all five
paths, cause `no_levels`, zero `none_ahead`**. Not a market condition — a
populated level book produces *some* `none_ahead`. Driving the real `LevelBook`
with production-shape candles returns 60 levels, so the book was never broken.

### Root cause — a rebuilt dict with a hand-maintained carry-over list

`_build_scan_context` assembles `smc_data` once and sets `level_book_levels`.
Every scalp channel then re-runs SMC detection with its own timeframe
preference, rebuilds the dict from `SMCResult.as_dict()` (12 detector keys) and
copies the context's additions across via an **enumerated list of 12 key
names**. `level_book_levels` and `cvd_15m` were not on that list, and all
**eight** scalp channels take the branch unconditionally — so this was every
evaluator, every scan, since the keys were introduced.

Same class as `is_tradfi_perp`: a list excludes exactly the keys somebody
already typed. The carry is now **structural** (anything the context has that
the detector does not produce), with an explicit override set for the three
keys that exist on both sides and where the context deliberately wins.

### The live blast radius was four evaluators, not the measurement column

Each read a dropped key, each took a fallback, and three carried a comment
saying that fallback "only triggers in tests / pre-warm":

| Evaluator | Behaviour with the key absent |
|---|---|
| LSR | HTF POI anchor check **skipped entirely** — §3.4a's hard-block never applied |
| SR_FLIP | legacy 5m pivot detector — replaced 2026-05-17 (43% of signals MFE=0) |
| FAR | 5m struct-scan — replaced after 115 signals at 39% MFE=0, −0.72% NET/sig |
| DIVERGENCE_CONTINUATION | legacy 5m CVD instead of the 15m read (`cvd_15m`) |

FAR is the setup whose +0.846R dark-lane reading had already prompted a
promotion request — its level sourcing was the legacy path throughout, which
makes that already-thin argument thinner.

### Owner decision

Presented three options (dark-first behind a flag / restore live now /
measurement only). **Owner chose restore live now**, against the dark-first
default, having been told plainly that it changes emission on four live
evaluators with no shadow window. Shipped as chosen. **Watch the delivered
feed and those four paths over the next windows** — this is the one change in
recent sessions with no measured before/after.

### Also shipped

- `cvd_source` on every entry-feature row. Restoring `cvd_15m` silently
  redefines `cvd_slope_aligned` from a 5m slope to a 15m one — same column,
  different series. Recorded rather than schema-bumped: the bump would discard
  ~4,000 rows whose other twelve features are unaffected.
- `ROW_METADATA_KEYS`. Whether a value counted as a feature depended on where
  its line sat in `capture()`, and `stack_sep_pct` — declared by
  `MOVER_TREND_PULLBACK` — was assigned *after* the missing-accounting, so it
  could never be reported dark. A blind spot in the very probe fixed in #866.

### Verification

Contract test parses `_build_scan_context`'s own source for the keys it
writes, so a key added tomorrow is covered without anyone updating a list.
**Verified by reverting**: against the enumerated list the test fails naming
`level_book_levels`. Full suite green.

### Open

- **Unmeasured**: how many signals actually change on the four evaluators. No
  shadow window was run, by owner decision.
- `mean_revert_emission` (+0.55R blocked, n=3486), `edge_reconciliation`
  (+0.38R, sign points at the cost model), `cohort_edge_gate` (working as
  designed) — all still open from Session 107.
- Ops `/signals/entry-features` can now render `level_dist_r` for real, and
  should split on `cvd_source` so the 5m and 15m populations are not pooled.

---

## 🟢 SESSION 107 2026-08-03 — three probes that paged without naming a cause

Hourly liveness alert, five findings sustained 15 audit cycles. Two were
diagnosable from the alert's own data and are fixed; three are real and are
reported below rather than acted on.

### `entry_feature_inputs` — 3 of its 8 items were noise, and the other 5 asserted a cause

- **The probe judged paths on features they never declared.** `capture` emits
  one flat feature block for every setup, so an input only some paths supply is
  `None` on the rest by construction. `extension_pct` needs `ma_slow`:
  `TREND_PULLBACK_EMA` and `MOVER_TREND_PULLBACK` pass it, MEAN_REVERT /
  MOVER_AVWAP_SCALP / RANGE_FADE do not — and those three read *"absent on
  EVERY stamp"* forever. That is the **'unused' the probe exists to tell dark
  apart from**, arriving as the alert. The tell was inside the alert itself:
  the two paths that *do* supply `ma_slow` were not among the flagged.
  `missing_by_setup` now counts only `features_for(setup)` — the same registry
  `describe_features` ships to ops, so the probe judges the columns the page
  actually draws — and `undeclared_absences` counts what was set aside, because
  a narrowed mode with no trace is how the next reader misreads the probe.
- **`level_dist_r` is absent on all five paths, and the message asserted a
  cause it could not know.** One `None` covered four findings needing four
  different responses: a dark LevelBook (`no_levels`), a level shape the reader
  cannot parse (`unreadable_levels`), broken geometry (`no_geometry`), and a
  fully working read whose answer is *"nothing opposing overhead"*
  (`none_ahead`) — which is not a fault at all. The old text said *"upstream is
  dark"* for all of them. `level_distance_r_with_reason` names which; the row
  carries it under `reason_key("level_dist_r")`, written **after** the
  missing-accounting so metadata never counts as a feature; the alert now
  renders the histogram. **Which cause is live is still unknown** — the ledger
  is on the VPS. The next audit cycle answers it.
- Paging behaviour is unchanged: a declared feature absent on every row is still
  a column ops cannot split on. Only the *narrowing to noise* was removed.

### `tuned_variants` — "66 unexplained non-stamps" was literal

Four paths produce a residue and the probe could name none: an uncomputable MTP
retest arm, an uncomputable ATR arm, a refusal by the ledger writer, and an
exception. Each now increments its own `residue:*` counter at the point it
returns, and the probe reconciles the named sum against `seen − stamped −
skipped` — one count is an assertion, two are a detector.

**A counter was named wrong on the first cut and the test hid it.** `store_reject`
was wrong: `stamp_candidate` never reads its store's return, so `rec is None`
means that writer's own degenerate-geometry guard or an exception it already
recorded. The test that "proved" it handed in a stub whose `add` returned None —
`stamp_candidate` calls `stamp`, so the stub raised `AttributeError`, was
swallowed, and **wrote a fabricated entry into `fail_open`**, the counter whose
whole job is making a real failure stand out. Renamed `stamp_refused`; the test
now drives the real writer's real refusal path and leaves `fail_open` empty.
`CLAUDE.md` already carried both halves of this — *never hand-write a
collaborator's return shape* and *a non-failure must never reach `fail_open`*.

The `tuned_variants` test fixture also hand-wrote the counter dict and had
already drifted; it now zeroes from the module's own key set.

### Reported, not acted on — these need data or sign-off

- **`mean_revert_emission`**: 849 detections since one emission, blocked
  candidates measuring **+0.55R over n=3361**. Real and expensive-looking, but
  that is a *counterfactual* (~0.38R optimistic by this repo's own measurement)
  and loosening a live gate on MEAN_REVERT is money-path, owner-sign-off.
- **`edge_reconciliation`**: `MOVER_AVWAP_SCALP` realized − counterfactual =
  **+0.38R** against a 0.3 bound. Note the **sign**: realized is *better* than
  the counterfactual, the opposite of the documented optimism bias — so this is
  more likely the cost constants or the counterfactual model than the path.
- **`cohort_edge_gate`**: all 27 cohorts still `macro_dir=DECLINE`. The probe is
  **working as designed** — it exists so this is never discovered from a P&L
  chart. Unchanged since 2026-07-30; a BTC macro flip still disarms every cohort
  at once.

### Verification

Full suite **7798 passed, 58 skipped**. Ruff clean; mypy unchanged (8 errors on
`entry_features.py` before and after — line shifts only). The scoping fix was
**verified by reverting it**: against the old code the new test fails with
exactly the alert's shape, `{'extension_pct': 20, 'level_dist_r': 20}` on 20
MEAN_REVERT rows.

### Open

- The `level_dist_r` cause histogram lands on the next audit cycle. If it reads
  `no_levels`, the LevelBook refresh is the target; if `none_ahead`, the feature
  works and the *paging threshold* is what wants revisiting.
- Ops `/signals/entry-features` renders an em-dash for `level_dist_r` with no
  cause beside it. The reason is now on the row and could be surfaced there —
  not built this session, since the ask was the engine alert.

---

## 🟢 SESSION 106 2026-08-02 — the feed's biggest gate had no counter

Owner: *"take the cohort_edge feed issue"* (~16 delivered signals/day). The
diagnosis moved the target.

### cohort_edge is not the culprit — and nothing could have told us

- **The funnel's "Emitted" column counts ENQUEUES.**
  `_increment_path_funnel("emitted", …)` fires right after `_enqueue_signal`
  succeeds (`scanner:8940`, `:8959`). `CLAUDE.md` already said *"emitted" means
  DELIVERED, and only the router knows that* — the artifact had been reading the
  wrong stage the whole time.
- **`SignalRouter._process` had zero instrumentation.** Twelve rejection
  conditions, every one a bare `return` after a `log.info`. `grep -c` for any
  counter in that file returned 0, and no truth-report section parsed those
  lines. Twelve live gates with no row in the Suppression Quality Audit, on the
  one hop that decides what a subscriber receives.
- **cohort_edge has no audit row at all**, despite 5 armed cohorts (4 of them
  every MVRTP side×regime combination). All 27 cohorts still end `/DECLINE` —
  the least-varying-component cliff from 2026-07-30, unchanged. `macro_direction()`
  needs a `closes` argument, so the quick check failed; **still unanswered
  whether the gate is armed under today's macro**.
- **`dispatch_staleness_v2`'s DROP verdict is not trustworthy.** −0.28R with
  166.4R missed, the loudest signal in the report — but its suppression stamp
  anchors `entry=sig.entry`, the very price the gate declared stale. Scored on a
  fill nobody could have got, biased against exactly this gate.
- The 8,498 MVRTP confidence-passes → 309 enqueues is **not** loss: a 27×
  collapse matching the 20–48 re-detections per move measured in Session 104.

### What shipped

Router drop telemetry (`src/signal_router.py`): a `_drop(signal, reason)` helper
replacing all 16 bare returns across 12 reasons. Each one now increments a
monotonic counter keyed `reason` and `reason:setup_class`, and stamps the
suppression audit as `router:<reason>` — so every router gate gets a WOULD_WIN%,
an EV and a KEEP/TUNE/DROP verdict beside every other gate. `delivery_stats()`
publishes processed / delivered / dropped / delivery_rate; `_log_delivery_stats()`
writes one `ROUTER_DELIVERY` line a minute on the existing cleanup tick (silent
while idle). Measurement-only — nothing changes about what emits.

### Open

1. **Read the first window**: `docker logs 360scalp-v2-engine | grep ROUTER_DELIVERY | tail -5`
   and the new `router:*` rows in the Suppression Quality Audit. That is the
   answer to where the feed goes, with an EV attached.
2. The funnel's `emitted` stage should be renamed `enqueued` — not done, it
   would break the truth-report parser and wants its own change.
3. Re-anchor the staleness suppression stamp to dispatch-time price, or mark
   those rows so the audit flags rather than silently mis-scores them.
4. Is cohort_edge armed under today's macro? Unanswered.

---

## 🟢 SESSION 105 2026-08-02 — the SMC gate was fine, and the live gate filters nothing

Owner ran the checks the previous session asked for. Both answers were the
opposite of what had been written down.

### The SMC gate is doing its job

Once `zone_distance_atr` could compute (Session 104's fix), the first 89 TPE
signals measured **median 0.13 ATR, p90 0.42, max 0.52** — 88 of 89 inside half
an ATR, no tail. The "a zone 40 ATR away satisfies it" claim, which was in a PR
body, two module docstrings, `CLAUDE.md` and an ops page, describes **no
candidate that exists**. Cause: `detect_fvg` uses `lookback=10`, so it only
finds gaps in the last ~12 bars, and a gap that recent is still near price. The
narrow lookback is what makes the loose gate behave like the strict one.

`entry_quality.tpe_smc_zone` is **retired** — no threshold discriminates on that
distribution, and a rule that cannot discriminate is noise on a panel rather
than a shadow rule awaiting evidence. The *feature* stays stamped: it is what
settled this, and what would catch the gate drifting if `lookback` changes.

The retraction is written into `CLAUDE.md` beside the original rule, which still
stands in its checking form: a gate whose comment and code disagree is worth
**checking**, not thereby a gate that does nothing. Two lessons attached —
reading code produces a hypothesis, never a measurement; and a broken
measurement is worse than none while it looks like agreement, because this
feature returned `None` on every row for its whole life and nothing could
challenge the claim.

### The live gate filters nothing

`profile_reject`: **900 candidates judged, 900 passed, 0 rejected, 0 unknown**,
feature present on 900/900. Not blind — it reads its input on every row and
changes no outcome, because the profile-free `_pass_basic_filters` call upstream
already rejects everything the tier-adjusted one would. Kept live (proven safe
rather than argued safe; starts filtering by itself if a tier multiplier ever
bites), but **the entry-quality gate is currently a no-op on the money path** and
that is now stated in code, tests and the panel rather than implied by an empty
table.

### Cleared, and the real problem

Delivered signals ran **1–2/hour flat across the whole 24h**, with the gate going
live at 10:28 UTC and no step change — 15 created before, 1 after in the partial
hour. The thin feed (~16/day) is **not** caused by anything in this lane.

**That is the open item worth a session**: ~16 delivered signals/day against a
scanner producing ~60 distinct setups per 110 minutes. `CLAUDE.md` already
records the feed falling ~48/day → ~9/day in July with `cohort_edge`'s absorbing
state implicated.

### Also still open

`entry_feature_inputs` should have paged on `smc_zone_dist_atr` missing from
57/57 TPE rows — was it firing and unnoticed, or not firing? Unanswered.

---

## 🟢 SESSION 104 2026-08-02 — `smc_zone_dist_atr` never worked, and orderblocks do not exist

Owner asked for a VPS command proving FVGs and orderblocks are really read from
Binance. The commands answered a bigger question than they were built for.

### What the VPS said

- **`orderblocks` has no writer anywhere in the engine.** Truth report:
  `orderblocks: presence[absent=474467] sources[not_implemented=474467]` — 474k
  observations, 100% empty. `SMCResult.orderblocks` is declared, defaulted to
  `[]`, serialised, never assigned. So TPE's `bool(fvgs) or bool(orderblocks)`
  has always been `bool(fvgs)`.
- **FVGs are genuinely computed from Binance.** Live klines through the engine's
  own `detect_fvg`: BTC 5m 2 zones, ETH 5m 3, SOL 5m 0. But the default
  `lookback=10` scans only the last ~12 bars — the same series at `lookback=100`
  holds 13–19 zones. The engine sees a narrow rolling window, by design or by
  accident; **not changed**, because it changes what a live gate sees.
- **`smc_zone_dist_atr`: 0 of 57 TPE rows.** Not a market fact — a broken reader.

### The bug

`zone_distance_atr` guesses zone edges from `top`/`bottom`/`high`/`low`/`price`.
`smc.FVGZone` carries `gap_high`/`gap_low` and none of those five, so every zone
yielded no edges, was skipped, and the function returned `None` on a full book.
Uncomputable since #851. Its tests passed because they hand-wrote
`{"top": 105.0, "bottom": 95.0}` — a shape nothing produces. `CLAUDE.md` already
carried the rule that forbids exactly this.

Fixed; the regression test drives `detect_fvg` and passes its real output in, and
fails against the old code.

### Two things the bug exposed

- **`tpe_smc_zone` was inert by construction** — always `unknown`, always
  abstaining. Harmless to the money path (it is shadow), but it could never have
  earned promotion. The probe judged only *enforcing* rules blind; total
  blindness is now a fault in either mode (0.8 enforcing / 1.0 shadow), engine
  and ops panel both.
- **`entry_feature_inputs` should have been paging** — `smc_zone_dist_atr` is in
  `missing` on 57/57 TPE rows, which is its failure condition. **Open question
  for next session: was it firing and unnoticed, or not firing?** If the latter,
  the watchdog has its own defect and that matters more than this one.

### Still open from Session 103

`profile_reject`'s live rejection volume — first read of the ops panel's
Suppressed / Would-have-removed / Unknown columns.

---

## 🟢 SESSION 103 2026-08-02 — the entry-feature lane gets a consumer

Owner: *"make entry features live, not only measurement"*, against #849 and #851.

### What shipped

`src/entry_quality.py` — a real gate in the scanner's post-scoring chain that can
suppress a candidate on its stamped entry features. Wired end-to-end: no scaffold,
no stored-but-unconsumed setting. It runs **after the confidence floor**, so a
rejection is always a candidate that would otherwise have emitted — the counter
means "signals this gate cost us", and the shadow population is the emitting book.

### Which rules are live, and why only one

The lane's own PR bodies say a filter cannot be chosen from its window: 19 cells
on 46 closed signals, exactly one CI excluding zero and *in the backwards
direction*, ~62% familywise. That has not changed. **Building the gate and
choosing its rules are separable, and only the second needs evidence.**

| Rule | Mode | Why |
|---|---|---|
| `profile_reject` | **enforcing** | A repair. `_pass_basic_filters` computes pair-tier volume/spread thresholds and 19 of 20 call sites discard them — including the path that is ~94% of the delivered book. Enforcing invents no number. |
| `tpe_smc_zone` | shadow | The repair is known (the gate's comment says "in the pullback zone"; the code says `bool(fvgs)`), the threshold is not. **Retired next session — measured max 0.52 ATR, nothing to discriminate.** |

### Three safety properties, each a rule from `CLAUDE.md` arriving from the other side

- **The gate starves its own evidence** unless every live rejection is stamped —
  a suppressed candidate never delivers, so it can never join the closed-signal
  record. `_stamp_suppressed(sig, "entry_quality:<rule>")` + its own
  `REASON_ENTRY_QUALITY`, so the suppression audit ranks it beside every other
  gate rather than folding it into one.
- **Unknown abstains** (fail-open) — a fail-closed rule here would kill the feed
  the moment an order book went dark, which is indistinguishable from a quiet
  market. Cost: an inert rule reads like a working one, so `unknown_frac` is a
  column and an enforcing rule blind on ≥80% of its own population pages
  `entry_quality_effective`.
- **A rolling blast-radius cap** (`ENTRY_QUALITY_MAX_REJECT_FRAC`, 0.35 over 200
  decisions) — no rule's rejection *volume* has ever been measured, the ledger is
  on the VPS, and the first live window is the first look. Over the cap the gate
  degrades to shadow. Order-dependent by construction, so counted and rendered as
  its own state.

### Control and reading

Every knob is a runtime tunable, **generated from the rule registry** — adding a
`Rule` surfaces its ops controls with no second edit. Ops `/signals/entry-features`
gains a **Live entry-quality rules** panel (ops #122) reading the `eq_*`
annotations off the ledger rows, and its old "Nothing on this page is applied"
copy is gone — that sentence became false the moment this shipped.

### Open

Neither rule's live behaviour has been observed yet. **First thing to read next
session**: the ops panel's Suppressed / Would-have-removed / Unknown columns and
whether the cap ever suspended. If `profile_reject` is rejecting a large share,
that is a finding about the mover admission path, not a reason to switch it off
without looking.

---

## 🟢 SESSION 102 2026-08-01 — the store had a second writer, SAR gets clean bars, and one recommendation was retracted

Owner brought the 11:00 exports (dark feed, both SAR arm ledgers) and asked to
fix the SAR data so the mechanism can be measured accurately.

### The retraction, first

Session 101 shipped *"floor TPE's TP1 — the single biggest lever"* into a merged
PR body, a module docstring, `CLAUDE.md` and an ops page. **It is wrong.** The
observation was right (median designed R:R 0.79, TP1 inside the stop, nothing
floors tp1 while the ladder floors tp2/tp3); the recommendation was backwards.

Simulated on the same window, both bounds:

On the 11:00 window (55 decided rows), both bounds:

| TP1 floored at | Win rate | Result per decided trade |
|---|---|---|
| left as-is | 47% | −0.081R |
| 1.0R | 25% | −0.186R … −0.404R |
| 1.5R | 18% | −0.245R … −0.536R |
| 2.0R | 5% | −0.436R … −0.836R |

It reproduces on the 08:26 window (48 rows, −0.135R → −0.252R…−0.460R at a 1.0R
floor), so the direction is not one export's artefact. The winners barely clear
their current targets — TPE's hit at a median 0.59R against a 0.89R peak, only
27% of decided trades ever moved 1R in our favour, median excursion **0.53R**.
The low target is what harvests a move that small.
Corrected in all four places. `CLAUDE.md` gained **§ Re-check Before You Test,
Not After** as the practice that would have caught it — one query against a CSV
already open in the session.

### The store had a second writer

`timestamps_unsorted` kept firing after Session 101's merge dedupe because a
WebSocket bar never passes through `_merge_candles`. `update_candle` appended
blindly, and `refresh_timeframe` REPLACING a bucket while the socket is still
delivering puts a bar behind the newest one — routine for promoted movers, which
is exactly where the SAR arms live. Same-timestamp bars now update in place,
older ones are dropped and counted, untimestamped ones still append.

### SAR refuses rather than degrades

The one consumer where "walk it and mark the row" is wrong. SAR is
path-dependent: one duplicate advances the AF an extra step and every level after
it is wrong with no recovery, and `times.index(last_seen)` finds the *first*
occurrence so an out-of-order bar makes the walk resume behind itself. `_series`
now checks the whole window (one interior duplicate leaves both endpoints
looking fine) and a refusal is counted by cause instead of reporting as
`no_series`.

### MAE — the field that unblocks the stop question

No lane recorded adverse excursion, so *"would a tighter stop have helped"* was
unanswerable: the optimistic and pessimistic bounds differed by more than the
whole edge under discussion, and the gap is exactly *did the winners survive it*.
Now stamped on the dark walk and the SAR arm, rendered and exported on both
pages. **Accrues from deploy forward** — historical rows cannot get one.

### SAR verdict, on the owner's read

Owner: *"SAR giving less losses also less profits too"* — correct. Losses average
**−0.689R against a full −1.00R**; net **+0.143R** on 82 arms. But CI
**[−0.09, +0.39]** spans zero, and the subgroup test kills it: where SAR
**governed from entry** (60 arms) it is **−0.008R**; all the edge sits in the 22
where SAR *opposed* at entry and the original stop ran until handover. Same shape
as FAILED_AUCTION_RECLAIM. **Keep measuring, do not adopt.**

### Open

1. **`bar_rolled_out_of_window`** — 10 of the 15 unmeasurable arms, and *not*
   addressed here. Cause is the arm's anchor bar vanishing when
   `refresh_timeframe` replaces a bucket. Next thing to fix if it stays at ~10
   per window.
2. **Three levers**: cut losses (SAR measured, not adopted) · raise win rate
   (entry features accumulating, needs a week) · tighten stops (**now measurable**
   — needs a fresh MAE window).
3. Watch that `timestamps_unsorted` stops appearing on rows created after this
   deploy. If it does not, there is a third writer.

---

## 🟢 SESSION 101 2026-08-01 — the dark feed's verdict was a geometry problem, and every path's entry is a boolean

Owner brought the 65-row dark-feed window (2026-07-31 08:25 → 08-01 08:10 UTC) and
then: *"we need to concentrate on entry, on which bases entry is confirming
especially on Trend pullback EMA and mover AVWAP"*.

### What the window says

56 scored rows, **−0.158R, bootstrap 95% CI [−0.40, +0.09]**. 48 decided, 42% win,
−0.185R. Nothing in it clears zero.

`FAILED_AUCTION_RECLAIM` reads +0.508R and its three decided rows are
**+1.54 / +2.00 / −1.00** — bit-for-bit the population `CLAUDE.md` already
records under *two winners are not a promotion*. The lane has added **zero** new
decided FAR evidence since; the two that closed were expiries. Removing the two
winners takes `execution:overextended` from +0.115R to +0.021R, and removing FAR
entirely takes it to −0.062R. Still not a promotion.

**The real finding is payoff geometry, not gates.**

| setup | n dec | designed R:R | breakeven win% | actual |
|---|---|---|---|---|
| `TREND_PULLBACK_EMA` | 17 | **0.79** | 54% | 35% |
| `MOVER_AVWAP_SCALP` | 19 | 1.05 | 52% | 42% |
| `MEAN_REVERT` | 5 | 1.24 | 50% | 40% |

TPE parks TP1 **nearer than its stop**: TP1 is the nearest 5m swing extreme,
capped by ATR percentile, and `_enforce_tp_ladder_monotonicity` floors tp2 at
2.0R and tp3 at 4.0R while **nothing floors tp1**. Median MFE on an SL row is 22%
of the distance to TP1 and 16 of 28 never reached a quarter of it — these are not
trades that were right and gave it back. Confidence has corr −0.019 with R.

### Fixes shipped

- **Duplicate bars on merge.** `_merge_candles` concatenated blindly while
  `_estimate_gap_candles` over-fetches by design, so every gap fill re-appended
  bars the bucket held. That double-weights fixed-bar-count indicators and makes
  `open_time` non-monotonic — and `slice_window` uses `np.searchsorted`, which is
  *undefined* on an unsorted array, while the resulting walk stamps `last_bar_ms`
  and reads `current`. 7 of the 9 open dark rows carried ~21 more array entries
  than elapsed minutes. Overlap now dropped and counted; the consumer keeps its
  own guard.
- **Expiries that never walked their window.** ROBOUSDT expired on 309 bars of a
  362-minute window, ARBUSDT on 329 of 365 — 89 unexamined minutes reported as
  "the setup did nothing" at 0R. Untouched rows stamp `window_coverage` and
  retire `INSUFFICIENT` (terminal, unscored) below the floor. Ops counts the two
  causes apart.

### Entry features, per path

Generalised `src/entry_features.py` from MVRTP to every dark-feed path.
**The first cut copied MVRTP's feature list onto all of them and the owner caught
it** — that list was chosen for MVRTP's blindness and measures nothing elsewhere.
Now a small core (geometry, trigger-bar shape) plus per-path extras:

| Path | What it confirms on | What it cannot see |
|---|---|---|
| `TREND_PULLBACK_EMA` | 1H EMA21/50, then six **booleans** on 5m | the magnitude of any of them |
| `MOVER_AVWAP_SCALP` | AVWAP + slope + volume | where in the move it is |

TPE stamps 1H trend separation, retrace of the impulse leg, RSI at entry, the
size of the `prev_high` break, and which of its **two direction mechanisms** ran
(the 1H path and the legacy 5m-regime fallback are different strategies sharing
one `setup_class`, and nothing had ever distinguished them). MVAVW stamps anchor
age, leg move %, prior returns to the anchor, slope magnitude and the exact
volume ratio `vol_ok` thresholds on.

`tp1_r_multiple` is stamped on every path and is the number to read first — it
bounds what any entry filter can achieve.

**Two defects found while reading:**
- `cvd_slope` / `book_imbalance` were stored raw and split "higher is better",
  scoring every SHORT backwards. Now signed toward the trade.
- TPE's SMC gate says *"at least one FVG or orderblock in the pullback zone"* and
  is `bool(fvgs) or bool(orderblocks)` — a global existence check a zone 40 ATR
  away satisfies. Stamped (`smc_zone_dist_atr`), **not** fixed: it rejects, so
  narrowing it changes what emits. A test pins the live behaviour.

### Open — owner decisions

1. ~~**TPE's TP1 floor** — "the single biggest lever".~~ **Retracted the same
   day, see Session 102.** The observation was right and the recommendation was
   backwards: raising the target makes the book worse under both bounds.
2. **FAR needs rows, not a promotion** — 3 decided rows in 24h means a CI that
   excludes zero is weeks away, which is itself a question about where the dark
   lane's row budget points.
3. Ops `/signals/entry-features` now has a per-path selector; the engine ships
   the feature registry in the ledger's `spec` so ops holds no mirror.

---

## 🟢 SESSION 100 2026-08-01 — MVRTP takes its entry off three SMAs, and now we can see what else was on the table

Owner, after rejecting an exit-side fix: *"some days something will be benefits,
that's not the correct solution, taking entry is matter, how we are taking entry
based on only EMA or what, what if we add some more data to that"* — plus *"we
need to know the difference as of now vs later"*.

### What MVRTP actually reads (`src/channels/scalp.py:2997`)

| Decision | Input |
|---|---|
| Direction | `SMA25 > SMA99` on 15m — two simple MAs, the whole thesis |
| Mover gate | `max(15m SMA7↔SMA99 sep, 1h EMA21/50 fan)` — a magnitude |
| Trigger | prev bar tagged SMA7 within a band, this close > SMA7 and > prev close |
| Stop | `min(SMA25, prev_low) − ATR×buffer`; TPs fixed at 1.0/1.6/2.5× |

Not even EMA — SMAs. `vols` **is** read in the function and handed only to
`_mover_consol_break`; `fast_pullback` and `deep_pullback`, which carry nearly
all the volume, never look at it. Meanwhile `smc_data` arrives at that call with
`cvd`/`cvd_15m`, `order_book`, `funding_rate`, `liquidation_clusters`,
`orderblocks`, `sweeps`, `mss`, `fvg`, `level_book_levels`, `recent_ticks` — and
MVRTP touches two keys from it, both only for display stamps.

**Live defect found while reading it:** MVRTP calls `_pass_basic_filters` without
`profile`. One of 20 call sites passes it, and the path that is 94% of the book
is not that one — so the pair-tier liquidity/spread adjustment is inert for
almost everything we ship. Stamped as `profile_would_reject`, **not** fixed:
changing it changes what emits.

### What shipped

`src/entry_features.py` — stamps pullback volume ratio, CVD slope, pullback depth
in ATR, extension from SMA99, distance to the nearest opposing level in R, book
imbalance, funding and the profile shadow, at the moment each MVRTP signal is
created. Measurement flag **ON**, nothing applied. Ops `/signals/entry-features`
renders "now vs later": the book as it shipped beside the book each candidate
rule would produce, on the same rows.

**No resolver.** Outcomes join from `signal_performance.json` on `signal_id`.
Every lane that grew its own resolution machinery cost a session — #839
INSUFFICIENT rows, #835 stalled arms, #836 stale anchors, #846 over-walks, #842
undatable windows, all in the *scoring* half, none in the *stamping* half. This
one inherits `trade_monitor`'s correctness (including #848's denominator).

### Why no filter shipped

46 closed MVRTP signals, 19 tested cells, ~62% familywise chance of a spurious
95% hit — and exactly one cell cleared, **in the backwards direction** (SAR
*disagreeing* at entry reading better than agreeing). By this repo's own
two-winners rule that is noise. On the corrected denominator MVRTP is already
**+0.253%/trade gross** (+11.62% over the window); the R subset reads +0.192R but
is favourably selected, so the gross is the honest number.

### Caught the same day (engine #850, ops #118)

Owner: *"check entry_regime is stamped on MVRTP"*. It was not. The stamp read
`sig.entry_regime` inside the evaluator; the scanner writes that attribute in
`_populate_signal_context`, which runs **after** the evaluator returns. Every row
would have carried `""` and the per-regime split would have been one nameless
bucket — no crash, no empty panel, just a page describing nothing.

The evaluator had `regime` as a parameter the whole time. Now passed explicitly,
pinned by a test that fails against the old read, and ops prefers the
closed-signal record's finalised value with the stamp as fallback (disagreement =
the scanner reclassified between evaluation and dispatch, which is information).

### Open

- Wait for a population that can decide, then read `/signals/entry-features`.
- The `profile` omission is stamped, not fixed — dark-first + sign-off.
- Exit-side ideas remain closed: Session 34 measured pre-TP partials + invalidation
  at −25.79% vs −6.65% for TP1-full on **494** signals. My +3.10R partial-take
  sizing was a 46-row counterfactual against that; the owner's study stands.

---

## 🟢 SESSION 99 2026-08-01 — the track record divided by a stop that had already moved

Owner supplied four exports (live feed, SAR live arms open + closed, dark feed)
covering 2026-07-29→08-01. Reading them found a denominator bug, killed a
promotion, and split the two feeds' failure modes cleanly apart.

### What shipped

**Engine** — `SignalRecord.sl_distance_pct_at_entry`, stamped by both terminal
paths (`trade_monitor._record_outcome` and the `main` expiry path) from
`Signal.original_sl_distance` via the new `performance_tracker.entry_sl_distance_pct`.

`trade_monitor` mutates `sig.stop_loss` **in place** — BE shift, TP1 park, trail —
so the `stop_loss` reaching the record is the stop as of the *exit*, and ops
divided by it. A trade BE-shifted and then stopped out for −0.1% therefore scored
exactly **−1.00R**, identical to one that gave back its whole designed risk. Nine
of 28 SL_HITs in the window were that row. The closed book read **−0.088R against
a true +0.160R** — a sign flip on the headline of the page whose own docstring
calls it "the number a subscription decision would rest on".

The engine already knew the right denominator in two places
(`snapshot._original_stop_loss` reconstructs it; the Layer-C writer divides by it
for `risk_pct`). It simply never travelled onto the artifact the owner reads —
the `entry_regime` failure class (#817) exactly: **a field one repo reads and no
repo writes fails silently and looks full.** Pinned with a producing-side test,
and the helper refuses rather than falling back to `stop_loss`, because that
fallback returns the wrong number for precisely the rows that have the bug.

**Ops** — `record_r` divides by the engine stamp; `unscored_reason` splits
`awaiting_engine_stamp` (pre-deploy, ages out on its own) from `no_geometry`
(current engine, still unstamped — a producer fault that does not age out), and
the page names both. Pre-fix records are **not** backfilled: their stop has
already been moved, so there is nothing honest to divide by.

### What did NOT ship, and why

Owner asked to promote `FAILED_AUCTION_RECLAIM` from the dark lane to the live
feed on the strength of its dark numbers. Declined, with the numbers:

- FAR is **already a live evaluator** — `FAR-1A5692AF` was delivered in this very
  window and hit SL at −2.77%. "Move it to live" is not available; what was
  actually being proposed is loosening a *gate*.
- FAR's dark record is **3 resolved rows**: +1.54R, +2.00R, −1.00R. Bootstrap 95%
  CI on that mean is **[−1.00, +2.00]**; 26% of resamples are ≤ 0.
- Both winners sit behind `execution:overextended`. Strip FAR from that gate and
  it goes **+0.146R → −0.149R** — the gate's positive read *is* the two FAR
  winners, so using the gate to justify FAR is circular.
- That gate carries 11 other resolved rows, 9 of them `MOVER_AVWAP_SCALP` at
  −0.146R. Loosening it ships those too.
- FAR's +0.846 beats a random 3-row draw from the lane 4.2% of the time — but it
  is the best of 6 setups tested, so familywise that is ~22%. Not a finding.

The correct move is more evidence, not promotion. **Open: give the dark lane a
per-setup row budget** so the rare paths accumulate n instead of being crowded
out by `TREND_PULLBACK_EMA` (20) and `MOVER_AVWAP_SCALP` (16). FAR produced 5
rows in 20.7h.

### The two feeds fail in opposite places — this is the entry-timing finding

| | dark (gated) lane | delivered book |
|---|---|---|
| stop-outs that never got 0.25R in front | **68%** (median 0.18R) | — |
| closed signals that reached the BE trigger | — | **61%** (30 of 49) |

The delivered book, 49 closed: **16 wins** (+4.63% mean), **14 scratches** that
got in front and finished flat (−0.06% mean), **19 full-risk losses** (−3.40%,
−0.938R). Net +8.65% gross. So the gated paths are failing at the **entry** —
the trigger fires and price goes against from the first bar — while the
delivered path is failing at the **exit**: 29% of the whole book earned a
break-even shift and then gave all of it back.

Bars-to-decision separates them early: a full loss flips SAR at a median **4.5
bars (5m) / 3.5 bars (15m)**; a winner takes **21 / 14**. A losing entry declares
itself almost immediately. (Partly circular — SAR flips fast *because* price
moved against — but the adverse move is demonstrably fast on losers.)

Also standing, from the same read: **confidence is inverted** on the delivered
book — (70,75] +0.156R / 50% win, monotone down to (85,100] −0.605R / 20% win.
n is 4–14 per bucket over 60h, so it is a flag, not a verdict — but it is the
score that routes dispatch.

### Open items

- **SAR live arm: do not activate.** Headline +0.133R over 73 resolved arms is
  carried entirely by (a) the 36 of 87 arms with `anchor_engine_stamped=False`
  (`unverified` by ops' own #109 rule) and (b) the 1000RATS/1000SATS cluster.
  Anchor-verified and non-concentrated is **−0.213R over 23 arms**, 26% win. On
  the clean population the live exit beats it (+0.252R vs +0.133R per arm).
- 16.1% of arms terminate `INSUFFICIENT` (10 `bar_rolled_out_of_window`, 3
  `candle_feed_stalled`, 1 `series_jumped_ahead`) — all rotated-out movers.
- `MVRTP-DE816E32:15m` observed RUNNING at `bars_seen=0` with a 20.05% risk
  denominator on a signal that had already closed SL_HIT at −5.24%.
- Arm entry ≠ signal entry on 9 of 69 matched arms, up to 1.74% (a 31%
  denominator gap on the worst one). Worth pinning as a contract.

---

## 🟢 SESSION 98 2026-07-31 — two owner directives, and a test artifact in the repo (engine #844/#845, ops #114/#115)

### SR_FLIP longs now emit into the dark feed (#844 + ops #114)

Owner: *"enable sr flip longs to here at dark feed"*. The long side has been off
since 2026-06-29 on a measured −21.8% / 19% win, and its only evidence since was
a `[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE` log line — a candidate **count**, which
cannot settle a re-enable. Dark rows give it forward-resolved outcomes.

First *evaluator-internal* disable the lane admits, and that dictated the shape:
`long_disabled` fires before the gate chain, so publishing there would produce
rows the page's own first sentence describes falsely. The candidate is
**carried** instead — evaluator finishes, every gate still applies, diverted at
the one enqueue site. `will_admit` decides the carry; it is **not** permission,
so the mark is re-checked with `is_dark` before returning. Both tests fail with
that guard removed. Lane off ⇒ rejected as before.

### SAR exit arms over the dark feed (#845 + ops #115)

Owner: *"observe this dark feed too with SAR exit mechanism along with regular"*.
Each dark row now carries two outcomes — its own SL/TP1, and a SAR handover from
the same entry.

- **Own ledger** (`dark_sar_arms_v1.json`). `sar_live_arms_v1.json` is the
  adoption evidence and every arm in it reached a subscriber; these reached
  nobody. A consumer pointed at a file it never opens cannot mix them.
- **Health is per lane.** Was module-global — a dark stall would have paged as
  though the delivered-signal arms froze. `dark_sar_arms` is its own probe.
- **The comparison population is the trap.** Only rows decided by *both* count;
  a row that resolved while its arm still runs describes one mechanism, not two.
  Expect the panel to read empty for the first hours — that is designed.

### `.tmp` — a test artifact committed since #839

Surfaced as a merge conflict on every branch. Both ledgers take `path=""` to mean
"in memory" and neither checked it before the atomic write, so `flush` wrote
`.tmp` into pytest's cwd (the repo root) and `git add -A` committed it. The file
was the symptom; `os.replace(".tmp", "")` then raised into **`fail_open`** — a
non-failure filling the counter that exists so real ones stand out, on every test
run for two months. Both flushes now return early; `.tmp` is gitignored.

### Both surfaces confirmed on screen, and the data found a bug (#846)

Owner exported both pages at 15:16 UTC. The dark feed is healthy: 18 rows, 5
open and **all being advanced**, `bars_behind ≈ 0.6`, `no candles` gone, pre-
restart rows correctly reading `unverified · stamp_before_timestamps`. SAR arms
show `running ×2` per row and the comparison panel correctly says nothing has
both verdicts yet.

The **live** SAR arms did not survive the same read. Three arms stamped
`anchor=clean`, `anchor_bars_behind≈0`, `first_step_bars=1`:

| arm | bars_seen | bars of life |
|---|---|---|
| `MVRTP-CF7DEF1F:15m` | 466 | ~17 |
| `MVRTP-1C478092:15m` | 159 | ~5 — **contributed −1.644R** |
| `MVRTP-7EDA88B4:5m` | 63 | ~9 |

#836 asked this question at the anchor and at the *first* advance only, so a
later over-walk was invisible. Cause: a frozen-then-refreshed series —
`refresh_timeframe` replaces a rotated-out mover's bucket, the arm's last bar is
still in the new window, and the walk crosses hours of history in one pass.
Fixed by bounding **every** advance by the clock; refuses as
`series_jumped_ahead`, stamped with `advance_replay_bars` /
`advance_allowed_bars`.

**Do not read the −0.034R mean over 44 scored arms** — at least one over-walked
arm is in it. Needs a fresh window. One reassurance: the 23% INSUFFICIENT
fraction is *not* loss-selected (mean MFE +2.54% unmeasured vs +2.71% scored),
which is #832's check coming out clean for once.

### Open

1. **#832's SAR verdict is owed a re-check** — `_ohlc_15m_detail` refused on the
   same undatable-bars condition #842 fixed, so "8 of 19 unresolved → starved
   refresh budget" may have been that bug wearing another name. Now doubly owed:
   #846 changes what resolves.
2. Elapsed-time candle slice still backs the suppression and invalidation audits.
3. **Ops does not yet render `series_jumped_ahead`** — the engine stamps it and
   `/signals/sar-live` will show it as a plain INSUFFICIENT until the page
   grades on the new stamps. Same "measured but nowhere to look" gap the dark
   lane just closed.
4. The dark feed's CSV export carries no SAR columns; the page does.

---

## 🟢 SESSION 97 2026-07-31 — bar timestamps never survived a restart (engine #842, ops #113)

Owner, from the live dark feed hours after Session 96 deployed: every open row
read `stalled — no candles`, **zero rows being advanced**. One was BCHUSDT, a
core pair whose candles were plainly arriving — so "the symbol rotated out"
could not be the explanation, and the fault was ours.

### The cause was in the snapshot, not the lane

`_save_snapshot_sync` wrote open/high/low/close/volume; `load_snapshot` read
back the same five. `open_time` had been added to the store without being added
to either, so **timestamps did not survive a restart**. `_merge_candles` then
correctly refused to merge the gap-fetch's timestamps onto a bucket with none,
and the whole candle store came back undatable — which Session 96's
`slice_window` refused, wholesale. The Session 96 deploy *was* the restart, so
the lane went blank on its first cycle.

**Not confined to the dark lane.** `_ohlc_15m_detail` refuses on the same
condition. The SAR resolver has been losing windows after every restart for as
long as it has located bars by time — **open item: re-read #832's "starved
refresh budget" conclusion (8 of 19 unresolved, all four winners among them)
against a post-fix window before trusting it.**

### What shipped

| Fix | Where |
|---|---|
| `open_time` saved when index-aligned; legacy npz loads as a NaN column, not an absent key | `historical_data._save_snapshot_sync` / `load_snapshot` |
| `slice_window` degrades to an undated walk instead of blanking; hard refusal kept only for rolled-off history | `dark_emission` |
| `searchsorted` now runs over the finite tail — a NaN prefix made it an unsorted array, which is undefined, not imprecise | `dark_emission` |
| Probe fails when the whole open book is advancing on undatable windows | `dark_emission.resolution_health` |
| An undated row reads `unverified` with its cause named, and is excluded from "still being advanced" | ops `dark_signals_live` |

Two lessons in `CLAUDE.md`: **a field one writer populates and one serializer
drops is invisible at both ends** (#817 one layer down — the round trip is a
contract, pin it against the real serializer), and **refuse the claim, not the
measurement** (an empty page is indistinguishable from a quiet market).

### What the page should show now

`no candles` gone; rows emitted before the restart read
`unverified · stamp_before_timestamps` (their entry bars sit in the restored,
untimestamped history) and resolve normally; rows emitted after it carry a real
age and populate "still being advanced", which read 0 of 3. The NaN prefix rolls
off the 1m ring over ~16h, after which everything is dated. **Not yet confirmed
on screen** — the deploy landed 12:08 UTC.

---

## 🟢 SESSION 96 2026-07-31 — the dark feed could not say what an open row was worth (engine #6709745, ops #4f96329)

Owner, on the dark feed the same day it shipped: *"there is no live prices real
PnL % etc"*. Correct, and it made the page unable to answer the question it was
built for — three open rows, entry prices, dashes under PnL and R. A dark row
resolves up to six hours later, and never at all if its candles stop, so until
then the page showed a list of symbols.

### What shipped

**Ops** — open rows carry a live mark (`/fapi/v1/ticker/price`, one request for
the whole book, TTL-cached, so cost does not scale with open trades), the
unrealized move, unrealized R against the **engine's** stamped `sl_distance_pct`,
and room to each level. An "Open right now" panel publishes two denominators —
every marked open row, and only the rows the engine is still advancing — and
calls neither "the" number. Unrealized never enters the per-path table; marks and
results share the PnL/R columns but can never share a row.

**Engine** — everything the page needs to know whether a row is still true:

| Was | Now |
|---|---|
| `last_bar_ms` written at publish, never updated | stamped every cycle with the bar actually consumed |
| resolver sliced `elapsed // 60` bars off the array end | `slice_window` locates the entry bar by `open_time`, refuses what it cannot place |
| a miss counted only in the cycle tally | `resolve_misses` / `resolve_miss_reason` / `stalled` on the row |
| horizon test behind a successful walk → unwalkable rows OPEN forever | retired as `INSUFFICIENT`, terminal and unscored |
| `flush()` wrote only on change → idle lane read STALE | forced once per resolve cycle |
| no liveness probe at all | `dark_resolution`, keyed on the rows owed a verdict |

### Four old lessons that re-entered through a new lane

Every one of these is already in `CLAUDE.md`; the lane shipped a day earlier and
inherited them anyway, which is worth naming as a pattern rather than five
separate bugs.

1. **A field one repo reads and no repo writes** (#817) — `last_bar_ms` existed
   in the row shape from day one and nothing ever set it.
2. **An array consumed by *when* something happened must carry its own
   timestamps** (#800) — the shared `fetch_ohlc_since` slices by elapsed time,
   which is right only while the series is gap-free and current. The dark lane
   now has its own timestamped fetch; **the suppression audit and the
   invalidation audit still use the elapsed-time one** (see Open).
3. **A fail-open `continue` with no per-row counter** (#815) — `no_candles`
   incremented a tally and left the row indistinguishable from one emitted a
   minute ago.
4. **A heartbeat that only fires on change is not a heartbeat** (#832) — the
   ledger's own flush docstring claimed this was fixed. It was not; nothing
   called it with `force`.

### Open

- **`fetch_ohlc_since` (elapsed-time slice) still backs `suppression_audit` and
  `invalidation_audit`.** Same latent fault, two consumers, both measurement-only.
  Worth converting to `dark_emission.slice_window` — one function, one refusal
  policy — rather than a third copy.
- **The page will read `unverified` on every current open row** until the engine
  redeploys and stamps them. That is the fallback working: a missing stamp is an
  unknown, not a pass.
- **Nothing about the lane's enrolment changed** — `setup_compat` + `execution`
  loosened, `min_confidence` and the context floors live, `MOVER_TREND_PULLBACK`
  excluded, no row reaching a channel, a push, the app feed or an order.

---

## 🟢 SESSION 95 2026-07-31 — the arm that anchored to a 40-hour-old bar (#836)

Owner delivered the first full read of the SAR exit mechanism: the live-arm CSV
(35 arms), the 5m and 15m dark-signal replays (16 signals each), and the
`/signals/sar-live` page. Reading them against each other is what found this.

### The verdict, on the data as it stands

32 resolved arms / 17 signals / **8 symbols** / 24h, 30 of 32 `MOVER_TREND_PULLBACK`,
COTIUSDT + ROBOUSDT alone 56% of the population.

| Cut | R@level | R@confirm | Win |
|---|---|---|---|
| All resolved (n=32) | **+0.248** | +0.214 | 59% |
| 5m (n=17) | +0.251 | +0.246 | 59% |
| 15m (n=15) | +0.245 | +0.177 | 60% |
| SAR governed (n=29) | +0.297 | +0.277 | 62% |
| Original geometry governed (n=3) | −0.227 | −0.395 | 33% |

**Confirm cost is real but small** — mean −0.039pp, i.e. waiting for the bar to close
costs about 4bp against the parked-stop fill. This number had never been measured
anywhere in the system; it is now, and it is not zero.

**t = 1.37 on arms, 0.95 per signal, 0.77 per symbol.** The mechanism is *not*
distinguishable from zero on this window. It is a promising read, not a verdict.

### Two measurement faults the cross-read exposed

1. **The dark-signals `sar_*` columns measure a different mechanism than the live
   arm.** The replay runs SAR from bar one unconditionally; the live arm hands over
   only once SAR comes onside, and until then the original SL/TP1 governs. On the 22
   matched arms where SAR agreed at entry the two agree to −0.10pp. On the 6 where SAR
   **opposed**, the replay reads **+0.73pp optimistic** — and on FAR-1A5692AF:5m it
   printed +1.04% where the live arm took the −3.00% stop. 21% of arms open opposed.
   *The dark CSV's SAR column is not a forecast of adopting this mechanism.*
2. **R is divided by the SL distance the trade was sized for, on arms where SAR
   replaced that stop with a wider one.** The SAR stop was **wider than the original
   SL on 14 of 27** handovers — mean 1.25×, max **2.81×**. Re-divided by the risk
   actually parked, +0.348R becomes **+0.292R**, and the worst arm's −1.90R is really
   −0.71R at 2.7× the risk. Both readings are defensible; publishing only the first
   flatters the mechanism on the upside and exaggerates it on the downside.

### The bug (#836) — an arm can be born a replay

ACHUSDT 15m: `bars_seen: 158` after **10 bars of life**, and `aligned_at_entry`
disagreeing with its own 5m sibling on the same signal. `new_arm` anchors to
`series["open_time"][-1]` — "the newest closed bar the store holds right now" — with
**no check that that bar is current**. The ACHUSDT 15m series was ~40h stale at
creation (a promoted mover: REST re-seed only, no WS klines), so SAR-at-entry was read
off a 40h-old bar and the arm's first advance walked 39.5 hours of history in one pass,
stamping `last_advance_at = now` on every one of them. The row published as a
forward-stepped fill on the one page whose first sentence is *"This is not a replay."*
The still-open PRLUSDT 15m arm on the page had the same shape (104 bars, ~1.7h old).

1 of 32 resolved arms affected — it does not move the verdict above, but it is #800
re-entering through the creation path, and every future promoted mover is exposed.

**Fix:** `observe_signal` computes `bars_behind` on the candidate anchor and **refuses
to open** past `SAR_LIVE_SHADOW_STALL_BARS` (default 3) rather than clamping the anchor
forward to *now* — "now" is not the entry bar either. Refusals are counted and named
(`refused_open` / `stale_anchor`) in `step_health`, reported by the liveness probe but
never paged on: no arm exists, so nothing is owed a verdict. Every arm now stamps
`anchor_bars_behind` where it becomes true, and `first_step_bars` — 1 on a live arm,
larger only if it walked history — as the detector that reports on the guard.

### A third caveat, from the Session-94 handoff's §4.1 trap: check the denominator

The handoff's rule — *"check the denominator before computing R"* — applies to this
window, and the answer is partly reassuring and partly not.

**Reassuring:** the SAR arm does **not** read `sl_distance_pct_at_entry`, the field
§4.1 shows is unusable (missing on 152 of 378, missingness outcome-correlated).
`new_arm` computes `sl_distance_pct` from the row's own `entry` and `stop_loss` at
creation, both of which are on the row — self-consistent, verifiable from the CSV,
and taken from the **shipped** stop rather than the evaluator's pre-noise-floor one.
`sar_live_shadow` already does what §4.1 asks the rest of the system for: one value,
recorded once, at the moment the shipped stop is known.

**Not reassuring:** **15 of 32 resolved arms (47%) divide by exactly 3.00%** — the
`NOISE_FLOOR_MAX_SL_PCT` cap. That is a real stop that really shipped, so the R is
honest; but for half the population the denominator is a **constant**, not the
evaluator's geometry, and the two halves do not agree:

| Denominator | n | R@level | Win | Raw pnl% |
|---|---:|---:|---:|---:|
| Capped at 3.00% | 15 | **+0.386** | 53% | +1.157 |
| Evaluator geometry | 17 | **+0.127** | 65% | +0.141 |

So +0.248R is a blend of two populations whose denominators mean different things,
and it moves with the cap mix. Checked and **not** supported: the tempting story that
SAR wins by widening a stop the cap had left too tight — SAR's stop was wider on 6 of
10 capped arms against 8 of 17 uncapped, which at this n is nothing.

### Open

- **Do not adopt on this window.** 8 symbols is not a population; wait for one that
  spans regimes and setups beyond `MOVER_TREND_PULLBACK` — and report the capped share
  beside the headline when it is re-read.
- Ops `/signals/sar-live` surfaces the anchor grading and both denominators (ops #109,
  merged): every arm graded `stepped` / `replayed` / `suspect` / `unverified` — replayed
  and suspect excluded from every R, counted and named — and an `R @risk` column beside
  the SL-denominated one. A missing stamp is `unverified`, not a pass, and the panel
  renders whether or not anything failed.
- **The page will read mostly `suspect` / `unverified` at first.** Every arm now in the
  ledger predates the stamps. That is the fallback working, not a regression; the
  `engine_stamped` count climbs as new arms open under #836.
- **Not yet surfaced: the capped-denominator share.** `/signals/sar-live` splits on
  *SAR stop vs designed SL* but not on *designed SL vs the noise-floor cap*, so the
  table above cannot be read off the page. Small addition, worth making before the
  next adoption read.

### Carried from the Session-94 handoff — owner-directed and **still not started**

Three sessions have now been spent on the SAR measurement plumbing (#832/#833 →
#835 → #836) and the two items the owner actually directed are untouched. Naming
that explicitly so it stops being invisible:

- **ITEM 1 — `MEAN_REVERT`.** 4.09% detection, **zero** delivered in 28 days, and the
  engine holds two numbers for it that **disagree in sign**: `MEAN_REVERT` reads 80% /
  +0.58R over n=3085 while `SHADOW_MEAN_REVERT` reads 40% / −0.01R over n=3414 — and
  `context_emission_policy._CONTROL_ARM` wires the **live gate** to the second. First
  task is not the unlock, it is establishing whether the two arms measure the same
  setup at all (`_CONTROL_ARM` maps `RANGE_FADE` the same way). Owner-sign-off,
  dark-first.
- **ITEM 3 — per-path verdict on the near-dead detectors.** `WHALE_MOMENTUM` 0 of
  118,642 (check whether it is starved of *tick input* before touching a threshold);
  `POST_DISPLACEMENT_CONTINUATION` 53% `regime_blocked` with the best positive cell in
  the matrix (n=67, 90%, +0.75R). Stamp-and-shadow first; do not add new paths.
- **§4.1 `sl_distance_pct_at_entry`** remains unusable system-wide — the SAR arm sidesteps
  it, `/track-record` does not.
- **§4.2 `pair_admission` still has no ops surface.** Directly relevant here: this
  window is 30 of 32 `MOVER_TREND_PULLBACK` and nothing on any page says which
  admission path those pairs came in through.
- Also unverified from #834: whether `cohort_edge` has earned a row in the Suppression
  Quality Audit yet, and whether delivered/day is recovering as cohorts age out.

---

## 🟢 SESSION 94 2026-07-30 — the live arm was not live (#835, ops #108)

Owner, hours after #832/#833 deployed, on the KORUUSDT SHORT arms: *"see that koru has
close when SAR flip but not closed why … we are treating SAR live as live signals but
its reactions is not."* Correct on both counts, and the arm had two independent reasons
to be frozen.

### The evidence, from the owner's two CSV exports

| Arm | Opened | Bars seen at 10:30 UTC | Parked stop | Price | State |
|---|---|---|---|---|---|
| KORUUSDT 5m | 08:11:30 | **0** | 11.79 | 12.47 | RUNNING, stop crossed by 5.45% |
| KORUUSDT 15m | 08:11:30 | **0** | 12.3337 | 12.47 | RUNNING, stop crossed by 1.09% |
| SLXUSDT 15m | 07:48:47 | **1** (in 2h42m) | 0.0875968 | 0.08709 | RUNNING |

Both KORU arms still carried `sar_up: False` — the direction read at entry — while the
app's chart showed SAR flipped up on both timeframes. The arms had not recomputed
anything in 2h19m. The ops page read **"LIVE — 3 arms running, stepped inside the
monitor loop"**, and the liveness probe read *"2 arms stepped, no candle misses"*.

### Two causes, and they compound

1. **Stepping rode the live signal list.** `observe_signal` was called once per
   **active** signal per tick, so when `trade_monitor` closed the signal the router
   popped it from `active_signals` and nothing touched the arm again — permanently
   RUNNING, never resolved. The arm's premise is that it exits on *its own* SAR flip,
   which is normally **later** than the signal's SL, so tying its life to the signal's
   truncated the population at the live exit and then abandoned it.
2. **A no-op and a dead feed were the same code path.** `step_arm` iterates bars newer
   than the last one it consumed. Between bar closes there are none — healthy. For a
   surge-promoted symbol that rotated back out of the scan universe there are none
   *ever* (the Session 44/45/46 frozen-candle class, already mitigated for **price** by
   the mark-feed fallback but never for **candles**). Identical no-op, and
   `record_step(symbol, True)` called it a healthy step because a series came back.

### What shipped

| Repo | Change |
|---|---|
| **360-v2 #835** | `sar_live_shadow.sweep()` — advances every open arm from the **ledger**, not the signal list; per-arm staleness (`bars_behind`, `stalled`, `last_advance_at`); stalled arms retire `INSUFFICIENT / candle_feed_stalled` past 1h; a 48h horizon on arms that never flip; the liveness probe now separates `stalled` from `no_series` |
| **ops #108** | `/signals/sar-live` grades liveness on the **arms**, not the file — per-row *Last advance*, `stalled` / `no candles` / `crossed` badges, ARMS STALLED / PARTLY STALLED states, freshness columns in the CSV |

`scripts/gen_ops_sar_live_fixture.py` generates ops' freshness fixture from this
engine, so the consumer's test data is engine output rather than a hand-typed shape.

### Rules earned

- **A measurement that rides another subsystem's loop inherits that subsystem's
  lifetime.** The monitor loop sees a signal until it closes; the arm needed to be
  seen until *it* closes. Key the sweep on the population owed a verdict — which is
  what #815 already said, and the probe's own docstring already claimed.
- **"Nothing to do" and "nothing works" are the same no-op unless something reads the
  clock.** A loop over "bars newer than the last one I saw" is silent by construction
  when the feed dies. Presence of data is not currency of data.
- **A page cannot grade its own liveness on a clock it supplies.** Ops fetched the live
  Binance price and printed it beside a two-hour-old stop under the words "right now" —
  breaking, from the other side, the very rule its docstring carried: *a working price
  feed is not evidence the measurement is running.*

### Open

- **No verdict has been lost, because there was none.** The arms in the ledger at the
  time of the report had produced 2 resolutions. Any pre-fix arm still open will now
  either resume or retire `candle_feed_stalled`; both are visible.
- **`SAR_LIVE_SHADOW_MAX_OPEN_HOURS=48` is a measurement-population decision, not a
  mechanism one.** An arm that never flips is retired unmeasured rather than handed an
  invented market close — the mechanism as specified has no time stop and
  `SIGNAL_EXPIRY_ENABLED` is off. Say so if the horizon should instead exit at market.
- **#833's risk stamps read blank on pre-#833 arms** (`sar_risk_pct` etc. absent from
  rows already persisted). The sweep re-stamps them on the next bar consumed, so this
  self-heals; no schema bump.
## 🔴 SESSION 93 2026-07-30 — the feed did not decline, it was gated off on 07-07, and the gate could never let go

**Owner:** *"if we demote MTP you can see our engine seems to be dead for users"*
→ *"fix the 07-07 gates and push"*. Correct on both counts, and Session 92's
"MTP goes dark" recommendation was wrong.

### The volume cliff, from the 500-signal history

| | |
|---|---|
| 07-02 → 07-06 | 43–55 delivered/day, MOVER ~25% |
| **07-08 onward** | **4–15/day** |
| last 7 days | 11.4/day, **MOVER 74%** (91% / 93% / 100% on 07-28/29/30) |
| non-mover today | **3.0/day** |

First half 23.9/day → last half 11.0/day. Not a decline — a step, dated to
**2026-07-07**, when Session 43 shipped cohort-edge STEP 2 ACTIVE. Removing MTP
takes 12.4/day → 5.0/day; removing all movers → 3.3/day. MTP is not the
disease, it is the only path still emitting.

### Two defects in `cohort_edge`, both structural

1. **Absorbing state.** The gate suppresses on measured expectancy;
   `CohortEdgeStore` is written only by `trade_monitor` resolving a *delivered*
   signal. Suppressed → never emits → never resolves → never records → the
   count-bounded (`_window=30`) deque never rotates. **Nothing bounded record
   age**, so a cohort locked on 07-07 was still judged on 07-07 data on 07-30,
   permanently. Live census: 29 cohorts, 11 reach n≥10, **9 of those 11 measure
   below the −0.05 threshold** — i.e. 9 locked cohorts with no path back.
2. **Invisible.** `_reject()` does not stamp; each gate calls
   `_stamp_suppressed` itself, and this one never did. It is the **only** live
   gate with no row in the Suppression Quality Audit — no WOULD_WIN%, no
   EV/suppression, no verdict. 23 days of unmeasured suppression next to a
   table that ranked every other gate. `pair_analysis:critical` had the same
   omission (its 30-day window does self-release, so only the stamp was missing).

**`context_floor` was left alone deliberately** — it already stamps, and Layer G
has already written `suppress_negative: false` for MOVER_TREND_PULLBACK,
MOVER_AVWAP_SCALP, SR_FLIP_RETEST, MEAN_REVERT, LIQUIDITY_SWEEP_REVERSAL and
DIVERGENCE_CONTINUATION. That loop self-corrects; `cohort_edge` could not.
The audit's `context_floor:MOVER_AVWAP_SCALP` **DROP** verdict (n=126, 58.7%
WOULD_WIN, −0.53R/suppression) is historical suppressions, already released.

### Shipped

| Change | Where |
|---|---|
| **Evidence expiry** — `sample_count`/`expectancy` count only records inside the window; gate releases and re-earns its verdict on real fills | `stat_filter.CohortEdgeStore` |
| `COHORT_EDGE_MAX_AGE_DAYS=14` + `cohort_edge_max_age_days` ops tunable (0 restores old behaviour, no deploy) | `config/`, `runtime_tunables` |
| `freshness()` / `frozen_cohorts()` — fresh-vs-total per cohort, and which cohorts stopped being re-measured | `stat_filter` |
| `_stamp_suppressed(sig, "cohort_edge")` and `"pair_analysis_critical"` | `scanner` |
| `cohort_edge_gate` liveness probe — pages if expiry is off while the gate is on, or if every cohort shares one `macro_dir` | `main._build_feature_liveness` |

**14 days is measured, not guessed:** 6 of 11 armed cohorts still reach n≥10
inside 14 days (3 at 7d, 7 at 21d), so the gate keeps working on the
high-volume cohorts while no verdict can outlive two weeks.

Tests: `tests/test_cohort_edge_absorbing_state.py`. All five core assertions
verified by reverting each half separately. Suite 7503 passed / 58 skipped;
ruff clean; mypy 104 (no new). A first cut used `except Exception: pass` and
`test_fail_open_sweep` caught it — now `fail_open.record`, failing open toward
the store's default window, never toward "no expiry".

### What the 500-signal + 7-day analysis actually said about MTP

- 28d: MTP n=147, **−0.543%/trade, −79.8% total**, 23.8% win, TP1 reached 2/147.
- 7d (`real_pnl_pct`, trail-aware): MTP −0.176%, whole book **+15.4%**. Improving.
- **Two thirds of MTP's stop-out loss never went favourable at all** — 55 of 85
  stop-outs never reached +1%, −138.4% of a −212.9% total. An exit change cannot
  touch those; the "give-back" story is the minority.
- A **+1.0% first target** is the only variant that improves MTP on *both*
  windows (28d +31pp, 7d +20pp); every other target improves one and degrades
  the other. Even at +1.0%, MTP is still −48.7% over 28 days. Non-movers
  realised +32.78% and beat *every* fixed target — the trail is right there.

### Open

- **`sl_distance_pct_at_entry` is unusable and it is Session 43's field.**
  Missing on 152/378 taken rows, missingness outcome-correlated (`PROFIT_LOCKED`
  39/42 present vs 3/42 absent), 125/226 values exactly 3.00 (the
  `noise_floor_max_sl_pct` clamp), disagrees with the signal's own geometry on
  218/226 rows. Written only inside the fail-open `_apply_noise_floor_stop`,
  while `original_sl_distance` is stamped earlier and never updated when the
  stop widens. **No R figure from these records is verifiable** — ops
  `/track-record` divides by this. Fix before publishing any R.
- **Watch the release.** `cohort_edge` rows should now appear in the
  Suppression Quality Audit with a KEEP/TUNE/DROP verdict, and non-mover
  volume should recover as locked cohorts age out. Re-read in a fresh window —
  do not judge from the pre-change report.
- **MTP entry quality, not MTP existence.** 55 stop-outs that never went
  favourable is an entry-trigger signature. Needs `pair_admission` (shipped
  Session 92) plus a never-went-favourable stamp to filter against.
- **`macro_dir` was `DECLINE` on all 29 cohorts.** A BTC macro flip resets every
  cohort to n=0 and disarms the gate in one step. Probe added; no fix — the
  behaviour is correct, the surprise was not.

---

## 🔴 SESSION 92 2026-07-30 — tokenised stocks were in the live paid book, and the path that put them there was the one nobody had filtered

**Owner ask:** *"discuss on scan universe"* → *"talk more on promoted pairs"* →
*"fix everything, automatic is important, we can't regularly check pairs."*

The discussion was supposed to be about universe *size*. Reading the delivered
signal book instead of the config made it a different session.

### What the emitted population actually says

`monitor-logs:signals_last100` — the last 100 signals the router **delivered**:

| | |
|---|---|
| Distinct symbols | 53 |
| Median 24h volume | **$25.7M** |
| Under $100M / $50M | 84 / 62 |
| `MOVER_*` setup classes | **73 / 100** |

The top-75 core scan — the subject of every capacity discussion this repo has
had, including Session 85's — produces a **minority** of what subscribers
receive. The delivered book is dominated by pairs admitted for 6h at a time
through mover promotion.

### Finding 1 — five stock perps, live, in the paid book

| Symbol | What it is | vol | pnl |
|---|---|---|---|
| SMCIUSDT | Super Micro Computer | $22.3M | −1.52%, 0 |
| SOXSUSDT | Direxion Semi Bear 3X ETF | $38.0M | −1.93%, −3.00% |
| IBMUSDT | IBM | $57.7M | −1.68% |
| NOKUSDT | Nokia | $25.9M | 0 |
| LRCXUSDT | Lam Research | $5.4M | −2.37% |

**7 delivered signals, mean −1.50%, zero TP hits, all seven stopped out.**
LRCXUSDT had already appeared in the Session-91 SAR export and nobody had
noticed what it was.

Root cause, one grep: `is_tradfi_perp` appeared in **all four** `pair_manager`
fetch paths and **nowhere in the scanner**. `_ensure_mover_pair` — the one
admission path that reaches outside the top-N onto the whole ~600-pair
`!ticker@arr` board, i.e. exactly where stock perps live — checked two static
name lists and nothing else. This is #B18 (WDCUSDT, `-4411` on a paid user's
auto-trade, 2026-07-18) recurring with five new tickers, because the
"structural filter" written to prevent the recurrence was never wired to the
path that leaks.

### Finding 2 — the 6h prune ate half of every promotion window

`refresh_top50_futures` deleted everything outside the fresh top-N from
`pair_mgr.pairs`, including the synthetic movers the scanner had parked there.
Refresh period 6h; `MOVER_PROMOTION_TTL_SEC` 6h → mean ~50% of each window
lost. Invisible three ways: the scanner never re-admitted (its own
`symbol in _mover_promoted_pairs` skip), the dead symbol kept consuming
promotion budget until TTL, and the scan-set builder dropped it on a
`pair_mgr.pairs.get(...) is not None` guard **with no else-branch**.

### Finding 3 — nothing recorded that a signal came from a promoted pair

`SignalRecord` carried 38 fields and not one answered "core or promoted?" The
population producing 73% of the book was analysable only through `setup_class`
as a proxy. Under that proxy: `MOVER_*` n=73 mean −0.259% with **zero** TP
hits; non-mover n=27 mean +0.581% with all 9 TP hits; `MOVER_TREND_PULLBACK`
alone n=60 mean −0.445%. Volume tells you nothing — `<$50M` and `>=$50M` split
−0.032% vs −0.033%. **Illiquidity is not the discriminator; MTP is.** (n=100,
one window, `pnl_pct` not R-normalised — not a verdict, a reason to measure.)

### Shipped — branch `claude/scan-universe-discussion-am3vnp`

| Area | Change |
|---|---|
| **Structural gate** | `symbol_filters.crypto_perp_admission` — **fail-closed** verdict (`metadata_unavailable` / `unknown_to_exchange_info` / `tradfi_perp`), called by `_ensure_mover_pair`, each reason separately counted |
| **Floor** | SMCI/SOXS/IBM/NOK/LRCX added to `_NON_CRYPTO_BLACKLIST`; `EURUSDT` de-duplicated across the two sets |
| **Hold registry** | `PairManager.hold_symbol` / `release_symbol` / `held_symbols`; **both** prune paths honour it; scanner claims on admit, releases on expiry |
| **Silent drop** | scan-set builder now counts `promoted_pair_vanished` and WARNs with the symbols |
| **Provenance** | `Signal.pair_admission` → `SignalRecord.pair_admission` → `SignalDetail` — `CORE` / `MOVER_IGNITION` / `MOVER_TOP24H` / `SURGE`, stamped at scan time |
| **Probes** | `promoted_pair_integrity` (keyed on pairs under promotion, not on the universe map) + `mover_admission_metadata` (a fail-closed gate needs a probe on *why* it closes) |
| **Dead code** | `run_periodic_top50_refresh` deleted — wired to nothing, advertised a 90s cadence the engine never ran; docstring corrected to the real 6h `_pair_refresh_loop` |
| **Types** | `_mover_promoted_pairs` was annotated `Dict[str, int]` while every write stored a monotonic float |

Tests: `tests/test_scan_universe_admission.py`, `tests/test_promoted_pair_provenance.py`.
**All nine core assertions verified by reverting the fix** — they fail against
the old code. Full suite 7491 passed / 58 skipped; ruff clean; mypy 105 → 104.

Two existing test files were driving `Scanner._populate_signal_context(None, …)`
and mover admission against an unseeded metadata cache — both now drive the
real collaborators.

### Dark-first note

The admission gate **narrows** what emits and closes a live leak into the paid
book, so it ships enforcing rather than shadow-first; the measurement half
(provenance, counters, probes) is ON from the same deploy per § Project Phase.

### Open

- **`pair_admission` has no ops surface yet.** Dark work must be observable —
  the engine now stamps it and nothing renders it. Next: a `/track-record`
  and Strategy-Lab split by admission, which is what makes "is MTP bad, or is
  MTP-on-promoted-pairs bad?" answerable. **No backfill** — the promotion
  expires long before the signal closes, so pre-deploy records stay `""`.
- **MTP is 60% of the delivered book at −0.445% mean and zero TP hits.** Do
  not act until `pair_admission` has a window; the proxy is not the fact.
- **Universe size is not the lever** and Session 85's QCB premise is stale —
  QCB now emits (2621 generated / 689 gated / **14 emitted**), and Layer G has
  persisted `min_samples: 15` for `QUIET_COMPRESSION_BREAK@ATR`/`@FIXED`.
  Those are **arm** keys; the live unsuffixed key carries no override — worth
  confirming the relaxation reached a routable key (#806/#807 pattern).
- **Surge promotion is effectively dead** under `TOP50_FUTURES_ONLY`:
  `_update_volume_baseline` only considers pairs in `pair_mgr.pairs` that are
  *not* in the scan set, and the map is pruned to exactly the scan set plus
  held movers. Left alone deliberately — deleting it is a separate change.

---

## 🟢 SESSION 91 2026-07-30 — a replay cannot tell you whether a mechanism is operable (#832, ops #106)

Owner asked whether the SAR ledger and the dark-signals bake-off were both measuring
correctly, and if not which to believe. Neither, as it turned out — and the reason
generalises past SAR.

### What shipped

| Repo | Change |
|---|---|
| **360-v2 #832** | **`src/sar_live_shadow.py`** — the SAR exit measured forward in the monitor loop, 5m + 15m arms per signal |
| **ops #106** | **`/signals/sar-live`** — Live tab (running arms, distance to the parked stop) + Resolved tab (the verdict) |

### The diagnosis, from the owner's three CSV exports

`/signals/sar` had **8 of 19 rows unresolved, and all four of the window's winners
were in that bucket.** Its resolved population read 2 wins / 11, −0.682R — a fact
about the resolver's refresh budget (40 symbols/cycle against ~85 ledger symbols),
not about SAR. Five of the eight had provably blown through their own SL or TP1:
BTWUSDT SHORT sat RUNNING 8% past its static stop; ESPORTSUSDT SHORT straight through
TP1.

Two rows also carried an entry 0.4–0.6% from the dispatched one (LRCX 262.17 vs
263.774). Backing the extreme out of each side's MFE gave the **identical** low from
both, so the price path agreed and only the entry did not — a promotion that attached
to a different detection of the same setup (#816 again).

Dark signals resolved all 21 and is honest, but it is still hindsight. Split by
whether the trail actually exited:

| Population | SAR-trail | Engine actual | Delta |
|---|---|---|---|
| All 21 | +0.069% | −0.306% | +0.375pp |
| The 18 that exited | −1.017% | −1.087% | **+0.070pp** |

**The entire apparent edge lived in three un-exited marks.** Separately, 5 of 21 real
exits were break-even-shift saves at −0.10% that the trail bleeds to −2.9%.

### Rules earned

- **A replay cannot validate a mechanism, only a hypothesis.** It answers "would this
  have been profitable" and is silent on "could we actually have done it". And a
  deferred verdict inherits its resolver's health — a loss-selected sample is worse
  than no sample, because it looks like an answer. Ask what fraction resolved, and
  whether the unresolved part is random.
- **A resting stop is part of the mechanism.** "Exit at market on the flip" specifies
  no stop between bars and would breach the naked-position invariant live, so
  measuring it literally measures something unshippable. Both fills are recorded —
  parked stop touched intrabar, and confirmed flip at the close — and their
  difference is the cost of confirmation, which nothing had ever measured.
- **"Blank" needs a cause before it gets a caption — and this session broke that rule
  and then caught it.** `flush()` wrote only when an arm changed, so with no open
  signals the file was never created and ops rendered UNAVAILABLE: *"the engine is
  not writing it, check the flag and the container."* A healthy engine in a quiet
  market produced a fault message. Owner caught it on screen minutes after deploy.
  The ledger now writes on a **60s heartbeat**, which is what makes the file's mtime
  mean anything: missing = loop not running, current-and-empty = nothing open,
  stale = loop stopped. Three states are only separable if a live loop keeps touching
  the file.

### Open

- **`/signals/sar` still misreports.** `SAR_EXIT_SHADOW_CANDLE_REFRESH_MAX_PER_CYCLE`
  is 40 against ~85 ledger symbols. Untouched deliberately — worth fixing only if that
  page should stay trustworthy alongside the live arm, which the live arm may make moot.
- **#830 is superseded.** It adds a third *replay* arm (`@SAREXIT5`) to answer the 5m
  vs 15m question that #832 now answers live, and would take each candidate from 2
  resolve targets to 3 on the resolver that is already starving. Its `aligned_for_arm`
  / `classify_pending` bug fixes are in its own new code, so closing it loses nothing.
  Its Session-90 notes are salvaged above.
- **`sar_disclosure.dart` says "our signal research runs on 15m".** No longer true —
  we now measure 5m and 15m. Hold the reword until the live arm has a window, so the
  copy is changed once.
- **No verdict yet, by construction.** Arms resolve as today's signals close, and 5m
  will resolve fastest and dominate early. That is a timing artefact — do not read the
  first window as a timeframe result.

---

## 🟢 SESSION 90 2026-07-29 — a marker captioned ENTRY was drawn at the exit (#828, #829, app #142, ops #104)

Session started as conflict cleanup and became two owner-caught display faults, both
of the same shape: **a value read for one purpose, reused as if it meant another.**

### What shipped

| Repo | Change |
|---|---|
| 360-v2 #828 | Liveness probes for the SAR resolver (rebase of #827; its conflicts were a squash-merge artifact, not a code disagreement) |
| **360-v2 #829** | **`dispatch_timestamp` / `terminal_outcome_timestamp` on `SignalDetail`**, `timestamp` normalised tz-aware |
| **lumin-app #142** | **Chart markers anchored on those stamps**, exit marker added |
| **ops #104** | **SAR ledger path v2→v3**, plus a drift guard for the next bump |

### 1. The chart drew the exit and called it the entry

Owner compared the ops signals CSV against the app's charts. Seven signals, seven
positive offsets — 2, 6, 18, 33, 41, 62, 65 minutes — and the only near-zero one was
the only signal still open. **The offset was the hold time.** On COTIUSDT and ZILUSDT
the arrow captioned ENTRY sat exactly on the SL line: the stop being hit, drawn as
the entry.

`_signalFromJson` read `minutes_ago` and dropped `timestamp`, so `ChartOverlay` had
nothing to anchor to and computed `now - minutesAgo`. `minutes_ago` is recency of the
signal's **last** event — for a closed signal the terminal one, deliberately, because
it feeds an "SL_HIT 3m ago" caption.

`minutes_ago` was **not** redefined: it is correct for the label it serves. The engine
now publishes the instants instead, so no consumer derives one.

Blast radius was wider than the arrow. `signal_snap` picked its *timeframe* from
`minutes_ago` too — a trade opened 6h ago that closed 2 minutes ago scored as 2
minutes old, got a 15m window ending long after its entry, and lost its marker
entirely rather than misplacing it.

### 2. Ops was reading a ledger the engine abandoned nine hours earlier

Owner reported the Clear SAR ledger button doing nothing. **The clear path has no
defect** — traced every hop. #822 bumped the engine ledger v2→v3 at 00:12 IST and ops
still read v2. The button correctly emptied v3 while the page re-read an orphan that
nothing writes, prunes or clears.

Everything on `/signals/sar` — 507 rows, the agreed/opposed split, the win rates —
was the population #822 had just ruled untrustworthy. Expect far fewer rows now; the
small number is the honest one.

### Rules earned

- **A recency label is not a timestamp.** "3m ago" and "happened at 04:05" answer
  different questions, and the difference is invisible until something plots it. Any
  consumer that needs a *point in time* must be given one; deriving it from a caption
  reintroduces whatever the caption was measuring from. The app now takes `timestamp`
  / `terminal_outcome_timestamp` and computes nothing.
- **An orphaned file is worse than a missing one.** A missing path surfaces as an
  error the page shows; an orphan renders as data — complete, confident, and wrong.
  #817 said *a field one repo reads and no repo writes fails silently and looks full*;
  this is the same failure at **file** scale. When a producer versions a path, the
  consumer needs a check that the two ends still agree, not a second copy of the
  constant. The fix for a drifting mirror is still not another mirror.
- **A naive datetime is a bug waiting for a timezone.** `DateTime.parse` binds a
  zone-less stamp to the *device* zone — 5h30m of silent error on an IST phone, on
  the field a chart marker is placed by. Normalise at the producer; parse
  defensively at the consumer.
- **A test can assert the bug.** The replaced `opened time precedes now` pinned
  `now - minutesAgo` as *correct*, which is why nothing caught this for months. And
  a test written with the same constant on both sides follows the code wherever it
  points: ops' first abandoned-file test passed happily with the path reverted to v2.
  **The revert check is what catches a test that asserts nothing** — run it on the
  test, not only on the fix.
- **A squash-merged base makes an honest branch look conflicted.** #827's three
  conflicting files were exactly the three files its already-merged parent touched;
  `git diff` between the pre-squash commit and the squashed one was empty. Replay the
  branch's own commit onto the new base rather than adjudicating a conflict that is
  a history artifact.

**Open:** #829's `dispatch_timestamp` is published and nothing reads it yet — the app
anchors on `timestamp` so the chart agrees with the ops CSV. If "when could a user
have acted" ever matters more than "when did the engine stamp it", that is the field
to switch to.

---

## 🟢 SESSION 89 2026-07-28 — the SAR arm's edge was inside its own fill error (#822, ops #101, app #140)

Owner asked for Parabolic SAR on the app charts, "aligned with our Signals". Shipping
the indicator took one PR. Asking what "aligned" should mean took the rest of the
session and ended with the arm's headline number deleted.

### What shipped

| Repo | Change |
|---|---|
| lumin-app #140 | SAR chip on the charts — dots, engine's 0.02/0.2, own caption module |
| 360-v2 #821 | Cross-repo vector pinning the app's port to `parabolic_sar` |
| **360-v2 #822** | **The fill fix**, bake-off script, ledger v2→v3, replay script |
| **ops #101** | Same fill fix, plus ops' third SAR copy finally pinned |

### The bug

`parabolic_sar` overwrites `out[i]` on a **reversal bar** with the post-flip level —
the prior trend's extreme, sitting on the *far side* of price. Both simulators read
that as "the stop in force during bar i", so `lows[i] <= stop` was trivially true on a
flip bar and the gap-through branch filled at **the bar's open** instead of the level
price actually breached. Right bar, wrong price.

One-directional, because a flip bar normally opens on the profitable side of the stop
and wicks through it:

| | |
|---|---|
| 820 real 15m flips, 10 symbols | mean **+0.222%**/trail exit, flatters the trade **95%** of the time |
| 186 delivered signals replayed | trail exits **−0.814%** once corrected, **0 of 186 improved** |
| genuine gap-throughs (open is correct) | **1%** |

Session 88 read **+0.197% net/trade** for this arm. Corrected: **≈ +0.02%**.
**The measured edge was smaller than the measurement error.**

### Three consequences bigger than the ledger

1. **PF 1.60 is affected.** `scripts/exit_method_backtest.py` carries the identical
   bug, and that script produced the headline this arm exists to confirm or kill.
   Fixed; **re-run before quoting PF 1.60 again.**
2. **It skewed the ranking, not just the level.** `atr` builds its own ratcheted trail
   and `supertrend` exits on the close — neither reads the flip-overwritten series.
   The bias landed on **SAR alone**, the method being considered for adoption.
3. **The ledger cannot answer the adoption question at all.** A 467-row / 8.6h export
   held **5 delivered** rows, 2 closed, and `delta_r` empty on **all 467** — the A/B
   has n=0. 462 of 467 rows describe signals no subscriber ever saw.

### What the delivered population actually says

`scripts/replay_signal_history_sar.py` (new) replays a `signal_history` export through
this module's **own** `simulate_sar_exit`. First run — 186 signals, spot proxy, 37%
coverage, **directional only**:

| | win | mean net | mean R |
|---|---|---|---|
| SAR arm (replayed) | 28.5% | +0.202% | +0.67 |
| **engine's real exit** | **37.1%** | **+0.256%** | **+2.46** |

The live exit wins on all three, against a counterfactual that never paid a spread.
Alignment split came out **agreed +0.42% vs opposed −0.06%** — the *opposite* ordering
to the ledger panel, which is itself evidence the ledger's split was biased.

**Open — do this next:** re-run on the VPS with `--market futures`. Binance futures is
451-blocked from the dev container, so 63% of rows were unreachable and the gap is
systematically the small-cap perps where the fill error is largest. Also: mean and
median disagree violently on both arms (SAR +0.202% vs −0.442%), and 44% of rows are
repeats of a symbol+side pair, so neither mean is a typical trade.

### Rules earned

- **A published indicator value is not a fill price.** Wilder's SAR publishes the
  post-flip level on a reversal bar; the level a position is *stopped at* is the
  projected-and-clamped one, knowable before the bar trades. Any simulator that reads
  an indicator series as a stop must ask which of the two it is holding.
- **Three copies, two pinned, is unpinned.** #821 locked engine↔app and left ops'
  transcription free. The copy nobody is watching is the one that drifts.
- **A fixture anchored to a frozen date, rendered by a route reading the real clock,
  is a time bomb** — and it names the wrong thing when it goes off. ops' trials test
  went red at 12:00 UTC on **a date, not a commit** (#101), reading as a broken trials
  page. Reducer tests inject their clock and stay frozen; route fixtures rebuild from
  `now()`.
- **"Is it measuring accurately?" is a question worth asking before every replay.**
  The owner asked it here and it deleted a headline number. Everything downstream of
  a wrong fill — `r_multiple`, `pnl_pct`, `delta_r` — is wrong with it, which is why
  v2 could not be migrated and had to be dropped.

---

## 🟢 SESSION 88 2026-07-28 — the SAR panel's verdict was an artifact, three times over (#815, #816, #817, ops #97, #98)

Owner asked a narrow question — *compare DEXE @ 2.95 across the Signals tab and the
Performance tab, which do I trust* — and every layer under it turned out to be
misreporting. Five PRs, all merged, all measurement-path.

### 1. RUNNING and `real_is_active` are different fields (no bug — a reading error)

`/signals/sar` status `RUNNING` means **the ledger record has not resolved yet**
(`sar_exit.py:255`), not that a position is open. The dark page's `real_is_active`
comes from the live `/api/signals` status, where `RUNNING` *is* in `_ACTIVE_STATUSES`
— so `False` genuinely meant the real signal had closed. Both surfaces were right;
they answer different questions. The real DEXE trade banked **+4.10%** while the SAR
counterfactual was still holding at **+13.12%** with only **+1.34% locked in** by its
stop. Quote the floor beside the mark or the counterfactual reads better than it is.

### 2. The resolver could not resolve a rotated-out mover, and said nothing (#815)

Four mover rows sat at RUNNING showing marks of −6% to −10% for trades that had
**already stopped out at their 3% cap** — COTIUSDT 15 minutes after entry, KAITOUSDT
120. `fetch_ohlc_15m_since` reads only the warm in-memory store, and a promoted mover
has no WS subscription at all: `scanner._refresh_stale_mover_candles` is its only 15m
writer and runs solely for **actively scanned** movers. Rotate out → array freezes →
walker returns WINDOW → `classify_pending` rightly refuses it → 48h → INSUFFICIENT.

This is the **mirror of #811**: that fix gave *core* pairs a `@kline_15m` stream and
left movers on the REST-reseed path, which works right up until the symbol stops being
scanned.

Neither watchdog could see it. The miss was silent by construction (`if early:
continue`, no counter), and `candle_coverage` walks `pair_mgr.pairs` — the *current*
universe, which by definition excludes the symbols at risk. It scored 100% throughout.

Fixed: `historical_data.refresh_timeframe` (replace, never merge — `_merge_candles`
has no `open_time` dedup, so an overlapping pull duplicates bars and a duplicate reads
as a zero-width gap to the contiguity guard, making a record *permanently*
unresolvable); a bounded oldest-first refresh on the audit loop; per-cycle miss
counters carrying a **cause**; and a `sar_ledger_candles` probe keyed on records we
owe a verdict on rather than on the live universe.

### 3. One move was buying ten rows (#816)

221 of 300 rows in the owner's export were re-stamps. SLXUSDT SHORT
MOVER_TREND_PULLBACK alone produced **10 rows in 2h10m across a 0.37% entry spread** —
36% of the whole resolved population.

| resolved population | n | win | avg R |
|---|---|---|---|
| per row (what the page showed) | 28 | 32% | **−0.364** |
| per move | 11 | 55% | **+0.003** |

**The sign flipped.** The cooldown bounds the stamp *rate*, not rows-per-move, and its
key carries provenance — so a candidate oscillating across a gate boundary holds two
budgets. All **21 of 21** sub-cooldown repeats were provenance flips; zero were genuine
cooldown misses.

The provenance key is **kept** (2026-07-25's reason still holds). Instead the move is
tracked provenance-free and a re-stamp must carry *new information* to earn a row —
the only such information being a suppressed→enqueued upgrade, spent **once per move**.
SLX becomes 2 rows. Rows carry `stamp_schema` so the two sampling regimes are never
pooled silently; `SAR_EXIT_SHADOW_SAME_MOVE_PCT=0` restores the old behaviour.

### 4. The page truncated before it filtered (ops #97)

`reduce_sar_signals` defaulted to `limit=300` and cut *before* `filter_sar_signals`, so
every filter ran on ~4.17h of a ~2,000-pair ledger. That starves the rarest and most
important population hardest: **"Delivered to users" silently meant "delivered, within
the newest 300"** — 4 emitted rows against 152 enqueued and 144 suppressed. The cap now
lives in the route, after filtering, bounding only the rendered table. `distinct_moves`
discloses concentration beside every count.

### 5. Closed-signal records never carried their regime (#817)

Found while scoping the track record. `app/routes/performance.py` has read
`r.get("entry_regime")` since it was written; `SignalRecord` carried neither that nor
`entry_regime_15m`. **The per-regime table on `/performance` has been bucketing every
closed signal into UNKNOWN** — a full-looking table describing nothing. Stamped now at
*both* terminal call sites (`trade_monitor` + `main` expiry); stamping one would skew
the population by outcome type. **No backfill** — the regime at entry is knowable only
at entry, so pre-deploy rows read UNPLACED rather than being handed a guess.

### 6. `/track-record` — paper trading without the month-long wait (ops #98)

Owner's ask: new users wait a week to a month for their per-user paper book
(`paper_book_registry`) to say anything, while the engine has recorded every closed
signal all along. Owner's call: **implement the record, no backfill.**

Two things turned out already to exist — `signal_history_store` persists the app feed,
and `PerformanceTracker` has been writing every closed signal, **uncapped**, to
`data/signal_performance.json`, which ops already mounts and reads. So no new engine
API was needed; only the regime field was genuinely missing.

`/track-record` renders it: day/week/month buckets, window presets + custom range
(inclusive end), regime/setup/symbol/side filters, CSV export. **Recorded, never
reconstructed** — nothing replays candles, which is what separates it from
free-run / dark-signals / exit-backtest. R is the headline, not portfolio %, because a
portfolio return needs an invented position size and `MAX_SAME_DIRECTION_GLOBAL=3`
means two users on identical settings get different fills.

### Open — next session

1. **Regime buckets read UNPLACED until new signals close.** Don't judge the regime
   filter until a fresh window accumulates.
2. **`PerformanceTracker` is uncapped and `_save()` rewrites the whole array per
   close.** O(n) per close, unbounded growth. Retention means *deleting history* —
   its own change, its own reasoning.
3. **TAGUSDT rows are stamped `agreed`**, where the trail governs from bar zero and the
   SL is never consulted, so their −6.5% may be real arm losses. Futures-only, so not
   replayable from this sandbox; #815 should now resolve them.
4. **`fetch_and_store_fallback` merges without stamping freshness**, unlike
   `seed_symbol` and `_gap_fetch_and_merge`. It feeds the dispatch staleness gate, so
   it wants its own change rather than riding along in a measurement PR.
5. **Lumin move for the track record** is now a presentation job, not a data one. The
   gating question is unchanged and is the owner's: **subscribers-only, or visible
   pre-signup?** Pre-signup makes it a financial promotion in the launch region.

---

## 🔴 SESSION 87 2026-07-27 — the 15m timeframe has had no live feed, ever

Owner asked for a real analysis of the SAR ledger: *how does it close on a flip, and
does it match live data with timing.* Every one of the 300 rows in the
`sar_signals_20260727165736Z.csv` export was replayed against independently fetched
15m candles using the engine's **own** `simulate_sar_exit` / `parabolic_sar` (imported,
not re-derived), so the only thing under test was the data and the timing.

### The exits that resolve are honest

| Check | Result |
|---|---|
| Closed rows landing on the **same 15m bar** as an independent replay | **21 / 25** |
| Median abs. price error on those | **0.148%** (max 0.456%) — cross-venue basis |
| Stamped `sar_aligned` reproduced | **24 / 25** |

The 4 timing misses are all symbols with no Binance data path from this session
(Binance REST answers 451 from our egress region; candles came from Binance **spot**
for 205 rows, Gate/MEXC perp for the rest). **No repeat of #800** — exit prices are not
a function of (symbol, side), holds vary, exit bars are real bars.

### But almost nothing resolves, and the root cause is not in the ledger

272 rows read RUNNING. On real candles **245 of them had already hit their trail —
median 4.4 hours earlier**, the oldest at 08:30. Resolution is **all-or-nothing per
symbol**: PENGU 0/17, BOME 0/16, RE 0/16, LAB 0/14 … while STORJ 6/8, ZRO 5/5,
USELESS 5/5 resolve fine. The nine that work are exactly the **mover-promoted** pairs.

**There is no `@kline_15m` subscription anywhere in production code.** `bootstrap.py`
subscribed 1m/5m/1h/4h; `update_streams_for_top50` (whose default *does* include 15m)
is never called; `WS_FALLBACK_POLL_INTERVALS` is 1m/5m; `_gap_refill` only refills
subscribed streams; `seed_symbol` runs on universe entry and `TOP50_FUTURES_ONLY`
makes `new_symbols` permanently empty. Movers are the sole exception **by design** —
`_seed_mover_pair` + `MOVER_CANDLE_REFRESH_SEC=120` re-seed them precisely because
they sit outside the WS set. So a core pair's 15m array is frozen at the last boot.

Confirmed three ways from the ledger itself:

| Test | Result |
|---|---|
| Stamped `sar_aligned` vs live data — fresh-15m (mover) symbols | 26/27 = **96.3%** |
| Same, every other symbol | 163/270 = **60.4%** (coin flip) |
| Per-symbol fit of a **frozen** SAR series | PENGU 17/17 · BOME 16/16 · RE 16/16 · LAB 14/14 · NIL 12/12 · SYN 10/10 · GWEI 5/5 (live explains 0/5) |
| Fitted freeze times | cluster at **2026-07-25 03:00–03:15 UTC** across 10 independent core symbols — the last boot |

### Blast radius: this was never a measurement-only bug

15m ATR feeds **live SL/TP geometry** (`channels/scalp.py:6650,6800`), MTF weights,
structure state, BTC-State (0.30 weight), the 15m CVD divergence path (its
`interval == "15m"` branch in `_on_ws_message` was unreachable), and the **BTC regime
kill switch** — a dispatch gate reading "the last 4h of 15m candles" with no timestamp
check, so its verdict had been frozen for 2.5 days.

**And the watchdog was blind by construction.** `candle_coverage` asserted ≥20 15m
candles *exist* — never their age — so a 500-bar array frozen for 2.5 days scored
100%. `last_kline_age_seconds` was already on the store and unused here. The #802
`alignment_crosscheck` counter was blind for the same reason: it only fires on records
that resolve, and only fresh-data records resolve.

### Shipped (this PR)

- `@kline_15m` added to the Tier-1 futures subscription set — one stream per pair,
  ~25% more messages on a pool sized at 200 streams/conn, no REST weight, no Firestore.
- `candle_coverage` now checks **depth AND age** (`CANDLE_COVERAGE_MAX_AGE_SEC`,
  default 2700 = 3 bars), so this class of freeze can never again be invisible.
- `tests/test_ws_15m_subscription.py` drives the real `start_websockets` and asserts
  *every seeded intraday timeframe has a live feed* — the general invariant, not a
  copy of the stream list. Verified by reverting: 3 of 4 fail against the old code.

### Follow-up shipped the same session — the guard (`src/data_freshness.py`)

#811 fixed the cause; the guard makes the *next* freeze impossible to score on
unnoticed. `candle_coverage` pages when the feed dies, but it cannot say whether a
**particular signal** was built on a dead bar, and it does not stop that signal — a
watchdog that reports after the geometry shipped is a detector, not a guard.

- **Refuses, never clamps.** Where 15m is known-stale its indicators are withheld, and
  every consumer already owns a *written* fallback for absent 15m: MOVER falls to 5m
  ATR, QCB to the legacy 5m compression check, `resolve_pre_tp_threshold` to its
  `"static"` source. Refusal routes into tested paths rather than inventing one.
- **Unknown ≠ stale, deliberately asymmetric.** `last_kline_age_seconds` returns None
  on a restored snapshot. Monitoring counts that as not-fresh and pages; the money path
  refuses **only on a positive age above the bound** — degrading every pair's geometry
  after a snapshot restore would be worse than the failure being guarded.
- **Dark-first, two flags.** Counting is ON and visible through the new
  `stale_tf_scoring` liveness probe (which reports what *would* have been withheld);
  `stale_tf_refuse_enabled` ships **false** and is registered as an ops tunable.
- Wiring is tested against the real `_build_scan_context`, not the module alone — a
  guard nobody invokes is a scaffold and unit tests can't tell the two apart. Verified
  by reverting: deleting the scanner hook fails `TestScannerWiring`.

**Owner decision pending:** arm `stale_tf_refuse_enabled` once a window shows what it
would have withheld. If the counters stay at zero, that is #811 working.

### Redesign after the clear — conditional handover (owner directive)

Owner cleared the ledger for fresh data, which is the **only moment redefining a live
measurement is free** — the same window #802 used. Owner's design, shipped into it:

> for opposed we do continue with paths SL and TPs and meanwhile if SAR alignment
> happened then it drops SLs and TPs follows SAR exit; if no alignment happens then
> original SLs TPs close the signal

So `@SAREXIT` is no longer trail-from-bar-zero:

| At entry | Behaviour |
|---|---|
| SAR onside | trail governs from bar one (unchanged) |
| SAR opposed | runs on **live SL/TP1** — bar for bar the control arm — and hands over to the trail only if SAR later comes onside |
| never comes onside | live geometry closes it; both arms agree **exactly** |

This removes the artefact today's analysis found: 84% of the opposed cohort was a
one-bar exit at the next bar's open — a ~7-minute drift measurement wearing an exit
method's name, dragging a pooled headline that moved with the alignment mix. It also
**sharpens the A/B**: a trade that never hands over contributes exactly 0 to `delta_r`,
so the comparison is decided only by trades where SAR actually took over. `handover_n`
/ `handover_share` are recorded and rendered for exactly that reason.

Two intrabar rules, both deliberately unflattering (counterfactuals are already
optimistic): a bar that takes out the static stop **and** flips SAR onside is a **stop**;
a TP1 touch before handover closes at TP1.

`REASON_STATIC_SL` / `REASON_STATIC_TP1` joined `_FINAL_REASONS` in
`suppression_audit` — without that every never-handed-over trade would park at RUNNING
for the full 48h, the exact failure #798 already paid for. Ops maps both to their own
statuses; they previously fell through to NO_DATA, which would have reported a data
fault about trades that resolved fine.

### Open — next session

1. **The 245 stuck ledger rows** are unresolvable from the in-memory store (their bars
   rolled past). Either re-resolve from REST once 15m is live, or clear and restart the
   window. Do not read the arm's verdict off the current population.
2. `delta_r` is empty on **all** 25 closed rows — `@SARBASE` needs the full 48h window,
   so the A/B this arm exists to run currently has **n = 0 comparisons**.
3. The resolved subsample is **72% "SAR opposed" vs 40% in the stamped population**
   (only movers resolve). Any split panel over closed rows describes nine small caps.
4. `_feed_sar_edge` writes both alignment cohorts into Layer C under one
   `SETUP@SAREXIT` key. `summarize_sar_alignment` splits them; the edge feed does not.

### What the exit did on 2026-07-27 (real candles, 297 rows, net of 0.10% RT taker)

| cohort | n | win | gross avg | **net avg** | one-bar | median hold |
|---|---|---|---|---|---|---|
| ALL | 270 | 56.3% | +0.297% | +0.197% | 49.6% | 30m |
| **SAR agreed at entry** | 151 | 53.0% | +0.107% | **+0.007%** | 22.5% | 60m |
| SAR opposed at entry | 119 | 60.5% | +0.537% | +0.437% | 84.0% | 15m |

The agreed cohort is the only one testing the exit — it nets **+0.007%/trade**, i.e.
it pays the fees and returns nothing, while median MFE before the trail fired was
0.859%. The opposed cohort is not trail performance at all: its stop is on the wrong
side of price from bar zero, so 84% of it is "exit at the next bar's open" — a ~7-minute
drift measurement. One censored day, gross of slippage; **not a verdict**, and nothing
resembling the bake-off's PF 1.60 yet.

---

## 🟡 SESSION 86 2026-07-27 — the QCB unlock doesn't exist; Layer G was tuning phantoms (#806)

Session 85's handoff called the QCB emission unlock *"the highest-value item on this
list, by a distance"* — the difference between **0 and non-zero** on a +2.21R path.
Checked it first, as instructed. **It closed as measured-false in three independent
ways.** The check itself then found a real bug (#806), which is the actual finding.

### §4 is closed — do not re-open it

All figures from `monitor-logs`, controller **cycle 279**:

| Handoff §4 claim | Measured now |
|---|---|
| Best cell `n=29`, **one sample short** of the n≥30 relax floor | **n=50** — crossed it unaided; the window cap, not a threshold |
| That cell is **+2.21R** | **+0.32R edge / +0.44 avg_r** (`OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL`) |
| QCB converts **0 of 1,055** → unlock the floor | QCB **emits 23**; generated 3,005 → gated 1,927 |
| Layer G should self-promote `QCB min_samples 30→25` | **HOLD is correct.** `has_unlock = 15 <= 50 < 30` is False — nothing is sample-blocked |

And the decisive one. QCB's dominant suppressor is `context_floor` (**733 of 979**), and
that gate is **measured protective**:

```
context_floor:QUIET_COMPRESSION_BREAK   n=662   EV +0.164 R/suppression   verdict=KEEP
```

`VERDICT_KEEP` is defined as *"gate correctly suppresses losers"* and positive EV means
the gate **saved** R (`suppression_audit.py:121,485-493`). So those 733 suppressions are
the gates working. Per CLAUDE.md § The Autonomous Portfolio: *"Zero emissions ≠ broken.
Fully gated + measured-negative is the gates working — don't 'fix' the first case."*
**§4 was pointing at exactly the case the doctrine says not to fix.**

Why it looked otherwise: the +2.21R was a thin-sample counterfactual that regressed
toward +0.44 as the window filled — *"counterfactuals are optimistic"* and *"wait for a
fresh window before judging a verdict"*, both already in the brief. A handoff that
quotes a cell R as a live opportunity is quoting the number those two rules exist to
distrust. **21 QCB cells are STRONG and most sit at the n=50 window cap** — the path is
measured and floor-relaxed where it wins. There is nothing to unlock.

### What the check actually found — Layer G tunes keys nothing reads (#806)

Layer G's **inputs** are keyed by *matrix* strategy (`build_inputs` walks
`StrategyEdgeStore.matrix()` verbatim → includes `X@ATR`, `X@FIXED`, `SHADOW_*`). Its
**output** is read by `PolicyParams.resolve_min_samples(strategy)`, and both callsites
pass `sig.setup_class` — a live `SetupClass` value (`scanner/__init__.py:5039,7934`).
So an override under any other key is **unreachable by construction**: stored,
persisted, logged `[EMISSION_CONTROLLER:APPLY]`, shown in ops as an "active override",
read by nothing.

| | |
|---|---|
| Persisted overrides that are dead keys | **9 of 18** |
| Lifetime promotions spent on unroutable keys | **23 of 40** (17 variant arms + 6 shadow units) |
| `best_strong_cell` keys unroutable | **8 of 23** |
| `gate_metrics` keys unroutable | **0 of 4** — the suppress loop is correctly keyed |

The phantoms don't merely leak, they **outcompete the real rows** for a 2-per-cycle
budget, for two compounding reasons:

- **The auto-tighten brake cannot fire on them.** `losing` needs `h_n >= health_min_n`
  (20) where `h_n` is summed `n_emitted`. An arm never emits → 0 forever → permanently
  `losing=False` → unconditionally promotable. Armed for only **3 of 23** strategies;
  `MOVER_AVWAP_SCALP` (emitted_n=20, avg_r −0.317) fired it correctly twice (20→25→30),
  which is precisely why its absence on the arms matters.
- **The sort prefers them.** Every `min_samples` candidate has
  `ev_per_suppression_r=None` → sort key `0.0`, so all tie and the stable sort falls
  back to alphabetical: `QUIET_COMPRESSION_BREAK@ATR` before `RANGE_FADE`,
  `SR_FLIP_RETEST@FIXED` before `WHALE_MOMENTUM`. Structural, not incidental.

This is *"Measurement arms are not strategies"* broken in a **third** place — CLAUDE.md
names the ops rollup and `geometry_ab._VARIANT_SUFFIXES`; the controller is a consumer
nobody added to that list.

**Fixed and shipped (#807 + ops #93), measurement live.** The owner's initial call was
write-up only; they then reframed it — *"just dark-flagging is, we don't [get] actual
data… do it like the SAR signals, how we are observing, then data is in front of us,
then we analyse, then take decision"*. That is § Project Phase as written
(**measurement ON, user-visible effect OFF**) and the correction to the SAR arm's
mistake of shipping the measurement switched off. So it shipped as two flags:

| Flag | Default | Effect |
|---|---|---|
| `emission_controller_routable_enabled` | **ON** | Classifies candidates, reports the standing dead-override footprint, computes the counterfactual. Changes nothing. |
| `emission_controller_routable_live` | **OFF** | Closes the action space and prunes the dead keys. **Owner decision — still open.** |

The decision-relevant output is the **counterfactual**: `run_cycle` re-runs its own
bounded selection over routable candidates only and diffs, naming both halves — the
promotions spent on dead keys *and* the live candidates that would have taken those
slots. Read off the controller's real decision, not inferred.

Two design points worth not re-deriving:

- **The dead-override count is a standing footprint, not candidate-derived.** Verified
  against real production state: cycle 279 has **0 candidates but 9 dead overrides**. A
  candidate-derived report would have read all-zeros on the panel and hidden the very
  thing it exists to show.
- **Enforcement's prune is re-derived from `routable` every cycle**, never a one-shot
  migration, so the invariant re-establishes itself and needs no schema stamp or
  deploy-date gate (#802's lesson applied rather than re-learned).

**Layer G had no ops surface at all** before this — live and self-promoting on the money
path since S72 with nowhere to watch it, which is *how the waste survived 279 cycles*.
Ops #93 adds `/emission-controller` (nav: Autonomy → Layer G). The panel renders the
engine's `routable` stamp and deliberately holds **no suffix constant** — the fix for a
drifting mirror is not a second mirror.

**A distinct sub-case, flagged not proposed:** `_CONTROL_ARM` makes `SHADOW_MEAN_REVERT`
/ `SHADOW_RANGE_FADE` the *cell* source for live `MEAN_REVERT` / `RANGE_FADE`, but the
cell resolves under the shadow name while the override resolves under the live one
(`context_emission_policy.py:305,388`) — measurement and override under two keys that
never meet. Folding them together would be a real money-path change.

### The transferable lesson

**A handoff's numbers are a snapshot, not a finding — re-measure before acting on the
item it ranked first.** Every §4 figure was accurate when written and wrong ~12h later,
because rolling per-cell windows keep moving. The cost of re-deriving was three
commands; the cost of acting on it would have been relaxing a floor the audit measures
as protective at n=662, on a live money path with real users behind it.

Corollary: **a stale premise is most dangerous when it is confidently ranked.** §4 came
with a mechanism, code references and a "do this first" — all of which survived the
data changing underneath them.

---

## 🟡 SESSION 85 2026-07-27 — we had the engine capped at 1.5 of the host's 4 cores (#803, #805)

**Owner ask:** *"can we add one more IP to VPS and scan full Binance futures in our
scanning universe — advantages, disadvantages, Binance minutes?"*

The answer is no, and the reason is not the one the question assumes. But the
investigation found something better than the thing it was looking for.

### The premise doesn't hold

We run at **~10% of one IP's 2,400/min futures weight budget**. Binance's rate limit
is not what stops us. And the asymmetry that settles the IP question: **weight is
per-IP, order limits are per-account** — a second IP buys market-data budget and
**exactly zero order throughput**.

Three things get conflated in "scan the full universe", and they have different answers:

| | Limited by | 2nd IP helps? |
|---|---|---|
| **Knowing** what every pair does | `!ticker@arr` — **already solved**, ~500 pairs, 1 WS conn, zero REST | not needed |
| **Deep-scanning** every pair | engine CPU | **no** |
| **Emitting** more signals | `MAX_SAME_DIRECTION_GLOBAL=3` | **no** |

That last row is decisive: **more pairs cannot produce more delivered signals**, only a
different candidate pool for the same 3 slots — and the extra pairs are by construction
the least liquid.

### What the measurement found (`scripts/diag_capacity.sh`, new)

First time anyone has looked at the box:

| | Measured | |
|---|---|---|
| Host | **4 cores / 7.8 GB** | at **~25% load** |
| Engine CPU | **130% of a 150% cap** | **~87% of allowance** |
| Engine RAM | **459 MB / 1 GB** | 45%, **0 OOM kills, 0 restarts** |

**We capped the engine at 1.5 cores and left ~3 host cores idle behind our own limit.**
At 87% on 75 pairs — with mover promotion already taking the scan set to 105 — the
engine was very likely **being throttled at candle boundaries**, i.e. exactly when every
timeframe recomputes and exactly when the market is worth scanning. Safe ceiling today
is **~85 pairs**, *below* where mover promotion already reaches.

### Two methodological corrections worth keeping

1. **RAM was never the constraint.** The first draft called it *Critical* ("6.7× against
   a 1 GB limit → OOM-kill → re-seed loop"). Measured 459 MB, never OOM-killed. An
   arithmetic guess dressed as a finding; marked measured-false in the doc.
2. **Extrapolating capacity from scan wall-clock hides Docker throttling** — throttling
   lives *inside* cycle times. Measuring CPU consumption directly is what exposed the
   87%. **When capacity is the question, measure CPU, not latency.**

### Shipped

| PR | What | State |
|---|---|---|
| [#803](https://github.com/mkmk749278/360-v2/pull/803) | Research doc + `scripts/diag_capacity.sh` | Draft, CI green — owner merge decision |
| [#805](https://github.com/mkmk749278/360-v2/pull/805) | Engine 1.5→2.5 cores, 1g→3g; redis capped (had none) | Draft — **needs owner deploy window** (recreate ⇒ re-seed) |

After #805: safe ceiling **~120–145 pairs**, RAM out of the picture past 600. Full
universe (~500) needs **8–9 cores** for the engine alone — this box has 4, so it stays a
hardware project with the §8 business case still unmade.

### ⚠️ The landmine, if a second IP is ever revisited

Every server-side auto-trade user has whitelisted **exactly one VPS IP**. Order traffic
egressing from a second IP returns `-2014` on every key — **including stop-loss placement
on an open position**. Direct hit on the naked-position invariant. Egress pinning must be
OS-level per container (~20 `ClientSession()` sites in `src/`) and the signing container
must **fail closed**. Full rules: research doc §6.

### 🔴 The QCB thread — carried to Session 86, highest value

Owner: *"our concentration we may get more chances for QCB path right?"* Right instinct,
wrong mechanism, and the correction is the useful part.

`QUIET_COMPRESSION_BREAK` best cell is **+2.21R** (OVERLAP/QUIET/COMPRESSED) and emits
**0 of 1,055**. The cell sits at **n=29, one sample under the n≥30 relax floor**.

- More pairs → **proportionally** more QCB candidates. `VOL_COMPRESSED` is a *per-symbol*
  ATR percentile (`market_context.py:144`), so ~20% of any pair set is compressed at any
  time — **do not claim illiquid alts compress more often; the percentile normalises that
  away.**
- **But supply is not the bottleneck** — feeding more candidates into a 0/1055 converter
  yields 0/1,760.
- **The real benefit is measurement velocity:** more candidates fill n=29 → n≥30 faster,
  the Layer G controller relaxes the floor, QCB starts emitting. Genuine reason to widen
  the universe; *not* a throughput argument.

Layer G already shipped to self-promote `QCB min_samples 30→25` (envelope: ceiling 30,
step 5, floor 15 — **one step unlocks it**). **First action next session:** check
`monitor-logs:monitor/analysis/emission_controller.json` for whether that promotion has
fired, and if not, why. That gates a +2.21R path currently emitting nothing — worth more
than anything about universe size.

### Open follow-ups (all in `docs/HANDOFF_SESSION_86.md` §5)

- **`SCAN_STAGE_TIMING_ENABLED` is OFF** — no scan-cycle data at all; the 16s figure used
  throughout is from **2026-06-04**. Enable alongside the #805 deploy.
- **No Binance weight gauge anywhere** — `rate_limiter.update_from_header` parses the
  authoritative `X-MBX-USED-WEIGHT-1M` and discards it; no ops panel in any of the 24
  route modules. Off money path, ships normally.
- ~~`src/api_limits.py` is **dead code with the wrong constant**~~ — **DONE 2026-08-05**
  (price-action program Phase 0). Module, its tests and both dead instantiations
  deleted; `rate_limiter.py` is now the single budget authority.
- ~~`/fapi/v1/trades` declared `weight=1` while fetched with `limit=1000`~~ —
  **DONE 2026-08-05**. Actual weights verified: `/fapi/v1/trades` **5**,
  `/api/v3/trades` **25**. All call sites now read `src/binance_weights.py`, and a
  CI test AST-parses `src/` to fail on any hand-typed weight or undeclared endpoint.
- **Three uncapped containers remain in `360ce-ops`** (`360ce-ops`, `-agent`, `-redis`).

---

## 🟢 SESSION 84 2026-07-27 — SAR agreement was decidable at entry and recorded 48h late (#802, ops #91)

**Owner ask:** *"what is that Any SAR agreement — at entry we only have two
situations right, agreed or opposed"*, from the live `/signals/sar` panel.

The question was about a dropdown label. The label was fine; what it exposed was
that **94% of the ledger carried no verdict at all**.

### The cross-tab that settled it

Full export, 277 rows:

| | has verdict | blank |
|---|---|---|
| `CLOSED_TRAIL` | 16 | 0 |
| `RUNNING` | 0 | 261 |

Perfectly diagonal, zero exceptions. The panel blamed those blanks on *"the
walker refused to replay them, or they predate the flag."* **Neither cause
accounted for a single row.** After #800 that is the worst possible false alarm —
a data-fault claim over a population that was merely still open.

### Root cause — a fact recorded where it was convenient, not where it was known

`aligned = entry_sar < entry` compares the indicator level on the entry bar
against the entry price. **No future candle participates.** Both numbers exist
the instant the scanner stamps. But the line lived inside `simulate_sar_exit`,
which runs when the walker resolves the trade up to 48h later.

So the agreement mix on screen always described a two-day-old population, the
sample read 16 when it could read 277, and *"how many of the signals we are
sending go against the indicator"* — an **entry-filter** question about the live
money path — was unanswerable.

**Fix (#802):** `stamp_sar_pair` takes the warm 15m arrays and writes
`sar_aligned_at_entry` onto both arms at stamp time, after the cooldown gate.
Undecidable inputs write nothing — `None` never collapses to `False`. The resolve
path keeps computing the same quantity under `sar_aligned_at_resolve` as a
**cross-check, never an overwrite**, behind a `sar_alignment_crosscheck` liveness
probe: a sustained divergence means the walker is not reconstructing the bar the
scanner saw, which is #800's failure mode made self-reporting.

### The off-by-one the proposal missed

The proposal said "use the same expression as the resolve path". Taken literally
that ships a detector firing forever on a definitional difference:

- The store appends **closed candles only** (`main.py`: `if k.get("x")`), so the
  newest bar at stamp time is the last *completed* one.
- The resolver's entry bar is the one **containing** the stamp — still *forming*
  when the signal fired.

Adjacent bars, and **across a SAR flip they sit on opposite sides of price**.
Worse, the resolver's answer was never knowable at entry, so it could not be the
definition of "what we knew when we took the trade". Both paths now read the last
bar **closed at entry**. This redefined a published measurement, which was free
only because the owner had cleared the ledger the same hour.

### What the data actually says about counter-SAR signals

Not what it looks like. The opposed bucket's −0.11R is the **trail's** result, and
an opposed SAR is a stop already breached at entry — the walk has no choice but to
exit on the first testable bar. The row records ~15 minutes of drift. 38% win over
8 trades, gross of fees, is a coin flip minus a round trip, not a verdict on the
signal.

Also, from the same export: **every opposed row is `enqueued`. Zero were ever
delivered.** An entry filter today would suppress a population with no measured
instances at the delivery layer.

The question "are counter-SAR *entries* bad" needs the **live-geometry arm**
(`@SARBASE`) split by agreement — impossible before #802, since only trail-resolved
rows got a flag. Collectable from this deploy onward.

### Ops #91 — the panel measured a population the page was not showing

`summarize_alignment(all_rows)` ignored every filter, so with Source set to
Gate-suppressed the page showed 149 rows under a split over all 267. That is #88
again: only the delivered population can justify changing what subscribers
receive. Also shipped: a **distinct-exits** column (three BUSDT rows stamped
00:04/00:47/01:34 all exited at 0.1959, one rally carrying 3/8 of the agreed
bucket — +1.24R is really ~+0.90R over ~5 independent moves), pending-vs-unresolved
split, and the alignment `<select>` given its own label instead of borrowing
"Status".

### Rules this bought

- **Record a fact where it becomes true, not where it is convenient.** Deferring a
  derivable value to a later pass does not just delay it — it silently shrinks
  every population that reads it, and the shortfall looks like missing data rather
  than late data.
- **"Blank" needs a cause before it gets a caption.** Not-yet-resolved and
  could-not-be-resolved are different states; pooling them under one sentence
  reported a fault that was not happening.
- **Closed bar ≠ current bar.** The store holds closed candles only; a resolver
  locating "the bar containing the stamp" is looking at the bar *after* the newest
  one the scanner had. Any stamp-time/replay-time comparison must reconcile that or
  it compares different bars.
- **Redefining a live measurement is only cheap while its population is empty.**

### Open

- `delta_r` empty on all 277 rows — **zero paired `@SARBASE` comparisons**, so the
  A/B has produced no comparison at all. Unverified whether that is ledger youth or
  a join bug. Next look.
- Ops panel splitting the live-geometry arm by agreement — the one thing standing
  between the owner and the counter-SAR decision.

---

## 🟢 SESSION 83 2026-07-26 — The SAR arm was replaying the wrong candle (#800, ops #89 + #90)

**Owner ask:** *"what happening to counter SAR signals — within 15 mins they are
seeing huge loss"*, with the `sar_signals` CSV attached. The question was about
counter-SAR entries. The answer was that the arm had not been measuring anything.

### The export disproved itself

| TRUMPUSDT SHORT | stamped | entry | exit |
|---|---|---|---|
| | 09:55:35 | 1.582 | **1.598** |
| | 12:21:29 | 1.574 | **1.598** |
| | 13:01:03 | 1.570 | **1.598** |

Exit price was a pure function of **(symbol, side)** — stamp time irrelevant.
XRPUSDT's nine rows gave two prices, one per side; DOGEUSDT, HYPEUSDT, BNBUSDT
the same. 41% of supposed one-bar moves exceeded 5%, the worst was **51.8% in a
single 15m bar**, all 172 rows claimed exactly a 15-minute hold, and `delta_r`
was populated on **0 of 172** — so there was no A/B either. Mean −4.40R,
cumulative −757R, all of it fabricated.

### Root cause — an index inferred instead of looked up

`fetch_ohlc_15m_since` found the entry bar arithmetically: `n_post = elapsed //
bar_sec`, counted back from the end of the array. That assumes the candle array
is gap-free **and** its last bar is current. Neither holds — feeds drop frames,
and a frozen feed keeps serving its last bar, which is why
`last_kline_age_seconds` exists at all (the MVLLUSDT 11-hour freeze). When the
assumption broke, `min()` on the length and `max(0, …)` on the index **absorbed
it silently**, so the walk replayed an unrelated bar and still returned a
confident verdict. A stale feed pinned every record for a symbol to the same
physical bar — exactly the constant-exit-price signature above.

The store could not have caught it: `update_candle` kept only OHLCV, **no
timestamps**.

**Fix:** candles carry `open_time` (seed + WS), the entry bar is located by
searching it, and the window is verified — finite timestamps, contiguous bars,
and the stamp actually *inside* the selected bar. Anything else returns `None`
and the record resolves INSUFFICIENT.

### Rules this bought

- **A clamp is not a guard.** `min()`/`max(0, …)` on an index turn "I cannot
  answer this" into a wrong answer with no signal. Where an input may not
  support the computation, **refuse** — a record that cannot be honestly
  replayed must produce no verdict. "We don't know" is a usable output; an
  invented number is not.
- **Positional data needs its own key.** Any array consumed by *when* something
  happened must carry the timestamp; inferring the index from wall-clock
  arithmetic is a silent-corruption class, not an optimisation.
- **When rows are evidence of a defect, purge — don't migrate.** No field can
  rescue a row whose candles were wrong. The ledger restarted on
  `sar_exit_candidates_v2.json`; v1 stays on disk for forensics, never read.

### Counter-SAR — the original question, now answerable

A trailing SAR is a stop that is *already somewhere* at entry. Agreed → its level
sits behind the entry and the trail rides (the method being measured). Opposed →
its level is already the wrong side of price, so the trade dies on the first
testable bar for **≈ −0.25R** (0.6% stop) or **≈ −0.50R** (0.3% stop) — a scratch
still pays the round trip. That figure says we took a signal against the
indicator; it says nothing about trail quality. Pooled, the headline moves with
the agreement mix rather than with the exit, so `sar_aligned_at_entry` is
recorded and the buckets are reported separately with an **opposed-share**.

**Process note.** The alignment split first shipped engine-side with nothing
calling `summarize_sar_alignment` and nothing rendering the flag — a scaffold,
caught by the owner asking the question a second time. Ops #90 closed it. *A
measurement is not shipped until a surface reads it.*

### Open

- **The v2 ledger starts empty.** No verdict until a clean window accumulates.
  The buckets fill at very different rates — opposed resolves in 15 minutes,
  aligned sits RUNNING for hours — so an early read is biased against SAR.
- **Watch for INSUFFICIENT clustered on particular symbols**: that is a real 15m
  feed gap the old code was papering over, worth chasing on its own.
- **Activation policy for opposed signals is undecided and owner-sign-off**: skip
  the signal (SAR as entry filter), keep the live static geometry, or trail and
  accept the scratch. Decide against the panel, not ahead of it.
- Also shipped: owner-gated `POST /api/admin/sar-ledger/clear` + ops Clear
  button (confirm · PRG · audited), so a poisoned window can be discarded
  without waiting on a deploy.

---

## 🟢 SESSION 82 2026-07-26 — iPhone PWA: every setup screen needed two taps (lumin-app #137, merged)

**Owner ask:** *"in iPhone web app while setting up, screens are not working
properly, we need to press couple of times to go next screen — they are like
freezing. After login everything is smooth."* Four screenshots: welcome slides
1–3 and the phone sign-in form.

**The diagnostic was in the ask.** "Smooth after login" is not a footnote — it
localises the bug. Every `NavShell` tab owns a real scrollable that consumes a
vertical drag. The screens that misbehave do not: the welcome carousel is a
`PageView` that scrolls **horizontally only**, and `WelcomeConsentPage` /
`PhoneSignInPage` are plain non-scrolling Columns. So any defect that depends on
the Flutter scene absorbing vertical drags breaks on exactly the pre-login set
and nowhere else.

**Four causes, all on that path. Fixed together — any one left in place still
costs the user a tap.**

| # | Cause | Fix |
|---|---|---|
| 1 | The HTML document was free to scroll. Flutter paints into one canvas so there is nothing to scroll, but Safari rubber-bands the document on any drag the scene did not consume — including the small one starting an ordinary tap. Canvas shifts under the finger, the tap resolves against stale coordinates, the press only resets the overscroll. | `web/index.html`: `body` pinned out of flow at `inset: 0`, `overscroll-behavior: none`, `touch-action: manipulation` |
| 2 | Seven text fields autofocused at mount. A browser raises the keyboard **only** inside a user gesture, so Flutter believed the field was focused while the user saw no keyboard — the first tap went into settling that. | New `lib/shared/platform_input.dart` → `kAutofocusTextFields` (`!kIsWeb`), applied at all seven sites. Native unchanged. |
| 3 | `_FirstRunGate._advance` re-ran the async flag read, so every "Get Started" / "Continue" dropped to the blank splash for ≥1 frame and swallowed taps landing there. | Stage order is fixed → walk it synchronously, read storage once on mount. |
| 4 | The carousel learned its slide from `onPageChanged`, which fires part-way through the 300ms animation; a tap before that read a stale index and re-targeted the slide already in flight. | Adopt the target on the frame the tap lands; guard `_done` so a double tap continues once. |

**Off money-path** — onboarding chrome, web shell CSS, input focus. No engine
contract, dispatch, FSM, scoring or entitlement surface touched, so it shipped
via the normal PR path, not the dark-flag rule.

**Verification:** `flutter analyze` no new issues (130 pre-existing
`withOpacity` / `activeColor` deprecations unchanged) · full `flutter test`
green incl. 7 new tests · `flutter build web --release --no-web-resources-cdn`
clean. The new carousel test was confirmed to **fail** against the pre-fix
widget and pass after, so it pins behaviour rather than restating the code.
`test/web_shell_test.dart` guards the `index.html` block, which `flutter create`
would otherwise regenerate away.

**⚠️ Open item — not device-verified.** No iPhone in the session environment, so
causes 1–2 are reasoned from the symptom and the platform rules, **not observed
on hardware**. Owner to re-test the setup flow on `app.luminapp.org` from the
iPhone. If any two-tap behaviour survives, the next lever is Flutter web's
`flt-semantics-placeholder`, which can absorb the first pointer event of a
session — `SemanticsBinding.instance.ensureSemantics()` on web removes it, at
the cost of an always-on semantics tree. Deliberately left out rather than
shipped speculatively.

---

## 🟢 SESSION 81 2026-07-26 — #794 didn't fix it (88x), and #795's second half shipped inert (#795, #798)

**Owner ask:** *"still not matching and still Everything is running state when
they actually close and shows real output"* — with the ops export and the real
signal export attached.

**Both complaints were correct. Two distinct bugs, one of them ours from #794.**

### Bug 1 — the migration cutoff was a wish, not a fact

#794 relabelled pre-fix `emitted` rows by comparing `suppress_timestamp` against
a **hardcoded wall clock**: `PROVENANCE_ENQUEUE_FIX_TS = 1785002400`
(2026-07-25T18:00Z) — set to when the fix was *written*. The PR then sat unmerged
overnight and shipped at **2026-07-26T02:10Z**, an **8.17-hour gap**. Every
record stamped in that gap was written by the *old* enqueue-site code yet sat
*after* the cutoff, so the migration **trusted** it.

Measured on the owner's two exports:

| | |
|---|---|
| SAR ledger window | 2026-07-25T19:30 → 2026-07-26T02:04 (6.6h) |
| Rows ops labelled "Delivered to users" | **88** |
| Rows stamped after the real deploy | **0** |
| Real signals delivered in that window | **1** (WIFUSDT LONG @ 0.1574, 21:46:03) |
| SAR "delivered" rows matching *any* real signal ever | **1 of 88** |

So the panel read 88 against a true 1 — **88x, worse than the ~30x #794 was
written to remove.** The duplicate-stamp signature was still there too
(CHILLGUY/EPIC/WLFI each 4 rows at an identical entry), because those rows are
old-code stamps that the cutoff waved through.

**Fix: key on who wrote the record, not when.** New `prov_schema` field,
`PROVENANCE_SCHEMA = 2`, written at the stamp site and by `promote_provenance`.
`_migrate_provenance` downgrades any `emitted` record lacking the current marker.
A marker written by the code itself cannot drift from its own deploy time; a
guessed timestamp always can. Replaying the owner's 88 production rows through
the fixed migration relabels **88/88 → `enqueued`**.

That includes the one genuinely-delivered WIFUSDT row — unavoidable, since a
pre-fix record carries no evidence of delivery — and it is the safe direction:
lose one true positive, drop 87 false ones.

### Bug 2 — nothing ever resolved because the classifier refused to look

`classify_pending` skipped **any** record younger than the full window
(`if now - ts < eff_window: continue`), so a trailing arm whose stop caught price
after 40 minutes still read `RUNNING` for **48 hours**. Hence "0 resolved, 88
still running" on a tab where the underlying signals had visibly closed.

A trailing arm's exit is knowable the moment the forward candles cover it — no
later bar can un-catch a trail. Trailing records now classify **early**, with one
guard: only a real `REASON_TRAIL` exit counts mid-window. A `REASON_WINDOW`
verdict on partial candles is just the walker running out of bars, and booking it
would record an arbitrary price as a realized result — so it is rejected until
the window genuinely elapses. Static arms are unchanged (their outcome is a TP/SL
race decided by window extremes and cannot be read from a partial window).

`REASON_TRAIL`/`REASON_WINDOW` moved to `suppression_audit` (the ledger needs
them and must not import `sar_exit_shadow` — that dependency runs the other way);
`sar_exit_shadow` re-exports them so there is one definition.

**Engine-only.** Ops already renders the right labels and reads `classification`
— both fixes surface there with no ops change.

### Early resolution is result-identical — proven, not assumed

Resolving early would be worthless (and dangerous) if it changed the answer:
these outcomes feed the Strategy×Context edge matrix through `on_classified`.
It doesn't, and the property is now pinned by test rather than argued:

- The SAR level at bar *i* depends only on bars ≤ *i*, and `fetch_ohlc_15m_since`
  anchors the slice so entry always lands `warmup` bars in — so the series start
  is the same absolute time whenever you ask.
- `TestEarlyResolutionIsResultIdentical` asserts, across four seed/side fixtures,
  that **every** truncation still containing the exit bar yields an identical
  exit price, exit bar and hold time; and the converse — truncating *before* the
  exit bar reports `REASON_WINDOW`, which is exactly what the new guard refuses
  to book.

Early resolution changes **when we learn** an outcome, never **what it is**.

### Does this touch the autonomous portfolio? — audited, no

Owner asked directly. Traced, because Layer C is LIVE on the money path via
`context_emission_policy` and Layer G self-promotes off it:

> **`strategy_edge.source` and the ledger's `provenance` are two different
> fields that happen to share the word "emitted".** Layer C never reads the
> ledger's `provenance`.

All four writers into the edge store set `source` independently of it:
`main.py:1786`/`:1807` use `SHADOW if _is_shadow_unit else SUPPRESSED`;
`main.py:1862` and `:1916` (`_feed_sar_edge`) hardcode `SOURCE_SHADOW`. The
allocator's `emitted_backed` reads `cell["n_emitted"]` — an edge-matrix count,
not the ledger — and Layer D is recommendation-only regardless.

**So `provenance` is display/analysis-only** (ops panels, truth report). That is
also *why this bug survived*: it corrupted the number the owner reads to make
decisions, not the machinery that routes. Arguably worse, but it means the
blast radius of the fix is zero. **Don't re-derive one field from the other.**

**Cost:** the early path adds no I/O. `fetch_ohlc_15m_since` reads the warm
in-memory store (no network, no Firestore); the loop is 5-minutely and runs in
`asyncio.to_thread`. Per pass it is a slice plus a ~200-element SAR walk per
pending record — single-digit ms, off the event loop, and not a per-tick /
per-scan / per-order path.

**The transferable lesson:** a data migration must never be gated on a timestamp
predicting a future deploy. `_migrate_provenance` is now schema-gated, and any
future provenance change bumps `PROVENANCE_SCHEMA` instead of adding a date.

**Shipped:** #795 → `06a8858` (provenance schema + early-resolution path) and
#798 → `db476d8` (the guard key that made the second half actually fire), both
deploy green. The migration runs on ledger load, so it took effect at the
deploy's engine restart — not gradually. 67 tests in `test_sar_exit_shadow.py`;
full suite 7212 passed, 0 failed; `ruff` clean; `mypy` unchanged at 107.

### Verified after deploy — half of it worked, half shipped inert (#798)

**Bug 1 confirmed fixed on production data.** Owner's post-deploy exports:
"Delivered to users" **88 → 3**, "Queued, dropped by router" **3 → 104**. The
three surviving `emitted` rows (B2USDT SHORT, DIAUSDT LONG, DEXEUSDT SHORT)
match the app feed on symbol/side/entry/time. Router promotion fires on
confirmed delivery; the schema marker holds across reload.

**Bug 2 did not work at all — the guard read a key that never exists.** The
mid-window check was `detail.get("exit_reason")`, the *walker's* internal key
(`simulate_sar_exit`'s return). A **trail classifier** returns
`trail_exit_reason` — the ledger's field name, renamed at exactly that boundary
inside `classify_sar_record`. So the lookup was always `None`, never matched
`REASON_TRAIL`, and `continue` fired on every early candidate. The path ran on
schedule, fetched candles, walked the SAR, computed the correct exit, **and
discarded it.** Fixed in #798 (`db476d8`, deploy green).

The tell was again two pipelines disagreeing: the SAR ledger read 0 of 107
resolved with the oldest row ~7h old, while the dark-signals replay showed the
same trades exiting with `sar_hold` of 15/15/15/30/105 minutes. Same math, one
side dropping its answer.

**Why the tests passed against a dead path.** They hand-wrote the classifier's
return with the invented key — `{"classification": "WIN", "exit_reason": ...}` —
so they asserted against code that never ran. **A mock whose shape you chose
cannot verify a contract you got wrong.** Coverage is rebuilt around the real
`classify_sar_record`, over an OHLC dict shaped exactly like
`fetch_ohlc_15m_since` returns, and the fix was checked by *reverting* the guard
to confirm the new tests actually fail on the old key.

**Still unverified end-to-end:** rows leaving RUNNING with `CLOSED_TRAIL` is a
prediction until read in ops. **If they are still RUNNING ~15 min after
`db476d8`, that is a third distinct cause — re-diagnose from a fresh export,
don't assume.** (`delta_r` staying blank is *not* a fault: it needs the paired
`@SARBASE` control, which still waits its full 48h window by design.)

**Still true from Session 80:** the emitted sample restarts from zero, and now
genuinely does — including the one real WIFUSDT delivery, which a pre-fix record
carries no evidence for and so cannot be rescued. No SAR exit decision until a
fresh window of *delivered* signals accumulates.

**Process note worth keeping.** **Three** claims were stated to the owner as
settled and were wrong: that #794 fixed the inflation (it made it worse, 88x);
that "no SAR closed is arithmetic, not breakage" (the classifier was refusing to
read data it already had); and that #795 fixed the resolution (it shipped
inert). Every one was caught by the owner comparing a panel against real data —
never by an internal test, because the internal tests were confirming the same
assumption the code made. **When a measurement panel and the live feed disagree,
the panel is the suspect — and when a panel and a second pipeline over the same
trades disagree, one of them is discarding its answer.**

---

## 🟢 SESSION 80 2026-07-25 — "Emitted" never meant emitted: enqueue ≠ dispatch (~30x inflation)

**Owner ask:** four SAR numbers that should agree and didn't — "actual Emitted
signals to users about 4 to 6 … SAR Emitted about 100 … actual signals 300 …
SAR Dark 700 plus … no SAR is closed yet".

**Three of the four reconciled cleanly. The fourth was a real bug.**

| Ops showed | Reality |
|---|---|
| "Emitted to live (98)" | **90 distinct candidates reached the QUEUE. 3 reached the feed.** |
| "All (300)" | 300-row page cap; 246 distinct setups (202 suppressed + 98 "emitted") |
| "760 arms stamped" | 380 trades × 2 arms — reconciles with the 300 cap, not a discrepancy |
| app shows 4–6 | correct: 1 ACTIVE + 4 TP1_HIT + 5 PROFIT_LOCKED; **50 real signals in 4.2 days** |

**Root cause.** `scanner/__init__.py` stamped `PROVENANCE_EMITTED` immediately
after `signal_queue.put()` succeeded, with a comment asserting *"the signal
really did go out."* **It had not.** `SignalRouter._process` consumes that
queue and applies a whole second gate layer — correlation lock, per-symbol and
per-channel cooldown, per-channel concurrent cap (default 5), correlation group
limit, global same-direction throttle, TP/SL sanity, staleness — and drops most
of what it dequeues. **Enqueue is not dispatch.**

The contamination was **not random**: the old "emitted" set was **81% SHORT**
against a **52% SHORT** real feed, because the same-direction throttle rejected
the short pile-up *after* it had been stamped emitted. Per
`sar_exit_shadow.py`'s own docstring, the emitted sample is "the only population
that can justify changing what users receive" — so every exit decision from it
would have been made on signals users never received. The same
`_stamp_geometry_ab` site feeds the `@FIXED`/`@ATR` arms, so they carried it too.

**Compounding defect.** Earlier the same day a session had "fixed" this symptom
by making EMITTED **bypass the stamp cooldown**, reasoning "an emission is a
discrete dispatch event, duplicates prevented upstream by dispatch_cooldown."
That premise was false *because* the stamp was at enqueue — so the bypass let
every 15s re-detection stamp as emitted and **amplified** the mismatch (one
WLFIUSDT setup produced 5 "emitted" rows at an identical entry in 6.7h; EPICUSDT
14 rows, SLXUSDT 13). Bypass removed; the premise is now true for promotion.

**Fix — three provenance states, and only the router writes the last one:**
`suppressed` (scanner gate killed it) · `enqueued` (passed the scanner, queue
took it, router dropped it — nobody saw it) · `emitted` (router confirmed
delivery). `PROVENANCE_EMITTED` is written **only** by
`sar_exit_shadow.promote_to_emitted`, called from the router's
`# Register only after confirmed delivery` point. Pre-fix records are relabelled
`enqueued` on load (truthful, and fails safe by removing them from the emitted
sample rather than inventing membership).

**Not dark-flagged, deliberately.** This is a *measurement* correction: it
changes what gets recorded, not which signals emit, how they score, or any
exit / FSM / dispatch behaviour. No subscriber sees any difference, so there is
no user-visible effect to gate — and per § Project Phase, shipping a
measurement default-OFF is the wrong reading of the rule. It ships **ON**, with
its ops surface in the same change (labels corrected to DELIVERED / QUEUED /
SUPPRESSED, and the new queued stage separately filterable so the routing caps'
cost is itself measurable).

**Answered for the owner:** "no SAR closed" is arithmetic, not breakage — the
arm needs 48h and the oldest stamp was 6.7h old — and `RUNNING` is a
measurement window, **not** an open position, so nothing needs keeping
activated. Performance → Dark signals *does* resolve SAR (8 rows, holds
5–235 min) because it replays a bounded forward window while the
`@SARBASE`/`@SAREXIT` arm waits 48h: two pipelines, different rules, both
labelled "SAR" — presentation fault, numbers fine.

**Not yet trustworthy:** the emitted sample restarts from zero today. Mean SAR
3.02% vs real 1.99% on the 8 resolved dark rows is n=8 and counterfactuals run
optimistic (~0.38R on MTP) — **not evidence of edge.** Wait for a fresh window
of genuinely-delivered signals before judging the SAR exit.

**Branch note.** This change was first raised as #792 from
`claude/free-trial-new-customers-moo099` — i.e. *stacked on* Session 79's branch
rather than cut fresh off `main`. When #791 squash-merged, the two already-merged
free-trial commits collided with their own squash and #792 went conflicted. It is
re-raised here rebased onto `main` HEAD as the single commit that is actually
this session's work; the only conflict was the `ACTIVE_CONTEXT.md` insertion
point (both sides adding a section under the same anchor), resolved by keeping
both entries newest-first. **Lesson, per § Change-management Protocol step 1:
cut the topic branch off `main` HEAD** — stacking on an unmerged branch buys a
guaranteed conflict the moment the parent squash-merges.

---

## 🟡 SESSION 79 2026-07-25 — 7-day free trial for new customers (all four repos, branch `claude/free-trial-new-customers-moo099`)

**Owner ask:** *"offer 7 days free trial for every new customer so that they
can understand our services."*

**Two decisions taken via AskUserQuestion**, because signals + levels are
already free here — the paywall is on *automation*, so a trial gives away
server-side execution on a new user's real capital:

| Decision | Owner's answer |
|---|---|
| Tier | **`auto`** — the full product, not a reduced demo |
| Mechanism | **server-granted, no card** (not a Play trial offer) |
| Activation | **opt-in** — welcome pop-up, user taps to start |

Play's own free-trial offer was rejected as the mechanism: it only reaches
users who already got to checkout *with a card*, which is not "every new
customer." Accepted trade-off: **no auto-conversion at day 7** — the trialist
must choose to subscribe, which the in-app countdown/upsell exists to drive.

**The design decision that matters is where the grant lives.** Entitlement
truth is one `(tier, paid_until)` on the user row, and Play verify / RTDN /
the read-time expiry downgrade all rewrite it wholesale — a trial written
straight onto that row is erased by the first RTDN. So the grant is banked in
`user_reward_grants` (`source='signup_trial'`), the same durable ledger the
referral rewards use, and the composition already wired into every entitlement
write site picks it up unchanged. Dispatch consumes it the moment the row is
recomposed; expiry needs no new job (the existing read-time downgrade
re-resolves from the ledgers). Grants share **one sequential timeline** with
referral rewards; the trial takes **no cap** (the one-row-per-user PK bounds it
to once ever, and capping from *now* would shrink the promised week for a user
holding a referral window).

**Ships DARK, per § Project Phase — two flags, not one:**

| Env | Default | Effect |
|---|---|---|
| `SIGNUP_TRIAL_MEASUREMENT_ENABLED` | **true** | Stamps the eligible cohort + offer/claim/conversion funnel from the deploy. Grants nothing. |
| `SIGNUP_TRIAL_ENABLED` | **false** | User-visible: the offer becomes claimable and a claim writes entitlement. |

The cohort stamp rides the **profile read** — the one path every app session
hits, including releases that know nothing about trials — which is what lets
the would-be cohort accumulate while dark. One indexed single-row SELECT the
first time a user is seen per process, then a bounded in-process set
short-circuits it; per-foreground path, not a scanner/tick/order loop.

**Observability shipped with it** (a dark change with nowhere to look is
unfinished): ops → **Trials** reads `GET /api/trial/admin/funnel` and shows
cohort / offered / claimed / running / converted beside *both* flag states,
keeps `cohort_dark` permanently separate from `cohort_live`, and renders an
empty-denominator rate as "not measured yet" rather than a fake 0%.

**Eligibility = new customers only:** never trialled (DB-level PK), no paid
history (a *lapsed* subscriber counts; a purchase that never completed does
not — a declined card leaves you a new customer), onboarded, and optionally an
account-age limit.

> ⚠️ **Open item for the owner before activation.**
> `SIGNUP_TRIAL_MAX_ACCOUNT_AGE_DAYS` defaults to `0` (no limit), so flipping
> the offer live hands a trial to **every never-paid free user, including the
> base that predates this feature** — a one-time burst of accounts able to arm
> auto-trade. Set the limit first if that isn't wanted. Flagged in the runbook
> and in the ops panel.

**PRs (all draft, none auto-mergeable — Business Rules change):**

| Repo | PR | Contents |
|---|---|---|
| 360-v2 | **#791** | `src/api/signup_trial.py`, `user_trials` ledger + generic `_grant_tier_window_locked`, `/api/trial{,/claim,/admin/funnel}`, config block, `docs/SIGNUP_TRIAL_ACTIVATION.md`, 22 tests |
| 360ce-ops | **#87** | `/trials` panel — the dark-window read |
| lumin-app | **#136** | Welcome sheet + countdown banner + Settings re-entry tile |
| lumin-legal | **#5** | Terms §4b — opt-in, no card, no auto-charge, free of charge ≠ free of risk |

**Verification:** engine `tests/api/` 694 passed with 22 new (the 27 failures
are the sandbox's pre-existing missing-`firebase_admin` set, identical on
`main`); ruff clean, no new mypy errors. Ops `pytest -q` 493 passed, zero
failures. **lumin-app: no Flutter SDK in the session container**, so
`flutter test` had not run locally at PR time — CI is its first execution.

**Next step is the owner's:** read the dark cohort in ops → Trials over a real
window, decide the account-age limit, then activate per
`docs/SIGNUP_TRIAL_ACTIVATION.md`.

---

## 🟢 SESSION 78 2026-07-25 — Ops bake-off "timeout after 1800s" → the Backtester was Θ(n²)

**Owner ask:** screenshot of the ops Performance tab — exit-method bake-off
`FAILED rc=None / timeout after 1800s`.

**The timeout was the symptom, not the bug.** `Backtester._backtest_channel`
called `_compute_indicators(window[:i])` on *every* candle, recomputing all
eight indicators over the whole growing prefix each time. Measured on this
box: cost is a clean **14.6 µs × n²** (T/n² constant to 3 significant figures
across n = 500…3000), i.e.

| window | per symbol | 20-pair universe |
|---|---|---|
| 6mo × 5m (n=51,840) | **656 min** | **219 hours** |

The ops job allows 1800 s. It was short by ~440×, so **no timeout value could
ever have made it pass** — and indicator recomputation was ~99% of the wall
time (an indicators-only microbenchmark reproduced 649 of the 656 min).

**Fix — `_IndicatorTape` (`src/backtester.py`).** Every indicator involved is
*causal*, so each is now computed **once** over the full series and read back
by index instead of recomputed per prefix. Verified **bit-identical** (0.0
relative error on all eight; 166 prefixes incl. every length gate), so no
backtest number anywhere moves — `run_monte_carlo`, `run_per_pair_sweep` and
`run_regime_stress_test` all ride the same loop and are unaffected in output.

Post-fix the loop is **linear** (~0.31 ms/candle at every n measured):

| | before | after |
|---|---|---|
| 6mo × 5m, one symbol | 656 min | **16.5 s** |
| 20-pair universe (compute) | 219 h | **~5.5 min** |

Comfortably inside the existing 1800 s ops timeout — the bake-off can now
actually answer the question it was written for (does SAR-15m's PF 1.51
survive on thousands of trades, or was it one RIFUSDT trade).

**Guarded against regression** — `tests/test_backtester_indicator_tape.py`
locks equivalence at every length gate *and* asserts **structurally** (by
counting indicator calls, not by timing, so it can't flake in CI) that
indicator work does not grow with candle count. Full suite: 7077 passed,
mypy clean on `backtester.py` (it was at zero errors — kept there), ruff clean.

**Off money path** — the `Backtester` is an analysis tool; it emits no live
signals, so this ships normally (no dark flag / shadow window needed).

### Part 2 — the next run 429'd on all 20 symbols (same session)

With compute fixed, the first real run failed fast (`rc=1`) with **HTTP 429 on
every symbol**, BTCUSDT included — i.e. the IP was already at budget when it
started, not gradually exhausted. **The speedup unmasked this**: the script used
to be too slow to reach the fetch wall.

**This was a production hazard, not an analysis annoyance.** The script runs via
`docker exec` inside the engine container — same IP as live trading — with raw
`urllib` at a fixed 0.12s pause and `limit=1500`, bypassing every piece of
rate-limit machinery both repos already have (`src/rate_limiter.py`,
`src/binance.py`, ops' `_BanCircuit`). Binance escalates sustained 429s to a 418
IP ban, which would stop live signals and order execution. The box was already
IP-banned on 2026-07-24 (#778).

The numbers: `src/rate_limiter.py` budgets the engine **2,200 of the 2,400
weight/min** futures cap, leaving **~200/min** spare. The script was demanding
~5,000/min — ~25x the headroom.

**Fixed in the script's fetch layer:**
- **`limit=499` (weight 2), not 1500 (weight 10).** Candles-per-weight peaks at
  499 (249.5) — the 1500 cap was the *worst* setting available (150). 1.66x more
  data for the same weight.
- **`WeightPacer`** — paces to a `--weight-per-min` budget (default 200 = the
  engine's spare headroom) and **yields when `X-MBX-USED-WEIGHT-1M` shows live
  traffic near the cap**. That header is server-authoritative and covers all
  traffic from the IP, so it gives cross-process cooperation the engine's
  in-process limiter cannot (the script is a separate process).
- **No bursting.** Requests are spaced `60*weight/per_min`; `src/rate_limiter.py`
  records that burning the budget in a burst is what trips Binance's hard 429
  lockout (~42s at 100% usage).
- **`Retry-After` + exponential backoff**; a 418/403 ban **aborts the run**
  instead of being retried — retrying into a ban is what deepens it.
- **On-disk kline cache** (gzip CSV, per symbol+interval, closed candles only).
  Sweeping exit knobs over the same candles is the whole point, so re-runs now
  cost ~0 weight and finish in minutes; only the missing gap is fetched.

Cold 6-month/20-pair run: ~5,540 weight ≈ **28 min** at 200/min, so ops'
`EXIT_BACKTEST_TIMEOUT_SEC` default went **1800 → 3600** (30 min was too tight by
construction) and the Profit-tab copy now states the real expectation.

Two bugs the new tests caught in my own pacer before it shipped: it **bursted**
a full minute's budget at each window roll, and its spacing loop **spun forever**
once the remainder rounded below a float ulp (34M sleeps advancing the clock 24s).
Both are now pinned by regression tests.

### Part 3 — the run finished, fetched cleanly, and produced NOTHING

Third run: **rate limiting confirmed working on real data** — zero 429s, all 20
symbols fetched. But every symbol reported `0 price-action entries`, and a
`[warn] kline cache write failed (Permission denied: '/data')` per symbol.

**Root cause — the Backtester has emitted zero signals since 2026-07-11.**
`_backtest_channel` passed `ai_insight=` to `channel.evaluate`. **No channel has
ever accepted that argument** — `BaseChannel.evaluate` and
`ScalpChannel.evaluate` both take `(symbol, candles, indicators, smc_data,
spread_pct, volume_24h_usd, regime=…)`. Every candle raised `TypeError`, and the
handler did `log.debug(...)` + `continue`. So the measurement path was **dead for
two weeks** (since #713), silently.

It survived because **every existing assertion is guarded** —
`if results[0].total_signals > 0: …`. A backtester that never emits satisfies the
entire suite. This also breaks the Hard Limit "never swallow an exception
silently in a data/measurement path": the arm now calls
`fail_open.record("backtester.channel_evaluate", exc)` and logs at WARNING.

Everything built on `Backtester` was affected: `run_monte_carlo`,
`run_per_pair_sweep`, `run_regime_stress_test`, `run_walk_forward`, and the
bake-off.

**Correction to Part 1's numbers.** The Θ(n²) measurements were taken while every
evaluator threw instantly — so they measured a dead loop. With evaluators
actually running, cost was still superlinear (0.63 → 1.27 ms/candle as n grew),
because `_evaluate_sr_flip_retest` does `list(highs)` on every candle
(`scalp.py:3845`) while reading only `[-50:]` — the copy grew with the window.

Fixed by handing evaluators a **bounded tail** (`_EVAL_WINDOW = 300`), which is
what the live scanner does anyway (fixed window from `HistoricalDataStore`), so
it is a fidelity improvement as well as a speed one. Deepest lookback anywhere is
50 bars (scalp) / 100 (SMC detector). **Verified signal-identical** at bounds
150 / 300 / 600 vs unbounded. Indicators are unaffected — they still come off the
full-history tape, indexed at `i`.

Real numbers now, evaluators live and firing:

| | before | after |
|---|---|---|
| ms/candle | 0.63 → 1.27 (rising) | **~0.62 flat** |
| 6mo 5m, 20 pairs (compute) | ~92 min (superlinear) | **~11 min** |

Cold run ≈ 11 min compute + ~28 min paced fetch ≈ **39 min**; warm ≈ 11 min. Both
inside the 3600s ops timeout.

**Also fixed:** the kline cache defaulted to `/data/exit_backtest/klines` — the
**ops** container's volume, but the script runs in the **engine** container. It
now defaults beside `--out-dir` (writable by construction), and the unwritable
warning fires once instead of 40 times.

**Open follow-up (ops, not done here):** on timeout the ops runner
(`360ce-ops:app/data_sources/exit_backtest.py`) kills the process and
discards both pipes, so the owner got `timeout after 1800s` and nothing else —
the script's per-symbol `[ok] SYM: N entries` progress on stderr is lost
exactly when it is most wanted. Streaming stderr into a ring buffer so the
failure card can show the tail would make the next long-run failure legible.

### Part 4 — the bake-off's answer, and the shadow arm that has to confirm it

With the Backtester alive, the 6-month run completed on the VPS: 5m entries →
15m exits, 20-pair fixed universe, **102,496 entries**.

| Method | Total % | Median | Win % | PF |
|---|---|---|---|---|
| Engine baseline | −8,172.7 | −0.126 | 42 | 0.74 |
| ATR-trail | −15,054.4 | −0.363 | 33 | 0.72 |
| SuperTrend | −3,490.6 | −0.187 | 35 | 0.93 |
| **Parabolic SAR** | **+11,660.6** | −0.070 | 40 | **1.60** |

**Every robustness test passed.** Outliers: top-1 trade = **0.1%** of gross
profit, top-100 = 3.1%; drop-top-3 leaves PF at **1.60** (total −0.5%) — which
kills the original worry, where one RIFUSDT trade carried the entire 7-day
+28.9%. Time: positive in **7/7 months** (PF 1.11–2.39) while the baseline was
negative in all 7. Regime: QUIET 1.58 · RANGING 1.53 · TRENDING_DOWN 1.77 ·
TRENDING_UP 1.18. Direction: LONG 1.14 · SHORT 1.72. Breadth: **20/20 symbols
profitable**, top-2 = 17% of total. The only negative cell in the entire matrix
is TRENDING_DOWN × LONG (PF 0.90).

**Caveats that must travel with these numbers:**

1. **Median is negative (−0.070), so it fails the script's stated criterion.**
   That criterion is the wrong instrument: negative median + positive mean is
   the *defining signature* of a trend-following exit, so the rule rejects that
   whole class by construction. It was written to catch the one-trade artifact,
   and drop-top-N is the correct test for that — which SAR passes decisively.
   **Owner ruling 2026-07-25: DEFERRED** — decide the promotion criterion on
   forward-measured data, not on klines-only backtest entries.
2. **The baseline comparison was confounded by hold time** — baseline got
   `lookahead 20` × 5m = 100 min, trails got `max_forward_bars 192` × 15m = 48h,
   29× longer. The trail-vs-trail ranking *is* clean (identical window; only SAR
   profitable). Fixed structurally in Part 5 below rather than by re-running.
3. **It is really two setup classes.** `SR_FLIP_RETEST` (n=51,018, PF 1.90)
   carries **83%** of the total; `FAILED_AUCTION_RECLAIM` (n=51,215, PF 1.23) is
   the rest. Nothing else has meaningful n — klines can't reconstruct the
   order-flow families. Note SR_FLIP's **long side is statically disabled live**.
4. **Mild decay trend:** 2.39 → 2.00 → 1.59 → 1.28 → 1.56 → 1.73 → 1.11 (Jan and
   Jul are partial months — don't over-read).
5. **Fidelity, per the script's own header:** klines-only entries, `Backtester`
   ≠ live scanner, so **absolute PnL is not truth**. Trust the relative ranking.

### Part 5 — `@SAREXIT` forward-shadow arm shipped DARK (owner-directed)

Owner picked the doctrine-mandated next step: forward-measure the verdict on
real live signals before proposing anything. New `src/sar_exit_shadow.py` stamps
a counterfactual **pair** per post-scoring candidate, into its own ledger:

- `SETUP@SARBASE` — the live evaluator geometry (entry / SL / TP1), static
- `SETUP@SAREXIT` — the same entry, exited by a trailing 15m Parabolic SAR

**Both arms are measured over the identical 192-bar (48h) window**, which is
Part 4's caveat 2 fixed at the root: the control arm gets exactly the window the
trail gets, so the comparison the owner has to sign off on is honest from the
first record. Both divide by the **live** `sl_distance`, so the trail is scored
in the risk units of the stop it would replace.

The SAR math is a **verbatim port** of the bake-off script's `parabolic_sar` /
trail walk, and `tests/test_sar_exit_shadow.py` locks the two implementations
together on shared fixtures (bit-identical series; exit price / MFE / hold to
1e-12). If they ever drift we would not know which number was lying, and the
entire value of this arm is that it confirms or kills one we already have.

Supporting change: `src/suppression_audit.py` grew a **method-agnostic**
trailing-exit concept — an `exit_model` field (defaulted, so every persisted
record keeps its semantics), a pluggable `trail_classifier` hook, and a
continuous-R branch in `candidate_outcome`. No SAR knowledge lives in the
generic module; the next trailing method plugs into the same seam.

**DARK by default** (`SAR_EXIT_SHADOW_ENABLED=false`, tunable
`sar_exit_shadow_enabled`), observe-only even when on: nothing in dispatch, the
FSM, or any live exit reads it, and the arms are registered in
`geometry_ab._VARIANT_SUFFIXES` so the allocator can never *recommend* a
measurement row. Cost: O(1) in-memory stamps on suppression/emission events
only, warm in-memory 15m candles, classification batched on the existing 5-min
audit loop — no network read, no Firestore read, nothing on a hot path.
Registered a feature-liveness probe (`sar_exit_shadow`) against the same
upstream that caught the geometry A/B's 25-hour silent death.

**Also removed a scaffold:** `Backtester.run(simulated_ai_score=…)` was threaded
through two signatures and consumed by nothing — its only consumer was the
`ai_insight=` kwarg that killed every backtest signal in Part 3. The old test
asserted only that the parameter was *accepted*, which an inert parameter always
is, so it passed throughout. Replaced with a regression test that fails if it
comes back.

### Part 6 — the arm made owner-readable (ops), and #781 diagnosed

**Owner switched `sar_exit_shadow_enabled` ON 2026-07-25.** Pairs are stamping;
first resolutions land ~48h later.

Ops surfaces shipped (360ce-ops #82 · #83 · #84):

- **`/sar-exit`** — the A/B summary: paired totals (total/avg/**median** R, win%,
  PF per arm), per-strategy rollup (leader only when BOTH arms clear n≥15), and
  the paired-trade table.
- **`/signals/sar`** — the arm as a *signal feed* under the Signals tab. A SAR
  trade has **no TP and no SL** — the trail is its only exit — so those columns
  don't exist; it's entry / closed-at / status / held / R / vs-live. Statuses:
  RUNNING (inside its 48h window), CLOSED_TRAIL, CLOSED_WINDOW, NO_DATA.
- **Source filter** — All / Emitted to live / Gate-suppressed, backed by a new
  `provenance` field recorded at the stamp (360-v2 #786). The arm stamps from
  *both* scanner call sites, so the ledger mixes signals that reached
  subscribers with candidates a gate killed; only the **emitted** half can
  justify changing what users receive. Pre-#786 records read UNKNOWN and match
  neither filter — counting them as emitted would inflate the one number an
  adoption decision reads.
- Ops-side fix: `MEASUREMENT_SUFFIXES` had drifted to `@FIXED`/`@ATR` only while
  the engine wrote `@TUNED`/`@DSV2`/`@GOV` for over a week, so those arms were
  counted in the Strategy Lab's **per-strategy rollup as strategies** —
  double-counting their own candidates.

### Issue #781 — diagnosed on real data; the three alerts have three answers

The truth report settles what six days of paging could not:

| Alert | Measured | Verdict |
|---|---|---|
| `range_fade_emission` | RANGE_FADE suppressed counterfactuals **−0.98R at 3% win, n=1804** | **Gates are RIGHT.** Emitting would lose money. False alarm. |
| `mean_revert_emission` | MEAN_REVERT **+0.60R at 80% win, n=2999**, 83/83 killed pre-scoring by `execution:overextended` (cap 5.0 ATR) | **Gating is COSTING us** — real, and money-path |
| `edge_reconciliation` | MOVER_TREND_PULLBACK realized−counterfactual **−0.38R** (bound 0.3) | **Working correctly** — it is measuring a real optimism bias in counterfactuals |

The third calibrates the second: counterfactuals run ~0.38R optimistic where we
have both sides, so MEAN_REVERT's +0.60R is realistically nearer +0.2R. Still
positive, much less dramatic — **do not act on the gross number.**

**Shipped (off money-path):**

- **Edge-aware emission probes** (`feature_liveness.gated_path_verdict` +
  `strategy_edge.pooled_suppressed_edge`). A fully-gated path is a fault only
  when its blocked candidates measure *positive*; measured-negative reports
  healthy **with the number visible**, unmeasured still pages. This is a
  reclassification, not a mute — the detection is unchanged, so the Hard Limit
  holds, and a page now means money on the table.
- **Gate rejections by setup** (`suppression_audit.gate_metrics_by_setup` + a
  truth-report section). The per-gate table pools every setup into one row, so
  *"this path emits nothing — which gate is stopping it?"* was unanswerable
  even though gate and setup were both on every stamped record. #781 said
  "check gate rejections" for days with no view that could.
- **SAR exit A/B section in the truth report** — the arm now appears alongside
  its siblings instead of only in its own ops tab.

**NOT done — owner-sign-off, money-path:** raising MEAN_REVERT's
`execution:overextended` cap (5.0 ATR) or disabling RANGE_FADE outright. Both
change which signals emit on a live app. Evidence is above; decision is the
owner's.

### Part 7 — doctrine corrected (owner, 2026-07-25): two false premises removed

**1. Telegram is NOT banned in India. It works.**

That claim was load-bearing in three places and each one used it as a *reason*:
ops owning the control plane, B1 (in-app feed primary), and B16 (Telegram payment
path retired). **Owner reaffirmed all three rules — only the false premise is
removed.** They now stand as product decisions rather than as consequences of a
ban. Corrected in `OWNER_BRIEF.md` (§2.2, B1, B16) and `360ce-ops/CLAUDE.md`.

Historical session entries in this file still contain the old claim (e.g. the
S-?? per-user re-enable note around L1466). **Those are left as written** —
rewriting a past session's record would falsify the log. `OWNER_BRIEF.md` is read
*before* this file in the session protocol, so the correction lands first.

**2. "Dark" means invisible to USERS, live to the OWNER — not switched off.**

The old wording said money-path changes ship "default-OFF", and I read that
literally on the SAR exit arm: shipped it OFF, so it stamped nothing, the ops
panel was empty, and the owner had to enable it and then ask where to look. That
is the wrong reading and it cost a day of measurement.

There are **two flags**, not one:

| Flag | Default | Controls |
|---|---|---|
| **Measurement** | **ON** | Stamping, shadow arms, counterfactuals, ops panels — runs for real on ship, fully visible in ops |
| **User-visible effect** | **OFF** | What subscribers see / what the money path does — owner sign-off to activate |

Corollary now in both briefs: **dark work must ship with its ops surface.** A
dark change isn't finished until there's a panel, table, or truth-report section
the owner can read the same day. "Measured but nowhere to look" is unfinished.

**Also corrected in the same pass (owner: "fix all of them"):**

| Was | Now | Evidence |
|---|---|---|
| "The 15 Signal Evaluators" | **19** (17 live; ORB + CLS disabled) | 19 `_evaluate_*` in `scalp.py`, 19 `EVAL::*` rows in the truth report. MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, MEAN_REVERT and RANGE_FADE had been generating for weeks with no table row. |
| §3.9 `invalidation_mode` "engine default: tight" | **loose** | `INVALIDATION_MODE_DEFAULT="loose"`; B17 and Profile D already said loose — the brief contradicted itself |
| "release 266 … 14 installs at 2026-06-30" | release 282+ as of 2026-07-16 | matched to CLAUDE.md; stale install count removed rather than guessed |
| §5.1 agent "in design — 2026-06-03" | **LIVE** | it is a running container in 360ce-ops and filed #781 |
| Part V ops "read-only consumer" | **control plane since 2026-06-20** | kill switch / mode flips / manual close all ship |
| §3.6 tiers → "Paid channel" | in-app feed + Telegram mirror | contradicted B1/B16 — signals are free, the paywall is automation |
| B9 "must post Telegram notification" | no silent disappearances, app-primary | the rule is the honesty, not the channel |
| B18 kill switch "<5s from Telegram" | operated from the ops control plane | owner: control is ops-only for the audit trail; alerting may use both |

**Owner rulings recorded:** the **app is the primary surface for users**, Telegram is a
mirror; **Telegram's wider role is a dedicated future session** — do not expand it as a
side-effect of other work. Control is ops-only; alerting may go to FCM *and* Telegram.

**Still open after this pass:** `§2.1` still says "360 Crypto Eye is the
signal-engine brand (Telegram channel, technical identity)" and `B15` still says
"Telegram channel never renames" — both fine as brand statements, but they are the
kind of Telegram-role wording the owner has reserved for a dedicated session. Left
alone deliberately.

### Open / next

1. ~~Owner: switch the arm on~~ — **done 2026-07-25**, stamping now.
2. **Read the pair once both arms clear n≥15 per cell** via
   `summarize_sar_exit`; thin arms report MEASURING, never a winner. Activation
   remains a separate dark-first, owner-signed change.
3. **Promotion criterion still undecided** (Part 4 caveat 1) — deliberately, to
   be settled on this arm's forward data.
4. **`#781` — diagnosed and the tooling fixed (see Part 6).** The remaining
   piece is an owner call: MEAN_REVERT's `execution:overextended` cap, and
   whether RANGE_FADE (−0.98R, 3% win) should be disabled rather than left to
   be gated 100% of the time. Both are money-path.
5. **The emitted-vs-suppressed split may be thin.** Gates kill most candidates,
   so the emitted subset of the SAR arm will grow far slower than the pooled
   one. If it can't reach n≥15 per strategy in reasonable time, read the pooled
   number as primary and treat the emitted split as a directional check —
   and say so explicitly rather than quietly pooling them.

---

## 🟢 SESSION 77 2026-07-23 — Truth-report deep-read → the emission bottleneck attacked dark-first (W5 slice 1 + staleness V2 + MTP perfect-entry study)

**Owner ask:** read the truth report + strategy lab — "what's still missing,
we're still negative-only" → then "continue with 1 and 2, look at perfect
entry for MTP, and what happened to the regular-pair paths."

### Diagnosis (the 4 findings, from the 2026-07-23 truth report)

1. **The measured edge never emits.** 54,631 measured outcomes, 14 realized
   trades.  MEAN_REVERT (77% win, +0.52R, n=2153) and RANGE_FADE's +4.10R
   cell emitted ZERO (liveness alerts sustained).  The emission policy's only
   lever was a 5-pt confidence-floor relax — it had no authority over the
   dispatch gates that actually killed the candidates.
2. **The two biggest suppressors are measured-negative and untuned:**
   `dispatch_staleness` (flat 0.5% drift, 1225 kills, **49.7% would-win**,
   EV −0.19R, 318R missed) and `level_still_in_play` (989 kills, 40.7%
   would-win).  The staleness gate adversely selects: it passes candidates
   where price sat still and kills the movers.
3. **Live exits ≠ measured exits.** Counterfactuals free-run 1h to TP1; live
   trades get invalidation-killed at median ~30 min, 0% TP rate, 0% pre-TP
   (PRE_TP_ENABLED=false).  The `edge_reconciliation` probe pages exactly
   this: MTP realized −0.37R below counterfactual.  MTP enters at the CLOSE
   of the reclaim bar — a full 15m bar off the pullback low.
4. **Regular-pair paths aren't broken — they're gate-starved** (see below).

### Shipped (all DARK-FIRST per production doctrine; measurement ON, live flags OFF)

- **`src/staleness_v2.py` (new)** — geometry-aware staleness: drift bounded
  per direction as a fraction of the candidate's own entry→SL / entry→TP1
  distances (`DISPATCH_STALENESS_V2_*`).  V1 keeps deciding; every
  V1-block/V2-pass disagreement stamps an **`X@DSV2`** arm with entry
  re-anchored at dispatch-time price (the W4 honest-fill note).
  `DISPATCH_STALENESS_V2_LIVE` + ops tunables flip it after sign-off.
- **W5 slice 1 — `context_emission_policy.gate_override`**: a STRONG cell
  (n≥floor, positive edge) may override `dispatch_staleness` /
  `level_still_in_play` (**`OVERRIDABLE_GATES` — safety gates structurally
  excluded, test-pinned**).  Shadow **`X@GOV`** rescue arms now; live behind
  `CONTEXT_EMISSION_GATE_OVERRIDE_LIVE` after sign-off.
- **MTP perfect-entry study — `MOVER_TREND_PULLBACK@TUNED`**: limit rests at
  the fast MA the pullback tagged (SMA-7 15m), live SL/TP1 kept.  Honest by
  construction: new **fill-aware limit classifier** in `suppression_audit`
  (`classify_limit_record`, candle-walk; `WOULD_NOT_FILL` = 0R — the cost of
  patience is measured, not assumed).
- **Truth report**: new "Recipe & rescue shadow arms (@TUNED/@DSV2/@GOV)"
  section = the sign-off evidence table.  **Liveness probes**
  `staleness_v2_shadow` + `gate_override_shadow` page if a measurement
  flat-lines.  Full suite 7023 passed; ruff clean; mypy at/below baseline.

### Regular-pair paths autopsy (owner question answered)

They generate fine (SR_FLIP 3015, MEAN_REVERT 1826, RANGE_FADE 1556, LSR
2356, DIV 1909, FAR 1653 in-window) — they die in the gate stack:
regime/execution pre-gates → confidence floor → then the two negative-EV
dispatch gates above.  Plus three deliberate switch-offs: ORB
(`feature_disabled`), CLS (merged into LSR), SR_FLIP longs
(`long_disabled`).  MTP dominates the *realized* book because mover-run
candidates clear momentum/confidence gates more often — not because regular
paths are broken.  The two shipped fixes target exactly the stage where
regular-pair paths die.

### Open / next (in order)

- **Data window**: let @DSV2 / @GOV / MTP@TUNED rows accumulate (truth-report
  "Recipe & rescue shadow arms" + Strategy Lab), then owner sign-off to flip
  `dispatch_staleness_v2_live` / `context_emission_gate_override_live`.
- **Exit-model gap (finding 3)**: invalidation audit has zero classified
  records this window — needs wiring verified; then either mirror
  invalidation in counterfactuals or kill the PREMATURE kills.  **PRE_TP
  decision is owner's** (doctrine says it's the banking path; it is OFF).
- W3 explicit retirement, W6 regime/universe focus, W7 latency — unchanged,
  pending validated net window.

---

## 🟢 SESSION 76 2026-07-22 — Autonomous system audit → cost-aware R made LIVE (owner directive); W1–W4 chain now net-steering (360-v2 #770 + #771, merged)

**Owner ask:** full audit of the autonomous system — what's working, gaps,
bottlenecks — because *"we're doing all this and still in negative edge only."*
Then: *"fix all, full documentation"* → *"make everything live, no darks."*

### Root cause found (the whole audit in one line)

Every recorded R — counterfactual (`suppression_audit.candidate_outcome`), shadow,
AND realized (`trade_monitor.py:610`) — was measured **GROSS**: wins booked at full
R-to-TP1, losses at exactly −1.0R, **no fees/funding/slippage**. `strategy_edge`
only *labelled* its fields "net-of-fees" without applying any. The gross edge
harvested (~+0.08R) is **smaller than the per-trade cost drag never subtracted
(~0.15–0.25R)** → net-negative while the dashboards read positive. And the emission
policy that would harvest winners sat effectively idle because the edge it steered
on was a cost-free fantasy.

Full design-of-record: **`docs/AUTONOMOUS_SYSTEM_AUDIT_AND_REMEDIATION.md`** (W1–W7,
sequenced, acceptance criteria).

### Shipped LIVE (owner directed live activation, overriding dark-first — briefed 3×)

- **W1 (#770) — cost-aware R.** New `src/trade_costs.py` (pure, leverage-independent,
  fail-toward-gross `net_r`). Wired into both seams: counterfactual (`suppression_audit`)
  + realized (`trade_monitor`). `gross_r_multiple` carried alongside net.
  `EDGE_COST_MODEL_ENABLED` flipped **default true** → the already-live emission
  controller now steers on **net** R. Reuses/extends the fee constants; new
  `EDGE_TAKER_FEE_PCT_ROUND_TRIP=0.10 / SLIPPAGE_PCT_PER_SIDE=0.02 / FUNDING_PCT_ESTIMATE=0.01`.
- **W2 (#771) — reconciliation + optimism-tax watchdog.** `net_r_multiple` computed
  **always** (flag-independent) through the edge store (matrix `avg_net_r` +
  `net_r_by_source`). `strategy_edge.reconcile_matrix()` → per-strategy REALIZED
  (emitted) vs COUNTERFACTUAL (suppressed) net-R + delta, surfaced in the truth
  report. New `edge_reconciliation` liveness probe pages when realized net-R diverges
  from counterfactual net-R beyond `EDGE_RECONCILIATION_ALERT_DELTA_R` (0.30) on
  adequate sample — validates the cost constants in-flight.
- **W3/W4 needed no new flip:** `CONTEXT_EMISSION_LIVE` + `CONTEXT_EMISSION_POLICY_ENABLED`
  were already `true`; the emission policy (suppress NEGATIVE / relax STRONG-POSITIVE)
  and the emission controller were already live. Making the cost model live
  re-points **both** at net edge automatically.

### Open / next

- **DATA WINDOW (the real gate now):** the per-cell rolling window (50) is gross until
  new net outcomes replace it. Verdicts (KEEP/DROP, STRONG/NEGATIVE) become net-honest
  as data rolls — do NOT judge or retire strategies until a fresh net window
  accumulates. Watch the truth-report reconciliation + `cost_drag_r` and the
  `edge_reconciliation` probe. **The cost constants are estimates** — the reconciliation
  is what validates/tunes them.
- **W3 explicit retirement** (retire confirmed net-negative strategies), **W5** (broaden
  the controller's action space), **W6** (regime/universe focus), **W7** (latency) —
  all pending the validated net window; acting sooner would steer on gross.
- Guardrails intact throughout: blast-radius caps, kill switch (`emission_controller_enabled`),
  the new watchdog, policy sample floors (Wilson-LB + `CONTEXT_EMISSION_MIN_SAMPLES=30`).

---

## 🟢 SESSION 75 2026-07-21 — Surface subscription + referral benefits across the app (lumin-app #135, merged)

**Owner ask:** the invite/subscription benefits were "nowhere" in the app —
show them everywhere to push and encourage users to subscribe and invite.

**Problem:** the B16 Assist/Auto value prop and the Session-74 referral deal
(7 free Auto days + 50% commission per join; referee 50% off) were only
reachable via Menu → Settings. A free user in the feed never saw why to
subscribe or invite.

### Shipped — lumin-app (`lib/shared/widgets/upsell_banners.dart`, new)

- **`UpgradeBanner`** — tier-aware subscription upsell on Pulse, Signals, Trade
  and top of Menu. Free users hear the whole ladder; Assist users are nudged to
  Auto; **hides itself at Auto+** (listens on `tierRevision`, vanishes the instant
  a purchase lands).
- **`InviteBanner`** — renders the standing reward deal from `GET /api/referral/me`,
  only promising rewards while `rewards_enabled` (falls back to a plain invite
  otherwise). On Pulse and top of Menu.
- Shared `openPaywall`/`openReferralPage` helpers (Play vs web by channel);
  dismissible per session; pure-card / scope-wrapper split so the presentational
  cards are widget-tested (9 cases, mirrors `CurrentPlanCard`). Menu Invite-row
  subtitle now hints at the reward.

**Scope:** off-money-path UI only — no engine/entitlement/gating logic touched;
banners render engine state and gate nothing. Shipped normally (not dark-first).
CI green (APK+`flutter test`, web build); squash-merged to `main`.

---

## 🟢 SESSION 74 2026-07-21 — Referral programme Phase 2: rewards, referee discount, 50% commission (all four repos, branch `claude/referral-program-incentives-kg50am`)

**Owner ask:** complete the invite screen's "rewards are coming soon" — 7 days of
full Auto per successful invitation, the invited person gets 50% off both plans one
time, and for people promoting full-time, 50% commission per successful paid user.
Decisions locked via AskUserQuestion: reward triggers **on join** (growth > revenue);
commission runs for the referee's **first 3 billing periods** (cross-channel).

### Shipped — engine (360-v2)

- **`src/api/referral_rewards.py`** (new) — reward grants, commission accrual, and
  **entitlement composition**: the user row stays the single entitlement truth, but
  every `aset_tier` write site (Play verify, RTDN, web IPN, expiry downgrade) now
  composes Play state ⊕ the reward ledger, so a banked reward survives Play rewrites
  AND a paying subscriber is never zeroed when a stacked reward lapses (RTDN revoke +
  `_maybe_downgrade_expired` re-resolve from stored `play_purchases` snapshots
  instead of writing blanket free).
- **Ledgers** in `user_overrides.py`: `user_reward_grants` (7d Auto per join,
  sequential stacking, 90d cap, DB-level one-shot per referee),
  `referral_commissions` (idempotent per `(purchase_token, period_expiry)` — RTDN
  redeliveries never double-credit), `user_referral_redemptions.converted_at`
  (migration; NULL = referee still holds the one-time 50% discount).
- **Commission = 50% of what the referee ACTUALLY paid**: Play uses
  `REFERRAL_COMMISSION_PRICES` (halved when the purchase used the `referral50`
  offer — `billing_play.py` now parses `offerDetails.offerId`); the web rail passes
  the confirmed USD amount from the IPN. Unpriced product → accrues nothing.
- **Web rail (`billing_web.py`)**: eligible referee's checkout is priced at 50% off
  server-side, the discount flag rides the HMAC-echoed `order_id` so the webhook's
  amount defence checks the right price; grant path runs the same hooks/composition.
- **API**: `/api/referral/me` extended (reward + commission + discount state, all
  fields defaulted for old clients); `/api/referral/claim` banks the reward and
  returns `discount_eligible`; owner-gated `GET /api/referral/admin/commissions` +
  `POST .../mark-paid` for the manual-payout ledger.
- **Config**: `REFERRAL_REWARDS_ENABLED` (default **true** — operational kill
  switch mirroring `GOOGLE_PLAY_BILLING_ENABLED`; off stops NEW rewards, never
  confiscates banked time) + days/tier/cap/rate/periods/prices/offer knobs.
- **Tests**: 19 new in `test_referral_rewards.py` + endpoint tests in smoke + 4 web
  referral tests. Full suite 6958 passed; ruff clean; mypy 105 = baseline (no new).
- **`docs/REFERRAL_REWARDS.md`** — runbook incl. **OWNER ACTION: create the
  `referral50` developer-determined offer (50% off, 1 period) on BOTH base plans in
  Play Console**; payout runbook; anti-abuse posture.

### Shipped — app / ops / legal (same branch in each repo)

- **lumin-app**: referral page rewrite (reward hero, banked-days + active-until,
  paid-friends count, per-currency commission earned/paid, share copy sells the 50%
  off); paywall buys the `referral50` offer variant when the engine says eligible
  (pure `pickPlanOffer` helper + `in_app_purchase_android` direct dep), 50%-OFF pill
  + base-price strikethrough; web paywall shows the engine-priced discount; signup
  referral card promises the discount. All rendered from engine truth
  (`rewards_enabled` gates the copy).
- **360ce-ops**: `/referrals` owner panel — accrued/paid totals by currency,
  commission table with referrer phone, checkbox mark-paid (PRG + confirm +
  audited), engine re-read after write.
- **lumin-legal**: `terms.md` referral-programme section **proposed on the branch —
  owner-sign-off to merge** (mechanics, 3-period cap, anti-abuse forfeiture, manual
  payouts, programme may change, rewards ≠ investment returns).

### Open

- Owner: create the two `referral50` Play offers (runbook above), merge the legal
  terms, then merge the four branch PRs (engine first, app second).
- Payout cadence is owner-manual; consider a monthly reminder Routine once volume
  appears.

## 🟢 SESSION 73 2026-07-20 — Web billing Phase 3: the PWA crypto (NOWPayments) subscription rail — built, merged, and taken LIVE (paired PRs: 360-v2 #757/#759 + lumin-app #133, branch `claude/web-app-implementation-xzkbzo`)

**Owner ask:** finish the web app (PWA) and give it its own way to sell the paid
tiers — Play/Apple billing is store-bound, the website is neither. Owner is **solo,
no business entity**, so card processors (Razorpay/Stripe) that need merchant KYC
were deferred; **crypto (NOWPayments) + manual** are the launch rails.

### Shipped — engine (360-v2, PRs #757 + #759)

- **`src/api/billing_web.py`** — the crypto rail, selling the **existing**
  `assist`/`auto` tiers through the one entitlement path (`UserStore.aset_tier`) —
  no new tiers, no parallel store (design §2).
  - `GET /api/billing/web/config` (public; region-aware rails + prices),
  - `POST /api/billing/web/checkout` (authed; engine creates the NOWPayments invoice
    server-side — **API key never leaves the engine, engine sets the price**, client
    only names a tier),
  - `POST /api/billing/web/crypto/webhook` (NOWPayments IPN: **HMAC-SHA512 over
    sorted JSON**, deduped on `payment_id`, amount-checked, then `aset_tier`).
  - Verifier confirmed against NOWPayments' **official reference** (sorted-key JSON,
    compact separators, `x-nowpayments-sig`). Renewal stacks from later of (now,
    expiry). 27 tests.
- **Dark-flag-first:** `WEB_BILLING_ENABLED` / `WEB_BILLING_CRYPTO_ENABLED` (default
  false), `WEB_BILLING_TEST_MODE` (sandbox vs live). Config in `config/__init__.py`.
- **`deploy.yml`** injects `NOWPAYMENTS_API_KEY` + `NOWPAYMENTS_IPN_SECRET` from
  GitHub secrets into the VPS `.env` (like Binance/OpenAI) — #759. Also hardened
  provider-error surfacing (httpx errors + provider status → clean 502, not a masked
  "Failed to fetch").
- **`docs/WEB_BILLING_DESIGN.md`** (design of record) + **`docs/WEB_BILLING_ACTIVATION.md`**
  (enable/disable, secret-injection flow, the 4 verify checks, the real-payment test).

### Shipped — app (lumin-app #133)

- `lib/data/web_billing_service.dart` + `web_paywall_page.dart` + repository models
  (`WebBillingConfig/Rail/TierPrice/WebCheckout`). Web-only: Settings→Subscription
  branches on `kDistribution == web` → crypto/manual paywall; native keeps Play
  Billing (Play anti-steering honoured at compile time). Polls the engine for the
  webhook-granted tier after checkout. 22 tests.

### Live state (as of session end)

- **LIVE in production**: `WEB_BILLING_ENABLED=true`, `CRYPTO_ENABLED=true`,
  `TEST_MODE=false`. Pricing **$15 assist / $25 auto, USDT, monthly, everywhere**.
- Verified without a real payment: `/config` live, invoice creation returns a real
  NOWPayments checkout (owner saw the $15 USDT page), webhook armed (`401`),
  signature algorithm matches vendor docs.
- **Incident caught & fixed:** the `NOWPAYMENTS_IPN_SECRET` GitHub secret had a
  **stray trailing `w`** (len 33, ended `28rw` vs the dashboard's `M28r`). Checks
  #1–#3 all passed but a real payment would have failed signature verification →
  money taken, no grant. Fixed by re-copying the secret (regenerated, now len 32) +
  redeploy. Lesson in the activation runbook: always run the `first4/last4/len`
  value-match check, copy secrets with the dashboard button.

### NOT done / open

- **Real end-to-end payment test** — owner had no funds at session end. The one
  remaining 100% confirmation; will print `web billing GRANT: … tier=assist`.
- **Razorpay/Stripe rails** — designed, dark, entity-gated (need a merchant entity
  + provider category clearance). Reserved flags exist.
- **Legal:** `lumin-legal` `terms.md` still describes Play billing only — needs a
  crypto/manual billing + manual-renewal update (owner-sign-off) before wide launch.

---

## 🟢 SESSION 72b 2026-07-20 — Layer G: autonomous emission controller (closed-loop policy tuner), branch `claude/autonomous-best-signal-system-qv49lv` (OWNER-SIGN-OFF, money-path)

**Owner directive:** "we are making an autonomous system, everything needs to adjust
dynamically based on data — we can't look daily and adjust" → then: "I don't confirm
anything, everything is autonomous but dark-first, first make it live autonomously."

**The gap it closes:** the suppression-audit gate verdicts (KEEP/TUNE/DROP) + edge
matrix are measured every cycle but nothing acted on them — where the edge matrix sat
before PR 752. On fresh 2026-07-20 data the loop is provably needed:
`context_floor:MOVER_TREND_PULLBACK` DROP −0.38R (n=1447) and `:SR_FLIP_RETEST` DROP
−0.37R (n=718) are killing winners, while QCB's +2.21R cell sits at n=29, one under the
n≥30 relax floor, emitting ~nothing.

**Layer G** consumes those verdicts and moves the `context_emission_policy` params
**per strategy**, inside a bounded envelope, with **no human in the loop** — the data
promotes each change, not a person:
- `src/emission_controller.py` — pure decision core (11 tests): only two per-strategy
  knobs (suppress_negative toggle, min_samples floor), hard-clamped; nothing promotes
  on first sight (boot-grace + K-cycle stability + EV-magnitude bar on the loosen
  direction + min gate sample); blast-radius capped/cycle; promotion clears history so
  a reversal needs fresh opposite evidence; symmetric auto-revert.
- `src/emission_controller_store.py` — singleton, JSON-persisted (not Firestore),
  **O(1) in-memory hot-path read** (`override_for`) since the scanner calls the policy
  per candidate (Cost Discipline). 8 integration tests.
- `context_emission_policy` — resolves suppress/min_samples per-strategy (override when
  set, global otherwise); global behaviour unchanged with no overrides. Gated by
  `emission_controller_enabled`.
- Loop in `main` (30-min cadence, off-thread, fail-open) + liveness probe
  `emission_controller` + 7 envelope tunables (Control → Signal gating) + monitor-logs
  surfacing (`analysis/emission_controller.json`).

**Rollout (per directive):** ships `emission_controller_enabled=ON`. Dark period is
**self-administered** — boot-grace observes only, then each candidate self-promotes when
its evidence clears the bar. No `_live` confirm-flag; owner owns the envelope + the kill
(`emission_controller_enabled=OFF` → static). Design: `docs/PLAN_AUTONOMOUS_EMISSION_CONTROLLER.md`.

**Verify:** 42 Layer-G/policy/bundle tests green; full cycle runs end-to-end against the
real suppression/edge stores; ruff clean; no new mypy. **OWNER-SIGN-OFF item** (new
money-path control loop) → review + merge, not auto-merge.

### NEXT
1. Owner: review + merge the Layer-G PR (money-path, no auto-merge). After deploy, watch
   `analysis/emission_controller.json` on monitor-logs — first self-promotions expected:
   MTP + SR_FLIP suppress→off, QCB min_samples 30→25.
2. Carried: retire the bespoke RANGE_FADE gate into `context_emission_policy`; the ops
   `/api/v1/analysis-bundle` could add the controller ledger (read-only follow-up).

---

## 🟢 SESSION 72 2026-07-20 — Analysis "mediator": get the signal data to a CTE session without manual CSV upload (paired PRs: 360-v2 + 360ce-ops, branch `claude/autonomous-best-signal-system-qv49lv`)

**Owner ask:** "can we build some mediator to get the data to you to analyse from
ops or engine" — stop hand-exporting the Strategy Lab / Profit / Performance CSVs
and uploading them. Owner picked **both** mechanisms.

### Shipped — A: secretless git dead-drop (360-v2, off money-path)

- **`src/analysis_bundle.py`** (new, pure): flattens `StrategyEdgeStore.matrix()`
  to the full per-cell matrix (the summarised `truth_snapshot.json` only carries
  per-strategy best/worst cells), aggregates per-setup performance **mirroring ops
  `performance.py:_classify_outcome` verbatim** (PROFIT_LOCKED counts as win), CSV
  writer, and a `bundle.json` index with a gate-verdict + strongest/weakest-cell
  rollup. `tests/test_analysis_bundle.py` (10).
- **`scripts/build_truth_report.py`**: new `--analysis-dir` / `--git-sha`; emits
  `analysis/{strategy_lab_matrix,performance_setup}.{json,csv}`,
  `analysis/suppression_audit.json`, `analysis/bundle.json`.
- **`.github/workflows/vps-monitor.yml`**: writes the analysis dir, validates it,
  preserves it across the monitor-logs checkout, and `git add`s it. So any session
  reads `git show origin/monitor-logs:monitor/report/analysis/…` — **no token, no
  live network**. On-demand freshness via the existing `workflow_dispatch`.
- Tunables are Firestore-persisted (no file to `cat`), so A deliberately omits live
  tunables — B is their source. Not a scaffold: A is a complete, consumed artefact set.

### Shipped — B: live on-demand bundle (360ce-ops, token-gated)

- **`GET /api/v1/analysis-bundle`** (`app/routes/api_v1.py`): one token-gated call
  composing strategy_lab (`_build_view`), profit held-to-stop replay (ops-only —
  the reason B exists alongside A), performance aggregate, invalidations (capped),
  live tunables, truth snapshot, alerts. Every section isolated via `_section(factory)`
  → a failing source degrades to `{"error": …}` for that key, never 500s the bundle;
  row/record caps bound the payload. Tests +4 (24 total in `test_api_v1.py`).

### Verification

- Engine: `test_analysis_bundle.py` 10/10; ruff clean on `src/`; mypy 0 new; end-to-end
  script smoke (fixtures → correct CSV/JSON artefacts). Unrelated collection errors
  (rust signing-service pyo3) are pre-existing env, not this change.
- Ops: `test_api_v1.py` 24/24; ruff clean. The 65 full-suite failures are the S71
  pre-existing Starlette/Jinja version-mismatch (template renders), untouched here —
  zero involve `api_v1`/`analysis`.

### NEXT

1. Owner: both PRs are off money-path → normal review/merge. After the engine PR
   deploys, trigger `vps-monitor` (workflow_dispatch) to seed the first analysis drop;
   CTE reads it from `monitor-logs`. Provision an ops app-token for B when live pulls wanted.
2. Carried from S71: merge #755 then #69 (owner Close button); retire the bespoke
   RANGE_FADE gate into `context_emission_policy`; flip `context_emission_cohort_aware`
   ON once cohort cells populate.

---

## 🟢 SESSION 71 2026-07-19 — Ops panel overhaul (grouped IA, readable Truth, CSV+JSON everywhere, modern restyle) + owner "Close" button for stuck signals (paired PRs: 360ce-ops #69 + 360-v2 #755)

**Owner ask (Truth PDF + follow-ups):** the Truth report is unreadable; make data
downloadable (Strategy Lab, Profit, anything) flexible for both owner + CTE; look at
every tab and upgrade to user-friendly, merging tabs that show the same data; make the
control panel rich/minimal/modern, best UI overall; and **add a manual Close button for
signals — "some might not close, we need to close them."**

### Shipped — ops UX (360ce-ops #69, one branch, 3 commits)

- **Full IA redesign (owner picked this over light-touch):** 16 flat tabs → 6 groups
  with a secondary sub-nav (Overview / Signals / Performance / Autonomy / Control /
  Diagnostics), all in `base.html` via a NAV table keyed off each route's existing
  `active` token (only `users.py` needed a distinct token). The Performance group
  absorbs the four overlapping outcome-analytics tabs (Profit / Performance / Raw Edge /
  Invalidations). **Every URL unchanged** — presentational merge, nothing 404s.
- **Readable Truth report** (`routes/truth.py._shape` + `truth.html`): Executive-summary
  cards, Feature-liveness green/red table, Confidence-gate per-setup kept-vs-filtered
  table; every other section collapsed into an expandable raw-JSON block + jump index.
  Raw md/JSON downloads kept.
- **CSV + JSON on every data view** (owner picked both formats): JSON exports added
  alongside the existing CSVs (Profit/Performance/Raw Edge/Invalidations); **Strategy
  Lab got both** (edge-matrix CSV + full-view JSON) — it had none. Data tab is now a
  central "Analysis views" export directory.
- **Modern restyle** (`static/style.css` rewritten as one design system — elevation
  ramp, richer palette, shadows, pill nav/badges, transitions, tabular figures, focus
  rings; all class names preserved; the two conflicting `.badge` defs consolidated) +
  **Control page** at-a-glance status strip + responsive card grid.
- Verified: **380 ops tests pass** + full render smoke-test. (The 65 initial "failures"
  were a pre-existing Starlette/Jinja version mismatch in the dev container, cleared by
  installing the repo's pinned versions — NOT the change; two assertions updated for the
  renamed Data heading + Positions sub-nav placement.)

### Shipped — owner Close button (360-v2 #755, engine, OWNER-SIGN-OFF)

- **`TradeMonitor.close_signal_manual(signal_id)`** reuses the EXACT expiry-close
  primitives (realise-or-ZERO PnL for never-filled, record outcome, flatten broker
  position, remove from active book) — no new exit path. Idempotent (not_found), never
  raises. `CryptoSignalEngine.close_signal_admin` delegates.
- **`POST /api/admin/close-signal`** (`close_signal_route`, owner-gated, in `build_app`
  → both modes): single-process direct; **isolated mode rides the existing manual-command
  Redis bridge with a new `kind="close"`** (`ManualTakeConsumer._process_close` +
  `redis_engine.enqueue_close_signal`) — no new consumer, shares the take result key. No
  staleness gate (a close is safe at any age).
- **Ops side (in #69):** per-row "Close" button on ACTIVE signals →
  `POST /control/close-signal` (`engine_api.close_signal`) — owner-gated, audited
  (`close_signal`), PRG + confirm, session flash, open-redirect guarded, graceful while
  the engine endpoint is undeployed.
- Verified: `tests/test_manual_close_signal.py` (monitor close filled/never-filled/
  not-found + consumer close-kind routing + missing-id drop); ruff clean; mypy 105 =
  baseline (0 new). The isolated-smoke loop-teardown flake when async files run first is
  pre-existing (same with `test_expiry_no_fill.py`); natural order passes.

### NEXT

1. Owner: merge **#755 first** (owner-sign-off — touches the exit path), then/with **#69**
   (the Close button needs #755 deployed to function). Both off the emission money path.
2. After deploy: the Signals feed Close button flatts a stuck OPEN signal at the mark;
   watch the audit log (`close_signal`) + the signal leaving the active book.
3. Carried from S69/S70: retire the bespoke RANGE_FADE gate into `context_emission_policy`
   (behaviour-equivalent cleanup); flip `context_emission_cohort_aware` ON once cohort
   cells populate.

---

## 🟢 SESSION 70 2026-07-19 — The three emission follow-ups shipped LIVE + ops-controlled: dispatch_cooldown leak, MEAN_REVERT compat (#739), Phase-5 pair-cohorts (branch `claude/strategy-lab-signals-analysis-ntw48u`, 360-v2)

**Owner ask:** "fix all three and update docs" — the follow-ups flagged at the end of
S69 (dispatch_cooldown DROP leak, MEAN_REVERT compat-map, Phase-5 pair-cohorts). Branch
reset onto merged main (S69 #752 is in) per the merged-PR protocol; one PR for all three.

### Fix 1 — dispatch_cooldown DROP leak (gate audit: 235R missed, 100% would-win)

The per-(symbol, setup, direction) 30-min re-emission guard blocked profitable
re-entries on continuing moves. **Default lowered 1800→900s** and exposed as two live
ops tunables (`dispatch_cooldown_enabled`, `dispatch_cooldown_sec` 0–7200s, Control →
Signal gating). Helpers honour an explicit ops override, else fall back to the module
global — so the existing monkeypatch tests (`test_signal_lifecycle_bugs`) and the env
default both keep working. Still guards against 15s bit-identical spam.

### Fix 2 — MEAN_REVERT compat-map (#739 / S64 audit F1) — the 18th path can finally emit

Root cause confirmed: `REGIME_SETUP_COMPATIBILITY` listed MEAN_REVERT under CLEAN/DIRTY_
RANGE only, but its ≥2.5σ 15m trigger is exactly the spike that flips the classifier OUT
of range INTO **VOLATILE_UNSUITABLE / BREAKOUT_EXPANSION** — so it was gated pre-scoring
by its own trigger (0 emissions all window despite 172 detections). Added MEAN_REVERT to
both those states (additive — range homes intact). An exhaustion fade of a statistical
over-extension is a volatility event, home alongside LIQUIDATION_REVERSAL. Safety net:
the S69 context-emission policy auto-suppresses any cell where MEAN_REVERT's edge turns
NEGATIVE, and `mean_revert_live` stays the ops kill.

### Fix 3 — Phase-5 pair-cohort dimension (the honest "which pairs")

`src/pair_cohort.py`: liquidity cohort MAJOR/MIDCAP/ALTCOIN (reuses the engine's own
volume-tier thresholds + `PAIR_TIER_MAP`). Every candidate stamps `mc_pair_cohort`
(new `Signal` field, set in `_populate_signal_context`). The edge-store feeders
(`main._feed_edge` suppressed/shadow + `trade_monitor` emitted) **dual-write** a
cohort-refined cell (`context_key/COHORT`) **alongside** the base cell — additive, so the
live matrix the policy reads is **never fragmented** (per-symbol was too sparse for n≥15;
cohort keys don't match the base `context_key` so they never leak into the allocator).
`context_emission_cohort_aware` tunable (default **OFF**): when ON the policy reads the
cohort cell first with base fallback when thin. Wired end-to-end: `pair_cohort` threaded
through `suppression_audit.stamp_candidate` → `SuppressedCandidateRecord` (asdict) → the
feed `rec`, and `context_emission_policy.effective_floor(..., cohort=...)`.

### Verification

New `tests/test_pair_cohort.py` (7 — cohort classification, key composition, cohort-aware
prefer/fallback/off) + `tests/test_emission_followups.py` (7 — MEAN_REVERT compat both
states + range intact, cooldown/cohort tunables registered, lowered default). Ran green:
new 37 (incl. S69 policy/allocator), `test_signal_lifecycle_bugs` + suppression_audit +
mean_revert + signal_quality + scanner + range_fade **446 passed**. ruff clean; **mypy 105
= baseline (0 new)**. All three ship **LIVE with ops control** per the owner's standing
"no darks, controls in ops" directive; guardrails intact (cohort default OFF until cells
populate; MEAN_REVERT protected by the NEGATIVE-cell auto-suppress; cooldown reversible).

### NEXT

1. Owner: merge the PR (MEAN_REVERT compat = scoring-eligibility change → owner-sign-off;
   shipped live per directive, so review + merge). Deploy, then watch the Strategy Lab:
   MEAN_REVERT emission count leaving 0; `dispatch_cooldown` missed-R shrinking; cohort
   cells (`.../MAJOR` etc.) accumulating — flip `context_emission_cohort_aware` ON once
   they pass n≥15.
2. Remaining cleanup: retire the bespoke RANGE_FADE context gate into the unified
   `context_emission_policy` (behaviour-equivalent).

---

## 🟢 SESSION 69 2026-07-19 — Autonomous context-adaptive emission: the edge matrix now DRIVES the confidence floor (Layer C→emission consumer), LIVE by owner directive with full ops control + allocator upgrade (branch `claude/strategy-lab-signals-analysis-ntw48u`, 360-v2)

**Owner ask (2 PDFs: Profit tab + Strategy Lab, 2026-07-19):** analyse the data;
build a *fully autonomous best-signals emitting system that dynamically adjusts based
on the Strategy Lab data*; **"no darks — make it live but give controls in ops"**;
as CTE decide the open questions and open PRs; upgrade the strategy allocator for
best data results; update ACTIVE_CONTEXT clearly.

### The problem the data proved (Strategy Lab p97–99 + Profit 7d)

Emission is decided by ONE context-blind gate — `sig.confidence < min_conf` (65 +
component floors) at `scanner/__init__.py`. That floor was tuned around the
trend/mover setups, so **MTP + FAR = 62% of ~42 emissions** while every other path
detects hundreds–thousands of setups and ~99.8% die at the gate — *even in cells the
edge matrix measures STRONG* (QUIET_COMPRESSION_BREAK +2.21R OVERLAP/QUIET/COMPRESSED
emits **0/1055**; SR_FLIP_RETEST +1.29R LONDON/VOL_EXP/CASCADE emits **1/4790**;
LIQ_SWEEP +1.53R ASIA/ACCUM emits **1/1035**). The edge lives in `session×regime×path`
cells; the emission decision only read a global score. The whole Layer A–E Strategy
Lab (built S53, PR #720) measures this per context, and the allocator (Layer D)
computes the right answer — but it was `RECOMMENDATION_ONLY`, **consumed by nothing**.
Gate audit: `min_confidence` blocks 797R of winners (net −0.11), `dispatch_cooldown`
is a pure loss (235R missed, **100% would-win**, DROP).

### Shipped — the Layer-C → emission consumer (one PR, 360-v2)

- **`src/context_emission_policy.py`** (new, pure, O(1) in-memory — no hot-path I/O):
  turns the single global floor into a **per-(strategy × context) floor driven by the
  measured edge matrix**. STRONG cell → *relax* toward the quality anchor (emit the
  path's best setups where it wins); POSITIVE → relax half; **NEGATIVE → hard-suppress**
  (stay silent where it loses); cold/thin/FLAT → global floor unchanged (never guess).
  The two-sided generalisation of the S67 RANGE_FADE gate to *every* strategy. Control-arm
  alias (RANGE_FADE→SHADOW_RANGE_FADE, MEAN_REVERT→SHADOW_MEAN_REVERT) for thin graduated
  paths; own cell preferred when populated. Fail-open to the global floor on any edge-store
  error (recorded via `fail_open`, never silent).
- **Scanner emission-gate wiring:** computes the decision on every post-scoring candidate,
  stamps 4 monotonic counters + a `context_floor:<verdict>:<divergence>` suppression
  counter, logs `[CONTEXT_FLOOR_SHADOW]` on every relax/tighten divergence, and (live)
  applies it — relaxing the effective floor or suppressing NEGATIVE cells
  (`_stamp_suppressed(sig, "context_floor:<SETUP>")` so the gate audit prices it).
- **Allocator upgrade** (`strategy_allocator.py`): (1) **provenance weighting** — a cell
  proven only on suppressed/shadow counterfactuals is haircut ×0.85 vs an emitted-confirmed
  one (counterfactual MFE overstates a live exit); (2) **emission-concurrency envelope**
  (`ALLOCATOR_EMISSION_MAX_CONCURRENT=10`, separate from the capital cap of 6) + an
  `emission_activate` ranked list in the ops payload.

### LIVE + ops controls (owner directive — NOT dark)

Ships **applying**, default-ON, with EVERY knob a runtime tunable (ops Control → Signal
gating, applied ≤5s, no redeploy): `context_emission_enabled` (instant kill →
pre-policy behaviour), `context_emission_live` (apply vs measure-only), quality anchor
(50–75), STRONG/POSITIVE relax pts, min samples, suppress-NEGATIVE. **CTE decisions
(owner-delegated):** anchor **60** (STRONG→60, POSITIVE→62 off 65; n≥30 to relax;
sub-anchor never reaches paid), provenance haircut **×0.85**, emission cap **10**,
pair-cohort **deferred to Phase 5**. Conservative live defaults; owner widens/narrows
in ops as the matrix proves out.

**CTE flag on doctrine:** this overrides dark-flag-first for a money-path (emission)
change — subscribers see the new set immediately, no shadow window. Accepted because
the owner directed it, it touches **emission only** (no execution/sizing/blast-radius —
no capital-safety limit relaxed), the safety envelope stays enforced in the math, and
it's instantly reversible from ops. The relax side (new 60–64 signals in STRONG cells)
is the only subscriber-visible change; bounded by anchor + n≥30.

### Verification

New `tests/test_context_emission_policy.py` (18 — truth table, anchor clamp, control-arm
alias, thin/cold, divergence classifier, store-error fail-open) + allocator tests
(+3: provenance ranking, emission set, payload). **Ran green:** policy+allocator 30,
range_fade/mean_revert/feature_liveness (incl. the new `context_emission_policy` probe on
real stores), scanner/suppression/edge/confidence **202 passed**, tunables/fail-open 22.
ruff clean; mypy 0 new errors (suppression_audit.py:214 is the pre-existing baseline).
Liveness probe `context_emission_policy` wired in `main._build_feature_liveness` (pages
if scanning is active ~6h with zero policy evaluations).

### Watch after deploy (Strategy Lab)

New `context_floor:*` gate-audit rows; per-path emission counts climbing (QCB / SR_FLIP /
LIQ_SWEEP / DIV_CONT in their STRONG cells); NEGATIVE-cell emissions → 0. If the relax
side misbehaves: raise the anchor toward 65 or flip `context_emission_live` OFF in ops.

### NEXT

1. Owner: merge the PR (new emission/scoring path = owner-sign-off item — shipped LIVE
   per directive, so review + merge, not a dark flag to flip). Deploy, then watch the
   Strategy Lab rows above over a real window.
2. **Follow-up PRs (flagged, not built this session):** `dispatch_cooldown` DROP leak
   (235R, 100% would-win) → make live-tunable + tune off the audit; MEAN_REVERT
   compat-map (#739) so the 18th path can emit at all; Phase 5 pair-cohort dimension.
3. RANGE_FADE (19th) is now covered by the general policy too — its bespoke context gate
   can be retired into `context_emission_policy` in a later cleanup (behaviour-equivalent).

---

## 🟢 SESSION 68 2026-07-18 — Web (PWA) channel Phases 1+2 built: the iPhone path ships as an installable web app (branch `claude/loop-continuation-scheduled-resets-9ouhm5`, paired PRs in lumin-app + 360-v2)

**Owner ask:** execute the approved iPhone PWA plan
(IOS_PWA_STRATEGY_AND_HANDOFF.md) to full implementation. Session runs on
scheduled 3AM/8AM IST wake-ups until done.

### Shipped — engine side (this repo)

- **`POST /api/push/{subscribe,unsubscribe}`** (`src/api/push_topic_routes.py`):
  stateless web-push topic proxy. Web FCM can't topic-subscribe client-side,
  so the authed client hands its registration token over for the one
  Admin-SDK call. Doctrine preserved: NO token registry (used once,
  discarded, first-8-chars-only logging), topics allow-listed to
  `alerts`/`signals`, per-identity rate limit
  (`FCM_TOPIC_PROXY_MAX_PER_MIN`, default 12/min), send path untouched.
  Registered via the standard `register(app, auth=..., identity_dep=...)`
  convention. 12 new tests (`tests/api/test_push_topic_routes.py`); full
  tests/api/ green (647), ruff clean, mypy no new errors.
- **`tools/setup-vps-webapp.sh`**: idempotent nginx + certbot provisioning
  for the `app.luminapp.org` static docroot (mirrors setup-vps-api.sh).
  Deploy-entry documents no-cache (web deploys ARE the channel's update
  mechanism); hashed bundles cache 1h.

### Shipped — app side (lumin-app, same branch)

- Phase 1: checked-in `web/` scaffold (Lumin manifest/branding), `web`
  distribution token (self-updater inert — the unknown-token→sideload
  fail-safe would otherwise enable it), reCAPTCHA phone-OTP path
  (`signInWithPhoneNumber`), chart host split (`chart_bridge.dart` payload
  contract + WebView/iframe hosts via conditional export, postMessage shim
  in the chart asset), device-key execution excluded on web (server-side
  only), boot guards, CI `build-web` job (Firebase web config from
  `FIREBASE_WEB_CONFIG` secret, CanvasKit bundled via
  `--no-web-resources-cdn`, artifact upload + atomic VPS docroot deploy).
- Phase 2: web push through the new engine proxy (getToken + VAPID
  dart-define, arms post-auth via NavShell→attachRepository→syncWebPush;
  re-arms every shell mount = token-rotation convergence),
  `firebase-messaging-sw.js` (CI-injected config), iOS `InstallBanner`
  (Add-to-Home-Screen walkthrough — iOS only grants web push installed;
  permission prompt behind user tap), notification-settings recovery card.
- Headless end-to-end verification: boot → welcome slides → consent page
  render + persist in Chromium (Firebase JS SDK + fonts served locally —
  the sandbox blocks gstatic; found and fixed the CanvasKit-CDN boot
  dependency this way). Full suite green (368). Owner go-live checklist:
  `docs/WEB_PWA_CHANNEL.md` in lumin-app (Firebase web app + 3 secrets +
  DNS + one script run).

### NOT done / gated

- **Phase 3 (web billing)** — money-path, owner-sign-off, and blocked on
  the Razorpay-vs-Stripe provider choice (region-dependent owner call).
  Server-side auto-trade UI already works on web via Phase 1 (take-sheet
  is server-side-only there). Engine `POST /api/billing/web/verify` +
  webhook → `aset_tier` is the planned shape, dark-first.
- Owner go-live steps (checklist above) — Firebase web app registration,
  `FIREBASE_WEB_CONFIG` / `FCM_VAPID_KEY` / VPS secrets in lumin-app,
  Cloudflare DNS for `app.luminapp.org`, run `setup-vps-webapp.sh`.
- Real-iPhone verification (Add to Home Screen → push arrives app-closed)
  per the handoff's Part 4 — needs the owner's device once live.

---

## 🟢 SESSION 67 2026-07-18 — RANGE_FADE goes in as the 19th evaluator: DARK + context-gated on the edge matrix, activation is an ops toggle (branch `claude/path-analysis-deployment-uy30js`, 360-v2 only)

**Owner ask (2 PDFs: Profit tab + Strategy Lab, 2026-07-18):** analyse the data,
build the next Path, make it live, give control in ops.

### Data read (the evidence the path ships on)

- **Profit 7d window (59 closed):** engine real +20.62% vs TP1-full sim +22.40%
  — exits leak a modest +1.78%; entries fine. VOLATILE remains the loss hole
  (-14.97%, 0% win, n=4). RANGING give-back is the biggest pile (+132.74%
  total, 9% capture) — the tape is range-heavy and the trend book milks it
  poorly. Best cohort unchanged: 75-80 × MOVER_TREND_PULLBACK × TRENDING_UP
  (+16.30%, 5/5).
- **Strategy Lab:** the allocator's TOP recommendation in the live context is
  **SHADOW_RANGE_FADE at the 0.35 weight cap** (+0.841R n=24
  ASIA/QUIET/NORMAL, in design ctx). Its STRONG cells: OVERLAP/RANGE/NORMAL
  +0.885R n=15 · NY/MARKDOWN/EXPANDED +0.799R n=16 · LONDON/QUIET/COMPRESSED
  +0.650R n=28 · ASIA/MARKUP/NORMAL +0.510R n=18 · ASIA/RANGE/NORMAL +0.393R
  n=37 · LONDON/RANGE/NORMAL +0.291R n=40. **BUT the gate audit prices
  blanket activation NEGATIVE**: `shadow_unit:SHADOW_RANGE_FADE` EV/suppression
  **+0.20R over n=223** (saved 157R vs missed 112.6R) — the NEGATIVE cells
  (NY/RANGE/NORMAL -0.237 n=50, NY/QUIET/COMPRESSED -0.314 n=50, …) outweigh
  the STRONG ones on net. Conclusion: the edge is REAL but CONTEXT-LOCAL —
  promote per-context, not blanket. (Also noted, no action: dispatch_staleness
  back at DROP -0.42 n=1263, 556.7R missed — owner's standing "keep measuring"
  from S60 applies; SHADOW_MEAN_REVERT gate row now +0.84 KEEP — the live
  MEAN_REVERT vs shadow control comparison matters next window.)

### Shipped — RANGE_FADE, 19th evaluator (one PR)

- **Evaluator** `_evaluate_range_fade` (scalp.py): SAME pure function as the
  shadow unit (`shadow_strategies.evaluate_range_fade`) — zero drift; geometry
  verbatim (stop = edge ± 1·ATR, TP1 = range mid, 240-min validity, id prefix
  `RNGFD`); TP2/3 R-extensions; `range_fade_mid` stamped for the execution
  gate. Excluded from young-pair AND mover-restricted sets (a listing ramp /
  igniting mover is not a tested range).
- **Full 13-site wiring** (the #739 silent-death checklist): SetupClass enum ·
  SUPPORT role · STRUCTURAL_SLTP_PROTECTED · 360_SCALP channel compat ·
  CLEAN/DIRTY_RANGE regime compat · SL cap 3.0 · min-RR = range family 0.8 ·
  identity preservation · scanner family `mean_reversion` · regime affinity
  RANGING/QUIET + regime-neutral set · execution_quality_check RANGE_FADE fade
  branch (anchor = mid, max_extension 8 ATR) · display label "↔️ RANGE FADE" ·
  agent "The Range Keeper" + snapshot path map · portfolio AFFINITY.
- **Context-edge gate (new, the data-mandated part):** post-scoring scanner
  gate — RANGE_FADE emits ONLY when the current `mc_context_key` cell for
  SHADOW_RANGE_FADE (the ungated control arm) has a **STRONG** Wilson verdict
  in the live edge matrix (env-relaxable to POSITIVE via
  `RANGE_FADE_CONTEXT_MIN_VERDICT`; master `RANGE_FADE_CONTEXT_GATE_ENABLED`).
  This is the allocator's own eligibility rule, consumed live for the first
  time — Layer C finally has a consumer. Fail-CLOSED on cold/thin/NEGATIVE
  cells and on store errors (recorded via `fail_open`). Every block is tagged:
  funnel `gate_reject:context_edge`, suppression tracker, and a shadow-ledger
  stamp under **`context_edge:RANGE_FADE`** — so the gate audit will price
  THIS gate's save/miss balance on real data. Pure in-memory lookups, no I/O.
- **DARK (production doctrine, unlike S58's testing-phase MEAN_REVERT):**
  `RANGE_FADE_LIVE` default **false**; `range_fade_live` runtime tunable
  (Signal gating) is the activation switch — it renders automatically on the
  ops Control page tunables card (applied ≤5s, no redeploy). OFF = shadow-only
  `[SHADOW] RANGE_FADE_WOULD_FIRE` logging; the shadow unit keeps stamping as
  the control arm either way.
- **Liveness:** `range_fade_path` (detections vs shadow stamps, ~6h) +
  `range_fade_emission` (backlog probe; a context-block counts as path-alive —
  a healthy gate can legitimately block for hours, monotonic counters
  `_range_fade_emitted_total` / `_range_fade_context_blocked_total`).
- **Tests:** new `tests/test_range_fade_evaluator.py` (28 — shadow parity,
  dark default, tunable contract, context-gate truth table, counter hooks,
  13-site wiring pins); count pins 18→19 / 12→13 updated in 5 suites. Full
  suite **6829 passed**, ruff clean, mypy 105 = baseline (verified vs HEAD).

### Activation runbook (owner)

1. Merge the PR (new evaluator path = owner-sign-off item; it ships DARK so
   the merge itself changes no live output).
2. Let the deploy settle, then flip **Control → Engine tunables → Signal
   gating → "RANGE_FADE live (context-gated)"** ON at ops.luminapp.org.
3. Watch: `RANGE_FADE_FIRED` / `CONTEXT_EDGE suppressed` log lines, the
   Strategy Lab matrix growing a `RANGE_FADE` (emitted) row next to
   `SHADOW_RANGE_FADE` (control), and the `context_edge:RANGE_FADE` row in
   the gate audit. First emissions should cluster in ASIA/OVERLAP range/quiet
   sessions — the STRONG cells.
4. If live diverges from shadow: flip the tunable OFF (instant, no deploy).

### NEXT

1. Owner: merge + activate per runbook above.
2. After a real window: compare RANGE_FADE (emitted) vs SHADOW_RANGE_FADE
   (control) rows + the `context_edge:RANGE_FADE` gate-audit verdict; if the
   gate reads DROP (blocking winners), relax `RANGE_FADE_CONTEXT_MIN_VERDICT`
   to "positive" — dark-first rules apply to that relaxation.
3. Unchanged owner queue from S64-S66: merge #746/#130 pair; re-enable
   affected subscribers; MEAN_REVERT #739 step-2 data read; paper-freeze VPS
   runbook; dispatch_log retention; ops-UI per-user enable button;
   dispatch_staleness re-read (still DROP this window).

---

## 🟢 SESSION 66 2026-07-18 — #745 verified CORRECT against the Binance wire; "auto trade not happening to anyone" root-caused to observability, fan-out blackout now pages (branch `claude/auto-trade-not-working-lu5ixz`, 360-v2 + lumin-app)

**Owner ask (6 screenshots):** is the last auto-trade PR (#745, merged 11:38 IST)
correct? Auto-trade "not happening to anyone" — own previously-tested account
all-green, NO TRADES YET; two different take-sheet errors on WDCUSDT ("Futures
agreement needed" at 11:04, "not on the tripwire allowlist (allowlist size: 76)"
at 11:41); check Binance documentation too.

### Verdict on #745: CORRECT, verified against real Binance data

- **Wire-verified** (mainnet geo-blocks this container; futures **testnet**
  served it): `contractType == "TRADIFI_PERPETUAL"` is Binance's exact enum
  (sic), 36 TradFi perps listed (AMZN/NVDA/SPY/QQQ/MSTR/COIN/COPPER/…), and
  `-4411` = "Please sign TradFi-Perps agreement contract" with its own sign
  endpoint `POST /fapi/v1/stock/contract`. Structural filter > name list is
  right: the router dispatch log shows **IBMUSDT, TSMUSDT and SOXSUSDT** (a
  leveraged ETF) also got signals on 07-17 — none were on the static blacklist.
- **The 11:41 "tripwire allowlist (size 76)" rejection IS #745 working**:
  deploy landed ~11:39 IST, the 2h-old WDCUSDT signal outlived the universe
  update, allowlist auto-tracked 92→76 (16 TradFi perps removed). The app's
  "92 symbols enabled" screenshot was from 11:04, pre-deploy. Not a bug.
- Fail-safe direction confirmed: empty exchangeInfo cache → `is_tradfi_perp`
  False with the static blacklist as floor; boot race closed by
  `_ensure_symbol_metadata`; exits unaffected (tripwire fires pre-entry only).

### "Not happening to anyone" — what the remote data actually shows

- Telegram delivery + fan-out invocation **work** (router dispatch_log rows
  through 07-18; fan-out runs post-delivery). Manual take at 11:04 went all
  the way to **Binance** (-4411 back) → keystore, signing service, KMS, kill
  switch (green), global breaker (not tripped) all live. The execution stack
  is healthy end-to-end.
- The signal mix since ~07-16 was contaminated with stock perps (WDC, IBM,
  TSM, SOXS) — every auto dispatch on those -4411'd for every user, and
  pre-#740 those storms breaker-disabled real subscribers. #745 removes the
  contamination class at the source.
- **The structural gap this session closed:** every per-user dispatch gate
  (mode / tier / auto-pause / path+regime prefs) skips silently with no
  counter, no honest summary, and no probe — and an empty keyed-user roster
  (keystore soft-fails to `[]`) is indistinguishable from "no customers". A
  fleet-wide silent-skip blackout was invisible by construction; the old
  per-signal log line even reported skips as "rejected".

### Shipped (360-v2, this branch)

- `signal_dispatch`: per-fan-out outcome tally → honest summary log
  (`fan-out summary … placed= rejected= skipped= outcomes={…}`), monotonic
  `_FANOUT_TOTALS` (auto path only; manual takes excluded), empty-roster
  fan-outs counted separately; `dispatch_totals()` accessor.
- `auto_dispatch_health_check` — **pure** predicate (ops-detector style):
  pages when ≥5 fan-outs reach keyed users with ZERO order attempts fleet-wide
  (silent-skip blackout, detail names the top skip reasons), or ≥5 consecutive
  fan-outs see an EMPTY roster (keystore outage). Gap measured in fan-outs,
  not cycles — sparse signals can't page, blackouts can't hide. Wired as
  `auto_dispatch` PredicateProbe in `main._build_feature_liveness`
  (min_streak=3; env knob `AUTO_DISPATCH_GAP_THRESHOLD`).
- Tests: `tests/execution/test_dispatch_fanout_telemetry.py` (12 — totals,
  skip-vs-attempt split, manual exclusion, predicate baseline/violation/
  restart/interleave). Execution suite 461+12 green, feature-liveness 22
  green, ruff clean. Telemetry-only: zero dispatch-decision changes, zero
  new Firestore reads/writes (dict increments + one log line).

### Shipped (lumin-app, this branch)

- Cherry-picked S65's `-4411` copy rewrite (was stranded unmerged on
  `claude/auto-trade-binance-issue-cgtbdh`): "Not a crypto pair — {symbol}
  is a Binance stock (TradFi) perpetual… your account is fine", transient.
- **New `SymbolNotAllowed` mapping** — the 11:41 screenshot showed the raw
  engine string reaching the take sheet ("…tripwire allowlist (allowlist
  size: 76)"): now "Pair not tradeable through Lumin… list was updated after
  this signal appeared… No action needed", transient. `sanitizeEngineDetail`
  gained `tripwire|allowlist` vocabulary so no other path can leak it.
- Tests added to `dispatch_event_test.dart` (mapping + sanitizer backstop);
  Flutter suite runs in CI (no Flutter in-container).

### Owner notes (from the screenshots, not code)

- Own account: Futures wallet ≈ **$3.35 (₹289.52)** with **$5 notional** —
  razor-thin against Binance min-notionals (5 USDT for most alts AFTER
  lot-size floor-rounding; ETH 20, BTC ~50-100). Recommend ≥$25 notional +
  a funded wallet before judging the next crypto dispatch; -4164/-2019
  rejects WILL now at least show in Recent Activity + the fan-out summary.
- After the next paid **crypto** signal: `docker logs 360scalp-v2-engine |
  grep "fan-out summary"` answers exactly who placed/rejected/skipped and why.

### NEXT

1. Owner: merge this PR pair (360-v2 #746 + lumin-app #130). The S65
   lumin-app `-4411` copy fix merged separately as lumin-app #129
   (owner, 06:43Z); #130 was rebased on top so it carries only the
   SymbolNotAllowed/sanitizer increment.
2. Watch the new `auto_dispatch` probe after deploy: a page within hours
   means the blackout is real and the detail line names the gate.
3. Unchanged owner queue from S64/S65: re-enable affected subscribers via
   the new endpoints; MEAN_REVERT #739 step-2 data read; paper-freeze VPS
   runbook; dispatch_log retention; ops-UI per-user enable button.

---

## 🟠 SESSION 65 2026-07-18 — TradFi-Perps (stock perps) leaked into the universe → paid user's auto-trade rejected -4411 (branch `claude/auto-trade-binance-issue-cgtbdh`, 360-v2 + lumin-app)

**Owner report (5 screenshots):** own Binance account, auto-trade active/all-green
but "NO TRADES YET"; take sheet on **WDCUSDT** shows "Binance Futures agreement
needed"; account has real crypto USDⓈ-M perp trades from 2026-06-28; Binance order
ticket for WDCUSDT shows **"Off-Hours"** + "regular trading hours" warning.

### Root cause (verified against Binance, not assumed)

**WDCUSDT is a Western Digital *stock* perpetual** — one of Binance's TradFi-Perps
(tokenised equity/ETF/commodity perps). Binance `-4411 "sign TradFi-Perps
agreement"` is **symbol-specific** to that product, NOT an account-wide state
(WorldCoin is WLD, not WDC; the ticket's "Off-Hours" tag = stock perp). The
engine's `_NON_CRYPTO_BLACKLIST` is a **hand-maintained name list**; WDCUSDT
wasn't on it, so it entered the top-N futures universe, fired a signal
(reached the paid channel), and auto-trade's order was rejected `-4411`. The
account was never the problem.

### Shipped (engine, 360-v2)

- **Structural filter** — `symbol_filters.py` now captures Binance's own
  `contractType == "TRADIFI_PERPETUAL"` marker on the exchangeInfo refresh it
  already runs, exposing `is_tradfi_perp()`. `pair_manager` excludes the whole
  class at **all four** fetch paths (`_ensure_symbol_metadata` closes the boot
  race with the bootstrap refresh; zero extra network cost — same cached
  exchangeInfo pull). Self-maintaining: every current AND future stock perp is
  excluded without editing a list.
- **Static floor** — WDCUSDT added to `_NON_CRYPTO_BLACKLIST` so it's caught
  even before the first exchangeInfo refresh.
- Tests: +8 (symbol_filters TradFi classification/atomic-swap/fail-open;
  pair_manager fetch-site exclusion incl. an *unlisted* stock perp). 536
  pair/scanner/execution tests green, ruff clean.

### Shipped (app, lumin-app)

- `-4411` copy rewritten: was "your account hasn't accepted the Futures
  agreement… Binance refuses every order" (false, alarming) → **"Not a crypto
  pair — {symbol} is a Binance stock (TradFi) perpetual… your account is fine"**,
  severity `transient`. Tests updated (take_error_mapper + dispatch_event).

### NOTE — owner-sign-off item (paid-channel routing + dispatch universe)

Pushed to the branch, **not merged**. Shipped unflagged (consistent with the
existing unflagged `_NON_CRYPTO_BLACKLIST` precedent — this is safety exclusion
of non-crypto contamination, not a crypto-scoring change needing a shadow
window). CI runs the Flutter tests (no Flutter in-container). No PRs opened
(none requested).

---

## 🟢 SESSION 64 2026-07-18 — Full-system audit + implementation map; MEAN_REVERT zero-emission root-caused past the S60 fix (branch `claude/system-audit-implementation-map-gqxnjz`, 360-v2, doc-only)

**Owner ask:** fully audit the system, every corner; deliver an MD file with the
full implementation map.

**Shipped:** `docs/SYSTEM_AUDIT_IMPLEMENTATION_MAP_2026_07_17.md` — code-verified
map of all four repos at `main` HEAD (engine `8a3d1af`, app `2b12a84`, ops
`22dbf6c`, legal `5cb85ef`): topology, the full 11-stage signal path with the
18-evaluator live-status table, execution stack + invariants, 57-route API
inventory, measurement/self-defence layer, flag register (dark vs live,
defaults from `config/`), S59 dead-code register, app/ops/legal maps, cross-repo
contracts, CI/CD, health snapshot, findings, outstanding owner actions.

### Audit findings

- **F1 (HIGH, live — open issue #739): MEAN_REVERT still 0 emissions ~24h after
  #732 deployed.** The liveness probe paged hourly all day (`emitted_total=0`,
  monotonic). Truth report: 15,410 generated → 15,410 gated → **zero rows in the
  confidence tables** — every candidate dies pre-scoring, so this is NOT the
  §3.6a scoring class and NOT the execution gate #732 fixed. Both pre-scoring
  kill sites reject reasonlessly (`_reject("gated", None)`,
  `scanner/__init__.py:5713`/`5718`). **Prime structural suspect:**
  `REGIME_SETUP_COMPATIBILITY` lists MEAN_REVERT under CLEAN_RANGE + DIRTY_RANGE
  only, while its ≥2.5σ trigger is exactly the move that flips the MarketState
  classifier OUT of the range states — trigger anti-correlated with its own
  compat map. FUNDING_EXTREME (172/214 gated, 0 emitted) and LIQ_REVERSAL
  (32/32) share the signature. Recommended sequence in the doc: (1) reason-tag
  the two silent gated rejects (off money path, ships normally), (2) read one
  real window, (3) compat-map decision dark-first + owner sign-off.
- **F2 (MED):** the `gated`-stage rejects are the last reasonless rejection
  layer in the funnel — the exact gap that delayed F1's diagnosis.
- **F3 (LOW, checklist):** `SIGNAL_EXPIRY_ENABLED` defaults false in code —
  confirm VPS `.env` value vs B9 next time on the box.
- **Clean:** ruff re-run clean this session; zero open PRs across all four
  repos (S61–S63 fully merged incl. owner items #736/#740); backups healthy
  (#714 closed via #725); breakers wired with -2019/-4411 exclusions; only
  auto-detected issue open is #739.

### Second half of session (owner screenshots + "implement what's important"):
three fixes shipped on the same branch, all off the money path, full suite
**6742 passed** locally, ruff clean, mypy 112 = baseline

- **F4 (HIGH, new): the documented `/enable_user` operator verb NEVER
  existed.** `kill_switch.enable_user()` had zero operator-facing callers on
  any surface — the paying customer's "Paused by a safety check — email
  support" state (owner screenshot, per-user breaker trip, -4411 storm
  pre-#740) was permanently un-fixable. Shipped: owner-gated
  `POST /api/admin/users/auto-trade-enable` (phone OR firebase_uid; enable, or
  audited manual disable; Firestore read-back = engine truth; breaker's 5-min
  in-memory window self-expires so no engine-side reset needed). Kill-switch
  adjacent → owner merges the PR. Ops-UI button = follow-up in 360ce-ops.
- **F5 (MED, new): "Watching 0 symbols" on an armed account** — isolated-api
  display bug, same container class as #736: no PairManager singleton in the
  api process + env unset ⇒ runtime-status reported an empty allowlist for
  every user. Display-only. Shipped: pairs-snapshot fallback
  (`published_pairs()`, regular+promoting) with user-pref intersection; env
  hard-narrow still wins.
- **F2 (from the morning audit) implemented:** the two reasonless pre-scoring
  kill sites now record `gate_reject:setup_compat:{channel|regime_<STATE>}` /
  `gate_reject:execution:{trigger_not_confirmed|overextended}` funnel stages;
  truth report gained "## Pre-scoring gate rejects". One real window after
  deploy names MEAN_REVERT's killing gate + MarketState (#739/F1 step 1).

**Paper-freeze question (owner screenshot: last paper trade 2d ago, toggle
ON):** not resolved from here — needs the VPS reads. Facts established:
per-user paper books fill ONLY while engine-wide `AUTO_EXECUTION_MODE` is
`paper` (fan-out is TradeMonitor's order manager); the probe shows ONE
per-user ledger on disk with closes yesterday afternoon, so engine paper mode
was active — divergence between that ledger and the app's 2d-old history
points at per-user paper eligibility (`resolve_paper_preferences_uid`) or a
mode-row change ~07-16. Runbook given to owner (engine auto-mode read, user
mode row + paper prefs SELECT, ledger mtimes).

### Third wave (owner: "we can't re-enable one by one — subscribers must
recover automatically"; picked **self-serve button** via AskUserQuestion)

Self-service breaker recovery, engine + app (PR #742 already merged; this
wave is a follow-up PR pair):

- **Engine:** `POST /api/auto-trade/resume-disabled-mine` (user-authed) —
  a breaker-disabled user clears their OWN flag; rate-limited once per
  `AUTO_TRADE_SELF_REENABLE_COOLDOWN_HOURS` (config, default 6; B8) via a
  Firestore stamp (`users/{uid}.auto_trade_self_reenabled_at`, two new
  additive KillSwitchClient methods, read only on the tap — no hot-path
  reads); 429 carries human-readable retry copy; no-op honest response when
  not disabled; runtime cache invalidated; blast radius unchanged (breaker
  re-trips on new qualifying failures; -2019/-4411 never feed it). 8 new
  route tests; api suite 679 green; ruff clean; mypy 112 = baseline.
- **App (lumin-app, same branch name):** paused card's "Email support" CTA
  replaced by primary **"Re-enable auto-trade"** (busy state, snackbar
  outcomes, 429 copy rendered verbatim) with Email support demoted to
  secondary; `SelfReenableResult` model + `resumeDisabledMine()` on both
  repository impls; SWR invalidation on success; 5 new HttpRepository
  tests (CI runs them — no Flutter in this container).

### NEXT

1. Owner: merge the self-serve recovery PR pair (engine PR is kill-switch
   adjacent — owner-approved in-session via AskUserQuestion, owner merges),
   deploy, then: (a) re-enable the paid customer via the new endpoint (after
   they accept the Binance Futures agreement), (b) set
   `AUTO_TRADE_MANUAL_TAKE_ENABLED=true` in VPS `.env` + `bash deploy.sh`,
   (c) run the paper-freeze + test-account runbook commands from the session
   reply.
2. After a real window: read "## Pre-scoring gate rejects" for MEAN_REVERT →
   confirm the compat-map hypothesis → compat-map change is dark-first +
   owner sign-off (F1 step 3).
3. Unchanged owner queue: alert-take geometry design; proration follow-up;
   data reads (dispatch_staleness, geometry A/B, @TUNED arms, BTC_DIR
   shadow); dispatch_log retention; ops-UI per-user enable button.

---

## 🟢 SESSION 63 2026-07-17 — test-coverage sweep across all three repos + /api/activity filter bug found by it (branch `claude/test-coverage-analysis-9ykleq`, 360-v2 + lumin-app + 360ce-ops)

**Owner ask:** analyze test coverage across the codebase, then implement all
the proposed improvements.

### Real bug found and fixed while writing tests (360-v2)

`snapshot_cache.filter_activity` filtered on `e.setup_class` — a field
`ActivityEvent` **does not have**. On a warm cache,
`/api/activity?setup_class=X` raised AttributeError into the route's
catch-all and the app got an **empty activity list** instead of a filtered
one (live-build fallback never ran — the except wraps both paths). Fix: a
setup_class query now returns `None` from the cache so the route falls back
to `build_activity`, which filters correctly at the signal level. Off money
path (display-only), shipped with regression pin in the same commit.

### New coverage (all suites green before push)

- **360-v2** (+71 tests, 6732 total pass): first direct `snapshot_cache`
  suite (warm/stale, authoritative `is_open` split incl. mover-runner at
  TP1_HIT, legacy-payload heuristic, Redis refresher fault tolerance,
  lifecycle); `performance_tracker_honest` bucket math (was only ever
  mocked out — hard-limit adjacent); `/auto_trade_global` command (admin
  guard, exact client-method mapping, failure surfacing) and `/deploy` /
  `/rollback` (ref validation ahead of subprocess).
- **lumin-app** (+100 tests, 294 total pass): second-wave money-path
  coverage — BinanceKeysService per-user isolation + corrupt-blob wipe;
  UpdateService tag parsing / silent-failure contract / cache;
  PlayBillingService (engine-verdict-only entitlement, completePurchase
  always); AppConfig live-by-default fail-safe; and the
  LuminApiClient/HttpRepository scaffolding (401 single-force-refresh, 5xx
  retry, tolerant older-engine defaults, verify defaults to NOT entitled,
  region soft-fail-open).
- **360ce-ops** (+45 mobile / +27 web tests, 378 web + 45 mobile pass):
  agent notifier delivery leg (Telegram + FCM fan-out + prune + heartbeat
  — detectors were pinned, the paging leg wasn't); `/signals/{id}`
  drill-down; mobile app pinned from 1 test → api_client wire contract,
  AuthService credential/biometric seams, humanize, and widget-level
  confirm gates on kill-switch/LIVE (control doctrine).
- **CI in all three repos** now writes a per-module coverage table to the
  job summary — measured and reported, never gated.

**Open item:** PRs opened on owner request — 360-v2 #741 (carries the
`/api/activity` fix), lumin-app #127, 360ce-ops #67. All subscribed; the
360-v2/ops PRs are off-money-path and auto-merge-eligible once CI is
green; lumin-app merge left to owner.

---

## 🟢 SESSION 62 2026-07-17 — Paying subscriber's broken experience: entitlement lost on restart, raw engine errors on screen, -4411 breaker lockout (branch `claude/subscription-status-display-rvnzg2`, lumin-app + 360-v2)

**Owner ask (17 screenshots from a real Auto subscriber):** subscribed user sees
no subscription status anywhere; app leaks engine internals ("user <uid> is
auto-disabled", "global kill switch engaged", "B12 caps leverage", "This IP is
safe to share", Telegram-as-support); improve Charts; Trade→Live looks like an
ops console. Follow-up screenshots after an app restart exposed the root bug.

### Root causes found

1. **Entitlement was memory-only** (lumin-app): tier/user_id cached in
   `AuthService` only at OTP sign-in or purchase — every cold start rendered a
   paying user as signed-out free (upsell sheet, "Sign in with phone first").
2. **Take sheet rendered engine 4xx `detail` verbatim** — including Firebase
   UIDs; the good `DispatchEventTranslation` humanizer was only wired into
   Recent Activity rows.
3. **This subscriber's account was auto-disabled by the per-user circuit
   breaker fed by Binance -4411** ("Please sign TradFi-Perps agreement") — a
   user-setup state (never accepted the Futures agreement in Binance) counted
   as engine faults. Not excluded like -2019 was.

### Shipped (lumin-app, one PR)

- **WS0 restart fix:** `EngineMetadataStore` (per-Firebase-UID SharedPreferences
  display cache) + AuthGate hydration + background `GET /api/profile` refresh;
  engine stays entitlement truth.
- **WS1 subscription status:** Subscription page CURRENT PLAN card (renewal
  date + Play manage deep link; owned tile marked, re-buys routed to Play
  manage to avoid duplicate subscriptions), Profile subscription card
  (replaces the unlabeled AUTO pill), live Menu subtitle.
- **WS2 error/jargon sweep:** `take_error_mapper` +
  `DispatchEventTranslation.forReject` share one copy source; **-4411 maps to
  "accept the Futures agreement on Binance" guidance**; `sanitizeEngineDetail`
  guarantees UIDs/engine vocabulary can't reach widgets; full consumer-voice
  sweep (B12, whitelist→IP access list, evaluators→analysts, Telegram-support
  → published support email, About links wired).
- **WS3 Trade Live redesign (owner decision):** single `LiveStatusCard`
  (pure `resolveLiveStatus`, armed verdict byte-identical to old card) with
  one reason + one action + Details expander; Live feed is per-user only —
  engine-wide activity removed; dispatch rows tagged Auto/One-tap (new
  `source` field parse); phone-placed takes (signal + alert) merged from the
  existing `OrderLogService`; merged "No trades yet" empty state.
- **WS4 Charts:** TF row/indicator row split (chip overflow fixed), 1D
  timeframe, live price + true 24h % header (new `symbolTicker24h`, 60s),
  Levels overlay toggle. 277 tests green.

### Shipped (360-v2, separate PR — owner-signed B18 item)

- `tripwires.record_order_placement_failure`: **-4411 excluded from both
  breakers** exactly like -2019 (`_BINANCE_USER_SETUP_CODES`); rejection still
  logs to dispatch_log + reaches the app. Owner approved in-session via
  AskUserQuestion. 445 execution tests green. **No auto-merge — owner merges.**

### ⚠️ Ops runbook for THIS subscriber (owner action)

1. He must open **Binance → Futures and accept the TradFi-Perps agreement**
   (source of every -4411 rejection).
2. Then re-enable his account (operator-only): breaker reset +
   `kill_switch.enable_user(<uid from his error screenshot>)`.
3. Follow-up candidate: ops-dashboard per-user re-enable surface (today it's
   Telegram-bot only, and Telegram is banned in-region).

### Open

- Owner to merge both PRs (engine PR is a B18 sign-off item).
- Assist↔Auto in-app plan *switching* deliberately routes to Play manage;
  proper `ChangeSubscriptionParam` proration is a follow-up.
- Auth-page `$e` renders (Firebase copy) left as-is — outside trading surfaces.

---

## 🟢 SESSION 61 2026-07-17 — Binance connect 500 (KMS never inited in api container) + armed card lying over silent dispatch skips (branch `claude/binance-api-trading-issues-s9858w`, 360-v2 + lumin-app)

**Owner ask (with screenshots):** (1) a NEW paying subscriber cannot connect
their Binance key — "Connection failed — Server misconfiguration — KMS not
initialised"; (2) owner's primary account shows Auto-trade ARMED, all four
gates green, key connected since 2026-05-19 and previously auto-traded — but
zero orders and zero "Recent activity on your account" rows while the
engine-wide signal feed keeps scrolling.

### Root cause 1 — isolated api container never initialised KMS (fixed)

`POST /api/binance/connect` runs in the **api** container
(`API_PROCESS_ISOLATED=true` live on VPS); `src/api/main.py` inited Firebase
Admin, keystore, kill switch, tunables — **but never `init_kms_client`**
(only `bootstrap.py` + the signing service do). The connect route's KMS
preflight (`binance_connect_routes.py`) therefore 500s on every isolated-mode
connect, while single-process mode works. Same bug class as the Session-14
isolation sweep (#565–#569) that added `init_keystore`/`init_kill_switch`
here — KMS was left out. #734 documented the env vars but didn't touch the
entry point. **Fix:** `_maybe_init_kms()` in `src/api/main.py` mirroring
bootstrap's guarded block (all four `GCP_KMS_*` → init, SA path or ADC,
warn-not-raise) + `tests/api/test_api_main_kms_init.py`. Owner-sign-off item
(KMS) — PR held for explicit approval, no auto-merge. Owner also confirmed
the business rule: **every tier (free/assist/auto) may connect a key** —
connect is never tier-gated; only execution differs.

### Root cause 2 — armed card evaluated 4 gates, dispatch skips silently on 7

`signal_dispatch._one_user` skips BEFORE any dispatch_log row on: mode, tier
entitlement (B16 gate, 2026-06-24, fails closed; read-time `paid_until`
downgrade), auto-pause, path pref, regime pref. The runtime-status `armed`
only ANDed globally_enabled/user_disabled/key_connected/mode — so a
tier-lapsed (or pref-blocked) user renders ALL GREEN + zero activity forever.
Prime suspect for the owner's primary account: the tier gate postdates the
key connect (2026-05-19) and Play Billing flipped on 2026-07-16 — verify the
row on the VPS (`users.tier`, `users.paid_until`,
`user_auto_trade_settings.paused_reason/path_preference/regime_preference`).
**Fix (status surface only, dispatch untouched, zero new reads — reuses the
route's existing user+row fetches under the 10s cache):** new pure
`auth.effective_tier(tier, paid_until)` (lockstep twin of
`signal_dispatch._resolve_user_tier`); runtime-status now returns
`user_tier`, `tier_gate_enabled`, `tier_allows_auto`, `auto_paused`,
`path_preference`, `regime_preference`, `preferences_block_all`; `armed` is
the FULL user-state conjunction (tightened in place — strictly green→yellow,
old builds degrade to honest-but-under-explained). `resume-mine` now
invalidates the runtime cache. lumin-app renders the new gates: tier row,
server-pause fold-in, block-all row, restrictive-prefs footnote.

### Server-side manual take (owner-approved in-session, same day)

After the KMS fix landed, the owner hit the NEXT wall: one-tap "Take trade"
(signals + alerts) is client-side — it demands device-stored keys (Settings
→ API keys), a different store from the server-side connect, and the
server-connected key is IP-whitelisted to the VPS so phone-placed orders
would be Binance-rejected anyway. Owner picked **server-side take**:
`POST /api/auto-trade/take {signal_id}` → (isolated mode) LPUSH
`snapshot:cmd:take` → engine `ManualTakeConsumer` (BRPOP, sub-second, zero
idle reads) → `engine.take_signal_for_user` → re-validate against the live
book → `dispatch_signal_to_uid_manual` — the SAME sizing / tripwire /
FSM-safety-gate / dispatch_log path as auto, with three tap-justified
differences: mode + auto-pause + path/regime pref gates skipped, tier gate
at `can_assist` (one-tap is the assist product surface), and a NEW
`(uid, signal_id)` dup guard (audit found `place_signal` never checked for
an existing position — a double-tap would have fired a second real MARKET
entry; guard fails CLOSED on store errors). Result key
`snapshot:take_result:<request_id>` polled by the route ≤8s → synchronous
placed/rejected answer; engine-down envelopes >60s old are refused as
stale (no minutes-late market orders). dispatch_log rows now carry
`source: auto|manual_take`. **Dark-flag-first honoured:
`AUTO_TRADE_MANUAL_TAKE_ENABLED` default-OFF** — owner activates with one
`.env` line + redeploy. **Scope: signals only** — alerts carry no SL/TP
geometry and "never OPEN without a stop" forbids a stop-less server entry;
engine-side alert-take needs a designed geometry-synthesis layer first
(B7 owner-sign-off follow-up, flagged to owner).

### Open

- Owner to run the VPS runbook (final report) to confirm which silent gate
  holds the primary account, then fix the row via the admin grant flow.
- Owner to activate `AUTO_TRADE_MANUAL_TAKE_ENABLED=true` after merging the
  take PR (one line in VPS `.env` + `bash deploy.sh`).
- Alert-take server-side: needs SL/TP synthesis design (B7). Until then the
  alert sheet stays client-side; its copy now explains the second-key
  requirement honestly.
- Optional follow-ups noted in PR: dedupe bootstrap/api KMS init; migrate
  `signal_dispatch._resolve_user_tier` onto `auth.effective_tier` (pure
  refactor, dark-first rules apply); owner/all-access exemption from the
  expiry downgrade was raised and NOT taken (owner described the three-tier
  model instead — no business-rule change shipped).

---

## 🟢 SESSION 60 2026-07-16 — 18th path was DEAD at the execution gate (fixed live), tuned shadow arms for the measured losers, WS gap-refill, Play Console fixes + AAB releases (branch `claude/system-audit-play-release-zsaa6d`, 360-v2 + lumin-app)

**Owner ask:** deep audit (numpy class, data sufficiency, WS management, limits);
why has yesterday's 18th path produced no signal; analyse attached Strategy Lab +
Profit-tab PDFs; resolve the two Play Console recommendations; AAB into the
Releases section + click-to-copy Play release notes.

### The 18th-path incident (root cause CONFIRMED, fixed)

Truth report showed `MEAN_REVERT | 300 generated | 300 gated | 0 emitted` —
**`execution_quality_check` had no MEAN_REVERT branch**, so the fade fell into
the generic ELSE whose trigger requires 5m EMA9 aligned WITH the trade
(structurally false for a counter-trend fade) AND the 1.5-ATR default
`max_extension` (always exceeded by a 2.5σ entry). Double-deterministic 100%
rejection; NOT display, NOT market conditions, NOT the z-trigger (107
detections). The `mean_revert_path` liveness probe compares detections vs
shadow stamps and was structurally blind to generated-but-fully-gated.

**Fix (live per the standing S58 owner directive; `mean_revert_live` stays the
off-switch):** evaluator stamps `mean_revert_mean` (== TP1) on the signal;
`execution_quality_check` gained a MEAN_REVERT fade branch (trigger = entry on
the stretched side of the mean) + `max_extension: 5.0`; new
`mean_revert_emission` liveness probe pages when ≥60 detections accrue with
zero emissions (~backlog predicate — RateProbe streaks reset on sparse flows).
Expect first emissions to cluster in RANGING/QUIET; confidence floor is 70 in
RANGING so a quiet tape can still legitimately go hours without one.

### Data read (owner-attached Strategy Lab + Profit PDFs, 2026-07-16)

- Entries healthy: last-3d 25 closed, +41.27% real, 56% win; TP1-full sim
  +43.04% — exits leak a modest +1.77%. QUIET-regime capture is **2%**.
- SHADOW_MEAN_REVERT rollup n=886 / 52% / +0.43R, gate-audit KEEP — the edge
  the dead live path was leaving on the table.
- `dispatch_staleness` back at **DROP** (n=589, 78.9% would-win, 440R missed,
  −0.70 EV) — biggest measured leak, but verdict has flip-flopped
  (DROP S54 → KEEP S56/S58 → DROP). **Owner decision: keep measuring, no
  action this session; re-read next window.**
- MOVER_AVWAP_SCALP capture **−17% on 100% runners**; VSB −4% — third
  consecutive losing window. **Owner decision: "disabling paths is never a
  good idea, need to tune it" → shipped observe-only `@TUNED` shadow arms**
  (`src/tuned_variants.py`): MAS arm banks TP1 at measured median MFE (2.1%)
  behind an ATR/structure stop; VSB arm adds a ≤1-ATR-from-20-bar-mean entry
  filter + 3.0% TP1. Rows land in the edge matrix as shadow variants
  (excluded from allocator + rollups; `@TUNED` added to geometry variant
  suffixes; stop-A/B rollup now suffix-explicit). Tunable
  `tuned_variants_enabled` (Measurement, ON) + `tuned_variants` liveness
  probe. Applying a winning recipe stays dark-first + owner-signed.
- Stop-geometry A/B: ATR leads 5/6 decided strategies — application half
  approaching actionable; give it ~a week more sample.

### Audit verdict + fixes

- **CLEAN (verified):** live numpy-truthiness, WS reconnect/backoff/listenKey
  lifecycle, REST weight/429 handling, ledger bounds, blast-radius caps, no
  bare excepts. REPORT-ONLY: `dispatch_log` Firestore subcollection grows
  unbounded (~500KB/user/day, free-tier today — retention policy pending).
- **Fixed — WS candle gap-refill:** quick reconnects (incl. Binance's 24h
  forced disconnect) never activate the REST fallback, so candles that closed
  during the gap were permanently missing. `_schedule_gap_refill` now
  REST-backfills each kline stream's missed closed candles after every
  reconnect (bounded, ~5 req/s, strong-ref'd task).
- **Fixed — numpy CI guard widened:** now scans `scripts/`+`tools/`+`config/`
  too, and catches bare `arr or []` / `if not arr|series|ohlc*` forms (3 new
  allowlist entries with proofs; all trees clean).
- **Fixed — money-path fire-and-forget:** expiry `close_full` task now
  strong-ref'd (`_expiry_close_tasks`) — loop's WeakSet could GC it mid-close.
- Housekeeping: dead `@skip` TestOBIChannel block deleted.
- Tests: full suite **6604 passed** (+~30 new), ruff clean, mypy 102 (=baseline).

### Lumin app (same branch, second PR)

- **R8 full optimisation** (Play recommendation: 46% rates): workflow patches
  the generated `build.gradle.kts` release block with `isMinifyEnabled` +
  `isShrinkResources` + `proguard-android-optimize.txt` + a minimal
  `proguard-rules.pro` (Flutter JNI + Play Core keeps). PR builds compile
  with R8 full, so breakage fails CI pre-merge.
- **Edge-to-edge** (Play recommendation, Android 15/SDK 35):
  `SystemUiMode.edgeToEdge` + transparent bars in `main()`, and
  `AppBarTheme.systemOverlayStyle` so per-page AppBars can't override it.
  NavigationBar/AppBar handle their own insets; no page changes needed.
- **AAB → Releases section:** both `action-gh-release` steps now attach the
  `.aab` next to the APK — Play upload is a one-click download from the
  release page. `docs/PLAY_RELEASE_NOTES.md` holds the `<en-US>` notes block.

### NEXT

1. Watch `MEAN_REVERT_FIRED` + first emissions in app/ops after deploy; the
   `mean_revert_emission` probe pages if detections accrue with zero emissions.
2. `@TUNED` rows appear in the Strategy Lab matrix once samples classify —
   compare vs the live MAS/VSB rows after a real window; tuning application
   is dark-first + owner sign-off.
3. Re-read `dispatch_staleness` next window (owner: keep measuring).
4. After next Play upload: confirm the two Play Console recommendations clear
   on the new release's dashboard (may take a few days of install data).
5. Unchanged: BTC_DIR shadow review → flip `btc_dir_penalty_apply`; geometry
   A/B application design (~1 week more data); Telegram→app decouple (owner);
   Phase 4 master-arm (owner); dispatch_log retention policy.

---

## 🟢 SESSION 59 2026-07-16 — Full system audit → 4-tier fix batch: inert circuit breakers wired, pre-TP naked-residual ladders, gate-chain fail-open sweep, 6 bug fixes (branch `claude/system-audit-signals-qshnvq`, 360-v2)

**Owner ask:** full audit on system for bugs, errors, dead code — especially
signal generation. Three parallel deep sweeps (signal path, execution path,
dead-code reachability) over all 4 repos; owner decided in-session: breakers
live NOW, FSM hardening IN, dead code REPORT-ONLY, MEAN_REVERT profile direct
fix.

### Audit verdict

- **CLEAN**: numpy-truthiness class (#726/#727) confirmed closed in live code;
  no long/short asymmetry in any of the 18 evaluators; enum/family coupling
  complete incl. MEAN_REVERT; hot-path caching (₹4,552 class) clear; secret
  handling clear; kill-switch coverage of order placement fails closed; ops
  repo 350 tests green.
- **The big one (F1)**: BOTH blast-radius circuit breakers (B18 #4/#5) were
  inert — `record_rejection` had ZERO production callers since PR-8. Checked
  on every order, fed by nothing, could never trip.

### Shipped (4 commits, one PR, all tiers owner-signed-off in-session)

1. **Tier 1 — breakers wired live**: dispatch failure handler feeds
   `tripwires.record_order_placement_failure`. Only OrderPlacementError
   counts (gate rejections excluded by type — a disabled user's own refusals
   can't walk the global breaker); -2019 stays with the consec-margin pause;
   Unreachable counts global-only (users aren't disabled for our signing
   outage). Per-user trip → kill_switch.disable_user (persists); global trip
   → engage_global. 10 new tests incl. end-to-end dispatch trip.
2. **Tier 2 — FSM exit-side hardening**: all three pre-TP paths now share
   `_protect_residual_final` (BE-SL → force-close REDUCE_ONLY → CRITICAL +
   new naked-residual Telegram page). Pre-fix: replacement-stop failure left
   the residual stopless for hours (volatile path had NO fallback at all);
   `close_reason=PROTECTION_FAILSAFE` marks these flattens. Also: pretp
   track/untrack tasks strong-ref'd (spawn_track/spawn_untrack — GC could
   silently kill per-tick management for a symbol); funding watcher re-fire
   suppression (15min after successful close; dropped fill event used to
   cause 30s cancel+close spam) + zero-residual no longer sends full qty.
3. **Tier 3 — gate-chain fail-open sweep** (the half S58 skipped): scanner
   had 27 fail-open handlers, 5 recorded. Converted 15 DEBUG-only gate
   handlers + 5 silent `except:pass` (incl. the min-distance block that
   mutates sig.stop_loss mid-loop) + base.py structural SL/TP snap (shared
   by EVERY evaluator) + shadow unit errors (MEAN_REVERT control arm).
   Gotcha fixed: the old LOCAL `from src import fail_open` imports shadowed
   the new top-level one → UnboundLocalError; hoisted. Truthiness regex
   widened (truthy `.get()`, `*_arr` names) — immediately caught 2 scanner
   sites (converted to len()) + 2 scalar false positives (allowlisted with
   proof). New AST pin: no new silent except-pass in scanner.
4. **Tier 4 — bug batch**: paper close-all NEVER worked (`int += dict`,
   TypeError swallowed per book, plus signature mismatch with the API
   route); MEAN_REVERT now passes `profile=` to basic filters (was the only
   evaluator of 18 skipping pair multipliers — owner-approved direct fix);
   reconciler order-side healing implemented (docstring promised it from day
   one; SL/TP live on `/fapi/v1/algoOpenOrders` post Dec-2025 -4120
   migration — the never-used openOrders constant would have missed them;
   re-places a lost protective stop, 3-min freshness guard against racing
   pre-TP transitions); ccxt boot/mode-switch guard (live mode used to
   NotImplementedError on the FIRST order); worker-manager boot dedup (slow
   reconcile could spawn two PositionWorkers per user).

### Dead-code register (owner decision: REPORT ONLY, no deletions)

Zero live importers, verified by reachability from main/bootstrap/api:
- `src/scanner_core.py` (compat shim; pyproject ruff comment still names it)
- `src/cvd.py` (re-export shim of order_flow)
- `src/macro_blackout.py` (+ its tests)
- `src/pair_analysis_report.py` + `src/pair_anomaly_detector.py` (dead pair)
- `src/simulation/` (+ tests/test_simulator.py)
- Config: `OPENAI_MIN_CONFIDENCE_THRESHOLD`, `OPENAI_HOT_PATH_BYPASS_CHANNELS`
- Zombie radar wiring: `main.py` assigns `scanner.on_radar_candidate =
  _handle_radar_candidate` but the scanner call site was disabled ("too
  spammy") — handler + FreeWatchService radar-watch path are unreachable.
- Zombie-by-flag (KEEP — one env flip from live): cornix_formatter
  (CORNIX_FORMAT_ENABLED=false), feedback_loop (FEEDBACK_LOOP_ENABLED=false).
- Informational: scalp_cvd/vwap/supertrend/ichimoku channels are `disabled`
  by default, fvg/orderblock `radar_only`, divergence pilot-only — under
  default config scalp.py is the ONLY paid-signal generator. ORB / CLS /
  SR-flip-LONG evaluators are flag-disabled. RANGE_REJECTION /
  EXHAUSTION_FADE enum values reserved, unemitted.

### Deferred / follow-ups

- Trade-monitor telemetry fail-opens still DEBUG-only (same class as Tier 3,
  lower stakes) — sweep in a future session.
- Reconciler qty-mismatch / modified-SL-price diffs remain a policy call.
- Owner-deferred from S58 unchanged: prune MOVER_AVWAP_SCALP +
  VOLUME_SURGE_BREAKOUT (both −0.78R); MVTP concentration handling.

### NEXT

1. Watch the fail-open counters after deploy — Tier 3 makes previously
   invisible failures visible; new WARNs = something was already dying.
2. Watch for breaker trips (per-user first); `/reset_global_breaker` and
   `/enable_user` are the operator verbs if a trip needs review.
3. Confirm MEAN_REVERT emissions unchanged post-F6 via shadow-stamp
   comparison in the Strategy Lab matrix.
4. Unchanged from S58: BTC_DIR shadow review → flip btc_dir_penalty_apply;
   geometry A/B window; Telegram→app decouple (owner); Phase 4 master-arm
   (owner).

---

## 🟢 SESSION 58 2026-07-15 — Strategy Lab data read → MEAN_REVERT goes LIVE (18th evaluator) + fail-open sweep closes the #727 blind spot (branch `claude/strategy-lab-signals-analysis-zi8tck`, 360-v2)

**Owner ask:** understand the ops Strategy Lab, analyse signals/profit/strategy
data, check for numpy-class failures on regular pairs (like #726/#727), propose
the next move. Mid-session owner directive: **"no dark on 18th path, make it
live."**

### Data read (truth report + last-100 signals + dispatch log + edge matrix)

- **Emission concentration confirmed**: MOVER_TREND_PULLBACK = 28 of the last
  50 dispatches (56%); mover-family = 68%. Regular pairs: only
  FAILED_AUCTION_RECLAIM emits at volume (32/100). Cause is structural, not a
  bug: mover-promoted pairs restrict to 4 evaluators; 64% QUIET/RANGING tape;
  min_confidence gate measured KEEP (+0.52R/suppression — it's correct).
- **The problem is inverted**: MVTP passes the confidence gate at 87% (regime
  dim pins 18.0 for movers) while its measured edge is **−0.29R (n=3,293)**.
  MOVER_AVWAP_SCALP (12% win, −0.78R, n=141; live 1/8) and
  VOLUME_SURGE_BREAKOUT (1% win, −0.78R, n=85) are measured losers.
  **SHADOW_MEAN_REVERT is the best strategy in the matrix: +0.67R, 59% win,
  n=550, consistent across two windows** — and had no emission path.
- **Numpy check**: regular-pair evaluators are CLEAN on the truthiness class
  (allowlisted sites are list-fed; fail-open counters zero; liveness 7/7 OK;
  zero-generators reject with real reasons — strict thresholds, not death).
  BUT the *silent-swallow* half survived in the files #727 skipped.
- dispatch_staleness regressed S54's DROP → now KEEP (+0.11R) — sample-floor
  discipline vindicated again. Geometry A/B: ATR leads 4/5, ΔR still thin.

### Shipped (both on this branch, one PR)

1. **Fail-open sweep** (off money path): ~18 silent `except` handlers in
   regime / chart_patterns / level_book / structure_state / volume_profile /
   signal_quality / mtf / scalp / scanner now call `fail_open.record` —
   behaviour unchanged, failures count + page via the #728 burst pager.
   `_safe_float`/`_last` skipped with reason (coercion contract). MTF KeyError
   stays silent (normal young-pair warmup); only TypeError/ValueError record.
   New `tests/test_fail_open_sweep.py` (10 tests).
2. **MEAN_REVERT — 18th evaluator, LIVE** (owner sign-off in-session; the
   S53-S56 shadow window IS the dark-first evidence):
   - `_evaluate_mean_revert` in scalp.py calls the SAME pure function as the
     shadow unit (`shadow_strategies.evaluate_mean_revert`) — zero drift
     possible; entry/SL/TP1 = measured geometry verbatim (±1.5·ATR stop, TP1 =
     20-bar mean, 180-min validity); TP2/3 = R-extensions (exit is TP1-full).
   - Full wiring: SetupClass enum + portfolio role (SUPPORT) + structural-SLTP
     protected + channel/regime compat (CLEAN/DIRTY_RANGE) + SL cap 3.0% +
     min-RR 0.9 (mean-reversion branch — 1.2 default would reject the measured
     geometry) + self-classifying + regime affinity RANGING/QUIET + regime-
     neutral set + scanner family `mean_reversion` (unmapped = blocked in its
     home regime!) + portfolio AFFINITY + labels + agent name "The Rubber
     Band" + snapshot path map.
   - Deliberately EXCLUDED from young-pair and mover-restricted evaluator sets
     (fresh listings have no stable mean; mover promotion is the anti-thesis).
   - **`mean_revert_live` runtime tunable (Signal gating, default ON)** — the
     instant ops off-switch; OFF = shadow-only WOULD_FIRE logging.
   - Liveness probe `mean_revert_path`: shadow stamps flowing while the
     evaluator detects zero = dead wiring, pages in ~6h.
   - The shadow unit keeps stamping unconditionally — it is the ungated
     control arm; edge matrix shows two rows by design (SHADOW_MEAN_REVERT/
     shadow vs MEAN_REVERT/emitted).
   - Tests: 7 new evaluator tests (incl. shadow-parity + tunable contract);
     count pins 17→18 updated in 4 suites. Full suite green, ruff clean, mypy
     102 (≤103 baseline).

### Owner deferred (evidence exists, act later)

- Prune MOVER_AVWAP_SCALP + VOLUME_SURGE_BREAKOUT (both −0.78R measured).
- MVTP concentration handling (per-setup floor / context gate — shadow first).

### NEXT

1. Watch `MEAN_REVERT_FIRED` lines + the app/ops after deploy; first real
   emissions should cluster in RANGING/QUIET. Flip `mean_revert_live` OFF from
   ops if live behaviour diverges from the shadow measurement.
2. Compare MEAN_REVERT (emitted) vs SHADOW_MEAN_REVERT (control) rows in the
   Strategy Lab matrix once samples accumulate — the gate chain's cost/benefit
   on this strategy is directly measurable.
3. Unchanged: BTC_DIR shadow review → flip `btc_dir_penalty_apply` (S56);
   geometry A/B needs more days; Telegram→app decouple (owner); Phase 4
   master-arm (owner).

---

## 🟢 SESSION 57 2026-07-14 — Feature-liveness alerting: silently-dead features now PAGE (branch `claude/pr-history-analysis-l3o9on`, 360-v2 + 360ce-ops)

**Owner directive after #726/#727:** *"this time you found — what if next time we
don't find? We need a proper solution: alerts on this, and data sufficient or
missing data."* The root failure of the incident wasn't numpy — it was that all
8 dead features failed SILENTLY (fail-open handlers at DEBUG, nothing comparing
output rates to upstream). Four layers shipped, built on the existing S47/S48
alert plumbing:

1. **`src/fail_open.py`** — every fail-open `except` in data/measurement paths
   now calls `fail_open.record(site, exc)`: thread-safe counters, WARNING logs
   rate-limited 10 min/site (never DEBUG again), snapshot into the manifest.
   Behaviour unchanged — still fail open, no longer invisible. Converted sites:
   geometry stamp, suppression stamp, shadow units, BTC gates (scanner +
   trade_monitor), market-context builder/publisher, allocator publisher,
   /market command, trade-observer price, alerts volume gate.
2. **`src/feature_liveness.py`** — probe registry on the existing 5-min audit
   loop; RateProbes compare output counters vs upstream drivers (monotonic
   `stamped_total`/`recorded_total` added to the stores), PredicateProbes check
   value health. Violations need upstream evidence (quiet market never pages),
   sustained streaks (≥6 cycles = 30 min), and a 30-min boot grace (S55).
   Probes: geometry_ab (THE incident probe: suppressions flow + zero pairs),
   suppression_audit, strategy_edge, market_context (staleness + raw
   `atr_percentile` — victim #2's blind spot, now also stamped into the
   published payload), shadow_units, candle_coverage, btc_reference, plus
   fail-open burst/drip alerting. Writes `data/feature_liveness.json` (~2 KB,
   atomic, local). Tunable `feature_liveness_enabled` (Measurement, ON).
3. **Alert wiring — zero new channels:** `monitor_heartbeat.check_feature_liveness()`
   turns manifest alerts into `INVARIANT_WARN:` lines → the existing hourly
   `vps-liveness.yml` pages Telegram + files the auto-detected issue (F-09).
   Manifest-itself-stale while engine fresh also pages (the watchdog can't die
   silently either). Truth report gains `## Feature Liveness & Fail-Open
   Telemetry` (builder flag + vps-monitor fetch wired; fixture-run verified).
4. **Prevention:** `xfail_strict = true` (an xpass now FAILS CI — the rot class
   from S56 is structurally impossible); CI guard test
   `tests/test_no_numpy_truthiness_regression.py` bans boolean-context OHLCV
   patterns in src/ (immediately caught 2 unaudited sites — fixed);
   `numpy_seeded_store` conftest fixture is the canonical candle-fixture shape;
   CLAUDE.md hard limits + conventions updated.

**Incident replay test proves the loop end-to-end**: pre-#726 production state
(suppressions flowing, geometry stamping raising numpy-truthiness) → geometry
flat-line alert + fail-open burst alert after the streak window → both become
INVARIANT_WARN lines from the monitor. This exact incident would have paged
within ~35 minutes instead of being found by a human 25 hours later.

### Owner drill after deploy (untested pager = a hope, S48)
Flip `geometry_ab_enabled` OFF in ops → wait ~40 min → expect a Telegram page
+ auto-detected issue for `feature_liveness geometry_ab` → flip back ON.

---

## 🔴 SESSION 56 2026-07-14 — Numpy-truthiness fail-open class: geometry A/B was DEAD, global context degraded, §2.1 BTC_DIR penalty never fired (branch `claude/pr-history-analysis-l3o9on`, 360-v2)

**Owner ask:** read briefs, review 4-day PR history, analyse the Strategy Lab PDF
(2026-07-14 07:00 UTC). Analysis found one production bug class with three victims.

### The bug class (code-verified + repro'd)

`HistoricalDataStore.get_candles()` returns `Dict[str, np.ndarray]`; `arr or []` /
`if not arr` on a multi-element numpy array raises `ValueError`. Three call sites
read the data store directly — bypassing the scanner's `_normalize_candle_dict`
list boundary (which exists because this class bit us before) — and swallowed the
raise in fail-open `except` handlers at DEBUG. Result: each feature silently did
nothing in production while all list-fixture tests stayed green:

1. **`Scanner._stamp_geometry_ab` (#722) — stop-geometry A/B stamped ZERO pairs
   in its first ~25h live.** Strategy Lab card + truth report both "no pairs yet"
   while the suppression audit classified hundreds through the same 5-min loop
   (that asymmetry was the tell). Fixed: None-checks, arrays passed through.
2. **`CryptoSignalEngine._build_global_market_context` (#721)** — ATR-percentile
   + HTF-prior inputs of the *published global* context silently None every cycle
   (per-signal contexts were fine — different, list-fed path). Allocator was
   routing on a coarser vector than the matrix cells it matches. Fixed.
3. **`check_btc_direction_gate` (OWNER_BRIEF §2.1 soft penalty) — never fired in
   production.** `_classify_btc_4h` raised on the numpy `close`; truth-report
   BTC_Dir column all-zero across ~2.8k scored samples while the structurally
   identical list-fed Sym_Dir gate fires. Repro: identical bearish inputs —
   list-fed returns the penalty, numpy-fed raises.

### Shipped

- `src/btc_direction.py` — `_classify_btc_4h` numpy-safe at the source (hardens
  sym-dir + countertrend-mover callers too).
- `src/scanner/__init__.py` — geometry stamp extracts arrays with None-checks;
  **BTC_DIR application ships DARK (owner decision, AskUserQuestion)**: new
  runtime tunable `btc_dir_penalty_apply` (Signal gating, default **OFF**) — while
  OFF every would-fire is shadow-logged (`btc_dir_shadow:*` suppression counter +
  `BTC_DIR_SHADOW` INFO line with the would-be points); ON applies as designed.
  Re-arming changes live scoring → owner flips after reviewing a real window.
- `src/main.py` — global-context candle reads numpy-safe.
- `config/__init__.py` + `src/runtime_tunables.py` — `BTC_DIR_PENALTY_APPLY`.
- `tests/test_incident_2026_07_14_numpy_truthiness.py` — 7 regressions driving
  the REAL production shape (real `HistoricalDataStore` seeded via
  `update_candle`); 4 of them fail on pre-fix code. Dark default pinned.

### Strategy Lab analysis verdicts (2026-07-14 07:00 UTC window)

- **`dispatch_staleness`: S54's DROP verdict is dead** — regressed to TUNE
  (n=961, 38% would-win, −0.06R EV). Do NOT loosen; the 75.6% read was an
  early-window artifact. Sample-floor discipline validated.
- **`min_confidence` KEEP** (+0.12R EV, n=1977; saved 881R vs missed 638R);
  `quiet_scalp_block` KEEP (+0.17R).
- **Shadow leader flipped:** SHADOW_MEAN_REVERT +0.44R avg, 54% win, n=290;
  S54's RANGE_FADE lead reversed (−0.07R, n=62). FUNDING_FADE confirmed bad.
- **Counterfactual sinks contained by gates:** MOVER_AVWAP_SCALP 0%/−0.95R
  (n=88), VOLUME_SURGE_BREAKOUT 2%/−0.64R (n=53), MOVER_TREND_PULLBACK −0.25R
  (n=2685, 4 emitted). Pruning evidence, not an emergency.
- **Emission drought persists:** ~10 emitted vs ~9,000 measured candidates;
  only QCB (+0.17R) and FUNDING_EXTREME (+0.57R) positive live. Volume-knob
  decision (S53 deferral) is becoming due.

### Follow-up sweep (same session, owner directive: "find ALL the bugs and test errors")

**Full audit of every `HistoricalDataStore.get_candles` consumer + every
boolean-context OHLCV array pattern in src/.** Four more numpy-truthiness
victims found and fixed (PR #727):

4. `trade_monitor._btc_opposes_direction` — BTC-correlation invalidation read
   fail-opened on every call (the env-gated adverse-tightening overlay AND its
   shadow logging were dead even where enabled). Data path repaired by #726's
   btc_direction fix; regression-pinned with a real numpy store. NOTE: the
   overlay stays dark (`INVALIDATION_BTC_CORRELATION_ENABLED` default false,
   has its own shadow branch) — no live behaviour change.
5. `trade_observer._get_reference_price` — returned None on every call.
6. `/market` Telegram command — BOTH primary and fallback branch broken; BTC
   price permanently "—". Fixed both.
7. `main._get_engine_context` — content-engine BTC price/1h/24h-change blanked
   forever. Fixed.
8. `scanner.diagnose_pair` — raised for any symbol WITH data (diagnosis broken
   exactly when there was something to diagnose). Fixed.
   Library hardening (same class, defense in depth): suppression_audit +
   invalidation_audit classify guards, volume_divergence inputs.
   Verified-safe (list-fed or len-guarded): all scalp.py evaluator sites,
   snapshot.py, alerts, kill switch, btc_state, cross-asset, macro gates.

**Test-suite debt cleared — the non-strict-xfail rot class.** 44 xfail markers
audited; every one was either contamination-blaming, stale-premised, or hiding
real rot:
- **Reload contamination fixed at the root**: test_pr04/test_pr06 rewrote
  reload-free (they deleted/re-imported config AND src.scanner mid-suite;
  their "default" assertions were circular — set the env then asserted it).
  All 28 cross-test-contamination xfails removed; suites green in CI order.
- **5 rotted tests found hiding under the blanket markers** (failing even in
  isolation, invisible because xfail): stale KZ-penalty expectations (kill_zone
  is profile-disabled), a 2-tuple patch of the 3-tuple cross-asset gate
  (which STILL hard-blocks — the xfail's "now soft-penalises" was a
  misdiagnosis), retired WATCHLIST tier, retired 360_SWING premise. Fixed or
  deleted with rationale.
- **pr01 "identity rewrite in dispatch" investigated: NO BUG** — FVG/ORDERBLOCK
  are `radar_only` by PR-04 governance so they never reach the queue; identity
  survives verbatim when rollout state is test-patched live. Tests fixed.
- Re-authored to current contracts: predictive SL-widening rejection
  (`sl_distance_widened` — new coverage), WHALE_MOMENTUM compress-cap
  telemetry, DIV_CONT TP1/TP2 dual-window geometry, SR_FLIP relative-penalty
  invariants, FUNDING_EXTREME QUIET non-block, min-SL floors via
  `_min_sl_distance_pct_for_setup`, lifespan/valid-for tables, "risk distance
  too tight" guard re-anchored to the reachable LSR protected-SL path.
- Deleted (premise retired, coverage exists elsewhere): SPOT/SWING channel
  tests (5), WATCHLIST reclassify, 360_SWING QUIET multiplier, two vacuous
  "no AI in pipeline" tests.

### NEXT

1. Owner: **verify kill switch re-enabled** from ops Control (S55 action;
   truth report shows last performance record ~3.7h old).
2. After a real window: review `BTC_DIR_SHADOW` would-fires (grep VPS logs /
   `btc_dir_shadow:*` counters) → flip `btc_dir_penalty_apply` from ops if the
   touched set looks right.
3. Geometry A/B now measuring for real — give it days before reading leaders
   (both arms ≥15 samples per strategy).
4. Unchanged: Telegram→app decouple (owner), volume knobs as live tunables
   (dark-first), Phase 4 master-arm (owner), `dispatch_staleness` action only
   if a fuller window re-sours.

---

## 🔴 SESSION 55 2026-07-13 — Engine-wedge → watchdog restart-storm → kill-switch incident fixed (branch `claude/pr-crypto-audit-review-a303z5`, 360-v2)

**Owner reported** (6 WATCHDOG Telegram screenshots, ~07:51–08:22 IST): repeating
`UNHEALTHY`, `scanner heartbeat 934s old`, `pricing-freshness 642s old`, then
`engine restart budget exhausted (3/h) … Escalating to kill switch — auto-trade
HALTS` firing every ~60s for 20+ minutes. **The kill switch is STILL engaged —
trading is halted until the owner re-enables it (owner-only by doctrine).** Engine
itself recovered 08:22; monitor-logs 04:15 UTC + Strategy Lab PDF 05:03 UTC confirm
healthy since.

### What actually happened (code-verified root cause)

1. **Primary — blocking Firestore read on the single asyncio event loop.**
   `RuntimeTunables._doc_values()` did a **synchronous** `.get()` on 5s-TTL expiry.
   Since #721 the scan loop calls `_rt.get(...)` per cycle, so a Firestore/network
   stall (client retry deadline = minutes) froze the **whole loop** — scanner
   heartbeat AND trade-monitor pricing publisher stopped **together**, exactly the
   observed twin-stall signature.
2. **Watchdog restart storm** — no boot grace; the `scanner_heartbeat` mtime
   **persists on the data volume across restarts**, so after its own restart the
   watchdog re-read the *pre-restart* age and re-killed the booting engine every 60s
   until the 3/h budget burned → kill switch.
3. **Page spam** — the budget-exhausted CRITICAL called `_page()` directly, bypassing
   the `dispatch_pages` cooldown → one identical page per loop.
4. **Contributor** — `StrategyEdgeStore.record()` did a full-store JSON dump *per
   record*; the 5-min classify batch (hundreds of records post #721/#722) ran
   hundreds of sync dumps + candle-copies on the loop thread.
5. **Healthcheck** — 180s grace vs a multi-minute REST re-seed of 75 pairs → UNHEALTHY
   flapping mid-boot → autoheal pile-on.

### Fixes shipped (all off the money path; kill-switch ENGAGE logic untouched)

- **`src/runtime_tunables.py`** — TTL expiry now **serves the stale cache instantly**
  and refreshes in a **single-flight daemon thread**; only the cold boot read fetches
  inline; failed refresh keeps last-known values; `set_values` merges into cache
  (no cold-fetch drop). Warns once/60s when the served cache is >60s stale.
- **`scripts/watchdog.py`** — `container_state()` returns `started_at` (parsed
  `State.StartedAt`); heartbeat/pricing ages **floored at engine StartedAt**; new
  `WATCHDOG_BOOT_GRACE_SEC` (600) disables the heartbeat-restart + blind-restart
  actions during warmup; budget-exhausted page is **cooldown-gated + silent while
  the kill switch is engaged** (engage still retried every loop until it lands);
  recovery re-arms the escalation page.
- **`src/strategy_edge.py` + `src/main.py`** — `record(..., persist=False)` + public
  `save()`; all three classify batches (invalidation, suppression, geometry) run via
  `await asyncio.to_thread(...)` with **one save per cycle** — the 5-min loop can
  never block the event loop again.
- **`healthcheck.py`** — grace 180→480s; a heartbeat mtime **older than the engine
  process** is treated as *warming up*, not stale (a genuine in-flight wedge — age ≤
  uptime — still fails). Made `main()` importable for tests.
- Tests: `tests/test_incident_2026_07_13.py` (new) + 11 new `test_watchdog.py`
  cases. Full suite green; ruff clean.

### ⚠️ OWNER ACTION REQUIRED
After this deploys and the engine shows healthy in ops, **re-enable auto-trade from
the ops Control page** (kill switch is owner-only to disengage — the watchdog has no
disengage path by design). Resting SL/TP on Binance protected open positions
throughout.

### Still open
- Issue **#714** — nightly encrypted backup failing since 2026-07-10 (no fresh
  off-site copy of the data volume). Separate item, high severity, untouched here.
- The exact 02:12-UTC first-trigger (what stalled Firestore) needs VPS logs, but the
  loop-blocking defect is real and fixed regardless of the trigger.

---

## 🟢 SESSION 54 2026-07-13 — Plan-vs-shipped audit + Stop-Geometry A/B wired (branch `claude/pr-crypto-audit-review-a303z5`, 360-v2 + 360ce-ops)

**Owner ask:** audit yesterday's PRs (#720/#721 + ops #62) against
`PLAN_AUTONOMOUS_PORTFOLIO.md`, the Crypto Market Doctrine, and the Strategy Lab
PDF (2026-07-13 05:03 UTC), and attend to the data.

### Audit verdict (verified in code, not PR bodies)

- Layers A–D + F, the 4 shadow units, tunables and truth-report sections: **all
  shipped and wired** as claimed.  Acknowledged deferrals stand: Telegram→app
  decouple (owner sign-off), volume knobs as live tunables (dark-first), Phase 4
  master-arm (owner).
- **One real gap found: Phase 3 item 8** — the fixed-% vs ATR/structure stop A/B
  for the *existing* evaluators (the plan's "single biggest edge lever") had only
  shipped for the 4 shadow units.  → closed this session (below).

### Strategy Lab first read (~12h window — directional only, sample floors rule)

- `dispatch_staleness` = **DROP** (n=717, **75.6% would-win**, 393R missed vs 66R
  saved, −0.46R/suppression) — the standout; acting on it is money-path →
  dark-first + owner sign-off, after a fuller window.
- `min_confidence` = TUNE (n=2202, ~neutral EV); `quiet_scalp_block` +
  `level_still_in_play` = KEEP (validated).
- SHADOW_RANGE_FADE 77%/+1.14R (31) — doctrine's range thesis leading;
  SHADOW_FUNDING_FADE 16%/−0.72R; FAILED_AUCTION_RECLAIM (live) −0.36R over ~438
  counterfactuals.  Allocator honestly cold in ASIA/QUIET/NORMAL/BTC_FALLING.

### Stop-Geometry A/B shipped (observe-only, Phase 3 item 8 measurement half)

- **`src/geometry_ab.py`**: pure ATR/structure stop math (`max(ATR14×1.5,
  pool_dist+buffer)` beyond the 20-bar swing extreme, 5% sanity clamp) +
  `stamp_geometry_pair` — every post-scoring candidate (emitted AND suppressed)
  stamps `X@FIXED` (live stop) + `X@ATR` pairs into a **dedicated ledger**
  (`data/geometry_ab_candidates.json`, own bound — can't evict gate records),
  per-(symbol,setup,side) 10-min pair cooldown, fail-open.
- Scanner: `_stamp_geometry_ab` hooks in `_stamp_suppressed` (own tunable — runs
  even with the suppression audit off) and on successful enqueue; the would-be
  stop is stamped on the signal (`Signal.geo_atr_stop`, consumed by nothing).
- 5-min audit loop classifies the pair ledger with the same TP1-before-SL
  classifier → edge matrix rows (`source="shadow"`).  **Allocator excludes
  `@FIXED`/`@ATR` rows** — measurement arms are never activatable.
- Truth report: `## Stop-Geometry A/B` (per-strategy pooled arms, ΔR, leader —
  leader named only when BOTH arms ≥15 samples); strategy rollups exclude
  variants (no double-counting).  Tunable `geometry_ab_enabled` ("Measurement").
- Ops `/strategy-lab`: new **Stop-geometry A/B card** (`reduce_geometry_ab`,
  engine-parity port; per-strategy rollup also excludes variants now).
- Tests: engine **6383 passed** (+22, incl. the doctrine scenario: wick to 98.7
  clips the 99.0 fixed stop, the 98.5 ATR stop survives to TP), ruff clean, mypy
  103 (< 113 baseline); ops **345 passed** (+3).  Fixture-ran
  `scripts/build_truth_report.py` — section renders with a real leader row.

### Follow-ups

- **Geometry application half** (owner sign-off, dark-first): wire the measured
  winner into live SL placement + `risk_scale` sizing once a real window names
  leaders per strategy/context.
- `dispatch_staleness` gate action after a fuller window (money-path, owner).
- Unchanged from S53: Telegram→app decouple; volume knobs as live tunables;
  Phase 4 master-arm.

---

## 🟢 SESSION 53 2026-07-12 — Autonomous Portfolio Phases 1–3 wired end-to-end: shadow ledger live, 4 shadow strategy units, allocator (recommendation mode), ops Strategy Lab (branch `claude/realtime-strategy-testing-ops-r318yu`, 360-v2 + 360ce-ops)

**Owner directive:** "use the time — try different strategies with real data in real
time with ops."  Foundation PR #720 (market_context / strategy_edge /
suppression_audit modules) was open-unmerged with nothing wired; merged it first
(CI green, observe-only), then wired the whole measurement pipeline.  **Everything
this session is observe-only / off the money path — zero change to which signals
emit or how they score.**  Scope selections (owner): core + allocator observe-only +
new strategy families.

### Engine (360-v2) — the measurement pipeline

- **Shadow ledger wired end-to-end:** `Scanner._stamp_suppressed` (fail-open,
  tunable-gated) stamps full geometry at all 8 post-scoring suppression gates
  (quiet_scalp_block, min_confidence/component floors, active_dup real branch only,
  dispatch_cooldown, data_stale, dispatch_staleness, level_still_in_play,
  regime_kill).  The 5-min `_invalidation_audit_loop` piggybacks
  `classify_pending()` (same in-memory `fetch_ohlc_since`) and feeds resolved
  outcomes into `StrategyEdgeStore` (`source="suppressed"`).
- **Latent bug fixed while relocating the mc stamp:** the #720 market-context stamp
  ran BEFORE `_populate_signal_context`, so `entry_regime` was always empty →
  Wyckoff phase always AMBIGUOUS.  Populate + mc stamp now both run above the QUIET
  gate; every suppressed candidate carries real regime + context key.
- **Real emitted outcomes feed the same matrix:** `trade_monitor._record_outcome`
  records into `StrategyEdgeStore` (`source="emitted"`, R from
  `original_sl_distance` — un-ratcheted risk), skipping EXPIRED_NO_FILL.
  `StrategyOutcome` gained provenance (`emitted|suppressed|shadow`); matrix rows
  expose `n_emitted/n_suppressed/n_shadow` so counterfactual vs realised edge is
  never conflated.
- **4 shadow-only strategy units** (`src/shadow_strategies.py`): SHADOW_RANGE_FADE,
  SHADOW_MEAN_REVERT, SHADOW_FUNDING_FADE, SHADOW_CASCADE_REVERSAL — pure functions,
  ATR-sized stops beyond the trigger extreme (doctrine §4), NO path to the signal
  queue; stamped as `gate_name="shadow_unit:*"` → classified → matrix
  (`source="shadow"`).  Per-(unit,symbol) 30-min stamp cooldown (monotonic,
  None-sentinel — a 0.0 sentinel silently swallowed all stamps for the first 30 min
  after boot; caught by test).
- **Strategy registry** (`src/strategy_portfolio.py`): context-affinity tags
  (phases/sessions) for all 27 SetupClass values + 4 shadow units;
  `is_context_aligned()`; single source of truth persisted to ops.
- **Allocator, RECOMMENDATION MODE** (`src/strategy_allocator.py`): every audit
  cycle reads current context × matrix verdicts → would-activate list (weights
  proportional to edge, alignment bonus ×1.2/×0.8) bounded by the safety envelope
  IN the math (`ALLOCATOR_MAX_CONCURRENT_STRATEGIES`=6,
  `ALLOCATOR_MAX_STRATEGY_WEIGHT`=0.35; capped surplus stays unallocated) + a
  would-demote list (NEGATIVE cells).  Persisted to
  `data/strategy_allocations.json`; **consumed by nothing** — Phase 4 master-arm is
  a later owner decision.
- **Publishers (5-min loop):** `data/market_context.json` (global BTC-anchored
  vector + affinity map) and `data/strategy_allocations.json`, atomic writes.
- **Truth report:** new `## Suppression Quality Audit` (per-gate WOULD_WIN% / EV-R /
  KEEP-TUNE-DROP) and `## Strategy × Context Edge Matrix` sections;
  `vps-monitor.yml` fetches `suppressed_candidates.json` + `strategy_edge_store.json`.
- **Tunables ("Measurement" category):** `market_context_enabled`,
  `suppression_audit_enabled`, `shadow_strategies_enabled`,
  `allocator_recommend_enabled` — all observe-only, live-flippable from ops.
- Tests: 6361 passed full suite; ruff clean; mypy at/below baseline.  New suites:
  portfolio registry, shadow units, allocator caps/floors, suppression wiring
  (incl. classify→edge end-to-end), trade-monitor edge feed, truth-report sections.

### Ops (360ce-ops) — Strategy Lab page

- New `/strategy-lab` (+ 60s HTMX partial): current context vector card (with
  staleness badge), Strategy×Context edge matrix (Wilson edge + verdict badges +
  emitted/suppressed/shadow split + in/out-of-design-context fit badges),
  per-strategy rollup, suppression-gate KEEP/TUNE/DROP table, and the allocator's
  "what it would do now" panel (mode RECOMMENDATION_ONLY, caps shown).  Data from
  the read-only volume (4 new accessors); engine math ported (~40 pure lines,
  thresholds displayed in footer); affinity comes from the engine-persisted map —
  zero hardcoding.

### Cost discipline

Stamps are O(1) in-memory appends; shadow units are pure list scans on already-warm
candles with per-symbol cooldowns; classification + all file writes batched on the
existing 5-min loop; tunables reads are the existing 5s-TTL cache.  No new network
or Firestore reads anywhere.

### Follow-ups (out of scope this session)

- Telegram→app-push decouple in `signal_router.py` — **owner sign-off (routing)**.
- Making QUIET-penalty / cooldown / min-confidence live tunables — money-path
  consumption change, dark-first.
- Phase 4 master-arm — owner flips only after the allocator's recommendations prove
  out in Strategy Lab on a real data window.
- Matrix/report verdicts need a fresh data window before they mean anything —
  don't judge the shadow units or gate verdicts until cells pass sample floors.

---

## 🟢 SESSION 52 2026-07-11 — 100eyes-parity Alerts v3: universe gate, honest touch counts, zone charts, card thumbnails (branch `claude/eye-scanner-alerts-charts-8xddta`, 360-v2 + lumin-app)

**Owner report (screenshots, 12:25 IST — one hour after S51 merged):** feed still
too busy ("look at exactly 100eyes"), small caps alerting (SKYAI/NAORIS/GRASS/GUN),
"(523 touches)" junk levels, alert-tap "still opens a normal chart", "still no auto
trade entry from chart".  Two causes: (a) S51 curated PUSH but left the FEED open to
all 75 pairs and the LevelBook's chop-inflated touch counts; (b) the owner's phone
runs a build predating S51's app PR #117 — the overlay + Take-trade button exist but
were never installed (in-app update banner is manual; told owner to update).

**Owner decisions (AskUserQuestion):** universe = majors+midcaps (≥$50M/day 24h vol,
tunable); NO global feed cap — fix junk quality floors instead; Take Trade stays
entry-only as S51 built it; alert cards get native mini-chart thumbnails.

### Engine (360-v2 PR #718 — off the money path, LevelBook untouched)

- **Universe gate:** `ALERTS_MIN_VOLUME_24H_USD` (50M default, ≤0 disables) —
  AlertService takes `volume_24h_getter` (PairManager dict lookup, no I/O);
  fail-closed on unknown volume.
- **Near-level honesty:** `_distinct_touch_events` state machine — consecutive
  in-band bars = ONE touch; re-arm needs `ALERTS_NEAR_LEVEL_MIN_SEPARATION_BARS` (3)
  out-of-band bars AND a close ≥ `ALERTS_NEAR_LEVEL_MIN_LEAVE_PCT` (0.5%) away.
  Chop rejection: > `ALERTS_NEAR_LEVEL_MAX_IN_BAND_FRAC` (25%) of lookback in-band →
  it's a range, no alert.  Enumerates `get_levels()` (not score-biased
  `nearest_level`) so junk can't shadow a clean level.
- **Zone geometry on the wire:** `zone_low/zone_high/touch_count/
  first_touch_bars_ago/last_touch_bars_ago` in metrics; back-compat keys kept,
  `touches` now honest (fixes "523×" titles on old app builds too).
- **Feed hygiene:** `_load` drops pre-v3 NEAR_* junk; first sweep lazily purges
  restored sub-gate symbols (can't purge in `_load` — PairManager volumes only
  exist after boot `refresh_pairs()`).
- Tests 57 (14 new); full suite 6240 passed.

### Lumin app (same branch, second PR)

- **100eyes chart from an alert:** shaded zone RECTANGLE via lightweight-charts
  ISeriesPrimitive (`attachPrimitive` verified in the bundled v4.2.3 standalone);
  divergence trend line mirrored on the RSI band (`priceScaleId: "rsi"`, values
  from `rsi_first/rsi_second`); `focus` visible-range zoom to the setup window
  (no more fitContent's 500 bars).  `AlertChartOverlay.fromAlert(chartTf:)` only
  emits time-anchored geometry on the alert's own TF (fixes latent wrong-TF draw).
- **Card thumbnails:** `AlertThumbnail` CustomPainter (no webview) — candles +
  zone box + divergence line + fired marker; `KlinesThumbnailService` (Binance
  public REST direct from phone, zero engine/GCP cost) with memory TTL cache,
  in-flight dedup, 3-fetch concurrency gate, SharedPreferences LRU disk layer;
  per-alert-id memo so scroll-back never refetches.  Alerts feed converted to
  `ListView.builder` (was eager ListView — 100 thumbnail cards must be lazy).

### Owner action required

**Install the app update** (in-app update banner / latest GitHub release APK) —
the S51 + S52 app features are invisible on the pre-#117 build on the phone.

---

## 🟢 SESSION 51 2026-07-11 — Alert spam cut + alert→chart setup sync + entry-only Take Trade (branch `claude/alerts-spam-chat-sync-pqemei`, 360-v2 + lumin-app)

**Owner directive (with screenshots):** the day-one Alerts feed spams (same
symbol firing volume+volatility+RSI at once, "1 touches" junk levels, every
15m wiggle buzzing the phone); tapping an alert must open the chart on the
ALERT's timeframe with the alert's indicators and the exact setup drawn, no
manual effort; and an alert-detail "Take trade" that places ENTRY ONLY (owner
explicit: no SL, no TP).

### Engine (all off the money path — scoring/dispatch/FSM/paid-routing untouched)

- **Quality floor:** `ALERTS_NEAR_LEVEL_MIN_TOUCHES` (default 3) — near-S/R
  alerts on 1-2-touch "levels" no longer fire (the worst spam class in the
  owner's screenshots).
- **Same-event coalescing:** volume spike + abnormal volatility from the same
  (symbol, TF) sweep = one market event → keep the volume card (it carries the
  move %), drop the volatility echo.
- **Per-symbol cross-type budget:** `ALERTS_SYMBOL_MAX_PER_WINDOW` (2) per
  `ALERTS_SYMBOL_WINDOW_SEC` (3600) — one violent candle can't stack cards for
  the same coin. Priority when the budget binds: divergence > near-level >
  RSI extreme > volume > volatility, and 4h > 1h > 15m. Budget rejections do
  NOT consume the type cooldown (the alert can still fire later).
- **Push curation (the real "spam" fix):** feed keeps everything (pull-based,
  filterable in-app, mirrors 100eyes); the PHONE only gets
  `ALERTS_PUSH_TIMEFRAMES` (default `1h,4h`) capped at
  `ALERTS_PUSH_MAX_PER_HOUR` (12). 15m alerts are feed-only now.
- **Divergence pivot geometry on the wire:** `pivot_a/b_bars_ago` +
  `pivot_a/b_price` in divergence metrics so the app draws the actual
  divergence line. Additive metrics — older apps unaffected.
- Tests: `tests/test_market_alerts.py` grown to 39 (floor, coalescing, budget
  priority, cooldown-not-consumed, push TF gate, push hourly budget).

### Lumin app (same branch)

- **Alert→chart sync:** `ChartPage(alert:)` opens on the alert's timeframe,
  auto-enables RSI for RSI-class alerts (session-only, saved prefs untouched),
  and draws the setup via the new `setAlertOverlay` JS bridge: solid S/R level
  line titled "Support · 43×" + alert-price reference, divergence pivot
  segment, alert-candle marker. `AlertChartOverlay`
  (`lib/features/charts/models/alert_overlay.dart`) owns the math (bars-ago →
  bar times). Alert context bar under the chart shows what fired + Take trade.
- **Feed filters (100eyes UX):** chip row on the Alerts tab — family
  (RSI / Divergence / S/R / Volume) + timeframe, client-side, session-only.
- **Take trade (entry-only):** `TakeAlertTradeSheet` →
  `OrderExecutor.placeAlertEntry` — market entry ONLY on the user's own
  device-key custody (same class as Take Signal manual trades; engine never
  manages the position). Sizing = Auto-trade settings (pct × leverage on live
  equity). Side pre-seeded from alert bias; NEUTRAL alerts force a pick.
  Idempotent on alert_id (log + broker clientOrderId). Unmissable no-SL/no-TP
  warning in the sheet; confirm button itself says "no SL / no TP".
  **CTE note for owner:** this is deliberately outside the engine's
  naked-position invariant (that guards ENGINE-managed positions); an
  alert-take is a user-initiated manual trade the user must close themselves.
  The engine-side pre-TP `protect_manual_entries` passive watcher still
  applies where auto-trade is connected. If we see users leaving these naked
  overnight, next step is an optional default-ON emergency stop % in the
  sheet.

---

## 🟢 SESSION 50 2026-07-11 — Market Alerts (Pulse → Alerts tab) + full FCM push (branch `claude/alerts-app-new-tab-ojlkps`, 360-v2 + lumin-app)

**Owner directive:** Pulse gets two top tabs — Dashboard (existing) + **Alerts**,
a 100eyes-Crypto-Scanner-class informational feed; detectors fire on their
NATURAL timeframe (some 4h, some 1h, some 15m, per the owner's screenshots);
and **full production FCM for all alerts and signals**.

### Engine (all off the money path — scoring/dispatch/FSM/paid-routing untouched)

- **`src/alerts/`** — detector pack + service:
  - Detectors (`detectors.py`, pure numpy on in-memory candles — **zero
    network I/O per sweep**): RSI Extremely Overbought/Oversold (15m/1h/4h,
    80/20), RSI Bullish/Bearish Divergence (1h/4h; strict fractal pivots +
    RSI zone gates + recency gate), Abnormal Volatility (15m, TR ≥ 3×prior
    ATR(14)), Abnormal Volume (15m, ≥5× 20-candle mean), Near Horizontal
    Support/Resistance (1h, LevelBook `nearest_level` ≤0.3%).
  - `AlertService` (`service.py`): own asyncio task (60s sweep, launched in
    bootstrap — can never slow the scanner), per-(symbol,type,TF) cooldowns
    (TF-relative for RSI types, wall-clock for hover-prone types), stale-feed
    guard (never alerts on frozen candles — S44/S49 class), closed-candle
    dedupe, ring buffer 300, persistence to `data/alerts.json` (feed AND
    cooldowns survive deploys — no re-push storm on restart).
  - All thresholds env-tunable (`ALERTS_*` block in config).
- **`/api/alerts`** — auth-gated, filters (type/symbol/limit), Cache-Control.
  Isolated mode fully wired: SnapshotWriter publishes `snapshot:alerts` every
  ~30s → RedisEngineFacade `published_alerts()` → route prefers the snapshot
  (mirrors positions_diag pattern).
- **`src/push_notifications.py`** — FCM via firebase-admin (already a dep;
  same service account as Phone Auth). **Topic-based** (`alerts`, `signals`)
  so there is NO device-token registry server-side. Contract: never blocks
  (send on worker thread), never raises, global rate cap
  (`FCM_MAX_SENDS_PER_MIN` 60), silent no-op when Firebase isn't initialised.
  Hooks: SignalRouter post-delivery (new signal), TradeMonitor
  `_record_outcome` (terminal outcomes, EXPIRED_NO_FILL excluded). Per-class
  gates: `FCM_PUSH_ALERTS/SIGNALS/OUTCOMES_ENABLED`.
- **Tests:** 40 new (detectors incl. divergence geometry + zone/recency
  gates, service cooldown/staleness/persistence, push contract, route +
  snapshot plumbing). Full suite **6215 passed**, ruff clean, mypy delta 0.

### Lumin app (same branch)

- **Pulse → two top tabs**: Dashboard (existing content, untouched) +
  **Alerts** — card feed (bias-coloured icon, symbol, TF chip, relative age),
  SWR-cached `/api/alerts` (30s TTL + disk persist), pull-to-refresh,
  keep-alive, empty/error states; tap a card → the symbol's Chart page.
  Mock mode has fixture alerts.
- **FCM end-to-end** (`lib/data/notification_service.dart`): topic
  subscribe on boot from persisted prefs (default both ON), Android 13
  permission request, foreground pushes → SnackBar with VIEW action
  (background/killed display is automatic via notification payload),
  tap routing — `signals` → Signals tab, `pulse_alerts` → Pulse → Alerts
  top tab (cold-start taps included). **Menu → Notifications** page with
  per-class toggles (off = unsubscribe: delivery stops at FCM).
- **CI:** `build-apk.yml` injects `POST_NOTIFICATIONS` into the manifest
  (same pattern as INTERNET). `firebase_messaging ^15.1.0` added.
- Analyzer 0 errors; **169 app tests pass** (9 new MarketAlert tests).

### Ship notes / owner verify after deploy

1. Engine logs: `AlertService started`, first `ALERT <SYM> ...` lines;
   `redis-cli GET snapshot:alerts` non-empty; app Pulse → Alerts populates.
2. FCM: needs `FIREBASE_SERVICE_ACCOUNT_PATH`/`FIREBASE_PROJECT_ID` set (they
   already are for Phone Auth). Watch for `push: Firebase Admin not
   initialised` warnings — that means pushes are off.
3. First **release build** must include the google-services secret as usual;
   verify a real device receives a signal push + an alert push, and that the
   Menu → Notifications toggles stop delivery.
4. Alert volume: watch a day of `ALERT` lines; if noisy, raise cooldowns via
   env (`ALERTS_*_COOLDOWN_*`, `ALERTS_RSI_OVERBOUGHT/OVERSOLD`, multipliers)
   — no redeploy of code needed beyond env.

---

## 🔴 SESSION 49 2026-07-10 — P1: TAIKO SL overshoot root-caused — Binance decommissioned our legacy WS URLs (branch `claude/taiko-sl-overshoot-6lds39`)

**Owner report (screenshot):** TAIKOUSDT LONG (MVRTP-8ABCA1F2, entry 0.09074,
SL 0.09060) still ACTIVE at 0.08721 — **3.7% past the stop, never closed**.
Same state on APEUSDT + POWERUSDT (issue #712; the new S48 F-07 pager fired
correctly on both GitHub and the alert Telegram bot — the detection layer works).

### Root cause (real-data-first: probe → vendor changelog → ecosystem confirmation)

Binance's **2026-03-06 USDⓈ-M Futures WebSocket System Upgrade** split WS
traffic into routed base paths (`/public`, `/market`, `/private`) and
**decommissioned legacy unrouted URLs after 2026-04-23**. Legacy connections
still complete the TCP+WS handshake but *market/private-category streams never
push a single frame* — silent death, no exception, so reconnect/backoff never
fires. Enforcement evidently reached our long-lived connections recently.

- `websocket_manager` / `BINANCE_FUTURES_WS_BASE` were **already migrated**
  (2026-05-14 incident) → scanner klines healthy, which masked the rest.
- `src/execution/mark_price_feed.py` was **missed**: still
  `wss://fstream.binance.com/ws/!markPrice@arr@1s` → feed "connected" with an
  **empty price map**. Everything downstream starved silently: the #706
  stale-candle→mark-price SL/TP fallback (blind on out-of-universe symbols —
  TAIKO's kline age was None after the day's deploy restarts), **pre-TP
  dispatch, trailing, funding-exit watcher** (`missing_funding_rate=264` in the
  truth report is the same outage).
- `src/execution/user_data_stream.py` was **also missed**: legacy
  `/ws/<listenKey>` → **FSM order-fill events (real money) not delivered**;
  only the REST Reconciler was compensating.
- The Lumin app polls `fapi/v1/premiumIndex` REST directly — that's why the
  owner's phone showed the real price while the engine was blind.

### Shipped on this branch

1. `mark_price_feed`: routed URL (`/market/ws/!markPrice@arr@1s`,
   env `MARK_PRICE_FEED_WS_URL`) + legacy-override auto-correct (same defence
   websocket_manager has) + **silence watchdog** — the @1s stream ticking
   nothing for `MARK_PRICE_FEED_SILENCE_TIMEOUT_SEC` (30s) now ERROR-logs and
   force-reconnects: silence can never look like health on the SL/TP path again.
2. `user_data_stream`: routed private URL
   `/private/ws?listenKey=<key>&events=<all legacy event types>` — the
   `events` param is REQUIRED in production (omitting it delivers nothing;
   field-confirmed by unicorn-binance-websocket-api). Default list mirrors
   legacy implicit-all, so parser behaviour is unchanged.
3. Regression pins: routed-URL contracts for both modules, legacy-path
   normalisation, silence-watchdog raise + healthy-path no-raise. Full suite
   green; ruff/mypy clean.

### On deploy (expected behaviour — tell the owner)

Engine restart → feed connects routed → mark prices flow → the blind ACTIVE
signals (TAIKO/APE/POWER) get repriced via the #706 fallback and **close
immediately at the real mark price**, recording the true overshot loss (TAIKO
≈ −3.9%, not the −0.15% SL). That is honest telemetry, not a bug. Verify in
logs: `mark_price_feed: receiving (N symbols in first frame)` and
`user_data_stream: connecting to wss://fstream.binance.com/private/ws?...`.

### Open follow-ups

1. **Verify user-data stream live after deploy** — watch for ORDER_TRADE_UPDATE
   events on the next real fill (Reconciler covers the gap meanwhile).
2. **REST `premiumIndex` fallback as third pricing tier** for the monitor when
   both kline + mark feed are dead (the app already proves it works) — new
   money-path pricing source, so dark-first + owner sign-off; not shoved in here.
3. Owner NEXT items from S48 unchanged (alert-bot secrets done per screenshot;
   healthchecks.io + host setup + drill still pending).

---

## 🟢 SESSION 48 2026-07-10 — Autonomous self-healing ops stack (branch `claude/audit-report-implementation-knx1h1`)

**Owner directive:** "we need an autonomous system — I'm only the one handling
all this, one can't observe all: self checks, self heal-up, self restart,
freezing issues, VPS issues. First go through the web to find what we can do."
Plus: **Telegram is fully operational in India again** → Telegram is the
paging channel (not ntfy/FCM).

**Researched first** (web): the standard single-node self-healing pyramid —
deep healthchecks → autoheal → custom supervisor → phone paging → external
dead-man's switch → host self-maintenance. Full design + rollout in
**`docs/AUTONOMOUS_OPS.md`** (the doc to read before touching any of this).

### Shipped (all off the money path — scoring/dispatch/FSM untouched)

- **Authority doctrine:** the autonomous machinery takes *risk-reducing
  actions only* — page / restart / prune / ENGAGE kill switch. It can never
  disengage, reset a breaker, or re-enable trading (source-level test pins
  the no-disengage property).
- **Layer 1:** redis + api containers got real healthchecks (ping /
  `/api/health` HTTP round-trip); engine already probed heartbeat freshness.
- **Layer 2:** `autoheal` sidecar (pinned 1.2.0) restarts any
  `autoheal=true` container that goes unhealthy — the "alive but frozen"
  class (S44/45/46) now self-recovers. Watchdog deliberately not labeled.
- **Layer 3:** new `watchdog` container (`scripts/watchdog.py`, stdlib-only,
  60s loop, docker.sock + data volume): container states, wedged scan loop
  (→ budgeted engine restart, 3/h), **audit F-07 blind-open-position pager**
  (stale 1m kline AND no mark price → page; persisting → engine restart,
  which re-seeds candles = the manual MVLLUSDT fix automated), breaker-trip
  paging (never resets), disk 85%/92% (page/auto-prune), memory pressure,
  budget-exhausted → **kill-switch engage** via API owner token + CRITICAL
  page. Dedupe 30min/key + ✅ recovery notices; audit JSONL + persisted state.
- **Engine feed for F-07:** trade monitor publishes
  `data/pricing_freshness.json` every 30s (`PRICING_FRESHNESS_PUBLISH_SEC`,
  local disk, hot-path clean); `monitor_heartbeat.py` gained
  `check_pricing_freshness()` → INVARIANT_WARN (hourly path pages too).
- **Layer 4:** `scripts/notify_telegram.py` (stdlib, never raises, never
  leaks token; `ALERT_TELEGRAM_CHAT_ID` else `TELEGRAM_ADMIN_CHAT_ID`);
  `vps-liveness.yml` + `vps-backup.yml` now page Telegram (problems AND
  recovery) alongside the auto-detected issue. **Owner chose a dedicated
  alert bot** → set `ALERT_TELEGRAM_BOT_TOKEN` + `ALERT_TELEGRAM_CHAT_ID`
  (repo secrets AND `.env`); falls back to `TELEGRAM_BOT_TOKEN` /
  `TELEGRAM_ADMIN_CHAT_ID` when unset. In-engine alerts
  (tripwires/breaker/kill-switch via telegram_alerts.py) stay on the
  engine bot by design.
- **Layer 5:** healthchecks.io dead-man pings from the watchdog loop
  (`HEALTHCHECKS_PING_URL`) + a host cron — external phone page when the
  whole box dies (~5 min). Also fixes audit F-20 (GitHub-only alerting).
- **Layer 0:** `deploy/host/setup_host.sh` (idempotent, as-code — audit
  S-7): swap, earlyoom, unattended-upgrades, fail2ban, ufw,
  `360scalp.service` (stack up after reboot via deploy.sh), nightly prune,
  dead-man cron.

**Tests:** 6168 passed (was 6120) — new: watchdog decision ladder,
notifier contract, F-07 publisher contract, heartbeat pricing checks.
Ruff clean, mypy delta zero, compose config validates (both profiles).
The dedupe test caught a real bug (fresh findings suppressed inside the
first cooldown window) — fixed before ship.

### Ops dashboard upgrade (same session, 360ce-ops branch `claude/audit-report-implementation-knx1h1`)

- **/audit** — audit-findings board: F-01..F-20 + S48 extras with colour-badged
  done/partial/open/owner status, needs-attention-first sort, summary-counter
  filters. Backed by `app/audit_findings.py` — **update it at session end**
  whenever a finding's status changes (same discipline as this file).
- **/data** — full read-only file browser of `/engine-data` (size + colour-coded
  write recency as a liveness readout) + raw downloads via `/data/raw/{path}`
  (resolve-then-contain traversal guard, tested).
- **Coloured badges** (signal lifecycle, severity, audit status) + **sortable
  tables site-wide** (`static/sort.js`, numeric-aware) + Signals lists open
  positions first (engine `is_open` stamp, heuristic fallback).
- Ops suite 327 passed (was 311).

### NEXT (owner, ~20 min total — the paging is inert until 1+2 are done)

1. Create the alert bot (@BotFather), DM it once, get the chat id from
   `getUpdates`; add `ALERT_TELEGRAM_BOT_TOKEN` + `ALERT_TELEGRAM_CHAT_ID`
   as repo secrets AND in the VPS `.env`.
2. healthchecks.io: two free checks → `HEALTHCHECKS_PING_URL` in `.env` +
   URL for setup_host.sh; install their app (or Telegram integration).
3. `bash deploy.sh` (brings up autoheal + watchdog), then
   `sudo REPO_DIR=$(pwd) bash deploy/host/setup_host.sh`.
4. **Drill it**: `docker pause 360scalp-v2-engine` → expect unhealthy →
   autoheal restart → phone page within ~2 min. An untested pager is a hope.
5. Session-46/47 open items unchanged (diag_paper_health root-cause on VPS;
   BACKUP_PASSPHRASE secret + first restore drill; ops TOTP enroll).

---

## 🟢 SESSION 47 2026-07-10 — Institutional audit + production-grade remediation sweep (branch `claude/crypto-audit-institutional-tic0ix`, all 3 code repos)

**Owner asked:** full institutional-grade audit of the whole stack, then "fix
everything actually what you can like production grade."

### Delivered part 1 — the audit

`docs/INSTITUTIONAL_AUDIT_2026_07_10.md` — 16-section audit across all four
repos (architecture, security, trading engine, signal quality, exchange
integration, auto-trade, mobile, infra, compliance, continuity, competitive
benchmark, findings table F-01..F-20, priority roadmap, scores). Verdict:
**Early Production**; risk HIGH; the three blockers to Production Ready are
(1) unproven net edge, (2) no backups/DR + bus factor 1, (3) no legal
entity/counsel. All figures sourced from our own telemetry.

### Delivered part 2 — remediations shipped on this branch

**360-v2** (all off-money-path: docs, infra, telemetry, API perimeter):
- **F-02 backups/DR:** `scripts/backup_data.sh` (WAL-safe SQLite snapshot via
  stdlib backup API → tar → AES-256-CBC pbkdf2 encrypt → verify → rotate 14)
  + `scripts/restore_data.sh` (refuses under a running engine; preserves
  prior state in `.pre_restore_<stamp>`) + nightly `vps-backup.yml` (SSH,
  pulls encrypted artifact off-box 30d, files `severity:high` auto-detected
  issue on failure, self-closes on success). **Needs new repo secret
  `BACKUP_PASSPHRASE`** (same value into the password manager).
- **F-02/F-04 docs:** `docs/DR_RUNBOOK.md` (RTO 2h/RPO 24h, scenarios A–D,
  drill log), `docs/SAFE_HALT_RUNBOOK.md` (non-engineer kill-switch
  procedure), `docs/CONTINUITY_PACK_TEMPLATE.md` (vault checklist),
  `docs/STATISTICAL_CHANGE_POLICY.md` (n≥200/21d bar, frozen control,
  proof-window discipline — binds future sessions).
- **F-14 API rate limiting:** `src/api/rate_limit.py` + wired in
  `server.py` — per-client (Bearer-hash else first-hop XFF IP) sliding
  window, 240/min default, health paths exempt, bounded memory, 429 +
  Retry-After. Env: `API_RATE_LIMIT_ENABLED/_PER_MIN/_MAX_CLIENTS`.
  18 new tests; full api suite green.
- **F-11 signing socket:** 0666 → **0660 + chgrp appgroup** (both containers
  share the image so the group exists; env `SIGNING_SERVICE_SOCKET_GROUP`);
  dev/test fallback to 0666 with loud warning. ⚠️ **Owner-sign-off item
  (signing service) — merge of this branch is the sign-off; verify engine
  connects after deploy** (`test -S` + a signed request in logs).
- **F-09 paper-silence paging:** `monitor_heartbeat.py` rewritten (env
  `ENGINE_DATA_DIR`, testable) + new check — engine perf file fresh (<6h)
  while ALL paper ledgers frozen (>24h) → `INVARIANT_WARN` line;
  `vps-liveness.yml` now pages on ANY `INVARIANT_WARN:` (future checks
  need no workflow change). 10 new tests.

**360ce-ops** (same branch): **F-08 TOTP 2FA** — stdlib RFC 6238
(`app/totp.py`, RFC test vectors), ±1-step drift, replay-protected,
enabled via `OPS_TOTP_SECRET` (enroll: `python scripts/generate_totp_secret.py`),
wired into BOTH login paths (web form field appears when enabled;
`/api/v1/auth/login` takes `totp`); failures return the same generic
message on either factor. Unset env = password-only (safe rollout).
Full ops suite green (311).

**lumin-app** (same branch): **F-12 obfuscation** — `--obfuscate
--split-debug-info` on BOTH the APK and AAB builds in `build-apk.yml`;
symbol maps uploaded as 90-day artifact (`flutter symbolize` for crash
traces). ⚠️ First obfuscated release: smoke-test Phone Auth + Play Billing
on a real device before promoting (reflection-adjacent plugins).

### Deliberately NOT done here (and why)

- **F-05 FSM LIMIT-at-zone / F-06 portfolio cap** — money-path FSM/dispatch
  design work, owner-sign-off items with their own spec docs; not
  shove-in-able alongside a hardening sweep.
- **F-13 remove in-app updater** — the GitHub-release APK path may still be
  a real distribution channel for pre-Play installs; removal is a
  distribution decision for the owner (audit recommends retiring it).
- **F-15 JSON→transactional store, F-10 owner-key split** — need design;
  JWT crypto itself verified sound (constant-time, alg-pinned, exp-checked).
- Legal entity / counsel / second operator — not code.

### NEXT

1. Owner: add `BACKUP_PASSPHRASE` secret → run backup workflow once → do the
   first restore drill (DR_RUNBOOK) + fill the continuity vault.
2. Owner: enroll TOTP (`generate_totp_secret.py` → env → redeploy ops).
3. Verify after deploy: signing socket 0660 connect OK; rate limiter logs
   sane; first liveness run shows the paper-books line.
4. S46 open item unchanged: run `diag_paper_health.py` on the VPS to
   root-cause the paper freeze (the new invariant only *detects* it).
5. Then the S46 verify-on-live-data list (mover re-seed, BE arm, is_open).

---

## 🟢 SESSION 46 2026-07-10 — Day-after-#707 production incident sweep (frozen mover price, dead BE arm, open/closed display truth, frozen paper book)

**Owner reported 7 symptoms** (screenshots + ops PDFs): paper trading frozen
~24h; actives should sort first; MVLLUSDT "reached >TP3 but shows closed at
TP1"; volume down to ~12/24h; Signals(12) vs Profit(7) mismatch; "TPs/SLs hit
but nothing happens"; "+2% runs going back to full −2.5% SL, no BE, no trail".
Branch (all three repos): `claude/paper-trade-frozen-signals-pamcw8`.

### Root causes found (code-verified)

1. **MVLLUSDT frozen price / blind SL-TP-trail** — promoted movers have NO WS
   kline subscription; their only candle writes are REST seeds, and seeds
   never stamped `_last_kline_update_ts`. `last_kline_age_seconds()` = None
   forever → BOTH staleness protections (scanner dispatch gate #359 +
   trade_monitor mark-feed fallback #706) fail-open on None. MVLL's close
   froze at 38.1800 for 11+ h with an open TP1_HIT runner: PnL/MFE pinned at
   +4.63%, TP2/TP3 detection blind, trail immobile, SL backstop dead. This is
   ALSO the "TPs/SLs hit but nothing happens" complaint, and it means mover
   evaluators were reading up-to-6h-frozen candles for their whole hold.
   **FIXED:** REST seeds/gap-fills stamp freshness; `_candle_stale` treats
   age-None as stale after a post-boot grace; scanner re-seeds active movers
   when 1m age > `MOVER_CANDLE_REFRESH_SEC` (120s, bounded/throttled).
2. **BE never armed on wide-stop signals** — #702's arm = max(flat 1%, 1R of
   own stop, 0.75×noise) double-counts the #702 noise-floor stop WIDENING: 1R
   of a widened 2.4-2.7% stop ≈ at/above TP1 → unreachable under the TP1
   full close. Exactly the owner's "+2% → full SL" trades (EPIC/CLO/POWER/
   TIA). **FIXED:** arm capped at `be_arm_tp1_cap_fraction` (0.5, runtime
   tunable) × the trade's own TP1 distance, floored at the flat trigger;
   wired in BOTH trade_monitor and pretp_dispatcher. **BE-shift = owner-
   sign-off item — merge of this branch is the sign-off.**
3. **TP1_HIT is ambiguous since #707** — a non-mover CLOSES at TP1_HIT
   (BE_THEN_TP1) while a runner mover at TP1_HIT/TP2_HIT is still OPEN.
   EIGENUSDT (closed) showed "open 8h"; MVLLUSDT (open runner) read "closed
   at TP1" (app shows the locked bestTp result for TP-hit statuses); the
   API's `status=="ACTIVE"` open filter dropped open runners from the Open
   tab. **FIXED:** `is_open` (active-book membership minus terminal
   statuses) on `/api/signals` + snapshot cache; lumin-app maps it to
   `MockSignal.effectiveIsOpen` and every widget uses it (labels, fade,
   live-PnL vs banked result, price polling); All feed sorts open-first
   (stable partition).
4. **Signals(12) vs Profit(7)** — NOT a bug: the ops Profit 24h window reads
   `signal_performance.json` = closed signals only (7 closed; EPIC/DELL/APT/
   MVLL still open); actives are live-window only. The "0 active · 7
   stopped" header is just misleading copy.
5. **Volume drop (~48/day Jul-06 → 9 Jul-08 → ~12/24h)** — began BEFORE
   #707: it is the intended compounding of owner-approved gates — #702 cohort
   edge gate + CT_LONG/CT_SHORT macro gates + #705 expiry-OFF (signals now
   occupy the book for hours: DELL open 13h) + #707 dup guard blocking
   re-entry while a same-key signal sits open + loss-streak escalation.
   Mover emissions also collapsed (truth report: MVRTP 35388 generated → 2
   emitted). No code change — knobs are on the ops panel if volume is the
   priority; the stale-candle fix may itself restore some mover volume
   (fresh data instead of frozen).
6. **Paper book frozen at the #707 deploy (~Jul 9 12:02 IST)** — engine book
   kept dispatching/closing signals with ZERO paper counterparts after the
   restart (BABAUSDT 09:22 IST was the last paper close; OP/CLO/EIGEN/TIA/
   POWER all closed with no paper rows). NOT root-caused statically: the
   open path has many silent-skip exits (empty paper cohort, per-user PAPER
   eligibility, risk gate, qty/notional floors, fan-out exceptions).
   **SHIPPED the decisive diagnostic:** `scripts/diag_paper_health.py`
   (+ ops Diag page button) — joins boot config, paper cohort modes/prefs,
   per-user book ledgers, and recent signals into per-signal × per-user
   verdicts. **NEXT SESSION: run it on the VPS**, plus:
   `docker logs 360scalp-v2-engine --since 30h 2>&1 | grep -E "paper_trade_skip|paper fanout|Auto-execution|risk_gate"`

### Shipped (this branch, owner to merge)

- 360-v2: staleness fix (seed stamping + boot-grace + mover re-seed, 20 new
  tests), BE arm TP1 cap (7 tests, sign-off item), `/api/signals is_open`
  (4 tests), `diag_paper_health.py`. Full suite green, ruff clean.
- 360ce-ops: Diag page "paper book health" tool (allowlist + route + 3 tests).
- lumin-app: `isOpen`/`effectiveIsOpen` everywhere, open-first All feed,
  "runner riding" label, live-PnL for open runners (1 new test file).

### Verify on live data (next session)

- MVLL-class: evicted-mover signals reprice off the mark feed (log
  `SL backstop via mark price` / trail moving); no more 11h-frozen closes.
- Mover re-seed logs (`mover candle refresh: re-seeded`) and that mover
  emissions are not blocked by the now-armed dispatch staleness gate.
- BE arm: `be_shift` triggers appearing on wide-stop signals around ~50% of
  the way to TP1; "+2% → full SL" round-trips should disappear.
- Paper: run the new diag; identify and fix the actual gate.

---

## 🟢 SESSION 45 2026-07-09 — PR #702 verdict + mover-path profitability package (owner-approved ACTIVE)

**Owner asked:** analyse PR #702's live effect (3d Profit CSV + PDF vs the
Jun-01→Jul-05 range CSV), deep-dive the mover paths, then implement fixes.

### Verdict on #702 (85 signals, small window — caveats below)

- Book flipped: **−0.39%/day gross (35d before) → +6.0%/day gross / +12.1% net
  (3d after)**. Win rate flat (41→42%) — the gain is exits, exactly what #702
  targeted: TP-hit rate 9%→21%, SL rate 34%→27%, MFE capture −3%→+10%.
- **Exit leak collapsed:** the BE@1%→TP1 simulator beat engine real exits by
  +36.5% total before; after, +2.74% — and ALL of it from 2 VSB signals. Every
  other path's real exits now match the ideal-BE sim.
- Caveats: 3d window straddles the merge (~1.3d pre), n=85, one KORU +5.5%
  outlier; NEW_LISTING stamps not visible in the export yet (36/85 UNKNOWN).

### Movers are the remaining drag (deep dive)

- MVRTP: −0.14%/trade (n=97, before) → **−0.46%/trade (n=18, after)**; volume
  doubled to 6/day. MVAVW: 20 signals across both windows, **zero TP hits,
  zero SL hits, 100% expired** — pure fee drag as shaped.
- 42% of after-window movers reached ≥1% MFE but realised ≤0 (68% MFE
  forfeited in 3d): HMSTR +31.3% MFE→0, TRIA +12.3%→0. Part of this is the
  Session-44 stale-candle bug (#706 fixed, needs a data window); the rest is
  exit shape — the 1R full-close inverts a momentum path's payoff.
- Cohort gate cold-start: store persists only since #702, no cohort has 10
  fresh samples → known-toxic cohorts (MVRTP LONG/RANGING) still dispatch.
- MONUSDT MVRTP LONG: 6 dispatches/−3.7% in 3d (cooldown metronome);
  SPCXUSDT MVRTP SHORT emitted twice 7min apart, identical entry/SL (dup
  guard gap across restarts).

### Shipped (branch `claude/pr-702-signal-analysis-c9zbsb`, PR #707) — ACTIVE

**Owner sign-off in-session: "make it live, no dark flags"** — the Profit
tracker's measured MFE/give-back over both windows is the counterfactual
evidence (mirrors the #702 activation). Every flag stays ops-reversible; the
OFF state shadow-logs so a rollback keeps measuring.

1. **Mover runner exit** (`mover_runner_exit_enabled`, **ON**) —
   `src/execution/runner_policy.py` + trade_monitor: movers bank 40% at TP1,
   30% at TP2 (stop→TP1), and the last 30% rides the phase-tightened ATR
   trail with **NO fixed TP3 cap** (owner directive, from the 4-5%-MFE
   screenshot rows: crossing TP3 stamps+posts but does not close — the trail
   is the only exit for the final slice). Banked slices credited honestly in
   `_set_realized_pnl`. Engine signal book only — the FSM/user-position
   runner is a separate owner-sign-off change.
2. **Ops live/shadow switches per mover path** (`mover_trend_pullback_live` /
   `mover_avwap_scalp_live`, default = env = ON) — flip a path to shadow-only
   from ops, no redeploy. Candidate: MVAVW → shadow on its 0-conversion record
   (owner call, not flipped).
3. **Loss-streak cooldown escalation** (`loss_streak_escalation_enabled`,
   **ON**; cap `loss_streak_cap_hours` 12h) — consecutive losses on the same
   symbol×setup×direction double the lifecycle cooldown extension (1h→2h→4h…).
   Streaks persist to `data/loss_streaks.json`.
4. **Active-duplicate dispatch guard** (`active_dup_guard_enabled`, **ON**) —
   blocks dispatch when the live book already holds the same
   symbol×setup×direction; restart-proof.

Tests: `tests/test_mover_runner_exit.py` (25); mover shadow tests updated to
the tunable-based switch. Full suite 6,064 passed, ruff/mypy clean.

### Verify on live data (next session)

- Mover exits: TP1 posts should read "banked 40%, runner riding"; watch
  PROFIT_LOCKED / TP2+/TP3 outcomes appearing on MVRTP; mover give-back and
  capture on the Profit page vs this window's −14% capture baseline.
- `loss_streak escalate` + `active_dup skip` log lines / suppression counters
  behaving (MONUSDT-style churn dropping, no duplicate live signals).
- Ops action needing NO code: `cohort_edge_gate_min_n` 10→5 to arm the cohort
  gate sooner while the persisted store fills.
- Verify #706 restored mover TP detection (no more 4-5% MFE movers expiring
  at 0 on stale candles) and NEW_LISTING stamps appearing in exports.

---

## 🟢 SESSION 44 2026-07-08 — Stale-candle price freeze on dropped-universe movers (peak stuck, SL/TP backstop blind)

**Owner-reported symptom:** CAPUSDT SHORT on the app showed **Live PnL +1.42%**
next to **Peak so far +0.05%** — impossible, a peak can't sit below the live gain.
Ops Profit tab had it right: candle-replay **Max profit +3.24%** (max price
0.019710) vs the engine's stored `max_favorable_excursion_pct` of **+0.05%**.

### Root cause (branch `claude/performance-metrics-analysis-h7cjxk`)

`_latest_price` returns the last 1m candle close from the scan store. When a
surge-promoted MOVER (or intermittently re-scanned Tier-3 pair) drops out of the
active scan universe, the store keeps serving a **stale, non-None** close near
entry. The pre-existing mark-feed fallback only fired on `None`, so it never
engaged — pinning `sig.current_price`, and with it `pnl_pct`, the running MFE
(peak) and the **SL/TP/invalidation backstop** (`_candle_extremes` reads the same
frozen high/low), all on an hours-old price. Same class as the BEATUSDT −6.52%
blown-stop; that fix only covered the None case, not stale-but-present.

### Fixed

- **Engine (360-v2):** `_latest_price` + `_candle_extremes` now check the store's
  1m kline age (`last_kline_age_seconds`, the same signal the scanner's dispatch
  gate uses). Older than the bound → price the signal off the all-symbols mark
  feed (1s cadence). `age is None` (seed-loaded / pre-first-WS-frame) counts as
  fresh, mirroring the scanner, so nothing diverts post-boot. Behaviour unchanged
  when the candle is fresh or the feed lacks the symbol. Wired through the #702
  runtime-tunables control plane: `mark_feed_staleness_enabled` (default ON) +
  `mark_feed_staleness_max_age_sec` (default 120s, range 30–600), ops-panel
  adjustable, reversible without redeploy. Tests: `test_trade_monitor_stale_price.py`
  (7 cases). Touches SL/TP evaluation → **owner-sign-off item, held from auto-merge.**
- **Lumin app** (branch same name): detail-sheet "Peak so far" can no longer render
  below the app's own live PnL — clamps the peak up to at least the current gain
  (live signals); closed signals keep the engine's recorded historical max. This
  removes the visible contradiction but can't reconstruct the true 3.24% on its own;
  the engine fix above is what restores the accurate peak end-to-end.

### Verify on live data (next session)

- Confirm a dropped-universe MOVER's snapshot `pnl_pct` / MFE now track the mark
  feed (not frozen near entry); Peak so far on the app matches ops Max profit.
- Watch for any signal whose SL/TP now fires off the mark-price point estimate
  (high=low=mark) when its candle is stale — expected, but confirm no premature
  stops on healthy pairs (the age bound should keep in-universe pairs on candles).

---

## 🟢 SESSION 43 2026-07-07 — Noise-aware exits + cohort gate ACTIVE (owner-approved), ops runtime tunables

**Owner sign-off in-session:** "approved everything, activate everything while
shipping itself, no manual env changes" — the four fixes from the 7-day signal
study ship ACTIVE with every knob runtime-controlled from the ops panel.

### The study that drove this (200 shorts CSV + 300 tracked signals vs real 1m klines)

- **52% of SL hits crossed back through entry within 1h** of stopping out (75%
  within 3h); avg post-SL favourable move 1.80% vs 1.00% median stop → stops sat
  inside hourly noise. 62% of SLs hit within 30min of creation.
- **84% of BREAKEVEN_EXIT scratches reached ≥1% profit within 3h** — flat 1% BE
  arm + exact-entry park scratched winners systematically (38 scratches/wk).
- **Score-band inversion:** conf 75+ ran −0.107%/trade vs +0.088% for 65–70.
  Cause: mover paths stamp `htf_trend_aligned=True` + surge-volume scoring →
  near-max scores by construction. MVRTP: 74 signals, conf 76.2, −19.9% total.
- **"UNKNOWN" regime = empty market_phase** (regime_context None at scan; fresh
  listings). That cohort was **+26.3% vs −26.1%** for stamped signals.
- LONGs −18.1% vs SHORTs +18.4% on the window.

### Shipped (branch `claude/signal-analysis-lag-ej2pyr`)

1. **Runtime tunables control plane** — `src/runtime_tunables.py`, Firestore doc
   `control/runtime_tunables`, 5s-cached reads, env boot defaults, owner-gated
   `GET/POST /api/tunables`. Ops panel renders the registry; changing engine
   behaviour no longer requires .env edits or redeploys.
2. **Noise-floor stops (ACTIVE)** — scanner widens every stop to ≥1.0×ATR(1h)%
   (cap 3%), widen-only, TPs untouched; `signal_router` passes `risk_scale` so
   `signal_dispatch` shrinks notional by the widen factor (risk-constant).
   Stamps: `noise_floor_pct`, `noise_floor_widen_factor`, `sl_distance_pct_at_entry`.
3. **BE ratchet re-tune (ACTIVE)** — shared `src/execution/be_policy.py`; arm =
   max(flat 1%, 1R of own stop, 0.75×noise floor); armed stop parks 0.15% on the
   loss side of entry (wick-immune). Wired in BOTH trade_monitor (signal book)
   and pretp_dispatcher (real positions).
4. **Cohort-edge STEP 2 (ACTIVE)** — scanner suppresses when cohort n≥10 and
   WLB expectancy ≤ −0.05%/trade (`REASON_COHORT_EDGE` telemetry). Store now
   persists to `data/cohort_edge_store.json` so deploys don't wipe measurements.
5. **NEW_LISTING regime stamp** — regime_context None now stamps NEW_LISTING
   (thin 1h history) / UNCLASSIFIED; `_record_outcome` backfills empty phases.
   The best-performing cohort is now visible instead of "UNKNOWN".

### Verify on live data (next session)

- Suppression telemetry: `cohort_edge` rejections appearing once cohorts arm.
- NOISE_FLOOR log lines: widen factors sane (1–3×), not pinned at cap.
- BE scratch rate falling in Profit page; SL-hit shakeout share falling.
- One open question: app showed `EXPIRED held 59m` cards ~7h before the ops
  screenshot with expiry DISABLED — confirm no new EXPIRED (non-NO_FILL) at
  ≈60m post-disable; if they appear, the toggle write isn't reaching the
  monitor.

---

## 🟢 SESSION 42 2026-07-04 — Paper trades execute again + Scoring STEP 1 (PR #696)

**Owner mandate (loop continued):** profitable signals first → volume second; scoring
redesign STEP 1; SR_FLIP long re-enable pending ≥1 week shadow data.

### Critical bug fixed: paper trading never executing active signals

**Root cause:** `build_channel_signal()` in `src/channels/base.py` always populates
`entry_zone_low/high` (display band) but never set `entry_zone_filled = True`.
`entry_never_filled` returns `True` any time the zone is set but unfilled.
The auto-execute gate in `trade_monitor.py` skips execution when `entry_never_filled`.

The zone fill check in `_evaluate_signal` races with favorable price movement: once
price moves above `zone_high`, all subsequent 1m candle lows are above it →
`_c_low <= zone_high` never passes → `entry_zone_filled` stays `False` forever.
Both HMSTRUSDT (MOVER_TREND_PULLBACK LONG) and 1000BONKUSDT (DIVERGENCE_CONTINUATION
LONG) visible in the Signals tab were silently blocked for 14+ hours.

**Fix:** `sig.entry_zone_filled = True` immediately after zone computation in
`build_channel_signal()`. All evaluators pass `close=current_price` so
`zone_center ≈ close` and entry is inside the zone by construction. Evaluators
needing true limit-order semantics (entry at a future level) must reset to `False`
explicitly after calling this function.

### Wiring bug fixed: StatisticalFilter outcomes were never recorded

`TradeMonitor` was constructed without `stat_filter=` in `main.py`, so
`self._stat_filter = None` and the recording block in `_record_outcome` was
always a no-op. The rolling win-rate store was permanently empty → always
fail-open → the stat_filter had zero effect in production.

**Fix:** `main.py` now passes `stat_filter=_scanner_stat_filter` and
`cohort_edge_store=_scanner_cohort_edge_store` to `TradeMonitor.__init__()`.
Both share the same singleton instances created at scanner module load time.

### Scoring STEP 1 shipped (observe-only, ships normally per STEP 1 doctrine)

Per `docs/SCORING_AUDIT_2026_07_03.md` rollout:

1. **`CohortEdgeStore`** (`src/stat_filter.py`) — new rolling outcome store keyed
   by `(setup_class, side, regime_family, macro_dir)`:
   - `regime_family`: "QUIET" if local regime ∈ {QUIET/CHOPPY/LOW_VOL/RANGING_LOW_ADX},
     else "ACTIVE" — collapses the 5m rear-view labels into the validated binary
   - `macro_dir`: BTC weekly macro at signal emit (BULL/RECOVERY/NEUTRAL/DECLINE)
   - Expectancy formula: `WilsonLowerBound(WR) × avg_win + (1−WR) × avg_loss` —
     small samples penalised rather than trusted
   - Zero new I/O; pure in-memory dict (same pattern as `RollingWinRateStore`)

2. **`SignalOutcome` extended** with `side` and `macro_dir` fields (defaults
   `""` / `"NEUTRAL"` preserve backward compatibility with existing test callers).

3. **Signal gets cohort edge fields** (`src/channels/base.py`):
   - `cohort_edge_key`: `"SETUP/SIDE/REGIME_FAMILY/MACRO"` stamped at emit
   - `cohort_edge_expectancy`: Wilson-bounded expectancy at emit time (None = no history)
   - `cohort_edge_samples`: sample count in cohort at emit time
   Carried through lifecycle so the truth report and perf records can show the
   cohort context without additional lookups at resolution time.

4. **Scanner shadow-logs `[SHADOW] COHORT_EDGE`** after the existing
   `_stat_filter.check()` block — logs `would-emit/would-suppress:edge=X%:n=N`
   per-signal in debug. No confidence change, no suppression — telemetry only.

5. **`TradeMonitor._record_outcome`** now records outcomes to BOTH stores when a
   signal resolves (excluding `EXPIRED_NO_FILL` non-trades, per existing rule).
   The `macro_dir` at resolution is taken from the emit-time `cohort_edge_key`
   so the store records the market context at entry, not at exit.

6. **12 new `CohortEdgeStore` tests** in `tests/test_stat_filter.py`: fail-open,
   positive/negative expectancy, regime_family bucketing, shadow verdicts,
   sample count, all_stats, window caps, backward-compat defaults.

**All 6001 tests pass.** PR #696 updated to cover both commits.

### What STEP 1 enables

Starting from the next signal resolution, every outcome is recorded with the
correct cohort key. After ≥2 weeks of clean data, read the shadow verdicts
in debug logs:
```bash
docker logs 360scalp-v2-engine --since 2w 2>&1 | grep '\[SHADOW\] COHORT_EDGE'
```
Group by verdict and join against realised P&L. If the would-suppress cohorts
have negative measured expectancy → proceed to STEP 2 activation (owner sign-off).

### NEXT (standing mandate, in order)

1. **PR #696 review** — owner-sign-off item (position_state.py FSM touch). CI green.
2. **SR_FLIP long re-enable** — read `[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE` counts
   after ≥1 week (armed since Session 41). Re-enable only if V2 candidates show
   ~45%+ implied win rate. Owner sign-off required.
3. **Scoring STEP 2** — after ≥2 weeks shadow data, review COHORT_EDGE verdicts
   against realised P&L. Activate `COHORT_EDGE_RANKER_ENABLED=true` on owner
   sign-off. Owner-sign-off item (new scoring model).
4. **FSM LIMIT entry machinery** (`position_state.py` done; rest pending):
   `order_placer.py` → `place_limit_entry()` GTC LIMIT; `position_fsm.py` →
   PENDING_ENTRY→SL-first→OPEN path; `reconciler.py` → skip PENDING_ENTRY from
   market-close detection + TTL sweep. Owner sign-off (Position FSM transition).
5. **CT_SHORT gate monitoring** — daily: `grep -c "CT_SHORT_MACRO_SUPPRESS"` in logs,
   short-side P&L trend, confirm shorts return when weekly macro turns down.
6. **Expiry tune** — re-audit after ≥5 days of clean (post-phantom-fix) data.
   FAR was the premature-kill hotspot but #685 data was contaminated.
7. **MOVER_AVWAP_SCALP entry geometry** — zero real fills ever (all phantoms pre-#685).
   On clean data: widen entry zone / market-entry variant / drop.

---

## 🟢 SESSION 41 2026-07-03 — SR_FLIP long V2: the thesis repair, shipped dark (issue #674)

**Owner mandate (loop):** "enable SR_FLIP longs in correct manner + deep research on
strategies/paths/gates/regimes/wiring + scoring system — profitable signals first,
then volume." This session delivered part 1; parts 2–3 continue next iterations.

### Diagnosis (deep code read of `_evaluate_sr_flip_retest`)

The long/short code is **symmetric** — retest zones, wick/RSI/EMA gates, SL/TP
geometry all mirror. The LONG side bled (19% win, losing in EVERY regime incl.
9% in TRENDING_UP) for thesis-level reasons the code couldn't see:

1. **Flip confirmation was pure price** — one break-and-close above resistance.
   In leveraged crypto an upside break is disproportionately a **bull trap**
   (breakout-chasing longs provide the exit liquidity; their flush IS the
   retest V1 bought). Downside breaks are cascade-driven — that's why the
   mirror-image SHORT side is +5.1% at 52% win on identical code.
2. **No acceptance requirement** — a single poke above the level counted.
3. **LONG had if-priority on whipsaws** — a window where price broke BOTH
   levels (chop) silently resolved LONG.
4. **No macro protection** — SR_FLIP wasn't in the CT_LONG gate scope
   (it was "already off").

### V2 (shipped DARK — merge is behavior-neutral, longs stay off)

- **Volume-backed break**: breakout candle ≥ `SR_FLIP_LONG_BREAK_VOL_MULT`
  (1.5) × prior-20 mean volume. Traps break thin; acceptance prints volume.
- **Acceptance hold**: ≥ `SR_FLIP_LONG_MIN_HOLD_CLOSES` (2) closed 5m candles
  above the level between break and retest.
- **Whipsaw guard**: both-direction confirmation in one window → reject
  `whipsaw_flip` (behavior-neutral today; protective on re-enable).
- **Macro scope**: `SR_FLIP_RETEST` added to `CT_LONG_MACRO_GATE_SETUPS` —
  inert while the side is off; protects re-enabled longs from the steamroll.
- **Shadow**: V2-passing longs log `[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE`
  (symbol, level, vol evidence, hold count) then reject `long_disabled`.
- New reject reasons: `long_break_volume_thin`, `long_acceptance_not_held`,
  `whipsaw_flip`. SHORT side deliberately untouched (no volume gate — it's
  the profitable side and cascade breaks are legitimately thin sometimes).

### Re-enable criteria (owner sign-off when met)

Read `[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE` counts after ≥1 week; join outcomes
via the backfill validator on the shadow candidates. Re-enable
(`SR_FLIP_LONG_ENABLED=true`) only if the V2 candidate set clears ~45%+
implied win on the counterfactual — the point of V2 is fewer, better longs.

### Wiring audit — pass 1 (setup-registration maps): one dead path found + invariant locked

Systematic diff of every emitted `setup_class` against every setup-keyed map:

- **`MA_CROSS_TREND_SHIFT` was silently dead since it shipped** — in the enum
  but registered in NO channel set, NO regime set, and not `_SELF_CLASSIFYING`
  (the exact #634 bug class): hard-rejected at `_prepare_signal` before scoring
  in every regime, while its evaluator burned ~190k attempts/window. Fixed:
  registered in `360_SCALP` + STRONG_TREND/WEAK_TREND/BREAKOUT_EXPANSION (a
  trend-shift entry; ranges whipsaw MA crosses) + self-classifying. First real
  emissions will be watched by the daily loop.
- **6 emitted setups had no `SIGNAL_TYPE_LABELS` entry** (FAR, LIQUIDATION_REVERSAL,
  MA_CROSS, MOVER_AVWAP, POST_DISPLACEMENT, TREND_PULLBACK_EMA) — subscriber
  messages fell back to raw enum names. Labels added.
- **Invariant test added** (`test_setup_registration_audit.py`): every emitted
  setup must be in ≥1 channel set, ≥1 regime set, and have a display label —
  the whole bug class is now unreintroducible.
- Verified clean: `_MAX_SL_PCT_BY_SETUP` (19 keys), `ACTIVE_PATH_PORTFOLIO_ROLES`
  (17), the `INVALIDATION_*_BY_SETUP` maps (sparse by design — per-setup
  overrides over channel defaults).

### Scoring audit (mandate part 3) — verdict + redesign design written

**Verdict: the confidence score cannot rank signals BY DESIGN** — it is an
uncalibrated presence-checklist (any sweep=10, MSS=8, FVG=2…), distributions
compress post-evaluator-gates so penalties do the real separating, and its
largest dimension (SMC) runs half-blind (`orderblocks` source `not_implemented`,
order book top-of-book only, spoof penalty has never fired). r≈0 and the band
inversion are the expected output, not a tuning problem.

**Key discovery: the measured-edge machinery already exists** —
`StatisticalFilter` (Wilson-bound rolling win rates, wired at emit) — but is
neutered by (1) the wrong key `(channel, pair, regime)`: channel is constant,
per-pair samples never clear min_samples, and `setup_class`/side are discarded;
(2) contaminated pre-#685 data; (3) veto-only (can't rank).

**Redesign (owner sign-off): `docs/SCORING_AUDIT_2026_07_03.md`** — two-layer
finalisation: checklist becomes a pass/fail sanity floor; ranking/finalising by
**measured cohort edge** (Wilson-bounded expectancy per setup × side ×
regime_family × BTC-macro), emit-if-positive-edge / probation-cap-if-unknown /
suppress-if-negative. Generalises the SR_FLIP-long disable, CT_SHORT gate, and
S19 setup-identity finding into a self-updating table. Rollout dark-first:
STEP 0 (this PR) `EXPIRED_NO_FILL` excluded from the stat store; STEP 1
observe-only cohort stamps + [SHADOW] COHORT_EDGE; STEP 2 activation on
sign-off after ≥2 weeks clean shadow.

### Wiring audit — pass 2 (stamped-field consumption): validity window was display-only

Traced every field stamped on a Signal to its consumers. `entry_regime_15m`,
`atr_value_at_entry` (FSM trail rate), `market_phase`, `btc_state_factor` — all
consumed correctly. **`valid_for_minutes` was consumed by NOTHING but the
Telegram card**: subscribers are told "valid 15 minutes" while the engine's
fill gate kept waiting up to the 1h max-hold — the engine/paper book could
"fill" a stale setup at minute 55 that rule-following subscribers abandoned at
minute 15 (book-vs-experience divergence + stale-thesis entries). **Fixed:**
`ENTRY_FILL_WINDOW_ENFORCED` (default ON, env-reversible) — an unfilled limit
signal finalises as `EXPIRED_NO_FILL` the moment its advertised validity
lapses.

**Open design question for owner (FSM, sign-off): auto-trade entries are
MARKET-at-dispatch** while the signal book + manual subscribers use the limit
entry zone — AUTO-tier users are IN trades the book correctly counts as
never-filled (~1/3 of signals in the last clean window). Options: (a) FSM
places LIMIT at entry zone with validity-window TTL (matches the book exactly,
users miss nothing the book doesn't), (b) keep MARKET entries and accept the
divergence, (c) hybrid: MARKET only when dispatch price is inside the zone.
Recommend (a) — one truth for every consumer of a signal. Not changed in code;
FSM entry shape is an owner-sign-off item.

### Research: regime classifier forward-validated — only QUIET is real

2,052 point-in-time checkpoints (12 symbols x 4 days, archive candles, engine's
own detector): **QUIET genuinely identifies dead markets** (half the forward
|drift|/range of every other label). But **TRENDING_DOWN's forward drift is
POSITIVE**, RANGING is statistically indistinguishable from TRENDING_UP, and
after the market-beta control NO label predicts forward direction at the 30-min
horizon (all |t| <= 1.05). The 5m regime label is a rear-view instrument; the
macro_direction classifier is the validated forward tool. Full study +
implications: `docs/REGIME_VALIDATION_2026_07_03.md`. Direct consequence for
the cohort-ranker key: regime_family collapses to {QUIET, ACTIVE}; BTC-macro
carries the directional context. Also explains the scorer's regime dimension
(8-vs-18 pts on a distinction with no forward validity). Gate-chain ordering
review (wiring pass 3): clean; one CPU-only note (cooldowns checked at enqueue,
after scoring).

### Research: LevelBook levels fail the placebo test

10 symbols x 4 days, book rebuilt point-in-time every 6h (engine's own
refresh): qualifying CLUSTERED/VP levels rejected 62.9% of touches — the SAME
level set offset +1.85% (structurally meaningless) rejected 65.4%. Price
"respects" any line at this horizon (mean-reversion base rate); the structural
selection added nothing measurable. `docs/LEVELBOOK_VALIDATION_2026_07_03.md`
(incl. the three-study pattern table: SMC half-blind, regime rear-view,
LevelBook ~placebo, while setup x side x macro cohorts separated outcomes
twice). Caveats recorded — longer-span + break-and-retest-specific re-run
before acting on structure-dependent paths.

### NEXT (the standing mandate, in order)

1. **BUILD: FSM LIMIT-at-zone + TTL entries** — owner chose "LIMIT at zone +
   TTL" (AskUserQuestion, 2026-07-03). Full implementation spec in
   `docs/FSM_LIMIT_ENTRY_DESIGN.md` (dark flag, PENDING_ENTRY state,
   SL-first fill handling, TTL sweep, reconciler awareness, shadow line,
   test matrix). Ships dark; activation = owner sign-off on shadow.
1a. **FSM LIMIT entry: shadow phase SHIPPED** — flags + zone/TTL field
   forwarding through dispatch + per-dispatch `[SHADOW] FSM_LIMIT_ENTRY`
   (in_zone / would_rest / market_semantics). Next: the PENDING_ENTRY
   machinery per the spec, then owner activation on shadow data.
1b. **Wiring pass 3** — gate-chain order in the scanner; pre-TP/FSM allowlist
   resolution vs config defaults.
2. **Scoring STEP 1 (observe-only)** — extend the outcome store key to
   (setup, side, regime_family, macro); stamp cohort edge + checklist
   components into perf records; [SHADOW] COHORT_EDGE decisions. Ships
   normally (observe-only). STEP 2 activation = owner sign-off per the doc."
3. Daily check-in items (CT_SHORT gate watch, expiry tune, MOVER_AVWAP, scorer
   data accumulation) continue.

---

## 🟢 SESSION 40 2026-07-03 — Fresh-window validation + phantom-trade accounting bug + tokenized stocks back via movers

**Owner trigger:** "look for signal quality, where things get bad and what's wrong now"
→ "monitor truth data is ready, analyse + PR history" → "look at MOVER paths not
closing at TPs or SLs".

### Fresh 72h truth window (Jul 1–3, 100 closed signals) — June fixes VALIDATED

- **Long bleed is dead:** LONG 40 signals **−0.71% (flat)** vs −25.1%/month pre-fix.
  `long_disabled` = 17,380 SR_FLIP evaluator rejections in 72h — #672 holding.
- **SR_FLIP shorts-only working:** 26 shorts, 50% win, −0.44% ≈ breakeven (was the
  −16.6% biggest single drag).
- **BE@+1% visible:** 12 BREAKEVEN_EXITs that used to round-trip to SL (RIF LONG
  +4.35% MFE → closed 0.00). Real TP hits back: 13 TP1 + 2 FULL_TP.
- **MOVER_TREND_PULLBACK now the top P&L contributor** (+2.05% / 18 longs) —
  excluding it from the macro gate was right. (Truth report's "most suspicious
  degradation: MOVER_TREND_PULLBACK" headline is a heuristic artifact — it keys
  off win-rate/emit ratios, not P&L. Ignore.)
- **THE BLEED SWITCHED SIDES:** SHORT 60 signals **−8.53%**. Regime flipped
  (TRENDING_UP 45.4% of cycles, was 20.9%); counter-trend SHORTs (LSR SHORT −3.75%,
  BREAKDOWN −3.18%, FAR SHORT −2.33%) now mirror the June long bleed. The live
  #683 gate is longs-only by design → activation path is the graded haircut, below.
- Scorer still non-monotonic mid-band (70–75 worst: 25% win, −0.33%/signal; 80+
  only positive band). Rebuild still deferred — n=100 and (see next) data was dirty.

### Root-cause find #1 — phantom no-fill trades (FIXED this session)

All 36 EXPIRED closes in the window had **hold=0s, MFE=MAE=0, no dispatch ts** —
limit signals whose entry zone was NEVER visited. `trade_monitor` skips them each
tick (fill gate), then `router.cleanup_expired` → `main._handle_signal_expiry`
stamped a perf record with **mark-vs-entry P&L for a position that never existed**
(AGLD "−1.25%", WHALE "−0.79%" — fabrications) and fed them into the invalidation
audit as `expired` kills. **36% of the book was phantom.** Consequences: the audit's
"21 PREMATURE expiry kills" verdict is unreliable → the planned expiry tune is
DEFERRED until clean data accumulates; scorer band tables + ops Profit page were
polluted the same way; MOVER_AVWAP_SCALP has in fact **never filled once** — all
its "trades" were phantoms (its entry geometry needs review on clean data).

**Fix (this session's PR):** no-fill expiries now record `EXPIRED_NO_FILL` with
zero P&L on BOTH expiry paths, are excluded from the invalidation audit, skip the
broker close, and the router-path record finally carries create/dispatch/terminal
timestamps (tolerating restart-restored ISO-string `dispatch_timestamp`, which
`_signal_from_dict` never converts back — that string-vs-datetime quirk is still
unfixed, only tolerated). New `Signal.entry_never_filled` property is the single
predicate.

### Root-cause find #2 — tokenized stocks re-entered via mover promotion (FIXED)

#666 admits movers straight off `!ticker@arr` (whole board) and
`_ensure_mover_pair` checked **no blacklist** → SAMSUNG/HOOD/COIN/QCOM/PLTR/SNDK/
RKLB/LITE/ASTS/AXTI equity perps were promoted, scanned, **emitted to the paid
channel** (6× SAMSUNGUSDT in the window), and dominated the phantom EXPIRED sweep.
Fix: `_ensure_mover_pair` now honours `pair_manager._PAIR_BLACKLIST` +
`SCAN_SYMBOL_BLACKLIST`; both blacklists extended with the 13 observed symbols
(incl. ARMUSDT/MRVLUSDT seen in QUIET blocks, XPTUSDT = platinum). Static-list
rot remains a known weakness — Binance keeps listing new xStocks; consider an
exchangeInfo `underlyingType`-based structural filter as the durable fix.

### Root-cause find #3 — "paper skips trades when app unopened" (owner report, FIXED)

The paper book is server-side (single shared PaperOrderManager; the app's
client-side AutoTradeWatcher was removed 2026-05-19), so app-open can't gate it
directly — but the skip was real: `_process_signal` opened the engine-book
position **at dispatch, before the entry-fill gate**. A no-fill signal's paper
position could then NEVER close (SL/TP checks are fill-gated; expiry was
default-off for stretches) → stuck positions accumulated in the risk manager's
**max_concurrent=5** slots → later signals rejected (`risk-gate concurrent-cap`).
Left unattended longer = more stuck slots = more skips; the owner's close-all /
resets on app-open freed slots, creating the "app not open → skips" correlation.
Fix: engine-book auto-execution now waits for `entry_zone_filled` (market-order
signals unaffected); the no-fill expiry path keeps a defensive `close_full` to
drain any pre-fix stranded positions. Same root family as find #1 — dispatch-time
fill fabrication.

### Docs gap closed — the missing macro-direction session (2026-06-30, #677–#683)

Between S38's doc and S39, one undocumented arc shipped: **#677** production-phase
doctrine (dark-flag-first restored) · **#678** graded BTC-State haircut
(`compute_haircut_factor`, stamps `btc_state_factor` on every signal since
2026-06-30, `BTC_STATE_HAIRCUT_ENABLED=false` dark) · **#679** coupling P&L
counterfactual · **#681/#682** directional weekly macro classifier (slope +
structure, quick to de-risk / patient to re-risk, replay-proven on 2021–24) ·
**#683** `CT_LONG_MACRO_GATE_ENABLED=true` LIVE — suppresses counter-trend LONGs
(scope: LSR; MOVER excluded as trend-continuation; SR_FLIP longs already off).

### Root-cause find #4 — the short bleed is MACRO-counter, not intraday-counter (haircut NO-GO; mirror gate shipped dark)

Ran the #675 validator on the clean window (64 real trades; klines from
data.binance.vision — fapi is geo-blocked from the session sandbox, the public
archive isn't). **The intraday BTC-State haircut FAILED its acceptance test:**
the bleeding shorts were BTC-*aligned* at 5m/15m/1h (bucket `4_short`: 22
shorts, 14% win, −0.396 avg = the whole bleed) while counter-trend shorts were
fine; every counterfactual cut made the book worse. The real pattern: shorts
fire into intraday BTC dips inside the weekly-BULL recovery — 36/36 bled shorts
were against `macro_direction` weekly-BULL; the book without them is **+0.42%**
(vs −7.66%). One weekly regime state ≠ a validated gate, so per dark-first:
**`BTC_STATE_HAIRCUT_ENABLED` stays OFF** (verdict recorded in the brief), and a
**CT_SHORT macro mirror** of #683 shipped **DARK** — `CT_SHORT_MACRO_GATE_ENABLED`
(false), scope `LIQUIDITY_SWEEP_REVERSAL,FAILED_AUCTION_RECLAIM,BREAKDOWN_SHORT`
(the 0–20%-win bleeders; QUIET_COMPRESSION 67%-win and SR_FLIP-breakeven shorts
excluded), flag-independent predicate + `[SHADOW] CT_SHORT_MACRO_SUPPRESSED`
telemetry (#597 pattern).

### CT_SHORT gate ACTIVATED (2026-07-03, explicit owner sign-off)

Owner answered "Activate now" (AskUserQuestion, after "proceed with fix") —
`CT_SHORT_MACRO_GATE_ENABLED` default flipped to `true` the same day #687
shipped it dark, accepting the single-regime-window caveat. Env-reversible;
auto-restores shorts when the weekly macro turns down; profitable short
cohorts (QUIET_COMPRESSION, SR_FLIP) out of scope. Daily loop check-in now
watches `CT_SHORT_MACRO_SUPPRESS` counts + short-side P&L on the clean window.

### NEXT (priority order)

1. **Watch the activated CT_SHORT gate** — daily: suppression counts
   (`grep -c "CT_SHORT_MACRO_SUPPRESS"`), short-side P&L trend, and that short
   volume returns when the macro genuinely turns down. Roll back via env if
   live data disagrees with the window evidence.
2. **Expiry tune** — re-audit `expired` kills after ≥5 days of post-fix (no-phantom)
   data; FAR was the premature-kill hotspot but the numbers were contaminated.
3. **MOVER_AVWAP_SCALP entry geometry** — zero real fills ever; on clean data
   decide: widen entry zone / market-entry variant / drop.
4. **Scorer rebuild** — still blocked on clean data volume (band×side, post-fix).
5. Truth-report heuristic: "most suspicious degradation" should weight avg P&L,
   not just win-rate deltas (it flagged the best performer). Low priority.

---

## 🟢 SESSION 39 2026-07-02 — Market Charts audit + Phase 2 shipped (lumin-app #112)

**Owner trigger:** "look at Charts implementation in app side … audit and what we can
add more features and wire everything, implement everything."

**Audit of the v1 Charts feature (lumin-app #108–#111) found four real gaps; all
fixed + Phase 2 shipped in one PR — lumin-app #112** (display-only, no money-path
surface, ships normally):

- **Fix: price-axis precision** — Lightweight Charts defaults to 2 decimals; every
  sub-dollar perp rendered in ~9% axis steps and overlay labels collapsed. Precision
  now derived from price magnitude (`chartPrecisionFor`, ~5 sig figs, clamp [2,8]).
- **Fix: design §10 never wired** — Charts tab now badges live-signal pairs
  (LONG/SHORT pill), floats them to top, and opens their chart WITH the overlay.
  Reads the SWR-cached open-signals stream (same key as Signals tab → no new engine
  load).
- **Fix: poll didn't pause on background** — 2s kline poll stops on pause, resumes
  with catch-up tick (`WidgetsBindingObserver`).
- **Fix: static overlay** — signal re-read every 30s (SWR list); BE-shift moves the
  stop line to entry live, status changes propagate; redraw only on payload change.
  Also TF-switch race-guarded (load generation + poll cancel).
- **Phase 2:** EMA 21/50 + SMA 7/25/99 (the owner's mover MA stack) + RSI 14
  (bottom band, swaps with volume — vendored LWC 4.2.3 has no panes); indicator
  math Dart-side + unit-tested; toggles/TF persisted. Older-history pagination
  (endTime paging, ≤3000 bars, viewport preserved). Crosshair OHLC legend.
  Direction-coloured volume.
- **Deferred with reasons:** Signals-list sparklines (changes the owner-approved
  signal-card layout — owner design call; plus per-row Binance fetches want a
  caching design). `setTheme` bridge dormant (app is dark-only).
- **Verification:** `flutter analyze` clean on touched files; full app suite green
  (156, incl. 22 new). `pubspec.lock` untouched.

**Open at session end:** lumin-app #112 (CI running, self-check armed). No engine
changes this session. Session-38 queue (BTC-State backfill run on VPS → wiring
design) still pending — untouched here.

---

## 🟢 SESSION 38 2026-06-30 — The long bleed is the BTC macro downtrend, not broken longs → BTC-State soft-confirmation design + validation harness (360-v2 #675 merged, #676 open; 360ce-ops #51 open)

**Owner trigger:** "we've been negative for over a month, even a blind trader profits sometimes — why?" Analysed the live Profit export (305 signals, ~1mo) + the ops Profit PDF.

**Diagnosis — the story CHANGED from S34–37 (exit work is DONE; it's entries/selection now):**
- The what-if simulator's **perfect exit (TP1-full, no machinery) still nets −35.65%** (engine real −42.83%, ~7% apart, down from the ~19–25% gap of S34). **The exit fix landed — more exit tuning won't move the book.** The remaining loss is entry/selection edge.
- **Math:** win rate **42%**, avg win +1.14% ≈ avg loss −1.00% (**~1:1 realized R:R**), expectancy **−0.10%/signal**, breakeven needs **47%**. We're structurally ~5 pts of win-rate underwater. BE@+1% + expiries cut winners to ~1:1 while losses run full SL.
- **Scorer band inversion:** win-rate FALLS as confidence rises — 65-70→42%, 70-75→39%, **75-80→30% (−23.6%, worst)**, 80+→41% (only positive band). The score can't rank our own signals; the 75-80s are our worst.

**Owner's correction (the real root cause, backed by his BTC weekly chart):** longs aren't broken — they're **fighting a BTC macro downtrend** (BTC broke its **200-week MA in June 2026**, mirroring June 2022). Alts couple to BTC **harder on the downside than the upside**, so counter-trend longs get steamrolled while shorts work.
- **Confirmed in our data:** LONG **−25.1%** (34% win) vs SHORT **+9.65%** (46% win). The three counter-trend reversal-LONG cohorts — **SR_FLIP_RETEST long −21.75% (19% win), MOVER_TREND_PULLBACK long −12.78% (24%), LIQUIDITY_SWEEP_REVERSAL long −10.19% (26%)** — carry −44.7% over just **63 signals (21% of book)**. **Cutting only those flips the book −15.45% → +29.27%** on the same window. LONGs lose in EVERY regime; every SHORT cohort is flat-to-positive. The SAME paths on the SHORT side are fine. Keep-engine: VOLUME_SURGE_BREAKOUT long +10.8%/67% win, FAILED_AUCTION_RECLAIM both sides, DIVERGENCE long.

**Research (3 parallel agents, owner asked for "2-3 parallel different thinkings") — CONVERGED on one design:** a **graded BTC-State soft-confirmation**, NOT a 200MA on/off gate (owner rejected the slow "6mo shorts/6mo longs" binary):
- **Layer 1 — BTC-State score b∈[−1,+1]:** 5m/15m/1h EMA(8/21/55) stack + ATR-normalised slope + RSI (v1 price-only), vol-shrunk in chop; BTC.D dominance (rising-BTC.D + falling-BTC = max long penalty) + structure/VWAP deferred to v2.
- **Layer 2 — per-pair downside coupling w_pair∈[0,1]:** downside-beta × downside-corr on 15m returns; decoupled pairs (memecoins/own-catalyst) ≈0 auto-exempt, exemption REVOKED the instant BTC dumps.
- **Layer 3 — wiring:** `factor = 1 − k·|b|·w_pair·A_side` haircut at EMIT (not a gate); floor (never zero) + recompute-every-dispatch ⇒ **auto-restores longs when BTC flips** (owner's "if BTC moves up longs brighten"); counter-trend LONG penalised ~2× counter-trend SHORT (the downside asymmetry).
- **Code reality found:** engine ALREADY has `src/btc_direction.py::check_btc_direction_gate` — but it's binary AND only fires when BTC **1H AND 4H both** oppose, so it's silent during relief bounces / TRENDING_UP (where our longs bled). Plus `src/correlation.py` (corr-magnitude only, direction-blind). New design SUBSUMES both. **This wiring is OWNER-SIGN-OFF (scoring model + routing) — bring design after backfill confirms.**

**Shipped this session:**
- **360-v2 #675 (MERGED):** `scripts/btc_state_backfill.py` — read-only point-in-time validator (no look-ahead). Reconstructs BTC-State + per-pair downside coupling per historical signal, stratifies outcomes by side × BTC_STATE × coupling band. 14 unit tests (synthetic, no network). Acceptance test: long win-rate collapses as BTC turns hostile, concentrated in BTC-LED pairs while DECOUPLED longs survive, shorts don't collapse.
- **360-v2 #676 (OPEN, CI running):** fix — backfill must read `dispatch_timestamp` (emit), NOT the perf record's generic `timestamp` (close time) which would corrupt the reconstruction. Also passes through signal_id/confidence/mfe so output joins into ops. +1 test (15 total).
- **360ce-ops #51 (OPEN, CI running):** Profit-page **Direction what-if dropdown** (All / Shorts only / Longs only / Exclude counter-trend longs) — orthogonal to exit-strategy, makes the −15%→+29% counterfactual a 2-click knob. No BTC/Binance dep (keys on recorded side+setup). 6 tests.

**NEXT SESSION — do in order:**
1. **Run the backfill on the VPS** (after #676 merges + ~45s deploy): `docker exec 360scalp-v2-engine python scripts/btc_state_backfill.py --signals /app/data/signal_performance.json --out /app/data/btc_state_backfill.csv`. Read the verdict table against the acceptance test.
2. **If thesis confirms:** bring owner the graded soft-confirmation **wiring design** (owner-sign-off) — replace the coarse binary `check_btc_direction_gate` with the graded `factor` in `confidence.py`/scoring, env off-switch default ON, stamp `btc_state` on every signal. If it doesn't confirm, retune the design first.
3. **Layer-2 ops:** add **BTC-State-conditioned** filter options to the Profit Direction dropdown (drop counter-trend longs only when BTC hostile AND pair BTC-led), reading `btc_state_backfill.csv` from the data volume — ready once step 1 generates the CSV. (Owner asked whether to pre-wire this; left pending his call.)
4. **Scorer calibration** (separate lever): the 75-80 band inversion — likely dissolves once the counter-trend longs are cut; confirm band×side on fresh data before touching the scorer.

**Open PRs to check at session start:** 360-v2 #676, 360ce-ops #51 (both were in CI at session end; self-checks armed). 360-v2 #675 already merged. Pre-existing unrelated: 360ce-ops `tests/test_alerts.py` + `app/agent/*` ruff debt fail on clean main (redis/env), not ours.

---

## 🟢 SESSION 37 2026-06-29 — Mover pipeline made to actually fire + exit-model default fix + SR_FLIP shorts-only (merged: 360-v2 #666–#672, 360ce-ops #48/#49/#50)

One long arc: get the promoted movers to actually trade, then fix the exit logic that was bleeding the whole book, then cut the worst-bleeding direction. Built the diagnostic that found each wall, fixed each in turn.

**Mover pipeline — from "Promoting (0)" to signals firing:**
- **#666** — admit outside-top-75 movers into the promotion universe. With `TOP50_FUTURES_ONLY=true`, `pair_mgr.pairs` is capped at the top ~75 by volume and both promotion sources keyed off `pair_mgr.pairs.get(symbol)` → real movers (GUAUSDT −23%, SKYAIUSDT −44%) resolved to `None` and were silently dropped. The `!ticker@arr` detector sees the whole board; now it captures `(24h %change, quote_vol)` per symbol and the scanner admits outside movers as synthetic TIER3 pairs (`_ensure_mover_pair`), evicted on promotion expiry.
- **#667 / #668 / #670** (engine) + **ops #48 / #49 / #50** — per-pair "Why not firing" column on the ops Pairs page. Built incrementally: in-evaluator reason capture (#667) → scanner-side pre-eval skip capture (#668, the all-`—` was telling us movers were skipped *before* evaluation) → specific skip reasons instead of generic `channel_skipped` (#670). This diagnostic is what surfaced every subsequent root cause.
- **#669 — THE mover bug.** The mover spread gate compared `ctx_for_chan.spread_pct` (a **percent**, 0.5 == 0.5%) against the literal `0.005` — i.e. 0.005%, ~100× too tight — so it skipped **every** promoted mover before evaluation. Its own log said "> 0.5% — skip", so 0.5% was always the intent; written as a fraction by mistake. Fixed via env-tunable **`MOVER_MAX_SPREAD_PCT`** (default 0.5). After this, movers reached the evaluators and MOVER_TREND_PULLBACK started firing (TURBO, RIF, US, BEL, PENDLE all `✓ fired`).
- Note for next session: **MOVER_AVWAP_SCALP has not fired yet** — every mover signal so far is MOVER_TREND_PULLBACK. Watch whether the AVWAP rider's anchor+slope+pullback gate is too strict.

**Exit model — the −18% leak (#671, owner-sign-off, owner-directed):**
- Profit-Lab (233 closed signals, ops Profit page): engine real exits net **−18.13%** while "SL→entry once +1% in profit, then close 100% at TP1" nets **−0.23%** (+17.89% edge). Avg MFE +1.55% — signals go green then give it back. **The leak is the exit logic, not the entries.**
- Root cause: the Session-34 model (BE@+1%, TP1-full, pre-TP off, loose invalidation) was wired into the **execution FSM** only. **`trade_monitor`** — the signal tracker that drives the Profit page + what a signal-follower experiences — still ran the OLD model: 40% partial at TP1 + TP2/TP3 runner, BE only on TP1 hit, structural/trailing invalidation kills. That mismatch was the −18%.
- Fixed: `trade_monitor` engine-default exit now = BE→entry at +1% MFE (ratchet-only, pre-TP1) + full close at TP1 (`_close_full_at_tp1`) + no engine-wide invalidation. Gated by **`BE_THEN_TP1_DEFAULT_ENABLED`** (default on, env-reversible). **Per-user opt-in for pre-TP / invalidation preserved** (handled by `_check_per_user_invalidation` + FSM) — this flag governs only the engine's default book. Tradeoff: TP1-full forgoes the occasional TP2/TP3 runner; backtest still nets +17.89%.

**SR_FLIP shorts-only (#672, owner-sign-off, owner-directed stopgap):**
- SR_FLIP_RETEST is the biggest single drag (−16.6% / 85 signals) — but one-sided: SHORT +5.11% (52% win), **LONG −21.75% (19% win)**, losing in every regime (9% win even in TRENDING_UP). Win rate is exit-independent → an entry-quality problem the #671 exit fix only half-addresses (SR_FLIP → ~−8.8% under the new exit).
- Gated longs off by default via **`SR_FLIP_LONG_ENABLED`** (env-reversible); shorts unaffected. **Explicitly a tourniquet, not a cure** — owner's words. Follow-up tracked as a GitHub issue: investigate *why* SR_FLIP long flips fail and fix-or-drop the long thesis (do it on a fresh post-#671 data window, not stale numbers).

**New env tunables this session:** `MOVER_MAX_SPREAD_PCT` (0.5), `BE_THEN_TP1_DEFAULT_ENABLED` (true), `SR_FLIP_LONG_ENABLED` (false).

**Watch next (fresh data window — counters are cumulative, old closed signals reflect old exits):** Profit page "engine real exits" should converge from −18% toward the simulator's −0.23%; mover givebacks (POWRUSDT-type +5% MFE → invalidated) should convert to BE/TP1; SR_FLIP drag should drop with longs gone.

---

## 🟢 SESSION 36 2026-06-27 — Referral/invite-a-friend + manual tier-grant control (merged: 360-v2 #654/#655, lumin-app #106, 360ce-ops #43)

**Two features shipped end-to-end this session, both across multiple repos:**

1. **Referral / invite-a-friend (Phase 1).** Engine-side code generation, claim, and stats API (360-v2 PR #654) + app-side share sheet, repository methods, and onboarding capture (lumin-app PR #106). Both merged.

2. **Manual tier-grant (owner comp for testers/influencers).** Built per owner instruction *after* the referral PRs merged, with a default expiry (no permanent comp via this path):
   - **360-v2 PR #655** (engine): `GET /api/admin/users/lookup` + `POST /api/admin/grant-tier`, owner-gated (`owner_required` dependency, same as kill-switch/reset-signals). Reuses the existing `UserStore.aset_tier()` write path — the same one the Play Billing verify flow and the `/internal/billing/grant` webhook use, so this is a third caller onto one source of truth, not a parallel entitlement system. `tier` accepts `free` / `assist` / `auto` (the current two-tier automation paywall, B16) — **not** a single legacy "pro" tier; this was caught mid-implementation after pulling 45 commits of upstream drift and correctly rescoped before writing code. `duration_days` defaults to 30, range 1–365; `tier=free` revokes immediately and ignores duration. 11 new tests, full suite 5828 passed.
   - **360ce-ops PR #43** (ops UI): `EngineApiClient.user_lookup()` / `.grant_tier()`, a new `/control/users` route + template (lookup form → current tier display → grant form with tier/duration/reason), wired into nav next to Control. Same control doctrine as every other write surface here: owner-gated via the static Bearer token, audited via `app/audit.py` (best-effort, non-blocking), PRG + JS confirm before the grant POST. 9 new tests, full suite 232 passed.

**Both judged not owner-sign-off items** (no Position FSM / signing-service / scoring / paid-channel-routing touch) — auto-merged once CI was green and review threads were empty, per the Change-management Protocol.

**Environment note (360ce-ops):** the sandbox this session ran in had a stale dependency set (`itsdangerous` and `python-multipart` missing, wrong `jinja2`/`starlette` versions resolved). Reinstalling from the repo's own `requirements.txt` fixed it — not a code issue, just a reminder that `pip install -r requirements.txt` should be step zero in a fresh container before trusting a red test run.

---

## 🟢 SESSION 35 2026-06-25 — Mark-price-triggered BE SL shift at +1% MFE (engine, merged PR #646)

**Owner trigger:** simulation in `ops.luminapp.org/profit` showed that signals often move 1%+ in our favour then reverse to the stop, giving back the unrealised gain. With the new TP1/SL-only default (Session 34 PR #645), there is no pre-TP to bank profit early — the loss is taken in full when SL hits.

**Simulation evidence (499 closed signals, live window, `exit_sim.py`):**
| Strategy | Total PnL | Edge vs engine real exits |
|---|---|---|
| Engine real exits (mixed legacy) | −29.28% | — |
| TP1-only (current default) | −11.51% | +17.77% |
| **BE at +1.0% → TP1** | **−10.62%** | **+18.67% (+0.89% vs TP1-only)** |
| BE at +0.5% → TP1 | −6.53% | +22.75% |

Owner signed off: **"keep at 1%"** (1.0% chosen over 0.5% to avoid scratching signals that dip briefly then continue to TP1; avg TP1 distance is 2.29%).

Also shipped in this session (360ce-ops):
- **PR #37** (`feat/be-stop-tp1-diagnostic`): BE simulation strategy + TP1-miss diagnostic banner on the profit tab — merged.
- **PR #38** (`fix/be-tp1-namefix`): hotfix `NameError` in `_build_rows` — merged.

### Shipped — PR #646 (360-v2, engine, owner-sign-off: BE shift + FSM)

| Change | File | Why |
|---|---|---|
| `BE_SHIFT_TRIGGER_PCT = 1.0` (env-overridable) | `config/__init__.py` | Single-source trigger threshold |
| `be_shift_fired: bool = False` on `Position` + Firestore serde | `src/execution/position_state.py` | Prevents double-fire across ticks + survives restart |
| `maybe_fire_be_shift()` async function | `src/execution/pretp_dispatcher.py` | Cancel original SL, place STOP_MARKET at entry via `coid_sl_be`; wired into `_on_tick()` after `maybe_fire_pretp` |
| 8 unit tests | `tests/test_be_shift.py` | LONG/SHORT fire, below-threshold no-fire, double-fire guard, sl_order_id==0 guard, pretp_fired guard, placement-failure retry |

**Cost:** zero additional Firestore reads per tick — reuses the existing in-memory live-position index. One `put_position` write per position when the shift fires (one-time per signal life).

**FSM integration (existing infrastructure):**
- When BE-SL fires, the FSM routes via `coid_sl_be` → `_apply_sl_be_fill()` → `close_reason="SL_BE"` → CLOSED ✓
- When TP1 fires (full close): `sl_order_id == 0` (already zeroed at BE-shift time) → skip cancel; Binance auto-cancels the resting BE-SL (`closePosition=true`) when position reaches zero ✓
- Pre-TP users unaffected: `pretp_fired=True` guard + PRE_TP_FIRED state excluded from OPEN-position query ✓

### VPS action required

On next `main` deploy (auto ~45s after merge), the engine image will include the BE-shift logic. No env vars required — `BE_SHIFT_TRIGGER_PCT=1.0` is the default.

To verify it is live after the first position crosses +1% MFE:
```bash
docker logs 360scalp-v2-engine --since 1h | grep "be_shift: triggering"
docker logs 360scalp-v2-engine --since 1h | grep "be_shift: placed BE-SL"
```

### REMAINING (from Session 34)
1. **lumin-app (PR 2):** outcome-summary card redesign per owner's reference mockup — highlight positive result + "Max profit reached before SL", faded-but-visible closed-signal bars, active-signal trade button; copy aligned to the new model. **In progress.**
2. **360ce-ops:** Profit-Lab data window still maturing after Session-34 default flip. Wait for fresh window before judging the TP1-only + BE-shift real-book edge.
3. **VPS:** verify `.env` does not pin old pre-TP / invalidation defaults (`PRE_TP_GRAB_FRACTION`, `INVALIDATION_MODE_DEFAULT`, `PRE_TP_ENABLED`) — clear them if so.

---

## 🟢 SESSION 34 2026-06-24 — Default exit reversed to TP1-full + fixed SL (pre-TP & invalidation now opt-in)

**Owner trigger (Profit-Lab screenshots, `ops.luminapp.org/profit`):** "pre-TP and
invalidations aren't working and are making more losses; taking full profit at TP1
makes more sense. No pre-TP, no invalidations — pure signals with TPs and SL, and
Max profit reached before hitting SL." Plus an app redesign brief (see lumin-app).

**Data basis (the Profit-Lab, 494 closed live signals, net of 0.07% fee):**
| Exit method (TP/SL only) | Total P/L | Edge over engine real exits |
|---|---|---|
| **TP1-full (100% @ TP1)** | **−6.65%** | **+19.14%** |
| 50% @ +1% · 50% TP1 | −14.09% | +11.70% |
| 50% TP1 · 50% TP2 | −16.44% | +9.35% |
| TP1/TP2/TP3 thirds | −19.70% | +6.09% |
| Flat +1% (100%) | −21.53% | +4.26% |
| **Engine real exits (pre-TP + invalidation)** | **−25.79%** | baseline |

Every simple exit beat the engine's machinery; **TP1-full beat it most**. The exit
logic, not the entries, was giving back the edge. *Honest caveat told to owner:
TP1-full is still slightly net-negative (−6.65%) — it stops most of the bleed but
the residual gap is entry quality + fees, the next lever. UI must not imply green.*

**Owner decisions (AskUserQuestion):** exit shape = **TP1-full @ 100%**; backstop =
**TP-or-SL only + 2h reconciler** (no timed exit; naked-SL invariant + caps stay);
per-user pre-TP/invalidation dials **remain usable**, engine **default** = TP1+SL.

### Shipped — PR 1 (360-v2, engine, owner-sign-off: FSM + B-rules)
Three env-overridable default flips + the FSM fix that makes them safe:
| Change | File | Why |
|---|---|---|
| `PRE_TP_GRAB_FRACTION` 0.50 → **0.0** (pre-TP disabled by default) | `config/__init__.py` | no banking on the default path |
| `INVALIDATION_MODE_DEFAULT` `tight` → **`loose`** (loose short-circuits to SL/TP-only) | `config/__init__.py`, `trade_monitor.py` | the "TP/SL only" lab method |
| New `TP{1,2,3}_CLOSE_FRACTION` (default **1.0/0.0/0.0** = TP1-full); dispatch reads them lazily | `config/__init__.py`, `signal_dispatch.py` | TP1 closes 100%; ladder restorable via env (B8) |
| **`_apply_tp1_fill` terminal-close fix** — on a full TP1 close go CLOSED + cancel SL, place NO breakeven-SL | `position_fsm.py` | without this, TP1=100% stranded the position in TP1_HIT with an orphaned BE-SL on zero qty (only the 2h reconciler clearing it) |
| Monitor `_check_pre_tp_grab`: grab ≤ 0 → return False (no engine-book banking) | `trade_monitor.py` | grab=0 must truly disable, not clamp up to 0.30 |
| `PretpSettings.grab_fraction` `ge=0.30` → **`ge=0.0`**; `_coerce_pretp` preserves 0 (disabled), clamps positives into [0.30,1.0] | `api/schemas.py`, `api/user_overrides.py` | the resolved view for a fresh user is now 0.0 — was a 422 (real end-to-end bug, not a test issue) |

Per-user opt-in still fully wired: a user who sets `grab_fraction>0` /
`invalidation_mode∈{standard,tight}` gets it forwarded at dispatch (tests prove it).

**Tests:** +6 new (TP1-full terminal close; default-grab-disables-pre-TP;
loose-default-suppresses-invalidation; env-override-restores-ladder; full-mgmt
default-no-pretp + user-opt-in). Updated the mechanics suites (pre-TP, dispatch,
trade-monitor invalidation, audit, btc-overlay) to pin their opt-in mode rather
than assume the old default. Full suite green. ruff clean on `src/`+`config/`.
Doctrine: OWNER_BRIEF §2.3/§3.2/§3.9/B17 rewritten; profile **D (TP1-full)** is
the new default.

### REMAINING
1. **lumin-app (PR 2):** outcome-summary card redesign per owner's reference mockup
   — highlight positive result + **"Max profit reached before SL"**, faded-but-visible
   closed-signal bars, active-signal trade button; copy aligned to the new model
   (drop "Pre-TP banked / SL→BE" as the default framing). **In progress.**
2. **360ce-ops:** Profit-Lab already exposes the exit-method comparison; once the
   new default has a fresh data window, re-read to confirm the live book tracks the
   −6.65% sim (don't judge early — counters are cumulative).
3. **VPS:** new default ships live on `main` deploy. If `.env` pins the old values
   (`PRE_TP_GRAB_FRACTION`, `INVALIDATION_MODE_DEFAULT`, `PRE_TP_ENABLED`), clear
   them so the code defaults take effect.

---

## 🟢 SESSION 33 2026-06-24 — Monetization corrected to two-tier auto-trade model (signals free)

**Owner correction mid-rollout:** the product is NOT "pay to see signals." Signals +
entry/SL/TP + analysis are **FREE**. The paywall is **trade automation**, two monthly
Play subscriptions:
- **Assist** `lumin_assist_monthly` **₹1000/mo** — one-tap "take trade" (app places
  the order client-side on the user's own Binance keys).
- **Auto** `lumin_auto_monthly` **₹2000/mo** — hands-off server-side auto-execution.

Tier hierarchy `free < assist < auto`. This reworks the Session-32 Play Billing landing
(which wrongly locked levels behind a single `paid` tier).

### Shipped (engine — two-tier rework, owner-sign-off PR)
- `auth.py`: `ASSIST_TIER`/`AUTO_TIER` + `tier_rank`/`can_assist`/`can_auto` hierarchy.
- **`signal_dispatch` money-path gate**: hands-off execution runs ONLY for `auto`
  users (`_resolve_user_tier`, 30s cache, expiry-aware, **fails closed**). Reversible
  via `AUTO_TRADE_TIER_GATE_ENABLED` (default ON). End-to-end test proves a free user
  is skipped, an auto user dispatched.
- `billing_play`: product→tier map (`GOOGLE_PLAY_PRODUCT_TIERS`); `entitlement_for`
  returns assist/auto by product. `server.py` expiry-downgrade covers both tiers.
- Tests: 53 dispatch + 40 billing/tier green; ruff clean.
- Doctrine: B16 rewritten (two-tier automation paywall), B1/§2.2 — signals free.

### Owner / business status (2026-06-24)
- Engine billing armed on VPS (`configured=True`); Firebase SA granted Android
  Publisher access.
- **Payments KYC submitted via BillDesk** (individual a/c, Finance category — accurate
  for crypto auto-trade; NOT "Education"). Awaiting Google/BillDesk payout approval
  (days). Min ₹1000 / max ₹3000 ticket; income ₹750k.

### REMAINING
1. **lumin-app**: stop locking levels (free); gate one-tap take-trade by ≥assist; gate
   live auto-trade by =auto; subscription page → two plans (₹1000/₹2000).
2. **Play Console**: create `lumin_assist_monthly` + `lumin_auto_monthly`; Internal
   testing release; license tester; Financial features declaration.
3. ⚠️ **Legal**: charging for automated crypto execution — keep a legal sanity-check
   current (Play financial-services + Indian regulatory exposure).

---

## 🟢 SESSION 32 2026-06-23 — Monetization pivot: Google Play Billing (Telegram payment retired); engine entitlement core shipped

**Owner trigger:** Play Console granted **production access** (screenshot). Owner: "we
need to proceed with Google Play billing, because Telegram is presently banned in
India." Approved the full plan + "update owner brief."

### Doctrine decision (owner-approved — Business Rule change, owner-sign-off)
- **B16 rewritten:** Google Play Billing is the v1 purchase path; **Telegram-bot
  payment retired** (a bot paywall reaches no one in a Telegram-banned region).
  Subscription positioned as **education / market-analytics content**, never
  "trading signals" — Google Play Payments policy bars *investment-consulting*
  services from Play billing, so the framing is load-bearing.
- **B1 reconciled:** paid signals deliver **in-app first** (Lumin Signals feed,
  paid-tier-gated). Telegram paid channel = optional single mirror only.
- Policy basis (verified against Google's own pages): Payments policy
  ("stock trades, investment consulting … should not use Google Play's billing
  system") + Financial Services declaration + India alternative-billing (−4%).

### Key finding — the entitlement plumbing already existed
Delivery is **already in-app** (`signals_page.dart`, free-tier gate locks
entry/SL/TP). The engine already had `UserStore(tier, paid_until)` +
`aset_tier()` + `mint_user_token(tier, paid_until)` + JWT tier-claim enforcement.
The ONLY missing link was: **Play purchase → server-side verify → set_tier**.
Grep confirmed zero pre-existing Play/billing code.

### Shipped this session (engine — fully wired, no scaffold)
| Area | What |
|---|---|
| Config | `GOOGLE_PLAY_*` env (package name, service-account JSON, allowed product IDs, RTDN audience, feature flag) — all env-overridable, SA key never logged. |
| `src/api/billing_play.py` | `PlayBillingVerifier` — service-account OAuth2 token (RS256 via google-auth, cached) → Google Play Developer API `purchases.subscriptionsv2.get`; derives entitlement (ACTIVE/GRACE/CANCELED→paid until expiry; ON_HOLD/PAUSED/EXPIRED/REVOKED→free); acknowledges pending purchases; parses RTDN Pub/Sub envelopes. |
| `src/api/play_purchases.py` | `PlayPurchaseStore` — maps `purchase_token → user_id` (so RTDN, which has no JWT, resolves the user); tracks product/expiry/state; handles `linkedPurchaseToken` on upgrade/resignup. |
| `src/api/server.py` | `POST /api/billing/play/verify` (user-JWT authed) + `POST /api/billing/play/rtdn` (Pub/Sub push, audience-verified). Refresh path consults UserStore so an expired sub downgrades to free on next JWT refresh. |
| `main.py` + `bootstrap.py` | construct + thread `PlayBillingVerifier` + `PlayPurchaseStore` (both isolated + single-process boot sites). |
| Tests | verifier entitlement mapping, acknowledge, RTDN parse + re-fetch, token→user resolution, endpoint auth, refresh downgrade. |

### REMAINING (next increments)
1. **lumin-app:** `in_app_purchase` plugin; replace `subscription_page.dart`
   Telegram CTA with Play purchase + restore-purchases; education/analytics copy;
   drop reader-app language; verify→JWT-refresh.
2. **lumin-legal:** auto-renew / billing terms + data-safety alignment.

### OWNER ACTIONS (Play Console / GCP — only owner can do; blocks app increment)
- Create subscription products (IDs → into `GOOGLE_PLAY_PRODUCT_IDS`); base plans + pricing.
- File **Financial features declaration**; reframe listing + data-safety as education/analytics.
- GCP **service account** w/ Android Publisher access, linked to Play Console → env `GOOGLE_PLAY_SA_JSON`.
- **RTDN**: Pub/Sub topic + push subscription → engine `/api/billing/play/rtdn`.

---

## 🟢 SESSION 31 2026-06-20 — Per-user PATH + REGIME live eligibility (shipped); paper-per-user + Full/Entry sequenced

**Owner trigger:** "We give per-user symbol choice but not which paths / which
regime — make those flexible too, neatly in auto-trade settings, paper + live
each individual, with reset to default. Reset-to-default also missing on
Invalidation + Pre-TP. Signals tab: tapping a symbol → take signals **full**
(entry+exit+pre-TP+invalidation) vs **entry-only** (engine places entry, user
manages). Add to CLAUDE.md: no shortcuts / scaffolds / fast-tracks, production-
grade only. No dark flags (we're testing, no users)."

### Doctrine + decisions
- **CLAUDE.md** operating-standard strengthened: no scaffolds / no fast-tracks /
  no stub-now-wire-later — a setting the engine *stores but doesn't consume* is a
  banned scaffold; money-path features ship storage + dispatch/FSM consumption +
  UI together. (No-dark-flags was already doctrine in § Project Phase.)
- Owner decisions (via AskUserQuestion): **entry-only on LIVE = entry + protective
  SL (never naked) then skip pre-TP/TP/invalidation**; **Full/Entry saved per
  symbol**; **make paper per-user** (so paper selectors are real, not a scaffold).

### Shipped this session (fully wired + tested)
| Area | What |
|---|---|
| Engine | `user_auto_trade_settings.path_preference` + `.regime_preference` (JSON; NULL=all, []=block-all) — schema, idempotent migration, coerce (path uppercase; regime via `_normalise_regime_input`), persistence, `resolve_auto_trade_preferences_uid` resolver. |
| Engine | LIVE gate in `dispatch_signal_to_active_users` — skips user silently (pre-signing) when `setup_class` ∉ path pref or `regime_label` ∉ regime pref. Symbol gate (position_fsm) unchanged. |
| Engine | `GET /api/auto-trade/runtime-status` now returns `allowed_paths` (from `ACTIVE_PATH_PORTFOLIO_ROLES` — single source of truth, no app drift) + `regime_options`. |
| App | `AutoTradeSettings` model + `AutoTradeRuntimeStatus` carry path/regime; new `eligibility_preference_page.dart` (shared Path + Regime picker, preset all/custom/block); "What auto-trades for me" card in Auto-trade settings (Symbols/Paths/Regimes rows + one **Reset to default**). |
| App | Pre-TP + Invalidation **Reset-to-default** now always visible (was hidden via `if (!_usingDefaults …)` → looked missing on a default page). |
| Tests | +11 engine tests (store 8, dispatch 3); affected suites green: 197 pass (user_overrides 91, signal_dispatch 50, status_routes 20, tripwires + others). |

| Engine | **Per-symbol Full / Entry-only** (Signals-tab tap): `user_symbol_management` table + `resolve_symbol_management_uid`; entry-only reuses tested levers at dispatch (`grab_fraction=0` + `invalidation_mode='loose'` + `management_mode='entry'`) and `place_signal` lays NO TP ladder. **Entry + protective SL still placed** — never naked (B12/B18). `GET/PUT /api/settings/user/symbol-management`. |
| App | Signals-tab detail sheet: "AUTO-TRADE {SYMBOL}" section, two highlightable tiles (Take full / Entry only), persisted per symbol; repo `fetchSymbolManagement`/`setSymbolManagement`. |
| Tests | +9 more (store/resolver 6, dispatch 2, FSM bracket-skip 1) → 329 pass across affected suites incl. API smoke. |

Scope note: path/regime + per-symbol management are the **LIVE** filters today
(live dispatcher is per-user). Paper selectors + per-symbol management on paper
land with Increment 2.

### Per-user paper engine — Phase 3 (PR #636, owner-sign-off, NOT merged)
Owner decisions this session: **isolated paper registry** (not in-FSM); **namespace
per user, one source** (no duplication; engine-wide paper = aggregate of per-user
books); **per-user only** (paper fires only for paper/both opt-in — operator opts in
like any user; no always-on operator book).

**Built + unit-tested (inert — every change additive/defaulted; existing suites pass
unchanged; 46 tests green):**
- `paper_symbol/path/regime_preference` columns + migration + coerce +
  `resolve_paper_preferences_uid` (independent of the live triple).
- `PaperOrderManager` per-user `pnl_path` / `trades_db_path` / `pnl_history_mode`
  (default = legacy shared paths → inert).
- `trade_records`: every helper takes optional `db_path` (per-user SQLite files);
  `iter_user_db_paths` + `list_trades_all_users` / `count_trades_all_users` aggregate.
- `src/execution/paper_book_registry.py` — `PaperBookRegistry` (one book/user) +
  `PaperBookFanout` (drop-in for the single `PaperOrderManager`; fans lifecycle out
  to eligible users; entry-only skips pre-TP/TP, survives invalidation, closes on SL).

**ACTIVATION LANDED — gated behind `PAPER_PER_USER_BOOKS` (default OFF), atomic
write+read flip, both flag states fully wired (owner approved "gated, default OFF"
2026-06-20). Engine #1/#2 below DONE; app + ops (#3/#4) still pending.**
- `config.PAPER_PER_USER_BOOKS` (default `false`) + `PAPER_BOOKS_DIR` — kill switch,
  not a dark flag. OFF = legacy shared-book path untouched; ON = per-user fanout.
- `main.py._build_paper_order_manager()` builds the fanout at BOTH construction sites
  (boot + `set_auto_execution_mode`); `PaperBookRegistry` now threads position sizing +
  a **per-user RiskManager factory** (each book gets its own daily-loss/concurrency
  limits — no shared global paper cap).
- `pnl_history` aggregate readers (`get_*_aggregate("paper")` / `reset_aggregate`) sum
  `paper:*`; fanout gains `positions_for_user` / merged `_positions` / `pnl_history_mode_for`
  / `trades_db_path_for`.
- Read repoint (gated; OFF → unchanged window path): `build_pulse`, `build_positions`,
  `build_auto_mode` header + engine-wide aggregate, `build_pnl_history` read per-user;
  `/api/trades` lists the user's own DB via `list_trades(db_path=…)`; paper reset wipes
  every `paper:<uid>` bucket.
- **First unit coverage for the (previously untested) snapshot builders** — per-user
  isolation (no cross-user PnL leak) + OFF-path fallback. 61 tests green.

**VALIDATION GATE (before promoting ON to default):** merge to `main` (deploys OFF, no
behavior change) → set `PAPER_PER_USER_BOOKS=true` + restart paper engine on the VPS →
confirm per-user snapshots populate + `data/paper_books/paper_*_user_<uid>.*` files
appear → then flip ON as the default.

**REMAINING:**
3. App **paper** eligibility selectors + per-symbol management on paper (lumin-app).
4. 360ce-ops engine-wide paper reads → `paper:*` aggregate.

Sign-off flags raised to owner: (a) per-user RiskManagers = no global paper risk cap;
(b) operator paper-reset wipes all users' buckets. Both deemed correct defaults.

---

## 🟢 SESSION 30 2026-06-19 — Raw-Edge diagnostic tab + 60-min invalidation window; MOVER_TREND_PULLBACK gate root-caused

**Owner trigger:** "performance still negative — suspect pre-TP and invalidation;
add an ops view of how signals do WITHOUT them; widen the invalidation window;
and what about that new path (MOVER_TREND_PULLBACK) still firing nothing."
Worked off the attached `signal_performance` (365 closed, Jun 15–19),
`signal_history` (500), `invalidation_records` (154), and a fresh truth report.

### Shipped + MERGED this session
| PR | Repo | What |
|---|---|---|
| [#16](https://github.com/mkmk749278/360ce-ops/pull/16) | 360ce-ops | **Raw Edge** tab — signal edge *without* pre-TP & invalidation: MFE reach, exit attribution (true SL vs pre-TP vs invalidation vs expiry), capture (realized÷MFE), give-back, + invalidation PREMATURE/missed-R per family. Read-only. |
| [#628](https://github.com/mkmk749278/360-v2/pull/628) | 360-v2 | Invalidation-audit observation window **30→60 min** (`INVALIDATION_AUDIT_WINDOW_SEC` 1800→3600). Our scalps run 5–60 min, so 30 min judged kills before the hold elapsed. Observation-only; no FSM change. |

### Diagnosis from the Raw Edge data (the honest answer to the owner's suspicion)
- **Pre-TP IS capping winners.** Book-level *capture* = **6%** (avg MFE 0.53% vs
  avg realized 0.033%); avg give-back **0.51%/signal**. 175 pre-TP signals banked
  +0.39% avg vs +0.85% true peak; 30% reached MFE ≥ 1% and banked a sliver — the
  residual "runner" (§3.2) is dying at break-even instead of running.
- **The 80+ band is the worst** — capture **−7%** (only negative band). High-conviction
  signals reach the biggest MFE (one SR_FLIP +2.11% MFE banked 1.05; a DIV_CONT
  +1.61% MFE realized 0.65) and pre-TP+BE caps them hardest, while the few losers
  take full adverse. Asymmetry inverted exactly where conviction is highest.
- **Invalidation is mostly PROTECTIVE — NOT the main drag.** 113 PROTECTIVE vs 22
  PREMATURE; `momentum_loss` +0.33R/kill (68 prot vs 10 prem). PREMATURE give-back
  (37.8R total) concentrates in `trailing_invalidation` (27% premature rate) and
  `adverse_excursion` — tunable, but gutting invalidation loses money. Told owner
  the invalidation half of the suspicion is largely **not** supported by data.
- **Book context:** raw +12.2% / 365 = +0.033%/sig → net-negative after ~0.07%
  raw round-trip fee. BUT RANGING bleed is gone (+0.029 avg) and SR_FLIP is now
  ~breakeven (−0.012, was −4.80) — Session-29's 3 flags worked. FAR (+0.096) /
  DIV (+0.111) / BDS (+0.277) are the profitable engine — leave alone.

**Next lever (owner-sign-off, FSM):** regime-per-exit (§3.2b) — pre-TP HIGH/OFF for
trend-aligned + the 80+ band, let the residual run. Slice the Raw Edge tab by
`entry_regime` first, bring owner a design before any FSM code.

### MOVER_TREND_PULLBACK (16th path) — root-caused: 0 emissions = a GATE block, not the evaluator
Truth report: ~58k generated, **99.9% gated, 0 emitted**, never reaches the
confidence gate. The evaluator is sound and returns real signals; candidates die
inside `_prepare_signal`'s gate chain.
- **Root cause:** the path is mapped to family **`trend_following`** (PR #627), and
  `trend_following` is in `_SCALP_RANGING_LOW_ADX_BLOCKED_FAMILIES`
  (`scanner/__init__.py:4667-4694`) — any 360_SCALP signal is hard-rejected when
  the entry-TF context is RANGING with ADX < 15. A trend-pullback fires *at* the
  pullback, which reads RANGING/low-ADX on the 5m entry TF **by design**, so the
  gate kills it before scoring. Same failure-mode as the §3.6a scoring bugs, but
  at the **gate** layer (the scoring side was already fixed in #621 via
  `htf_trend_aligned`). **TPE corroborates** — also `trend_following`, 7,742
  generated → 4 emitted.
- **Proposed fix (owner-sign-off — gate + new path; NOT shipped):** exempt
  trend-pullback setups carrying `htf_trend_aligned=True` (MOVER_TREND_PULLBACK's
  MA stack IS its HTF trend; TPE sets it on the 1H-trend path) from the
  RANGING-low-ADX family block — mirrors the #621 doctrine. Narrower option: a
  MOVER_TREND_PULLBACK-only carve-out. Also consider adding it to
  `_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS` (§3.4: mover continuation fires in any HTF
  context). **Awaiting owner decision before shipping.**

---

## 🟢 SESSION 29 2026-06-18 — SR_FLIP/RANGING bleed remedies ACTIVATED on VPS (3 dark flags flipped live)

**Owner trigger:** "analyse signals quality after yesterday's PRs — where are we lagging."
Pulled a **fresh** truth report (monitor-logs, 2026-06-18 07:34 UTC — post-Session-28)
+ the attached `signal_performance` (277 closed sigs, Jun 15–18), `signal_history`
(500), `invalidation_records` (118).

### Finding: yesterday's work didn't touch the bleed
Session 27–28 (#614–#621) was all **scoring/generation on the dead paths**
(VSB/BDS/MA_CROSS/TPE) — correct work, but those paths are a volume rounding error
(VSB n=2, BDS n=7, TPE n=4 in the 277). The actual P&L drag is **unchanged since
Session 24**:
- **SR_FLIP_RETEST −4.80 (n=108 = 39% of all signals).** Upside-down R:R: avg win
  +0.33 vs avg loss −0.42, 63 SL hits. Concentrated in **RANGING −5.50 (60 sigs,
  36 SL)**.
- **RANGING regime −2.22** (47% of volume) — the one losing regime besides tiny VOLATILE.
- **LONGs −2.50 (n=142)** vs SHORTs +7.43; 7 of 8 worst losers are LONG in
  RANGING/UP/VOLATILE — the slice #615's TRENDING_DOWN gate does NOT catch.
- Book gross +4.94% raw (~thin); 24 full-SL events (−25.6 raw) wipe most of the
  +49.4 pre-TP banking. Net ≈ breakeven-to-negative after fees.
- Profitable engine (leave alone): DIVERGENCE_CONTINUATION +6.94, FAILED_AUCTION_RECLAIM +4.37.
- Invalidation audit healthy (76% PROTECTIVE, momentum_loss +0.36R/kill) — the
  KILLS aren't the problem; RANGING SR_FLIP entry quality + exit geometry is.

**The disconnect:** the remedies for this bleed (#603/#604/#608/#613) were merged
and shipped **dark up to 11 days ago and never activated**. We'd been adding
scoring polish to paths that barely fire while the fix for 39% of our volume sat
switched off.

### Owner decision: activate the dark flags (one-shot, owner ran on VPS)
Three flags flipped live + engine `--force-recreate` (verified True×3):
| Flag | Effect |
|---|---|
| `RANGING_LOW_ATR_LOSER_SUPPRESS_ENABLED=true` | drops low-ATR RANGING SR_FLIP/LSR entries (pctile ≤25) — cuts the −5.50 slice at the gate |
| `SR_FLIP_PRETP_R_SCALING_ENABLED=true` | floors pre-TP at SL_dist×0.35R so wide-SL SR_FLIPs stop banking at 0.2R |
| `INVALIDATION_TRAILING_ARM_RSCALE_ENABLED=true` | trailing kill arms at min(0.80, 0.30+0.15×SL%) not flat 0.30R (global) |

`.env` backed up to `.env.bak.<ts>` before the change; one-line revert documented.
**No code shipped this session** — env-only activation. Expect signal VOLUME to drop
(RANGING SR_FLIP was 39% of flow) — intended trade, not a fault.

### NEXT SESSION — judge at +48h on a FRESH truth report (don't judge early):
| Metric | Baseline (this session) | Target |
|---|---|---|
| SR_FLIP `Avg PnL%` | −0.044 | → toward/above 0 |
| RANGING SR_FLIP slice | −5.50 (60 sigs) | → shrinking, fewer sigs |
| `trailing_invalidation` EV/kill | +0.09R (TUNE) | → above +0.10R (KEEP) |
| DIV + FAR | +6.94 / +4.37 | → unchanged (regression = back out) |

Shadow-confirm the drop volume:
`docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "RANGING_LOW_ATR_LOSER_SUPPRESS"`

### Built this session (shadow-first): MOVER_TREND_PULLBACK — the mover continuation path
Owner studied live mover charts (AGT +108%, BTW −28%) and identified a real gap:
VSB/BDS are **one-shot ignition** detectors (swing-break + single retest; #1 reject
`breakout_not_found` 89k) — they catch the breakout candle and go silent for the rest
of the move. The recurring edge on a strong mover is the **continuation**: ride the MA
stack and re-enter every pullback to the MA. TPE is that logic but is locked out of
movers (mover allowlist = VSB+BDS only) and gated on a 1H structure young movers lack.

**New evaluator `_evaluate_mover_trend_pullback` (16th path), owner-approved:**
- Mover-only (self-gates on `smc_data['is_mover_promoted']`, stamped by scanner).
- 15m MA stack (SMA 7/25/99 — the owner's chart) decides direction; LONG gainers,
  SHORT losers. Entry = pullback tags fast-MA band + reclaim candle. SL beyond mid-MA,
  ATR-buffered. R-multiple TP ladder (1.0/1.6/2.5R). `htf_trend_aligned=True` (the stack
  IS the higher-context trend) → full regime affinity + volume-floor via
  `_FAMILY_TREND_PULLBACK` (§3.6a).
- **Ships LIVE** (`MOVER_TREND_PULLBACK_ENABLED=true` default — testing phase, no
  subscribers; see CLAUDE.md § Project Phase). Set the flag false for shadow-only
  fallback. CPU-only, no new reads/writes. Added to `_mover_evaluators` so it runs
  alongside VSB/BDS → the head-to-head the owner asked for (ignition vs continuation).
- 5 new tests; full local suite green (5,329 pass; 42 pre-existing env/dep failures
  confirmed on the stashed tree, none mine). Files: `config/__init__.py`,
  `channels/scalp.py`, `scanner/__init__.py`, `signal_quality.py`,
  `tests/test_mover_trend_pullback.py`, `tests/test_scanner.py` (count 15→16).

**Activation (after shadow window):** read `[SHADOW] MOVER_TREND_PULLBACK_WOULD_FIRE`
counts on the VPS to size opportunity, then `MOVER_TREND_PULLBACK_ENABLED=true` +
engine recreate. Compare VSB/BDS vs MOVER_TREND_PULLBACK on the truth report; keep the
winner(s).

### Session 29 follow-up — mover gate was too narrow (fixed)
First live check (VPS logs) showed the path live + registered but **0 emissions** —
root cause: the real movers (BTW −28%, ESPORTS +109%) enter the scan as
**universe/young pairs**, not via mover-promotion, so the `is_mover_promoted` gate
locked the path out of its own targets (BTW was logged as `young_pair_restriction`,
ESPORTS in the critical-pairs set; zero `MOVER PROMOT` lines in 3h). Fix: define
"mover" by **MA7↔MA99 stack separation ≥ `MOVER_TP_MIN_STACK_SEP_PCT` (3%)** instead
of promotion bookkeeping, and add the path to `_YOUNG_PAIR_EVALUATORS` so young
movers can run it. Now fires on a strong run wherever the pair sits; gently-trending
majors stay TPE's domain. Removed the now-dead `is_mover_promoted` scanner stamp.
Confirm live: `docker logs 360scalp-v2-engine --since 1h | grep -c MOVER_TREND_PULLBACK`.

### Still open after this (next levers, in order)
1. **LONG bleed** — −2.50, worst losers are LONG in RANGING/UP/VOLATILE; #615 only
   gates TRENDING_DOWN. Investigate extending the longs regime gate (shadow-first).
2. **SR_FLIP entry-quality re-tighten** (#612 kill-switch never merged; #613 dark
   re-tighten) — only if the 3 flags above don't pull RANGING SR_FLIP to ~breakeven.
3. **TPE generation gate** (82.6%-SL guard) — still deferred, shadow-first.

---

## ⏳ SESSION 28 CLOSE 2026-06-17 — scoring corrections shipped, NOW WAITING FOR DATA

**Do not re-diagnose VSB / BDS / TREND_PULLBACK_EMA / MA_CROSS_TREND_SHIFT off the
current truth report.** The latest `monitor-logs` truth report has **cumulative
counters that predate today's merges** — it still shows the *old* (pre-change)
emission. The four scoring/filter PRs below all merged today and auto-deployed;
their effect will only appear after a fresh data window accumulates. Next session:
**pull a fresh truth report first**, then judge.

**Merged today (all on `main`):**
| PR | Path(s) | Change |
|---|---|---|
| #618 | VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT | regime floor 8→14; score volume off the validated breakout candle |
| #619 | MA_CROSS_TREND_SHIFT, TREND_PULLBACK_EMA | MA_CROSS regime 8→14; TPE volume floored at neutral 7.5 |
| #620 | MA_CROSS_TREND_SHIFT | HTF trend-alignment gate (1h cross must agree with 4h trend; 4h cross price-vs-EMA200 confirm) |
| #621 | TREND_PULLBACK_EMA | regime scored on the HTF (1H) trend via `htf_trend_aligned` → 18, not the 5m label |

Durable lesson promoted to `OWNER_BRIEF.md §3.6a` (Scoring Doctrine).

**Path emission snapshot (PRE-change, from stale truth report — for reference only):**
- Producing: SR_FLIP_RETEST 165, FAILED_AUCTION_RECLAIM 115, LIQUIDITY_SWEEP_REVERSAL 82, DIVERGENCE_CONTINUATION 32, VOLUME_SURGE_BREAKOUT 3, POST_DISPLACEMENT_CONTINUATION 1, QUIET_COMPRESSION_BREAK 1.
- 0-emit (today's targets): TREND_PULLBACK_EMA (571 gen), BREAKDOWN_SHORT (2225 gen), MA_CROSS (15 gen), + WHALE_MOMENTUM / FUNDING_EXTREME / LIQUIDATION_REVERSAL.
- Disabled: OPENING_RANGE_BREAKOUT (feature_disabled), CONTINUATION_LIQUIDITY_SWEEP (merged into LSR), TREND_PULLBACK_CONTINUATION (legacy).

**Open items / next levers (after data confirms):**
1. **TPE generation bottleneck still deferred** — the over-tight entry-quality gate (`no_prev_high_break` + `ema21_not_tagged`, the 82.6%-SL guard). Today's PRs fix TPE *scoring*, not *generation*. Do it shadow-first if data shows survivors scoring well but volume still low.
2. **kept-vs-emitted gap** — across all paths, confidence-"kept" is 10–30× "emitted". Likely expected dedup of the same signal across 15s cycles; **confirm dedup-vs-cull** before assuming a bug. Potentially the highest-leverage cross-path investigation.
3. **MA_CROSS will stay near-zero by nature** (15 gen; crosses are rare; #620 filter cuts further) — not a bug, don't loosen.
4. **WHALE_MOMENTUM / FUNDING_EXTREME / LIQUIDATION_REVERSAL** — 0-emit, low gen, not yet diagnosed this session.

---

## Session 28 checkpoint 2026-06-17 — TPE regime scored on the wrong timeframe (HTF-aware fix, research-backed, owner-approved)

### Owner trigger
Owner asked about the regime score for the TREND_PULLBACK_EMA path, then: "go
through deep research on crypto trend-pullback conditions / which timeframes
give best, then we decide."

### Research finding (web, multi-source)
Pullbacks are a **trending-market** setup ("step aside" in ranges). Canonical
multi-timeframe doctrine: **trend is defined on the HIGHER timeframe; entry is
timed on the LOWER** (HTF=trend → MTF=structure → LTF=entry). Rule repeated
everywhere: *"never trade against the HTF trend; always time entry on the LTF."*
EMA21 = canonical pullback-retest level, EMA50 = trend filter — our 1H EMA21/50
usage matches. This validates the evaluator's post-2026-05-17 redesign (trend on
1H, entry on 5m; the old 5m-trend version scored 78% MFE=0).

### Diagnosis
`_score_regime` judges TPE on `ctx.regime_result.regime` — the **5m label**, the
*entry* TF. During the pullback the 5m label reads RANGING/QUIET, so TPE dropped
to **8** even though it only fires when the **1H is trending** (evaluator
precondition). Scoring the trend on the entry timeframe is the exact multi-TF
error the research warns against.

### Owner decision: HTF-aware regime score (the doctrinally-ideal option, not the quick 14-floor)
### Shipped (branch `feat/tpe-htf-regime-score`)
| Change | File |
|---|---|
| New `Signal.htf_trend_aligned` flag | `channels/base.py` |
| TPE stamps `sig.htf_trend_aligned = bool(_uses_1h_trend)` (True only on the 1H-trend path) | `channels/scalp.py` |
| New `ScoringInput.htf_trend_aligned` | `signal_quality.py` |
| `_score_regime`: trend-pullback family with `htf_trend_aligned` → full affinity **18** in any regime (scoped to `_FAMILY_TREND_PULLBACK`; legacy 5m-fallback path keeps the label score) | `signal_quality.py` |
| Scanner passes `sig.htf_trend_aligned` into `ScoringInput` | `scanner/__init__.py` |
| 5 scorer tests (`TestTrendPullbackHtfRegimeScore`) + 2 evaluator tests (`TestTrendPullbackHtfFlag`, incl. fires-under-RANGING-label) | `tests/test_signal_quality.py`, `tests/test_channels.py` |

CPU-only; no new reads/writes/hot-path cost. Full suite passes.
Still secondary to TPE's real generation bottleneck — the over-tight entry-quality
gate (82.6%-SL guard, `no_prev_high_break` + `ema21_not_tagged`) deferred in #619;
that's the next lever if we want TPE *generation* up (shadow-first).

---

## Session 28 checkpoint 2026-06-17 — MA_CROSS: filter is the edge, not the period (research-backed, owner-approved)

### Owner trigger
Owner: "understand crypto market and which ema works… go through research and
actually what works implement that."

### Research finding (web, multi-source — quant-signals, QuantifiedStrategies, hyrotrader, et al.)
**The EMA *periods* are second-order; the FILTER is the edge.** Consistent across
sources: raw MA crosses LOSE money in crypto (~60% of time ranging → whipsaws;
lag eats the move). 50/200 is the most robust *structural* pair (~40% win rate,
trend-following payoff — beat BTC buy-and-hold 2017-25 on 4h/6h); 9/21 etc. are
faster but whipsaw more. **Adding a higher-timeframe trend filter improves results
far more than tuning periods.** → Our existing periods (4h 50/200, 1h 21/50) are
already the research-favoured choices; the gap was the *filter*.

### Owner decision: HTF-alignment gate (periods unchanged)
Did NOT touch periods (research says don't). Added the filter that actually drives
the edge.

### Shipped (branch `feat/ma-cross-htf-alignment`)
| Change | File |
|---|---|
| 1h 21/50 cross now fires only when it agrees with the **4h structural trend** (ema50_4h vs ema200_4h); fails closed (`ma_cross_htf_unconfirmed`) if 4h unavailable, rejects (`ma_cross_htf_misaligned`) if counter-HTF | `channels/scalp.py` |
| 4h 50/200 cross gets a light **price-vs-EMA200 confirmation** (rejects failing/reverted crosses; fail-open if EMA200 missing) | `channels/scalp.py` |
| 5 tests (`TestHtfAlignmentGate`) | `tests/test_ma_cross_trend_shift.py` |

CPU-only; reuses 4h indicators already in scope — no new reads/writes/hot-path
cost. Reduces generation (filters do) in exchange for higher win quality — the
right trade for a paid A+/B-only channel. Full suite 5,618 pass.
Synergy with #619: the regime-neutral 14 + HTF gate together mean a 1h cross is
no longer regime-penalised AND is confirmed by the 4h trend.

### Declined (told owner, per "tell me when a direction is wrong")
Adding a faster 9/21 tier for more signals — research does not support it
(faster pairs whipsaw more). Quality over quantity.

---

## Session 28 checkpoint 2026-06-17 — TREND_PULLBACK + MA_CROSS scoring deficits (scoring-only fix, owner-approved)

### Owner trigger
Owner: "trend pull back and ma cross trend shift — concentrate on them." Same
data-first deep dive as VSB/BDS, off the live truth report.

### Root cause (per-path)
- **MA_CROSS_TREND_SHIFT** (15 generated, 0 emitted): generation is **inherently
  sparse and correct** — a golden/death cross is a once-in-days event
  (`no_ma_cross` 69%); the 24h cooldown is right. The fixable bug: MA_CROSS was
  **absent from every `_REGIME_SETUP_AFFINITY` list and the neutral set** →
  `_score_regime` returned a flat **8.0** in all regimes. A cross fires AT the
  regime turn (5m label still RANGING) → penalised for doing its job.
- **TREND_PULLBACK_EMA** (571 generated, 0 emitted): two layers.
  (1) Volume dimension scored the quiet pullback entry candle 3/15 — a healthy
  pullback is low-volume BY DESIGN. (2) The "entry-quality tightening" block
  (scalp.py ~1580-1609) demands a near-unicorn candle that both deep-wicks to
  tag EMA21 (`ema21_not_tagged`) AND closes above the prior high
  (`no_prev_high_break`) — crushing generation. (2) was added to fix an 82.6%
  SL rate, so it's money-risky to loosen.

### Owner decision: "scoring fixes only"
Shipped the two safe scoring corrections; **left the TPE entry gates untouched**
(TPE stays low-generation by choice — relaxing those gates re-imports the
82.6%-SL risk and would need shadow measurement first).

### Shipped (branch `feat/trendpullback-macross-scoring`)
| Change | File |
|---|---|
| `MA_CROSS_TREND_SHIFT` added to `_REGIME_NEUTRAL_SETUPS` → regime 8→14 (fires at the transition, like a counter-trend setup) | `signal_quality.py` |
| `_score_volume` floors the `_FAMILY_TREND_PULLBACK` family at neutral 7.5 — quiet pullback volume no longer scored 3/15; high-volume reclaims still earn more | `signal_quality.py` |
| 5 tests (`TestTrendPullbackAndMaCrossScoring`) | `tests/test_signal_quality.py` |

CPU-only scorer change; no hot-path reads/writes. Full suite 5,613 pass.

### Deferred (owner-gated, NOT done)
- **TPE entry-gate de-contradiction** (the `no_prev_high_break` + `ema21_not_tagged`
  double-bind). Highest lever for TPE *generation*, but money-risky — do it
  shadow-first if/when the owner wants the volume back.

---

## Session 27 checkpoint 2026-06-17 — top-mover breakout/breakdown paths were dying in the SCORER, not the gates (VSB/BDS)

### Owner trigger
Owner: "why are the remaining paths not producing signals" → "we have two special
paths for shorts and longs top movers, separate from the regular 75 — VSB and BDS
— go deep on them." Diagnosis driven off the live truth report (monitor-logs).

### Architecture recap
Movers (24h %-change ≥ `MOVER_PROMOTION_MIN_PCT`, vol ≥ `MOVER_PROMOTION_MIN_VOLUME`)
are promoted into the scan for `MOVER_PROMOTION_CYCLES` (5) with a **restricted
evaluator set: VSB (long, top gainers) + BDS (short, top losers) only**.

### Root cause (truth report, path-funnel + scoring-dimension tables)
Both evaluators correctly **removed their regime gate** (§3.4 "fire in any HTF
context") and the broken current-candle volume gate — but those fixes were
**never applied at the SCORING layer**, so the composite scorer kept punishing
them for the exact things that define them:
- **VSB dies on the Regime dimension (8 vs 18 kept).** `_score_regime` gives 8
  when the regime is known but the setup isn't in its affinity list. VSB/BDS are
  in TRENDING/VOLATILE affinity but NOT RANGING/QUIET — and a top gainer
  mid-pullback often reads RANGING/QUIET on 5m (market is 64% RANGING+QUIET). 10-pt
  deficit → lands ~61 vs the 65 floor. (My #614 unification increased the RANGING
  share, slightly worsening this.)
- **BDS dies on the Volume dimension (3 vs 12 kept).** `_score_volume` scores the
  current candle, but the BDS entry is a dead-cat bounce (low volume by design);
  the surge already fired on the breakdown candle, which the scorer never saw.

### Shipped (branch `feat/mover-breakout-scoring`, owner approved "both fixes, neutral floor")
| Change | File(s) |
|---|---|
| `_score_regime`: floor breakout-surge setups (`_BREAKOUT_SURGE_SETUPS` = VSB/BDS/ORB) at neutral 14 in non-affinity regimes instead of 8 | `signal_quality.py` |
| `_score_volume`: for those setups, score off the validated breakout-candle ratio (`breakout_volume_ratio`) instead of the low-volume entry candle; falls back to the entry ratio when unset | `signal_quality.py` |
| Evaluators stamp `sig.breakout_volume_ratio = breakout(/down)_vol / rolling_avg` | `channels/scalp.py` |
| New `Signal.breakout_volume_ratio` + `ScoringInput.breakout_volume_ratio` fields; scanner passes it through | `channels/base.py`, `signal_quality.py`, `scanner/__init__.py` |
| 8 scoring tests (`TestBreakoutSurgeScoring`) | `tests/test_signal_quality.py` |

Expected: VSB recovers ~10 regime pts, BDS ~9 volume pts → both clear 65 when
otherwise structurally sound, without touching any hard gate. No new hot-path
reads/writes (CPU-only scorer change). Owner-sign-off item (scoring model).

### Watch next session
- Truth report: VSB/BDS `Emitted` column should rise from ~0–3; confirm the
  `Regime`/`Volume` filtered-vs-kept gaps close for these two setups.
- The current truth report predates #614–#617 + this change — next report is the
  first to reflect all of them.

---

## Session 26 checkpoint 2026-06-17 — MTF trend definition unified + longs HTF-regime gate (PRs #614, #615 MERGED)

### Owner trigger
Continuing the signals-quality work: the 496-signal audit's losing bucket was
LONGs fired while the higher timeframe was rolling over. Owner approved the
"Option 2" fix (unify the trend definition, then gate longs on it).

### Root cause
Two contradictory definitions of "trend":
- **5m (`AdaptiveRegimeDetector._decide_adaptive`)** stamped TRENDING in the weak
  ADX zone (between the tier's ranging/trending floors) on EMA separation alone
  — even with ADX *decaying* — manufacturing trends from fading moves.
- **15m (`detect_regime_from_arrays`)** used a flat ADX≥25 floor, no weak zone,
  no tier profile — so a midcap at ADX 22 read TRENDING on 5m and RANGING on 15m
  *by construction*, making any MTF comparison meaningless.

### Shipped (branch `claude/google-services-cost-analysis-w61lnc`)
| PR | Change | File(s) |
|---|---|---|
| **#614 MERGED** | Weak-zone trends now require ADX **rising** (`adx_slope>0`); unknown slope → RANGING. `detect_regime_from_arrays` made **tier-aware** + same weak-zone rule, so 5m and 15m mean the same thing by "trend". | `regime.py`, `scanner/__init__.py`, `tests/test_regime_mtf_unification.py` (9 tests) |
| **#615 MERGED** | **Filter 1b** in `_prepare_signal`: drop a LONG when the unified 15m regime is TRENDING_DOWN. Env toggles `MTF_LONGS_REGIME_GATE_ENABLED` (default on) + `MTF_LONGS_REGIME_GATE_DARK` (measure-only). Telemetry: `mtf_longs_regime_eval/block/would_block`. | `scanner/__init__.py`, `tests/test_scanner.py` (`TestLongsRegimeGateInScanner`) |
| **follow-up (this session, in PR)** | **§3.4 doctrine bypass for Filter 1b**: breakout/tape/liquidation-reversal longs (`_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS`) are NOT HTF-vetoed — a breakout into a down 15m IS the regime change. Owner chose "exempt them". Telemetry: `mtf_longs_regime_doctrine_bypass:360_SCALP:<setup>`. | `scanner/__init__.py`, `tests/test_scanner.py` |

Per the owner's audit, removing the losing longs bucket flipped the audited
book from **−14.1 to +3.0** (owner-supplied figure, not re-measured here).

### Watch next session
- **`/suppressed` → `mtf_longs_regime_block` vs `mtf_longs_regime_doctrine_bypass`**:
  confirm the live block volume tracks the audit, and see how many longs the
  §3.4 exemption preserves. Flip `MTF_LONGS_REGIME_GATE_DARK=true` to pull back
  to measure-only without a code redeploy.
- Shorts are intentionally ungated; only 15m is used (not 1h/4h) — both deliberate.

### Follow-up (not done)
- **Pre-existing API test red** (FastAPI `204` + `response_model` at app
  construction) is failing on `main` in CI's container — unrelated to these PRs,
  but a possible live `api`-container risk. Worth confirming the live FastAPI pin.

---

## Session 25 checkpoint 2026-06-16 — GCP cost spike was Firestore reads, not auth (PR #609, MERGED)

### Owner trigger
Owner shared the `lumin-app` GCP/Firebase billing screens: ₹4,558/mo with a
climbing forecast, asking why "phone-number authentication only" was costing
so much. The "App Engine" line dominated despite **no App Engine services
deployed**.

### Root cause (confirmed on live billing data)
- **99.9% of the bill is Cloud Firestore — ₹4,552 — and specifically READS.**
  Writes/deletes sat inside the free tier; the read free-tier quota was
  exceeded daily. **Phone Auth / SMS = ₹0 (0% of quota).** Auth was never the
  cost — it was a red herring.
- **Why "App Engine" with no App Engine services:** Firestore-in-Datastore-mode
  bills under the "App Engine" SKU grouping in GCP. Confirmed via Billing →
  SKU breakdown (Cloud Firestore ₹4,552.25, non-Firebase ₹5.88) + the Firebase
  Usage tab ("Reads: limit exceeded").
- **The leak:** `pretp_dispatcher._on_tick` ran a Firestore collection-group
  query on *every* mark-price tick (~1/sec × open symbols, 24/7) to find OPEN
  positions. The module header already flagged it as `O(N) per tick` debt.

### Shipped (branch `claude/google-services-cost-analysis-w61lnc`, PR #609 — MERGED to main)
| Change | File(s) | Notes |
|---|---|---|
| `_write_generation` counter, bumped on `put_position`/`delete_position`; `get_write_generation()` | `position_state.py` | the freshness signal |
| Per-symbol OPEN-positions cache gated on that generation (+ defensive 10s TTL) | `pretp_dispatcher.py` | removes Firestore from the per-tick hot path |
| Cache tests (generation invalidation, TTL expiry, per-symbol, put/delete bump) | `tests/test_pretp_dispatcher_cache.py` | 5 new; 325 in the exec suite pass; ruff clean |

Correctness: the cache cannot serve a stale `pretp_fired`/`state` and double-fire
— every mutation funnels through `put_position`/`delete_position`, both of which
bump the generation and invalidate. No change to pre-TP threshold/firing logic.

### Process changes (this session)
- **`CLAUDE.md` gained a "Cost Discipline" section** + a Hard Limit ("never add
  an uncached Firestore/network read to a hot loop") + an operating-standard
  bullet ("cost is a first-class concern"). Every future change is reviewed for
  cost the way it's reviewed for correctness.

### Follow-up (not done)
- **Full in-memory open-positions index** would eliminate even the cold-path
  query (zero reads). The generation-gated cache is the lower-risk first step;
  the index is the next optimisation if reads still register.
- **No PR-level CI exists** in this repo (only `deploy.yml` on push-to-main +
  manual `vps-monitor`). Local test/lint runs are the only pre-merge gate today
  — worth adding a PR test workflow.
- Confirm the bill drops after the engine redeploys with #609 (reads keep
  accruing until the new image is live).

---

## Session 24 checkpoint 2026-06-15 — signals-quality audit: the bleed is RANGING SR_FLIP/LSR, not the trending exits

### Owner trigger
Owner reported sustained losses (paper P&L 7d −$34.74) and asked for a full
audit "per path / per regime / per market / per pair" — why the auto engine
lags a manual trader.

### Root-cause findings (live data, last-100 signals Jun 13–15)
- **The bleed is RANGING, not trending.** RANGING = 67% of volume and −7.22%
  of the −8.7% aggregate. TRENDING_DOWN ≈ flat (−0.12%). The two exit flags
  that ARE on (`TRENDING_PRETP_SUPPRESSED=True`, `RETRACE_REGIME_AWARE=True`)
  only touch the ~26% trending slice — they cannot fix a RANGING bleed. That
  is why flipping them never moved P&L.
- **Concentrated in two setups:** SR_FLIP_RETEST −4.36% (45 sigs, +0.25/−0.38)
  and LIQUIDITY_SWEEP_REVERSAL −3.77% (20 sigs, +0.47/−0.73). Both ~1:2
  win:loss. FAILED_AUCTION_RECLAIM (+0.71, 67% win) and DIVERGENCE_CONTINUATION
  (+0.42, 60% win) are profitable — leave alone.
- **0 TP hits / 45 full SL / 55 pre-TP-or-invalidation** across 100. Wins are
  capped small while losers run to wide structural stops → upside-down R:R.
- **`entry_regime` is EMPTY on the monitor's signals_last100.json** even with
  #606 in the tree. signals_last100.json is monitor-augmented (carries
  non-dataclass fields), so this is NOT authoritative for live FSM state —
  but it is suspicious. AUTHORITATIVE CHECK PENDING (see open items): read
  `data/signal_history.json` (raw vars(sig) dump) on the VPS. If empty there,
  the Session-23 bug is back / engine image predates #606 → rebuild engine.
- Tokenized-stock blacklist confirmed working (none in last 100).

### Shipped this session (branch `claude/signals-quality-audit-yn1a1f`, NOT yet PR'd to main)
| Change | File(s) | Default | Reversible |
|---|---|---|---|
| Micro-cap momentum-kill bug fix — sub-$0.001 coins no longer get a 10×-tighter kill threshold (momentum is scale-invariant); `INVALIDATION_MOMENTUM_MICROCAP_MULT` default 1.0 | `config`, `trade_monitor.py` | **LIVE (1.0)** | env → 0.1 |
| `entry_regime`/`entry_regime_15m` stamped into `dispatch_log.json` | `signal_router.py` | live (telemetry) | n/a |
| RANGING low-ATR loser-suppression gate (SR_FLIP/LSR only, ATR%ile ≤ 25) | `config`, `scanner` | **DARK** + `[SHADOW]` | flag |

All tests green (913 passed in the scanner/quality/invalidation sweep; 4 + 8
new cases). No PR to main opened yet (owner batching the full package).

### Geometry rebuild (C) — DONE on branch (dark), owner sign-off to activate
- **SR_FLIP:** already built (#603 pre-TP R-scaling, #604 trailing-arm R-scale)
  — activation only.
- **LSR (this session):** win-side `LSR_PRETP_R_SCALING_ENABLED` (pre-TP
  R-scaling, mirror of #603) + loss-side `LSR_SL_TIGHTEN_ENABLED`
  (`LSR_MAX_SL_PCT_TIGHT` 1.5%). LSR is reject-not-compress, so the tighten
  DROPS wide-stop LSRs (no wick-out risk). Both dark + shadow.

### Remaining work (owner)
1. **Run the authoritative `entry_regime` check** (signal_history.json) + rebuild
   engine if empty — settles whether the trending exit-flags are actually live.
2. **Activation sequence (A)** — see runbook below, after merge + 48h shadow.

### Activation runbook (owner — after the entry_regime check + engine rebuild)
```bash
cd /root/360-v2
# AUTHORITATIVE entry_regime check (settles whether the trending flags are live):
docker exec 360scalp-v2-engine python -c "import json; d=json.load(open('data/signal_history.json')); r=sorted(d,key=lambda x:x.get('timestamp',0))[-6:]; [print(x.get('symbol'),repr(x.get('entry_regime'))) for x in r]"
# If empty -> rebuild so #606 is actually running:
docker compose -f docker-compose.yml --profile isolated up -d --no-deps --force-recreate engine
```
Then, once this branch is merged to main + deployed, read 48h of shadow counts
before flipping each flag:
```bash
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] RANGING_LOW_ATR_LOSER_SUPPRESS"
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] MICROCAP_MOMENTUM_SPARED"
```
Activation order (one at a time, measure between): SR_FLIP R-scaling (#603) →
trailing-arm R-scale (#604) → RANGING low-ATR suppression → revisit LSR geometry.

---

## Session 23 checkpoint 2026-06-10 — entry_regime empty bug found and fixed (PR #606)

### Root cause finding (drove the session)

`TRENDING_PRETP_SUPPRESSED` shadow telemetry (`DARK_FLAG_SHADOW_TELEMETRY=true`) returned
**0 hits after 48h** despite signals dispatching normally. Diagnosis: `sig.entry_regime`
was always `""` at dispatch time for every signal.

Bug in `_populate_signal_context` (`src/scanner/__init__.py`): `sig.entry_regime = rc.label`
was inside a `try` block that ran `float(rc.atr_percentile)` and `float(rc.adx_slope)` in
f-strings **above** it. When either `float()` raised `TypeError` or `ValueError`, the
`except` clause silently dropped the entire block — `entry_regime` was never written,
leaving the `Signal` default of `""`.

### Impact (two features were dead letters in production)

| Feature | PR | Effect |
|---|---|---|
| `TRENDING_PRETP_SUPPRESSED` shadow + real flag | #594 | `regime_label=""` → suppress condition always False; 0 shadow hits since deploy |
| Regime-per-exit FSM gating | #578 | `entry_regime=""` → all FSM regime checks silently bypassed on every dispatched position |

### Fix — PR #606 (merged 2026-06-10)

`sig.entry_regime = rc.label` hoisted above the `try` block. Pure string assignment,
cannot raise. The `float()` calls that may fail remain inside `try/except` as before.

### Action required on VPS after merge

```bash
# Rebuild engine image with the fix:
cd /root/360-v2
docker compose -f docker-compose.yml --profile isolated up -d --no-deps --force-recreate engine

# Confirm shadow telemetry now fires (within hours of next TRENDING signal dispatch):
docker logs 360scalp-v2-engine -f | grep "\[SHADOW\] TRENDING_PRETP_SUPPRESSED"

# Confirm entry_regime is now populated on dispatched positions:
docker exec 360scalp-v2-redis redis-cli hgetall snapshot:<uid> 2>/dev/null | grep entry_regime
```

### Open items (priority order)

1. **Deploy PR #606 on VPS** — `docker compose ... up -d --no-deps --force-recreate engine` after merge.
2. **Confirm shadow telemetry fires** — grep `[SHADOW] TRENDING_PRETP_SUPPRESSED` post-deploy; expect counts within hours.
3. **Re-verify regime-per-exit live (PR #578)** — with `entry_regime` now populated, confirm it is non-empty in Redis snapshot and FSM trail/cancel paths are actually being reached.
4. **TRENDING_PRETP_SUPPRESSED activation** — blocked on 7 days of shadow data post-#606 deploy. Do not activate blind.
5. **Change A activation on VPS** — `SR_FLIP_CONSECUTIVE_REQUIRED=3`; commands in Session 22 section below.
6. **#604 shadow telemetry → activation** — read `TRAILING_RSCALE_WOULD_SUPPRESS` count after 48h, then activate `INVALIDATION_TRAILING_ARM_RSCALE_ENABLED=true`.
7. **Google Play approval** — awaiting email (submitted 2026-06-06, ≤7 days). Complete store listing + data-safety form while waiting.
8. **Scoring-model rebuild** — blocked on data accumulation in Ops score-band view.

---

## Session 22 checkpoint 2026-06-07 — SR_FLIP premature-kill audit + trailing R-scale arm

### Root cause finding (drove the session)

Owner ran `invalidation_records.json` audit on VPS. Among 16 PREMATURE SR_FLIP kills:

| Kill family | Count | Premature % |
|---|---|---|
| trailing_invalidation | 7 | **44%** |
| momentum_loss | 4 | 16% |
| other | 5 | — |

Root cause of `trailing_invalidation` dominance: the trailing kill **arms at a flat 0.30R** regardless of SL width. SR_FLIP structural SLs are 1.6–2.5% wide. At 0.30R × 1.6% SL ≈ 0.48% absolute, normal reversal pullbacks (>50% retrace) fire the kill near breakeven before the position has established real profit. EDGEUSDT was the canonical proof: entry 0.6472 SHORT, SL 1.63%, MFE 0.56% (+0.36% R) → killed at 0.06% by a retrace.

### What shipped this session (2 PRs merged)

| PR | What | Flag (default) | Shadow telemetry |
|---|---|---|---|
| [#603](https://github.com/mkmk749278/360-v2/pull/603) | **Change A**: SR_FLIP momentum-kill grace — per-setup `INVALIDATION_CONSECUTIVE_THRESHOLD` key (`360_SCALP::SR_FLIP_RETEST`) requires 3 vs 2 consecutive bad-momentum readings | `SR_FLIP_MOMENTUM_GRACE_ENABLED` (false) | `[SHADOW] SR_FLIP_GRACE_WOULD_SUPPRESS` |
| [#603](https://github.com/mkmk749278/360-v2/pull/603) | **Change B**: SR_FLIP pre-TP R-scaling — floors pre-TP threshold at `SL_dist_pct × 0.35R` so wide-SL signals don't bank at 0.20R | `SR_FLIP_PRETP_R_SCALING_ENABLED` (false) | `[SHADOW] SR_FLIP_RSCALE_WOULD_RAISE` |
| [#604](https://github.com/mkmk749278/360-v2/pull/604) | **R-scaled trailing-kill arm** — arm threshold becomes `min(0.80, 0.30 + 0.15 × sl_dist_pct)` globally for all setups; fixes the EDGEUSDT premature kill class | `INVALIDATION_TRAILING_ARM_RSCALE_ENABLED` (false) | `[SHADOW] TRAILING_RSCALE_WOULD_SUPPRESS` |

Both PRs ship **completely dark** — no live behavior change on merge. 5566 tests pass, 0 failures.

### Change A activation (owner task — do now)

Owner decided to activate Change A immediately (momentum-kill grace for SR_FLIP, `SR_FLIP_CONSECUTIVE_REQUIRED=3`). Commands on VPS:

```bash
cd /root/360-v2
grep -q '^SR_FLIP_CONSECUTIVE_REQUIRED=' .env \
  && sed -i 's/^SR_FLIP_CONSECUTIVE_REQUIRED=.*/SR_FLIP_CONSECUTIVE_REQUIRED=3/' .env \
  || echo 'SR_FLIP_CONSECUTIVE_REQUIRED=3' >> .env
docker compose -f docker-compose.yml --profile isolated up -d --no-deps --force-recreate engine
# Verify:
docker exec 360scalp-v2-engine python -c \
  "from config import INVALIDATION_CONSECUTIVE_THRESHOLD as c; print(c.get('360_SCALP::SR_FLIP_RETEST'))"
# → should print 3
```

### Activation sequence for #604 (read shadow data first)

After 48h with the new engine image deployed, check shadow counts:

```bash
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] TRAILING_RSCALE_WOULD_SUPPRESS"
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] SR_FLIP_GRACE_WOULD_SUPPRESS"
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] SR_FLIP_RSCALE_WOULD_RAISE"
```

When confident in shadow count, activate #604:
```bash
echo 'INVALIDATION_TRAILING_ARM_RSCALE_ENABLED=true' >> /root/360-v2/.env
docker compose -f docker-compose.yml --profile isolated up -d --no-deps --force-recreate engine
```

### New config constants (all in `config/__init__.py`)

```
SR_FLIP_CONSECUTIVE_REQUIRED          = 2       (3 when activated)
SR_FLIP_MOMENTUM_GRACE_ENABLED        = false
SR_FLIP_PRETP_R_SCALING_ENABLED       = false
SR_FLIP_PRETP_R_FACTOR                = 0.35
INVALIDATION_TRAILING_ARM_RSCALE_ENABLED  = false
INVALIDATION_TRAILING_ARM_R_PER_SL_PCT    = 0.15
INVALIDATION_TRAILING_ARM_R_MAX           = 0.80
```

### Open items (priority order)

1. **Change A activation on VPS** — owner task, commands above. Verify 3 is live before enabling #604.
2. **#604 shadow telemetry** — read `TRAILING_RSCALE_WOULD_SUPPRESS` count after 48h, then activate `INVALIDATION_TRAILING_ARM_RSCALE_ENABLED=true`.
3. **Google Play approval** — awaiting email (≤7 days from 2026-06-06). Complete store listing / data-safety form while waiting.
4. **Scoring-model rebuild** — still blocked on data accumulation in the Ops score-band view.
5. **PR #594 (regime-aware exit)** — owner sign-off required. Do not auto-merge. Touches position FSM / regime-per-exit doctrine (§3.2b).
6. **Dark-flag shadow telemetry (session-19/20 flags)** — read counts before enabling `TRENDING_PRETP_SUPPRESSED`, `PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED`, `INVALIDATION_BTC_CORRELATION_ENABLED`:
   ```bash
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] TRENDING_PRETP_SUPPRESSED"
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] PRETP_FULLGRAB_ON_CANCEL"
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] INVALIDATION_BTC_CORRELATION"
   ```

---

## Session 21 checkpoint 2026-06-06 — Play Store submitted + universe/reset-defaults complete

### What shipped this session

| PR | Repo | What | Status |
|---|---|---|---|
| [#599](https://github.com/mkmk749278/360-v2/pull/599) | 360-v2 | Scan blacklist sweep: CRCL/MU/INTC/CL/EWY added to `SCAN_SYMBOL_BLACKLIST` | Merged |
| [#600](https://github.com/mkmk749278/360-v2/pull/600) | 360-v2 | All 9 tokenized stocks added to `_NON_CRYPTO_BLACKLIST` (selection-time) — guarantees 75 real crypto pairs | Merged |
| [#601](https://github.com/mkmk749278/360-v2/pull/601) | 360-v2 | `DELETE /api/settings/user/pretp` + `DELETE /api/settings/user/invalidation` — reset per-user settings to engine defaults | Merged |
| [#93](https://github.com/mkmk749278/lumin-app/pull/93) | lumin-app | Reset-to-engine-defaults button on Pre-TP and Invalidation settings pages; Pre-TP page redesign (headline controls + collapsed Advanced) | Merged |
| [#94](https://github.com/mkmk749278/lumin-app/pull/94) | lumin-app | `LUMIN_DISTRIBUTION` compile-time flag + `kSelfUpdateEnabled` const — gates Play AAB off the self-updater | Merged |
| [#95](https://github.com/mkmk749278/lumin-app/pull/95) | lumin-app | `build-apk.yml` AAB step adds `--dart-define=LUMIN_DISTRIBUTION=play` — defense in depth | Merged |
| [#96](https://github.com/mkmk749278/lumin-app/pull/96) | lumin-app | `docs/PLAYSTORE_SUBMISSION.md` — paste-ready Play Console answers, data-safety table | Merged |

### Google Play production application — SUBMITTED

Applied today 2026-06-06 at 18:06. Confirmation screen: "We have your application for production access." Google will email within 7 days.

**Remaining Play Console steps (complete while waiting for approval):**
1. Data safety form — use table in `docs/PLAYSTORE_SUBMISSION.md`
2. Store listing — name, short/full description, screenshots, feature graphic
3. Content rating — IARC questionnaire (answer truthfully; paper trading is not gambling)
4. Upload Play AAB — trigger tag push or `flutter build appbundle --release --dart-define=LUMIN_DISTRIBUTION=play`
5. Pricing & distribution — set regions matching the in-app region gate

### Universe fix — confirmed complete

Two-layer blacklist now in place:
- **Scan-time** (`SCAN_SYMBOL_BLACKLIST`): 9 tokenized stocks excluded before scanning
- **Selection-time** (`_NON_CRYPTO_BLACKLIST`): same 9 excluded before the `[:75]` slice

Result: the 75-pair slot always fills with real crypto. No tokenized stocks reach subscribers.

### Open items (priority order)

1. **Google Play approval** — awaiting email (≤7 days). Complete store listing / data-safety while waiting.
2. **Scoring-model rebuild** — still blocked on data accumulation in the Ops score-band view.
3. **PR #594 (regime-aware exit)** — owner sign-off required. Do not auto-merge. Touches position FSM / regime-per-exit doctrine (§3.2b).
4. **Dark-flag shadow telemetry** — read `[SHADOW]` counts before enabling TRENDING_PRETP_SUPPRESSED:
   ```bash
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] TRENDING_PRETP_SUPPRESSED"
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] PRETP_FULLGRAB_ON_CANCEL"
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] INVALIDATION_BTC_CORRELATION"
   ```

---

## Session 20b checkpoint 2026-06-06 — universe cleanup + dark-flag measurability

Continuation of session 20. Two follow-ups from the list below cleared, plus
the companion lumin-app production-UI pass.

### What shipped this session (3 PRs merged)

| PR | Repo | What | Live effect |
|---|---|---|---|
| [#596](https://github.com/mkmk749278/360-v2/pull/596) | 360-v2 | Tokenized-stock blacklist — AVGOUSDT/QQQUSDT/SKHYNIXUSDT/DRAMUSDT added to `SCAN_SYMBOL_BLACKLIST` | **Live on merge.** Those 4 pairs no longer scanned. |
| [#597](https://github.com/mkmk749278/360-v2/pull/597) | 360-v2 | Shadow telemetry for the 3 dark exit flags — logs `[SHADOW]` lines when a flag *would* fire while off | **Live on merge** (log-only, trade-neutral). `DARK_FLAG_SHADOW_TELEMETRY=true` default. |
| [#92](https://github.com/mkmk749278/lumin-app/pull/92) | lumin-app | Production UI: paper-first journey, removed engine-internal "75 pairs" copy, wired Telegram subscribe deep link, prominent paper-reset button | Merged. |

**#596 evidence (verified, not assumed):** pulled `origin/monitor-logs`
`signals_last100.json` + `dispatch_log.json` — all 4 symbols were actively
firing to the paid channel (AVGO 8×, QQQ 6×, SKHYNIX 3×, DRAM 1× of last
100), quotes track equity prices ($55–$1366), near-exclusively SHORT. Class-C
misfit per `docs/SYMBOL_CLASS_RESEARCH_2026_05_23.md`.

**#597 design:** flag-independent predicates shared by the real apply-funcs
and the shadow path (count can't drift from the gate); BTC shadow eval only on
the adverse-excursion path, TTL-cached, skipped entirely when master flag off.
49 tests pass.

### Now measurable from prod logs (before flipping the real flags)

```bash
# Count how often each dark flag WOULD have fired in recent logs:
docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] TRENDING_PRETP_SUPPRESSED"
docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] PRETP_FULLGRAB_ON_CANCEL"
docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] INVALIDATION_BTC_CORRELATION"
```

Read these counts before enabling `TRENDING_PRETP_SUPPRESSED` (the first flag
in the activation sequence below) so the blast radius is known in advance.

### Open follow-up from #596 (owner call)

Research doc also lists older tokenized stocks `CRCL/MU/INTC/CL/EWY` (already
100% QUIET-blocked). Not added — couldn't re-verify them in the current
100-signal window. Fold into the blacklist as a complete sweep, or leave them?

---

## Session 20 checkpoint 2026-06-06 — regime-aware exit (TRENDING runner fix)

### Research finding (drove the session)

Binance realized P&L analysis of 107 closed positions proved the profit/loss split is almost entirely explained by HOW LONG a position runs:

| Hold duration | Count | Net P&L | Win rate |
|---|---|---|---|
| > 40 minutes | 9 | **+$1.049** | 67% |
| < 40 minutes | 98 | **-$0.492** | 39% |

Pearson r(hold_minutes, PnL) = **+0.379**. The top-4 realized winners (NEAR +$0.348, NEAR +$0.291, WIF +$0.213, XPLV2 +$0.183) ran 47–68 minutes. The signal book had already PROFIT_LOCKEd those signals at 2–6 min while the Binance bracket kept running.

**Root cause split:**
- RANGING/QUIET markets: pre-TP + tight trailing-kill work correctly — contain chop losses, bank small wins
- TRENDING markets: the same mechanisms cut the exact positions that generate all profit. Pre-TP banks 50% at +0.35%; trailing-kill at 50% MFE retrace fires on normal continuation pauses (pullbacks routinely retrace 50-65% of a trend leg without reversing)

### What shipped this session (1 PR, owner sign-off required)

| PR | Repo | What | Flag (default) |
|---|---|---|---|
| [#594](https://github.com/mkmk749278/360-v2/pull/594) | 360-v2 | Regime-aware exit: suppress pre-TP + widen trailing-kill in TRENDING | see below |

**PR #594 — owner sign-off required.** Do not auto-merge. Touches position FSM / regime-per-exit doctrine (§3.2b).

### New env flags — activation when ready

| Flag | Default | Effect when `true` |
|---|---|---|
| `TRENDING_PRETP_SUPPRESSED` | `false` | Zero grab fraction for TRENDING_UP/DOWN signals → full position rides the trend |
| `INVALIDATION_TRAILING_RETRACE_REGIME_AWARE` | `false` | TRENDING signals use wider retrace threshold (default 0.70 vs 0.50 baseline) |
| `INVALIDATION_TRAILING_RETRACE_PCT_TRENDING` | `0.70` | Override the TRENDING retrace threshold (tune after observing) |

**Recommended activation sequence:**
1. Merge PR #594 (owner sign-off)
2. Enable `TRENDING_PRETP_SUPPRESSED=true` first — measurable via whether TRENDING signals run longer on Binance
3. After a week of data, enable `INVALIDATION_TRAILING_RETRACE_REGIME_AWARE=true`
4. Compare hold-time distribution + net P&L against session 20 baseline

### Also confirmed this session

- `PRE_TP_REGIME_ALLOWLIST = "QUIET,RANGING,VOLATILE"` (config) is enforced by `trade_monitor.py` for the signal book, but the **server-side FSM dispatch path** (`resolve_pretp_allowlists_uid`) returns allow-all by default when no user DB setting exists — TRENDING regime signals WERE getting pre-TP fired via the FSM. PR #594 fixes this at the dispatch level.

### Open follow-ups (carry-forward from session 19)

1. **Scoring-model rebuild** — blocked on data accumulation in the new Ops score-band view
2. ~~**Tokenized stock exclusion**~~ — ✅ **DONE** in PR #596 (session 20b). AVGOUSDT/QQQUSDT/SKHYNIXUSDT/DRAMUSDT added to `SCAN_SYMBOL_BLACKLIST`.
3. ~~**Shadow telemetry for dark flags**~~ — ✅ **DONE** in PR #597 (session 20b). `DARK_FLAG_SHADOW_TELEMETRY=true` default; `[SHADOW]` lines now in prod logs.

---

## Session 19 checkpoint 2026-06-05 — scoring research + BTC-in-invalidation + CANCEL-path fee fix

### Research finding (drove the whole session)

Owner supplied a 107-signal Ops report pairing **confidence score with outcome**. Decisive result: **Pearson r(confidence, PnL) = −0.027** — the confidence score has **no predictive power** over outcome. Raising the score threshold only cuts volume, it does **not** improve quality (the "trade 80+ only" idea = 4 signals, still net-negative). The real discriminators are **setup identity** (FAILED_AUCTION_RECLAIM / FUNDING positive; SR_FLIP_RETEST / LSR / BREAKDOWN negative) and **exit geometry**, not the score. Owner direction: do **not** pause setups — research paths, fix structurally, consider BTC correlation.

### What shipped this session (3 PRs merged)

| PR | Repo | What | Flag (default) |
|---|---|---|---|
| #591 | 360-v2 | BTC correlation in the **invalidation** system — tightens adverse-excursion exit when BTC 1H+4H oppose an open position | `INVALIDATION_BTC_CORRELATION_ENABLED` (false) |
| #592 | 360-v2 | **Full-grab pre-TP on CANCEL-bound regimes** — closes full position at the pre-TP LIMIT instead of partial+market-close (2 maker fees not 3, no residual slippage) | `PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED` (false) |
| #11 | 360ce-ops | Performance page: **score-band table + live Pearson r(confidence, PnL)**; fixed `PROFIT_LOCKED` not counted as a win | — (read-only) |

**All three engine changes ship DARK** — merges were behavior-neutral. Nothing changes live until the flags are flipped on the VPS.

### New env flags — how to A/B them on the VPS

| Flag | Effect when `true` | Companion tunables |
|---|---|---|
| `INVALIDATION_BTC_CORRELATION_ENABLED` | Open position that is losing **and** fighting BTC's 1H+4H trend exits earlier (adverse fraction × mult). Tape-driven setups exempt; fail-open on missing BTC data. | `INVALIDATION_BTC_ADVERSE_FRACTION_MULT` (0.70), `INVALIDATION_BTC_DIRECTION_CACHE_TTL_SEC` (60) |
| `PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED` | RANGING/QUIET-entry pre-TP closes 100% at the LIMIT (fee win, ~76% of cycles). Identical exit, 1 fewer fee. | — |

Validate enabling either against the truth report's PROTECTIVE/PREMATURE classifier + the new Ops score-band view.

### Open follow-ups (next session)

1. **Scoring-model rebuild** — "each score point should filter." Blocked on data: let the new Ops score-band view + per-setup outcomes accumulate (~days), then rebuild scoring on the components that actually discriminate (MTF/SMC look strongest; needs confirmation from real per-component outcome data — do **not** rebuild blind).
2. **SRFLIP/LSR geometry** — the small-win/big-loss asymmetry is the core bleed; the CANCEL fee fix (#592) trims fees but does not flip profitability. Investigate SL placement vs known liquidity clusters + pre-TP threshold sizing.
3. **Settings reset to defaults** — one-time VPS SQLite/API op when owner wants a clean baseline (pre-TP on, grab 0.50, threshold 0.35% ATR-adaptive, invalidation `tight`).
4. **Shadow telemetry for #591/#592** — optional: log when the dark overlays *would* fire so impact is measurable before flipping the flags live.

---

## Session 18 checkpoint 2026-06-04 — monitoring agent live + scan latency fixed (64s → ~3s) + Positions tab fixes

### What shipped this session (8 PRs merged to `main`)

| PR | Repo | What | Type |
|---|---|---|---|
| #583 | 360-v2 | `/internal/diag/tasks` endpoint (owner-tier) | feat, auto-merged |
| #584 | 360-v2 | Engine task census published to Redis (D2 re-enable) | feat, auto-merged |
| #585 | 360-v2 | Signing-client 16 MiB socket read buffer (reconciler overflow fix) | fix, auto-merged |
| #586 | 360-v2 | Per-stage scan timing instrumentation | feat, auto-merged |
| #587 | 360-v2 | SMC result cache + indicator fingerprint (insufficient — see #588) | fix, auto-merged |
| #588 | 360-v2 | Per-timeframe indicator caching (the real scan-latency fix) | fix, auto-merged |
| #589 | 360-v2 | `monitor_running` from task census in isolated mode (false-negative fix) | fix, auto-merged |
| #590 | 360-v2 | Positions X-ray populated in isolated mode via engine-published diag | fix, auto-merged |
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

### Positions tab — two isolated-mode false-negatives (#589, #590), FIXED

Both surfaced from owner screenshots of the dashboard Positions tab. Root cause in both
cases: the isolated `api` container serves from `RedisEngineFacade`, which lacks the live
engine objects the single-process build assumes are present.

1. **`monitor_running: NO` false-negative (#589).** The diag derived liveness from
   `getattr(engine, "monitor", None)._running`. The facade has no `.monitor` object, so it
   always read `None` → "NO" — even though the Redis task census showed `trade_monitor
   ALIVE: True`. Fix: when no `.monitor` object exists, derive `monitor_running` from the
   published task census (`get_background_task_census()` → any name containing
   `trade_monitor`). Single-process path unchanged.

2. **Blank/zero Positions X-ray rows (#590).** `build_positions_diag` needs live
   `router.active_signals` (full signal geometry: SL/TP, entry) AND `data_store` candle
   wicks to compute the SL-breach / candle-age columns. In isolated mode the facade only
   carries `_MockSignal` stubs (signal_id + timestamps) and `data_store is None`, so active
   positions rendered as blank-symbol, all-0.0 rows. Fix: the engine computes the diag
   itself (it has the real objects) and publishes the rendered rows to a new Redis key
   `snapshot:positions_diag` (TTL 60s) via `SnapshotWriter._write_positions_diag`; the API
   handler serves `engine.published_positions_diag()` when present, falling back to a live
   build in single-process mode. Mirrors the task-census pattern from #584.

   Files: `src/api/snapshot_store.py` (key + TTL), `src/api/snapshot_writer.py` (writer),
   `src/api/redis_engine.py` (`published_positions_diag()` + refresh), `src/api/server.py`
   (handler). 444 API tests green.

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
2. **Verify Positions X-ray post-#590 deploy** — confirm the Positions tab renders active
   signals with real symbol / SL / TP / candle-wick columns (not blank-0.0 rows), and
   `monitor_running: YES`. `snapshot:positions_diag` should be present in
   `redis-cli KEYS "snapshot:*"`; the same code deploy also applies
   `SCAN_STAGE_TIMING_ENABLED=false`.
3. **D1 NakedPositionDetector upgrade** — currently geometry-only (`stop_loss≤0`).
   Real naked-position detection (Binance stop order not placed) requires engine to
   publish `sl_order_id` per position in the Redis snapshot. Design needed.
4. **Verify regime-per-exit live** (PR #578) — `place_trailing_stop_market`/`trail_sl`
   in engine logs on TRENDING-aligned exits; `entry_regime`/`atr_value_at_entry`
   non-empty on dispatched positions; clean RANGING/QUIET market-closes.
5. **Verify funding-exit watcher live** (PR #581) — grep `funding_exit_watcher: exiting`;
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
