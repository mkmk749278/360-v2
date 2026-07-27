# Stamp SAR agreement at entry, not at resolution

**Status:** PROPOSAL — owner sign-off required, not implemented
**Raised:** 2026-07-27, owner-caught from the live `/signals/sar` panel
**Engine module:** `src/sar_exit_shadow.py`
**Ops counterpart:** `mkmk749278/360ce-ops#91` (merged separately; already forward-compatible with this change)

---

## The observation

At the moment a signal fires, the Parabolic SAR is either behind the entry or in
front of it. There are exactly two possibilities and no third one. The owner's
question was why the ops filter offered a third option reading *"Any SAR
agreement (267)"* when the two real buckets held 8 and 8.

The answer is that 251 — now 261 — rows carried no agreement verdict at all.
Cross-tabbing a full export of the ledger (277 rows, 2026-07-27T05:52Z) gives a
perfectly diagonal table:

| | has verdict | blank |
|---|---|---|
| `CLOSED_TRAIL` | 16 | 0 |
| `RUNNING` | 0 | 261 |

Zero exceptions in either direction. Those 261 rows are not rows the walker
refused and not rows that predate the flag — they are trades still inside their
48h window.

## Why they are blank

`sar_aligned_at_entry` is computed inside `simulate_sar_exit` and returned as
part of the resolution result (`src/sar_exit_shadow.py:246`, surfaced at `:538`):

```python
entry_sar = float(series[entry_idx])
aligned = (entry_sar < entry) if is_long else (entry_sar > entry)
```

Two numbers: the SAR level on the entry bar, and the entry price. **No future
candle participates.** The comparison is fully determined the instant the signal
stamps — but it lives inside the function that only runs when the walker
resolves the trade, up to 48 hours later.

So the engine defers a fact it already holds, by two days, and 94% of the ledger
reads blank for no reason other than where that line sits.

## What that costs

1. **Opposed share is 48h stale.** The 50% on the panel describes the mix of
   trades old enough to have resolved. The mix running *right now* is unknown.
2. **The product question is unanswerable.** "How many of the signals we are
   sending are against the indicator?" is decidable today for all 277 rows. It
   is the question that matters, because if counter-SAR entries are bad entries
   that is an **entry-filter** decision, not an exit one — and it would apply to
   the live money path, not just to this shadow arm.
3. **The sample looks 16 when it is 277.** The R and win-rate columns genuinely
   require resolution — you cannot know what a trade made until it is over. The
   *agreement label* does not. Splitting the two lets the agreement question
   reach full sample immediately while performance fills in over time.
4. **It hid the real shape of the arm.** With only resolved rows labelled, the
   agreed bucket's +1.24R rests on 8 trades that are ~5 independent moves (three
   BUSDT rows stamped 00:04 / 00:47 / 01:34 all exit at 0.1959). A 277-row
   agreement population makes concentration like that visible immediately
   instead of after two days.

## Proposal

Stamp the flag at stamp time.

`stamp_sar_pair` (`src/sar_exit_shadow.py:293`) currently receives no candle
data, so it cannot compute the SAR itself. The change is to pass in the value
the scanner already holds and write the flag onto both arms of the pair.

**Shape:**

- Add an optional `entry_sar: Optional[float] = None` parameter to
  `stamp_sar_pair`. The scanner call sites supply the SAR level for the entry
  bar from the series they already have in hand.
- Compute `aligned` with the **same expression as the resolve path**, extracted
  into one shared helper so the two can never drift. One function, two callers —
  not two copies of a comparison.
- Write `sar_aligned_at_entry` onto the record at stamp time.
- When `entry_sar` is absent or unusable, **write nothing**. The field stays
  absent and the row reads "not yet decided" exactly as today. *A clamp is not a
  guard* — do not substitute a default and do not infer the level.

**Cost:** none on the hot path that matters. The SAR value is read from a series
the scanner already computed; there is no Firestore read, no network call, no new
allocation per tick. Do the work **after** the cooldown gate so it only runs on
candidates that actually stamp.

**Hard limits this must respect:**

