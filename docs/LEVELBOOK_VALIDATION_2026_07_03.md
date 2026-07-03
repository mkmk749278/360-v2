# LevelBook Forward-Validation (S41 research)

*Question: do the LevelBook's qualifying levels (CLUSTERED multi-TF /
VP-anchored — the ones SR_FLIP's HTF path trades) mark reversal points any
better than arbitrary price lines?*

## Method

10 liquid symbols × 4 days (2026-06-29 → 07-02). LevelBook rebuilt
point-in-time every 6h from 1h/4h/1d candles closed before the checkpoint
(the engine's own `LevelBook.refresh`, no look-ahead). Walking forward on 5m
candles: each first touch of a qualifying level (±0.15%, the SR_FLIP premium
zone) is scored by what resolves first within 60 minutes — **REJECT** (price
moves ≥0.4% away, against the approach) or **ACCEPT** (closes ≥0.4% through).

**Placebo control:** identical measurement against the same level set offset
by +1.85% — same count, same clustering topology, zero structural meaning.

## Result

| Level set | Touches resolved | Reject % | Accept % |
|---|---:|---:|---:|
| **Real (CLUSTERED/VP)** | 256 | **62.9%** | 37.1% |
| **Placebo (+1.85% offset)** | 243 | **65.4%** | 34.6% |

The real levels do **not** out-reject the placebo. A ~63–65% rejection rate
is the base rate of short-horizon mean reversion at this resolution — price
"respects" any line. The structural selection (multi-TF clustering, VP
anchoring) added nothing measurable in this window.

## Caveats

One 4-day window in one market phase; one parameterisation (0.15% touch,
0.4% resolve, 60-min horizon); rejection-on-touch is the simplest property —
the flip-retest usage (break, hold, retest) is a richer pattern this test
doesn't isolate. Re-run over a longer archive span and with a
break-and-retest-specific design before acting on structure-dependent paths.

## The pattern across the three S41 studies

| Layer the scorer/gates trust | Study verdict |
|---|---|
| SMC dimension (largest score weight) | Half-blind inputs (`orderblocks` not implemented; top-of-book-only book) |
| 5m regime label (gates + 20-pt dimension) | Rear-view; only QUIET has forward validity |
| LevelBook structural levels | Indistinguishable from placebo on touch-rejection |
| **Setup × side × BTC-macro cohorts** | **Separated outcomes decisively, twice (S38 long bleed, S40 short bleed)** |

Every "textbook structure" layer fails forward-validation at scalp horizons
in these windows, while measured cohort edge keeps working. This is the
empirical foundation for the cohort-ranker redesign
(`SCORING_AUDIT_2026_07_03.md`): rank by what is measured to work, use
structure only as setup context, and validate every layer before weighting it.
