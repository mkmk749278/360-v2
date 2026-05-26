"""Tests for the per-user paper-mode view filter (2026-05-23).

Covers :mod:`src.api.paper_user_view` — the helper module that turns
the engine's shared paper-trade ledger into per-user visibility windows.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.api.paper_user_view import (
    filter_trades_for_user,
    pnl_history_for_user,
    trade_closed_within_any_window,
)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def test_trade_outside_all_windows_is_hidden() -> None:
    """A trade closed before the user's first subscription is invisible."""
    windows = [("2026-05-23T10:00:00+00:00", None)]
    assert not trade_closed_within_any_window(
        "2026-05-22T15:00:00+00:00", windows,
    )


def test_trade_inside_active_window_is_visible() -> None:
    windows = [("2026-05-23T10:00:00+00:00", None)]
    assert trade_closed_within_any_window(
        "2026-05-23T12:00:00+00:00", windows,
    )


def test_trade_inside_closed_window_is_visible() -> None:
    windows = [("2026-05-22T10:00:00+00:00", "2026-05-22T15:00:00+00:00")]
    assert trade_closed_within_any_window(
        "2026-05-22T12:00:00+00:00", windows,
    )


def test_trade_after_closed_window_is_hidden() -> None:
    """A trade after a window's ended_at is not in that window."""
    windows = [("2026-05-22T10:00:00+00:00", "2026-05-22T15:00:00+00:00")]
    assert not trade_closed_within_any_window(
        "2026-05-22T16:00:00+00:00", windows,
    )


def test_trade_in_one_of_multiple_windows_is_visible() -> None:
    """Sum-of-windows semantics: a trade in any window is visible."""
    windows = [
        ("2026-05-20T00:00:00+00:00", "2026-05-21T00:00:00+00:00"),
        ("2026-05-23T00:00:00+00:00", None),
    ]
    assert trade_closed_within_any_window(
        "2026-05-20T12:00:00+00:00", windows,
    )
    assert trade_closed_within_any_window(
        "2026-05-23T01:00:00+00:00", windows,
    )
    # Between the two windows — invisible.
    assert not trade_closed_within_any_window(
        "2026-05-22T00:00:00+00:00", windows,
    )


def test_no_windows_means_no_visibility() -> None:
    """Fresh users (empty subscription list) see nothing — bug-fix invariant."""
    assert not trade_closed_within_any_window(
        "2026-05-23T00:00:00+00:00", [],
    )


def test_filter_trades_for_user_empty_windows_returns_empty() -> None:
    rows = [
        {"closed_at": "2026-05-23T00:00:00+00:00", "net_pnl_usd": 5.0},
        {"closed_at": "2026-05-22T00:00:00+00:00", "net_pnl_usd": -2.0},
    ]
    assert filter_trades_for_user(rows, []) == []


def test_filter_trades_for_user_keeps_only_in_window() -> None:
    rows = [
        {"closed_at": "2026-05-23T01:00:00+00:00", "net_pnl_usd": 5.0},
        {"closed_at": "2026-05-22T01:00:00+00:00", "net_pnl_usd": -2.0},
        {"closed_at": "2026-05-23T02:00:00+00:00", "net_pnl_usd": 1.0},
    ]
    windows = [("2026-05-23T00:00:00+00:00", None)]
    out = filter_trades_for_user(rows, windows)
    assert len(out) == 2
    assert all(row["closed_at"].startswith("2026-05-23") for row in out)


def test_filter_open_trades_use_created_at_when_include_open() -> None:
    """Open positions (closed_at=None) are admitted iff their created_at
    falls within a user window AND include_open=True."""
    rows = [
        {"closed_at": None, "created_at": "2026-05-23T01:00:00+00:00",
         "net_pnl_usd": None},
        {"closed_at": None, "created_at": "2026-05-22T01:00:00+00:00",
         "net_pnl_usd": None},
    ]
    windows = [("2026-05-23T00:00:00+00:00", None)]
    # include_open=False filters all open trades out
    assert filter_trades_for_user(rows, windows, include_open=False) == []
    # include_open=True keeps the one created inside the window
    out = filter_trades_for_user(rows, windows, include_open=True)
    assert len(out) == 1
    assert out[0]["created_at"].startswith("2026-05-23")


