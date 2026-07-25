"""Rate-limit + cache tests for the exit-method bake-off fetch layer.

WHY (2026-07-25). The first run after the Backtester was made linear failed with
HTTP 429 on all 20 symbols. The script fetched with raw urllib at a fixed 0.12s
pause and `limit=1500`, bypassing every piece of rate-limit machinery both repos
already have (`src/rate_limiter.py`, `src/binance.py`, ops' `_BanCircuit`).

That matters more than a failed analysis run: the script executes via
`docker exec` inside the engine container, so it shares the production IP with
live trading, and Binance escalates sustained 429s to a 418 IP ban — which would
stop live signals and order execution. The box was already IP-banned once on
2026-07-24.

These tests pin the properties that keep the job off the money path's budget.
All are pure: no network, no sleeping on real clocks beyond tiny bounded naps.
"""
from __future__ import annotations

import io
import urllib.error

import pytest

import scripts.exit_method_backtest as eb


class TestWeightBudgetIsSpentEfficiently:
    def test_page_limit_sits_in_the_cheapest_weight_tier(self):
        """limit=499 is weight 2; 500 would cost 5 and 1500 would cost 10.

        Candles per weight unit: 499/2 = 249.5, vs 1000/5 = 200 and 1500/10 =
        150. Paging at the 1500 cap — what the script used to do — is the *worst*
        setting available, not the best.
        """
        assert eb._PAGE_LIMIT == 499
        assert eb._PAGE_WEIGHT == 2
        assert eb._PAGE_LIMIT / eb._PAGE_WEIGHT > 1500 / 10
        assert eb._PAGE_LIMIT / eb._PAGE_WEIGHT > 1000 / 5

    def test_default_budget_stays_inside_engine_headroom(self):
        """src/rate_limiter.py budgets the engine 2,200 of the 2,400 IP cap."""
        assert eb._DEFAULT_WEIGHT_PER_MIN <= eb._FUTURES_WEIGHT_CAP - 2_200


class _FakeClock:
    """A clock that only advances when the code under test sleeps."""

    def __init__(self, t: float = 1000.0) -> None:
        self.t = t
        self.slept: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.t += seconds


def _paced(per_min: int) -> tuple[eb.WeightPacer, _FakeClock]:
    clock = _FakeClock()
    return eb.WeightPacer(per_min=per_min, now=clock.now, sleep=clock.sleep), clock


