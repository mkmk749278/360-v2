"""The subscriber-facing track record — reducers, loader, and the ops contract.

Two jobs here, and the second is the one worth reading.

**Unit** — the reducers do what the module says: fees charged, win rate counted
on the net money, close time preferred over entry, days bucketed in UTC, today
marked partial, a row with no readable move refused rather than scored zero.

**Contract** — ``CONTRACT_ROWS`` and ``CONTRACT_EXPECTED`` below are
**byte-identical to 360ce-ops' ``tests/test_track_record_contract.py``**. Ops has
rendered this same book on ``/track-record`` since 2026-07-28 and the app now
renders it too, so there are two implementations of one number in two repos that
cannot import each other. Two surfaces under one name computing two different
books has already cost this system a session (2026-07-31, the SAR replay against
the live arm), and the way that stayed invisible was agreement on the easy
majority. A shared vector is what makes the disagreement fail CI instead.

The expected values are **derived by hand in the comments below**, never recorded
from either implementation's output: a vector copied out of one implementation
agrees with that implementation by construction and pins nothing.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from src import track_record as tr


UTC = timezone.utc


def _ts(y, m, d, hh=0, mm=0):
    return datetime(y, m, d, hh, mm, tzinfo=UTC).timestamp()


def _rec(symbol, direction, entry, pnl, closed, **extra):
    out = {
        "symbol": symbol,
        "direction": direction,
        "setup_class": "MOVER_TREND_PULLBACK",
        "entry": entry,
        "pnl_pct": pnl,
        "terminal_outcome_timestamp": closed,
    }
    out.update(extra)
    return out


# ---------------------------------------------------------------------------
# THE SHARED CONTRACT VECTOR — keep byte-identical with 360ce-ops
# ---------------------------------------------------------------------------

#: Eight closed signals across four UTC days inside a seven-day window, chosen so that every rule this
#: module carries is exercised by at least one row and none of them cancel out.
CONTRACT_ROWS = [
    # --- 2026-08-04: THE BOUNDARY ROW --------------------------------------
    # The oldest day the 7-day window claims, and this row closed at 04:00 —
    # BEFORE the hour of CONTRACT_NOW. A window starting at ``now - 7 days``
    # (12:00) drops it while still labelling the bucket 2026-08-04, which is
    # precisely the fault that flipped a day's sign on the ops page: the oldest
    # bucket holds a fragment and renders identically to a complete day. The
    # row exists so that fault fails CI rather than passing unnoticed.
    _rec("LINKUSDT", "SHORT", 20.0, -2.00, _ts(2026, 8, 4, 4)),
    # --- 2026-08-08: deliberately empty ------------------------------------
    # Inside the window, nothing closed. It must be ABSENT from items, not a
    # zero point — an invented zero is indistinguishable from a real flat day.
    # --- 2026-08-09 --------------------------------------------------------
    # Two entries into one BTC move: 30000 and 30090 are 0.30% apart, inside
    # SAME_MOVE_PCT (0.5), so they are ONE move and two trades.
    _rec("BTCUSDT", "LONG", 30000.0, 2.00, _ts(2026, 8, 9, 4)),
    _rec("BTCUSDT", "LONG", 30090.0, -1.00, _ts(2026, 8, 9, 6)),
    # Same symbol, opposite side — a different (symbol, direction) key, so a
    # second move however close the price is.
    _rec("BTCUSDT", "SHORT", 30090.0, 0.50, _ts(2026, 8, 9, 8)),
    # --- 2026-08-10 --------------------------------------------------------
    # +0.05% gross is a LOSS net of a 0.07% round trip. A trade that made less
    # than its own fee did not make money.
    _rec("ETHUSDT", "SHORT", 2000.0, 0.05, _ts(2026, 8, 10, 1)),
    # No readable pnl_pct: counted in n, excluded from every money figure,
    # never scored zero.
    _rec("SOLUSDT", "LONG", 100.0, None, _ts(2026, 8, 10, 2)),
    # No close timestamp at all -> undateable, in no bucket.
    _rec("XRPUSDT", "LONG", 1.0, 1.00, None, timestamp=None, create_timestamp=None),
    # --- 2026-08-11 (== "today" for CONTRACT_NOW) --------------------------
    _rec("ADAUSDT", "LONG", 0.5, 3.00, _ts(2026, 8, 11, 2)),
]

#: The moment the contract is evaluated at. Inside 2026-08-11, so that day is
#: the partial one; a 7-day window snaps back to midnight on 2026-08-04.
#: 7 rather than 4 because ops offers PRESET windows (1d/7d/30d/90d) while
#: the engine takes an arbitrary day count — the contract has to be a
#: window both surfaces can actually be asked for.
CONTRACT_NOW = datetime(2026, 8, 11, 12, 0, tzinfo=UTC)

#: The window the contract is evaluated over.
CONTRACT_DAYS = 7

#: Derived by hand. Seven dateable rows, six with a readable move.
#:
#: gross moves:      -2.00, +2.00, -1.00, +0.50, +0.05, +3.00  -> sum +2.55
#: net (each -0.07): -2.07, +1.93, -1.07, +0.43, -0.02, +2.93  -> sum +2.13
#: wins on NET:      +1.93, +0.43, +2.93                        -> 3W / 3L
#: fee:              6 priced rows x 100 USDT x 0.07%           -> 0.42
#: gross_usd:        100 x 2.55 / 100                           -> +2.55
#: net_usd:          100 x 2.13 / 100                           -> +2.13
#: avg gross:        2.55 / 6                                   -> +0.425
#: avg net:          2.13 / 6                                   -> +0.355
#: moves:            BTC LONG (2 rows, 0.30% apart) = 1, BTC SHORT = 1,
#:                   ETH = 1, SOL = 1, ADA = 1, LINK = 1        -> 6
#: n counts the un-priced SOL row; n_pnl does not.
CONTRACT_EXPECTED = {
    "range_start": "2026-08-04",
    "total_records": 8,
    "undateable": 1,
    "summary": {
        "n": 7,
        "moves": 6,
        "n_pnl": 6,
        "no_pnl": 1,
        "wins": 3,
        "losses": 3,
        "win_rate": 0.5,
        "gross_usd": 2.55,
        "fee_usd": 0.42,
        "net_usd": 2.13,
        "total_pnl_pct": 2.55,
        "avg_pnl_pct": 0.425,
        "total_net_pct": 2.13,
        "avg_net_pct": 0.355,
        "best_pnl_pct": 3.00,
        "worst_pnl_pct": -2.00,
    },
    # Oldest first. 2026-08-08 closed nothing and is therefore ABSENT — an
    # empty day is not a zero-PnL day. The curve carries its level across it.
    "days": [
        # 2026-08-04: the boundary row. -2.00 gross, -2.07 net, 0W / 1L.
        {"date": "2026-08-04", "n": 1, "moves": 1, "wins": 0, "losses": 1,
         "net_usd": -2.07, "cum_net_usd": -2.07, "partial_reason": None},
        # 2026-08-09: +2.00 -1.00 +0.50 = +1.50 gross, 3 fees = 0.21,
        #             net +1.29. Wins on net: +1.93, +0.43 -> 2W / 1L.
        #             Moves: BTC LONG (one) + BTC SHORT (one) = 2.
        {"date": "2026-08-09", "n": 3, "moves": 2, "wins": 2, "losses": 1,
         "net_usd": 1.29, "cum_net_usd": -0.78, "partial_reason": None},
        # 2026-08-10: +0.05 gross on one priced row, -0.02 net; the SOL row is
        #             counted in n and in nothing else.
        {"date": "2026-08-10", "n": 2, "moves": 2, "wins": 0, "losses": 1,
         "net_usd": -0.02, "cum_net_usd": -0.80, "partial_reason": None},
        # 2026-08-11: +3.00 gross, +2.93 net, and it is TODAY -> in_progress.
        {"date": "2026-08-11", "n": 1, "moves": 1, "wins": 1, "losses": 0,
         "net_usd": 2.93, "cum_net_usd": 2.13, "partial_reason": "in_progress"},
    ],
}


@pytest.fixture
def contract_path(tmp_path):
    tr.reset_cache()
    p = tmp_path / "signal_performance.json"
    p.write_text(json.dumps(CONTRACT_ROWS), encoding="utf-8")
    yield str(p)
    tr.reset_cache()


class TestContractVector:
    """The numbers ops publishes and the app renders must be one book."""

    def test_summary_matches_the_shared_vector(self, contract_path):
        out = tr.build_track_record(
            days=CONTRACT_DAYS, path=contract_path, now=CONTRACT_NOW,
        )
        assert out["range_start"] == CONTRACT_EXPECTED["range_start"]
        assert out["total_records"] == CONTRACT_EXPECTED["total_records"]
        assert out["undateable"] == CONTRACT_EXPECTED["undateable"]
        for key, want in CONTRACT_EXPECTED["summary"].items():
            got = out["summary"][key]
            assert got == pytest.approx(want, abs=1e-9), key

    def test_days_match_the_shared_vector(self, contract_path):
        out = tr.build_track_record(
            days=CONTRACT_DAYS, path=contract_path, now=CONTRACT_NOW,
        )
        assert [d["date"] for d in out["items"]] == [
            d["date"] for d in CONTRACT_EXPECTED["days"]
        ]
        for got, want in zip(out["items"], CONTRACT_EXPECTED["days"]):
            for key, value in want.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    assert got[key] == pytest.approx(value, abs=1e-9), (
                        f"{want['date']}.{key}"
                    )
                else:
                    assert got[key] == value, f"{want['date']}.{key}"

    def test_a_day_that_closed_nothing_is_absent_not_zero(self, contract_path):
        """2026-08-08 is inside the window and has no row.

        Emitting a zero point for it would draw a flat segment the book never
        traded, and a reader cannot tell an invented zero from a real flat day.
        """
        out = tr.build_track_record(
            days=CONTRACT_DAYS, path=contract_path, now=CONTRACT_NOW
        )
        assert out["range_start"] < "2026-08-08"
        assert "2026-08-08" not in {d["date"] for d in out["items"]}
        # ...and the curve carries its level across the gap rather than
        # dropping to zero: 08-07 closed at -2.07 and 08-09 resumes from it.
        by_date = {d["date"]: d for d in out["items"]}
        assert by_date["2026-08-09"]["cum_net_usd"] == pytest.approx(-0.78)


class TestFees:
    def test_win_rate_counts_on_the_net_money(self):
        """+0.05% gross against a 0.07% round trip is a loss.

        Counting it as a win is how a fee-sized edge reads as a winning book —
        the owner's 30d window runs roughly ten times more fee than edge.
        """
        rows = [{"symbol": "E", "direction": "LONG", "entry": 1.0, "pnl_pct": 0.05}]
        assert tr.summarize(rows, fee_pct=0.07)["wins"] == 0
        assert tr.summarize(rows, fee_pct=0.00)["wins"] == 1

    def test_zero_fee_renders_the_gross_book(self):
        rows = [{"symbol": "E", "direction": "LONG", "entry": 1.0, "pnl_pct": 2.0}]
        got = tr.summarize(rows, fee_pct=0.0)
        assert got["net_usd"] == pytest.approx(got["gross_usd"])
        assert got["fee_usd"] == pytest.approx(0.0)

    def test_best_and_worst_stay_gross(self):
        """So the fee is not subtracted twice in the reader's head."""
        rows = [{"symbol": "E", "direction": "LONG", "entry": 1.0, "pnl_pct": 2.0}]
        assert tr.summarize(rows, fee_pct=0.07)["best_pnl_pct"] == pytest.approx(2.0)


