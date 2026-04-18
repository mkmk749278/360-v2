# AUDIT_PATH_SILENCE_QUALITY_DURATION_GEOMETRY_GPT-5.4

**Model tag:** GPT-5.4  
**Repository:** `mkmk749278/360-v2`  
**Code baseline:** `main` working tree as inspected on 2026-04-18  
**Live evidence baseline:** `monitor/latest.txt` from `monitor-logs` generated 2026-04-18 02:30:45 UTC  
**Validation note:** attempted `python -m ruff check .` and `python -m pytest` before editing, but the sandbox Python environment does not have `ruff` or `pytest` installed.

---

## 1. Executive verdict

The live engine is not expressing only `TREND_PULLBACK_EMA` and `SR_FLIP_RETEST` because those are clearly the best live setups. It is expressing them because they are the two `360_SCALP` paths whose **generation rules are broad enough** and whose **downstream policy fit is strongest** under the current funnel.

The strongest current root-cause stack is:

1. **Path generation is intrinsically sparse for most setup families.** Many families require extreme order-flow, specific regime windows, or multi-leg structure that simply does not appear often enough (`LIQUIDATION_REVERSAL`, `FUNDING_EXTREME_SIGNAL`, `WHALE_MOMENTUM`, `QUIET_COMPRESSION_BREAK`, `POST_DISPLACEMENT_CONTINUATION`, `CONTINUATION_LIQUIDITY_SWEEP`, `DIVERGENCE_CONTINUATION`). In those cases silence is mostly a generation problem, not a scanner bug (`src/channels/scalp.py:772-862, 945-1055, 2013-2088, 2169-2248, 2321-2423, 2534-2684, 2791-3013`).
2. **The reclaim/retest and reversal families are still judged by trend-style downstream policy in practice.** PR-1 only lowers the `check_mtf_gate()` minimum score cap by family; it does not change the semantics of the MTF test. The live suppressor keys prove this policy still blocks reclaim/retest and reversal setups in size: `mtf_gate:360_SCALP`, `mtf_gate_family:360_SCALP:reclaim_retest`, `mtf_gate_setup:360_SCALP:SR_FLIP_RETEST`, `mtf_gate_setup:360_SCALP:FAILED_AUCTION_RECLAIM`, `mtf_gate_family:360_SCALP:reversal`, `mtf_gate_setup:360_SCALP:LIQUIDITY_SWEEP_REVERSAL` (`src/scanner/__init__.py:333-373, 2722-2798`; `monitor/latest.txt@monitor-logs:65-82, 261-266, 289-314`).
3. **Geometry friction is still a major live blocker for reclaim/retest paths.** `geometry_rejected_risk_plan:360_SCALP:reclaim_retest` repeats at 8-14 hits per cycle in the monitor output, while the code still enforces a universal scalp max-SL cap of 1.5%, a near-zero SL rejection, and minimum-risk-distance guards after evaluator-authored structural stops are preserved (`src/signal_quality.py:343-401, 1072-1190`; `src/scanner/__init__.py:3036-3080`; `monitor/latest.txt@monitor-logs:65-69, 88-99, 257-265, 289-314`).
4. **The two expressive paths survive because the current scorer explicitly likes them.** `TREND_PULLBACK_EMA` and `SR_FLIP_RETEST` both have direct regime affinity and direct family thesis adjustments; several silent paths do not. `DIVERGENCE_CONTINUATION`, `LIQUIDATION_REVERSAL`, `FUNDING_EXTREME_SIGNAL`, and `QUIET_COMPRESSION_BREAK` are still under-credited by regime affinity; `BREAKDOWN_SHORT`, `OPENING_RANGE_BREAKOUT`, `QUIET_COMPRESSION_BREAK`, and `WHALE_MOMENTUM` still receive no family thesis adjustment (`src/signal_quality.py:1500-1565, 1628-1642, 1725-1956`).
5. **The currently expressive paths are weak because the funnel selects policy-compatible survivors, not necessarily thesis-best survivors.** `TREND_PULLBACK_EMA` is trend-policy-native and exempt from SMC hard-gating; `SR_FLIP_RETEST` gets reclaim-family scoring support and a lower MTF threshold cap. But their live SL data shows mostly immediate adverse excursion, low MFE, and average hold duration around 4 minutes, which is weak real quality, not just a reporting illusion (`monitor/latest.txt@monitor-logs:103-142, 145-252`).
6. **The “3 minute” pattern is both real and an artifact.** Real, because live outcomes show almost no favorable excursion before stop on most losses. Artifact, because the trade monitor cannot close a signal before `MIN_SIGNAL_LIFESPAN_SECONDS[360_SCALP] = 180`, then only checks every 5 seconds, and monitor scripts round/floor hold duration to minutes (`config/__init__.py:1034-1054, 944`; `src/trade_monitor.py:249, 359-369, 545-559, 640-659, 986-1008`; `scripts/monitor_sl_followthrough.py:37-64, 191-227`). A trade can effectively fail in seconds and still be reported at roughly the first 3-minute eligibility check.

