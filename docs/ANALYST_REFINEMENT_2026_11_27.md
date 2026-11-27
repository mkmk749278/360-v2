# Analyst refinement — 2026-11-27

The owner uploaded an outside blueprint ("Finalized Senior AI Analyst
Architecture & Engineering Blueprint") and asked for the analyst to be
refined. As on 2026-11-25, each claim was checked before anything was built.
The checks used the live ledger (`plan_outcomes` over `/mcp`, read 2026-11-27)
and the walk's own code.

## The live ledger, as it stood before this change

| Arm | n | win | avg net | w/o top 1% |
|---|---|---|---|---|
| analyst, old headline | 225 | 58.2% | +0.420% | +0.324% |
| ↳ filled only | 139 | 41.0% | **−0.201%** | −0.284% |
| ↳ unfilled, scored at market | 86 | 86.0% | +1.424% | +1.362% |
| tranche, old headline | 225 | 61.8% | +0.606% | +0.512% |
| market | 228 | 63.2% | **+0.098%** | **+0.041%** |
| fixed_rule, old headline | 227 | 29.1% | +0.688% | +0.555% |

Calibration on filled setups (n 139): Brier **0.2123** against a base-rate
Brier of **0.2080**. The stated p(TP1) is **no better than always guessing the
observed hit rate**.

The realized per-posted-setup figure for the analyst arm is
−27.99% over 225 setups, about **−0.124%**. Walk v2 now publishes it as the
headline.

## Claim by claim

| Blueprint claim | Verdict | Evidence |
|---|---|---|
| Unfilled market profits are blended into limit rows | **True, and it was the headline** | Old headline +0.42% against −0.20% for fills. Fixed: realized headline (unfilled = 0.00%), with filled-only and missed-market published beside it. |
| Tranche look-ahead / retroactive blend | **True** | `limit_arm` blended every leg that filled before expiry and walked the blend from the first fill. A leg reached after the target was booked as held from the start. The new test fails on the old code (entry 98.4 where only 99 filled). Fixed. |
| Flat 0.07% without order-type cost or funding | **True** | Fixed beside the flat figure: maker/taker by order type, plus funding from the recorder at each symbol's own settlement times. Some perps settle every 4h, so the blueprint's fixed 00/08/16 grid would have been wrong for them. |
| "Market at submit, N=148, 69.59%, +0.42%" | **False — mislabelled** | +0.42% is the analyst *headline*. The market arm is n 228, +0.098% (+0.041% without the top 1%), at a 0.07% fee that understates a taker entry. |
| Unfilled setups averaged +1.44% "at market", so go immediate | **Wrong direction** | This population is selected: a limit goes unfilled because price ran away from it. The unconditional "enter at market" result is the market arm, which is about break-even. Not adopted. |
| Keep PR #1103's 3-outcome forecast (`p_target`, `p_stop`, `p_neither`) | **Does not exist** | The validator took `p_target` only. The prompt asked for p(stop)/p(neither) inside the free-text `scenario`, where they can't be scored. Added optional structured `p_stop` (p_neither = remainder) and a three-outcome Brier. |
| `partial_runner` arm | Built as **`ladder`** | Half at TP1, half to the analyst's own TP2, original stop, no break-even. The blueprint's trail (confirmed 1h swings or 2.5 × ATR) is a parameter this repo has not chosen; it is not built. |
| `existing_signals` arm | Not built | Still named under `arms_not_built`. It needs a window join to the closed-signal record, not a per-setup walk. |
| Day-clustered summary | Built | `by_arm.*.by_day`. |
| Pullback expiry 2–4h, never 12h | **Measured, not imposed** | `analyst_whatif.expiry_2h / expiry_4h` re-scores the analyst arm with late fills dropped. It is exact, because it only removes fills. |
| Cancel a pending limit once price touches TP1 | **Measured, not imposed** | `tp1_before_fill` is stamped. `cancel_if_tp1_first` re-scores; rows walked before v2 count as unknown. |
| OIPoller −1003 IP ban | Already OPEN in `ACTIVE_CONTEXT` | Not touched here: it is an independent infra change and gets its own watched PR. |
| Submit `≥20s` past clock boundaries; +8–12 bps collar | Not testable on this walk | 5m OHLC cannot resolve seconds. This belongs to a live execution path, which does not exist and is gated on graduation. |

## What prompt v2.5 should and should not change

Apply to the scheduled task only after the engine change has deployed, and
judge it on a fresh window, because the headline moves.

- **Ask for structured `p_stop`** beside `p_target`, plus `prompt_version: "v2.5"`.
- **Read `realized_net_pct`** in `recent_closed`, not `net_pct`. For a
  not-filled row, `net_pct` is the market's outcome, not the analyst's.
- **Do not add an "immediate" execution style yet.** The evidence offered for
  it is the selected population above. If it is wanted, stamp the choice and
  compare the market arm on the setups the analyst tags immediate against the
  analyst arm on the rest. That is a measurement, and it would need its own PR.
- The BTC-exhaustion pre-mortem and a post-mortem citing `recent_closed` are
  prose changes and cost nothing. Fine to include.
- Keep no caps or gates (owner direction 2026-11-25). Every candidate filter
  is stamped and read on the record.

## What changed in the numbers

Every limit arm's headline drops, because unfilled rows now earn 0.00%. The
analyst arm goes from about +0.42% to about −0.12% per posted setup on the
2026-11-27 ledger. Tranche rows with both legs filled are re-walked where bars
still exist (the 5m buffer is ~83h). Older ones are marked
`insufficient / blend_defect_history_rolled_off` and leave the average. The
Desk (`GET /api/desk`, Lumin 2.0) carries the realized figure under the same
keys; the app parses it but does not render it yet.
