# 1. Executive truth

## Bottom line

The current live scoring calculation is **not good enough** for a high-integrity multi-path signal engine. It is not broken in the sense of being random; it is broken in the more important sense of being **strategically miscalibrated**.

The runtime path is now a **hybrid model**:

- a legacy uniform confidence model in `src/confidence.py`
- a structured but still mostly generic setup score in `score_signal_components(...)`
- a final composite scorer in `SignalScoringEngine`
- then large scanner-level soft penalties and hard gates in `src/scanner/__init__.py`

That stack is mathematically coherent, but it is **not sufficiently thesis-faithful by path**. In practice, too many materially different setups are still being judged by the same generic dimensions:

- SMC presence
- regime affinity
- last-candle volume
- EMA / RSI / MACD confluence
- generic pattern score
- generic MTF score

That is acceptable for some paths. It is **architecturally wrong** for reclaim / retest, failed-auction, and displacement-continuation paths, and only partially corrected for sweep-reversal / sweep-continuation paths.

## Confirmed implementation truth

1. The final runtime confidence that decides FILTERED vs WATCHLIST vs paid is set in `src/scanner/__init__.py`, not in `src/confidence.py`.
2. `src/confidence.py` is only an upstream input layer now. Its adaptive threshold code exists, but it is **not the authoritative live decision gate** for the active scanner path.
3. `score_signal_components(...)` is also not the final scoring authority. Its result is later overwritten by `SignalScoringEngine.score(...)`, although its `market` / `execution` / `risk` components still survive as downstream floor checks.
4. Final tiering is effectively:
   - `<50` → FILTERED
   - `50–64` → WATCHLIST
   - `65–79` → B-tier paid
   - `>=80` → A+ paid
   via `classify_signal_tier()` in `src/scanner/__init__.py:444-463`, plus router handling in `src/signal_router.py:482-489,896-918`.

## Runtime / business truth

Per the task context, the system is currently producing 250+ WATCHLIST alerts in 24 hours while paid conversion remains weak. That is not an “engine alive” problem. It is a **conversion architecture** problem: the system is expressing setup formation upstream, but the scoring / penalty / threshold stack is not converting enough real candidates into paid signals.

## Architectural truth

The engine now needs **stronger family-aware scoring**, and in a few cases **true path-specific thesis scoring**.

The next correct move is **not** broad threshold loosening.

The next correct move is:

1. **family-aware / path-aware scoring correction**
2. **targeted soft-penalty rebalance**
3. keep global quality discipline and tier thresholds broadly intact

Threshold rebalance should be secondary and narrow, not the lead correction.

---

# 2. Current scoring architecture — what actually happens at runtime

## 2.1 Authoritative runtime path

The authoritative live path is in `Scanner._prepare_signal(...)` in `src/scanner/__init__.py:2413-3390`.

The runtime order is:

1. evaluator builds a path-specific signal (`src/channels/scalp.py`)
2. setup classification via `classify_setup(...)`
3. execution assessment via `execution_quality_check(...)`
4. risk plan via `build_risk_plan(...)`
5. scanner-level hard/soft gates
6. legacy base confidence from `src/confidence.py`
7. predictive adjustments
8. `score_signal_components(...)`
9. pattern / candlestick / MTF modifiers
10. `SignalScoringEngine.score(...)` overwrites confidence again
11. evaluator + scanner soft penalties deducted
12. stat filter / pair-analysis penalties
13. hard SMC / trend gates
14. QUIET gate
15. WATCHLIST or paid/final filter handling

## 2.2 What `src/confidence.py` really does now

`Scanner._compute_base_confidence(...)` calls:

- `score_smc(...)`
- `score_trend(...)`
- `score_liquidity(...)`
- `score_spread(...)`
- `score_data_sufficiency(...)`
- `score_multi_exchange(...)`
- `score_onchain(...)`
- `score_order_flow(...)`
- `compute_confidence(...)`

Relevant files:

- `src/scanner/__init__.py:2141-2260`
- `src/confidence.py:117-385,588-671`

Important facts:

- all SCALP channels use the same flat weights (`_SCALP_DEFAULT_WEIGHTS`) in `src/confidence.py:70-84`
- `compute_confidence(...)` is therefore basically a **uniform raw-sum model** for SCALP
- `compute_adaptive_threshold(...)` exists in `src/confidence.py:687-752`, but the live scanner path does **not** use it as the final acceptance threshold
- `compute_per_signal_confidence(...)` / `build_confidence_metadata(...)` are also not the final live gate for the active scanner route

