# The AI Trade Governor, v2 — the Deep Lane

**Status:** design of record for the *deep* lane. Written 2026-09-03. Nothing in
this document is implemented.
**Superseded in part by `docs/PLAN_AI_TRADE_GOVERNOR_V3.md` (2026-09-04).** v3
measured the recorded book — 1,580 closed signals — and found the program aimed
at the wrong half of the trade: the book's entire profit is ten trades, so the
`ADJUST_TP` arm this document schedules first (§12 D4) is measured *negative*,
and the headroom is in a veto at emission. v3 supersedes this document's
**targeting and rollout**; its invariants (§10), transport findings (§6) and
scoring discipline (§7) stand.
**Relationship to v1:** `docs/PLAN_AI_TRADE_GOVERNOR.md` remains the design of
record for the **fast lane** — the bar-clock classifier that is live, measuring,
and described accurately there. This document does not replace it. It adds the
second clock, the transport, the verdict the owner asked for, and the
measurement discipline that the first scored window showed we do not yet have.
**Owner request, 2026-09-03:** *"after signal delivery AI take charge … first look
is that correct signal, right time, with right Entry SL TPs … it fully analyse
signal and then act accordingly, if signal is not correct it cancels or adjust
values"*, then *"if anything has potential we do keep move it with trail"*, then
*"we don't judge yourself for just 4 outcomes, there is lot to observe and we not
making live, we do dark to ops first for our observations, so continue to build
robust."*

Two standing rules from `CLAUDE.md` govern this document as they did v1. Every
fact is labelled **[verified]** (read from this tree, or from the running system
during the session that wrote this), **[documented]** (vendor documentation read
but not exercised), or **[inferred]**. An unlabelled inference reads exactly like
a measurement. And a finding and a fix are separate deliverables: §1–§3 are
findings, §4 onward is the build.

---

## 0. Executive summary

v1 built a **classifier**: one snapshot in, one word out, 3.6s, on the signal's
own bar clock. It is live and measuring. What the owner has asked for is an
**agent**: something that independently investigates the instrument, the chart,
the market and the news, and reaches its own view of whether the trade is right.
Those are different machines, and the second one is built on top of the first
rather than instead of it.

Five things decide whether the deep lane is worth having, and four of them are
architectural:

1. **The scoring harness comes first, before any deep analysis ships.** The first
   scored window (§1) produced a wrong thesis on 3 of 4 signals and was caught in
   **four hours** because the outcomes happened to be checkable by hand. Nothing
   in the repo does that automatically. Until it does, this lane is the
   sophisticated exit machinery that already cost 19.14 points (`OWNER_BRIEF`
   §3.2 **[verified]**), with no instrument pointed at it.
2. **Two clocks, not one.** A 60–180s research loop cannot run on a 5s tick. The
   fast lane holds the position between deep passes; the deep lane produces a
   standing thesis. Neither replaces the other.
3. **The engine owns the chain; the agent is an upgrade.** A session is
   ephemeral — this is not a caution, it is a measured property (§6.2). Any
   design where a trade waits on an external session is disqualified.
4. **A menu key, never a price — unchanged from v1, and it now matters more.** An
   agent that has read the open web is a wider input surface, so the output
   contract has to stay exactly as narrow as it is today.
5. **Ops first, and dark means visible to the owner from day one.** Every lane
   below ships its panel in the same change. "Measured but nowhere to look" is
   what left the v1 governor's blindness rate unpublished (§3.3).

---

## 1. The first scored window — what it is, and what it is not

On 2026-09-03 the owner sent a screenshot of four open signals and asked for
exactly the analysis this lane is meant to produce. It was done by hand at
**10:20 UTC** using live market data (OKX, CoinGecko), multi-timeframe candles,
market-structure metadata and web news search. By **14:52 UTC** all four had
closed. **[verified — outcomes read from the ops closed-signal feed, which
renders `signal_performance.json`.]**

| Signal | Thesis at 10:20 | Recorded outcome | Correct? |
|---|---|---|---|
| BULLAUSDT LONG · MVRTP | "pull TP nearer, harvest ~+5%" | `PROFIT_LOCKED` **+7.31%** | No |
| SUIUSDT SHORT · LSR | "sound, hold, no change" | `SL_HIT` **−1.66%** | No |
| PENGUUSDT LONG · QBREAK | "failed break, let the stop take it" | `SL_HIT` **−1.11%** | Yes |
| LINKUSDT LONG · QBREAK | "premise broken, let the stop take it" | `TP1_HIT` **+1.70%** | No |

