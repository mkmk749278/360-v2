# AUDIT 2026-04-14 — Report Comparison and Canonical Verdict

- title: Report Comparison and Canonical Verdict
- date: 2026-04-14
- repository: `mkmk749278/360-v2`
- branch: `main`
- reports compared:
  - `docs/AUDIT_2026-04-14_LIVE_SIGNAL_EXPRESSION_INVESTIGATION_GPT-5.4.md`
  - `docs/AUDIT_2026-04-14_LIVE_SIGNAL_EXPRESSION_INVESTIGATION_CLAUDE-OPUS-4.6.md`
  - `docs/AUDIT_2026-04-14_LIVE_SIGNAL_EXPRESSION_INVESTIGATION_GPT-5.3-CODEX.md`
- final recommended next PR: **WATCHLIST lifecycle segregation / doctrine alignment** — stop `WATCHLIST` from entering paid active lifecycle, and implement an explicit free/watchlist route instead of reusing the current paid path

## Method

This synthesis compares the three reports against the current code and, where one report relied on live evidence, against `origin/monitor-logs:monitor/latest.txt`.

## 1. Areas where all three reports agree

1. **WATCHLIST is not preview-only in the current runtime.**  
   `WATCHLIST` (`50–64`) survives scanner preparation, bypasses the router min-confidence floor for `360_SCALP`, is posted through the paid channel path, is registered in `_active_signals`, and is then monitored by `TradeMonitor` (`src/scanner/__init__.py:2942-2953`, `src/signal_router.py:628-756`, `src/trade_monitor.py:367-403`).

2. **That behavior contradicts declared doctrine.**  
   `OWNER_BRIEF.md` says `WATCHLIST | 50–64 | Post to free channel only` (`OWNER_BRIEF.md:467-474`).

3. **The current scanner WATCHLIST comment is false.**  
   The code says “clear entry/SL/TP for zone-alert-only format” but only calls `_populate_signal_context()` and returns the full signal (`src/scanner/__init__.py:2951-2953`).

4. **Duplicate lifecycle posting risk is real.**  
   `TradeMonitor` has no generic lifecycle-send dedupe ledger; `_post_update()` blindly sends; expiry has two posting owners (`src/trade_monitor.py:552-560,631-670,931-955`, `src/signal_router.py:1109-1140`).

5. **Weak live expression should not be answered with broad scoring redesign first.**  
   All three reports reject broad threshold/evaluator rewrites before routing/lifecycle truth is corrected.

## 2. Areas where they disagree

### A. What should be the next PR

- **GPT-5.4:** fix WATCHLIST lifecycle admission first.
- **Claude Opus 4.6:** same verdict; strongest form of this recommendation.
- **GPT-5.3-Codex:** fix lifecycle idempotency / duplicate-post hardening first.

**Canonical judgment:** GPT-5.4 + Claude are stronger here. The WATCHLIST governance/runtime contradiction is directly proven and it contaminates both paid-channel quality and downstream lifecycle evidence.

### B. Best explanation of duplicate lifecycle posting

- **GPT-5.4:** strongest on the fact that SL-style exits are already dual-posted by design (`_post_update` + `_post_signal_closed(..., is_tp=False)`), and careful not to overclaim about duplicate `INVALIDATED`.
- **Claude:** strongest on the concrete re-fire mechanism: terminal branches call `_post_update()` before `_remove()`, without `try/finally`; if posting throws, the signal persists and can fire again on the next poll.
- **GPT-5.3-Codex:** broadly correct about missing idempotency and split expiry ownership, but weaker on exact root-cause isolation.

**Canonical judgment:** both GPT-5.4 and Claude are partly right; Claude is strongest on the actual re-fire bug, GPT-5.4 is strongest on the “duplicate-looking” stop-loss output that is already built into current design.

### C. Which setup family is the main weak-signal source

- **Claude:** `SR_FLIP_RETEST` is the strongest confirmed family-level concern.
- **GPT-5.4:** recent resolved live losses are concentrated in low-confidence `TREND_PULLBACK_EMA`, while current scoring-funnel concentration is strongest for `SR_FLIP_RETEST`.
- **GPT-5.3-Codex:** `SR_FLIP_RETEST` and `CONTINUATION_LIQUIDITY_SWEEP` are structurally plausible concerns; live proportions were left unconfirmed.

**Canonical judgment:** the best reconciled answer is:  
`WATCHLIST` leakage is the primary system-level cause; among families, `SR_FLIP_RETEST` is the strongest code-supported quality concern, while `TREND_PULLBACK_EMA` is the strongest recent live-loss concentration in the fetched monitor snapshot.

## 3. Which claims are strongly supported by code

These are the highest-confidence claims across the three reports:

1. **WATCHLIST becomes paid active lifecycle on `360_SCALP`.**  
   Strongly supported by code path end-to-end (`src/scanner/__init__.py:2942-2953`, `src/signal_router.py:628-756`, `src/main.py:152-157`, `src/trade_monitor.py:367-403`).

2. **Doctrine and runtime disagree.**  
   Strongly supported by `OWNER_BRIEF.md` vs runtime (`OWNER_BRIEF.md:467-474`).

3. **WATCHLIST formatting is only cosmetic.**  
   The Telegram formatter switches message shape only; it does not change routing/lifecycle admission (`src/telegram_bot.py:291-313,514-531`).

4. **Router pulse logic already treats WATCHLIST as non-live-status material.**  
   `_signal_pulse_loop()` skips WATCHLIST-tier signals (`src/signal_router.py:354-362`).

5. **Expiry has duplicate-post risk from split ownership.**  
   `TradeMonitor` posts expiry and `SignalRouter.cleanup_expired()` also posts expiry (`src/trade_monitor.py:552-560`, `src/signal_router.py:1109-1140`).

6. **Terminal-event branches lack robust removal guarantees.**  
   `SL`, `INVALIDATED`, `EXPIRED`, and `CANCELLED` post before remove and do not use `try/finally` (`src/trade_monitor.py:552-560,592-611,634-651,657-673`).

7. **Stop-style terminal events currently produce two messages by design.**  
   `SL_HIT`/breakeven/profit-locked paths call `_post_update()` and then `_post_signal_closed(..., is_tp=False)` (`src/trade_monitor.py:634-650,957-1010`; close-message formatter in `src/formatter.py:310-344`).

8. **`SR_FLIP_RETEST` has the widest confirmed soft-penalty funnel.**  
   Up to 20 points of cumulative soft penalties are visible in code (+3 proximity, +4 wick, +5 RSI, +8 missing SMC in fast regimes), and it blocks only `VOLATILE` (`src/channels/scalp.py:1777-1778,1833-1905,1999-2004`).

9. **Current free-channel helper is not the same thing as a WATCHLIST route.**  
   `_maybe_publish_free_signal()` only posts once per day per group and requires confidence `>= 75`, so it cannot be reused unchanged for `WATCHLIST 50–64` (`src/signal_router.py:897-926`).

10. **PR-18 tests currently encode the runtime behavior, not doctrine.**  
    The test suite explicitly asserts that a `WATCHLIST` `360_SCALP` signal is dispatched (`tests/test_pr18_scalp_tier_dispatch_alignment.py:194-207`).

## 4. Which claims are speculative or weak

1. **“Duplicate INVALIDATED is caused by a second explicit invalidation path.”**  
   Weak. Code shows only one invalidation posting branch (`src/trade_monitor.py:657-673`).

2. **“Overlapping monitor loops are the likely main duplicate source.”**  
   Weak. `TradeMonitor.start()` is not idempotent (`src/trade_monitor.py:351-364`), so this is plausible risk, but none of the reports prove dual-loop runtime happened.

3. **“`CONTINUATION_LIQUIDITY_SWEEP` is currently a major live-output driver.”**  
   Weak. Code shows plausible softening, but the fetched live snapshot does not show it as a dominant scoring family.

4. **“`TREND_PULLBACK_EMA` is structurally bad.”**  
   Weak. The evaluator is mostly hard-gated (`src/channels/scalp.py:619-684`), and its recent low-confidence losses are better explained by WATCHLIST admission than by a clearly broken evaluator.

5. **“Just route WATCHLIST through the existing free publish helper.”**  
   Weak / incomplete. That helper is daily, condensed, and `>= 75` only; it is not a drop-in WATCHLIST implementation (`src/signal_router.py:897-926`).

## 5. Best explanation of WATCHLIST lifecycle truth

**Canonical truth:** doctrine says WATCHLIST is preview-only, but runtime treats `360_SCALP` WATCHLIST as a real paid trade object.

The decisive code path is:

1. tier becomes `WATCHLIST` at `50–64` (`src/scanner/__init__.py:383-402`);
2. scanner preserves that object for scalp-family channels (`src/scanner/__init__.py:2942-2953`);
3. router bypasses min-confidence for `360_SCALP` WATCHLIST (`src/signal_router.py:628-647`);
4. router sends it through the same paid channel delivery path and stores it in `_active_signals` (`src/signal_router.py:663-756`);
5. trade monitor evaluates everything in `_active_signals` with no WATCHLIST exclusion (`src/trade_monitor.py:367-403`).

The strongest report on this point is **Claude**, because it traces the full contradiction cleanly.  
The strongest corroborating live evidence is **GPT-5.4**, because the fetched monitor snapshot shows sub-65 signals reaching resolved outcomes (`origin/monitor-logs:monitor/latest.txt:64-76`).

## 6. Best explanation of duplicate lifecycle posting root cause

**Canonical truth:** there are two different phenomena, and the reports were sometimes describing different ones.

