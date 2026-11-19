# Hourly AI analyst: build spec (2026-11-19)

Owner decisions (2026-11-19):
- Signals move from reactive bar-close triggers to the disciplined-analyst process:
  context first, levels marked in advance, pre-entry setups.
- Claude does the analysis, through the owner's **Claude subscription** (Pro),
  not the API, as **scheduled Claude Code sessions**.
- The engine executes deterministically.
- The connection is an **MCP server in ops** plus a **machine access tier** (read +
  `submit_plan` only). Both were approved.

Evidence base:
- Claude deep research: `docs/research/AI_ANALYST_DEEP_RESEARCH_2026_11_19.md`, published as the
  "Crypto Setup Analyst Research" artifact.
- Gemini Deep Research: "Designing an Evidence-Based Hourly AI Setup Analyst for Binance
  USD-M Perpetual Futures" (27 pp, owner upload).
- The comparison of the two is in this session's notes and summarised in §2.

## 1. What the analyst is, and is not

The analyst plans; the engine executes. The analyst never emits a price, never sizes,
never places, moves or cancels an order. It reads pre-computed, timestamped summaries.
It picks levels **by id** from an engine-built menu and returns a plan in a fixed schema.
The engine validates the plan, then measures it.

Both reports agree that LLMs picking direction from raw prices lose (Alpha Arena S1,
FINSABER, Profit Mirage, LiveTradeBench, the 2026 ACM survey). The realistic edge is
**restraint and consistency**: trade fewer pairs, at levels with a structural reason,
only in regimes where the archetype has paid, and say "no setup" most hours.

The refutation condition is written down before any data exists:

> If a **fixed rule on the same level menu** matches the analyst net of fees, the model
> added nothing and we ship the rule.

## 2. Evidence carried into the design

| Input | Grade | Role |
|---|---|---|
| Fees vs gross expectancy | strong | Cost floor on every setup |
| Fat right tail (our top 1% = ~80% of gross) | strong | No rule may cut runners; report every arm with and without its top 1% |
| Limit-order adverse selection | strong | Unfilled setups scored at the market-entry outcome; breakout arm kept |
| BTC higher-timeframe regime | moderate–strong | Gate on alt longs |
| Levels (HTF swings, PDH/PDL, PWH/PWL, round numbers) | moderate | Stops just beyond, take-profits just before (Osler) |
| Volume profile / AVWAP | moderate rationale, weak alpha | Confluence only |
| Token unlocks (team/investor cliff) | moderate | Long veto 30d before → 14d after |
| New listings, monitoring tags, hacks | moderate | Exclusions |
| Macro releases | moderate (volatility) | Stand aside ±30 min |
| Funding / OI | moderate as crowding context | Context, never a trigger |
| OI quadrants, long/short ratio, liquidation heatmaps, hourly OBI, ICT/SMC | folklore | Not used |

**Checked against our own data, and refuted.** Gemini attributes our entry drift to the
first 10 seconds after a 15-minute boundary. In our data:
- only **13 of 3,155** stamped entries fall in that window;
- drift is **~0 in the first minute** of the bar and **largest late in the bar** (longs:
  median 0.135%, mean 0.34% at 7.5–15 minutes).

The drift is a stamp-to-action delay. A planned entry price fixes it; delaying orders
past the boundary does not.

**Adopted from Gemini as hypotheses, not facts:**
- the 0–100 level score (weights are invented; v1 config);
- two-tranche entries (40% shallow / 60% deep);
- the altcoin breadth gate;
- risk-based sizing (owner decision; money path).

**Not adopted:**
- "delete break-even, take 50% at +1R" goes to the existing held-to-stop arm instead;
- "minimum R:R 1.8" — the Aug-01 TPE lesson says measure per path first;
- "spot-vs-perp CVD as a core gate" — its citation does not test this.

## 3. Components and build order

Each step ships as its own PR. Nothing reaches a user or an order until the last step,
which needs owner sign-off.

### Step 1: analyst read model (engine). This PR.