def test_pnl_history_for_user_bucket_aggregation() -> None:
    """Daily PnL bucketing sums net_pnl_usd by UTC date of closed_at."""
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    rows = [
        {"closed_at": _iso(datetime.combine(today, datetime.min.time(),
                                            tzinfo=timezone.utc)),
         "net_pnl_usd": 3.0},
        {"closed_at": _iso(datetime.combine(today, datetime.min.time(),
                                            tzinfo=timezone.utc)
                            + timedelta(hours=2)),
         "net_pnl_usd": 2.5},
        {"closed_at": _iso(datetime.combine(yesterday, datetime.min.time(),
                                            tzinfo=timezone.utc)),
         "net_pnl_usd": -1.0},
    ]
    windows = [
        (_iso(datetime.combine(yesterday, datetime.min.time(),
                                tzinfo=timezone.utc) - timedelta(hours=1)),
         None),
    ]
    series, weekly, monthly = pnl_history_for_user(rows, windows, days=7)
    # Series length = days (7), oldest-first; today and yesterday have buckets
    assert len(series) == 7
    today_key = today.strftime("%Y-%m-%d")
    yest_key = yesterday.strftime("%Y-%m-%d")
    series_dict = dict(series)
    assert series_dict[today_key] == 5.5
    assert series_dict[yest_key] == -1.0
    # Weekly rollup matches sum.
    assert weekly == 4.5
    # Monthly includes weekly (no other entries).
    assert monthly == 4.5


def test_pnl_history_for_user_filters_out_invisible_trades() -> None:
    """Trades outside subscription windows must not appear in any bucket."""
    today = datetime.now(timezone.utc).date()
    rows = [
        # Visible
        {"closed_at": _iso(datetime.combine(today, datetime.min.time(),
                                            tzinfo=timezone.utc)
                            + timedelta(hours=10)),
         "net_pnl_usd": 5.0},
        # Invisible (pre-window)
        {"closed_at": "2020-01-01T00:00:00+00:00", "net_pnl_usd": 99.0},
    ]
    windows = [(_iso(datetime.combine(today, datetime.min.time(),
                                       tzinfo=timezone.utc)
                      + timedelta(hours=5)), None)]
    series, weekly, monthly = pnl_history_for_user(rows, windows, days=7)
    today_key = today.strftime("%Y-%m-%d")
    series_dict = dict(series)
    assert series_dict[today_key] == 5.0
    assert weekly == 5.0
    assert monthly == 5.0


def test_malformed_iso_stamps_are_silently_skipped() -> None:
    """A row with a malformed closed_at must not 500 — return empty/skip."""
    rows = [{"closed_at": "not-an-iso-stamp", "net_pnl_usd": 5.0}]
    windows = [("2026-05-23T00:00:00+00:00", None)]
    assert filter_trades_for_user(rows, windows) == []




# ---------------------------------------------------------------------------
# signal_visible_within_any_window — open-position window check
# (PR #503, 2026-05-26)
# ---------------------------------------------------------------------------


from src.api.paper_user_view import (  # noqa: E402
    rolling_pnl_for_user,
    signal_visible_within_any_window,
)


def test_signal_visible_accepts_naive_datetime() -> None:
    """Naive datetimes are interpreted as UTC — same posture as the
    underlying ISO-string parser."""
    naive = datetime(2026, 5, 23, 12, 0, 0)
    windows = [("2026-05-23T10:00:00+00:00", None)]
    assert signal_visible_within_any_window(naive, windows)


def test_signal_visible_accepts_aware_datetime() -> None:
    aware = datetime(2026, 5, 23, 12, 0, 0, tzinfo=timezone.utc)
    windows = [("2026-05-23T10:00:00+00:00", None)]
    assert signal_visible_within_any_window(aware, windows)


def test_signal_visible_outside_window_is_hidden() -> None:
    """A signal dispatched before the user's window opened is hidden."""
    pre_window = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
    windows = [("2026-05-23T00:00:00+00:00", None)]
    assert not signal_visible_within_any_window(pre_window, windows)


def test_signal_visible_with_iso_string_input() -> None:
    """Defensive: ISO-string input is accepted (mirrors trade rows)."""
    windows = [("2026-05-23T00:00:00+00:00", None)]
    assert signal_visible_within_any_window(
        "2026-05-23T12:00:00+00:00", windows,
    )


def test_signal_visible_none_timestamp_is_hidden() -> None:
    """A signal with no dispatch_timestamp + no timestamp is invisible."""
    windows = [("2026-05-23T00:00:00+00:00", None)]
    assert not signal_visible_within_any_window(None, windows)


def test_signal_visible_empty_windows_is_hidden() -> None:
    """Fresh users (no subscription windows) see no signals — bug-fix
    invariant matching the trade-row filter."""
    aware = datetime(2026, 5, 23, 12, 0, 0, tzinfo=timezone.utc)
    assert not signal_visible_within_any_window(aware, [])


# ---------------------------------------------------------------------------
# rolling_pnl_for_user — daily/weekly/monthly/total rollups
# (PR #503, 2026-05-26)
# ---------------------------------------------------------------------------


