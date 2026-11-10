# External audit — verified claim by claim (2026-11-10)

The owner supplied a third-party write-up, *"Verdict: Is Your Signal
Production Correct?"*, listing seven code-level defects and a six-step
remediation plan. Every claim was checked against `main` @ 5a071f8 and against
the live box (ops read-only session, 2026-11-10 ~07:00 UTC).

Labels: **[code]** read in the source · **[ran]** executed here ·
**[live]** read off ops / the truth report · **[inferred]** reasoning from those.

## Short answer

- **One claim is new and real** (#1): the risk plan replaces the two mover
  paths' stop and target ladder. The mechanism is confirmed in code, by
  running it, and on the live feed. **The proposed fix is wrong and would
  reject most of the dominant path.**
- **One claim is real and already visible on ops** (#3): the entry-quality cap
  is being spent by one rule. It is an owner tunable decision.
- **Two are our own 2026-10-23 audit, restated** (#4, #6). The owner already
  ruled on them.
- **One describes a deliberate owner directive as a defect** (#5), with a
  mechanism claim that is out of date.
- **One names a true code fact and attributes the wrong effect to it** (#2).
- **One was three false alarms** (#7). Two are fixed in this PR.

Nothing on the money path is changed by this PR.

---

## 1. Risk plan overwrites mover SL/TP — **TRUE; the proposed fix is harmful**

**The mechanism.** `MOVER_TREND_PULLBACK` and `MOVER_AVWAP_SCALP` author a 15m
stop (beyond the MA / anchored VWAP) and a 1.0 / 1.6 / 2.5 R ladder.
`build_risk_plan` then recomputes both for any setup not in
`STRUCTURAL_SLTP_PROTECTED_SETUPS`. Neither mover path is in it. [code]

- [ran] Same synthetic signal (entry 103, authored stop 100.5, TP1 at 1.0R):
  both mover setups come back with stop 101.78 and TP1 at **1.3R**; a protected
  setup keeps 100.5 and 1.0R.
- [live] Every recent MVRTP signal whose stop has not yet been moved shows TP1
  at **1.30–1.50 R**, never 1.0 (9 of 9 such rows in the newest 50 signals).
- [live] Truth report, 30 closed MVRTP: authored stop 3.30% median, shipped
  3.00%, 19 tightened, 10 widened.
- [live] 90 days, MVRTP longs: shipped TP1 sits at a median **~3.95%** from
  entry while the average MFE is **2.35–2.5%**.

`CLAUDE.md` describes MVRTP as *"an MA stop with TPs at fixed 1.0/1.6/2.5
R-multiples"*. That is what the evaluator writes and not what ships.
`performance_tracker.shipped_sl_distance_pct` and the truth report's
"designed vs shipped" caption both named two stages that move the stop and
omitted this one, which is the largest. Both are corrected in this PR.

**Why the proposed fix must not ship.** The write-up says: add both setups to
`STRUCTURAL_SLTP_PROTECTED_SETUPS`. That set does three things, not one:

1. keeps the authored stop and targets (the intent);
2. switches the stop cap from *clamp* to *reject* — the authored stop's median
   is 3.30% against a 3.0% cap, so about half of MVRTP candidates would be
   rejected outright [inferred from the 30 closed rows above + code];
3. leaves the authored 1.0R TP1 to face the 1.2 default R:R floor, which
   rejects it. [ran] A protected setup with this exact geometry returns
   `rr 1.00 below 1.20`.

So the one-line fix removes most of a path that is ~60% of the delivered book.
`tests/test_session_and_geometry_stamps.py::TestMoverGeometryIsReplacedByTheRiskPlan`
pins both halves.

**What is not known.** Whether the authored geometry would do better. The
shipped target is farther than the authored one (≈3.95% vs ≈3.3%), which
argues for the authored one; the 2026-08-01 TP1 study argues that targets on
this book are easy to get wrong in either direction. This is TP/SL shape:
owner sign-off, dark first.

**Shipped here (measurement only).** The closed-signal record now carries
`designed_tp1_distance_pct` (from `Signal.original_tp1`), and the truth report
gains *"TP1 — authored vs shipped"*: per setup, how many authored targets were
nearer, how many were reached, and how many were **rescued** (MFE cleared the
authored target and not the shipped one). The farther direction is counted as
undecidable and draws no figure. Rows start accumulating at deploy; MVRTP
closes ~20 a day (226 in the first ten days of November).

## 2. `execution_quality_check` uses a 5m EMA rule on 15m setups — **code fact true, effect not shown**

- [code] True: the mover and pullback setups fall into the generic branch,
  which requires 5m EMA9 ≥ EMA21 for a long.
- **"Evicts 1,220,744 bottom-of-dip triggers" is a count of scan-cycle
  rejections, not of signals.** The scanner re-evaluates every pair every ~15s,
  so one setup on one symbol is rejected hundreds of times. [live:
  `prescoring_audit` 1,221,130 for all paths since boot]
- **The +0.206% entry drift is real and is not caused by this gate.** [live:
  mean 0.2059% over 2,737 rows] It was measured on 2026-09-26 as the gap
  between the stamped entry and the tape at dispatch
  (`ACTIVE_CONTEXT` "longs research"), and a drift gate was tested and
  rejected there.
- Whether the gate rejects good pullbacks is measurable and unmeasured: the
  gate has stamped into the pre-scoring audit since 2026-10-23 (293 rows held
  for it). Its forward verdict was not read in this session.

No change. Changing an execution gate is an evaluator-path change.

## 3. Entry-quality blast-radius cap is spent by one rule — **TRUE, owner decision**

[live, `/signals/entry-features`] Four rules are enforcing. Over 2,484 judged
candidates:

| Rule | Would remove | Result of the rows it would remove (book +0.13%) | Suppressed |
|---|---|---|---|
| `session_quality` | 1,387 (56%) | +0.02% | 167 |
| `cvd_aligned` | 915 (37%) | **−0.11%** | 0 |
| `mover_stack_15m` | 152 of 2,126 | +0.10% | 0 |
| `profile_reject` | 37 | +0.64% | 0 |

**1,753 held back by the cap.** One rule wants to reject 56% of candidates
against a shared 35% budget, so the gate is over budget most of the time and
the rule with the best evidence (`cvd_aligned`) is credited with nothing.
"Suppressed" attributes a candidate to the first rule that rejects it, so
`cvd_aligned`'s zero is partly ordering. [inferred]

The cap is working as designed; the combination of rules is what does not fit
inside it. Options, all the owner's:

- turn `session_quality` back to shadow (its removed rows are barely worse
  than the book), which frees the budget for `cvd_aligned`;
- or give each rule its own budget (code change, money path, sign-off).

Raising the cap to 0.75 as the write-up suggests would let the gate remove
most of the feed on the strength of the weakest rule.

## 4. SMC scorer is direction-blind; 11 adjustments overwritten — **TRUE, already ruled on**

This is `docs/SCORING_AND_GATE_AUDIT_2026_10_23.md` §2, §3 and §5, restated.
Owner decision of 2026-10-23 (§6): unchanged, because the composite score
barely ranks live outcomes and the SMC gate it would re-arm blocks ~1% of
candidates. Nothing new.

## 5. `BE_THEN_TP1` disables invalidation, "gives back 94% of MFE", SAR stuck dark — **mostly not a defect**

- Invalidation off under the engine-default exit is an **owner directive of
  2026-06-29**, recorded in the code at the line cited. Invalidation is a
  per-user setting.
- "Hits neither TP1 nor the BE ratchet" is out of date: the arm has been
  capped at a fraction of TP1 since 2026-07-10 [code], and **820 of 3,310**
  closes in the last 90 days are break-even exits [live].
- "94% give-back" is average PnL (+0.14%) over average MFE (2.10%). The
  arithmetic is right [live]. MFE is a hindsight maximum that no exit captures
  in full, and the 2026-09-26 research found the exits are not the lever.
- SAR "+2,260%" is the kline-only bake-off, whose own summary says to trust
  the ranking and not the PnL. SAR is measured forward on delivered signals
  (`/signals/sar-live`) and is available per user through the trail governor.
  Promoting it book-wide is an FSM change and the owner's call.

## 6. October small-cap losses; correlated cap per path — **our own findings**

Both come from `docs/MARKET_FIRST_PHASE1_RESULTS_2026_10_23.md` and the
2026-10-23 owner ruling ("per path same signals max 4"). Layer D being
recommendation-only is documented doctrine. Restricting MVRTP to the top 75
pairs is a real option the Phase-1 doc raises; it is a universe change and has
not been decided.

## 7. "Pipeline violations" — **three false alarms; two fixed here**

| Probe | What it said | What was true | State |
|---|---|---|---|
| `auto_dispatch` (362 cycles) | "every user is being silently skipped" | The one keyed user chose CoinDCX. The Binance dispatcher hands them over and counts `venue:coindcx`; CoinDCX attempted every signal [live, `read.dispatch_funnel`, `read.coindcx`]. | **Fixed** — `venue:coindcx` is a deliberate skip. Named exactly, so another venue stays red. |
| `entry_feature_inputs` (364 cycles) | `RANGE_FADE.campaign_prev_won` absent on every stamp | RANGE_FADE never delivers, so every stamp is a first leg (`first_leg×662`). | **Fixed** — an absence wholly explained by `first_leg` is ordinary and is said on the healthy line. |
| `tuned_variants` (364 cycles) | 302 `atr_arm_uncomputable` | Not investigated. | OPEN |

Also seen on the overview and not investigated: `edge_reconciliation`
(BREAKDOWN_SHORT +0.46R against a 0.3 bound), `ai_governor_verdicts`
(7 cycles), `dark_resolution` (1 of 162 rows not advancing, GRAMUSDT).

**A real one behind the false alarm.** The CoinDCX user's entries are all
rejected with `Insufficient funds` [live, `read.coindcx`]. That is the user's
account balance and not an engine fault, but nothing tells the user.

---

## The remediation plan, item by item

| # | Proposed | Verdict |
|---|---|---|
| 1 | Add mover setups to the protected set | **Do not.** Rejects most of the path (§1). Measure first. |
| 2 | Add a 15m branch to the execution check | Evaluator-path change. No evidence yet (§2). |
| 3 | Raise the entry-quality cap to 0.75+ or drop `session_quality` | The second half is reasonable and is one ops switch. The first is not (§3). |
| 4 | Disable five paths; restrict MVRTP to top-75 | Path retirement exists (`/control/routing`); each is an owner click with the path scorecard beside it. |
| 5 | Fix `_score_smc` direction and sweep index | Ruled on 2026-10-23: unchanged. |
| 6 | Promote Parabolic SAR book-wide | FSM change. Forward evidence is on `/signals/sar-live`. |