So `src/confidence.py` is currently **upstream context scoring**, not the final live score authority.

## 2.3 What `score_signal_components(...)` really does now

`score_signal_components(...)` in `src/signal_quality.py:1383-1433` creates:

- `market` (pair quality scaled to 25)
- `setup` (mostly generic setup/regime/channel compatibility)
- `execution` (trigger + extension)
- `risk` (R multiple)
- `context` (10% of legacy confidence, cross-verify adjustment)

This result is written onto the signal in `src/scanner/__init__.py:2878-2896`.

But it is **not final**. Later, the composite engine overwrites `sig.confidence` with a different total.

What remains important from this layer:

- `market`
- `execution`
- `risk`

because they survive in `sig.component_scores` and are later used as floor checks in `src/scanner/__init__.py:3375-3379`.

## 2.4 What `SignalScoringEngine` really decides

`SignalScoringEngine.score(...)` in `src/signal_quality.py:1474-1815` is the final structured scoring authority before post-score deductions.

It scores:

- `smc` max 25
- `regime` max 20
- `volume` max 15
- `indicators` max 20
- `patterns` max 10
- `mtf` max 10
- `thesis_adj` variable

That total overwrites confidence in `src/scanner/__init__.py:3057-3144`.

This is the most important scoring fact in the repo.

## 2.5 Where path-awareness currently exists

There is some path/family awareness, but it is limited:

1. **MTF family policy caps**  
   `src/scanner/__init__.py:341-373,2505-2514`

2. **SMC hard-gate exemptions**  
   `src/scanner/__init__.py:248-286`

3. **Trend hard-gate exemptions**  
   `src/scanner/__init__.py:288-301`

4. **Family thesis adjustment inside `SignalScoringEngine`**  
   only for:
   - reversal / liquidation family
   - divergence family
   - sweep-continuation family  
   `src/signal_quality.py:1683-1815`

This means the current architecture is **not globally uniform anymore**, but it is also **not genuinely path-aware enough**.

## 2.6 What finally determines FILTERED / WATCHLIST / paid

### FILTERED

A signal becomes FILTERED if any of these happen:

- setup / execution / risk hard fail  
  `src/scanner/__init__.py:2458-2474,2786-2799`
- MTF hard gate fail  
  `src/scanner/__init__.py:2493-2556`
- composite score `<50`  
  `src/scanner/__init__.py:3112-3136`
- stat filter suppresses  
  `src/scanner/__init__.py:3166-3188`
- pair analysis CRITICAL suppresses  
  `src/scanner/__init__.py:3195-3221`
- SMC hard gate fails  
  `src/scanner/__init__.py:3236-3271`
- trend hard gate fails  
  `src/scanner/__init__.py:3273-3300`
- QUIET scalp block fails  
  `src/scanner/__init__.py:3320-3360`
- post-score confidence `< min_conf`, or `market < 12`, or `execution < 10`, or `risk < 10`  
  `src/scanner/__init__.py:3375-3387`

### WATCHLIST

WATCHLIST is not a separate scoring model. It is just the band:

- `50–64` after scoring + penalties + reclassification  
  `src/scanner/__init__.py:3162-3165,3361-3373`

### B-tier paid

- `65–79`
- must also survive all later gates and floor checks
- router then applies static channel min-confidence again  
  `src/signal_router.py:632-642`

### A+ paid

- `>=80`
- same downstream gates still apply

### Important router truth

WATCHLIST signals are short-circuited to free only in `src/signal_router.py:482-489,896-918`.

That means WATCHLIST candidates:

- do **not** enter paid lifecycle
- do **not** get correlation lock / trade monitor lifecycle
- and, critically, they bypass later router AI enrichment because the short-circuit happens first

---

# 3. Is the scoring calculation good or not?

No.

It is **coherent but still miscalibrated**.

## Why it is not good enough

### 3.1 The dominant final model is still mostly generic

The final composite score is dominated by generic dimensions in `SignalScoringEngine`:

- SMC
- regime
- volume
- indicators
- patterns
- MTF

That is a fine backbone for a simple engine. It is not enough for a live multi-path engine whose paths express different theses:

