# The AI Trade Governor, v3 — where the AI actually belongs

**Status:** design of record for the whole program. Written 2026-09-04, from a
measurement of the recorded book rather than from an argument about it.
**Supersedes:** the *rollout* and *targeting* of `PLAN_AI_TRADE_GOVERNOR.md`
(v1, the fast lane) and `PLAN_AI_TRADE_GOVERNOR_V2.md` (v2, the deep lane).
Their **invariants and safety rules carry forward unchanged** — the menu key,
the two flags, the apply budgets, the panic ceiling, "never blocks a fill". What
changes is *what the model is pointed at*, and the order things get built.

**Owner's requirement, unchanged and restated here so the design is judged
against it** (2026-09-03 and again 2026-09-04): *"new signal out, you Claude
wake review that signal with your own analysis, adjust if anything needed, if
that not correct we do cancel — everything should go automatic."* And the
diagnosis he gave for why the engine cannot do it today: *"it can't keep in
memory what that coin actually is, how it reacts to news or BTC; the engine only
takes pivots and measures mathematically."*

Every fact below is labelled **[measured]** (computed in this session from the
recorded book), **[verified]** (read from this tree or the running system), or
**[inferred]**. An unlabelled inference reads exactly like a measurement.

---

## 0. Executive summary

The program has been aimed at the wrong half of the trade.

Measured on **1,580 delivered, closed signals over 90 days** (the engine's own
recorded book, exported from `/track-record`) **[measured]**:

1. **The book's entire profit is ten trades.** Net +88.21% at a fixed notional;
   the **top 10 trades of 1,580 contribute 105% of it**. Remove the top 5% and
   the book is **−398%**.
2. **Therefore the arm that is currently armed is the dangerous one.**
   `ADJUST_TP` may only move a target **nearer** (v1 §7). Applying that to this
   book — capping every winner at +2% — takes it from **+88% to −558%**.
   Even a generous +5% cap gives **−11%**.
3. **The asymmetry is enormous and points the other way.** A perfect veto that
   removed the worst 5% of trades would produce **+478%** — the same magnitude
   in the opposite direction. Exit management has negative headroom on this
   book; entry filtering has enormous headroom.
4. **Per-symbol lifetime memory does not predict.** Across 60 symbols with ≥8
   trades, the correlation between a symbol's first-half and second-half mean
   PnL is **−0.19**; symbols that were positive went on to average −0.189% and
   symbols that were negative went on to +0.109%. The dossier idea, in its
   "which coins are good" form, is **refuted**.
5. **Episode memory does survive, in one direction.** A signal whose previous
   trade *on the same symbol within 6 hours* lost averages **−0.309%** against a
   +0.026% baseline, and it stays negative after removing the top 10 trades
   (−0.343%) and the top 5% (−0.642%). The winning side of the same split is
   weaker and does not survive the top-5% cut.

So the answer to *"where does the AI go"* is: **at emission, not at exit** — and
the first things to ship there are not models at all.

---

## 1. The measurement

