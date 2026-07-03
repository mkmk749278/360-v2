# BTC-State Graded Haircut — Activation Brief (owner sign-off)

*2026-07-03. Status: shadow-stamping live since #678/#683 (2026-06-30);
activation = one env flip. Scoring-model change → owner sign-off required.*

---

## ⚠️ VERDICT UPDATE (2026-07-03, same day): NO-GO on current evidence

The #675 validator was run against the fresh window (64 real trades, phantoms
excluded, point-in-time candles from the Binance public archive). **The
acceptance test FAILED:**

- The bleeding shorts were BTC-**ALIGNED** at the intraday (5m/15m/1h) horizon:
  22 shorts in the `4_short` bucket ran 14% win / −0.396 avg — essentially the
  whole short bleed — while **counter-trend** shorts (the cohort the haircut
  would tax) ran fine (50–60% win, flat-to-positive).
- Every counterfactual cut made the book worse (−7.66 → −11.4).
- Interpretation: shorts are firing into **intraday BTC dips inside the macro
  recovery** — the intraday state reads "short-favourable" at dispatch, then the
  weekly uptrend resumes and stops them out. The intraday haircut cannot see
  this; the **macro layer** can: 36/36 bled shorts fired against a weekly-BULL
  `macro_direction`, and the book without them is +0.42%.

**Actions taken:** `BTC_STATE_HAIRCUT_ENABLED` stays **OFF** (keep stamping).
A **counter-trend SHORT macro mirror** of the live #683 long gate shipped dark
in #687 (scope: LSR / FAR / BREAKDOWN_SHORT — the 0–20%-win bleeders;
QUIET_COMPRESSION and SR_FLIP shorts excluded as the working cohorts) with
`[SHADOW] CT_SHORT_MACRO_SUPPRESSED` telemetry.

**ACTIVATED 2026-07-03, same day, by explicit owner sign-off** ("Activate now",
AskUserQuestion) — `CT_SHORT_MACRO_GATE_ENABLED` default flipped to `true`,
accepting the single-regime-window caveat. Safety properties relied on: the
gate auto-restores shorts the moment the weekly macro turns down; the flag is
env-reversible on the VPS (`CT_SHORT_MACRO_GATE_ENABLED=false` + engine
recreate); scope excludes the profitable short cohorts. **Watch after
activation** (daily loop check-in): suppression counts via
`grep -c "CT_SHORT_MACRO_SUPPRESS" ` on engine logs, and whether short-side
P&L improves without starving short volume when the macro is genuinely down.

The original haircut brief below stands as reference — re-evaluate it on a
longer window (its per-pair coupling layer may still add value once the macro
mirror handles the side selection).

---

## Why now — the bleed switched sides

Fresh 72h truth window (2026-07-01 → 07-03, 100 closed signals, post-#671/#672/#683):

| Side | n | Total P&L | Win% |
|---|---:|---:|---:|
| LONG | 40 | **−0.71%** (flat) | 30% |
| SHORT | 60 | **−8.53%** | 38% |

The June fixes killed the long bleed (was −25.1%/month). But the market regime
flipped — TRENDING_UP is now 45.4% of cycles (was 20.9%) — and the loss moved to
**counter-trend SHORTs fighting the recovering tape**, the exact mirror of the
June long bleed:

| Cohort | n | Total | Win% |
|---|---:|---:|---:|
| LIQUIDITY_SWEEP_REVERSAL SHORT | 11 | −3.75% | 36% |
| BREAKDOWN_SHORT | 3 | −3.18% | 0% |
| FAILED_AUCTION_RECLAIM SHORT | 9 | −2.33% | 22% |

The live protection (`CT_LONG_MACRO_GATE`, #683) is **longs-only by design** and
cannot catch this. The graded haircut covers **both sides** with the asymmetric
weights the S38 research prescribed.

## What is already built and running

`src/btc_state.py::compute_haircut_factor`, wired at emit in the scanner:

```
factor = clamp(1 − k·|b|·w_pair·side_mult·setup_weight, floor, 1)
```

- `b ∈ [−1,+1]` BTC-State (5m/15m/1h EMA stack + slope + RSI, vol-shrunk)
- `w_pair ∈ [0,1]` per-pair downside coupling (decoupled pairs auto-exempt)
- `side_mult`: counter-trend LONG 1.0, counter-trend SHORT **0.5** (downside asymmetry)
- `setup_weight`: severe reversal setups 1.0, others 0.5
- `floor = 0.55` — never zeroes a signal; aligned signals untouched
- Recomputed at every emit → **auto-restores** as BTC turns (no manual flips)

`BTC_STATE_ENABLED=true` (default) has been **stamping** `btc_state_factor` on
every signal since 2026-06-30 — the shadow window is already accumulating.
`BTC_STATE_HAIRCUT_ENABLED=false` keeps it observe-only.

## Evidence to read before flipping (1 command on the VPS)

Join stamps to outcomes with the #675/#676 backfill on the fresh window:

```bash
docker exec 360scalp-v2-engine python scripts/btc_state_backfill.py \
  --signals /app/data/signal_performance.json \
  --out /app/data/btc_state_backfill.csv
```

Acceptance for activation (mirror of the S38 long-side acceptance, short side):
1. The bleeding counter-trend SHORT cohorts show `factor < 1` stamps (the haircut
   *would have* engaged on them).
2. Aligned SHORTs (e.g. SR_FLIP shorts, −0.44% ≈ breakeven at 50% win) show
   `factor = 1` — the haircut must NOT tax the working cohort.
3. Counterfactual: re-scoring the window with the haircut applied removes more
   losing than winning signals at the 65-confidence gate.

**Data-quality caveat:** 36 of the last 100 records are `EXPIRED_NO_FILL`
phantoms (fixed in this PR). Exclude `EXPIRED_NO_FILL` / zero-hold records from
the counterfactual, or run it on data accumulated after this PR deploys.

## Activation (after sign-off)

```bash
# VPS .env
BTC_STATE_HAIRCUT_ENABLED=true
docker compose -f docker-compose.yml --profile isolated up -d --no-deps --force-recreate engine
```

Tunables if the shadow data argues for it: `BTC_STATE_K` (0.40),
`BTC_STATE_FLOOR` (0.55), `BTC_STATE_CT_SHORT_MULT` (0.5).

## Relationship to the live binary gate

`CT_LONG_MACRO_GATE` (#683) stays as-is during shadow → activation. Once the
graded haircut is proven live (≥1 week), decide whether it subsumes the binary
gate (S38 design intent) or both remain (belt + suspenders). Removing the binary
gate is a separate owner-sign-off decision.
