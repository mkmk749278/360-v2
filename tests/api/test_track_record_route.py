"""``GET /api/track-record`` — the route the Lumin Pulse tab reads.

The reducers themselves are pinned in ``tests/test_track_record.py`` against a
vector shared with ops. What this file guards is the *wiring*, which is where
this repo's defects actually live: a field the schema drops, a switch nothing
reads, an identity requirement that would lock out the one caller it exists for.

Three properties, each of which would fail silently rather than crash:

* **It is reachable without a token.** A new subscriber with no trades is the
  reader this endpoint was built for, and the book is identical for every
  caller. An auth dependency added here would empty the card for exactly the
  audience it is meant to convince.
* **The response model carries every key the reducer produces.** Pydantic drops
  unknown fields silently, so a schema that forgot ``partial_reason`` would ship
  a chart with today rendering as a finished day and nothing anywhere failing.
* **The switch is read from the tunable, not from the env constant**, so the
  owner can pull a subscriber-facing performance claim without a redeploy.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src import track_record as tr  # noqa: E402
from src.api.server import build_app  # noqa: E402

_TEST_SECRET = "track-record-route-test-secret"


class _StubEngine:
    """/api/track-record reads a file, never the engine — hence the emptiness.

    That is deliberate and worth stating: the endpoint works identically in
    single-process mode and in the isolated ``api`` container, because both
    mount ``/app/data``. Reaching through the engine facade would have made it
    a Redis-snapshot problem for no gain.
    """


@pytest.fixture
def client(tmp_path, monkeypatch):
    now = datetime.now(tz=timezone.utc)
    rows = [
        {
            "symbol": "BTCUSDT", "direction": "LONG",
            "setup_class": "MOVER_TREND_PULLBACK", "entry": 30000.0,
            "pnl_pct": 2.0,
            "terminal_outcome_timestamp": (now - timedelta(days=1)).timestamp(),
        },
        {
            "symbol": "ETHUSDT", "direction": "SHORT",
            "setup_class": "MOVER_AVWAP_SCALP", "entry": 2000.0,
            "pnl_pct": -1.0,
            "terminal_outcome_timestamp": now.timestamp(),
        },
    ]
    path = tmp_path / "signal_performance.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    tr.reset_cache()
    monkeypatch.setattr(tr, "DEFAULT_RECORD_PATH", str(path))
    app = build_app(_StubEngine(), jwt_secret=_TEST_SECRET, allow_static=False)
    yield TestClient(app)
    tr.reset_cache()


class TestReachableWithoutAuth:
    def test_no_token_is_required(self, client):
        assert client.get("/api/track-record").status_code == 200

    def test_the_book_is_the_same_for_every_caller(self, client):
        """No identity is resolved, so two callers cannot see two books.

        If this ever changes, the card stops being the thing a signed-out or
        brand-new user can read — and ``/api/pnl/history`` already exists for
        the per-user question.
        """
        a = client.get("/api/track-record").json()
        b = client.get(
            "/api/track-record", headers={"Authorization": "Bearer nonsense"}
        ).json()
        assert a["summary"] == b["summary"]
        assert a["items"] == b["items"]


class TestSchemaKeepsEveryKey:
    def test_response_model_drops_nothing_the_reducer_produces(self, client):
        """Pydantic silently drops unknown fields.

        A schema missing ``partial_reason`` would render today as a finished
        day; one missing ``moves`` would hide concentration. Compare against the
        reducer's own output rather than a hand-written key list, so a field
        added to the reducer and forgotten in the schema fails here.
        """
        served = client.get("/api/track-record?days=30").json()
        direct = tr.build_track_record(days=30, path=tr.DEFAULT_RECORD_PATH)

        assert set(direct) - set(served) == set()
        assert set(direct["summary"]) - set(served["summary"]) == set()
        assert served["items"], "fixture should produce at least one day"
        assert set(direct["items"][0]) - set(served["items"][0]) == set()

    def test_todays_bucket_is_marked_in_progress_end_to_end(self, client):
        served = client.get("/api/track-record?days=30").json()
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        by_date = {d["date"]: d for d in served["items"]}
        assert by_date[today]["partial_reason"] == "in_progress"


class TestInputs:
    def test_amount_scales_dollars_and_leaves_percentages_alone(self, client):
        at100 = client.get("/api/track-record?amount=100").json()["summary"]
        at500 = client.get("/api/track-record?amount=500").json()["summary"]
        assert at500["net_usd"] == pytest.approx(at100["net_usd"] * 5)
        assert at500["total_net_pct"] == pytest.approx(at100["total_net_pct"])

    def test_the_assumed_size_and_fee_ride_in_the_response(self, client):
        """A dollar figure whose size the reader cannot see is an assumption
        wearing a measurement's clothes."""
        got = client.get("/api/track-record?amount=250&fee_pct=0.1").json()
        assert got["amount_usdt"] == pytest.approx(250.0)
        assert got["fee_pct"] == pytest.approx(0.1)

    def test_zero_fee_is_honoured_rather_than_falling_back_to_the_default(
        self, client
    ):
        """0 is a legitimate value (the gross book), so a falsy check here
        would silently charge the default fee to a caller who asked for none."""
        got = client.get("/api/track-record?fee_pct=0").json()
        assert got["fee_pct"] == pytest.approx(0.0)
        assert got["summary"]["net_usd"] == pytest.approx(
            got["summary"]["gross_usd"]
        )

    def test_out_of_range_days_is_refused_by_the_route(self, client):
        assert client.get("/api/track-record?days=0").status_code == 422
        assert client.get("/api/track-record?days=999").status_code == 422