The engine's own governor answered `MAINTAIN` on all four, which is the recorded
book: `+7.31 − 1.66 − 1.11 + 1.70` = **+4.24%**. The single actionable
recommendation in the analysis — clipping BULLA — would have produced
**+1.93%** **[inferred, from the stated harvest level against the recorded
close]**.

### 1.1 What this window does NOT establish

**Four rows decide nothing, and this document will not pretend otherwise.**
`STATISTICAL_CHANGE_POLICY` rule 1 requires ≥200 closed signals in the affected
cohort spanning ≥21 days **[verified]**; four is three orders of magnitude short
of a verdict, no confidence interval on it is worth printing, and this repo has
already paid a session for reading a three-row cell as a promotion
(`FAILED_AUCTION_RECLAIM`, +0.846R on n=3, CI [−1.00, +2.00]). The correct
reading of the table above is **"the first four rows of a ledger"**, not "the
deep lane loses to `MAINTAIN`".

It is recorded here for three reasons, none of which is a verdict:

- It is the **first evidence of any kind** about what this lane produces. v1's
  ledger holds 7 rows, all `MAINTAIN`, and therefore contains no information
  about intervention at all.
- It establishes the **baseline the lane must beat**, and that baseline is
  `MAINTAIN`, not zero. A lane that intervenes and matches doing-nothing has
  cost fees for nothing.
- It demonstrates the **scoring harness is the deliverable** (§7). The thesis was
  falsified in four hours by a join that already exists in the repo. Nobody had
  to wait for a window; the machinery to catch a bad thesis fast is *already
  there* and simply is not wired up.

### 1.2 What it does establish, and is worth designing around

Three observations survive the small n because they are structural rather than
statistical:

- **Every fact in the BULLA thesis was true and the conclusion was backwards.**
  $32M market cap, +57% on the day, $3.8M spot volume, giving back from its
  peak — all correct **[verified]**, and the right action was the one the engine
  already takes: breakeven stop, let it run. The same path profit-locked
  **+7.31 / +5.59 / +8.35** on that symbol inside twelve hours **[verified, ops
  closed feed]**. This is `CLAUDE.md`'s *check the direction of every
  recommendation, not only its premise* — and it means an instrument classifier
  (§8) is a **feature**, never a policy. The policy on top of it is measured, not
  assumed.
- **One macro variable dominated all four outcomes.** BTC moved **77,670 →
  80,285 (+3.4%)** across the window **[verified, OKX]** and lifted the whole
  book. Two identical `QUIET_COMPRESSION_BREAK` longs resolved in opposite
  directions with nothing in the per-coin analysis separating them. The engine
  already computes and already publishes this input.
- **The news layer changed no verdict, for the second time.** Yesterday's
  five-trade pass scored it 0 of 5 on judgement alone; this pass scored it 0 of 4
  with outcomes attached. That is not proof it is worthless, but it is now twice
  the weakest of the four candidate inputs, and it is also the only one carrying
  a prompt-injection surface (§10). It ranks last, and it ships last.

---

## 2. What v1 shipped, measured on the running system

Read live from `/signals/ai-governor` and `read.ai_governor` through the
diagnostic console, 2026-09-03 **[verified]**:

| | |
|---|---|
| Lane | MEASURING · apply OFF · `armed_arms: ["tp"]` |
| Sweeps | 1,320 |
| Triggers fired | 7 |
| Model calls | 6 · all `ok` · served `gemini-3.7-flash` |
| Verdicts | 7 — **all `MAINTAIN`** |
| Applied | 0 |
| Refusals | none · throttles: `cooldown` 250 |
| Spend | **$0.0044** total · last latency 3,642 ms |
| Ledger | 7 rows |

Two readings matter for this document:

- **Only one of four trigger rungs has ever fired.** `trigger:r_band` 7;
  `macro`, `near_tp` and `flow_opposed` are **zero**, and every arm shows
  `calls_made: 1` **[verified]**. In practice the fast lane takes exactly one
  look per signal shortly after arming, and the 300s cooldown plus a
  half-R band keeps it quiet for the rest of the trade's life. The rungs designed
  to notice *reality changing* have contributed nothing — and on 2026-09-03 the
  `macro` rung was the one that would have mattered.
