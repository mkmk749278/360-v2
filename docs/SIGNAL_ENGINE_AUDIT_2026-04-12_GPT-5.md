# Signal Engine Audit — 2026-04-12

## 1. Executive judgment

The engine is **not yet cleanly trustworthy as a full institutional-grade portfolio on fresh redeploy**.

My blunt read:

- There **are several genuinely strong paths** in here.
- But the engine you think you have is **not the engine you are actually deploying**.
- The biggest issue is **not evaluator quality alone**. It is the **funnel/scoring architecture**:
  - PR09 scoring heavily favors sweep/MSS-style structure
  - many active non-sweep paths are under-scored by design
  - `360_SCALP` still requires `min_confidence=80`
  - `65-79` is labeled **B**, but B-tier signals are suppressed while `50-64` WATCHLIST signals are allowed through
- Result: several paths that are marked as active/core/support are, in practice, **overblocked, under-ranked, or effectively non-contributing**.

So the answer is:

- **The engine has strong pieces**
- **The live portfolio architecture is still misaligned**
- **Another correction pass should happen before fresh VPS reinstall/deploy**

---

## 2. Full active path inventory

### Live-published active paths on `main`
`360_SCALP` is enabled by default, and these evaluator paths are wired in `src/channels/scalp.py` and called from `ScalpChannel.evaluate()`:

1. `LIQUIDITY_SWEEP_REVERSAL` — `src/channels/scalp.py:_evaluate_standard`
2. `TREND_PULLBACK_EMA` — `src/channels/scalp.py:_evaluate_trend_pullback`
3. `LIQUIDATION_REVERSAL` — `src/channels/scalp.py:_evaluate_liquidation_reversal`
4. `WHALE_MOMENTUM` — `src/channels/scalp.py:_evaluate_whale_momentum`
5. `VOLUME_SURGE_BREAKOUT` — `src/channels/scalp.py:_evaluate_volume_surge_breakout`
6. `BREAKDOWN_SHORT` — `src/channels/scalp.py:_evaluate_breakdown_short`
7. `SR_FLIP_RETEST` — `src/channels/scalp.py:_evaluate_sr_flip_retest`
8. `FUNDING_EXTREME_SIGNAL` — `src/channels/scalp.py:_evaluate_funding_extreme`
9. `QUIET_COMPRESSION_BREAK` — `src/channels/scalp.py:_evaluate_quiet_compression_break`
10. `DIVERGENCE_CONTINUATION` — `src/channels/scalp.py:_evaluate_divergence_continuation`
11. `CONTINUATION_LIQUIDITY_SWEEP` — `src/channels/scalp.py:_evaluate_continuation_liquidity_sweep`
12. `POST_DISPLACEMENT_CONTINUATION` — `src/channels/scalp.py:_evaluate_post_displacement_continuation`
13. `FAILED_AUCTION_RECLAIM` — `src/channels/scalp.py:_evaluate_failed_auction_reclaim`

### Present in code but not live-active on `main`
- `OPENING_RANGE_BREAKOUT` — implemented, but **disabled by default** and explicitly acknowledged as not institutional-grade yet
- `360_SCALP_FVG`, `360_SCALP_ORDERBLOCK`, `360_SCALP_DIVERGENCE`, `360_SCALP_CVD`, `360_SCALP_VWAP`, `360_SCALP_SUPERTREND`, `360_SCALP_ICHIMOKU` — **disabled by default**, radar-only / governance-rebuild status, not part of the trusted live portfolio

---

## 3. Path-by-path audit