class TestTheSwitch:
    def test_off_serves_an_empty_book_with_a_named_reason(self, client, monkeypatch):
        """Not a 404 and not a bare empty list: the app must be able to tell
        'the owner switched this off' from 'the record could not be read', and
        hide the card either way without inventing a caption."""
        from src import runtime_tunables as rt

        monkeypatch.setattr(
            rt, "get", lambda key: False if key == "track_record_public_enabled" else rt.get(key)
        )
        got = client.get("/api/track-record").json()
        assert got["enabled"] is False
        assert got["unavailable_reason"] == "disabled"
        assert got["items"] == []
        assert got["summary"]["n"] == 0

    def test_the_switch_is_registered_as_a_tunable_ops_can_flip(self):
        from src import runtime_tunables as rt

        tun = rt.registry().get("track_record_public_enabled")
        assert tun is not None, "ops cannot flip a switch that is not registered"
        assert tun.type == "bool"

    def test_a_tunable_read_failure_never_500s_the_page(self, client, monkeypatch):
        """Falls back to the env default. A performance card is not worth an
        error page, and a Firestore blip must not take one."""
        from src import runtime_tunables as rt

        def _boom(key):
            raise RuntimeError("firestore down")

        monkeypatch.setattr(rt, "get", _boom)
        resp = client.get("/api/track-record")
        assert resp.status_code == 200
        assert resp.json()["enabled"] is True


class TestMissingRecord:
    def test_a_record_the_engine_has_never_written_is_named_not_blank(
        self, tmp_path, monkeypatch
    ):
        """An engine that has closed no signal has never written the file. That
        is not a fault, and 'missing' is not 'unreadable' — different fixes."""
        tr.reset_cache()
        monkeypatch.setattr(tr, "DEFAULT_RECORD_PATH", str(tmp_path / "nope.json"))
        app = build_app(_StubEngine(), jwt_secret=_TEST_SECRET, allow_static=False)
        got = TestClient(app).get("/api/track-record").json()
        assert got["enabled"] is True
        assert got["unavailable_reason"] == "missing"
        assert got["items"] == []
        tr.reset_cache()


