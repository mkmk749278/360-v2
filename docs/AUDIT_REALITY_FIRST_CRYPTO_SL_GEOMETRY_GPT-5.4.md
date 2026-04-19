# AUDIT_REALITY_FIRST_CRYPTO_SL_GEOMETRY_GPT-5.4

- Repository: `mkmk749278/360-v2`
- Audit basis date: 2026-04-19
- Runtime artifact baseline: `refs/heads/monitor-logs:monitor/latest.txt`, `refs/heads/monitor-logs:monitor/report/truth_snapshot.json`, `refs/heads/monitor-logs:monitor/report/window_comparison.json`
- Validation baseline before editing: `ruff check .` failed on pre-existing lint issues; targeted `pytest` run had 10 pre-existing failures outside this doc task.

## 1. Executive summary

The repo does **not** fully match real crypto market stop-loss reality.

The strongest reality-first conclusion is:

- **`SR_FLIP_RETEST` is very likely being stopped too tightly for real crypto retest behavior, both because the evaluator itself uses a fixed 0.20% structural buffer and because downstream policy still subjects structural setups to generic geometry/governance constraints.**
- **`TREND_PULLBACK_EMA` looks weak for a different reason as well: entry/confirmation quality is still not strong enough to prove the pullback has actually finished.**
- **`LIQUIDITY_SWEEP_REVERSAL` is not primarily a stop-width problem in current runtime truth; it is more a generation / generic-MTF / trend-governance problem.**
- **System-wide, the live-quality problem is not explained by one thing only. The best answer is: too-tight stop / geometry distortion is a primary defect, especially for reclaim/retest paths, but overall poor live quality is a combination of stop doctrine problems plus weak timing/confirmation on the currently active trend-pullback path.**

Evidence split:

- **Confirmed from code:** evaluator stops are path-specific at first, but protected setups still pass through a universal channel SL cap, near-zero floor, minimum-risk-distance checks, minimum R:R checks, generic scanner MTF, and same-direction winner selection (`src/channels/scalp.py:765-768,2037-2043`; `src/signal_quality.py:343-468,1055-1325`; `src/scanner/__init__.py:2879-2994,3232-3273,3994-4055`).
- **Confirmed from monitor/runtime evidence:** current live paths are low-quality, with `SR_FLIP_RETEST` and `TREND_PULLBACK_EMA` both classified `active-low-quality`; both have 0% win rate and 100% SL rate in the current runtime snapshot, and terminal outcomes cluster around the 3-minute floor (`refs/heads/monitor-logs:monitor/report/truth_snapshot.json`).
- **Strong inference:** the reclaim/retest family is the clearest place where real crypto volatility and current stop doctrine are misaligned.
- **Uncertain / not yet proven:** exact bar-by-bar intratrade overshoot beyond structural levels is not present in the repo artifacts, so the precise fraction of losses caused by stop placement vs bad entries cannot be proven from this snapshot alone.

## 2. Reality-first crypto market truth

Lower-timeframe crypto futures do not trade like clean textbook diagrams.

1. **Wick-heavy behavior is normal.** Small-cap and even major-perp order books regularly print thin-book spikes, forced sweeps, and immediate reclaim candles.
2. **Liquidation sweeps are part of normal price discovery.** A level can be structurally correct and still be breached intrabar before the real move starts.
3. **Intrabar volatility is large relative to tidy retail stop distances.** A stop that looks attractive for headline R:R can still sit inside ordinary 1m/5m noise.
4. **False breakouts and reclaim behavior are common.** Crypto often breaks a level, trades beyond it, then reclaims and resolves in the original thesis direction.
5. **Retests frequently overshoot before resolving.** The invalidation point is often beyond the wick extreme / failed reclaim boundary, not exactly at the pretty level.
6. **Spread/noise matters more on scalps.** When expected edge is small, a stop placed inside normal spread + noise + sweep behavior becomes a noise-harvesting device, not a thesis invalidation.
7. **“Tight for nice R:R” is different from “true invalidation.”** A stop is correct only when the trade thesis is actually wrong there. A stop chosen to manufacture a cleaner reward multiple is not a truthful stop.
8. **A wider stop is correct when the setup remains valid after a normal sweep/overshoot.** That is common on reclaim/retest, sweep-reversal, and failed-break structures.
9. **A wider stop is wrong when it merely hides a weak setup.** If truthful invalidation is so far away that the trade no longer offers acceptable economics, the setup should usually be rejected, not geometry-compressed into fake viability.