**Bottom line:** the current engine is expressing the paths that are most compatible with current trend/MTF/scoring/geometry policy, not the paths most likely to produce the best business outcome. The narrowest high-confidence fixes are therefore **not** global threshold loosening; they are: (a) make reclaim/retest/reversal downstream policy truly thesis-aware, (b) stop geometry from distorting reclaim/retest structures on micro/tight-price symbols, and (c) separate real fast failure from 3-minute lifecycle compression in telemetry.

---

## 2. What is actually happening live

- Recent live history is concentrated entirely in `TREND_PULLBACK_EMA` (17/28) and `SR_FLIP_RETEST` (11/28) (`monitor/latest.txt@monitor-logs:137-142`).
- Top live suppressor keys are dominated by spread, generic MTF, reclaim/retest family MTF, reclaim/retest setup MTF, quiet-block, and low-score outcomes (`monitor/latest.txt@monitor-logs:71-83`).
- Reclaim/retest is the only family repeatedly visible in both **MTF suppression** and **geometry rejection** summaries (`monitor/latest.txt@monitor-logs:65-69, 261-266, 289-314`).
- Reversal is visible as an MTF-suppressed family, and `LIQUIDITY_SWEEP_REVERSAL` occasionally reaches scoring, but it is not surviving to live concentration (`monitor/latest.txt@monitor-logs:65-69, 291-314`).
- The quiet-market safety net is active in live logs (`QUIET_SCALP_BLOCK`), but the only explicit exemption paths are `QUIET_COMPRESSION_BREAK` and `DIVERGENCE_CONTINUATION` ≥64; neither is showing meaningful live expression (`src/scanner/__init__.py:3610-3650`; `monitor/latest.txt@monitor-logs:54-59, 71-83, 313-314`).
- Live SL follow-through is poor: 55% clean failure, 20% possible stop-too-tight/continuation, 10% partial reclaim, average MFE only +0.04%, average SL exit -0.43%, average hold about 4 minutes (`monitor/latest.txt@monitor-logs:231-252`).

Runtime truth: **most non-expressive paths are dying before emission; the two expressive paths are surviving because they fit the current policy; and many of those survivors are still failing almost immediately.**

---

## 3. Path-by-path survival matrix

Legend: **Gen** = generates evaluator signal; **Gate** = dominant live hard-gate loss; **Score** = dominant score-tier loss; **Geom** = geometry/risk-plan loss; **Route** = arbitration/router loss; **Life** = live outcome truth.

