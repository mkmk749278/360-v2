# Handoff — Session 77 start

**Written:** 2026-07-23 · **From:** Session 76 (autonomous-system audit + convergence)
**Read this after** `OWNER_BRIEF.md` and `ACTIVE_CONTEXT.md`, then open
`docs/AUTONOMOUS_SYSTEM_AUDIT_AND_REMEDIATION.md` **§0** — that is the design of record.

---

## 1. The one thing you are here to build

The whole autonomous programme has converged to a **single root cause and a single fix**.
Do not re-open the diagnosis; it is closed and code-grounded in §0. Do not propose new
workstreams — every prior idea (W1–W8, the LLM critic, edge-decay) is already folded into
the one umbrella.

**Root cause (proven in code):** a **momentum-shaped emission gate is applied uniformly to
every pair regardless of liquidity cohort.**
- One flat scoring rubric for all pairs — `src/confidence.py` `_SCALP_DEFAULT_WEIGHTS`
  (docstring: channels "raw-sum identically").
- 75 of 100 confidence points are trend/momentum/flow (`smc` 30 + `trend` 25 +
  `order_flow` 20), so mean-revert/range setups **cannot structurally reach the 65 floor**.
- `compute_adaptive_threshold` raises the bar in `RANGING`/`VOLATILE`, lowers it in
  `TRENDING` — momentum-favoring twice over.
- `src/pair_manager.py` auto-promotes TIER3→TIER2 on a volume surge — that promotion path
  **is MVRTP, which is the entire measured −49%.**

Every leak found on the live tape (MVRTP = the whole loss; anti-predictive confidence,
80–100 conf → 7% win; ~20% born-dead entries; 24% breakeven-bleed; choked regular paths
mean_revert 3,253 detected / 2 emitted) is a **facet of that one gate**.

**The fix (≈80% already built, switched OFF):**
> Emission clears on the signal's own `cohort × strategy × context` **net-edge** cell —
> not on the momentum-shaped confidence 65.

That single wire simultaneously: retires net-negative promoted-mover cells (MVRTP drops),
emits net-positive regular cells (volume refilled **with edge** — the answer to "where does
volume come from if we retire MVRTP"), and removes confidence as the gate (so
anti-predictive confidence stops mattering).

---

## 2. What is already done (do not redo)

| Piece | State | Location |
|---|---|---|
| W1 cost-aware R (`net_r`, gross+net on every outcome) | **LIVE in `main`** (`EDGE_COST_MODEL_ENABLED=true`) | `src/trade_costs.py`, merged #770 |
| W2 reconciliation + watchdog (always-net, pages on divergence) | **LIVE in `main`** | `src/strategy_edge.reconcile_matrix`, merged #771 |
| Audit design-of-record + §0 umbrella + status ledger | **merged** (PR #772) | `docs/AUTONOMOUS_SYSTEM_AUDIT_AND_REMEDIATION.md` |
| LLM-critic bridge design (shadow-critic, not inline editor) | **merged** (PR #772) | `docs/LLM_SIGNAL_CRITIC_BRIDGE.md` |
| Pair-cohort classification (MAJOR/MIDCAP/ALTCOIN) | **built, OFF** (`context_emission_cohort_aware`) | `src/pair_cohort.py` |
| Cohort × strategy × context net-edge cells | **built, dual-write OFF** | `src/strategy_edge.py` |
| Emission actuator (relax/suppress on measured edge) | **LIVE, net-aware** | `src/context_emission_policy.py` |

---

## 3. The build (this is the next PR — W3, absorbing W4)

Ship it **end-to-end** (no scaffolds); it is a **money-path scoring change** — kill switch
(`context_emission_*`) + blast-radius caps retained; W2 watchdog validates cohort cells
in-flight. Per standing owner directive ("make everything live, no darks") it activates
live rather than dark, but confirm with the owner before flipping the emission authority,
since this is the one change that redirects *which signals ship*.

1. **Turn on cohort dual-write** at the `strategy_edge` feed points — accumulate
   `cohort_context_key(base, cohort)` cells **in parallel** with base cells (never fragment
   the base matrix). `src/pair_cohort.py` already composes the key; wire it at the three
   feed sites (`trade_monitor.py`, `main.py` — see the W1 `gross_r_multiple` feed sites,
   same call sites).
2. **Make the emission bar cohort-aware** in `context_emission_policy.py` — read the
   `cohort × strategy × context` net cell; fall back to the base cell while the cohort cell
   is under the n-floor. A signal emits when its cohort cell's net edge clears, **replacing**
   the momentum-confidence-65 as the emission authority (confidence can remain a tiebreak /
   display, not the gate).
3. **Retire net-negative promoted-mover cells** through the same policy (no separate switch)
   — MVRTP's promoted cells fall below the bar and self-suppress.
4. **Land the two detector axes with it:**
   - `+ax1` confidence-bucket dimension on the edge matrix (off-money-path telemetry).
   - `+ax2` MFE/MAE stamp per signal → into reconciliation (off-money-path telemetry).
5. **Liveness probes** for the cohort cells and both new axes (no silent flat-line).
6. **Tests:** cohort dual-write pairing, cohort-aware emission fallback, retire-on-negative,
   both axes; use the `numpy_seeded_store` fixture; `xfail` strict; mypy baseline (~102) not
   exceeded; `ruff` clean.

**Acceptance:** fresh truth-report window shows per-cohort net-R; MVRTP promoted cells
trend to suppressed; mean_revert/range emission count rises from ~0; born-dead rate and
confidence-bucket net-R are both visible in the report.

---

## 4. Standing constraints (unchanged, non-negotiable)

- Every change via PR; **never push to `main`**; never push to `claude/general-session-*`
  or harness long-lived branches (cut a fresh `docs/`|`feat/`|`fix/` topic branch off `main`).
- Money-path = owner-sign-off item (new scoring/evaluator/emission authority). The emission
  authority flip is the single most significant such change — confirm before activating.
- Secrets: never log/write/surface a Binance secret or `ANTHROPIC_API_KEY`; auto-reject
  withdraw-enabled keys; never weaken blast-radius caps; never leave a position without a
  stop.
- No uncached Firestore/network read on hot loops; no numpy truthiness on candle arrays; no
  silent excepts in measurement paths (`fail_open.record`).
- Do **not** put the `claude-opus-4-8` model id in any commit, PR, or artifact.
- `subscribe_pr_activity` immediately on opening any PR.

---

## 5. First moves for Session 77

1. Check open GitHub Issues tagged `auto-detected`.
2. `git fetch origin main && git checkout -b feat/cohort-net-edge-emission origin/main`.
3. Pull a fresh truth-report window (`monitor-logs` branch) to confirm the pre-change
   numbers still hold before building.
4. Build W3 per §3 above; open the PR pointing back at §0 of the audit doc.