Implication: in live crypto, many valid setups fail not because the thesis was wrong, but because the stop sat inside routine wick/sweep territory.

## 3. Correct stop-loss / invalidation doctrine for crypto

A reality-first doctrine for live crypto should be:

1. **Stop-loss = thesis invalidation, not desired cosmetics.**
2. **Evaluator-owned invalidation matters.** The setup generator knows whether invalidation is beyond a sweep, beyond a reclaim failure, beyond EMA structure, or beyond a failed auction extreme.
3. **Path/family-aware doctrine is mandatory.** Reclaim/retest, reversal, trend pullback, and breakout continuation should not share one generic stop doctrine.
4. **Global stop rules are dangerous.** A universal max-SL cap can convert a valid wide stop into a false narrow stop.
5. **Downstream compression/capping is only safe when it does not change thesis truth.** If it changes thesis truth, it should reject the trade, not mutate it into a different trade.
6. **Near-zero floors are useful only as sanity guards.** They must not substitute for real invalidation doctrine.
7. **A setup with a truthful but economically unattractive stop should be rejected honestly.** That is better than sending a trade with a stop placed inside normal crypto noise.

So the correct live question is not “Can we keep this under 1%?” The correct question is “Where is this trade actually wrong?”

## 4. Current repo implementation truth

### Evaluator-authored stop logic

- **`SR_FLIP_RETEST`** places stop at the flipped level ±0.20%: `sl = level * (1 - 0.002)` for longs or `* (1 + 0.002)` for shorts (`src/channels/scalp.py:2037-2043`). That is a fixed percentage buffer from the flip level, not a wick-aware / ATR-aware / sweep-aware invalidation.
- **`TREND_PULLBACK_EMA`** places stop beyond EMA21, using `max(min_sl_pct, 1.1 * distance_to_ema21, 0.5 * ATR)` (`src/channels/scalp.py:765-768`). This is more structure-aware than SR flip, but still assumes EMA21 is the right invalidation boundary for the live pullback.
- **`LIQUIDITY_SWEEP_REVERSAL`** (the standard scalp evaluator that self-classifies as that setup) uses swept-level ±0.10% when a sweep level exists, with a 0.5 ATR minimum distance fallback (`src/channels/scalp.py:520-545,596-608`).

### Scanner prep / gate flow

- The scanner evaluates execution quality before risk-plan logic and uses setup-specific anchors for `SR_FLIP_RETEST` and `LIQUIDITY_SWEEP_REVERSAL` (`src/signal_quality.py:905-1052`).
- MTF gating is still generic first: family policy mostly changes the **minimum score threshold cap**, not the base MTF semantics (`src/scanner/__init__.py:341-379,2879-2994`).
- A semantic-MTF rescue exists for reclaim/retest and reversal families, but it still relies on trend-state counts across timeframes and only rescues near-misses (`src/scanner/__init__.py:2213-2261,2946-2968`).

### Downstream risk-plan logic

- Protected setups preserve evaluator-authored SL/TP first, including `TREND_PULLBACK_EMA`, `SR_FLIP_RETEST`, `LIQUIDATION_REVERSAL`, `FUNDING_EXTREME_SIGNAL`, and others (`src/signal_quality.py:110-129,1105-1119,1223-1235`).
- But the preserved geometry still goes through:
  - **universal channel max SL cap** (`360_SCALP = 1.5%`) (`src/signal_quality.py:343-354,1121-1140`)
  - **near-zero SL rejection** (`src/signal_quality.py:1142-1170`)
  - **minimum risk-distance rejection** (`src/signal_quality.py:1198-1209`)
  - **minimum RR policy** (`src/signal_quality.py:356-386,465-467`)
