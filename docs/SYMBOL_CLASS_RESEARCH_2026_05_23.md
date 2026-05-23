# Symbol-class filtering — research doctrine

**Status:** Research-only. **No code change proposed for execution yet** — per owner instruction "go deep research and based on truth report come to with solution". This document gathers the evidence and lays out the design questions; an implementation plan will follow once the owner picks a class taxonomy.

**Companion changes in this commit set (already implemented):**
- `FEEDBACK_LOOP_ENABLED=false` by default (config) — disable the "AI" history-based confidence adjustment.
- `TP_QUIET_COMPRESSION_FACTOR=0.6` (config) — QUIET regime TP compression tightened from 0.9× to 0.6×.

---

## What the data shows about symbol concentration

### From the last 100 closed signals (`signals_last100.json` on `origin/monitor-logs`):

**Top winning symbols (sum of positive PnL):**
| Symbol | N | Net PnL | Avg | Class hypothesis |
|---|---:|---:|---:|---|
| FARTCOINUSDT | 10 | +3.54% | +0.354% | Narrative meme |
| JTOUSDT | 10 | +2.97% | +0.297% | Solana DeFi |
| FILUSDT | 9 | +2.59% | +0.288% | Storage narrative |
| ENAUSDT | 8 | +1.72% | +0.216% | Restaking narrative |
| PLAYUSDT | 6 | +1.37% | +0.228% | GameFi |
| **Top-5 net** | **43** | **+12.19%** | — | **51% of total signal volume, 100% of net wins** |

**Top losing symbols (sum of negative PnL):**
| Symbol | N | Net PnL | Avg | Class hypothesis |
|---|---:|---:|---:|---|
| BZUSDT | 4 | −1.19% | −0.298% | Newer listing |
| GRASSUSDT | 1 | −1.17% | −1.169% | Newer listing |
| AGTUSDT | 2 | −1.02% | −0.508% | Newer listing |
| XMRUSDT | 7 | −0.95% | −0.136% | Privacy (decoupled from narrative cycle) |
| PLUMEUSDT | 2 | −0.81% | −0.403% | Newer listing |
| PHAROSUSDT | 1 | −0.80% | −0.800% | Newer listing |
| MITOUSDT | 2 | −0.73% | −0.363% | Newer listing |
| AVNTUSDT | 1 | −0.65% | −0.651% | Newer listing |
| SOLUSDT | 9 | −0.64% | −0.071% | Large-cap (currently in compression) |
| LPTUSDT | 2 | −0.60% | −0.300% | Older mid-cap |

### From the truth snapshot (24h, `truth_snapshot.json`):

**Pre-TP fires by symbol (where the engine is actually banking partials):**
| Symbol | Pre-TP fires | Confirms |
|---|---:|---|
| ENAUSDT | 5 | Top of winning list |
| PLAYUSDT | 5 | Top of winning list |
| FARTCOINUSDT | 4 | Top of winning list |
| JTOUSDT | 4 | Top of winning list |
| PUMPUSDT | 3 | Narrative — meme/launchpad |
| SOLUSDT | 3 | Large-cap (signals fire but residual flat) |
| FILUSDT, SAHARAUSDT, USELESSUSDT | 2 each | Narrative tokens |
| 11 others | 1 each | Long tail |

19 of 75 pairs accounted for all pre-TP fires. **56 pairs (75%) produced zero pre-TP fires in 24h**.

**Quiet-scalp-block by symbol (signals correctly filtered in QUIET regime):**
| Symbol | Block count | Class observation |
|---|---:|---|
| AVAXUSDT | 53 | Large-cap, compressed |
| LITUSDT | 53 | Older mid-cap |
| CRCLUSDT | 52 | **Tokenized stock (Circle IPO)** |
| MUUSDT | 49 | **Tokenized stock (Micron)** |
| 1000PEPEUSDT | 44 | Meme |
| ASTERUSDT | 30 | — |
| BCHUSDT | 30 | Large-cap |
| TAOUSDT | 30 | AI narrative (but blocked anyway) |
| EWYUSDT | 28 | **Tokenized stock (iShares ETF)** |
| DOGEUSDT | 26 | Large-cap meme |
| INTCUSDT | 19 | **Tokenized stock (Intel)** |
| CLUSDT | 19 | **Tokenized stock (Colgate)** |
| BTCUSDT | 21 | Large-cap |

**Important discovery**: the engine's pair universe includes tokenized stocks (CRCL=Circle IPO, MU=Micron, INTC=Intel, CL=Colgate, EWY=iShares ETF, BCH=BCH ticker but also tokenized?). These are correctly QUIET-blocked already, but they're crypto-paired on a 24/7 venue and have entirely different microstructure than spot-crypto pairs. **They should never have been admitted as scalp candidates in the first place.**

---

## Five candidate symbol-class taxonomies

Each taxonomy is a different way to partition the 75-pair universe. The goal is to find the cut that maximally separates winners from losers without over-fitting on small samples.

