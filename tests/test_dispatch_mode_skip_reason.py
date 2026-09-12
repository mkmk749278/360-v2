"""``skip:mode`` must name WHICH world it is in (2026-09-13).

`resolve_user_mode_uid` returned a bare ``None`` for five structurally
different reasons and the dispatcher folded all five into one counter, so
*"the fleet is deliberately on paper"* and *"this process cannot read the
store"* were the same number on the same panel — on the gate that decides
whether a paying Auto subscriber's order is placed at all. That is the
repo's own *unknown is not a value* rule arriving on the money path, and
it is the 2026-09-02 blackout signature one gate over.

These pin the split. They deliberately do **not** assert that any of these
cases dispatches: the gate still fails closed in every one of them, per
B12, and a test that let one through would be pinning the wrong property.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src.api import user_overrides as uo

SRC = Path(__file__).resolve().parents[1] / "src"


class _Boom:
    """A user store whose lookup raises — the 'we could not ask' world."""

    def get_by_firebase_uid(self, _uid):  # noqa: D401
        raise RuntimeError("firestore unavailable")


class _NoUser:
    def get_by_firebase_uid(self, _uid):
        return None


class _User:
    def __init__(self, user_id=7):
        self.user_id = user_id


class _Found:
    def get_by_firebase_uid(self, _uid):
        return _User()


class _Overrides:
    def __init__(self, row):
        self._row = row

    def get_auto_trade(self, _uid):
        return self._row


def _patch(monkeypatch, *, singleton, user_store):
    monkeypatch.setattr(uo, "_SINGLETON", singleton, raising=False)
    import src.api.users as users_mod
    monkeypatch.setattr(users_mod, "get_singleton", lambda: user_store)


class TestReasonsAreDistinguished:
    def test_store_cold_is_not_a_user_choice(self, monkeypatch):
        _patch(monkeypatch, singleton=None, user_store=_Found())
        mode, reason = uo.resolve_user_mode_uid_detailed("uid-1")
        assert mode is None
        assert reason == uo.MODE_REASON_STORE_COLD
        assert reason in uo.MODE_UNREADABLE_REASONS

    def test_user_store_cold_is_not_a_user_choice(self, monkeypatch):
        _patch(monkeypatch, singleton=_Overrides({}), user_store=None)
        mode, reason = uo.resolve_user_mode_uid_detailed("uid-1")
        assert mode is None
        assert reason == uo.MODE_REASON_USER_STORE_COLD
        assert reason in uo.MODE_UNREADABLE_REASONS

    def test_a_raising_lookup_is_not_a_user_choice(self, monkeypatch):
        _patch(monkeypatch, singleton=_Overrides({}), user_store=_Boom())
        mode, reason = uo.resolve_user_mode_uid_detailed("uid-1")
        assert mode is None
        assert reason == uo.MODE_REASON_LOOKUP_FAILED
        assert reason in uo.MODE_UNREADABLE_REASONS

    def test_no_user_row_is_readable_not_a_fault(self, monkeypatch):
        _patch(monkeypatch, singleton=_Overrides({}), user_store=_NoUser())
        mode, reason = uo.resolve_user_mode_uid_detailed("uid-1")
        assert mode is None
        assert reason == uo.MODE_REASON_NO_USER_ROW
        # We asked and got an answer. Not a fault.
        assert reason not in uo.MODE_UNREADABLE_REASONS

    def test_paper_is_readable_and_is_a_user_choice(self, monkeypatch):
        _patch(monkeypatch, singleton=_Overrides({"mode": "paper"}),
               user_store=_Found())
        mode, reason = uo.resolve_user_mode_uid_detailed("uid-1")
        assert mode == "paper"
        assert reason == uo.MODE_REASON_OK
        assert reason not in uo.MODE_UNREADABLE_REASONS

    def test_mode_unset_is_readable_not_a_fault(self, monkeypatch):
        _patch(monkeypatch, singleton=_Overrides({"mode": ""}),
               user_store=_Found())
        mode, reason = uo.resolve_user_mode_uid_detailed("uid-1")
        assert mode is None
        assert reason == uo.MODE_REASON_UNSET
        assert reason not in uo.MODE_UNREADABLE_REASONS


class TestFailClosedDirectionIsUnchanged:
    """The whole point is that only observability changed."""

    @pytest.mark.parametrize("singleton,user_store", [
        (None, _Found()),
        (_Overrides({}), None),
        (_Overrides({}), _Boom()),
        (_Overrides({}), _NoUser()),
        (_Overrides({"mode": "paper"}), _Found()),
        (_Overrides({"mode": ""}), _Found()),
    ])
    def test_no_unreadable_world_ever_resolves_to_live(
        self, monkeypatch, singleton, user_store
    ):
        _patch(monkeypatch, singleton=singleton, user_store=user_store)
        mode, _ = uo.resolve_user_mode_uid_detailed("uid-1")
        assert mode not in ("live", "both")

    def test_the_thin_wrapper_still_returns_just_the_mode(self, monkeypatch):
        _patch(monkeypatch, singleton=_Overrides({"mode": "LIVE"}),
               user_store=_Found())
        # Callers that only want the value keep working, and the lowercase
        # normalisation the dispatcher's ("live", "both") check depends on
        # survives the refactor.
        assert uo.resolve_user_mode_uid("uid-1") == "live"


class TestTheFailureIsCounted:
    def test_a_raising_lookup_records_a_fail_open(self, monkeypatch):
        from src import fail_open
        seen = []
        monkeypatch.setattr(fail_open, "record",
                            lambda site, exc, **kw: seen.append((site, exc)))
        _patch(monkeypatch, singleton=_Overrides({}), user_store=_Boom())
        uo.resolve_user_mode_uid_detailed("uid-1")
        assert len(seen) == 1, (
            "a swallowed exception in a money-path read must reach "
            "fail_open, or the feature-liveness watchdog cannot page on it"
        )
        assert seen[0][0] == "user_overrides.resolve_user_mode_uid"

    def test_a_user_choice_records_no_failure(self, monkeypatch):
        from src import fail_open
        seen = []
        monkeypatch.setattr(fail_open, "record",
                            lambda site, exc, **kw: seen.append((site, exc)))
        _patch(monkeypatch, singleton=_Overrides({"mode": "paper"}),
               user_store=_Found())
        uo.resolve_user_mode_uid_detailed("uid-1")
        assert seen == [], (
            "filling the fail-open counter with non-failures is how a real "
            "one stops standing out"
        )


class TestDispatchStampsTheReason:
    """Pinned on the AST, not on a substring.

    Reverting the fix must fail this. A substring check for 'skip:mode'
    passes against BOTH trees — the exact rot this repo has recorded — so
    the assertion is that the noted key is an f-string carrying the
    reason, never a bare constant.
    """

    def _note_call(self):
        tree = ast.parse((SRC / "execution" / "signal_dispatch.py").read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_note"
                and node.args
            ):
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and arg.value == "skip:mode":
                    return "bare"
                if isinstance(arg, ast.JoinedStr):
                    literal = "".join(
                        v.value for v in arg.values
                        if isinstance(v, ast.Constant)
                    )
                    if literal.startswith("skip:mode"):
                        return "reasoned"
        return None

    def test_the_mode_skip_counter_carries_its_reason(self):
        assert self._note_call() == "reasoned", (
            "signal_dispatch must note skip:mode:<reason>, not a bare "
            "skip:mode — otherwise 'the fleet chose paper' and 'this "
            "process cannot read the store' are the same counter"
        )

    def test_the_probe_prefix_split_still_classifies_it_as_a_skip(self):
        # auto_dispatch_health_check partitions on startswith("skip:") and
        # renders via removeprefix, so an extra ':' segment is safe here —
        # unlike the '":" not in k' partition that broke /system/redis.
        key = "skip:mode:lookup_failed"
        assert key.startswith("skip:")
        assert key.removeprefix("skip:") == "mode:lookup_failed"

    def test_the_counter_key_space_is_bounded(self):
        from src.execution import signal_dispatch as sd
        # An arbitrary stored mode must not mint a new _FANOUT_TOTALS key.
        assert "live" in sd._KNOWN_USER_MODES
        assert "' OR 1=1 --" not in sd._KNOWN_USER_MODES
        assert len(sd._KNOWN_USER_MODES) <= 8


class TestTheReasonReachesTheOperator:
    """The counter is only worth changing if the probe message shows it.

    `auto_dispatch_health_check` renders `skip:*` by removing the prefix,
    so the reason arrives on the page with no change on that side — which
    is the property worth pinning, because it is what the owner reads
    instead of `docker exec`-ing for a log line.
    """

    def test_an_unreadable_store_reads_differently_from_a_user_choice(self):
        from src.execution import signal_dispatch as sd

        def _detail(skip_key: str) -> str:
            state: dict = {}
            sd.auto_dispatch_health_check(
                state,
                {"fanouts_with_users_total": 2.0, "attempts_total": 2.0},
            )
            ok, detail = sd.auto_dispatch_health_check(
                state,
                {
                    "fanouts_with_users_total": 8.0,
                    "attempts_total": 2.0,
                    skip_key: 9.0,
                },
                gap_threshold=5,
            )
            assert not ok
            return detail

        chose_paper = _detail("skip:mode:paper")
        could_not_ask = _detail("skip:mode:lookup_failed")

        assert "mode:paper=9" in chose_paper
        assert "mode:lookup_failed=9" in could_not_ask
        # The whole point: these two are no longer the same sentence.
        assert chose_paper != could_not_ask