| Path | Gen | Gate | Score | Geom | Route | Life | Evidence-led status |
|---|---|---|---|---|---|---|---|
| `TREND_PULLBACK_EMA` | **Yes, broad** in `TRENDING_UP/DOWN` with EMA touch + RSI 40-60 + rejection candle + any FVG/OB (`src/channels/scalp.py:619-685`) | Usually passes; trend-native path and no live suppressor concentration around it | Survives well because it has trend regime affinity + family thesis bonus (`src/signal_quality.py:1501-1508, 1898-1935`) | Usually preserved; not the main geometry-friction family | Can win same-direction arbitration because it scores well (`src/scanner/__init__.py:3794-3854`) | **Weak**: many 3m SLs, MFE ~0 (`monitor/latest.txt@monitor-logs:159-217`) | Expressive but low-quality; selected because it is policy-compatible, not because it is proving robust |
| `SR_FLIP_RETEST` | **Yes, frequent**; structural flip window is broad enough to generate often (`src/channels/scalp.py:1746-1906`) | **Major live loss** at generic MTF despite family cap relief (`src/scanner/__init__.py:2722-2798`; `monitor/latest.txt@monitor-logs:71-82`) | Some candidates only reach `50-64` or `<50` (`monitor/latest.txt@monitor-logs:69, 314`) | **Major live loss** at reclaim/retest risk-plan geometry (`monitor/latest.txt@monitor-logs:65-69, 261-266, 289-314`) | Can still win arbitration when it survives and scores above peers | **Weak**: mostly 3m SLs, occasional 14m, some partial reclaim/possible stop-too-tight (`monitor/latest.txt@monitor-logs:153-229`) | Expressive, but only the tight, trend-compatible reclaim subset is surviving |
| `FAILED_AUCTION_RECLAIM` | **Yes, but narrower**; needs failed auction + reclaim distance + ATR + RSI (`src/channels/scalp.py:3124-3417`) | **Major live loss** at generic MTF; direct monitor key proves setup-specific suppression (`monitor/latest.txt@monitor-logs:71-79, 291-314`) | Little evidence of scoring survival | **Major live loss** in reclaim/retest geometry bucket (`monitor/latest.txt@monitor-logs:65-69, 291-314`) | Rarely reaches arbitration winners | n/a | Silent mainly from MTF + geometry mismatch, not from absence of generation alone |
| `LIQUIDITY_SWEEP_REVERSAL` | **Yes** when sweep + momentum + EMA alignment + 1h MTF support all line up (`src/channels/scalp.py:360-463`) | **Major live loss** at family/setup MTF and likely trend hard-gate (`monitor/latest.txt@monitor-logs:65-69, 291-314`; `src/scanner/__init__.py:3563-3590`) | Reaches `50-64` / `65-79`, but not live concentration (`monitor/latest.txt@monitor-logs:65-69`) | Not main geometry issue in snapshot | Loses to higher-confidence same-direction paths in scalp arbitration when present | n/a | Silent because reversal path is still double-policed by trend-style MTF/trend gates |
| `LIQUIDATION_REVERSAL` | **Very sparse**; requires 2% 3-candle cascade + opposite CVD + RSI extreme + near FVG/OB + 2.5x volume (`src/channels/scalp.py:782-862`) | Some family-level reversal MTF suppression likely applies when it does generate (`monitor/latest.txt@monitor-logs:65-69, 80-82`) | Also under-credited by regime affinity: not listed in volatile affinity table (`src/signal_quality.py:1511-1514, 1628-1642`) | Structural geometry protected; not main live blocker shown | Rarely reaches arbitration | n/a | Mostly correct rarity at generation, plus scoring under-credit and residual MTF mismatch |
| `WHALE_MOMENTUM` | **Very sparse**; needs whale alert or delta spike, high tick-dollar flow, directional dominance, and usable order book (`src/channels/scalp.py:955-1055`) | No specific live suppressor evidence; most loss is pre-generation | No family thesis bonus (`src/signal_quality.py:1527-1536, 1955-1956`) | Can suffer geometry cap on volatile microcaps, but not proven in current monitor snapshot | n/a | n/a | Mostly correct protective silence; not the main current defect |
| `VOLUME_SURGE_BREAKOUT` | **Sparse**; needs current surge volume, recent breakout candle, specific retest zone, EMA trend, breakout volume, and usually SMC context (`src/channels/scalp.py:1157-1283`) | No strong live suppressor evidence; mostly pre-generation | Has family thesis bonus and regime affinity, but no live scoring evidence in snapshot | Structural geometry protected; not main live blocker shown | Could lose same-direction arbitration if present | n/a | Silent mainly from strict generation rarity; likely correct protection |
| `BREAKDOWN_SHORT` | **Sparse**; mirror of surge breakout with bounce-zone and bearish EMA requirements (`src/channels/scalp.py:1373-1510`) | No explicit live suppressor evidence | Has trend-down regime affinity but **no family thesis bonus** (`src/signal_quality.py:1505-1508, 1561-1564, 1955-1956`) | Could contribute to capped short-SL logs, but attribution is not proven | Could lose same-direction arbitration | n/a | Silence is partly correct rarity, partly under-credit vs other trend-native paths |
| `OPENING_RANGE_BREAKOUT` | **No** | Hard-disabled by `SCALP_ORB_ENABLED=false` (`config/__init__.py:838-842`; `src/channels/scalp.py:1596-1600`) | n/a | n/a | n/a | n/a | Correct silence by explicit doctrine; should stay silent until rebuilt |
| `FUNDING_EXTREME_SIGNAL` | **Very sparse**; requires extreme funding, EMA reclaim, RSI turn, CVD support, and FVG/OB (`src/channels/scalp.py:2023-2088`) | No live suppressor evidence; mostly pre-generation | Under-credited: no regime affinity entry for its natural conditions (`src/signal_quality.py:1500-1514, 1628-1642`) | Structural geometry protected | n/a | n/a | Mostly correct rarity, but scoring still under-recognises it |
| `QUIET_COMPRESSION_BREAK` | **Very sparse**; requires QUIET/RANGING, BB squeeze <1.5%, band break, MACD zero-cross, 2x volume, RSI band, and FVG/OB (`src/channels/scalp.py:2169-2248`) | Exempt from quiet-block, but almost certainly not generating enough to matter (`src/scanner/__init__.py:3610-3625`) | Under-credited: quiet regime affinity still only lists `RANGE_FADE`; no family thesis bonus (`src/signal_quality.py:1509-1510, 1955-1956`) | Structural geometry protected | n/a | n/a | Silence is generation-led, but scorer still does not recognise its intended quiet-role |
| `DIVERGENCE_CONTINUATION` | **Sparse**; trend-only + 20-bar CVD divergence + EMA21 proximity + FVG/OB (`src/channels/scalp.py:2321-2423`) | No direct live suppressor evidence | **Scoring mismatch:** trend-only generator, but not in trend regime affinity table (`src/signal_quality.py:1501-1508, 1628-1642`) | Structural geometry protected | n/a | n/a | Likely silent from both rarity and a real scoring mismatch |
| `CONTINUATION_LIQUIDITY_SWEEP` | **Sparse**; valid only in continuation regimes and needs recent reclaimed same-direction sweep (`src/channels/scalp.py:2534-2684`) | No current live suppressor evidence, though generic MTF can still hit if generated | Gets family thesis bonus and regime affinity (`src/signal_quality.py:1503-1508, 1542-1544, 1853-1867`) | Structural geometry protected | Could lose to higher-scoring trend pullback on same direction | n/a | Silence looks mostly generation-led, not a proven downstream bug |
| `POST_DISPLACEMENT_CONTINUATION` | **Sparse**; valid only in continuation/expansion regimes and requires displacement + tight consolidation + breakout (`src/channels/scalp.py:2801-3117`) | No current live suppressor evidence | Has family thesis bonus and trend/volatile affinity (`src/signal_quality.py:1503-1508, 1511-1514, 1561-1564, 1937-1953`) | Structural geometry protected | Could lose arbitration if same-direction competitor scores higher | n/a | Silence looks mostly generation-led; current snapshot does not prove downstream blockage |

