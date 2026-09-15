"""Guards for the user-lifecycle Telegram alerts (2026-09-15).

The defect this feature is most exposed to is not a bug in the alert — it is
a FOURTH user-creation path being added later that quietly does not announce.
``users.py`` already has three ``INSERT INTO users`` sites and one of them is
deliberately silent, so "it looks like the others" is not a check. The first
test derives the requirement from the module's own AST.

The second exposure is the one that made this a cross-process change at all:
the alert is composed in the **api** container and sent from the **engine**
container, because only the engine holds a live TelegramBot. A test that
patched a bot into the api process would go green over a production no-op.
So nothing here fakes the bot into the wrong process.
"""
from __future__ import annotations

import ast
import time
from pathlib import Path

import pytest

import config
from src.api import lifecycle_events as lc
from src.api.users import UserStore
from src.execution.lifecycle_alert_bridge import LifecycleAlertConsumer, format_event


@pytest.fixture(autouse=True)
def _clean():
    lc.reset_for_tests()
    yield
    lc.reset_for_tests()


# ---------------------------------------------------------------- AST guard
def _functions_touching_user_inserts(tree: ast.AST):
    """Yield (function, inserts_users, calls_emit) for every function whose
    body contains an ``INSERT INTO users`` literal."""
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        src = ast.dump(node)
        inserts = any(
            isinstance(n, ast.Constant)
            and isinstance(n.value, str)
            and "INSERT INTO users" in n.value
            for n in ast.walk(node)
        )
        if not inserts:
            continue
        emits = any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "emit"
            for n in ast.walk(node)
        )
        yield node.name, emits, src


#: The one creation path that must stay silent, with the reason recorded
#: here rather than only in a comment — a silent exemption is how a real
#: miss hides among an intended one.
SILENT_BY_DESIGN = {
    "bootstrap_owner_if_empty": "creates the OPERATOR row on first run, not a customer",
}


def test_every_user_creation_path_announces_or_is_named_silent():
    tree = ast.parse(Path("src/api/users.py").read_text())
    found = list(_functions_touching_user_inserts(tree))
    assert found, "no INSERT INTO users sites found — did users.py move?"
    for name, emits, _ in found:
        if name in SILENT_BY_DESIGN:
            assert not emits, (
                f"{name} is listed as silent by design "
                f"({SILENT_BY_DESIGN[name]}) but now emits — remove it from "
                "SILENT_BY_DESIGN or drop the emit."
            )
            continue
        assert emits, (
            f"{name} inserts a user row and never calls lifecycle_events.emit. "
            "A new signup path that does not announce is invisible: the owner "
            "asked to be told about every new user, and this is how that "
            "silently stops being true."
        )


# ------------------------------------------------------- masking / payload
@pytest.mark.parametrize("raw", ["+919876543210", "919876543210", "+14155550142"])
def test_mask_keeps_country_and_last_two_only(raw):
    masked = lc.mask_phone(raw)
    digits = "".join(c for c in raw if c.isdigit())
    assert masked.endswith(digits[-2:])
    assert masked.startswith("+" + digits[:2])
    # The middle must not survive anywhere in the output.
    assert digits[2:-2] not in masked
    assert digits not in masked


def test_mask_refuses_rather_than_printing_a_stub():
    for bad in (None, "", "12"):
        assert lc.mask_phone(bad) == "unknown"


def test_emit_never_carries_the_full_number():
    lc.emit(lc.EVENT_SIGNUP, user_id=7, phone_e164="+919876543210")
    (row,) = lc.drain()
    assert "9876543210" not in str(row)
    assert row["phone_masked"].endswith("10")
    assert "phone_e164" not in row


def test_unknown_event_is_dropped_at_the_producer():
    lc.emit("something_else", user_id=1)
    assert lc.drain() == []


def test_queue_is_bounded_and_counts_what_it_drops(monkeypatch):
    for i in range(int(config.LIFECYCLE_ALERT_QUEUE_MAX) + 25):
        lc.emit(lc.EVENT_SIGNUP, user_id=i)
    s = lc.stats()
    assert s["queued"] == int(config.LIFECYCLE_ALERT_QUEUE_MAX)
    assert s["dropped"] == 25, "overflow must be counted, or a flood reads as a quiet day"


def test_disabled_flag_emits_nothing(monkeypatch):
    monkeypatch.setattr(config, "LIFECYCLE_ALERTS_ENABLED", False)
    lc.emit(lc.EVENT_SIGNUP, user_id=1)
    assert lc.drain() == []


# ------------------------------------------------- the real store, not a mock
def test_creating_a_user_through_the_real_store_announces(tmp_path):
    store = UserStore(tmp_path / "u.db")
    user = store.get_or_create_by_firebase_uid("uid-abc", "+919876543210")
    rows = lc.drain()
    assert len(rows) == 1
    assert rows[0]["event"] == lc.EVENT_SIGNUP
    assert rows[0]["user_id"] == user.user_id


def test_a_returning_user_does_not_announce_again(tmp_path):
    store = UserStore(tmp_path / "u.db")
    store.get_or_create_by_firebase_uid("uid-abc", "+919876543210")
    lc.drain()
    store.get_or_create_by_firebase_uid("uid-abc", "+919876543210")
    assert lc.drain() == [], "a sign-in is not a signup"


def test_onboarding_announces_the_transition_not_every_edit(tmp_path):
    store = UserStore(tmp_path / "u.db")
    user = store.get_or_create_by_firebase_uid("uid-abc", "+919876543210")
    lc.drain()
    store.update_profile(
        user.user_id, display_name="Asha", accept_terms=True, country_code="IN",
    )
    rows = lc.drain()
    assert [r["event"] for r in rows] == [lc.EVENT_ONBOARDED]
    # Editing the profile again must not re-announce.
    store.update_profile(user.user_id, display_name="Asha K")
    assert lc.drain() == []


# ------------------------------------------------------------- the consumer
class _Bot:
    def __init__(self, ok=True):
        self.sent = []
        self._ok = ok

    async def send_admin_alert(self, text):
        self.sent.append(text)
        return self._ok


def test_consumer_renders_an_unknown_event_badged_not_invented():
    line = format_event({"event": "who_knows", "user_id": 3})
    assert "who_knows" in line and "unclassified" in line


def test_a_late_event_says_it_is_late():
    now = time.time()
    line = format_event({"event": "signup", "ts": now - 3600}, now=now)
    assert "late" in line, (
        "a restart backlog must not read as a burst of signups that just "
        "happened"
    )


async def test_rate_cap_is_spent_per_event_examined_and_overflow_coalesces(monkeypatch):
    monkeypatch.setattr(config, "LIFECYCLE_ALERT_MAX_PER_MIN", 3)
    bot = _Bot()
    c = LifecycleAlertConsumer(redis_client=None, telegram_bot=bot)
    for i in range(10):
        await c._send({"event": "signup", "user_id": i, "ts": time.time()})
    assert len(bot.sent) == 3, "the cap must bound the vendor calls, not the events"
    assert c._suppressed == 7, "suppressed events are counted, never silently dropped"
    await c._flush_suppressed()
    assert "7 more" in bot.sent[-1]


async def test_a_bot_with_no_admin_chat_counts_refused_rather_than_sent():
    bot = _Bot(ok=False)
    c = LifecycleAlertConsumer(redis_client=None, telegram_bot=bot)
    await c._send({"event": "signup", "user_id": 1, "ts": time.time()})
    assert c.sent == 0 and c.refused == 1, (
        "'off' and 'broken' must stay distinguishable"
    )