class TestSignalList:
    """The drill-down: which signals made a day what it was.

    A headline nobody can open is a claim rather than a record. The property
    that matters is that the list under a bar IS the bar — same population,
    same close-time filter, same fee — because two surfaces disagreeing about
    one day is exactly the seam this system keeps paying for.
    """

    def test_a_day_filter_selects_the_same_rows_the_bucket_counted(self, client):
        record = client.get("/api/track-record?days=30").json()
        for day in record["items"]:
            listed = client.get(
                f"/api/track-record/signals?date={day['date']}"
            ).json()
            assert listed["matched"] == day["n"], day["date"]

    def test_the_window_list_matches_the_window_summary(self, client):
        record = client.get("/api/track-record?days=30").json()
        listed = client.get("/api/track-record/signals?days=30").json()
        assert listed["matched"] == record["summary"]["n"]

    def test_rows_carry_what_a_reader_needs_to_recognise_the_trade(self, client):
        listed = client.get("/api/track-record/signals?days=30").json()
        row = listed["items"][0]
        for key in ("signal_id", "symbol", "direction", "setup", "outcome",
                    "entry", "closed_at", "pnl_pct", "net_pct", "net_usd"):
            assert key in row, key

    def test_newest_first(self, client):
        listed = client.get("/api/track-record/signals?days=30").json()
        stamps = [r["closed_at"] for r in listed["items"]]
        assert stamps == sorted(stamps, reverse=True)

    def test_the_fee_is_charged_here_too(self, client):
        listed = client.get("/api/track-record/signals?days=30").json()
        row = next(r for r in listed["items"] if r["pnl_pct"] is not None)
        assert row["net_pct"] == pytest.approx(
            row["pnl_pct"] - listed["fee_pct"]
        )

    def test_an_unreadable_outcome_is_listed_with_null_money(self, tmp_path,
                                                             monkeypatch):
        """Included, not dropped.

        It is part of what closed that day, and omitting it would make the
        list disagree with the count above it. The shortfall is named on the
        summary instead.
        """
        now = datetime.now(tz=timezone.utc)
        path = tmp_path / "signal_performance.json"
        path.write_text(json.dumps([
            {"symbol": "A", "direction": "LONG", "entry": 1.0, "pnl_pct": None,
             "terminal_outcome_timestamp": now.timestamp()},
        ]), encoding="utf-8")
        tr.reset_cache()
        monkeypatch.setattr(tr, "DEFAULT_RECORD_PATH", str(path))
        app = build_app(_StubEngine(), jwt_secret=_TEST_SECRET, allow_static=False)
        listed = TestClient(app).get("/api/track-record/signals").json()
        assert listed["matched"] == 1
        assert listed["items"][0]["pnl_pct"] is None
        assert listed["items"][0]["net_usd"] is None
        tr.reset_cache()

    def test_the_cap_is_applied_after_filtering_and_says_when_it_bit(
        self, tmp_path, monkeypatch
    ):
        now = datetime.now(tz=timezone.utc)
        path = tmp_path / "signal_performance.json"
        path.write_text(json.dumps([
            {"symbol": f"S{i}", "direction": "LONG", "entry": 1.0,
             "pnl_pct": 1.0,
             "terminal_outcome_timestamp": (now - timedelta(minutes=i)).timestamp()}
            for i in range(20)
        ]), encoding="utf-8")
        tr.reset_cache()
        monkeypatch.setattr(tr, "DEFAULT_RECORD_PATH", str(path))
        app = build_app(_StubEngine(), jwt_secret=_TEST_SECRET, allow_static=False)
        listed = TestClient(app).get("/api/track-record/signals?limit=5").json()
        # `matched` reports the true population; only the render is capped.
        assert listed["matched"] == 20
        assert listed["truncated"] is True
        assert len(listed["items"]) == 5
        tr.reset_cache()

    def test_off_returns_an_empty_list_with_a_named_reason(self, client,
                                                           monkeypatch):
        from src import runtime_tunables as rt

        monkeypatch.setattr(rt, "get", lambda key: False)
        got = client.get("/api/track-record/signals").json()
        assert got["enabled"] is False
        assert got["unavailable_reason"] == "disabled"
        assert got["items"] == []