**Matrix conclusion:** the live engine has **three different silence modes**:

- **Correct rarity / protective silence:** `OPENING_RANGE_BREAKOUT`, `WHALE_MOMENTUM`, `FUNDING_EXTREME_SIGNAL`, `QUIET_COMPRESSION_BREAK`, much of `LIQUIDATION_REVERSAL`, `POST_DISPLACEMENT_CONTINUATION`, `CONTINUATION_LIQUIDITY_SWEEP`.
- **Real downstream suppression:** `SR_FLIP_RETEST`, `FAILED_AUCTION_RECLAIM`, `LIQUIDITY_SWEEP_REVERSAL`.
- **Generation rarity plus scoring mismatch:** `DIVERGENCE_CONTINUATION`, `LIQUIDATION_REVERSAL`, `QUIET_COMPRESSION_BREAK`, `FUNDING_EXTREME_SIGNAL`.

---

## 4. Root causes of silent paths

### 4.1 Correct filtering / correct silence

These are mostly doing what they should:

- **`OPENING_RANGE_BREAKOUT`** is intentionally disabled until rebuilt with real session logic (`config/__init__.py:838-842`; `src/channels/scalp.py:1596-1600`).
- **`WHALE_MOMENTUM`** requires rare flow conditions plus usable order-book confirmation; silence here is expected protection, not a bug (`src/channels/scalp.py:955-1055`).
- **`FUNDING_EXTREME_SIGNAL`** and **`LIQUIDATION_REVERSAL`** require rare order-flow extremes plus CVD/funding/liquidation context. Those should be infrequent (`src/channels/scalp.py:782-862, 2023-2088`).
- **`QUIET_COMPRESSION_BREAK`** is intentionally narrow: it only lives in `QUIET/RANGING` and still needs squeeze, band break, zero-cross MACD, 2x volume, and FVG/OB (`src/channels/scalp.py:2169-2248`).
- **`POST_DISPLACEMENT_CONTINUATION`** and **`CONTINUATION_LIQUIDITY_SWEEP`** are structurally multi-leg patterns; low frequency is expected if the market is not cleanly trending/expanding (`src/channels/scalp.py:2534-3117`).
- **`pair_quality:spread`** is mostly correct protection for a scalp channel with a 2.5% hard spread limit (`src/signal_quality.py:685-787`; `src/scanner/__init__.py:1915-1954`; `monitor/latest.txt@monitor-logs:71-79`).

### 4.2 Incorrect suppression / doctrinal mismatch

These are the real misalignments.

#### A. Reclaim/retest and reversal are still scored through generic trend-style MTF semantics

- The family-aware policy only changes the **minimum score threshold cap**; it does **not** change what `check_mtf_gate()` measures (`src/scanner/__init__.py:333-373, 2722-2798`).
- Live evidence shows this relaxation is only partially saving candidates (`mtf_policy_saved`) while the family/setup-specific MTF suppressors remain high (`monitor/latest.txt@monitor-logs:65-82`).
- `FAILED_AUCTION_RECLAIM` is exempt from the later trend hard-gate, but it is **not exempt from MTF**. So the engine first recognises a failed-auction reclaim, then still judges it via generic EMA/MTF confluence (`src/scanner/__init__.py:288-301, 2722-2798`).
- `LIQUIDITY_SWEEP_REVERSAL` is even more mismatched: the evaluator already requires EMA alignment and its own 1h MTF gate (`src/channels/scalp.py:441-462`), then the scanner applies another generic MTF gate and later a trend hard-gate, despite reversal-family relaxations (`src/scanner/__init__.py:2722-2798, 3563-3590`).

#### B. Geometry policy is disproportionately suppressing reclaim/retest

- The evaluator authors structural stops for `SR_FLIP_RETEST` and `FAILED_AUCTION_RECLAIM`, then the risk-plan layer preserves them but still applies a universal 1.5% scalp cap, a 0.05% near-zero floor, and minimum risk-distance checks (`src/signal_quality.py:343-401, 1072-1190`).
- Live reclaim/retest geometry rejections are persistent and high-volume (`monitor/latest.txt@monitor-logs:65-69, 261-266, 289-314`).
- This means the reclaim/retest family is squeezed from both sides: **too wide** gets capped or rejected; **too tight** gets near-zero rejected.

#### C. Several silent paths are still under-credited by the scorer

