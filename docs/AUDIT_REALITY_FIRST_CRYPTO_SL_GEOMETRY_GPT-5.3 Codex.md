# AUDIT_REALITY_FIRST_CRYPTO_SL_GEOMETRY_GPT-5.4

## 1. Executive summary
- Crypto LTF futures are wick-heavy and sweep-heavy; “nice R:R tight” is often not “true invalidation tight.”
- In this repo, evaluator-authored structural invalidation is **partly** preserved, but still constrained by global downstream controls (notably `360_SCALP` max SL cap `1.5%`) and global router RR floor `1.3`.
- Runtime truth (from `origin/monitor-logs`) shows concentrated expression and poor quality on expressed paths (`SR_FLIP_RETEST`, `TREND_PULLBACK_EMA` both currently 100% SL in sampled window, ~3-minute terminal clustering).
- Final judgment: too-tight/geometry distortion is a **major contributor** for structural families, but the live-quality problem is **not primarily only SL tightness**; setup timing/selection and funnel governance are at least as important.

## 2. Reality-first crypto market truth
- LTF crypto behavior is dominated by: stop sweeps, wick overshoots, liquidation cascades, noisy intrabar spikes, spread/slippage bursts, false breaks/reclaims, and retest overshoots before resolve.
- A structurally valid setup frequently experiences adverse excursion before directional follow-through.
- Therefore, an SL inside ordinary wick/noise/liquidation envelope is not “risk-efficient”; it is usually a premature stop.
- “Tight for optics” (high headline R:R) and “tight at true invalidation” are different doctrines.
- Wider stops are correct when they are tied to structural failure (acceptance back through reclaimed level, break of sweep extreme + buffer, collapse of continuation structure), not arbitrary percent widening.

## 3. Correct stop-loss / invalidation doctrine for crypto
- Valid SL = thesis-level invalidation (structure-first), not convenience-distance.
- Unrealistically tight SL = inside normal volatility/noise envelope for that setup family and symbol microstructure.
- Evaluator-owned invalidation matters because setup logic knows the structural anchor.
- Downstream compression/capping is dangerous if it converts “valid but wide” into “fake viable but fragile.”
- Global stop rules are structurally unsafe; doctrine should be family/path-aware.
- If truthful SL is too wide to produce acceptable business geometry, reject the trade; do not compress it into synthetic viability.

## 4. Current repo implementation truth
### Confirmed from code
- `360_SCALP` global max SL cap is `1.5%` (`src/signal_quality.py:345-347`, cap applied in `build_risk_plan` at `1121-1140`).
- Geometry policy validates near-zero floor and min risk distance (`src/signal_quality.py:1142-1170`, `1198-1209`).
- Router-level risk manager applies global RR floor `1.3` (`src/risk.py:35`, `119-123`).
- Trade lifecycle enforces min lifespan `180s` and poll interval `5s` (`config/__init__.py:944`, `1034-1036`; `src/trade_monitor.py` min-lifespan gate around `549-553`).
- Predictive TP/SL scaling bypass exists for structural setups including `TREND_PULLBACK_EMA`, `SR_FLIP_RETEST`, `LIQUIDATION_REVERSAL`, FAR (`src/predictive_ai.py:44-56`, `164-172`).
- Scanner revalidates predictive geometry against policy and reverts if invalid (`src/scanner/__init__.py:2665-2725`).

### Confirmed from runtime monitor evidence
- `origin/monitor-logs:monitor/report/truth_snapshot.json` and `truth_report.md` show:
  - Active low-quality concentration in `SR_FLIP_RETEST` and `TREND_PULLBACK_EMA`.
  - Current sampled quality for both: `win_rate=0`, `sl_rate=100`.
  - Median create->first breach ~`183.88s`, create->terminal ~`186.07s`, and terminal-close-around-3m at `92.9%`.

## 5. Path-by-path analysis
### 5.1 SR_FLIP_RETEST
- Evaluator SL is fixed near flipped level (`level * (1±0.002)`) (`src/channels/scalp.py:2037-2041`).
- Setup is structural and protected in downstream preservation set (`src/signal_quality.py:118-126`), but global cap/guards still apply.
- Runtime: path emits but quality is poor (monitor truth artifacts: active-low-quality, sampled 100% SL).
- Interpretation: structural intent exists, but current live behavior is consistent with invalidation too close for real noise **and/or** weak entry timing quality.

### 5.2 TREND_PULLBACK_EMA
- Evaluator uses EMA-anchored SL with ATR/min-distance constraints (`src/channels/scalp.py:765-769`), plus momentum/reclaim checks (`731-755`).
- Path is structural-protected downstream (`src/signal_quality.py:123`), predictive TP/SL bypassed.
- Runtime still shows poor outcomes (monitor truth artifacts: sampled 100% SL, low-quality concentration).
- Interpretation: not mainly cap-compression here; entry/timing quality and path selectivity likely dominate.

