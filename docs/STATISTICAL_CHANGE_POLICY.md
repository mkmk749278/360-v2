# Statistical Change Policy

*Audit finding F-16 (2026-07-10). This is a doctrine document — it binds CTE
sessions the same way OWNER_BRIEF Hard Limits do. Its purpose is to stop the
overfitting treadmill: strategy changes shipped weekly on windows of 10–85
trades are partially fits to last week's regime, and they also reset the
measurement clock that the product's credibility depends on.*

## The rules

1. **Minimum evidence for a live strategy change.** No gate, scoring, exit,
   or sizing change goes live (flag flipped ON) unless the supporting window
   has **≥ 200 closed signals in the affected cohort(s) AND spans ≥ 21
   days**, whichever is later. Wilson lower bounds do not exempt a decision
   from this rule — a bound on n=15 is still a guess.

2. **Safety exemption — narrow.** Fixes for *incorrect behaviour* (frozen
   prices, phantom trades, naked positions, accounting bugs) ship immediately
   as always. The test: "is this change making the system do what it was
   already supposed to do?" If yes → safety fix. If it changes *what the
   strategy is* → rule 1 applies.

3. **One change-set per window.** Do not stack a second strategy change onto
   a window that is still accumulating evidence for the first — attribution
   dies. Queue it.

4. **The frozen control.** The paper book runs a **frozen reference
   configuration** (engine defaults as of the freeze date) permanently,
   regardless of what the live config does. Every live change is judged
   against this control, not against last week. (Until per-config paper
   cohorts exist, the shadow-flag OFF-state logging serves this role — every
   ACTIVE flag must keep shadow-logging its OFF counterfactual, which #707
   already established as the pattern.)

5. **Proof-window discipline.** When a formal proof window is declared (the
   60–90-day / ≥500-signal run required before quantitative marketing
   claims), **no strategy changes ship at all** except rule-2 safety fixes,
   which are logged in the window's caveats.

6. **Report the stats that matter.** Any analysis used to justify a change
   must report: n, window dates, net-of-fees expectancy **with a 95% CI**,
   win rate, profit factor, and max drawdown of the affected cohort. "It
   flipped positive" without a CI is not evidence.

## Why this exists (the receipts)

- The #702 "verdict" was drawn on 85 signals over 3 days straddling the merge.
- The cohort gate arms at n=10 per cohort — a coin flipped 10 times.
- Exit policy changed 4 times in 6 weeks (S34 TP1-full → S43 BE re-tune →
  S45 mover runner → S46 BE arm cap), each justified on the prior week's
  regime, while the long-window book stayed negative.
- The scorer's band inversion was itself discovered because *enough data
  finally accumulated* — patience found what iteration hid.

## Interaction with existing doctrine

This policy tightens, never loosens, the Production-phase dark-flag-first
rules in `CLAUDE.md § Project Phase`. Owner sign-off is still required where
it was before; this adds the evidence bar that a sign-off request must meet.
The owner may explicitly override this policy for a specific change — the
override and its rationale get recorded in `ACTIVE_CONTEXT.md`.