- pullback continuation
- reclaim/retest
- failed auction reclaim
- displacement continuation
- reversal after sweep/liquidation
- breakout on participation

Those are not the same thesis.

### 3.2 Family correction is too narrow and too weak

Only three families receive thesis adjustment in `src/signal_quality.py:1732-1811`:

- reversal / liquidation
- divergence
- sweep continuation

Everything else gets `0` thesis adjustment, including:

- `TREND_PULLBACK_EMA`
- `SR_FLIP_RETEST`
- `VOLUME_SURGE_BREAKOUT`
- `POST_DISPLACEMENT_CONTINUATION`
- `FAILED_AUCTION_RECLAIM`

That is the core structural miss.

### 3.3 Soft penalties are large enough to dominate the entire architecture

Base soft penalties for `360_SCALP` are:

- VWAP: 15
- kill zone: 10
- OI: 8
- volume divergence: 12
- cluster: 10
- spoof: 12  
  `src/scanner/__init__.py:404-416`

Then they are multiplied by regime:

- trending: `0.6`
- volatile: `1.5`
- quiet scalp: `1.8`  
  `src/scanner/__init__.py:303-324,2570-2576`

So in quiet scalp, a single VWAP penalty becomes **27 points**. A single volume-divergence penalty becomes **21.6 points**.

That is not a gentle soft-penalty layer. That is a **score-dominating second scoring system**.

### 3.4 The architecture still over-rewards the wrong generic proxies

The strongest generic biases are:

- last-candle volume as a universal conviction proxy
- EMA alignment as a universal path health proxy
- regime-affinity table that does not fully cover all valid path/regime relationships

Those are not universally wrong. They are wrong when elevated into shared final scoring for paths whose edge is:

- structural reclaim
- rejection quality
- failed acceptance
- displacement + absorption + re-acceleration

---

# 4. Are all paths scored too uniformly?

## Verdict

The current system is **hybrid but still biased**, not genuinely family-aware.

## Why

### Uniform parts

1. `src/confidence.py` uses flat SCALP weights for all scalp channels  
   `src/confidence.py:70-84`
2. `SignalScoringEngine` uses the same six base dimensions for almost every setup  
   `src/signal_quality.py:1475-1566`
3. scanner soft penalties are generic and mostly family-agnostic  
   `src/scanner/__init__.py:2578-2780`

### Partial corrections

1. family MTF caps
2. some gate exemptions
3. limited thesis adjustment for 3 families

### Why that still leaves structural bias

Because the shared model still carries most of the score mass, while family correction is only a small additive patch. The architecture still says, in effect:

> “All setups are mainly SMC + regime + volume + indicators + patterns + MTF, and a few special cases get a small afterthought bonus.”

That is exactly the wrong hierarchy for several live setup families.

---

# 5. Which paths are under-credited and why

## Summary verdict by path

| Path | Runtime thesis | Current verdict |
|---|---|---|
| `TREND_PULLBACK_EMA` | orderly trend pullback into EMA value with rejection | **under-credited** |
| `SR_FLIP_RETEST` | confirmed role-change retest with structural rejection | **strongly under-credited** |
| `FAILED_AUCTION_RECLAIM` | failed acceptance beyond level, then reclaim back inside | **severely under-credited** |
| `CONTINUATION_LIQUIDITY_SWEEP` | sweep-reclaim continuation in trend direction | **closest to fairly scored**, still imperfect |
| `LIQUIDITY_SWEEP_REVERSAL` | sweep / exhaustion reversal | **partially corrected but still under-credited in range regimes** |
| `VOLUME_SURGE_BREAKOUT` | real breakout participation + retest continuation | **moderately under-credited** |
| `POST_DISPLACEMENT_CONTINUATION` | displacement → absorption → re-acceleration | **strongly under-credited** |

## 5.1 `TREND_PULLBACK_EMA`

### Real thesis

Price is not supposed to explode. It is supposed to:

- already be in a trend
- pull back into EMA value
- reject from value
- continue with controlled structure

Source: `src/channels/scalp.py:619-760`

### What currently rewards it

- `indicators` score: EMA/RSI/MACD
- `regime` score when trend regime matches
- execution anchor via EMA in `execution_quality_check(...)`

### What fails to reflect it