- `DIVERGENCE_CONTINUATION` is trend-only in generation, but absent from trend regime affinity, so it often starts 10 points behind trend-native survivors (`src/channels/scalp.py:2331-2338`; `src/signal_quality.py:1501-1508, 1628-1642`).
- `QUIET_COMPRESSION_BREAK` is purpose-built for quiet/ranging but quiet affinity still only recognises `RANGE_FADE` (`src/signal_quality.py:1509-1510`).
- `LIQUIDATION_REVERSAL` and `FUNDING_EXTREME_SIGNAL` still lack regime-affinity treatment in the states where they naturally occur (`src/signal_quality.py:1509-1514, 1628-1642`).
- `BREAKDOWN_SHORT`, `OPENING_RANGE_BREAKOUT`, `QUIET_COMPRESSION_BREAK`, and `WHALE_MOMENTUM` still get **zero** family thesis adjustment (`src/signal_quality.py:1520-1565, 1725-1956`).

#### D. Same-direction scalp arbitration amplifies survivability bias

`360_SCALP` now evaluates all candidates, but then keeps only the best final-confidence candidate per direction before emission (`src/scanner/__init__.py:3773-3854`). That is correct operationally, but it means the policy already decided by MTF/scoring/penalties determines which thesis survives. The engine is therefore optimising for **highest current policy score**, not necessarily highest real-world thesis quality.

---

## 5. Root causes of weak quality on the two expressive paths

## `TREND_PULLBACK_EMA`

Why it survives:
- Generator is relatively broad in trend regimes: EMA stack, near EMA9/21, RSI 40-60, one rejection candle, any FVG/OB (`src/channels/scalp.py:619-685`).
- It is explicitly favoured by regime affinity and family thesis adjustment (`src/signal_quality.py:1501-1508, 1898-1935`).
- It is exempt from SMC hard-gate, so lack of sweep structure does not kill it downstream (`src/scanner/__init__.py:259-286, 3526-3562`).

Why quality is weak:
- The generator can still enter **before the pullback is truly finished**. It requires proximity and one rejection candle, but not a deeper absorption/continuation confirmation. That fits current trend policy, but it does not guarantee local timing quality.
- Live evidence shows repeated **immediate adverse move with effectively zero MFE** on many losses (`monitor/latest.txt@monitor-logs:159-217`).
- Several losses later see same-direction re-entry reclaim the original level, which points to **premature timing and sometimes too-tight structural invalidation**, not only thesis invalidity (`monitor/latest.txt@monitor-logs:199-217`).
- Because the scorer rewards trend fit strongly, the path can survive even when the actual pullback entry is mediocre.

**Verdict:** `TREND_PULLBACK_EMA` is surviving mainly because it is the cleanest match to current trend-centric doctrine. Its live weakness is a mix of **entry timing too early within the pullback** and **policy over-selection of trend-compatible setups**.

## `SR_FLIP_RETEST`

Why it survives:
- Generator is broad enough to find many role-flip/retest patterns (`src/channels/scalp.py:1746-1906`).
- It gets trend regime affinity and reclaim-family thesis credit (`src/signal_quality.py:1501-1509, 1869-1896`).
- It receives the reclaim/retest MTF threshold cap reduction (`src/scanner/__init__.py:361-369, 2734-2742`).

Why quality is weak:
- The path still requires **EMA alignment in the signal direction** at generation (`src/channels/scalp.py:1864-1873`), so the surviving SR flips are mostly trend-synced continuation-style retests, not pure structural reclaims.
- Downstream MTF remains generic and trend-style, so only the most trend-compatible reclaim candidates survive. That pushes the path toward **late, policy-compatible continuation retests** instead of the best structural reclaims.
- Its stop is only **0.2% beyond the flipped level** before downstream risk handling (`src/channels/scalp.py:1907-1915`). Some live follow-through evidence points to stop-too-tight/partial-reclaim behavior (`monitor/latest.txt@monitor-logs:183-229`).
- At the same time, wider structural SR/FAR candidates are frequently blocked by the reclaim/retest geometry rules, so the emitted set is biased toward **tighter geometry survivors**, not necessarily best setups.

**Verdict:** `SR_FLIP_RETEST` survives because reclaim logic got some targeted relief, but quality is still weak because the path is being forced through **trend-style selection plus tight structural geometry**.

## Overall quality diagnosis on the two expressive paths

The weak live quality is **not one single issue**. It is a combination of:

1. **Policy-favored path survival** (trend-friendly / reclaim-friendly scoring and MTF caps)
2. **Entry timing weakness** (many trades stop before meaningful MFE)
3. **Structural stop tightness on surviving candidates**
4. **Some genuine thesis failure** (55% of recent SLs classify as clean failure)

The dominant mix is: **policy survivability bias + early/tight timing**, with genuine thesis failure still the largest bucket.

---

## 6. 3-minute duration analysis

## Executive answer

The 3-minute pattern is **both**:

- a **real rapid-failure problem** in many cases, and
- a **lifecycle/telemetry artifact** created by the monitoring design.

## What is real

- The live SL follow-through table shows most recent losses had **+0.00% MFE** and were classified as quick clean failures (`monitor/latest.txt@monitor-logs:159-239`).
- That means the market often moved against the thesis almost immediately after entry.

## What is artifact

### A. The system cannot close before 180 seconds

`TradeMonitor` explicitly skips SL/TP checks until `age_secs >= MIN_SIGNAL_LIFESPAN_SECONDS[channel]`, and `360_SCALP` is configured at **180 seconds** (`src/trade_monitor.py:549-559`; `config/__init__.py:1034-1042`).