### 3.1 `LIQUIDITY_SWEEP_REVERSAL`
- **Location:** `src/channels/scalp.py:_evaluate_standard`
- **Thesis:** Recent liquidity sweep, momentum confirms reversal, EMA/MACD/MTF alignment tries to avoid blind fade entries.
- **Regime fit:** Best in trend/breakout/volatile reversal conditions. Acceptable. Less attractive in dead quiet/range chop.
- **SL review:** Good at evaluator level: stop anchored just beyond swept level with minimum ATR floor. Thesis-valid.
- **TP review:** Evaluator TP logic is decent (FVG first, then swing, then extension), but downstream risk-plan rewrites it into generic reversal ratios. That is a quality downgrade.
- **Funnel/scanner review:**
  - SMC gate treatment is correct
  - trend gate treatment is correct
  - but it gets **double MTF pressure**: path-level MTF plus scanner-level hard MTF
  - same-symbol arbitration will often let this path beat more nuanced paths because it scores better under PR09
- **Business-quality judgment:** Coherent, tradeable, one of the few paths that still resembles a live institutional scalp trigger.
- **Deploy verdict:** **Good but needs refinement**
- **Recommended action:** Keep active; preserve evaluator TP geometry or intentionally redesign it; remove redundant MTF pressure.

### 3.2 `TREND_PULLBACK_EMA`
- **Location:** `src/channels/scalp.py:_evaluate_trend_pullback`
- **Thesis:** Textbook trend pullback into EMA9/EMA21 with trend alignment, neutral RSI, rejection candle, and SMC support.
- **Regime fit:** Correct. This belongs in directional trend regimes only.
- **SL review:** Acceptable, not elite. Beyond EMA21 is logical, but still indicator-anchored rather than true structural invalidation.
- **TP review:** Good. Swing target + 4h target + extension is coherent for a continuation path.
- **Funnel/scanner review:**
  - SMC exemption is correct
  - risk-plan preservation is correct
  - predictive bypass is correct
  - **PR09 treatment is wrong**: no regime-affinity support, almost no SMC score unless incidental context appears
  - with `min_confidence=80`, this path is **mathematically close to dead unless it inherits extra sweep/MSS baggage that is not its own thesis**
- **Business-quality judgment:** The setup itself is strong and belongs in a serious engine.
- **Deploy verdict:** **Effectively inactive / blocked / not contributing**
- **Recommended action:** Keep in portfolio, but fix scoring/funnel before trusting redeploy; otherwise it is mostly a paper path.

### 3.3 `LIQUIDATION_REVERSAL`
- **Location:** `src/channels/scalp.py:_evaluate_liquidation_reversal`
- **Thesis:** Fast cascade, CVD absorption, RSI extreme, nearby structure, and volume spike = exhaustion reversal.
- **Regime fit:** Conceptually best in panic/flush conditions. That part is right.
- **SL review:** Evaluator SL is good: beyond cascade extremum plus buffer.
  Current system problem: downstream risk-plan does **not preserve it**.
- **TP review:** Generic downstream mean-reversion ratios are acceptable, but not especially sharp.
- **Funnel/scanner review:**
  - SMC exemption correct
  - trend exemption correct
  - scanner MTF hard gate is thesis-mismatched for reversal entries
  - path is also penalized by PR09 because its edge is not sweep/MSS-centric
- **Business-quality judgment:** Valid specialist idea, but the implementation is still crude: hard-coded 3-candle/2% cascade logic is not volatility-normalized.
- **Deploy verdict:** **Usable but questionable**
- **Recommended action:** Keep only as support; refine before redeploy; preserve evaluator SL and make the trigger ATR/regime-aware.

### 3.4 `WHALE_MOMENTUM`
- **Location:** `src/channels/scalp.py:_evaluate_whale_momentum`
- **Thesis:** Whale/tick-flow impulse with dominant side control and optional order-book confirmation.
- **Regime fit:** Specialist path for fast tape-driven moves. Acceptable.
- **SL review:** Good at evaluator level: recent 1m swing invalidation is appropriate for an order-flow impulse.
  Bad system interaction: downstream risk-plan can rewrite it.
- **TP review:** Generic downstream momentum ratios are acceptable, but not truly order-flow-specific.
- **Funnel/scanner review:**
  - SMC exemption correct
  - trend exemption correct
  - scanner MTF gate still mismatches this path
  - if order book is absent, path is allowed with penalty; operationally pragmatic, but trust falls