class TestSizeIsAnInput:
    def test_dollars_scale_linearly_and_percentages_do_not_move(self):
        """The engine sizes at a fixed notional, which is what makes this a
        multiplication rather than a model — and why the percentage columns are
        untouched by the amount."""
        rows = [{"symbol": "E", "direction": "LONG", "entry": 1.0, "pnl_pct": 2.0}]
        at100 = tr.summarize(rows, amount=100.0, fee_pct=0.07)
        at500 = tr.summarize(rows, amount=500.0, fee_pct=0.07)
        assert at500["net_usd"] == pytest.approx(at100["net_usd"] * 5)
        assert at500["total_net_pct"] == pytest.approx(at100["total_net_pct"])


class TestRefuseDontClamp:
    def test_unreadable_move_is_counted_but_never_scored_zero(self):
        rows = [
            {"symbol": "A", "direction": "LONG", "entry": 1.0, "pnl_pct": 1.0},
            {"symbol": "B", "direction": "LONG", "entry": 1.0, "pnl_pct": None},
            {"symbol": "C", "direction": "LONG", "entry": 1.0, "pnl_pct": "n/a"},
        ]
        got = tr.summarize(rows, fee_pct=0.0)
        assert (got["n"], got["n_pnl"], got["no_pnl"]) == (3, 1, 2)
        # Averaged over the priced row only — a missing move is "we cannot
        # say", and folding it in as 0.0 would drag the average to a third.
        assert got["avg_pnl_pct"] == pytest.approx(1.0)

    def test_empty_book_reports_none_not_zero(self):
        got = tr.summarize([], fee_pct=0.07)
        assert got["n"] == 0
        assert got["win_rate"] is None
        assert got["net_usd"] is None
        assert got["avg_pnl_pct"] is None