So if price hits the stop 5 seconds after entry, the engine still will not record the trade as closed until the first eligible check after ~180 seconds.

### B. The monitor only checks every 5 seconds

The trade monitor loop sleeps `MONITOR_POLL_INTERVAL = 5.0` seconds between passes (`src/trade_monitor.py:359-369`; `config/__init__.py:944`). So recorded close time is additionally quantized to the next 5-second poll.

### C. Hold duration is measured at terminal handling time, not first breach time

`hold_duration_sec = max((utcnow() - sig.timestamp).total_seconds(), 0.0)` is computed inside `_record_outcome()` at the moment the trade is actually processed as terminal (`src/trade_monitor.py:249-280`). There is no separate stored “first touched SL” timestamp.

### D. Multiple reporting layers compress the number further

- `monitor_sl_followthrough.py` prints `hold_sec/60:.0f`, so 181-209 seconds still shows as `3m` (`scripts/monitor_sl_followthrough.py:59-64, 191-227`).
- `trade_monitor.py` closed-post text floors to `int(hold_sec // 60)}min`, so anything under 240 seconds can still present as `3min` in that channel post (`src/trade_monitor.py:986-1008`).
- `monitor_signal_history.py` shows the **record timestamp** (close-time), not open-time (`scripts/monitor_signal_history.py:31-37`).
- `PerformanceTracker` stores the record timestamp at outcome-recording time, not signal-open time (`src/performance_tracker.py:49-52, 122-151`).

## Clear answer to the user’s question

- **Yes, some trades can practically die in seconds.**
- **No, current live telemetry will not show that truth directly.** It will usually show the first terminal handling window around 3 minutes, because of the 180-second minimum lifespan plus 5-second polling plus minute rounding.
- Therefore the repeated `3m` pattern is **not proof that trades genuinely lasted 3 full minutes before failing**. It is proof that many trades were still open at the first eligible lifecycle check and were then closed there.

## Every place duration truth is compressed / delayed / rounded

1. `MIN_SIGNAL_LIFESPAN_SECONDS['360_SCALP']=180` blocks earlier closure (`config/__init__.py:1034-1042`).
2. `TradeMonitor.start()` polls every 5 seconds (`src/trade_monitor.py:359-369`).
3. `_record_outcome()` measures elapsed time at closure processing, not first breach (`src/trade_monitor.py:249-280`).
4. `monitor_sl_followthrough.py` rounds hold to nearest whole minute (`scripts/monitor_sl_followthrough.py:59-64, 197`).
5. `trade_monitor.py` closed-post formatting floors hold to whole minutes (`src/trade_monitor.py:1005-1008`).
6. `monitor_signal_history.py` reports close timestamp only (`scripts/monitor_signal_history.py:31-37`).

---

## 7. Geometry-friction analysis

## What the code does end-to-end

1. Evaluators author SL/TP geometry (`src/channels/scalp.py`).
2. `build_risk_plan()` preserves structural geometry for protected setups and FAR where valid (`src/signal_quality.py:1072-1338`).
3. It then applies universal hard controls:
   - channel max-SL cap (`360_SCALP = 1.5%`) (`src/signal_quality.py:343-354, 1102-1121`)
   - near-zero SL rejection (`0.05%`) (`src/signal_quality.py:369, 1123-1151`)
   - minimum risk-distance guard (`src/signal_quality.py:373-397, 1179-1190`)
4. Scanner records whether geometry was rejected, changed, capped, or preserved (`src/scanner/__init__.py:3036-3080, 2499-2568`).
5. Predictive adjustment is revalidated against the same policy and can be reverted (`src/scanner/__init__.py:2491-2568`).

## Interpreting the live warnings

### Near-zero SL rejection

Example live warnings: `SL near-zero rejection ... only 0.0415% ... min=0.0500%` (`monitor/latest.txt@monitor-logs:257-259`).

- **Correct rejection:** this is a real invalidation problem on tight-price / sub-penny symbols. A stop that small is functionally noise.
- **Operational implication:** some evaluator-authored structures on very tight-price instruments are below the minimum viable scalp stop once rounded to actual price scale.

### Repeated 1.96% / 2.09% / 2.40% / 2.80% cap events

Examples live warnings: `SL capped for 360_SCALP SHORT: 2.80% > 1.50% max` (`monitor/latest.txt@monitor-logs:89-99, 260-265, 289-312`).

- **Correct protection:** if a scalp path naturally needs >1.5% invalidation, that is outside current scalp doctrine.
- **But also distortion risk:** once capped, the signal that survives is no longer the original structural thesis. The engine has effectively converted a wider structural setup into a tighter scalp stop.
- **Business consequence:** this can create both silence (rejected risk-plan) and poor quality (survivor stop too tight).

### Extreme FVG rejection cases

Examples: `232.15% > 2.00% max`, `59.32% > 2.00% max` (`monitor/latest.txt@monitor-logs:89-99`).

- These are **correct rejections** of clearly invalid geometry on auxiliary FVG paths.
- They are not evidence that the paid `360_SCALP` doctrine should be loosened.

