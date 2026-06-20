# Per-User Trade Eligibility & Management Mode — Design + Sequencing

**Owner trigger (Session 31, 2026-06-20):** "We give per-user symbol choice
but not which paths / which regime — make those flexible too, neatly in
auto-trade settings, paper and live each an individual selection, with reset
to default. Reset-to-default also missing on Invalidation and Pre-TP. In the
Signals tab, tapping a symbol should offer two modes: take signals **full**
(entry + exit + pre-TP + invalidation) vs **entry-only** (engine places the
entry, user manages the rest). No shortcuts, no scaffolds, production-grade,
no dark flags (testing phase)."

This doc is the change-management design summary for the multi-increment build.
Each increment ships **fully wired** (CLAUDE.md: no scaffolds — a setting the
engine stores but does not consume is banned).

---

## Owner decisions captured this session

1. **Entry-only on LIVE** — engine still places the signal's protective **SL**
   at entry (never naked, honours the B12/B18 naked-position invariant), then
   skips pre-TP / TP ladder / engine invalidation. The user manages the rest.
   Paper entry-only may be fully hands-off (no real risk).
2. **Full vs Entry is saved per symbol** (tap a symbol in the Signals tab →
   set its management mode → persists for future signals on that symbol).
3. **Paper made per-user** — the "individual paper + live selection" ask is
   satisfied by turning the engine's single shared paper book into a per-user
   simulation, so paper selections are genuinely consumed (not a scaffold).

---

## Increment 1 — LIVE path + regime selection — ✅ SHIPPED (this session)

Per-user **path** (setup class) and **regime** eligibility filters, the
analogue of `symbol_preference`, consumed at LIVE dispatch.

- Schema: `user_auto_trade_settings.path_preference`, `.regime_preference`
  (JSON list; `NULL` = all, `[]` = block-all). Idempotent migration.
- `_coerce_auto_trade`: path = uppercase set; regime = `_normalise_regime_input`
  (UI TRENDING/RANGING/CHOPPY → backend labels).
- `resolve_auto_trade_preferences_uid()` resolver (None = allow-all, frozenset
  incl. empty = restrict).
- `dispatch_signal_to_active_users`: skips the user silently (before signing)
  when `setup_class` ∉ path pref or `regime_label` ∉ regime pref.
- `GET /api/auto-trade/runtime-status` exposes `allowed_paths`
  (from `ACTIVE_PATH_PORTFOLIO_ROLES` — single source of truth) + `regime_options`.
- App: `AutoTradeSettings` model carries `pathPreference`/`regimePreference`;
  `eligibility_preference_page.dart` (shared Path + Regime picker); Eligibility
  card in `auto_trade_settings_page.dart` with per-dimension pickers + a single
  **Reset to default** action.
- Tests: store coerce/persistence/resolver (8), dispatch gate (3).

## Increment 1b — Reset-to-default discoverability — ✅ SHIPPED (this session)

Pre-TP + Invalidation pages already had a Reset action but **hid it when the
user was on defaults** (`if (!_usingDefaults …)`), so it looked missing on a
fresh page. Now always visible once loaded (DELETE endpoint is idempotent).

---

## Increment 2 — Per-user PAPER engine (NEXT — owner-approved direction)

**Why:** today `PaperOrderManager` is a single engine-wide simulated book
(one equity, one positions dict; `execute_signal(signal)` takes no user). The
per-user dispatcher only fires LIVE orders; paper-only users are skipped and
the app's "paper" is a shared book viewed from each user's subscription window.
There is no per-user paper execution to attach a per-user paper selection to —
so a per-user paper picker today would be a scaffold.

**Design:**
- Introduce a per-user paper book keyed by `user_id` (equity, positions,
  realised PnL) — either N `PaperOrderManager` instances behind a registry, or
  a single manager that namespaces all state by `user_id`. Persisted per user
  (extend the paper-PnL state file → per-user rows, or a `user_paper_book`
  table). Reuses the existing fee model + lifecycle simulation.
- A **paper dispatch path** analogous to `dispatch_signal_to_active_users`:
  for each user whose mode ∈ {paper, both}, apply that user's **paper**
  eligibility (symbols/paths/regimes) + management mode, then simulate.
- Per-mode preferences: split into `live_*` and `paper_*` (keep existing
  `symbol_preference`/`path_preference`/`regime_preference` as the LIVE set;
  add `paper_symbol_preference` etc.), consumed by the respective path.
- App: surface the Paper selectors alongside Live in the Eligibility card.
- **Cost discipline:** per-user paper sim is CPU/SQLite only — no new Firestore
  hot-path reads. Gate any per-tick lifecycle reads behind the existing
  generation-cache pattern (see `pretp_dispatcher`).

**Owner-sign-off:** touches the paper execution path (money-path-adjacent) —
bring the registry-vs-namespaced decision + the per-mode schema split to the
owner before coding.

## Increment 3 — Per-symbol Full / Entry-only management mode (NEXT)

**Behaviour (owner-decided):**
- **Full** (default): current behaviour — engine manages entry, SL, pre-TP, TP
  ladder, invalidation.
- **Entry-only**: engine places entry **+ protective SL** (never naked), then
  does NOT place pre-TP / TP ladder and does NOT run engine invalidation. The
  user manages the exit. (Paper entry-only may skip even the SL.)

**Design:**
- Storage: per-(user, symbol) management mode — new `user_symbol_management`
  table (`user_id, symbol, mode`) or a JSON map on the auto-trade row.
  Default `full` when unset.
- Consumption (LIVE, the FSM — owner-sign-off): in `dispatch_signal_to_active_users`
  resolve the per-symbol mode; for `entry`, place entry + SL and **skip** the
  pre-TP LIMIT, TP ladder, and register the position as user-managed so the
  invalidation/pre-TP dispatchers leave it alone. This is close to execution
  profile C (`grab_fraction=0`, loose invalidation) but also suppresses the TP
  bracket and engine invalidation — a distinct FSM path. Reconciler's naked-
  position force-close still applies (SL guarantees a stop).
- App: Signals tab — tapping a symbol opens a sheet highlighting the two modes
  (Full / Entry-only) with the doctrine copy; persists the per-symbol choice;
  the choice is reflected back on the symbol row.

**Owner-sign-off:** Position FSM transition change — confirm the entry-only FSM
path (entry+SL, no bracket, no invalidation) before coding.

---

## Guardrails (apply to every increment)

- No dark flags / shadow-first (testing phase, no subscribers) — ship live with
  a reversible env off-switch only.
- Naked-position invariant is NOT relaxed: entry-only LIVE always carries the SL.
- Blast-radius caps, withdraw-key rejection, secret handling unchanged.
- Every per-tick/per-dispatch read stays cached + generation-gated (Cost Discipline).