class TestBucketByClose:
    def test_close_time_beats_entry_time(self):
        """Bucketing by entry credits Monday with a trade that closed Thursday."""
        rec = {
            "symbol": "A", "direction": "LONG", "entry": 1.0, "pnl_pct": 1.0,
            "create_timestamp": _ts(2026, 8, 3, 9),
            "terminal_outcome_timestamp": _ts(2026, 8, 6, 9),
        }
        assert tr.close_time(rec) == datetime(2026, 8, 6, 9, tzinfo=UTC)

    def test_written_at_timestamp_is_the_fallback_before_entry(self):
        rec = {
            "create_timestamp": _ts(2026, 8, 3, 9),
            "timestamp": _ts(2026, 8, 6, 9),
        }
        assert tr.close_time(rec) == datetime(2026, 8, 6, 9, tzinfo=UTC)

    def test_iso_strings_are_tolerated_and_naive_ones_read_as_utc(self):
        assert tr.close_time({"timestamp": "2026-08-06T09:00:00Z"}) == datetime(
            2026, 8, 6, 9, tzinfo=UTC
        )
        assert tr.close_time({"timestamp": "2026-08-06T09:00:00"}) == datetime(
            2026, 8, 6, 9, tzinfo=UTC
        )


class TestWindowSnapsToMidnight:
    def test_range_start_is_midnight_utc_not_now_minus_n(self, contract_path):
        """A preset starting at ``now - N days`` leaves the oldest bucket
        holding only the tail of that day while rendering identically to a
        complete one. That flipped a day's sign on the ops page.

        The assertion that bites is the row count, not the label: an un-snapped
        window prints the SAME ``range_start`` string (both fall on 2026-08-07)
        and silently drops the 04:00 boundary row, so a test that only checked
        the label would pass against the bug. It did — this test was written
        without the boundary row first and a ``start = now - timedelta(days)``
        mutation survived all 24 cases.
        """
        out = tr.build_track_record(
            days=CONTRACT_DAYS, path=contract_path, now=CONTRACT_NOW
        )
        assert out["range_start"] == "2026-08-04"
        # The 04:00 row on the start day is IN. Un-snapped it would be out,
        # taking the book from 7 trades to 6 and the net from +2.13 to +4.20.
        assert out["summary"]["n"] == 7
        assert out["summary"]["net_usd"] == pytest.approx(2.13)
        oldest = out["items"][0]
        assert oldest["date"] == "2026-08-04" and oldest["n"] == 1

    def test_only_today_is_marked_in_progress(self, contract_path):
        out = tr.build_track_record(days=30, path=contract_path, now=CONTRACT_NOW)
        partial = {d["date"]: d["partial_reason"] for d in out["items"]}
        assert partial["2026-08-11"] == "in_progress"
        assert partial["2026-08-09"] is None
        assert partial["2026-08-10"] is None