class TestWeightPacer:
    def test_first_spend_is_immediate(self):
        pacer, clock = _paced(200)
        pacer.spend(2)
        assert clock.slept == []

    def test_blocks_once_the_budget_is_exhausted(self):
        pacer, clock = _paced(4)
        pacer.spend(2)
        pacer.spend(2)
        pacer.spend(2)  # over budget — must wait for the window to roll
        assert clock.slept, "pacer did not throttle once over budget"
        assert pacer.waited_sec > 0

    def test_throttling_holds_the_long_run_to_the_budget(self):
        """The property that actually protects live trading: over a long run the
        realised rate must not exceed the configured weight/min."""
        pacer, clock = _paced(200)
        start = clock.t
        spends = 400                      # 400 * 2 = 800 weight
        for _ in range(spends):
            pacer.spend(2)
        # A spend claims budget for the 60s window it opens, so the run occupies
        # its elapsed span plus that trailing window.
        elapsed_min = max((clock.t - start + 60.0) / 60.0, 1e-9)
        realised = (spends * 2) / elapsed_min
        assert realised <= 200 * 1.05, f"realised {realised:.0f} weight/min > budget"

    def test_spend_terminates_promptly(self):
        """Regression: spacing was once re-measured in a loop, so once the
        remainder rounded below a float ulp `spend` spun forever (34M sleeps
        advancing the clock 24s). Each spend must cost a bounded number of naps.
        """
        pacer, clock = _paced(200)
        for _ in range(400):
            pacer.spend(2)
        assert len(clock.slept) <= 400 * 3, (
            f"spend is looping: {len(clock.slept)} sleeps for 400 spends"
        )

    def test_does_not_burst_the_budget(self):
        """src/rate_limiter.py: burning the budget in a burst is what trips
        Binance's hard 429 lockout (~42s at 100% usage) — hence engine-side burst
        protection. This job must trickle, not burst."""
        pacer, clock = _paced(200)
        stamps: list[float] = []
        for _ in range(30):
            pacer.spend(2)
            stamps.append(clock.t)

        expected_gap = 60.0 * 2 / 200.0          # 0.6s between weight-2 requests
        gaps = [b - a for a, b in zip(stamps, stamps[1:])]
        assert gaps, "no spacing observed"
        assert min(gaps) >= expected_gap * 0.99, (
            f"requests bursted: min gap {min(gaps):.3f}s < {expected_gap:.3f}s"
        )

    def test_a_bigger_budget_spaces_requests_more_tightly(self):
        tight, tight_clock = _paced(200)
        loose, loose_clock = _paced(600)
        for _ in range(20):
            tight.spend(2)
            loose.spend(2)
        assert loose_clock.t < tight_clock.t

    def test_yields_when_live_traffic_nears_the_cap(self):
        pacer, clock = _paced(200)

        pacer.observe(100)          # engine idle — no reason to wait
        assert clock.slept == []

        pacer.observe(eb._YIELD_ABOVE_USED_WEIGHT + 1)
        assert clock.slept == [eb._YIELD_SLEEP_SEC]
        assert pacer.yielded_sec == eb._YIELD_SLEEP_SEC

    def test_observe_tolerates_a_missing_header(self):
        pacer, clock = _paced(200)
        pacer.observe(None)  # must not raise
        assert clock.slept == []


def _http_error(code, headers=None, body=b"nope"):
    return urllib.error.HTTPError(
        url="http://x", code=code, msg="err",
        hdrs=headers or {}, fp=io.BytesIO(body),
    )


class TestRetryAndBanHandling:
    """All of these drive the pacer's injected clock — never the real one, so a
    retry that sleeps 30s costs the suite nothing."""

    def test_retries_429_and_honours_retry_after(self, monkeypatch):
        pacer, clock = _paced(1000)
        calls = {"n": 0}

        def fake_get(url, timeout=30.0):
            calls["n"] += 1
            if calls["n"] == 1:
                raise _http_error(429, headers={"Retry-After": "7"})
            return [[1, "1", "2", "0.5", "1.5", "10"]], 50

        monkeypatch.setattr(eb, "_get", fake_get)
        out = eb._get_paced("http://x", pacer)
        assert out and calls["n"] == 2
        assert 7.0 in clock.slept, f"Retry-After ignored; slept {clock.slept}"

    def test_backs_off_exponentially_without_retry_after(self, monkeypatch):
        pacer, clock = _paced(1000)
        calls = {"n": 0}

        def fake_get(url, timeout=30.0):
            calls["n"] += 1
            if calls["n"] < 3:
                raise _http_error(503)
            return [], 10

        monkeypatch.setattr(eb, "_get", fake_get)
        eb._get_paced("http://x", pacer)
        backoffs = [s for s in clock.slept if s in (1.0, 2.0, 4.0)]
        assert backoffs == [1.0, 2.0], f"expected exponential backoff, got {clock.slept}"

    @pytest.mark.parametrize("code", sorted(eb._BAN_STATUSES))
    def test_a_ban_aborts_and_is_never_retried(self, monkeypatch, code):
        """Retrying into a ban is what deepens it — the exact #778 failure."""
        pacer, _clock = _paced(1000)
        calls = {"n": 0}

        def fake_get(url, timeout=30.0):
            calls["n"] += 1
            raise _http_error(code, body=b"banned until 999")

        monkeypatch.setattr(eb, "_get", fake_get)
        with pytest.raises(eb.BinanceBanned):
            eb._get_paced("http://x", pacer)
        assert calls["n"] == 1, "a ban must not be retried"

    def test_gives_up_after_max_attempts(self, monkeypatch):
        pacer, _clock = _paced(10_000)
        monkeypatch.setattr(
            eb, "_get", lambda url, timeout=30.0: (_ for _ in ()).throw(_http_error(500))
        )
        with pytest.raises(urllib.error.HTTPError):
            eb._get_paced("http://x", pacer)


