# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `4183` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 38 | 38 | 38 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 682 | 682 | 682 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 3868 | 3868 | 3401 | 17 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1592681 | 1592643 | 38 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1592681 | 1591999 | 682 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1592681 | 1588813 | 3868 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1592681 | 1514793 | 77888 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1592681 | 1585890 | 6791 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1592681 | 1592681 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1592681 | 1592681 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1592681 | 1592681 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1592681 | 1583081 | 9600 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1592681 | 1521111 | 71570 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1592681 | 1511335 | 81346 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1592681 | 1592675 | 6 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1592681 | 1592380 | 301 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 1592681 | 1592681 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 77888 | 77888 | 65498 | 35 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 6791 | 6791 | 6791 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 81346 | 81346 | 70015 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 9600 | 9600 | 8608 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 71570 | 71570 | 31758 | 119 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 6 | 6 | 5 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 301 | 301 | 299 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1592643): regime_blocked=743025, breakout_not_found=526441, basic_filters_failed=223740, retest_proximity_failed=96324, volume_spike_missing=3061, ema_alignment_reject=41, missing_fvg_or_orderblock=11
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1591999): regime_blocked=1029765, sweeps_not_detected=206183, basic_filters_failed=166450, ema_alignment_reject=160659, adx_reject=24595, momentum_reject=3763, reclaim_confirmation_failed=533, rsi_reject=51
- **EVAL::DIVERGENCE_CONTINUATION** (total=1588813): regime_blocked=1029765, cvd_divergence_failed=313534, basic_filters_failed=166450, missing_cvd=55508, ema_alignment_reject=14690, retest_proximity_failed=8865, missing_fvg_or_orderblock=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1514793): auction_not_detected=539830, basic_filters_failed=451674, regime_blocked=284876, reclaim_hold_failed=132988, tail_too_small=104974, rsi_reject=451
- **EVAL::FUNDING_EXTREME** (total=1585890): funding_not_extreme=1046102, basic_filters_failed=506532, rsi_reject=12703, ema_alignment_reject=11744, missing_funding_rate=6526, momentum_reject=1821, cvd_divergence_failed=460, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=1592681): cascade_threshold_not_met=1047831, basic_filters_failed=508930, cvd_divergence_failed=35907, rsi_reject=13
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1592681): feature_disabled=1592681
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1592681): regime_blocked=1029765, breakout_not_found=211212, basic_filters_failed=166450, ema_alignment_reject=160659, adx_reject=24595
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1583081): regime_blocked=847792, basic_filters_failed=285224, breakout_not_detected=268188, compression_not_detected=156368, rsi_reject=16570, missing_fvg_or_orderblock=5315, macd_reject=3624
- **EVAL::SR_FLIP_RETEST** (total=1521111): basic_filters_failed=446114, retest_out_of_zone=411493, regime_blocked=284876, flip_close_not_confirmed=182125, reclaim_hold_failed=153185, wick_quality_failed=16522, insufficient_candles=10321, missing_fvg_or_orderblock=9741, rsi_reject=5188, ema_alignment_reject=1546
- **EVAL::STANDARD** (total=1511335): momentum_reject=443675, basic_filters_failed=404910, adx_reject=273460, sweeps_not_detected=189191, ema_alignment_reject=150949, macd_reject=17160, insufficient_candles=16668, invalid_sl_geometry=8441, rsi_reject=6876, htf_ema_reject=5
- **EVAL::TREND_PULLBACK** (total=1592675): regime_blocked=1029765, basic_filters_failed=162275, ema_not_tested_prev=161759, ema_alignment_reject=160636, no_ema_reclaim_close=29654, body_conviction_fail=17131, rsi_reject=12702, prev_already_above_emas=9493, insufficient_candles=8392, ema21_not_tagged=490, no_prev_high_break=356, prev_already_below_emas=17, no_prev_low_break=2, missing_fvg_or_orderblock=2, momentum_flat=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1592380): regime_blocked=743025, breakout_not_found=369066, retest_proximity_failed=237394, basic_filters_failed=223740, volume_spike_missing=19134, ema_alignment_reject=11, rsi_reject=7, missing_fvg_or_orderblock=3
- **EVAL::WHALE_MOMENTUM** (total=1592681): momentum_reject=849656, regime_blocked=743025

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 865317 | 44.3% |
| TRENDING_UP | 704205 | 36.0% |
| VOLATILE | 371832 | 19.0% |
| TRENDING_DOWN | 11885 | 0.6% |
| RANGING | 1891 | 0.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **4456**
- Average confidence gap to threshold: **18.81** (samples=4456) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=1299, SIRENUSDT=525, TRXUSDT=428, ZENUSDT=380, EWYUSDT=321, FILUSDT=271, ONDOUSDT=237, WLFIUSDT=230, SOLUSDT=101, 币安人生USDT=88

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 130 |
| DIVERGENCE_CONTINUATION | kept | watchlist_tier_keep | 353 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 6051 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 691 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 5743 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 10064 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 885 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 593 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 420 |
| QUIET_COMPRESSION_BREAK | kept | watchlist_tier_keep | 1 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 2287 |
| SR_FLIP_RETEST | filtered | min_confidence | 1759 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 8742 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 71 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 1 |
| VOLUME_SURGE_BREAKOUT | kept | watchlist_tier_keep | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 130 | 49.05 | 80.00 | 30.95 | 20.73 | 19.91 | 19.90 | 1.24 | 4.43 |
| DIVERGENCE_CONTINUATION | kept | 353 | 50.95 | 50.00 | -0.95 | 20.81 | 19.90 | 20.00 | 0.25 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 6742 | 66.06 | 78.46 | 12.40 | 19.92 | 19.60 | 14.00 | 4.21 | 1.71 |
| FAILED_AUCTION_RECLAIM | kept | 5743 | 50.31 | 50.00 | -0.31 | 23.12 | 18.00 | 14.00 | 1.00 | 5.99 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 10949 | 70.15 | 78.79 | 8.64 | 21.04 | 19.16 | 15.20 | 3.02 | 0.46 |
| QUIET_COMPRESSION_BREAK | filtered | 1013 | 53.51 | 71.22 | 17.71 | 19.47 | 18.74 | 15.86 | 0.00 | 3.62 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 53.70 | 50.00 | -3.70 | 21.60 | 20.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 4046 | 47.31 | 71.52 | 24.21 | 21.71 | 20.00 | 15.22 | 1.61 | 4.43 |
| SR_FLIP_RETEST | kept | 8813 | 56.22 | 50.24 | -5.98 | 21.30 | 20.00 | 15.20 | 1.21 | 10.96 |
| TREND_PULLBACK_EMA | kept | 1 | 80.50 | 80.00 | -0.50 | 20.20 | 18.90 | 17.70 | 5.50 | 0.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 68.50 | 80.00 | 11.50 | 21.40 | 20.00 | 16.00 | 1.50 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 53.50 | 50.00 | -3.50 | 22.90 | 19.10 | 20.00 | 1.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 130 | 49.05 | 25.00 | 18.00 | 3.00 | 10.28 | 5.00 | 4.81 | 1.24 |
| DIVERGENCE_CONTINUATION | kept | 353 | 50.95 | 24.93 | 18.00 | 3.01 | 10.01 | 5.00 | 4.71 | 0.25 |
| FAILED_AUCTION_RECLAIM | filtered | 6742 | 66.06 | 23.12 | 14.00 | 3.15 | 10.22 | 7.81 | 7.41 | 4.21 |
| FAILED_AUCTION_RECLAIM | kept | 5743 | 50.31 | 17.00 | 14.00 | 3.00 | 11.00 | 5.00 | 5.30 | 1.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 10949 | 70.15 | 24.31 | 14.00 | 3.16 | 12.15 | 7.79 | 6.76 | 3.02 |
| QUIET_COMPRESSION_BREAK | filtered | 1013 | 53.51 | 18.23 | 18.00 | 3.63 | 15.29 | 5.70 | 4.34 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 53.70 | 17.00 | 8.00 | 3.00 | 17.00 | 5.00 | 3.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 4046 | 47.31 | 19.27 | 12.28 | 3.73 | 13.64 | 5.03 | 6.03 | 1.61 |
| SR_FLIP_RETEST | kept | 8813 | 56.22 | 15.96 | 18.00 | 3.08 | 11.09 | 7.93 | 9.93 | 1.21 |
| TREND_PULLBACK_EMA | kept | 1 | 80.50 | 17.00 | 18.00 | 3.00 | 17.00 | 10.00 | 10.00 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 68.50 | 17.00 | 18.00 | 3.00 | 14.00 | 8.00 | 10.00 | 1.50 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 53.50 | 2.00 | 18.00 | 6.00 | 11.00 | 5.00 | 10.00 | 1.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 130 | 49.05 | 0.00 | 0.00 | 4.43 | 0.00 | 0.00 | 0.00 | **4.43** |
| DIVERGENCE_CONTINUATION | kept | 353 | 50.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 6742 | 66.06 | 0.00 | 0.00 | 1.03 | 0.00 | 0.09 | 0.00 | **1.12** |
| FAILED_AUCTION_RECLAIM | kept | 5743 | 50.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 10949 | 70.15 | 0.00 | 0.00 | 0.46 | 0.00 | 0.00 | 0.00 | **0.46** |
| QUIET_COMPRESSION_BREAK | filtered | 1013 | 53.51 | 0.08 | 0.00 | 0.17 | 0.00 | 0.22 | 0.00 | **0.47** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 53.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 4046 | 47.31 | 0.03 | 0.00 | 0.07 | 0.00 | 0.09 | 0.00 | **0.19** |
| SR_FLIP_RETEST | kept | 8813 | 56.22 | 0.00 | 0.00 | 2.85 | 0.00 | 0.00 | 0.00 | **2.85** |
| TREND_PULLBACK_EMA | kept | 1 | 80.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 68.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 53.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=5 (50.0%) | PREMATURE=0 (0.0%) | NEUTRAL=5 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 5 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| momentum_loss | 5 | 0 | 5 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 2 | 0 | 2 | 0 |
| SR_FLIP_RETEST | 3 | 0 | 3 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `7995912`
- `Path funnel` emissions: `265`
- `Regime distribution` emissions: `265`
- `QUIET_SCALP_BLOCK` events: `4456`
- `confidence_gate` events: `37793`
- `free_channel_post` events: `8`
- `pre_tp_fire` events: `1`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **1**
- Avg resolved threshold: **0.350%** raw → avg net **+2.80%** @ 10x
- Avg time-to-fire from dispatch: **48s**
- By threshold source: static=1

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| TREND_PULLBACK_EMA | 1 | 0.350% | +2.80% | 48 | static=1 |
- Top symbols: SKYAIUSDT=1

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **8**