- no dedicated thesis adjustment
- SMC score can be structurally low because this path does not require sweep/MSS
- last-candle volume is a weak proxy for a pullback-quality thesis
- path-specific pullback quality is not scored directly

### Verdict

The system understands “trend exists” better than it understands “pullback was good.” That under-credits the actual path edge.

## 5.2 `SR_FLIP_RETEST`

### Real thesis

This is a structural level trade:

- prior swing broken
- role changed
- price retests that exact level
- rejection wick/body confirms hold

Source: `src/channels/scalp.py:1746-1985`

### What currently rewards it

- execution anchor near the flipped level
- generic regime/indicator scoring if EMAs support the move
- SMC hard-gate exemption prevents outright structural misclassification

### What fails to reflect it

- composite scoring does **not** directly score retest proximity
- composite scoring does **not** directly score rejection wick quality
- composite scoring does **not** directly score role-change confirmation
- no family thesis adjustment
- volume score is not a reliable proxy for this setup

### Verdict

`SR_FLIP_RETEST` is being pushed through a trend/volume model when its real edge is structural precision. That is a strong under-credit.

## 5.3 `FAILED_AUCTION_RECLAIM`

### Real thesis

This is a failed acceptance / reclaim trade:

- obvious level probed
- acceptance fails
- price reclaims back inside structure
- reclaim magnitude confirms rejection

Source: `src/channels/scalp.py:3134-3417`

### What currently rewards it

- execution anchor uses `far_reclaim_level` in `execution_quality_check(...)`
- risk geometry preserves evaluator-authored structure
- trend hard-gate exemption stops one obvious mismatch

### What fails to reflect it

- `SignalScoringEngine._score_regime()` does **not** list `FAILED_AUCTION_RECLAIM` in its regime affinity table at all (`src/signal_quality.py:1491-1503`)
- no thesis adjustment
- no direct scoring for reclaim distance, auction-tail quality, or acceptance failure quality
- generic indicator score still includes EMA alignment even though thesis is level reclaim, not EMA trend

### Verdict

This is the most obvious scoring mismatch in the audited set. The evaluator is path-aware; the final score is not. This path is severely under-credited.

## 5.4 `CONTINUATION_LIQUIDITY_SWEEP`

### Real thesis

- trend already exists
- local counter-trend liquidity is swept
- price reclaims
- continuation resumes

Source: `src/channels/scalp.py:2544-2775`

### What currently rewards it

- strong SMC fit
- trend/indicator fit
- regime affinity explicitly includes it in trending regimes
- dedicated family thesis adjustment for aligned CVD + rising OI

### What fails to reflect it

- sweep age / reclaim quality only appear as evaluator soft penalties, not dedicated positive scoring
- still exposed to generic volume/penalty stack

### Verdict

This is one of the few paths that the current model actually tries to understand. It is the closest thing to fairly scored in the live stack.

## 5.5 `LIQUIDITY_SWEEP_REVERSAL`

### Real thesis

- liquidity sweep
- exhaustion / reclaim
- often counter-trend at entry
- order-flow and liquidation behavior matter

### What currently rewards it

- strong SMC scoring
- reversal-family thesis adjustment
- order-flow components materially help it

### What fails to reflect it

- `_score_regime()` rewards it in trending/volatile lists, but not in ranging states even though `classify_setup()` allows it in clean/dirty range contexts (`src/signal_quality.py:273-300,1491-1503`)
- this means range-valid reversal setups can still receive only the “setup not optimal” regime score
- it does **not** receive a trend hard-gate exemption in `src/scanner/__init__.py:288-301`, so a reversal path that is only partially through EMA realignment can still be judged by a generic indicator floor after already being only partially corrected in the composite scorer

### Verdict

This path is no longer badly ignored, but it is still mis-scored in one of its natural habitats: range conditions.

## 5.6 `VOLUME_SURGE_BREAKOUT`

### Real thesis

- real participation breakout
- breakout confirmed by surge volume
- then controlled retest / continuation

Source: `src/channels/scalp.py:1157-1335`

### What currently rewards it

- volume score
- trend/indicator score
- regime affinity includes it

### What fails to reflect it

- composite volume score uses `volume_last_usd / volume_avg_usd` on the current candle, not the path’s richer breakout/retest context
- no direct scoring for pullback-zone quality or breakout-candle quality
- no thesis adjustment

### Verdict