`src/analyst_snapshot.py`. Pure assembly over state the engine already holds:
- data store candles, 1h–1w;
- `LevelBook`;
- both `VolumeProfileStore`s;
- the unlock-short ledger's calendar.

It makes no new network or Firestore reads.

- **Level menu.** Each candidate comes from:
  - `LevelBook` levels, which carry timeframe, touches, round-number flag and last test;
  - prior day / week high and low, from the last **closed** 1d / 1w bar;
  - volume-profile POC, VAH and VAL, micro and macro.

  Each level gets a stable id (`kind@price`), a side, distance in % and in 1h-ATR, and a
  0–100 score with the parts shown. The top levels above and below price are returned.
- **Pair snapshot**:
  - price;
  - bar freshness per timeframe;
  - ATR (1h / 4h, absolute and %);
  - trend score per timeframe (the BTC-state scorer applied to the pair);
  - 24h / 7d change, and 7d relative strength vs BTC;
  - value-area position;
  - unlocks inside the veto window;
  - the level menu.
- **Market context**:
  - BTC state and per-timeframe trend, BTC 24h / 7d change and ATR%;
  - 7-day **altcoin breadth** (share of the universe beating BTC, with n and missing
    counted);
  - UTC session;
  - macro calendar **readability**. The macro event list is not wired (`macro_blackout`
    receives an empty list), so it reports `not_available`. It never reports "no events".
- **Watchlist**: pairs within 1.5 × 1h-ATR of a level scoring ≥ 60, best first, capped.

Exposed as diagnostic catalog reads: `read.analyst_market`, `read.analyst_pair`
(symbol), `read.analyst_watchlist`. They are usable today from the ops console (guest
included) and become the MCP tools' backend in step 3.

Every field that could not be computed says why. Unknown is never a value.

### Step 2: derivatives recorder (engine, off the money path)

Binance keeps only 30 days of open interest, long/short and taker ratio history, so we
record our own:
- hourly OI (coin-denominated), funding, premium and taker ratio per universe pair;
- stored to SQLite;
- **default OFF** per the background-loop rule;
- request weight stated in the PR body;
- armed by the owner after one watched cycle.

### Step 3: plan endpoint, validator, ledger (engine) + MCP server and machine token (ops)

- **Engine:** `submit_plan` takes a JSON plan with:
  - bias, plus a setups list;
  - each setup: symbol, archetype, side, entry level ids (one or two tranches), stop
    level id, target level ids, invalidation, expiry.

  The validator checks, in order:
  - crypto-perp admission;
  - every level id exists in the **current** menu;
  - stop beyond structure plus an ATR buffer, within [0.8, 2.5] × 1h-ATR;
  - the cost floor;
  - setup caps;
  - unlock / listing / macro vetoes.

  A rejection carries its reason. The ledger is SQLite or Redis, never Firestore.
- **Ops:** MCP tools for market context, watchlist, pair snapshot, book state, calendar,
  last plan / notes, plan outcomes, and `submit_plan`. Every call is audited; the token is
  scoped and revocable on Control → Access.

### Step 4: dark measurement

Forward walk of every plan on the money-path clock. Arms on the same opportunities:
- the analyst;
- the fixed rule on the same menu;
- the analyst's pick at market at the stamp;
- two-tranche entry;
- the existing signals;
- no trade.

Unfilled setups are scored at their market outcome. Every arm is reported with and
without its top 1%. The ops page and liveness probe ("hourly plan missed") ship with it.

### Step 5: scheduled sessions on

Hourly Claude Code scheduled task. Usage is logged for the first week against the Pro
limit. A missed run means the last plan expires and no new setups arm; that is the safe
direction.

### Step 6: limit-order executor

Owner sign-off on step 4 results. Default OFF.

## 4. Sample size

Per-trade SD is ~2.5–2.9% (our book). Detecting +0.2% per trade at 80% power takes:
- ~1,200–1,600 paired setups;
- ~2,500–3,200 per arm unpaired;
- more if the gain comes from the tail.

Use day-clustered bootstrap intervals. Read results in months, not weeks.