- **Business-quality judgment:** Interesting specialist path, but not clean enough to be a core institutional signal.
- **Deploy verdict:** **Usable but questionable**
- **Recommended action:** Keep as specialist only; preserve evaluator SL/TP or accept that it is only semi-structural.

### 3.5 `VOLUME_SURGE_BREAKOUT`
- **Location:** `src/channels/scalp.py:_evaluate_volume_surge_breakout`
- **Thesis:** Real breakout on surge volume, then controlled retest below the broken level.
- **Regime fit:** Correct. Good in trend/expansion/volatile conditions; correctly blocked in QUIET.
- **SL review:** Good. Slightly fixed-width, but still directly tied to the broken level. Acceptable business-grade construction.
- **TP review:** Good. Measured-move targets from prior range are coherent and preserved downstream.
- **Funnel/scanner review:**
  - SMC exemption correct
  - trend gate alignment correct
  - quiet handling correct
  - PR09 still underweights pure breakout structure unless MSS/sweep also exist, but this path can still survive
- **Business-quality judgment:** One of the strongest live paths.
- **Deploy verdict:** **Strong / trust for redeploy**
- **Recommended action:** Keep active. This is safe to carry into a clean deploy.

### 3.6 `BREAKDOWN_SHORT`
- **Location:** `src/channels/scalp.py:_evaluate_breakdown_short`
- **Thesis:** Bearish mirror of volume-surge breakout: genuine support failure, then dead-cat bounce into continuation short.
- **Regime fit:** Correct. Strong in bearish trend/expansion/volatile tape.
- **SL review:** Good. Above broken level; structurally coherent.
- **TP review:** Good. Measured-move downside targets are coherent and preserved.
- **Funnel/scanner review:**
  - SMC exemption correct
  - trend gate alignment correct
  - good fit with directional short environments
  - still somewhat score-dependent on incidental structure, but less broken than many other paths
- **Business-quality judgment:** Strong path. One of the best bearish paths in the engine.
- **Deploy verdict:** **Strong / trust for redeploy**
- **Recommended action:** Keep active. Safe for clean redeploy.

### 3.7 `SR_FLIP_RETEST`
- **Location:** `src/channels/scalp.py:_evaluate_sr_flip_retest`
- **Thesis:** Confirmed support/resistance role flip, then retest with rejection candle.
- **Regime fit:** Conceptually correct across trend/range transition states; correct to block in pure volatility.
- **SL review:** Good. Just beyond flipped level; thesis-valid.
- **TP review:** Good. Swing target + 4h target is coherent.
- **Funnel/scanner review:**
  - structural path is good
  - risk-plan preservation is good
  - but PR09 treats it badly: low SMC, no regime-affinity help
  - arbitration likely suppresses it behind sweep-heavy setups
- **Business-quality judgment:** Strong institutional-style setup.
- **Deploy verdict:** **Effectively inactive / blocked / not contributing**
- **Recommended action:** Keep it, but fix scoring before redeploy. Right now it is better on paper than in live flow.

### 3.8 `FUNDING_EXTREME_SIGNAL`
- **Location:** `src/channels/scalp.py:_evaluate_funding_extreme`
- **Thesis:** Contrarian funding extreme with price/RSI/CVD confirmation and structural context.
- **Regime fit:** Too permissive. Funding extremes can persist; not every extreme is fadeable.
- **SL review:** Mixed. If liquidation-cluster data is real and nearby, SL is good. If not, it collapses to ATR fallback and loses specificity. Then downstream risk-plan may rewrite anyway.
- **TP review:** TP1 improvement is good; TP2/TP3 are generic.
- **Funnel/scanner review:**
  - SMC exemption correct
  - trend exemption correct
  - scanner MTF gate still mismatches the fade thesis
  - funding also gets additional downstream funding boost/penalty logic, which risks double-counting a thesis already embedded in the evaluator
- **Business-quality judgment:** Specialist only; not a path I would promote as a top-trust institutional engine component in current form.
- **Deploy verdict:** **Usable but questionable**
- **Recommended action:** Deprioritize unless refined. If kept, preserve evaluator SL and tighten regime restrictions.