| Source | Count |
|---|---:|
| regime_shift | 6 |
| pre_tp | 1 |
| signal_close | 1 |

- By severity: HIGH=8

## Dependency readiness
- cvd: presence[absent=240493, present=1352188] state[empty=240493, populated=1352188] buckets[many=572082, none=240493, some=780106] sources[none] quality[none]
- funding_rate: presence[absent=6526, present=1586155] state[empty=6526, populated=1586155] buckets[few=1586155, none=6526] sources[none] quality[none]
- liquidation_clusters: presence[absent=1592681] state[empty=1592681] buckets[none=1592681] sources[none] quality[none]
- oi_snapshot: presence[absent=177, present=1592504] state[empty=177, populated=1592504] buckets[few=702, many=1587342, none=177, some=4460] sources[none] quality[none]
- order_book: presence[absent=87122, present=1505559] state[populated=1505559, unavailable=87122] buckets[few=1505559, none=87122] sources[book_ticker=1505559, unavailable=87122] quality[none=87122, top_of_book_only=1505559]
- orderblocks: presence[absent=1592681] state[empty=1592681] buckets[none=1592681] sources[not_implemented=1592681] quality[none]
- recent_ticks: presence[absent=119434, present=1473247] state[empty=119434, populated=1473247] buckets[many=1473247, none=119434] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `0.9086143970489502` sec
- Median create→first breach: `49.18510413169861` sec
- Median create→terminal: `641.3619529008865` sec
- Median first breach→terminal: `0.21996188163757324` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 100.0}, "under_180s": {"count": 1, "pct": 100.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 100.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 5 | 5 | 0.0 | 0.0 | 0.0 | -0.1748 | None | 643.4388978481293 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 49.18510413169861 | 49.40506601333618 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 71570 | 119 | 31758 | 0.0 | 0.0 | None | 643.4388978481293 | 39812 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 6 | 1 | 5 | 0.0 | 0.0 | 49.18510413169861 | 49.40506601333618 | 1 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `12`
- Gating Δ: `41868`
- No-generation Δ: `1115637`
- Fast failures Δ: `1`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.2109, "current_avg_pnl": -0.1748, "current_win_rate": 0.0, "previous_avg_pnl": 0.0361, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 24, "geometry_changed_delta": 0, "geometry_preserved_delta": 6007, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 36.41, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 49.19, "median_terminal_delta_sec": 49.41, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
