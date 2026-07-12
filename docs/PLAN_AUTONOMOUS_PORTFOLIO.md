# Plan — Autonomous Regime-Adaptive Strategy Portfolio

*The approved implementation plan. Companion to
`docs/HANDOFF_AUTONOMOUS_PORTFOLIO.md` (execution status + exact insertion points) and
the Crypto Market Doctrine (the "why").*

---

## Context — why this exists

Signal **volume collapsed** (~48/day → ~7–12/24h). Session 44 already attributed it to
the *intended compounding of owner-approved gates* (cohort-edge, macro-dir, expiry-OFF
holding the book, dup-guard, loss-streak) plus the **QUIET-regime 1.8× penalty
multiplier** in a market that's been ~70% ranging/quiet.

The owner's steer: **reducing volume is not the same as good quality — the good setups
have to actually fire.** And the deeper reframe (Crypto Market Doctrine): we've been
building a *fast retail taker* — scoring indicators blindly and firing directional
scalps with fixed-% stops that sit inside crypto's noise band. The durable edge in crypto
is **structural** (selectivity, phase/session/tier awareness, noise-sized stops,
maker-side, funding/basis), not predictive frequency.

The owner also rejected slow ship-one-wait-tune-repeat: as a **one-person shop** it must
be **autonomous and self-maintaining** — many strategies running in parallel in shadow on
real data, viewable in ops, with the engine **switching/weighting strategies dynamically**
by market context.

**Intended outcome:** a self-driving portfolio that measures every strategy's real edge
per market context, lets an autonomous allocator route to what works *now*, and stays
inside the existing safety envelope on live user money — so good setups fire and bad ones
don't, without manual babysitting.

---

## The one rail that never moves (CLAUDE.md Hard Limits)
Autonomy runs **free in shadow**. On **live user money** it operates **inside the
existing safety envelope** — blast-radius caps, per-user/global circuit breakers,
naked-position invariant, kill switch — and the autonomous *live* promoter is **armed
once** by the owner (master switch), then self-runs. Kill switch overrides everything.
This keeps it hands-off without ever putting user capital outside the guardrails.

---

## Architecture — six layers

**A. Market-Context Engine** `src/market_context.py` — the "what regime is it *now*"
vector. Cached per scan (no hot-path network reads): Wyckoff **phase** per TF, **BTC
dominance/rotation** (BTC-led vs alt-season), **session/kill-zone**
(Asia/London/NY/overlap/weekend), **season/calendar** (funding clock, expiry, weekend),
**volatility & cascade** regime, **funding/basis** regime. This vector is the key
everything else routes on.

**B. Strategy Portfolio** — every strategy a uniform pluggable unit: `entry logic +
geometry policy (incl. ATR/structure-stop variants) + context-affinity tag`. Existing
15+ evaluators wrapped as units; new ones (range-fade at VAH/VAL, funding/basis carry,
mean-reversion, cascade-reversal) drop in without core surgery.

**C. Continuous Shadow/Paper Measurement** — the real-data backbone. **Every strategy
emits into a paper/shadow ledger continuously**, regardless of live state (built on
`paper-trade-frozen-signals` #709 + `CohortEdgeStore` + `invalidation_audit` + the new
`suppression_audit`). Produces the live **Strategy × Context → edge** matrix (win%, EV in
R net of fees, MFE capture, drawdown) on real data. Zero user impact.