class TestConcentration:
    def test_two_entries_into_one_move_are_one_move_and_two_trades(self):
        rows = [
            {"symbol": "B", "direction": "LONG", "entry": 30000.0,
             "pnl_pct": 1.0, "closed_at_ts": 1.0},
            {"symbol": "B", "direction": "LONG", "entry": 30090.0,
             "pnl_pct": 1.0, "closed_at_ts": 2.0},
        ]
        got = tr.summarize(rows, fee_pct=0.0)
        assert (got["n"], got["moves"]) == (2, 1)

    def test_the_opposite_side_is_always_a_second_move(self):
        rows = [
            {"symbol": "B", "direction": "LONG", "entry": 30000.0,
             "pnl_pct": 1.0, "closed_at_ts": 1.0},
            {"symbol": "B", "direction": "SHORT", "entry": 30000.0,
             "pnl_pct": 1.0, "closed_at_ts": 2.0},
        ]
        assert tr.summarize(rows, fee_pct=0.0)["moves"] == 2

    def test_a_slow_walk_cannot_drift_and_still_count_as_one_move(self):
        """Anchored on the OPEN move, not the previous row."""
        rows = [
            {"symbol": "B", "direction": "LONG", "entry": 100.0 + i * 0.3,
             "pnl_pct": 1.0, "closed_at_ts": float(i)}
            for i in range(6)
        ]
        assert tr.summarize(rows, fee_pct=0.0)["moves"] > 1

    def test_nothing_is_de_duplicated(self):
        """Disclosure, not de-duplication — the averages still cover every row."""
        rows = [
            {"symbol": "B", "direction": "LONG", "entry": 30000.0,
             "pnl_pct": 4.0, "closed_at_ts": 1.0},
            {"symbol": "B", "direction": "LONG", "entry": 30090.0,
             "pnl_pct": 0.0, "closed_at_ts": 2.0},
        ]
        got = tr.summarize(rows, fee_pct=0.0)
        assert got["avg_pnl_pct"] == pytest.approx(2.0)