- The scanner records when risk-plan geometry changes or caps the evaluator geometry (`src/scanner/__init__.py:3232-3273`).

### Predictive / adjustment / validation logic

- Predictive TP/SL scaling is bypassed for the main structural/protected setups, including `TREND_PULLBACK_EMA`, `SR_FLIP_RETEST`, `FAILED_AUCTION_RECLAIM`, and `LIQUIDATION_REVERSAL` (`src/predictive_ai.py:34-56,154-173`).
- For non-bypassed setups, predictive geometry can mutate SL/TP, but scanner revalidates and restores prior geometry if policy is violated (`src/scanner/__init__.py:2665-2738`).

### Lifecycle truth

- `360_SCALP` has a **180-second minimum lifespan** before SL/TP evaluation and the trade monitor polls every 5 seconds (`config/__init__.py:944,1034-1043`; `src/trade_monitor.py:405-415,595-605`).
- That means a trade can be wrong almost immediately but still look like a ~3-minute close in runtime reporting.

## 5. Path-by-path analysis

| Path | Reality-first stop doctrine | What code does | Main mismatch | Verdict |
|---|---|---|---|---|
| `SR_FLIP_RETEST` | Stop should usually sit beyond the **true reclaim failure / wick failure / local liquidity overshoot**, not just a neat line | Fixed ±0.20% from flip level; protected later, but still subject to global cap / downstream validation (`src/channels/scalp.py:2037-2043`; `src/signal_quality.py:1121-1209`) | Evaluator stop itself is likely too close for wick-heavy crypto retests | **Primary too-tight-stop path** |
| `TREND_PULLBACK_EMA` | Stop can be tight if entry is late enough and pullback finish is truly confirmed | Stop is EMA21/ATR-based and preserved downstream; entry logic still mainly checks proximity + directional turn + one-candle reclaim style conditions (`src/channels/scalp.py:709-768`) | Main issue looks more like timing/confirmation than downstream stop mutation | **Primary entry-quality path** |
| `LIQUIDITY_SWEEP_REVERSAL` | Stop belongs beyond sweep failure / reversal failure; path should not be judged like trend continuation | Evaluator already uses sweep/ATR stop and its own 1h MTF gate, but scanner adds generic MTF and later trend governance (`src/channels/scalp.py:498-545`; `src/scanner/__init__.py:2879-2994`) | Bigger issue is family-misaligned governance, not stop width | **Not mainly stop problem right now** |
| Shared downstream layer | Preserve evaluator invalidation unless rejecting trade honestly | Protected geometry survives better than before, but universal scalp cap and generic validation still sit above it (`src/signal_quality.py:110-129,343-468,1105-1209`) | “Preserved, then normalized” is still doctrinally risky | **Shared structural defect** |

### Runtime evidence for these paths

- `SR_FLIP_RETEST`: 10,638 generated, 9,278 gated, 19 emitted, classified `active-low-quality`; current closed sample shows 0% win rate, 100% SL rate, average PnL -0.4263% (`refs/heads/monitor-logs:monitor/report/truth_snapshot.json`).
- `TREND_PULLBACK_EMA`: 1,025 generated, 731 gated, 15 emitted, also `active-low-quality`; current closed sample shows 0% win rate, 100% SL rate, average PnL -0.297% (`refs/heads/monitor-logs:monitor/report/truth_snapshot.json`).
- `LIQUIDITY_SWEEP_REVERSAL`: 17,321 generated, 14,175 gated, only 2 emitted in the current snapshot (`refs/heads/monitor-logs:monitor/report/truth_snapshot.json`).
- Window-over-window, both `SR_FLIP_RETEST` and `TREND_PULLBACK_EMA` degraded further (`refs/heads/monitor-logs:monitor/report/window_comparison.json`).