- **The cost model is sound and the number is tiny.** $0.00074/call
  **[verified]** against a $5.54/mo plan estimate. Cost is not what decides
  anything here, which is the same conclusion v1 reached and is worth
  re-confirming rather than re-litigating.

---

## 3. What the governor cannot see today — verified gaps

### 3.1 No structure reaches the model

`Snapshot` carries: `signal_id`, `symbol`, `side`, `setup_class`,
`entry_regime`, `trigger_tf`, `as_of_bar_ms`, `dist_to_sl_pct`,
`r_multiple_now`, `mfe_pct`, `mae_pct`, `bars_since_entry`,
`book_imbalance_aligned`, `cvd_slope_aligned`, `price`, `macro`, `menu`
**[verified, `src/execution/ai_governor_snapshot.py`]**.

That is all of it. There is **no** Level Book, **no** Volume Profile POC or value
area, **no** structure state, **no** SMC zone, **no** chart pattern — and
`grep` for any of those modules across `src/execution/ai_governor*.py` returns
**nothing** **[verified]**. The engine computes all of them on every scan.

The owner's brief asks the AI to *"analyse chart structure"*. Most of that
request is satisfied by passing what already exists.

### 3.2 The menu builder does not read the level modules its own plan names

v1 §6's module map says `ai_governor_menu.py` *"reads `level_book`,
`volume_profile`, `structural_levels`"*. It does not: it runs a private pivot
scan over raw `highs`/`lows` arrays **[verified]**. This is the eighth
recurrence in these two repos of a description asserting a property the code
beneath it does not have, checkable in one command. v2 corrects the code, not
the sentence.

### 3.3 The blindness rate is specified and unpublished

**Corrected 2026-09-03, during D0.** This section first read *"it is absent from
the page and from the engine payload"*. That was imprecise in a way worth
recording rather than quietly editing: the **per-row stamp has always existed**
(`ai_governor.py` writes `unknown_frac` on every ledger row, and
`probe_blindness` reads it correctly **[verified]**). What was absent is the
**aggregate** — nothing in `build_diag()` reduced it and no surface rendered it,
so the stamp was being written into a ledger nobody could read it out of. The
fix is therefore an aggregator and a panel, not a stamp; had the section stood,
a future reader would have gone looking for a missing write that was never
missing. Same class as the claims this document exists to label.

v1 §3 requires `unknown_frac` for book and flow on the ops panel, on the
reasoning that a verdict issued blind is legitimate but must not be presented as
fully-informed. No aggregate reached the page or `build_diag()`
**[verified]**. `DEPTH_MAX_SYMBOLS` and `AGGTRADE_MAX_SYMBOLS` are both 40 while
much of the delivered book is promoted movers **[verified, v1 §3]**, so a large
share of verdicts are book- and flow-blind and **nothing on any surface says
which**. D0 also splits the two: `blind_fraction` pools book and flow into one
number, and an unsubscribed symbol (a stream-budget decision), a stale feed (an
incident) and a disabled consumer flag (a switch nobody threw) have three
different next moves. The pooled figure stays for continuity; the split and the
reason mix ship beside it. The 7 `MAINTAIN`s cannot currently be read as informed or blind. That
alone makes them uninterpretable, and it is fixed in the first PR of this
program regardless of which other lane ships.

---

## 4. The two clocks

```
FAST LANE (live, v1)                    DEEP LANE (this document)
5s tick · bar close · numbers only      once per signal + on macro/structural events
3.6s round trip                         60–180s, tool-using
holds the position between passes       produces a STANDING THESIS
never waits on anything external        may fail entirely with no consequence
```

The deep lane's output is a thesis the fast lane carries: a verdict key, a
confidence, and a set of named conditions under which the thesis is void. The
fast lane already runs every bar and already has the trigger ladder; a standing
thesis gives its rungs something to invalidate against, which is precisely what
they lack today (§2).

**The deep lane never blocks a fill, an exit, or a stop.** If it has not
answered, the fast lane's own verdict stands, which is what happens now.

---

## 5. The fifth verdict — `HAND_TO_TRAIL`

The owner's *"if anything has potential we do keep move it with trail"* collides
with v1's invariants as literally written: TP moves **nearer only** and SL
**tighter only**, and letting a winner run means moving a target further away —
banned as *"a new trade, not an adjustment"* **[verified, v1 §7]**.