**Source.** `/track-record/trades.csv?window=90d`, the ops export of
`signal_performance.json` — every signal the router confirmed, tracked forward
by `trade_monitor`, written at its terminal transition. Recorded, not
reconstructed. 1,580 rows, 2026-06-25 → 2026-09-04, fixed 100 USDT notional,
0.07% round trip charged to every row **[verified, method is the page's own]**.

**Headline [measured]:**

| | |
|---|---|
| Trades | 1,580 |
| Net | **+88.21%** (of one notional) |
| Average | +0.056% / trade |
| Median | **−0.070%** / trade |
| Win rate | **36.3%** (573W / 1,007L) |
| Average win | +2.620% |
| Average loss | −1.403% |

The median trade loses. The mean is positive. That gap *is* the strategy.

**By outcome [measured]:**

| Outcome | n | total | avg |
|---|---|---|---|
| `PROFIT_LOCKED` | 284 | **+1055.47%** | +3.716% |
| `TP1_HIT` | 123 | +287.54% | +2.338% |
| `EXPIRED` | 291 | +74.19% | +0.255% |
| `FULL_TP_HIT` | 14 | +24.61% | +1.758% |
| `BREAKEVEN_EXIT` | 235 | −16.45% | −0.070% |
| `SL_HIT` | **628** | **−1336.79%** | −2.129% |

**Trend [measured]:** the first 790 trades (to 2026-07-18) ran **−29.99%**; the
latest 790 ran **+118.20%**. The 30-day window is +172.52% and the most recent
seven days are **−21.96%**. The book is improving over the quarter and has given
back over the last week. Neither figure is quoted here as a verdict.

---

## 2. Finding 1 — the edge is a tail, and that decides everything else

**[measured]**

| | net contribution | share of the book's +88.21% |
|---|---|---|
| Top 5 trades (0.3%) | +50.7% | 57% |
| Top 10 trades (0.6%) | +92.5% | **105%** |
| Top 20 trades (1.3%) | +169.1% | 192% |
| Top 50 trades (3.2%) | +348.3% | 395% |
| Book minus its top 5% | **−398.3%** | — |

Ten trades of one thousand five hundred and eighty. Removing the single best
trade takes +88.21% to +75.6%.

Two consequences the rest of this document follows from:

- **Any mechanism that trims the right tail is negative-EV on this book by
  construction.** It does not need to be wrong often; it needs to be wrong once
  on the trade that was paying for the month.
- **A win-rate improvement is close to worthless here and a tail-preservation
  improvement is close to everything.** Optimising the 36.3% is optimising the
  part of the distribution that does not carry the money.

The top ten also show *how* the tail arrives **[measured]**: `BMTUSDT` appears
four times inside 12 hours (+9.41 / +8.66 / +8.63 / +8.46), all
`MOVER_TREND_PULLBACK`, all `PROFIT_LOCKED`. The tail is not scattered; it
comes in **episodes on one symbol during one move.** §5 returns to this.

---

## 3. Finding 2 — "adjust the target nearer" is measured negative, and it is the armed arm

v1 §7's invariant is that `ADJUST_TP` may move TP1 **nearer only** — widening a
target is "a new trade, not an adjustment". That invariant is correct as a
safety rule and it means the arm can only ever do one thing to this book.

Simulating it directly — cap every winner at +X% and leave every loser alone
**[measured]**:

| Cap winners at | Book becomes | Delta |
|---|---|---|
| +1.0% | −916.02% | −1004.23% |
| +2.0% | **−558.03%** | −646.24% |
| +3.0% | −283.29% | −371.50% |
| +5.0% | −10.90% | −99.11% |

**The one arm that is armed today (`AI_GOV_ARMS_ENABLED=tp`) is the one this
book cannot afford.** That is not a reason to panic — apply is OFF and no
verdict has ever been applied **[verified]** — but it is a reason not to arm it
on the current evidence, and it inverts the "ADJUST_TP is the fully decidable
arm, so activate it first" logic in v1 §11 and v2 §12 D4.

**Stated limits of this simulation, because they cut one way.** It assumes a
capped trade exits at the cap and that nothing else changes. It does **not**
model losers that would have touched +X% *before* reversing and so would have
been converted into small winners — the export carries no MFE column.

**P0 ran that proper version, and it confirms the direction while softening the
magnitude exactly as predicted.** Ops' Profit-tab simulator prices a flat target
from the engine's own recorded MFE/MAE, so it *does* count the rescued losers.
Over **562 closed signals, 30 days [measured]**:

| Exit | avg P/L | total |
|---|---|---|
| **the engine's real exits** | **+0.29%** | baseline |
| flat cap at +1% | −0.80% | −451.99% |
| flat cap at +1.5% | −0.63% | −351.40% |
| flat cap at +2% | −0.46% | −256.37% |
| flat cap at +3% | −0.15% | −86.98% |
| flat cap at +5% | +0.14% | +79.33% |

**No cap beats doing nothing at any threshold tested.** The stated refutation
condition — that MFE flips the sign — did not fire. `ADJUST_TP` is de-armed in
`config/__init__.py`, with this table in the constant's own comment.

**And P0 turned up something larger that this document must record.** The same
page reports the engine's real exits at **+86.03% against plain TP1-full's
+69.78% on the same 466 signals — the machinery is now +16.25 points AHEAD**
**[measured]**. `OWNER_BRIEF` §3.2's founding finding was the reverse (TP1-full
ahead by 19.14 points on 494 signals, Session 34). *That premise has flipped and
nobody had re-run it.* It does not rescue `ADJUST_TP` — the table above is on
the same window — because the engine's exits win by **letting winners run**
(`PROFIT_LOCKED`, +1055% of the book's +88%), which is the opposite of moving a
target nearer. What it does support is `HAND_TO_TRAIL`.

Beside it, the 17,709-entry exit bake-off already on `/exit-backtest`
**[verified]**: Parabolic SAR is the only method with a profit factor above 1
(**1.16**, +480.5% total) and it **survives drop-top-3** (PF 1.15) — engine
baseline 0.65, ATR-Chandelier 0.58, SuperTrend 0.71. Its own page's caveat
stands (synthetic klines-only entries, so trust the ranking not the absolute),
and it names the mechanism `HAND_TO_TRAIL` should hand to.

---

## 4. Finding 3 — the asymmetry, and what it says about where to point the model

The mirror of §3 **[measured]**:

| Perfect veto (uses the outcome — an upper bound nobody can reach) | Book becomes | Delta |
|---|---|---|
| Drop the worst 5% (79 trades) | +478.05% | **+389.84%** |
| Drop the worst 10% (158 trades) | +725.61% | +637.41% |
| Drop the worst 20% (316 trades) | +1123.21% | +1035.00% |

This is deliberately an unreachable bound: it is computed with knowledge of the
result. It is quoted for one purpose only — **the direction and the order of
magnitude of the headroom.** Exit management on this book is worth up to −646%;
entry filtering is worth up to +390%. They are not close, and they are not the
same sign.

`OWNER_BRIEF` §3.2 reached the same conclusion from the other end fifteen months
of sessions ago and it is worth quoting because it has been sitting there
unactioned: *"The exit logic, not the entries, was giving back the edge… the
residual gap is entry quality + fees, not the exit"* **[verified]**.

**So the AI's job is to decide whether a signal should be delivered at all, and
its default answer must be yes.**

---

## 5. Finding 4 — the owner's memory diagnosis, tested

The owner's argument is that the engine evaluates each coin with no memory of
what it is or how it behaves, and that this is why a reasoning model would beat
it. The first half is **correct and verified**; the second half splits into two
claims that measure very differently.

### 5.1 The engine really has no memory — verified

- `strategy_edge` — the store that actually routes — keys cells on
  `(strategy, context_key)` where context is session / phase / volatility /
  rotation. **Symbol appears nowhere in it** **[verified]**.
- One step of per-symbol memory exists: `entry_features._campaign_block` stamps
  `campaign_prev_won / prev_outcome / prev_pnl_pct / prev_age_h` (#998,
  2026-09-03). It is **observe-only, consumed by nothing** **[verified]** — and
  the liveness watchdog reports those two fields absent on *every* stamp of the
  `RANGE_FADE` path (#1010) **[verified]**.

### 5.2 "Which coins are good" — REFUTED

Across the 60 symbols with ≥8 trades (802 trades) **[measured]**:

- correlation between a symbol's first-half mean and its second-half mean:
  **−0.19**
- symbols positive in the first half → **−0.189%** in the second
- symbols negative in the first half → **+0.109%** in the second
- book baseline: +0.056%

A symbol's record over its lifetime does not predict its next trade; if
anything it mildly mean-reverts. **A dossier that ranks coins by how we have
done on them would actively mislead**, and it would have misled in exactly the
flattering direction — a machine for confident nonsense about coins. This
retracts the per-pair dossier as I proposed it earlier in this session.

### 5.3 "Is this coin in a paying episode right now" — SURVIVES, one-sided

Same data, keyed on the *previous trade on the same symbol* and the time since
it closed **[measured]**:

| | n | avg | total | vs baseline (+0.026%) |
|---|---|---|---|---|
| previous trade **won**, <6h ago | 191 | **+0.534%** | +101.97% | ×20 |
| previous trade **lost**, <6h ago | 254 | **−0.309%** | −78.50% | ×−12 |
| won, 6–48h | 100 | +0.227% | +22.67% | |
| lost, 6–48h | 236 | −0.044% | −10.35% | |
| won, >48h | 96 | −0.101% | −9.74% | |
| lost, >48h | 197 | +0.128% | +25.21% | |

The effect decays with elapsed time and inverts past 48 hours, which is the
shape an *episode* has and the shape noise does not.

**Then the test this repo's own rules demand — does it survive removing the
tail it might just be restating?** `HOT − COLD`, bootstrap 95% CI:

| Population | HOT − COLD | 95% CI |
|---|---|---|
| all 1,395 taggable trades | +0.843% | **[+0.335, +1.382]** |
| top 10 trades removed | +0.665% | **[+0.135, +1.175]** |
| top 5% removed | +0.397% | **[−0.053, +0.842]** |

**It survives removing the ten biggest trades and does not survive removing the
top 5%.** Concentration is real: the top three symbols are 56% of the HOT
bucket's total. So:

- the **COLD half is the robust half** — negative in every cut (−0.309 /
  −0.343 / −0.642) and worse than baseline in every cut. That is the
  **veto-shaped** half, and a veto is the direction §4 says has headroom.
- the **HOT half is suggestive and not established.** It is also the half that
  would tempt us to *act on winners*, which §2 and §3 say is where the danger
  is.

An in-sample count, labelled as such: skipping every COLD signal over the same
window takes the taggable book from +48.52% to +127.02%, dropping 254 of 1,395
trades **[measured, in-sample — this is the window that suggested the rule and
therefore cannot also test it]**.

### 5.4 What this does to the owner's diagnosis

He is right that the engine has no memory, right that it matters, and right
about the *mechanism* — but the memory that pays is **recency within a move**,
not **identity of a coin**. And the engine already stamps that memory and
consumes it nowhere.

It also revises what I concluded about BULLA earlier today. I said the fact that
would have saved my analysis was "this path has profit-locked +7.31/+5.59/+8.35
on this symbol". Under §5.2 that is not evidence about BULLA the asset; under
§5.3 it is evidence that BULLA was **inside a paying episode**, which is the
correct and much narrower reading.

---

## 6. Finding 5 — what the reviewer can and cannot see today

**[verified, read live 2026-09-04]**

- `fully_blind: 72 of 72`, `avg_unknown_frac: 1.0` — every verdict the governor
  has ever issued was made with **no order book and no CVD**. Cause is a stream
  budget (`DEPTH_MAX_SYMBOLS` / `AGGTRADE_MAX_SYMBOLS` = 40) against a
  mover-heavy book, not a fault. The engine's own watchdog has been paging on it
  for 47 audit cycles (#1010).
- **No structure reaches the model at all.** `grep` across all three
  `ai_governor*` modules returns nothing for Volume Profile, structure state,
  SMC or chart patterns — every one of which the engine computes on every scan.
  The Level Book reaches the *menu* (#1008) and nothing else.
- Two of four trigger rungs cannot fire while a symbol is unsubscribed:
  `flow_opposed` gates on `cvd_slope_aligned.readable`, and the
  `wall_ahead_of_tp` premise needs the book.
- 7 of 8 verdicts age out before the apply path reaches them; the monitor tick
  runs ~7–20s against a 10s bound, and **both** `ADJUST_SL` verdicts in the
  window were discarded (#1011 shipped the instrument that measured this).

So the model has been asked to beat a mathematical engine while being shown
strictly less than the engine sees. **That is the honest reading of the two
manual passes that scored 0-of-5 and 1-of-4** — and it is why those results are
not evidence that reasoning loses, only that reasoning-without-inputs loses.

---

## 7. The design

Four layers. Only one of them is a model, and it is not the first thing built.

### Layer A — the veto lane (deterministic, free, at emission)

**This is where "if that is not correct we cancel" lives, and it is not an LLM.**
A fill is instant; a model answers in seconds at best. A veto that runs *before*
`signal_queue.put` costs nothing and cannot be late. §4 says this is the only
direction with headroom, and §5.3 supplies its first candidate rule.

Ships **measure-only**: every candidate is stamped with what the veto *would*
have done, joined to the closed-signal record by `signal_id`, and rendered in
ops — the `entry_features` pattern, which is the one measurement lane in this
repo that never grew a resolver and never cost a session.

First rules to measure, all computable at emission and none invented today:
- `campaign_cold` — previous trade on this symbol lost, within 6h (§5.3). The
  stamp already exists and is consumed by nothing.
- `profile_reject` and the entry-quality rules already live in
  `entry_quality.py`, whose blast-radius cap the watchdog currently reports as
  exceeded (#1010) — meaning the gate is degraded to shadow and reads as passing.
- `mean_revert_emission` — 1,586 detections since the last emission, and the
  post-scoring blocked candidates measure **+0.36R over n=922** (#1010). A gate
  that is costing us is a veto pointed the wrong way, and it is measured.

### Layer B — the reviewer, in-process, on every signal

The existing fast lane, given what it lacks (§6): order book and flow for the
open book, and the structure the engine already computes, serialised into the
snapshot — swing sequence, levels with touch counts and ages, POC and value
area, higher-timeframe context, the recent bar sequence. **This is what "reads a
chart" means for a model**, and it is cheaper, more precise, cacheable and
testable against an image.

Its verdict vocabulary changes to match the findings:
- `MAINTAIN` — the default and the baseline, and on this book a strong one.
- `ADJUST_SL` — tighter only; the arm whose verdicts currently all age out.
- `HAND_TO_TRAIL` — the tail-preserving arm (v2 §5). `PROFIT_LOCKED` is already
  the book's best outcome by a wide margin (+1055% of +88% net), so the arm that
  lets a winner keep running is the one §2 argues for.
- **`ADJUST_TP` is de-armed** and demoted to shadow until §3's proper MFE-aware
  simulation says otherwise.

### Layer C — the deep pass, rare and escalation-only

Unchanged from v2 §9 in shape, changed in trigger: it runs when Layer A and
Layer B disagree, or on a named high-stakes condition — not once per signal.
Target ≤2 passes/day.

### Layer D — the scheduled-events calendar

The narrow, structured half of "news", and the only news-shaped input with any
evidence behind it (the SUI unlock; both open-web passes scored 0). Feeds
**Layer A as a rule**, never a model as prose. This is where the you.com credits
belong, and nowhere else.

**Exercised against the live vendor, 2026-09-04 [measured].** Three endpoints on
`https://api.you.com/v1/`, header `X-API-Key`:

| Endpoint | Latency | Returns |
|---|---|---|
| `/v1/search` | 0.7–1.0s | 10 web results, snippets, some dated |
| `/v1/answer` | 1.6–2.4s | the extracted fact plus citations |
| `/v1/research` | 19.4s | an agentic pass that checks its own work |

Coverage on our microcap movers is **not** the problem — BMT, BULLA, DEXE and
BICO all returned real tokenomics sources. **Data quality is.** Asked for the
*next* unlock:

| Symbol | `/v1/answer` | Verdict |
|---|---|---|
| SUI | Sep 3 2026 — 24,142,139 | correct |
| **BMT** | **Aug 18 2026** — 9,700,000 | **17 days in the past** |
| **BICO** | **1 Nov 2025** — 1,000,000,000 | **10 months stale, implausible size** |
| BULLA | NONE | correctly abstained |

Two of four confidently wrong, both on microcaps — the population this book
actually trades. `/v1/research` **fixed the BMT case** (*"18 September 2026 —
9,700,000 BMT (Investors), 0.97% of total supply"*, cited to CoinGecko): the
cheap endpoint had the right amount and the wrong month.

Three rules follow, and the first is what makes an unreliable source safe:

- **We never trust the text; we trust date arithmetic we do ourselves.** Any
  returned unlock date `<= today` is discarded and counted as `stale_answer`.
  That single rule catches both failures above. Refuse, do not clamp.
- **`/v1/research` for the calendar, not `/v1/answer`** — and therefore the
  calendar is a **per-symbol daily cache**, never a per-signal call. 19s is
  fine on a daily refresh and impossible on a signal.
- **A single answer is not ground truth.** Two sources disagreed on SUI (Sep 1 /
  22.01M against Sep 3 / 24.14M), so a fact without source agreement is marked
  `unverified` rather than published as a date.

One side-finding worth keeping: the research pass volunteered *"Bubblemaps
Surges on Upbit Listing"* with +66% 24h and +110% 30d on **BMT — the symbol that
produced four of the book's top ten trades** (§2). That is instrument context
the engine has never had, and it arrived from the calendar query rather than
from a news crawl.

### What does not change

Every invariant in v1 §7 and v2 §10 carries forward: a menu key and never a
price, the measurement flag ON and the effect flag OFF, the separate apply
budget, the panic ceiling that refuses while unset, the deep lane never blocking
a fill or an exit, and no second module that moves a resting stop.

---

## 8. Implementation process

Each phase ships dark, with its ops surface in the same change, and is gated by
a measurement rather than by a date.

| Phase | Ships | Gate to the next |
|---|---|---|
| ~~**P0**~~ **DONE** | The MFE-aware cap family, run and published in §3. No cap beats doing nothing; `ADJUST_TP` de-armed (`AI_GOV_ARMS_ENABLED` defaults to empty). | Complete — the refutation condition did not fire. |
| **P1** | The veto lane, measure-only: `campaign_cold` consumed from the existing stamp, plus the two gates the watchdog says are already misfiring. Ops panel in the same PR. | 200+ stamped candidates in a fresh window (`STATISTICAL_CHANGE_POLICY` rule 1). |
| **P2** | Unblind Layer B: on-arm depth/aggTrade subscription (bounded by the ~5 open signals, not the universe), and the structure serialisation into the snapshot. | `fully_blind` falls, and the two dead trigger rungs start firing. |
| **P3** ½ done | The verdict-age bound is now **derived from the observed sweep cadence** — floor 10s, slowest recent tick x1.5, hard cap 60s — instead of a constant asserting a property it did not have. Still to come: `HAND_TO_TRAIL` in shadow against the held-to-stop arm that already walks that counterfactual, handing to **SAR** on the bake-off evidence in §3. | The scorecard shows a per-arm estimate that is not `arm_undecidable_while_dark`. |
| **P4** | Arm **one** rule — the veto's `campaign_cold`, owner's account first — on a forward window that did not suggest it. | **Owner sign-off** against a scored out-of-sample window. |
| **P5** | Layer C and Layer D, on the evidence from P1–P4. | Owner sign-off. |

**Ordering rationale, stated so it can be argued with:** P0 first because the
currently-armed arm may be actively harmful and that is cheap to settle. P1
before P2 because the veto is where the headroom is and it needs no model. P2
before P3 because a bound fix on a blind reviewer arms an arm that cannot see.
P4 is one rule, not a lane.

**What this program will not do:** arm anything on the window that suggested it;
quote an in-sample figure as an expectation; treat §5.3's HOT half as
established; or put a model on the path that decides whether a fill happens.

---

## 9. Cost

Layer A costs nothing per signal. **Layer D's per-call price is not yet
measured** — the test above spent 6 `search`, 4 `answer` and 1 `research` call
against a $200 credit balance and the remaining balance has not been read back,
so the daily-refresh cost over ~75 symbols is **unpriced and must not be quoted
until it is**. It is a cache with a daily period, so it is not on any hot
path. Layer B is the existing fast lane:
**$0.00074/call measured, ~$2.80/month** at design volume **[verified]**; the
same lane on Claude Haiku 4.5 ($1/$5 per MTok) is ~4× that and still noise.
Layer C at ≤2 passes/day is ~$25/month. Total **$5–40/month** against one Auto
subscriber at ₹2,000.

**A consumer Claude or Gemini subscription cannot serve any of this** — a
subscription issues no API key, so the engine cannot call it, and a Slack-woken
session spends the owner's personal plan quota (~16/day at design volume, and
the plan was already near its cap after a handful) **[verified, 2026-09-04]**.

Cost is not what decides this program. §2 and §3 are.

---

## 10. What this retracts

- **v2 §12's D4** ("activate one arm — `ADJUST_TP` or `HAND_TO_TRAIL`, both
  fully decidable"). `ADJUST_TP` is decidable and, on the measured book,
  harmful. Decidability was being used as a proxy for safety and they are
  different properties.
- **The per-pair dossier as a symbol-quality memory**, proposed by me earlier in
  this session and refuted in §5.2 by the data I proposed it from.
- **My reading of the BULLA case** (§5.4): the saving fact was episode recency,
  not instrument history.
- **v2's framing that the deep lane is the destination.** On this evidence the
  destination is a deterministic veto with a model as its second opinion.

---

## 11. Open questions for the owner

1. **De-arm `ADJUST_TP` now?** It is the only armed arm, apply is off so nothing
   changes today, and §3 says it is the wrong arm to be first.
2. **The stream budget** — widen `DEPTH_MAX_SYMBOLS`/`AGGTRADE_MAX_SYMBOLS`, or
   subscribe on-arm and release at close? P2 assumes the second.
3. **The veto's first live rule** is a *reduction in signals delivered*, against
   `OWNER_BRIEF` §3.2's "quantity matters — 1–10 paid signals/day". `campaign_cold`
   would have dropped 254 of 1,395. That is a product decision, not an
   engineering one.
4. Carried from v2: `HAND_TO_TRAIL` per-signal or per-user and to which
   mechanism; `AI_GOV_MAX_USD_PER_DAY`; signal geometry in a third-party
   workspace.

---

## 12. Sources

**Measured this session:** `/track-record/trades.csv?window=90d` (1,580 rows,
2026-06-25 → 2026-09-04), analysed with the bootstrap and the
remove-the-tail cuts shown inline. Every figure in §§1–5 is reproducible from
that export.

**Verified live 2026-09-04:** `/signals/ai-governor`, `read.ai_governor` and
`read.ai_governor_scorecard` via the diagnostic console; GitHub issue #1010
(engine liveness watchdog).

**In repo:** `src/strategy_edge.py`, `src/entry_features.py`,
`src/execution/ai_governor*.py`, `src/entry_quality.py`, `OWNER_BRIEF.md` §3.2,
`docs/STATISTICAL_CHANGE_POLICY.md`, `docs/PLAN_AI_TRADE_GOVERNOR.md`,
`docs/PLAN_AI_TRADE_GOVERNOR_V2.md`.