class TestKlineCache:
    def _rows(self, start_ms, n, step_ms):
        return [(start_ms + i * step_ms, 1.0, 2.0, 0.5, 1.5, 10.0) for i in range(n)]

    def test_roundtrips_through_gzip_csv(self, tmp_path):
        path = str(tmp_path / "BTCUSDT_5m.csv.gz")
        rows = self._rows(1_000_000, 25, 300_000)
        eb._save_cache(path, rows)
        assert eb._load_cache(path) == rows

    def test_missing_or_corrupt_cache_is_not_fatal(self, tmp_path):
        assert eb._load_cache(str(tmp_path / "nope.csv.gz")) == []
        bad = tmp_path / "bad.csv.gz"
        bad.write_bytes(b"not gzip at all")
        assert eb._load_cache(str(bad)) == []

    def test_a_warm_cache_fetches_nothing(self, tmp_path, monkeypatch):
        step = 300_000  # 5m
        start = 1_600_000_000_000
        rows = self._rows(start, 40, step)
        eb._save_cache(str(tmp_path / "BTCUSDT_5m.csv.gz"), rows)

        # Pin "now" past the cached window so every cached bar counts as closed.
        monkeypatch.setattr(eb.time, "time", lambda: (rows[-1][0] + 10 * step) / 1000.0)

        def boom(*a, **kw):
            raise AssertionError("network hit despite a warm cache")

        monkeypatch.setattr(eb, "_fetch_range", boom)
        out = eb.fetch_klines("BTCUSDT", "5m", start, rows[-1][0],
                              cache_dir=str(tmp_path))
        assert out == rows

    def test_only_the_missing_tail_is_fetched(self, tmp_path, monkeypatch):
        step = 300_000
        start = 1_600_000_000_000
        cached = self._rows(start, 20, step)
        eb._save_cache(str(tmp_path / "BTCUSDT_5m.csv.gz"), cached)

        want_end = cached[-1][0] + 10 * step
        monkeypatch.setattr(eb.time, "time", lambda: (want_end + 5 * step) / 1000.0)

        asked: list[tuple[int, int]] = []

        def fake_range(symbol, interval, s, e, pacer):
            asked.append((s, e))
            n = (e - s) // step + 1
            return self._rows(s, int(n), step)

        monkeypatch.setattr(eb, "_fetch_range", fake_range)
        out = eb.fetch_klines("BTCUSDT", "5m", start, want_end,
                              cache_dir=str(tmp_path))

        assert len(asked) == 1, f"expected one gap fetch, got {asked}"
        assert asked[0][0] == cached[-1][0] + step, "refetched already-cached history"
        assert out[0][0] == start and out[-1][0] == want_end
        assert len(out) == len(set(r[0] for r in out)), "duplicate candles"

    def test_the_forming_bar_is_never_cached(self, tmp_path, monkeypatch):
        step = 300_000
        start = 1_600_000_000_000
        now_ms = start + 10 * step
        monkeypatch.setattr(eb.time, "time", lambda: now_ms / 1000.0)

        def fake_range(symbol, interval, s, e, pacer):
            n = (e - s) // step + 1
            return self._rows(s, int(n), step)

        monkeypatch.setattr(eb, "_fetch_range", fake_range)
        eb.fetch_klines("BTCUSDT", "5m", start, now_ms, cache_dir=str(tmp_path))

        cached = eb._load_cache(str(tmp_path / "BTCUSDT_5m.csv.gz"))
        assert cached, "nothing cached"
        # The bar still forming at now_ms must not be persisted.
        assert cached[-1][0] <= now_ms - step