### 3.9 `QUIET_COMPRESSION_BREAK`
- **Location:** `src/channels/scalp.py:_evaluate_quiet_compression_break`
- **Thesis:** BB squeeze in quiet/ranging market, then release with MACD, volume, RSI, and structure confirmation.
- **Regime fit:** Correct.
- **SL review:** Good. Opposite band invalidation matches the setup.
- **TP review:** Good. Band-width targets match the thesis.
- **Funnel/scanner review:**
  - quiet exemption exists, which is correct
  - but PR09 gives it very little structural/regime credit
  - generic MTF/trend logic is not really designed for a squeeze-release starter path
  - with current scoring thresholds this path is **close to non-actionable**
- **Business-quality judgment:** Valid specialist path.
- **Deploy verdict:** **Effectively inactive / blocked / not contributing**
- **Recommended action:** Keep only if you fix scoring. Otherwise it is basically decorative.

### 3.10 `DIVERGENCE_CONTINUATION`
- **Location:** `src/channels/scalp.py:_evaluate_divergence_continuation`
- **Thesis:** Hidden CVD divergence inside a trend, near EMA21, with structure support.
- **Regime fit:** Correct: trending only.
- **SL review:** Evaluator SL is acceptable, but not preserved downstream.
- **TP review:** Evaluator TP logic is decent; downstream generic handling weakens it.
- **Funnel/scanner review:**
  - SMC exemption correct
  - trend gate alignment is acceptable
  - PR09 family adjustment helps, but not enough
  - still under-scored versus sweep paths
  - arbitration likely suppresses it when a sweep-style path exists on the same symbol/direction
- **Business-quality judgment:** The thesis is coherent and useful as a support path.
- **Deploy verdict:** **Effectively inactive / blocked / not contributing**
- **Recommended action:** Keep conceptually; fix scoring and preserve evaluator risk geometry.

### 3.11 `CONTINUATION_LIQUIDITY_SWEEP`
- **Location:** `src/channels/scalp.py:_evaluate_continuation_liquidity_sweep`
- **Thesis:** Trend already exists, local stop-hunt cleans the path, price reclaims, continuation resumes.
- **Regime fit:** Very good. Correctly blocked in quiet/range/chaotic regimes.
- **SL review:** Strong. Beyond sweep level plus ATR buffer is directly thesis-valid.
- **TP review:** Good. FVG first, swing second, extension third; preserved downstream.
- **Funnel/scanner review:**
  - SMC gate alignment is strong
  - trend gate alignment is strong
  - PR09 regime affinity and family-thesis adjustment both support it
  - one of the few paths where evaluator, scorer, and risk-plan are actually pulling in the same direction
- **Business-quality judgment:** Best-in-class path in this engine.
- **Deploy verdict:** **Strong / trust for redeploy**
- **Recommended action:** Keep active. This is one of the safest paths in the system.

### 3.12 `POST_DISPLACEMENT_CONTINUATION`
- **Location:** `src/channels/scalp.py:_evaluate_post_displacement_continuation`
- **Thesis:** Strong displacement, quiet absorption, then breakout from consolidation in the same direction.
- **Regime fit:** Correct. Good continuation/expansion path.
- **SL review:** Strong. Beyond consolidation range is exactly right.
- **TP review:** Strong. Measured move from displacement height is coherent and preserved.
- **Funnel/scanner review:**
  - evaluator quality is good
  - risk-plan protection is good
  - predictive bypass is good
  - but PR09 treats it badly: low SMC, no regime-affinity support, no thesis adjustment
  - as a result, a genuinely good path is largely score-starved
- **Business-quality judgment:** This is a serious path design.
- **Deploy verdict:** **Effectively inactive / blocked / not contributing**
- **Recommended action:** Keep, but fix scoring before redeploy. This should be core, not dead.