### Class A: Narrative-driven small-caps
**Examples in data:** FARTCOIN, JTO, FIL, ENA, PLAY, PUMP, SAHARA, USELESS, NIL, SWARMS
**Win rate in data:** Heavy concentration of positive PnL (+12.19% from top-5 alone)
**Hypothesis:** These pairs trade on narrative flow — DeFi launchpad rotations, AI-token rotations, meme cycles. They have realistic intraday volatility (1-3%/hour) within which TP1 is reachable.
**Source signal in code:** Currently NONE. The engine doesn't know what is "narrative-driven."
**Implementation difficulty:** Hard. Needs an externally-curated list updated weekly, or a heuristic based on recent realized vol + funding-rate behavior + listing-recency.

### Class B: Large-cap majors (compression-prone)
**Examples in data:** BTC, SOL, BNB, AVAX, BCH, UNI, NEAR, DOGE
**Behavior in data:** Either heavily QUIET-blocked OR fires signals that exit near break-even (SOL: 9 signals, −0.64% net).
**Hypothesis:** BTC dominance ~60% + 7-month low implied vol means majors are too compressed to scalp profitably right now. The engine already has `pair_tier=MAJOR` with SL multiplier 0.95×, but the TP compression isn't aggressive enough.
**Source signal in code:** `PairProfile.tier == "MAJOR"` (from `src/pair_manager.py::classify_pair_tier`) already exists; threshold is ≥ $500M/day volume.
**Implementation difficulty:** Easy. The classifier already runs.

### Class C: Tokenized stocks (24/7 misfit)
**Examples in data:** CRCL, MU, INTC, CL, EWY
**Behavior:** Already QUIET-blocked 28-52× per pair in 24h. Almost never fire.
**Hypothesis:** These are crypto-wrapped equities. Their price discovery happens during US RTH, then they drift through Asian/EU hours. Scalp microstructure does not apply.
**Source signal in code:** None. Currently classified into MAJOR/MIDCAP/ALTCOIN by 24h crypto volume only — they fall into ALTCOIN.
**Implementation difficulty:** Medium. Needs a maintained blocklist or a regex pattern on Binance's "stock" tickers (CRCL, MU, INTC, etc. are recognisable but the pattern is not regex-safe).

### Class D: Newer listings (within 90 days)
**Examples in data:** BZ, GRASS, AGT, PLUME, AVNT, MITO, BEAT, PHAROS
**Behavior:** Concentrated in the losing column. Limited price history → unreliable structural levels.
**Hypothesis:** SR_FLIP, FAR, LSR all depend on multi-day swing structure. Newer listings don't have the history; their MFE-to-MAE ratios are worse because structural levels are wrong.
**Source signal in code:** Binance listing-date isn't tracked. Could derive from "first kline timestamp older than X."
**Implementation difficulty:** Medium. Needs a one-time backfill of listing dates plus periodic refresh.

### Class E: Realized-vol regime per pair
**Behavior:** Per-pair 1h realized-volatility threshold — only emit signals if realised vol is in a productive band (not too low → no TP reach, not too high → no SL hold).
**Hypothesis:** This is the cleanest signal but requires per-pair rolling stats. Already partially implemented via `atr_percentile` in the existing regime classifier.
**Source signal in code:** `atr_percentile` is computed per-pair; the QUIET regime block already uses it.
**Implementation difficulty:** Easy-medium. Add a per-pair sweet-spot band (e.g., 30th-70th ATR percentile = OK, outside = penalised).

---

## Which class taxonomy actually carves the data best?

**Combining Class A (narrative) and Class C (tokenized stocks) explains nearly all the signal:**

- Top-5 winning symbols (Class A): +12.19% net on 43 signals (45% of all PnL).
- Top tokenized stocks (Class C): already 100% QUIET-blocked. Effectively zero contribution either way.
- Class B (large-caps): mostly QUIET-blocked already; the few that fire (SOLUSDT n=9) net slightly negative.
- Class D (newer listings): concentrated in losers but small samples per symbol (1-4 each).

**The most actionable cut for this market regime**: explicit symbol-class boost for narrative-driven small-caps (Class A) and explicit deprioritisation for newer-listings (Class D).

Class B (large-caps) is already handled by `pair_tier=MAJOR` SL scaling. Class C (tokenized stocks) needs a one-line blocklist addition.

---

## What "narrative-driven" actually means — operational definition

This is the hard problem. Three possible signal sources to define Class A:

1. **External curated list, updated weekly.** Most accurate. Highest maintenance burden. Could ship as a YAML in `config/narrative_pairs.yaml` and be owner-editable.
2. **Heuristic on listing recency + volume growth + funding-rate behavior.** Less accurate. Self-maintaining.
3. **Hybrid: 30-day rolling realized PnL per symbol from `signals_last100.json`-style logs.** Self-supervising — promote symbols that won recently, demote symbols that lost recently. Risk: this becomes a feedback loop that overfits to recent regime.