### 5.3 LIQUIDITY_SWEEP_REVERSAL
- Evaluator stop is sweep-anchored in standard evaluator (`src/channels/scalp.py:520-537`), but this setup is **not** in structural protection set (`src/signal_quality.py:118-129` excludes it), so risk-plan can rewrite geometry generically.
- Family faces generic scanner MTF gate + family cap/semantic rescue layer (`src/scanner/__init__.py:2908-2974`), still trend-confluence-centric by construction (`src/mtf.py:111-211`).
- Runtime shows high generation but heavy gating and very low emission (`truth_snapshot.json` path funnel).
- Interpretation: major thesis-to-downstream mismatch; this is governance/semantic friction at least as much as stop distance.

### 5.4 Shared downstream layer
- Global cap (`1.5%`) + global RR floor (`1.3`) + family-agnostic safety controls can force structural families into reject/compress tension.
- System does preserve some evaluator geometry and blocks predictive widening beyond baseline (`src/scanner/__init__.py:2708-2713`), which is good doctrine, but shared rules still dominate feasibility.

## 6. Where codebase matches reality
- Structural-preservation doctrine exists for key setups (`STRUCTURAL_SLTP_PROTECTED_SETUPS`).
- Predictive stage does not freely distort protected SL/TP geometry.
- Scanner explicitly tracks geometry changes/capping outcomes.
- Family-semantic MTF rescue exists for reclaim/retest and reversal families (partial correction).

## 7. Where codebase violates reality
- Global `360_SCALP` SL cap (`1.5%`) can conflict with truthful invalidation on volatile/sweep regimes.
- Router global RR floor (`1.3`) is not path-family aware and can reject setups whose truthful invalidation is wider.
- `LIQUIDITY_SWEEP_REVERSAL` remains vulnerable to downstream generic geometry rewrite (not structural-protected).
- MTF core metric remains trend-alignment centric (`ema_fast/ema_slow/close` confluence), still doctrinally imperfect for structural reclaim/reversal families.

## 8. Is the current problem primarily too-tight SL / geometry distortion?
### Strong inference
- Too-tight/geometry distortion is a **major** root-cause for structural families (especially reclaim/retest and sweep-reversal contexts).
- But runtime evidence shows even non-cap-dominant expressed path (`TREND_PULLBACK_EMA`) is low quality and stop-heavy.
- So the primary system-wide issue is **combined**: setup/timing quality + downstream governance friction + (in structural families) stop doctrine friction.

## 9. Alternative explanations and how much they matter
- **Setup logic / entry timing quality:** high impact (explains persistent SL-first outcomes on expressive paths).
- **Downstream governance (MTF/trend-centric gating for structural families):** high impact (large generated->gated losses in monitor truth).
- **Stop geometry compression/tightness:** high impact for SR/reclaim/reversal subset, medium system-wide.
- **Lifecycle handling (~3 minute behavior):** medium impact for observability interpretation; not primary causal driver of losses itself.

## 10. Best next action
- Run family-aware invalidation audit in production terms:
  1) for each target family, compare evaluator-authored SL distance vs final live SL distance;
  2) classify each rejection as “reject wide-valid” vs “compress then reject” vs “accept compressed.”
- Then enforce doctrine: reject unattractive truthful setups; stop compressing structural invalidation into fake viability.

## 11. Concrete PR recommendations
1. Make SL cap policy family-aware (not blanket `360_SCALP=1.5%`), with explicit reject-not-compress option for structural families.
2. Add `LIQUIDITY_SWEEP_REVERSAL` to structural SL protection if its evaluator anchor is the intended thesis owner.
3. Introduce family-aware RR feasibility checks in router/risk layer (avoid universal `1.3` for all families).
4. Emit explicit geometry-lineage telemetry: evaluator SL/TP -> risk-plan SL/TP -> post-predictive final live.
5. Add explicit runtime counters for “truthful wide rejected” vs “compressed geometry accepted/rejected.”

## 12. Confidence / uncertainty
- **High confidence (code):** global cap, global RR floor, min-lifespan lifecycle, protected-set behavior, predictive bypass behavior.
- **High confidence (runtime artifacts):** current emitted-path concentration, poor sampled outcomes, ~3-minute terminal clustering.
- **Uncertain / not yet proven:** exact percentage of losses directly caused by cap compression in this specific latest 24h truth window (truth snapshot does not expose per-trade cap lineage).

## 13. Final verdict
**Direct answer:**  
**The current live-quality problem is not primarily only because stops are forced too tightly, but stop/geometry distortion is a major co-driver for structural families.**  
System-wide, the bigger first-order issue is a combination of setup/timing quality and downstream family-misaligned governance; within reclaim/retest/reversal, tight/compressed invalidation is materially harming realism and outcomes.