### 3.13 `FAILED_AUCTION_RECLAIM`
- **Location:** `src/channels/scalp.py:_evaluate_failed_auction_reclaim`
- **Thesis:** Price probes beyond obvious structure, fails to accept, then reclaims back inside range.
- **Regime fit:** Good. Correctly blocked in the worst volatility/strong-trend contexts.
- **SL review:** Excellent. Beyond failed-auction wick extreme is one of the cleanest invalidation models in the engine.
- **TP review:** Good. Tail/measured-move projection is coherent and preserved.
- **Funnel/scanner review:**
  - SMC exemption correct
  - trend exemption correct
  - but scanner MTF gate is still not thesis-aware
  - PR09 gives it very little help despite the path being structurally sound
- **Business-quality judgment:** Strong support/specialist path; one of the better structural designs in the codebase.
- **Deploy verdict:** **Effectively inactive / blocked / not contributing**
- **Recommended action:** Keep and prioritize scoring repair. This path deserves live capital more than the current funnel allows.

---

## 4. Cross-path findings

### Strongest paths
- `CONTINUATION_LIQUIDITY_SWEEP`
- `VOLUME_SURGE_BREAKOUT`
- `BREAKDOWN_SHORT`
- `LIQUIDITY_SWEEP_REVERSAL` (good path, but downstream geometry is weaker than it should be)

### Weakest paths
Weakest as currently deployed, not necessarily as ideas:
- `QUIET_COMPRESSION_BREAK`
- `POST_DISPLACEMENT_CONTINUATION`
- `FAILED_AUCTION_RECLAIM`
- `TREND_PULLBACK_EMA`
- `SR_FLIP_RETEST`
These are not weak ideas. They are **weakly represented by the live funnel**.

### Paths with best SL design
- `FAILED_AUCTION_RECLAIM`
- `POST_DISPLACEMENT_CONTINUATION`
- `CONTINUATION_LIQUIDITY_SWEEP`
- `SR_FLIP_RETEST`

### Paths with weakest SL design
- `TREND_PULLBACK_EMA` (indicator-anchored, not truly structural)
- `FUNDING_EXTREME_SIGNAL` (good only when liquidation-cluster data is good)
- `LIQUIDATION_REVERSAL` / `WHALE_MOMENTUM` (evaluator SLs are decent, but downstream rewriting damages them)

### Paths with best TP design
- `VOLUME_SURGE_BREAKOUT`
- `BREAKDOWN_SHORT`
- `POST_DISPLACEMENT_CONTINUATION`
- `FAILED_AUCTION_RECLAIM`

### Paths with weakest TP design
- `LIQUIDITY_SWEEP_REVERSAL` in live flow, because evaluator TP logic gets flattened downstream
- `WHALE_MOMENTUM`
- `FUNDING_EXTREME_SIGNAL`
- `DIVERGENCE_CONTINUATION`

### Paths likely overblocked
- `TREND_PULLBACK_EMA`
- `SR_FLIP_RETEST`
- `POST_DISPLACEMENT_CONTINUATION`
- `FAILED_AUCTION_RECLAIM`
- `QUIET_COMPRESSION_BREAK`
- `DIVERGENCE_CONTINUATION`
- `LIQUIDATION_REVERSAL`
- `WHALE_MOMENTUM`

### Paths likely too noisy if you loosen the funnel without redesign
- `FUNDING_EXTREME_SIGNAL`
- `LIQUIDATION_REVERSAL`
- `WHALE_MOMENTUM`

### Duplicated / overlapping paths
- `LIQUIDITY_SWEEP_REVERSAL`, `CONTINUATION_LIQUIDITY_SWEEP`, `FAILED_AUCTION_RECLAIM`, and `SR_FLIP_RETEST` all compete around structure reclaim / rejection / sweep resolution
- `VOLUME_SURGE_BREAKOUT` and `POST_DISPLACEMENT_CONTINUATION` both attack continuation after directional expansion, but at different phases
- The current same-direction arbitration means overlap is not just conceptual; it is portfolio-shaping