- Never boolean-test the candle/series array — `is None` and `len()` only
  (`tests/test_no_numpy_truthiness_regression.py`).
- The fail-open path calls `fail_open.record("sar_exit_shadow.stamp_alignment", exc)`.
  Behaviour stays fail-open; the failure counts and pages.
- Refuse rather than clamp. No entry-index inference of any kind.

## This also removes the #800 bug class from this field

#800 was caused by inferring the entry-bar index from elapsed wall-clock time and
clamping when the candle array did not match — the arm then replayed an
unrelated bar and published 172 confident rows averaging −4.4R that described
nothing.

At stamp time there is nothing to infer. The entry bar **is** the current bar;
the SAR value is the one the scanner just computed against the same series it
made the decision on. The inference step that produced #800 does not exist on
this path.

## Keep the resolve-path value as a cross-check, not an overwrite

The resolve path should keep computing its own value and record it under a
**separate** key (e.g. `sar_aligned_at_resolve`), with the stamp-time value
remaining authoritative.

The two should always agree. If they ever disagree, that is a real signal that
the walker's replay window is not reconstructing the entry bar the scanner
actually saw — the exact failure mode of #800, turned into a detector instead of
a silent overwrite. Wire a disagreement counter into the feature-liveness
watchdog (`src/feature_liveness.py`) so it pages rather than sitting in a file.

**This is the part that makes the change worth doing carefully.** Simply moving
the computation earlier would be a small win; keeping both and comparing them
converts a known-dangerous replay path into one that reports on itself.

## Dark-flag classification

Per `CLAUDE.md § Project Phase`, dark means **invisible to users, fully live to
the owner** — two flags, not one:

| Flag | Default | Applies here? |
|---|---|---|
| Measurement | **ON** | **Yes.** Stamping the flag is measurement. It ships ON and is visible in ops the same day. |
| User-visible effect | OFF | **Nothing to gate.** This writes a field to a shadow-ledger record. It does not change scoring, emission, dispatch, FSM behaviour or anything a subscriber sees. |

So this ships with its measurement live from day one. Shipping the measurement
default-OFF is the misreading that produced the original SAR arm incident on
2026-07-25 — an observe-only path that stamped nothing until someone remembered
to flip it, an empty ops panel, and a decision that kept being deferred.

The ops surface already exists (`/signals/sar`, panel from #90, corrected in
#91), so this does not ship blind.

## What this does NOT decide — still owner sign-off

Making counter-SAR entries **visible at signal time** is not the same as deciding
what to do about them. If SAR agreement ever becomes an input to live behaviour,
the options are:

1. **Entry filter** — don't emit a signal whose SAR is opposed at entry.
2. **Geometry switch** — emit it, but keep the live static geometry rather than
   a trail.
3. **Emit and accept** — take the scratch.

All three change what subscribers receive, so all three are **dark-first +
shadow-measured + owner sign-off**, and none of them should be decided until a
clean window has accumulated against a corrected panel. Note also that the
current measurement is **gross** — `candidate_outcome` charges no fees or
slippage — so an opposed row reading roughly flat is a real cost live, and
option 3 is worse than the ledger makes it look.

One further caution against reading the label too hard: it describes bar zero of
an indicator that flips. Of the 8 opposed rows in the 2026-07-27 window, 7 exited
at exactly 15.0m (the first testable bar) but one held 75m — SAR flipped to our
side before it was touched and the trail genuinely rode. "Opposed at entry" is a
property of one instant, not a stable property of the trade.

## Open question for the owner

Should the stamp-time flag be **backfilled** onto the 261 currently-running rows
at deploy?

- **No (recommended).** Their entry bars are in the past; reconstructing the SAR
  level for them means exactly the replay-and-infer step that caused #800. Let
  them resolve as they are and let the population rebuild forward from the
  deploy.
- **Yes.** Full sample immediately, at the cost of trusting a reconstruction we
  have already been burned by once.

Recommendation: **no backfill.** A clean 277-row population accumulates within a
day of the deploy, and it is worth more than a fast one we cannot fully trust.