This path is not ignored, but it is scored too much like “high-volume momentum now” and not enough like “validated breakout structure.” Moderate under-credit.

## 5.7 `POST_DISPLACEMENT_CONTINUATION`

### Real thesis

- real displacement
- tight absorption consolidation
- re-acceleration breakout

Source: `src/channels/scalp.py:2801-3117`

### What currently rewards it

- regime fit in continuation contexts
- indicator/trend score
- execution anchor via stored breakout level

### What fails to reflect it

- no direct scoring for displacement quality
- no direct scoring for consolidation tightness / absorption quality
- no direct scoring for re-acceleration quality
- no thesis adjustment
- SMC score may stay low despite path quality being high

### Verdict

This is another major under-credit path. The evaluator captures the thesis. The final scorer does not.

---

# 6. Soft-penalty / threshold interaction analysis

## 6.1 The largest score-compression mechanism is post-score penalties

The most dangerous architecture feature is that large scanner penalties are applied **after** composite scoring:

- evaluator `soft_penalty_total`
- scanner `soft_penalty`
- then deducted from final score  
  `src/scanner/__init__.py:3034-3043,3147-3165`

That means even a structurally good composite score can be pushed into WATCHLIST or FILTERED late in the funnel.

## 6.2 Which penalties are most likely converting 65+ into WATCHLIST

For `360_SCALP`, the main suspects are:

1. **VWAP extension**: 15 base  
2. **volume divergence**: 12 base  
3. **spoof**: 12 base  
4. **kill zone**: 10 base  
5. **cluster**: 10 base  
6. **pair analysis weak**: additional 8 later  

Source: `src/scanner/__init__.py:404-416,2578-2780,3219-3232`

These are especially large because:

- in volatile: multiplied by `1.5`
- in quiet scalp: multiplied by `1.8`

## 6.3 Which families are disproportionately exposed

### Reclaim / retest families

- `SR_FLIP_RETEST`
- `FAILED_AUCTION_RECLAIM`

These can be structurally valid without exceptional last-candle volume and can trigger outside ideal session windows. Generic kill-zone and VWAP extension penalties can hit them harder than is architecturally justified.

### Breakout / re-acceleration families

- `VOLUME_SURGE_BREAKOUT`
- `POST_DISPLACEMENT_CONTINUATION`

These are especially exposed to:

- VWAP extension
- volume divergence

even though controlled extension after breakout/displacement is part of the thesis, not always a contradiction.

### Reversal family

- `LIQUIDITY_SWEEP_REVERSAL`

It gets some thesis-aware help, but the generic OI gate in `src/oi_filter.py:219-326` is still family-agnostic. The gate logic is not written as a reclaim/reversal-thesis model; it is a generic signal-quality model.

## 6.4 Threshold interaction

### Global floor interaction

The scanner still ultimately uses the static channel floor:

- `min_confidence=65` for `360_SCALP`  
  `config/__init__.py:591-605`

So the practical architecture is:

1. generic final score
2. late heavy penalties
3. global 65 paid floor

That is exactly the structure that creates “good-looking WATCHLIST volume, weak paid conversion.”

### QUIET interaction

QUIET is especially harsh:

- soft penalties multiplied by `1.8`
- separate hard floor `QUIET_SCALP_MIN_CONFIDENCE = 65.0`
- only divergence gets a narrow 64.0 exemption  
  `src/scanner/__init__.py:303-313,3320-3360`  
  `config/__init__.py:1049-1054`

That is mathematically strict, but it is also evidence that the system is using threshold exceptions to patch deeper scoring mismatches.

### Adaptive threshold truth

`compute_adaptive_threshold()` exists in `src/confidence.py`, but the live active path does not rely on it for final gating. So the repo contains adaptive-threshold machinery, but the live paid conversion path is still effectively governed by:

- composite score
- penalties
- static 65 channel floor

---

# 7. Whether per-path or per-family scoring is required

## Verdict

Yes. The system now requires **stronger per-family scoring**, with a smaller amount of **true per-path thesis scoring**.

## What should remain shared

These should stay shared:

1. universal safety standards
   - geometry validity
   - stale suppression
   - spread sanity
   - hard directional sanity
   - post-risk floor checks

2. shared base scoring
   - market quality
   - some regime context
   - broad MTF context
   - generic risk quality

## What must become family-aware