It does not have to. `src/execution/trail_governor.py` is live and already
carries both mechanisms (Parabolic SAR and ATR-Chandelier), six sessions of
guards, `reduceOnly` sizing, place-then-cancel ordering and the -4130 repair
**[verified]**. "Let it run" is therefore not *widen the target* — it is **retire
the fixed TP1 and hand the position to the trail**, and a trail only ever
tightens.

So the fifth verdict is `HAND_TO_TRAIL`, and it:

- violates **no** existing invariant — the stop only ratchets toward price;
- **reuses** the one module allowed to move a resting stop, rather than adding a
  second;
- is **decidable from the record** — the held-to-stop arm in `sar_live_shadow`
  already walks exactly this counterfactual **[verified]**, so the ledger can
  score "what would the trail have produced" against "what TP1 produced" without
  a new resolver;
- is the arm the 2026-09-03 window most obviously wanted: BULLA at breakeven with
  a +57% day behind it is a chandelier's textbook case, and clipping it was the
  wrong call.

**Two open design points, both owner decisions, neither derivable from a shadow
window.** Whether `HAND_TO_TRAIL` is per-signal (overriding the per-user
`exit_mechanism` B17 setting) or applies only to users already opted into a
trail; and which mechanism it hands to. Both gate the arm, not the measurement.

---

## 6. The transport

### 6.1 What was tested

- **An engine cannot wake a Claude session directly.** A session-scoped inbound
  webhook was created and POSTed to from outside: **HTTP 401** **[verified]**.
  The credential is sealed to the artifact service and cannot be handed to the
  VPS. That path is closed.
- **The Slack connector works outward.** Channel creation, channel and thread
  reads, and threaded posting all exercised against the live workspace
  **[verified]** — `#lumin-signals` (`C0BUB9R8WCX`) was created and the first
  scorecard posted during the session that wrote this.
- **An incoming webhook posts into the channel.** `Lumin Engine`
  (`B0BUGDU0223`) created 2026-09-04, HTTP 200, message stored with a bot id
  and no user, mentions resolved **[verified]**. This is the engine → Slack
  direction and it works.
- **Slack cannot wake a Claude session either — see §6.2a.** Both routes are
  now measured dead, not assumed.
- **Binance public REST 451s from non-whitelisted IPs** **[verified]**; OKX and
  CoinGecko answer keyless and were used for every market figure in §1
  **[verified]**.

### 6.2 The durability property, stated as a constraint

Every session-bound mechanism available expires, and none announces it: cron
jobs here are session-only and auto-expire after 7 days **[documented, tool
contract]**, an inbound watch ends with the session **[documented]**, and the ops
guest credential used for §1 expires in hours **[verified]**.

**Therefore: no lane in this document may be a link in the chain that guards
live capital.** By this repo's own standard — a watchdog that fails silently is
worse than no watchdog — an ephemeral analyst is admissible only as an
enhancement. The engine decides; the deep lane upgrades a thesis; if it is not
there, nothing waits and nothing degrades.

### 6.2a The wake test — RUN 2026-09-04, and it answered NO

§16's first open question, settled by measurement rather than by argument. Two
posts into `#lumin-signals`, both with the mention resolved to
`<@U0BUVE692R4|Claude>`, in a channel Claude had been invited to and where a
message typed by the owner gets a reply within seconds **[verified]**:

| Test | Poster | Result |
|---|---|---|
| 1 · 07:30 IST | the Claude app, on the owner's behalf (`Sent using Claude`) | **no reply**, one hour |
| 2 · 08:31 IST | the `Lumin Engine` incoming webhook — a bot id, no user | **no reply** |

Test 1 alone was not conclusive and this document says so rather than burying
it: the connector and the Slack Claude app are the **same app**
(`A08SF47R6P4`, bot user `U0BUVE692R4`), so Claude was ignoring its own
message, which is ordinary loop protection. Test 2 removed that confound
entirely — a different app, its own bot identity, the exact shape the engine
would send — and the answer did not change.

**The mechanism is structural, not a setting.** Claude in Slack runs each
session under *the connected Claude account of the person who mentioned it*
**[documented, vendor]**. A webhook message has no person behind it, so there
is no account to run a session under and nothing to wake. No toggle changes
that.