### Scoring inconsistencies
This is the biggest system problem.
- PR09 regime-affinity coverage is incomplete for active paths
- SMC score strongly rewards sweep/MSS structure, even for explicitly exempt non-sweep paths
- Several active paths can only reach strong publishable scores if they inherit **incidental** sweep/MSS context that is not part of their own thesis
- `360_SCALP min_confidence = 80` creates a **B-tier dead zone**:
  - `80+` = publishable
  - `65-79` = labeled B but suppressed
  - `50-64` = WATCHLIST and allowed
- That is not business-clean architecture

### Portfolio-role inconsistencies
- `TREND_PULLBACK_EMA`, `POST_DISPLACEMENT_CONTINUATION`, and `SR_FLIP_RETEST` are marked as **core**, but the funnel treats them like second-class citizens
- `FAILED_AUCTION_RECLAIM` is a good support path, but live scoring suppresses it too hard
- `OPENING_RANGE_BREAKOUT` still exists in role mapping while explicitly disabled and acknowledged as not production-grade

### Architecturally unfinished / suspect areas
- ORB is knowingly unfinished and disabled
- auxiliary paid channels are disabled pending governance rebuild
- evaluator-level confidence boosts are largely cosmetic because scanner scoring overwrites them
- predictive confidence adjustments are mostly overwritten by later composite scoring
- risk-plan preservation is inconsistent across active paths

---

## 5. Pre-redeploy action list

### 1. Absolutely must be corrected before fresh VPS reinstall/deploy
1. **Fix the scoring/funnel mismatch**
   - active paths cannot remain “core/support” on paper while being practically dead in live scoring
   - either lower `360_SCALP` publish threshold or make PR09 actually score these paths on their own thesis
2. **Make MTF gating thesis-aware**
   - reversal and structural-reclaim paths should not be hard-blocked by generic trend-alignment logic
3. **Preserve evaluator-authored SL/TP on the remaining unprotected live paths**
   - especially `LIQUIDITY_SWEEP_REVERSAL`, `LIQUIDATION_REVERSAL`, `WHALE_MOMENTUM`, `FUNDING_EXTREME_SIGNAL`, `DIVERGENCE_CONTINUATION`
4. **Resolve the B-tier dead-zone architecture**
   - right now the confidence ladder is business-illogical

### 2. Should ideally be refined before redeploy
1. Volatility-normalize `LIQUIDATION_REVERSAL`
2. Tighten regime logic for `FUNDING_EXTREME_SIGNAL`
3. Review arbitration bias so sweep-style paths do not mechanically dominate every same-direction symbol decision
4. Decide whether `WHALE_MOMENTUM` without order-book confirmation is truly acceptable in production

### 3. Can wait until after fresh deployment
1. Auxiliary disabled channel rebuild
2. ORB rebuild
3. Cosmetic confidence-boost cleanup and dead-score code cleanup
4. Diagnostics/inventory helper cleanup

### 4. Paths safe to trust immediately after a clean deploy
If you had to trust some paths today:
- `CONTINUATION_LIQUIDITY_SWEEP`
- `VOLUME_SURGE_BREAKOUT`
- `BREAKDOWN_SHORT`
- `LIQUIDITY_SWEEP_REVERSAL` (with caveat: downstream TP/risk handling is weaker than it should be)

---

## 6. Final deploy recommendation

**Redeploy only after one more correction pass**

### Why
Because the issue is not “the engine has no good setups.”
The issue is: **the live funnel does not faithfully express the good setups it already has.**

Right now:
- a few paths are strong and redeployable
- several other good paths are being mis-scored, overblocked, or risk-distorted
- the portfolio on paper is broader and better than the portfolio actually emitted live

For a normal retail bot, that might be acceptable.

For the stated goal — **best possible institutional-grade, trustworthy signal engine** — it is not yet acceptable.

My business-first conclusion:

- **Good engine base**
- **Strong top subset**
- **Portfolio architecture still dishonest to its own intent**
- **Do one more correction pass before fresh VPS reinstall/deploy**