class TestLoaderAndCache:
    def test_missing_file_is_named_not_silently_empty(self, tmp_path):
        tr.reset_cache()
        rows, error = tr.load_rows(str(tmp_path / "nope.json"))
        assert rows == [] and error == "missing"

    def test_unreadable_and_wrong_shape_are_different_reasons(self, tmp_path):
        tr.reset_cache()
        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        assert tr.load_rows(str(bad))[1] == "unreadable"
        tr.reset_cache()
        obj = tmp_path / "obj.json"
        obj.write_text('{"records": []}', encoding="utf-8")
        assert tr.load_rows(str(obj))[1] == "unexpected_shape"

    def test_the_reason_reaches_the_payload_rather_than_reading_as_no_trades(
        self, tmp_path
    ):
        tr.reset_cache()
        out = tr.build_track_record(path=str(tmp_path / "nope.json"))
        assert out["unavailable_reason"] == "missing"
        assert out["items"] == [] and out["summary"]["n"] == 0

    def test_cache_is_invalidated_by_the_writer_not_by_a_ttl(self, tmp_path):
        """Gated on the file's own mtime+size, so a fresh close is visible on
        the next request and a quiet hour costs one stat."""
        import os
        import time

        tr.reset_cache()
        p = tmp_path / "perf.json"
        p.write_text(json.dumps([_rec("A", "LONG", 1.0, 1.0, _ts(2026, 8, 10))]))
        assert len(tr.load_rows(str(p))[0]) == 1

        p.write_text(json.dumps([
            _rec("A", "LONG", 1.0, 1.0, _ts(2026, 8, 10)),
            _rec("B", "LONG", 1.0, 1.0, _ts(2026, 8, 10)),
        ]))
        # Some filesystems have coarse mtime; nudge it so the stamp differs on
        # size alone at worst.
        os.utime(p, (time.time() + 1, time.time() + 1))
        assert len(tr.load_rows(str(p))[0]) == 2