def test_rolling_pnl_empty_windows_returns_all_zeros() -> None:
    """Fresh users see zeros across every window — the headline
    invariant of the day-zero Trade-tab fix."""
    rows = [
        {"closed_at": "2026-05-23T00:00:00+00:00", "net_pnl_usd": 5.0},
        {"closed_at": "2026-05-22T00:00:00+00:00", "net_pnl_usd": -2.0},
    ]
    counters = rolling_pnl_for_user(rows, [])
    assert counters == {
        "daily_pnl_usd": 0.0,
        "weekly_pnl_usd": 0.0,
        "monthly_pnl_usd": 0.0,
        "total_pnl_usd": 0.0,
    }


def test_rolling_pnl_buckets_today_separately() -> None:
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    rows = [
        {"closed_at": _iso(datetime.combine(today, datetime.min.time(),
                                            tzinfo=timezone.utc)
                            + timedelta(hours=2)),
         "net_pnl_usd": 3.0},
        {"closed_at": _iso(datetime.combine(yesterday, datetime.min.time(),
                                            tzinfo=timezone.utc)
                            + timedelta(hours=2)),
         "net_pnl_usd": -1.0},
    ]
    # Window opened 7 days ago — covers both rows.
    open_at = datetime.combine(today, datetime.min.time(),
                                tzinfo=timezone.utc) - timedelta(days=7)
    windows = [(_iso(open_at), None)]
    counters = rolling_pnl_for_user(rows, windows)
    # Daily = today only
    assert counters["daily_pnl_usd"] == 3.0
    # Weekly + monthly + total = both rows
    assert counters["weekly_pnl_usd"] == 2.0
    assert counters["monthly_pnl_usd"] == 2.0
    assert counters["total_pnl_usd"] == 2.0


def test_rolling_pnl_excludes_pre_window_trades() -> None:
    """Trades closed before the user's window started are not counted —
    same invariant as the trade-list filter."""
    today = datetime.now(timezone.utc).date()
    rows = [
        # Inside window
        {"closed_at": _iso(datetime.combine(today, datetime.min.time(),
                                            tzinfo=timezone.utc)
                            + timedelta(hours=10)),
         "net_pnl_usd": 4.0},
        # Outside window (engine-wide operator's prior trade)
        {"closed_at": "2024-01-01T00:00:00+00:00", "net_pnl_usd": 99.0},
    ]
    open_at = datetime.combine(today, datetime.min.time(),
                                tzinfo=timezone.utc) + timedelta(hours=5)
    windows = [(_iso(open_at), None)]
    counters = rolling_pnl_for_user(rows, windows)
    # Pre-window trade absent from every counter
    assert counters["daily_pnl_usd"] == 4.0
    assert counters["weekly_pnl_usd"] == 4.0
    assert counters["monthly_pnl_usd"] == 4.0
    assert counters["total_pnl_usd"] == 4.0


def test_rolling_pnl_total_spans_full_window_history() -> None:
    """``total_pnl_usd`` spans the user's full visible history — older
    than 30 days but inside the window still counts."""
    today = datetime.now(timezone.utc).date()
    long_ago = today - timedelta(days=60)
    rows = [
        # >30 days ago but inside window — only counted in total
        {"closed_at": _iso(datetime.combine(long_ago, datetime.min.time(),
                                             tzinfo=timezone.utc)
                            + timedelta(hours=10)),
         "net_pnl_usd": 7.5},
    ]
    # Window opened 90 days ago — covers the trade.
    open_at = datetime.combine(today, datetime.min.time(),
                                tzinfo=timezone.utc) - timedelta(days=90)
    windows = [(_iso(open_at), None)]
    counters = rolling_pnl_for_user(rows, windows)
    assert counters["daily_pnl_usd"] == 0.0
    assert counters["weekly_pnl_usd"] == 0.0
    assert counters["monthly_pnl_usd"] == 0.0  # outside 30-day rolling window
    assert counters["total_pnl_usd"] == 7.5  # but inside subscription window


def test_rolling_pnl_skips_malformed_rows() -> None:
    """Malformed rows are silently skipped — must not 500."""
    today = datetime.now(timezone.utc).date()
    rows = [
        {"closed_at": "not-an-iso-stamp", "net_pnl_usd": 99.0},
        {"closed_at": _iso(datetime.combine(today, datetime.min.time(),
                                             tzinfo=timezone.utc)
                            + timedelta(hours=2)),
         "net_pnl_usd": "not-a-number"},  # type: ignore[dict-item]
        {"closed_at": _iso(datetime.combine(today, datetime.min.time(),
                                             tzinfo=timezone.utc)
                            + timedelta(hours=4)),
         "net_pnl_usd": 1.5},
    ]
    open_at = datetime.combine(today, datetime.min.time(),
                                tzinfo=timezone.utc) - timedelta(days=1)
    windows = [(_iso(open_at), None)]
    counters = rolling_pnl_for_user(rows, windows)
    # Only the well-formed numeric row is counted.
    assert counters["daily_pnl_usd"] == 1.5
    assert counters["total_pnl_usd"] == 1.5
