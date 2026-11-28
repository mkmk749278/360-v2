# Analyst desk plan — 2026-11-28

The owner asked for the hourly analyst to behave like a desk trader, not a
rule-follower. Four asks:
- read charts properly, as a person would;
- watch a level and enter only when the situation on arrival is right
  (not limit-and-forget);
- carry full market and per-coin data;
- carry the experience of each coin from one hour to the next.

The plan merges the owner's direction, our own reading of the ledger, and a
second opinion from Gemini. Each Gemini claim was checked against the ledger
first; the verdicts are in the last section. It ships in phases, each its own
PR.

## Where it stands (ledger, 2026-11-28, 9 days)

| Arm | n | Avg per setup posted | Note |
|---|---|---|---|
| analyst (limit at first entry) | 317 | −0.21% | fills average −0.34%; 61% fill rate |
| market at submit | 330 | −0.03% | taker fees modelled; slippage not modelled |
| fixed_rule | 336 | +0.03% | one day (11-26, +66.5%) carries it |

- **By setup type** (`by_setup`, #1109): in the two short continuation types the
  analyst loses while market entry on the same setups does not:

  | Setup | n | Analyst | Market |
  |---|---|---|---|
  | breakout_retest short | 78 | −0.48% | +0.08% |
  | trend_pullback short | 31 | −0.60% | +0.09% |

  Likewise risk_off shorts: −0.35% against +0.41% (n 84). The short limits
  fill when price comes back against the trade. That is a fault in how it
  enters, and it is what limit-and-forget produces.
- **Calibration:** Brier 0.213 against a base rate of 0.205. It forecasts stops
  at 0.44 against 0.57 observed.
- **How it works today:** each run takes ~2 minutes (12:36 → 12:38 on
  11-28) with ~20 tool calls, reads numbers only, and keeps no memory between
  runs.
- **One market phase** (BTC 81k → 59k), so no cell is a rule.

## Who reads the analyst's output — this is not fully dark

`src/desk.py` publishes the latest plan's bias and notes, the accepted setups
and the walk record as `snapshot:desk`, read by `GET /api/desk` for the Lumin
2.0 Desk. So every phase below that changes what a setup *is* (a `size: 0`
pass, a `watching` or `cancelled` state, a new entry type) is a cross-repo
contract with `lumin-app`. Each phase states what the Desk shows, and none
ships a new state the app would render under the wrong caption:

- **`size: 0` setups are not desk positions.** The Desk keeps showing only
  `size > 0` setups as setups. A size-0 row is published as `passed`, with its
  own count.
- **New states** (`watching`, `in_zone`, `cancelled`) are published under new
  keys. They are added to the app's label table in the same paired PR. Until
  then the Desk maps them to the existing `pending`, never to a filled state.
- Nothing in this plan reaches an order, a signal or the money path. The walk
  stays a measurement.

## Can the model read a chart the way a person does?

Yes. It is multimodal and reads a rendered candlestick image much as a trader
does: swings, trend, ranges, wicks, compression, failed breaks. Today it never
gets one. The `chart` tool returns arrays of numbers, and a model reading 120
rows of OHLC is reading a spreadsheet, not a chart.

Image and numbers do different jobs:
- **Image** → shape and context (where we are in the move, what the structure
  looks like).
- **Numbers** → exact prices for entries, stops and targets. Vision is
  imprecise on exact levels.

Phase 1 gives it both.

## Phases

### Phase 1 — Data, memory and sight

**1a. `chart_image(symbol, tf, bars)`**
- A rendered candlestick PNG (mplfinance is already a dependency) with volume.
  It optionally overlays the levels the analyst marked earlier and the
  engine's level menu, plus the price axis and a timestamp of the last closed
  bar.
- Rendered in the engine container, **off the event loop** (`to_thread`),
  bounded size, no network.
- The tool returns the image; the analyst decodes it to a file and views it.

**1b. `pair_flow(symbol)`** — market data the engine already collects and the
analyst cannot see. Each field carries its coverage and freshness; an absent
feed is `null` with a reason, never a zero:
- **liquidations** from `order_flow` (forceOrder): recent long and short
  liquidation notional, last burst;
- **order-flow delta:** CVD slope, and footprint delta at the nearest marked
  levels (footprint keeps ~120 1m bars);
- **order-book depth and imbalance** from `depth_book`. It covers at most
  `DEPTH_MAX_SYMBOLS` (40) symbols, so `covered: false` elsewhere;
- **volume profile:** POC, VAH, VAL, and the macro profile;
- **derivatives:** OI, funding and premium history.

**1c. `pair_profile(symbol)`** — engine-computed, cached ~6h, built on the
call (no new background loop):
- BTC beta and correlation (1h/4h), split on BTC up and down days;
- whether the coin has decoupled from BTC right now; 7d relative strength;
- volatility percentile, typical daily range, wick-to-body ratio;
- 30-day trend persistence vs mean reversion, and breakout follow-through;
- behaviour during BTC trends vs BTC ranges;
- funding z-score, OI change, liquidity, unlocks.

Dropped (Gemini, agreed): session and weekday patterns (~21 days of 1h is too
thin) and per-coin win/loss history in the prompt. The history is stamped,
not shown.

**1d. Pair book — per-coin memory.** For each coin the analyst touches:
- **Engine-recorded facts:** every level the analyst marked (entry, stop,
  target, invalidation) and what price did there. The walk already steps
  every 5m bar, so it classifies each level as `respected`, `broke`,
  `swept_reclaimed` or `untested` with a timestamp. It also records the
  coin's setups and how each ended, with n.
- **Analyst notes:** an optional per-symbol `pair_notes` block in
  `submit_plan` (thesis, key levels, what it is waiting for, ≤300 chars). It
  is stored labelled as hypothesis, and the engine appends what happened
  next.
- **`pair_book(symbol)`** returns both, newest first, bounded.

`submit_plan` stays the only writer, so the ops tool table keeps its one
write tool.

**1e. Stamps.** At submit, each setup records the profile values (beta,
decoupled, wick ratio, persistence) and which reads were used (`saw_image`,
`read_flow`, `read_book`). The split can then later say whether any of them
helped.

**Ops:** four new read tools in `app/routes/mcp.py`, each forwarding one
catalog key.

**Cost:** local reads only; no Firestore, Redis or exchange calls. At most ~20
renders an hour, each a few hundred ms in a thread. The pair book is one more
table in the existing analyst SQLite ledger, bounded per symbol.

### Phase 2 — Watch, confirm, then enter

**New `entry_type: "watch"`**, beside `"immediate"` and `"pullback"`. A watch
carries structured fields, not prose:
- **`zone`** — `[low, high]`.
- **`confirm`** — a closed vocabulary:
  - `close_back_inside {tf}` (tagged the zone, then a close back on our side);
  - `rejection_wick {tf, min_wick_ratio}`;
  - `btc_not_beyond {price, dir}`;
  - `reclaim {tf, level}`.
- **`cancel`** — likewise closed:
  - `close_through {tf, level}`;
  - `btc_beyond {price, dir}`;
  - `forecast_invalidated`;
  - `expiry_hours`.

A condition outside the vocabulary is a validator reject, never a guess.

**The engine watches.** The walk evaluates every armed watch on each closed 5m
or 15m bar. A watch moves `watching → in_zone → entered` (at market on the
confirming bar's close, taker fee plus slippage) or `→ cancelled`, with the
reason. Like every arm it uses only bars that have closed, so there is no
look-ahead.

**Hourly review.** `plan_outcomes` carries `watches` (armed, in zone, entered,
cancelled, with reasons). The analyst keeps, moves or kills each one by
submitting a replacement watch, or a `cancel_watch` id in the next plan.

**Measured as arm `watch`** on the same setups as today's `analyst` limit arm.
The question is whether entering on confirmation at arrival beats a resting
limit, on identical setups.

**`immediate`** is walked as a market entry at submit, taker in.

*As built (2026-11-28):* slippage is not modelled for any arm. Charging it to
`immediate` and `watch` alone would make them read worse than the market and
`zone_limit` controls for a reason that is not real; it belongs in the cost
model for every taker fill at once, as its own change. The confirm vocabulary
shipped as `close_beyond_zone` (a close on the trade's side of the zone, which
covers both a rejection back out and a break through) and `rejection_wick`;
`btc_not_beyond` is a cancel (`btc_beyond`) rather than a confirm, since both
end the watch. `forecast_invalidated` waits for the Phase 3 forecast.

**Order-flow confirmation** (footprint delta in the zone) is **Phase 2b**. The
dark walk evaluates on candles, and delta is live-only, so a delta condition
can only be evaluated forward, as bars arrive, and stamped then.

**Desk:** `watching` / `in_zone` / `cancelled` are published per the contract
section above.

### Phase 3 — Judgement scoring

- **`size ∈ {0, 0.5, 1, 1.5, 2}`** on every setup. `size: 0` means the desk
  would pass and the setup is logged only. The walk reports three results:
  - a size-weighted active book;
  - the unsized book over all setups;
  - the passed setups (`size == 0`).

  The analyst's selectivity then shows as active against passed, on the same
  days.
- **Beta-weighted side budget** in the prompt, reported in `active_book` as
  units × beta.
- **Plan `forecast`:** `btc_4h` (±0.7%) and `btc_12h` (±1.2%), each
  `up | down | range` with p and an invalidation price. Scored against BTC's
  close, with Brier against the base rate. The bands are Gemini's choice, not
  measured, and are stamped on each row so a later change is a new
  population.
- **Day-clustered statistics:** every headline also published as a daily
  series with a block-bootstrap 95% CI. Setups on one side in one hour are one
  bet, not many.
- **Stop diagnostics:**
  - the share of stops hit on an ambiguous 5m bar (the walk counts the stop
    first);
  - post-stop MFE at 6h and 12h (did it go on to target?);
  - results by `entry_dist_atr` bucket.
- **The 11-26 anomaly:** fixed_rule +66.5% against market −26.6% on the same
  symbols and sides. Read row by row before anything here is judged; it is
  either a real clue (wider stops, wick fills) or a walk defect.

### Phase 4 — Exits

- **`runner_24h` arm:** half at TP1, half trailed behind the last confirmed 1h
  swing, 24h cap, original stop with no break-even. The trail rule is stamped
  as a parameter.
- **`btc_invalidated_exit` arm:** exit at market when BTC closes beyond the
  plan's own `btc_4h.invalidation`.
- Both are on the same fills as `analyst` and `ladder`, and none is blended.

### Phase 5 — Prompt v3.2 and the judging window

- **v3.2** = v3.1 (Gemini-merged) plus the Phase 1–4 tools:
  - read the pair book first; view the chart image, then use numbers for
    levels;
  - read `pair_flow` at the level;
  - prefer `watch` over a resting limit;
  - size with the beta budget; forecast 4h/12h.
- **Applied to the scheduled task only after the phases it relies on have
  deployed.** A prompt field the validator drops is a scaffold.
- **Judged on ≥ 21 days spanning at least two BTC regimes**, on day-clustered
  CIs, never on a 3-day cell. `prompt_version` is stamped, so v2.5 and v3.2
  rows never pool.

## Order and gates

| Phase | Depends on | Touches the Desk | Owner sign-off |
|---|---|---|---|
| 1 Data, memory, sight | — | no | no (dark reads) |
| 2 Watch / immediate | 1 (flow for 2b) | yes: new states, paired lumin-app PR | no (dark arm) |
| 3 Judgement scoring | — | yes: `passed` count | no |
| 4 Exits | — | no | no (dark arms) |
| 5 Prompt v3.2 | 1–3 deployed | yes: brief text | **yes** — changes what the analyst does every hour |

Phases 1, 3 and 4 are independent and can run in parallel. Phase 2 needs 1's
level classifier.

**Phase 1 merge order:** engine endpoints first, then the ops tool table, then
the prompt.

## Gemini second opinion — verdicts

| Claim | Check against the ledger | Verdict |
|---|---|---|
| Cadence 11-25→27 lost on market entry too (−80.1%) | Sums match `by_day` | **True.** Fewer active setups (0–2 / 0–1) |
| Filled stop rate 61% | 61% is the 46-row three-outcome slice; across all filled setups it is 48% | **Overstated.** The under-forecast of stops stands |
| Market arm's 0.07% fee understates cost | Taker fees already modelled; slippage is not | **Partly.** Slippage added for `immediate` / `watch` |
| `n ≥ 50` over ≥ 7 days before acting on a cell | Agrees with the independence point | **Adopted** |
| 24h forecast vs a 12h trade | Correct | **Adopted:** `btc_12h` |
| `size: 0` keeps the record while sizing carries judgement | Owner's middle option | **Adopted** (Phase 3) |
| `entry_type` immediate / pullback | The 11-27 refinement doc proposed the same measurement | **Adopted, extended with `watch`** (Phase 2) |
| Slim profile, no session/weekday, no per-coin history in the prompt | Thin samples | **Adopted** |
| Spot vs perp CVD | No spot data in the engine | **Not now** |
| Liquidation bursts, lead/lag vs BTC | Liquidations exist in `order_flow` | **Adopted** in `pair_flow`; lead/lag later |
| Runner trail, BTC-invalidation exit | Not built | **Phase 4** |
| Inspect 11-26 | Confirmed anomaly | **Phase 3, first** |
| Equal-dollar-risk units | Live sizing is fixed-notional; changing it is a money-path owner decision | **Not adopted here.** The dark walk scores % × size |