## 6. Where codebase matches reality

1. **Evaluator-owned geometry is explicitly recognized as important.** Protected-setup preservation exists in both risk-plan and predictive layers (`src/signal_quality.py:110-129,1105-1119`; `src/predictive_ai.py:34-56`).
2. **Execution anchors are path-aware.** `SR_FLIP_RETEST` uses `sr_flip_level`; `FAILED_AUCTION_RECLAIM` uses reclaim level; sweep reversal uses sweep level (`src/signal_quality.py:928-999`).
3. **The repo already knows global generic MTF is not ideal.** It adds family caps and a semantic rescue for reclaim/retest and reversal families (`src/scanner/__init__.py:341-379,2213-2261`).
4. **The system distinguishes “too wide to be viable” from “wrong side / nonsense geometry” better than a purely global model would.** Near-zero, wrong-side, widened-vs-baseline, and RR checks exist (`src/signal_quality.py:411-468`).
5. **Tests explicitly protect path-specific doctrine.** `SR_FLIP_RETEST` execution anchoring and `TREND_PULLBACK_EMA` entry-quality behavior are covered (`tests/test_signal_quality.py:260-292`; `tests/test_channels.py:1591-1640`).

## 7. Where codebase violates reality

1. **`SR_FLIP_RETEST` stop doctrine is too clean for real crypto retests.** A flat 0.20% beyond the flip level is not the same thing as true invalidation. In wick-heavy futures, the valid reclaim can overshoot that line before resolving.
2. **The downstream layer still treats protected geometry as negotiable.** Even when evaluator geometry is preserved first, a universal 1.5% scalp cap can still redefine viability (`src/signal_quality.py:343-354,1121-1140`).
3. **The system can still optimize for acceptable geometry instead of truthful invalidation.** A setup that needs more room may be compressed or rejected by shared policy rather than judged honestly at the evaluator level.
4. **MTF doctrine is still partially trend-native.** Family threshold caps are not the same as family-owned MTF semantics (`src/scanner/__init__.py:341-379,2879-2994`).
5. **Runtime lifecycle hides true failure timing.** The ~3-minute pattern is mostly a monitor-policy artifact overlaying a real quality issue, so it delays diagnosis of whether stops were effectively hit much earlier (`config/__init__.py:1034-1043`; `src/trade_monitor.py:595-605`; `refs/heads/monitor-logs:monitor/report/truth_snapshot.json`).

## 8. Is the current problem primarily too-tight SL / geometry distortion?

### Confirmed from code

- `SR_FLIP_RETEST` is explicitly hard-wired to a fixed 0.20% stop buffer from the structural flip level (`src/channels/scalp.py:2037-2043`).
- Shared downstream policy still applies universal cap / minimum-distance / RR doctrine even after evaluator preservation (`src/signal_quality.py:1121-1209`).
- `TREND_PULLBACK_EMA` is preserved more faithfully downstream, so if it is failing, the cause is less likely to be predictive/risk-plan rewriting and more likely to be evaluator timing or thesis quality.

### Confirmed from monitor/runtime evidence

- The two active paths are both low-quality in live runtime.
- `SR_FLIP_RETEST` is the most suspicious degradation target in the runtime truth snapshot.
- Terminal closes cluster around the 180s floor, so many failures are happening before the system can honestly separate “immediate thesis failure” from “stop simply checked later” (`refs/heads/monitor-logs:monitor/report/truth_snapshot.json`).

### Strong inference

- **For reclaim/retest paths, yes: too-tight stop doctrine and geometry distortion are the primary explanation.**
- **For the total live-quality problem across the currently active engine, not entirely.** `TREND_PULLBACK_EMA` weakness points to entry/confirmation quality as a co-equal cause.

### Uncertain / not yet proven

