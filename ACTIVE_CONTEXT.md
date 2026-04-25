# ACTIVE CONTEXT
*Updated: 2026-04-25 — Fresh start session*

---

## Current Phase
**Phase 1 — Signal Quality Validation**  
Engine is live, all bug fixes deployed, no paying subscribers yet.  
Current focus: confirm candle OHLC SL/TP fix is working, then diagnose path silence.

---

## Current Priority (Do This First)

**Run the VPS monitor** after 6-12 hours of the candle OHLC fix running.  
Share the zip in the Project chat.  

What to look for:
- Breach cluster at 30-60s should drop below 20% (was 88.9%)
- No phantom TP hits (signals closing within seconds)
- Signals holding open 2-20 minutes before resolution
- FAILED_AUCTION_RECLAIM still the strongest path

---

## All Confirmed Bug Fixes (Deployed to main branch — verified on fresh download 2026-04-25)

| Fix | File |
|---|---|
| MIN_LIFESPAN 180s → 30s | `config/__init__.py` |
| WS fallback limit=2, raw[0] | `src/websocket_manager.py` |
| EXPIRED outcome label | `src/performance_metrics.py` |
| OI readiness present=count>0 | `src/scanner/__init__.py` |
| Indicator cache includes candle count | `src/scanner/__init__.py` |
| OI backfill at boot (30 snapshots) | `src/order_flow.py` |
| TREND_PULLBACK_EMA confirmation entry | `src/channels/scalp.py` |
| Universal SL minimum 0.80% | `src/scanner/__init__.py` (_enqueue_signal) |
| SL minimum (0.50, 0.80) all channels | `config/__init__.py` |
| TP confirmation buffer 0.05% | `src/trade_monitor.py` |
| WATCHLIST spam disabled | `src/signal_router.py` |
| SL/TP uses 1m candle HIGH/LOW | `src/trade_monitor.py` |
| ATR minimum SL in evaluators | `src/channels/scalp.py` |

---

## Known Live Issues

1. **30-60s breach cluster** — was 88.9% before candle OHLC fix. Fix just deployed. Need data.
2. **SR_FLIP_RETEST 100% SL rate** — direction reads correct but SL geometry still structurally tight
3. **10 of 14 paths silent** — MTF gate dominant suppressor, low market volatility, wide spreads
4. **stop_loss = 0.00000 in performance records** — SignalRecord missing stop_loss field
5. **Signal volume ~0.45/hour** — low but correct given current market conditions

---

## Next PR Queue

| Priority | Task | Scope |
|---|---|---|
| 1 | Confirm candle OHLC fix via monitor data | Observation only |
| 2 | Add stop_loss field to SignalRecord | Small — 3 files |
| 3 | SR_FLIP_RETEST SL geometry diagnosis | Investigate before fixing |
| 4 | Per-evaluator silent path diagnosis | Observability |
| 5 | Signal volume recovery — targeted MTF exemptions | Discuss first |

---

## Open Risks

- Candle OHLC fix may not cover all TP check paths — verify TP1/TP2 short checks specifically
- SR_FLIP_RETEST direction reads are correct but exits are wrong — risk of user distrust if continues
- Low signal volume means slow feedback loop — each fix takes 24-48h to validate
- 10 silent paths means the system is underperforming its design intent

---

## How to Raise Issues in Project Chat

- Share monitor zip → CTE analyzes and responds with findings + action
- Share Telegram screenshots → CTE reads timing, prices, compares to chart
- Describe what you observed → CTE reads the actual code before proposing any fix

---

*Read alongside OWNER_BRIEF.md at every session start.*  
*Update this file at every session end.*