**D. Autonomous Allocator / Router** `src/strategy_allocator.py` — reads **A (current
context) × C (each strategy's measured edge in this context)** → decides **which
strategies are active and their weight/size now**, switching dynamically as context
changes and edges drift. **Auto-promote** shadow→live-eligible on an edge+sample floor;
**auto-demote** on edge decay. Runs first in **recommendation mode** (logs would-do,
changes nothing) → armed to live once its decisions are visibly good. Bounded by Layer E.

**E. Safety Envelope** (always on) — existing caps/breakers/kill-switch/naked-position
invariant, plus new **per-strategy live capital cap**, **max concurrent live strategies**,
and the **single owner master-arm** for autonomous live promotion. Demotion always
allowed; promotion gated by these limits.

**F. Ops Observability** (`mkmk749278/360ce-ops`) — the one-person control surface:
current **context vector**, the **Strategy×Context edge matrix** on real data, each
strategy's **shadow/live state + allocation + rolling PnL**, the allocator's **decisions
and the why**, master-arm + per-strategy overrides + kill switch.

---

## Execution order (parallel-first, not serial)

**Phase 1 — Backbone + get ALL strategies into ops shadow fast (off money path)**
1. `market_context.py` (Layer A) + stamp the context vector on every signal. ✅ **DONE**
2. Strategy interface (Layer B) — wrap existing evaluators as portfolio units + affinity
   tags.
3. Continuous shadow ledger (Layer C): `suppression_audit.py` ✅ **DONE (module)** +
   paper-emit every strategy's would-be trades + the **Strategy×Context edge matrix**
   store (`strategy_edge.py` ✅ **DONE**). Remaining: scanner stamps + classify loop +
   edge feed + truth-report sections.
4. Ops (Layer F v1): context panel + edge matrix + per-strategy shadow PnL, real data.
5. Cross-cutting: **Telegram→app-push decouple** (`signal_router.py` ~922–1029), and
   **register knobs/flags in `runtime_tunables.py`** for live ops control.
   → *Ships normally; nothing about live output changes; owner sees every strategy
   competing on real data in ops.*

**Phase 2 — Allocator in recommendation mode (observe-only, money path but OFF)**
6. `strategy_allocator.py` (Layer D) decides + logs allocations from context×edge, changes
   nothing live — shown in ops as "what it would do." Safety envelope (Layer E) enforced
   in the recommendation math. → *Observe; confirm switching tracks session/phase/season.*

**Phase 3 — New strategies + geometry, all measured in parallel (dark)**
7. Add missing strategy families (range-fade, funding/basis, mean-reversion,
   cascade-reversal) — enter shadow immediately, appear in the matrix.
8. **ATR/structure stop geometry** as a selectable geometry policy (size scaled to hold
   risk constant; stop beyond the liquidity pool) — A/B'd in shadow against fixed-% per
   strategy so the matrix shows which geometry wins per context. *(Biggest edge lever.)*
   → *All competing on real data at once — no serial waiting.*

**Phase 4 — Arm autonomy (owner master-switch, then hands-off)**
9. Owner flips the **master-arm**; the allocator promotes/weights/demotes strategies live
   within the safety envelope, self-adjusting to context and edge decay. Kill switch +
   caps always override.

---

## Non-negotiables carried through every phase
- **Wired end-to-end, no scaffolds** — each layer stores *and* consumes in the same change.
- **Cost discipline** — context + matrix cached & invalidation-gated; no new
  per-tick/per-scan network or Firestore reads.
- **Everything measured before it's trusted** — shadow/paper edge on real data gates any
  live promotion; the allocator's own decisions observed in recommendation mode first.
- **§3.6a scoring honesty** — a strategy is scored on the evidence that defines it.

## Verification
- Full pytest green + new suites per layer; `ruff` + `mypy` clean; syntax check pre-commit.
- **Ops real-data proof at each phase**: context vector correct vs the clock/market; edge
  matrix populating from real shadow trades; allocator recommendations tracking context;
  safety-envelope caps demonstrably binding in tests.
- Branch `claude/signals-volume-quality-pjep8o`; PR(s) to `main`; `subscribe_pr_activity`.

## The one design default (change at approval if you disagree)
Autonomous **selection + weighting** always run. Autonomous **live promotion** is bounded
by the safety envelope and **armed once** by the owner; a strategy whose live edge decays
is **auto-demoted** without asking. Kill switch and blast-radius caps override autonomy at
all times. (The only way "fully autonomous" and "real user capital, one-person shop"
coexist safely.)