## Is geometry friction still a major cause of path silence?

**Yes for reclaim/retest; no for the whole portfolio.**

- For reclaim/retest, geometry friction is a **major live blocker**. The monitor repeatedly shows reclaim/retest risk-plan rejections before emission (`monitor/latest.txt@monitor-logs:65-69, 261-266, 289-314`).
- For the portfolio as a whole, many other silent paths are quiet primarily because they never generate, not because geometry kills them.

---

## 8. MTF-policy reality check

## The code reality

PR-1 did this:
- map `360_SCALP` setups to families (`src/scanner/__init__.py:344-359`)
- assign family min-score caps (`src/scanner/__init__.py:361-373`)
- lower the generic MTF threshold for some families before calling the same `check_mtf_gate()` (`src/scanner/__init__.py:2722-2798`)

PR-1 did **not** do this:
- rewrite MTF semantics by setup family
- stop reclaim/retest/reversal from being judged by generic EMA/close alignment logic across timeframes
- exempt FAR or reversal from MTF entirely

## Live reality

The monitor snapshot shows:
- `mtf_policy_relaxed:360_SCALP:reclaim_retest` is high
- `mtf_gate_family:360_SCALP:reclaim_retest` is also high
- `mtf_policy_saved:360_SCALP:reclaim_retest` is low
- reversal family still gets `mtf_gate_family:360_SCALP:reversal` / `LIQUIDITY_SWEEP_REVERSAL` suppression (`monitor/latest.txt@monitor-logs:65-82, 291-314`)

That means the current “family-aware MTF” change is **real but narrow**. It is not fake, but it is also **not substantively thesis-aware**. It is still a generic trend-style MTF gate with slightly lower pass thresholds for some families.

## Direct answers

- **Is current relaxed / family-aware MTF policy substantively working?**  
  **Partially, but only as threshold relief.** It is not a family-semantic rewrite.

- **Are reclaim/retest and reversal still judged by trend-style policy in practice?**  
  **Yes.** The live suppressor keys and the code both show that they still pass through generic MTF semantics.

---

## 9. Best narrow corrective actions

Ordered by likely business impact.

### 1. Make reclaim/retest MTF genuinely thesis-aware

**Problem:** reclaim/retest currently gets threshold relief but still generic trend-style MTF semantics. FAR and SR flip are being judged as if they were plain trend-alignment trades.

**Change:** keep the family cap, but change the family’s MTF pass logic to treat reclaimed structure / role-flip confirmation as primary, with trend alignment as supporting evidence rather than the dominant semantic.

**Why narrow:** only reclaim/retest family; no global MTF loosening.

### 2. Stop reclaim/retest geometry from selecting only the tightest survivors

**Problem:** reclaim/retest candidates are repeatedly rejected or distorted by the combination of 1.5% cap, near-zero floor, and tight-price rounding.

**Change:** keep the universal scalp guardrails, but add a narrow reclaim/retest geometry branch that rejects “impossible” micro/tight-price structures earlier and preserves valid structural stops where they are inside doctrine, instead of letting them oscillate between near-zero and capped states.

**Why narrow:** only reclaim/retest geometry path; no global SL cap increase.

### 3. Add first-breach telemetry for live duration truth

**Problem:** current monitoring cannot distinguish “failed in 8 seconds but recorded at 181 seconds” from “actually held 3 minutes.”

**Change:** store first SL-touch / TP-touch timestamps separately from terminal close timestamp, and report both raw seconds and rounded presentation minutes.

**Why narrow:** telemetry-only; no trading policy change.

### 4. Fix scoring under-credit only where generator doctrine already proves intent

High-confidence scoring mismatches:
- `DIVERGENCE_CONTINUATION` should have trend affinity because its generator only runs in `TRENDING_UP/DOWN`
- `QUIET_COMPRESSION_BREAK` should have quiet/ranging affinity because its generator only runs there
- `LIQUIDATION_REVERSAL` / `FUNDING_EXTREME_SIGNAL` need regime-affinity treatment for their natural order-flow states

**Why narrow:** scoring table alignment, not broad score loosening.

### 5. Add explicit observability for evaluator non-generation by path

**Problem:** current funnel telemetry starts at `generated`; when a path never emits a raw signal, runtime evidence is sparse.

**Change:** count evaluator attempts / non-generation reasons per internal `360_SCALP` method.

**Why narrow:** observability-only; it reduces future audit uncertainty without changing doctrine.

---

## 10. What should not be changed

- **Do not globally lower the 65 paid-signal floor.** That would increase weak path throughput without solving timing/geometry truth.
- **Do not broadly loosen spread protection.** `pair_quality:spread` is one of the few clearly correct scalp protections in the live snapshot.
- **Do not remove the 180-second minimum lifespan without adding first-breach telemetry first.** Otherwise you change behavior without understanding how much of the 3-minute issue is real vs artifact.
- **Do not globally exempt reversal/reclaim from all MTF.** The problem is semantic mismatch, not that higher-timeframe context is useless.
- **Do not widen the 1.5% scalp cap for the whole channel.** The issue is path-specific geometry handling and symbol fit, not a universal need for wider scalp stops.