### 6.1 Duplicate-looking stop-loss output

This is **confirmed by design** for stop-style terminal exits: the monitor posts a lifecycle event and then a second “signal closed” summary to the same active channel (`src/trade_monitor.py:634-650,957-1010`).  
GPT-5.4 is strongest on this point.

### 6.2 True repeated terminal-event re-fire

This is **most strongly explained by missing removal guarantees plus missing event idempotency**:

- terminal branches post before remove;
- `_post_update()` has no local exception handling;
- those branches do not use `try/finally`;
- if send fails, `_remove()` is skipped and the signal can be evaluated again next poll.

That makes **Claude’s explanation the strongest true root-cause diagnosis** for repeated SL / INVALIDATED / EXPIRED / CANCELLED posts.

### 6.3 Expiry duplicates

A separate, independently real source exists: both monitor and router can post expiry. GPT-5.3 and GPT-5.4 both captured this correctly.

## 7. Best explanation of low-confidence overexpression / weak live quality

**Canonical explanation:** weak live quality is primarily a routing/governance problem first, then a family-quality problem second.

1. **Primary cause:** `WATCHLIST 50–64` signals are being treated as paid active trades.  
   That alone guarantees low-confidence objects will show up in paid lifecycle outcomes.

2. **Strongest family-level contributor:** `SR_FLIP_RETEST`.  
   Claude is strongest here because the evaluator really does combine broad regime allowance with multiple cumulative soft penalties that can still pass the path.

3. **Strongest recent live-loss concentration in fetched evidence:** `TREND_PULLBACK_EMA`.  
   GPT-5.4 is strongest here because it used the monitor snapshot rather than code alone.

4. **`CONTINUATION_LIQUIDITY_SWEEP`:** present, plausible, but not proven dominant.

So the best reconciled statement is:

> The system is not mainly suffering from “no signals” or from a globally broken scorer. It is suffering from `WATCHLIST` objects being allowed to behave like paid live trades, with `SR_FLIP_RETEST` as the clearest path-level widening inside that contaminated funnel.

## 8. Ranked recommendation for the next PR

### 1. WATCHLIST lifecycle segregation / doctrine alignment

Best next PR scope:

- stop `WATCHLIST` from entering the paid active-signal lifecycle;
- do not register `WATCHLIST` in `_active_signals`;
- implement an explicit free/watchlist route that matches doctrine, instead of silently reusing the current paid path or the current `>=75` free helper;
- update the false scanner comment and PR-18-aligned tests/docs.

**Why rank #1:** this is the clearest code-proven integrity failure and it contaminates every downstream quality read.

### 2. Lifecycle idempotency / duplicate-post hardening

- add terminal-event send dedupe keyed by signal/event;
- wrap terminal post/remove sequences so `_remove()` is not skipped on send failure;
- consolidate expiry posting to one owner;
- then decide whether stop-style dual-posting should remain or be reduced.

### 3. Evidence-gated `SR_FLIP_RETEST` tightening

Only after #1 and #2.  
Re-evaluate retest proximity, wick softness, RSI softness, and fast-regime missing-SMC softness after cleaner telemetry.

## 9. Explicit recommendation of what NOT to change yet

1. **Do not broadly retune global confidence thresholds.**
2. **Do not broadly rewrite the composite scoring engine.**
3. **Do not broadly retune `TREND_PULLBACK_EMA` or `CONTINUATION_LIQUIDITY_SWEEP` yet.**
4. **Do not treat a TradeMonitor-only tier filter as the primary fix.**  
   If used at all, it should be defense-in-depth after router admission is corrected.
5. **Do not reuse `_maybe_publish_free_signal()` unchanged as the WATCHLIST solution.**  
   Its semantics are wrong for `50–64` WATCHLIST.
6. **Do not redesign the whole architecture before fixing the narrow routing/lifecycle contradictions already proven by code.**

## 10. Final canonical verdict

The three reports converge on one central truth:

> `WATCHLIST` semantics are currently broken in production code.

`WATCHLIST` is documented as free-only preview material, but current `360_SCALP` runtime promotes it into paid-channel active lifecycle. That is the best-supported explanation for low-confidence live pollution. Separately, duplicate lifecycle output has two layers: built-in dual stop-style messaging, and a stronger true bug where terminal events can re-fire because posting happens before guaranteed removal and without event idempotency.

### Final decision

- **Best overall report on live evidence:** GPT-5.4  
- **Best overall report on duplicate-post root-cause mechanics:** Claude Opus 4.6  
- **Best overall conservative governance synthesis:** GPT-5.3-Codex

### Single recommended next action

**Open the next PR to enforce WATCHLIST lifecycle segregation and doctrine alignment first.**  
Make WATCHLIST explicitly free/watchlist-only, remove it from paid active lifecycle, and only then use cleaner telemetry to judge duplicate-post residuals and family-level tightening.