**So there is no path by which the engine wakes an external analyst.** The
session-scoped inbound webhook answers 401 (§6.1) and Slack does not respond to
machines. Every remaining design is **pull, not push**, and that is the finding
that reorganises this document — see §6.2b.

### 6.2b What that means: the automatic lane is IN the engine

The owner's requirement, restated 2026-09-04: *"new signal out, you Claude wake
review that signal with your own analysis, adjust if anything needed, if that
not correct we do cancel — everything should go automatic."*

Automatic on every signal, with no human in the loop, rules out an external
Claude session **by measurement, not by preference**. What it does not rule out
is the requirement itself: the engine already makes its own model call, on its
own clock, with no session and no Slack, and that call is the fast lane that is
live today. The deep lane is therefore **not a different machine reached over a
transport** — it is the same in-process call given more context (§3.1, §8), a
longer clock (§4), and the fifth verdict (§5).

This collapses the roadmap rather than extending it: D1's polling analyst and
D2's woken analyst were two transports for a component that should not be
remote at all. What survives from them is the part that was always independent
of the transport — the packet, the standing thesis, and the scorecard.

**Slack is demoted from transport to surface**, and that is not a loss:

- the engine posts the packet through the webhook (verified working);
- the owner reads it on his phone, where he already is;
- when he wants a research pass with judgement in it, he `@Claude`s the thread
  himself — a human mention, which works today, costs nothing when unused, and
  analyses only the signals he cares about.

That last line is an **override channel and never a link in the chain** (§6.2),
which is exactly the standing this document already required of anything
session-bound.

### 6.3 Slack as the reporting surface

Chosen by the owner. Three properties earn it over GitHub:

- **The smallest credential on the trading box** — one write-only incoming
  webhook URL scoped to one channel, revocable in a click, against a repo-write
  token.
- **Bidirectional, so it is the return path too** — thesis in a thread, engine
  reads the thread. No ops credential in the session and no new engine control
  endpoint for v1.
- **A fresh session per signal, if the inbound path works** — nothing to keep
  alive, which is the only clean answer to §6.2.