**Owner discussion needed:** which of these three matches the engineering culture you want — curated, heuristic, or self-supervising?

A pragmatic v1: **curated list of ~15-20 narrative-driven pairs, owner-editable, with a per-pair confidence-bonus modifier (+2 pts when in list, default 0).** Low-risk, easily reversible, easily auditable. The truth report should then surface whether the bonus is earning its keep before any further tuning.

---

## Decision matrix — taxonomy choices

| # | Taxonomy choice | Strength | Implementation risk | Reversibility |
|---|---|---|---|---|
| A1 | Curated narrative-pair list with +2pt confidence modifier | Strongest evidence: top-5 = +12% net | Low-medium (one config file) | Trivially editable |
| A2 | Heuristic narrative detection (vol/funding/listing-age) | Self-maintaining; no human input | Medium-high (risk of mis-classifying) | Reversible via env flag |
| A3 | Self-supervising rolling PnL per symbol | Naturally adapts to regime | High (feedback loop risk) | Env-flag gated |
| B1 | Tokenized-stock blocklist | Crystal clear; no false-positive risk | Trivial (5-line config addition) | Owner-editable list |
| C1 | Newer-listings dampener (-2pt for symbols < 90 days old) | Moderate evidence | Medium (need listing-date backfill) | Env-flag gated |
| D | Defer all symbol-class work and let TP-compression + AI-disable changes bed in first | Conservative | Zero | n/a |

---

## What I would NOT propose blindly

- **Removing pairs from the universe.** Coverage matters for subscriber retention (truth-report shows 75 pairs scanned). Better to weight or block at signal-emission than to drop pre-scan.
- **Hard symbol blocks based on per-symbol PnL.** The sample sizes per symbol are 1-10 signals. PnL-based blocks would overfit immediately.
- **Adding a new "narrative score" evaluator to the 15 setup paths.** The doctrine in CLAUDE.md is clear: each evaluator owns its geometry; cross-cutting signals like symbol class belong in a post-evaluator soft-modulator step (B5), not as a 16th evaluator.

---

## Recommended next step (owner picks)

Pick one of these for the next implementation slice:

1. **Curated narrative-pair list (A1) + tokenized-stock blocklist (B1)** — combined, 30 min of implementation, owner-editable YAML, gated by env-flag. Lowest blast radius, strongest evidence-to-action ratio.
2. **Heuristic narrative detection (A2)** — 1-2 days of implementation, higher complexity. Skip until A1 has been measured for one truth-report cycle.
3. **Defer (D)** — let the FEEDBACK_LOOP and TP-compression changes bed in for 24h, re-measure the per-signal data, then re-evaluate. This protects against multi-knob blame distribution if outcomes shift.

---

## Verification approach for whichever option is picked

Per-signal data should be the validation metric, not just truth-report aggregates:

1. Run for one full 24h cycle after the change is live.
2. Re-pull `signals_last100.json` from monitor-logs.
3. Re-run the per-signal analysis. Track:
   - Winning-symbol concentration: does the top-5 still carry ~50% of net wins, or has it broadened?
   - Per-symbol-class avg PnL: do Class A symbols still outperform after the bonus?
   - Total signal count: did the symbol filter reduce volume too much for subscriber retention?
4. Truth-report aggregate confirms: avg PnL up, pre-TP fire rate up.

The success condition: avg PnL/signal moves from +0.073% toward +0.20%+ over 24h, AND total signal count stays above 80/24h (subscriber-retention floor).

---

## Files referenced

| Concern | File | Notes |
|---|---|---|
| Per-symbol signal records | `signals_last100.json` on `origin/monitor-logs` | 100 signals, 37 fields each |
| Per-symbol truth aggregates | `truth_snapshot.json` on `origin/monitor-logs` | pre_tp_fires.by_symbol + quiet_scalp_block.by_symbol |
| Pair classifier (MAJOR/MIDCAP/ALTCOIN) | `src/pair_manager.py::classify_pair_tier` | Volume-based; already used in SL scaling |
| Pair universe + tier promotion | `src/pair_manager.py` | TIER1/TIER2/TIER3 promotion logic |
| Soft-penalty hook for symbol class | `src/scanner/__init__.py` post-evaluator block | Where a per-symbol modifier would attach |
| Tunables | `config/__init__.py` | Where a curated-list path or env flag would land |

---

## Open questions for the owner

1. **Class A operational definition** — curated list, heuristic, or self-supervising? (My recommendation: curated A1 first.)
2. **Tokenized-stock pairs** — should they be hard-blocked (remove from universe) or soft-blocked (added to symbol-blocklist gate)?
3. **Class D (newer listings) cutoff** — 90 days? 60? 180?
4. **Acceptable signal-volume floor** — at what point would a symbol filter reduce signal count too much for subscriber retention? Currently 100 signals/24h ≈ 4/hour.
5. **Sequencing** — implement Class A+B together, or one at a time with measurement in between?