- The repo does not include per-trade intrabar path reconstruction showing exactly how often `SR_FLIP_RETEST` would have survived with a wick-aware invalidation instead of the current fixed 0.20% buffer.

## 9. Alternative explanations and how much they matter

1. **Weak setup logic / poor confirmation quality — High importance.**
   - Especially for `TREND_PULLBACK_EMA`. The path can still enter before the pullback is truly absorbed and resumed.
2. **Bad routing / governance — Medium to high importance.**
   - Generic MTF and same-direction winner selection bias the engine toward policy-compatible survivors rather than thesis-best survivors (`src/scanner/__init__.py:2879-2994,3994-4055`).
3. **Lifecycle handling — Medium importance for diagnosis, lower for root cause.**
   - It does not create the loss by itself, but it obscures how quickly the thesis was actually wrong.
4. **Weak evaluator generation on other paths — Medium importance for expression diversity, lower for the specific live-loss issue.**
   - `LIQUIDATION_REVERSAL`, `WHALE_MOMENTUM`, `VOLUME_SURGE_BREAKOUT`, and others are mostly generation-silent or heavily gated, but that explains silence more than the current active-path losses.

## 10. Best next action

**Audit and repair `SR_FLIP_RETEST` invalidation doctrine first, then separate that from `TREND_PULLBACK_EMA` entry-quality repair.**

That is the highest-value next step because runtime truth already flags `SR_FLIP_RETEST` as the top anomaly, and it is the path where real crypto retest behavior most clearly conflicts with the current stop doctrine.

## 11. Concrete PR recommendations

1. **Replace the fixed `SR_FLIP_RETEST` 0.20% stop rule with evaluator-owned structural invalidation.**
   - Base it on reclaim failure / retest wick failure / local liquidity extreme plus volatility-aware buffer.
   - If the truthful stop becomes too wide, reject the setup rather than compress it.
2. **Stop using universal cap-to-fit behavior for evaluator-protected structural paths.**
   - For protected setups, prefer: preserve truthful stop -> accept if viable -> otherwise reject.
3. **Add emitted-live telemetry for evaluator stop vs final stop.**
   - `eval_sl_pct`, `final_sl_pct`, `cap_applied`, `risk_plan_reason`, `first_breach_before_180s_estimate`.
4. **Strengthen `TREND_PULLBACK_EMA` finish-confirmation doctrine.**
   - Require clearer evidence that the pullback has actually ended, not just that price is near EMA and printing one favorable candle.
5. **Reduce double-policing on reversal/reclaim families.**
   - Make MTF semantics genuinely family-owned instead of generic trend-confluence with a lower threshold cap.
6. **Add path-level replay tests for live-loss archetypes.**
   - Especially “overshoot then resolve” retests and “pullback not actually finished” trend setups.

## 12. Confidence / uncertainty

- **High confidence:** code-path findings about stop generation, preservation, cap logic, semantic-MTF limits, and lifecycle timing.
- **Medium confidence:** runtime interpretation that reclaim/retest stop doctrine is the leading structural defect.
- **Medium confidence:** `TREND_PULLBACK_EMA` poor quality being mostly an entry-quality problem.
- **Lower confidence:** exact percentage of current losses attributable purely to stop placement, because the repo does not include full intrabar replay of each closed trade.

## 13. Final verdict

**Direct answer:** The current live-quality problem is **not only** that the system forces stops too tightly, but **too-tight / doctrine-distorting stop placement is the primary architectural problem for `SR_FLIP_RETEST` and the reclaim/retest family, while weak entry/confirmation quality is the other major problem for `TREND_PULLBACK_EMA`.**

So if the question is:

**“Is the current live-quality problem primarily because the system is placing/forcing stops too tightly for real crypto market conditions, or is something else more important?”**

The best evidence-led answer is:

**Mostly yes for reclaim/retest; not fully yes for the whole engine. The overall live-quality problem is a combination, with too-tight / geometry-distorting stop doctrine as the biggest architectural defect and weak trend-pullback timing as the other major cause.**