**That gate was run on 2026-09-04 and it answered no** (§6.2a). The three
properties above still earn Slack its place — they were always properties of
the *channel*, not of the wake — but the third one ("a fresh session per
signal, if the inbound path works") is struck. Slack is where the owner reads
and overrides; it drives nothing.

**Push the data, do not grant the access.** The engine posts the packet; the
session needs no ops credential at all, only outward public market data. That is
strictly better than handing a rotating guest code to a session.

**One caveat found by testing:** the connector acts as the *owner's user
account*, not a bot **[verified]**, so posts by the analyst and by the owner are
indistinguishable by author. Engine posts must therefore come through a webhook
with its own bot identity, and loop protection is designed in before anything is
armed.

### 6.4 Content

Signal geometry — entry, SL, TP, setup class — would live in a third-party
workspace. It is the owner's private workspace with one member, which is about as
contained as this gets, but it is the same consideration that disqualified the
Gemini free tier for the decision prompt (v1 §9), and it is recorded as a
deliberate decision rather than a default.

---

## 7. The scoring harness — the FIRST deliverable

**Nothing else in this document ships before this does.**

The §1 thesis was falsified in four hours using a join that already exists:
`signal_performance.json`, written by `trade_monitor` at the terminal transition,
carrying the corrected `original_sl_distance` denominator **[verified]**. Doing
it by hand is not a system.

Requirements, each of which is a rule this repo has already paid for:

- **Every thesis is stamped, including `MAINTAIN`.** A lane that records only its
  interventions cannot compute a baseline and will look brilliant (v1 §10).
- **The baseline is `MAINTAIN`, and it is computed on the same rows.** Not zero,
  not the market. The question is only ever *did acting beat not acting on these
  signals*.
- **Do not build a resolver.** Join outcomes the closed-signal record already
  owns. Every forward-measurement arm in this repo that grew its own cost a
  session — `INSUFFICIENT` rows, stalled arms, stale anchors, over-walked series,
  undatable windows. `entry_features` is the pattern that avoided all of it
  **[verified]**.
- **Per arm, never blended.** `MAINTAIN`, `ADJUST_TP`, `HAND_TO_TRAIL` and
  `PANIC_CLOSE` are decidable from the record; `ADJUST_SL` is only partly so and
  its residue is direction-biased (v1 §8). A test asserts no combined figure
  exists.
- **Charge the round trip to both arms.** Charging the fee to the intervention
  and not to the baseline manufactures an edge out of the fee; charging it to
  neither hides the cost that dominates this book.
- **Every thesis is reconstructible.** The snapshot, the tool calls and their
  responses are stored with the verdict. A deep pass that cannot be re-read is
  not evidence — and unlike the fast lane, a web-informed thesis cannot be
  re-derived later because the web moved.
- **The scorecard renders in ops the day it ships**, and posts back into the
  signal's own Slack thread when the signal closes. A thesis nobody grades is an
  opinion.

The §1 table is the harness's first four rows, entered by hand. Its purpose in
this document is to show what the automated version must produce.

---

## 8. Lane A — the instrument X-ray, no model

The only actionable finding in two days of manual analysis came from three
numbers: market cap, spot volume, 24h change. No model produced it; a rule
produces it. And the *policy* attached to it was wrong (§1.2), which is exactly
why it ships as a **feature and a measurement, not a rule**.

- One keyless CoinGecko call per symbol per hour, cached: market cap, spot 24h
  volume, 24h/7d change, distance from ATH, listing age. **[verified reachable
  and keyless.]**
- The structure the engine already computes (§3.1), passed into the snapshot.
- The menu built from the Level Book rather than a private pivot scan (§3.2).
- A deterministic classifier: instrument tier, liquidity tier, parabolic flag —
  **stamped on every signal, consumed by nothing** until a scored window says
  what the right policy is.

This needs no model, no key, no vendor and no approval, and it is the input the
deep lane would otherwise have to fetch on every pass. It ships first alongside
§7 and §3.3.

---

## 9. The deep lane

### 9.1 Shape

A tool-using pass, run **once per signal** shortly after arming and again on a
macro or structural event, producing a standing thesis the fast lane carries.

Tools, in the order the evidence ranks them:

1. **Instrument X-ray** (§8) — in-process, free, and it is what flagged BULLA.
2. **Chart structure** (§3.1) — already computed, currently discarded.
3. **Multi-timeframe candles** — already in the store.
4. **Token unlock / event calendar** — the single news item across two manual
   passes that would have changed a decision (SUI's September unlock) was a
   *scheduled* fact. A calendar is a bounded structured feed; a crawler is not.
5. **News / web** — 0 of 5 and 0 of 4. Ships last, and only behind §10's
   classifier.

### 9.2 Cost

Measured from the manual passes: ~15 tool calls, and **$0.05–0.10 per deep
analysis** at the configured tier **[inferred, from token volume against the v1
rate table]**. At ~16 signals/day with one deep pass each that is ~$40/month;
with re-runs on macro events, ~$120/month. Against $0.0044 of measured fast-lane
spend **[verified]** that is 100–500×, which makes `AI_GOV_MAX_USD_PER_DAY`
mandatory rather than optional (v1 §12 deliberately left it unset).

**An IP-split may take it to zero.** v1 disqualified the Gemini free tier because
the prompt carries `setup_class`, entry geometry and gate provenance. That is
true of the *decision* prompt and false of the *research* prompt: characterising
a public instrument from public market data and public news carries none of our
IP. Research on the free tier, decision in the engine, is a legitimate split and
is worth pricing before committing to a paid tier for the deep lane.

### 9.3 Latency, and what "cancel" can actually catch

A deep pass takes 60–180s; fills are instant. So "cancel" means **close at market
within the first minutes, plus a retraction on the signal card** — a
subscriber-facing decision, not only an engineering one.

Calibration from the two manual windows: **none of the nine signals examined
would have been cancelled at that horizon.** LINK and PENGU failed over three
hours, not three minutes, and no information available at minute two would have
called either. The veto catches *"this signal is wrong on its face"* — wrong
instrument class, a known event, a macro break — not *"this setup will fail"*.
That is worth having and it is a smaller claim than the brief implies, and
saying so now is cheaper than discovering it in month three.

---

## 10. Invariants

Everything in v1 §7 carries forward unchanged. The deep lane adds:

| Invariant | Why |
|---|---|
| The thesis returns a **menu key**, never a price — including from an agent that has read the open web | Tools widen what the model *knows*; they must not widen what it can *do* |
| **No free-form external text enters the verdict prompt.** News arrives as bounded classified fields from a separate pass | An agent with web access whose output can close a position is the largest attack surface this system will have |
| A thesis that cannot be reconstructed is **not admissible evidence** | The web moves; a fast-lane snapshot digest is not sufficient here |
| The deep lane **never gates** a fill, an exit, a stop, or a fast-lane verdict | §6.2 — an ephemeral analyst may only ever be an upgrade |
| `HAND_TO_TRAIL` hands to `trail_governor`; **no second stop-mover exists** | Six sessions of guards live in one module and are not re-bought |
| A verdict arriving after `AI_GOV_VERDICT_MAX_AGE_SEC` is **refused and counted** | Unchanged from v1, and a 180s pass makes it load-bearing rather than theoretical |

---

## 11. Ops first — what dark means here

Per `CLAUDE.md § Project Phase`: measurement flag **ON** and visible from the day
it ships, user-visible effect **OFF** until owner sign-off on a measured result.
The owner restated it directly for this program: *"we not making live, we do dark
to ops first for our observations."*

Concretely, and in the same PR as the code:

- `/signals/ai-governor` gains the **blindness columns** (§3.3) — the first thing
  to ship, because without them no verdict on the page is interpretable.
- A **scorecard panel**: thesis vs recorded outcome, per arm, with the
  `MAINTAIN` baseline beside it and the decidable fraction beside every delta.
  No combined figure, and a route test asserting none appears.
- **Deep-lane provenance**: which tools ran, which returned `readable:false`,
  latency, spend, and the reconstruction blob.
- **The Slack thread link on every row**, so the panel and the conversation are
  one artifact rather than two.
- Every panel graded on the **engine's** stamps, never on ops' clock.

---

## 12. Rollout

| Phase | Ships | Gate |
|---|---|---|
| **D0** | Blindness columns (§3.3) · scoring harness (§7) · Lane A stamps (§8) · menu reads the Level Book (§3.2) | Normal PR — no model involved, nothing on the money path |
| **D1** | Slack channel + engine packet poster. Packets posted, theses recorded, scored, applied to nothing. ~~Polling analyst~~ — see §6.2b | Owner arms after one watched cycle |
| ~~**D2**~~ | ~~Event-driven fresh session per signal~~ — **STRUCK 2026-09-04.** The wake test ran and answered no (§6.2a); there is no path by which the engine wakes a session, so the analyst is in-process or it does not exist | Closed by measurement |
| **D3** | Deep lane with the §9.1 tool stack, news last | Owner sign-off |
| **D4** | Activate one arm — `ADJUST_TP` or `HAND_TO_TRAIL`, both fully decidable — owner's account first | **Owner sign-off** against a scored window |
| **D5** | Harvest a consistently-winning pattern into a **deterministic rule** | Dark-first + owner sign-off |

**D5 is the point, not an afterthought**, and §1.2 is the argument for it: the one
finding worth having so far was three numbers, not a paragraph. A permanent
per-signal LLM oracle on the money path is the scaffold this repo bans.

**On the window.** v1 §11.1 sizes it by *acted-on* rows, and at the fast lane's
current 0% intervention rate that window never closes. The deep lane's
intervention rate is unknown and is itself a thing D1 measures. Until D1 reports
one, no date is quoted here — quoting one would be the invented constant this
file has recorded seven times.

---

## 13. Config (additive to v1 §12)

```
AI_GOV_DEEP_ENABLED             bool   default TRUE    # measurement — ON when it ships
AI_GOV_DEEP_APPLY_ENABLED       bool   default FALSE   # effect — owner sign-off
AI_GOV_DEEP_MAX_USD_PER_DAY     float  default 10.0    # mandatory here, unlike the fast lane
AI_GOV_DEEP_TIMEOUT_SEC         float  default 180.0
AI_GOV_DEEP_MAX_PASSES_PER_SIG  int    default 3
AI_GOV_DEEP_TOOLS               str    default "xray,structure,candles"   # news added last
AI_GOV_SLACK_WEBHOOK_URL        secret deploy-injected; never logged
AI_GOV_SLACK_CHANNEL_ID         str    default ""
AI_GOV_TRAIL_HANDOFF_MECHANISM  str    choices {sar, atr}   # owner-set, gates D4
```

`AI_GOV_DEEP_TOOLS` is choices-validated and an unrecognised token is a **counted
refusal**, never a silent inert lane — the `TRAIL_GOVERNOR_TIMEFRAME` defect,
which shipped as free text and went permanently inert with its switch reading ON
**[verified, `CLAUDE.md`]**.

---

## 14. Testing

Beyond v1 §13, which carries forward in full:

- **The scorecard's baseline is the same rows.** A test drives a mixed set and
  asserts the `MAINTAIN` baseline is computed over exactly the rows the
  intervention arm scored — the panel-on-a-filtered-population defect (#90/#91),
  arriving at a scorecard.
- **A `MAINTAIN` thesis is recorded.** Assert the ledger holds it, or the lane
  will look brilliant.
- **The deep lane cannot block.** A test stalls the deep pass past its timeout
  and asserts the fast lane's verdict is unaffected and the position is untouched.
- **No thesis without provenance.** A row missing its tool-call record is refused
  at write time, not filtered at read time.
- **`HAND_TO_TRAIL` reaches `trail_governor` and nothing else.** An AST test
  asserts no second code path places or moves a stop.
- **The menu reads the Level Book.** A test drives the real `level_book` and
  asserts the candidates come from it — pinning the call site, not the import,
  because §3.2 is what a docstring alone bought us.
- **Slack payloads carry no secret.** Force every error path and assert neither
  the webhook URL nor any credential renders.
- **`ruff` before believing a green suite.** A missing import inside a handler the
  suite never enters is `F821` and invisible to 9,000 passing tests.

---

## 15. What this program will not claim

Everything in v1 §14, plus:

- **It will not read §1 as a verdict on the deep lane.** Four rows, no interval
  worth printing, and this repo has already paid a session for reading three.
- **It will not read §1 as a verdict on the fast lane either.** Seven `MAINTAIN`s
  on an unpublished blindness rate is not evidence that `MAINTAIN` is right; it
  is evidence that we cannot yet tell.
- **It will not claim the deep lane works because its write-ups read well.** The
  §1 theses read extremely well and were wrong three times out of four.
- **It will not present a manual pass as the automated lane's expected
  performance.** Different operator, different clock, different tool budget.

---

## 16. Open questions

Settled by the owner, 2026-09-03, recorded so they are not re-asked: Slack is the
transport; dark-to-ops before any live effect; the program continues to be built
out rather than paused on a four-row result.

Settled by measurement, 2026-09-04: **the Claude Slack app does not respond to
a machine-posted message** — twice, once from the connector and once from a
plain incoming webhook (§6.2a). D2 is struck and the automatic lane lives in
the engine (§6.2b). Recorded here in full because a question answered by a test
is worth more than the design that asked it, and because the next reader will
otherwise re-run it.

Still open:

1. **`HAND_TO_TRAIL` — per-signal or per-user, and to which mechanism?**
   *Gates D4.*
2. **Cancel semantics** — retract-and-close-at-market with a signal-card
   retraction, or veto-before-dispatch at the cost of entry latency? *Gates the
   veto arm; §9.3 says the catchable population is small either way.*
3. **The IP-split free-tier research lane, or a paid key?** *Gates D3's cost.*
4. **Signal geometry in a third-party workspace** — deliberate acceptance
   required (§6.4). Narrower now that Slack carries no verdict: the packet is
   a report, not a control path.

---

## 17. Sources

**In-repo [verified]:** `src/execution/ai_governor.py`,
`ai_governor_snapshot.py`, `ai_governor_menu.py`; `src/ai_governor_ledger.py`;
`src/execution/trail_governor.py`; `src/diag_catalog.py`;
`src/structural_snap.py`; `src/sar_live_shadow.py`; `config/__init__.py`;
`OWNER_BRIEF.md` §3.2; `CLAUDE.md`; `docs/PLAN_AI_TRADE_GOVERNOR.md`;
`docs/STATISTICAL_CHANGE_POLICY.md`.

**Running system [verified], read 2026-09-03 via ops guest session and the
diagnostic console:** `/signals/ai-governor`; `read.ai_governor`; the ops
closed-signal feed (`signal_performance.json`).

**External [verified], read 2026-09-03:** OKX public market data and candles;
CoinGecko markets endpoint (keyless); Binance Futures public REST returning HTTP
451 from non-whitelisted addresses.

Market figures in §1 are as of their stated timestamps and are not constants.