class TestDisabled:
    def test_off_returns_the_same_shape_with_a_named_reason(self, contract_path):
        """A caller must never have to tell 'switched off' from 'failed' by the
        absence of a key."""
        out = tr.build_track_record(
            days=30, path=contract_path, now=CONTRACT_NOW, enabled=False,
        )
        assert out["enabled"] is False
        assert out["unavailable_reason"] == "disabled"
        assert out["items"] == []
        assert set(out) == set(
            tr.build_track_record(days=30, path=contract_path, now=CONTRACT_NOW)
        )


class TestNoRAnywhere:
    def test_the_payload_never_publishes_an_r(self, contract_path):
        """R divides by a stop the sizing never used and that most rows do not
        carry. PnL needs no denominator — see the module docstring."""
        out = tr.build_track_record(days=30, path=contract_path, now=CONTRACT_NOW)
        blob = json.dumps(out).lower()
        for banned in ('"r_', '_r"', '"avg_r', 'sl_distance'):
            assert banned not in blob, banned


class TestCalendarMonthMode:
    """A month on screen must be the month a reader means by the word.

    Added 2026-08-11 on the owner's direction: the calendar grid and the period
    chips become **independent controls**. Before this the calendar was a
    rolling grid over whatever window the chips had selected, so "month" meant
    "the last thirty days", which straddles two of them.

    The mode earns something beyond tidiness. A rolling grid cannot honestly
    draw a day on which nothing closed, because a missing day might equally be
    outside the fetched window — the two are different facts and the grid draws
    them differently. Fetching a whole calendar month removes the ambiguity:
    every day of it was asked for, so an absent day is a fact about the market.
    """

    def test_a_month_is_that_month_and_nothing_either_side(self, contract_path):
        out = tr.build_track_record(
            month="2026-08", path=contract_path, now=CONTRACT_NOW,
        )
        assert out["month"] == "2026-08"
        assert out["range_start"] == "2026-08-01"
        # The 2026-08-04 boundary row is August; nothing from July leaks in and
        # nothing from September could.
        assert [d["date"] for d in out["items"]] == [
            "2026-08-04", "2026-08-09", "2026-08-10", "2026-08-11",
        ]

    def test_it_excludes_a_row_past_the_month_end(self, tmp_path):
        """The rolling mode is open-ended; a month is CLOSED at both ends.

        A row in September must not appear under August's heading — and the
        rolling path has no `end` at all, so this is the branch that needed
        writing rather than reusing.
        """
        tr.reset_cache()
        p = tmp_path / "perf.json"
        p.write_text(json.dumps([
            _rec("A", "LONG", 1.0, 1.0, _ts(2026, 8, 31, 23)),
            _rec("B", "LONG", 1.0, 5.0, _ts(2026, 9, 1, 1)),
        ]), encoding="utf-8")
        out = tr.build_track_record(
            month="2026-08", path=str(p),
            now=datetime(2026, 9, 5, 12, tzinfo=UTC),
        )
        assert [d["date"] for d in out["items"]] == ["2026-08-31"]
        assert out["summary"]["n"] == 1
        tr.reset_cache()

    def test_a_month_with_no_trades_is_empty_rather_than_refused(
        self, contract_path
    ):
        """And that emptiness is now MEANINGFUL.

        The month was fetched, so "no rows" is the market being quiet, not our
        window being elsewhere. That is precisely what lets the grid render `—`
        on a day instead of having to say "not loaded".
        """
        out = tr.build_track_record(
            month="2026-01", path=contract_path, now=CONTRACT_NOW,
        )
        assert out["unavailable_reason"] == ""
        assert out["items"] == []
        assert out["summary"]["n"] == 0
        # ...and the ledger counts still describe the whole record, so a caller
        # can tell an empty month from an empty record.
        assert out["total_records"] == CONTRACT_EXPECTED["total_records"]

    def test_month_spans_are_calendar_spans_not_thirty_days(self):
        for key, first, nxt in [
            ("2026-01", datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 2, 1, tzinfo=UTC)),
            ("2026-02", datetime(2026, 2, 1, tzinfo=UTC), datetime(2026, 3, 1, tzinfo=UTC)),
            ("2026-12", datetime(2026, 12, 1, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC)),
            # Leap year — 29 days, and the span must still land on the 1st.
            ("2028-02", datetime(2028, 2, 1, tzinfo=UTC), datetime(2028, 3, 1, tzinfo=UTC)),
        ]:
            assert tr.month_span(key) == (first, nxt), key

    def test_an_unparseable_month_is_REFUSED_not_silently_a_window(
        self, contract_path
    ):
        """Falling back to the rolling window would render the wrong period
        under a month's heading, and the caller could never tell."""
        for bad in ("2026-13", "August", "2026", "", "2026-1-1"):
            out = tr.build_track_record(
                month=bad, path=contract_path, now=CONTRACT_NOW,
            )
            if bad == "":
                # Empty means "no month asked for" — the rolling window, which
                # is the default and not a refusal.
                assert out["unavailable_reason"] == ""
                assert out["month"] == ""
                continue
            assert out["unavailable_reason"] == "bad_month", bad
            assert out["items"] == [], bad

    def test_the_rolling_window_is_untouched_by_the_new_parameter(
        self, contract_path
    ):
        """The two modes are independent controls; adding one must not move
        the other. This is the contract vector, re-asserted through the same
        function that now carries a second mode."""
        out = tr.build_track_record(
            days=CONTRACT_DAYS, path=contract_path, now=CONTRACT_NOW,
        )
        assert out["month"] == ""
        assert out["range_start"] == CONTRACT_EXPECTED["range_start"]
        for key, want in CONTRACT_EXPECTED["summary"].items():
            assert out["summary"][key] == pytest.approx(want, abs=1e-9), key


class TestEarliestDate:
    """Where a month stepper should stop.

    Without it a reader paging backwards walks into empty months forever and
    cannot tell "we never traded then" from "you are past the beginning of the
    record" — a blank with no cause, one control over.
    """

    def test_it_is_the_oldest_close_in_the_WHOLE_record(self, contract_path):
        # Not the oldest in the window: the stepper needs to know where the
        # record ends, which a windowed answer cannot say.
        out = tr.build_track_record(
            days=1, path=contract_path, now=CONTRACT_NOW,
        )
        assert out["earliest_date"] == "2026-08-04"

    def test_it_is_blank_rather_than_a_guess_when_nothing_is_dateable(
        self, tmp_path
    ):
        tr.reset_cache()
        p = tmp_path / "perf.json"
        p.write_text(json.dumps([
            _rec("A", "LONG", 1.0, 1.0, None, timestamp=None, create_timestamp=None),
        ]), encoding="utf-8")
        out = tr.build_track_record(path=str(p), now=CONTRACT_NOW)
        assert out["earliest_date"] == ""
        assert out["undateable"] == 1
        tr.reset_cache()