---

## 11. PR recommendations

## PR 1 — Reclaim/retest downstream policy alignment

- **Exact problem:** `SR_FLIP_RETEST` and `FAILED_AUCTION_RECLAIM` are still evaluated by generic trend-style MTF semantics, causing high family/setup-specific MTF suppression despite PR-1 threshold relief.
- **Exact change:** implement a reclaim/retest-specific MTF evaluator branch and corresponding telemetry that scores reclaimed structure / role-flip confirmation as primary evidence, while keeping current hard protections for clearly contradictory HTF direction.
- **Explicit non-scope:** no global MTF threshold reduction; no changes to other families.
- **Validation criteria:** live suppressor counts for `mtf_gate_family:360_SCALP:reclaim_retest`, `mtf_gate_setup:...:SR_FLIP_RETEST`, and `...:FAILED_AUCTION_RECLAIM` fall materially without broad increase in low-score/watchlist emissions.

## PR 2 — Reclaim/retest geometry integrity hardening

- **Exact problem:** reclaim/retest candidates are repeatedly lost or distorted by near-zero rejection / cap interaction after evaluator-authored structural stops are preserved.
- **Exact change:** add path-aware pre-validation and price-scale sanity for reclaim/retest geometry so invalid micro/tight-price structures are rejected cleanly, while valid in-doctrine structural stops are preserved without avoidable cap/rounding distortion.
- **Explicit non-scope:** no channel-wide SL cap increase; no blanket stop widening.
- **Validation criteria:** `geometry_rejected_risk_plan:360_SCALP:reclaim_retest`, near-zero warnings, and repeated 1.96%/2.09%/2.40%/2.80% cap churn fall materially; emitted reclaim/retest trades no longer cluster around ambiguous tight-stop outcomes.

## PR 3 — Lifecycle truth telemetry for fast failures

- **Exact problem:** the system records hold duration only at terminal handling time, so sub-minute or seconds-level failures collapse into the first 3-minute eligibility window.
- **Exact change:** record first SL-touch / TP-touch timestamps, preserve raw seconds in performance history, and update monitor scripts to print both raw and rounded duration.
- **Explicit non-scope:** no change to trade-management logic, no change to minimum lifespan yet.
- **Validation criteria:** monitor output can distinguish first-breach time from terminal close time, and audits no longer need to infer whether `3m` means real hold vs lifecycle compression.

---

## 12. Confidence / uncertainty

## Proven from current code + live monitor evidence

- Live expression is concentrated in `TREND_PULLBACK_EMA` and `SR_FLIP_RETEST` (`monitor/latest.txt@monitor-logs:137-142`).
- Reclaim/retest suffers repeated live MTF suppression and repeated live risk-plan geometry rejection (`monitor/latest.txt@monitor-logs:65-82, 261-266, 289-314`).
- Reversal still suffers live MTF suppression (`monitor/latest.txt@monitor-logs:65-82, 291-314`).
- MTF family-awareness is threshold-only, not semantic (`src/scanner/__init__.py:333-373, 2722-2798`).
- Hold duration reporting is materially compressed by the 180-second minimum lifespan, 5-second polling, and minute rounding (`config/__init__.py:944, 1034-1042`; `src/trade_monitor.py:249-280, 545-559, 986-1008`; `scripts/monitor_sl_followthrough.py:59-64, 191-227`).
- The two expressive paths have weak live quality, with many near-immediate SLs and very low MFE (`monitor/latest.txt@monitor-logs:145-252`).

## Strong inference, but not fully proven by the current monitor snapshot

- Most of the other silent families are silent primarily because they are not generating, rather than because the scanner is killing large numbers of raw candidates. This is strongly supported by evaluator code strictness and the absence of their suppressor signatures in the current monitor snapshot.
- Same-direction arbitration is likely amplifying path concentration toward trend-native survivors, although the snapshot does not expose per-cycle raw same-direction candidate sets.
- Some repeated short-side SL cap warnings likely come from structurally-authored short breakout/reclaim candidates on tight-price symbols, but the snapshot does not attribute each warning to a named setup.

## What still needs runtime confirmation

- Path-level **non-generation counters** per internal `360_SCALP` evaluator.
- Path-level **pre/post-arbitration candidate mixes** to quantify survivability bias directly.
- First-breach timestamps to separate true seconds-level failures from 3-minute lifecycle compression.
- Exact setup attribution for recurring cap / near-zero geometry warnings.

---

## Final conclusion

The engine is not broken in one place. It is **funnel-misaligned**.

- **Most silent paths** are either correctly rare or are still under-credited / mis-gated after generation.
- **The two expressive paths** are surviving because they best fit current trend/MTF/scoring doctrine, not because they are proving strongest live quality.
- **The 3-minute pattern** is both a real fast-failure signature and a lifecycle-reporting compression artifact.
- **The best next fixes are narrow:** reclaim/retest MTF semantics, reclaim/retest geometry integrity, and first-breach telemetry.

That is the shortest path to improving both **quality** and **path expression** without globally loosening the engine.