### Reclaim / retest family

- `SR_FLIP_RETEST`
- `FAILED_AUCTION_RECLAIM`

Needs direct scoring for:

- level precision
- reclaim strength
- rejection candle / tail quality
- structural acceptance failure

### Breakout / continuation family

- `VOLUME_SURGE_BREAKOUT`
- `POST_DISPLACEMENT_CONTINUATION`
- `CONTINUATION_LIQUIDITY_SWEEP`

Needs direct scoring for:

- breakout quality
- pullback quality
- consolidation / absorption quality
- re-acceleration quality
- continuation energy

### Trend-pullback family

- `TREND_PULLBACK_EMA`

Needs direct scoring for:

- EMA touch quality
- pullback depth
- rejection quality
- trend cleanliness

## What must become path-specific

Only the path thesis fields that are truly unique:

- `FAILED_AUCTION_RECLAIM`: failed-acceptance + reclaim magnitude
- `POST_DISPLACEMENT_CONTINUATION`: displacement body + consolidation compression + breakout re-acceleration
- `SR_FLIP_RETEST`: role-change retest precision + rejection quality

Those should not be hidden inside generic penalties. They should be scored as positive thesis evidence.

---

# 8. Best next action

## Direct decision

The next correct move is **not** “no scoring change.”

The next correct move is a combination of:

1. **family-aware scoring correction**
2. **targeted soft-penalty rebalance**

Threshold rebalance should be narrow and secondary.

## Why this is the narrowest doctrine-safe correction

Because the root problem is not that the bar is globally too high. The root problem is that the score itself is not faithful enough to several setup theses, and then generic penalties hit those setups with outsized force.

If you loosen thresholds first, you risk admitting more weak generic candidates.

If you make the score more thesis-faithful first, you preserve discipline while improving paid conversion quality.

## What should *not* be changed first

- do **not** globally lower `MIN_CONFIDENCE_SCALP`
- do **not** globally relax WATCHLIST / B / A+ tier boundaries
- do **not** broadly shrink all penalties

That would inflate quantity without fixing the architecture.

---

# 9. Concrete recommendation for the next PR

## Recommended PR doctrine

Build a **family-aware scoring correction PR** that keeps the current universal safety rails but changes how final conviction is earned.

## Concrete scope

### A. Keep these unchanged

- paid thresholds: 65 / 80 tier boundaries
- router WATCHLIST free-only doctrine
- market / execution / risk minimum floors
- geometry and stale protection

### B. Refactor the final scorer into:

1. **shared base score**
   - market
   - baseline regime context
   - broad MTF context
   - generic risk quality

2. **family thesis score**
   - reclaim/retest
   - trend-pullback
   - breakout/continuation
   - reversal/liquidation

3. **small path-specific thesis module** for:
   - `FAILED_AUCTION_RECLAIM`
   - `SR_FLIP_RETEST`
   - `POST_DISPLACEMENT_CONTINUATION`

### C. Rebalance soft penalties narrowly

Do **not** remove them. Make them family-aware:

- reduce VWAP-extension penalty for reclaim/retest paths
- reduce or cap volume-divergence penalty for breakout/displacement paths
- review OI penalty application for reversal/reclaim families
- keep hard safety gates intact

### D. Specific architectural targets for the next PR

1. `FAILED_AUCTION_RECLAIM`
   - add direct positive score for reclaim magnitude and failed-auction tail quality
   - add regime affinity where architecturally valid

2. `SR_FLIP_RETEST`
   - add direct positive score for retest proximity and rejection quality

3. `POST_DISPLACEMENT_CONTINUATION`
   - add direct positive score for displacement quality, consolidation compression, and breakout re-acceleration

4. `TREND_PULLBACK_EMA`
   - add direct positive score for pullback quality instead of relying mostly on generic indicator scoring

5. `VOLUME_SURGE_BREAKOUT`
   - score breakout candle quality and retest quality explicitly, not just last-candle volume ratio

## Final recommendation

The current scoring calculation should be treated as **structurally miscalibrated, not merely conservative**.

The correct next PR is:

> **family-aware scoring correction with targeted penalty rebalance, while preserving global discipline and leaving broad thresholds intact**

That is the narrowest change that is doctrine-safe and consistent with the business truth that the engine is expressing valid setups upstream but failing to convert enough of them into paid-tier signals.
