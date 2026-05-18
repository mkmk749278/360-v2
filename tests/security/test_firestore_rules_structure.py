"""Structural tests for ``firestore.rules``.

These tests do NOT use the Firebase Rules Emulator (which would require
Java + the Firebase CLI + an emulator suite — overkill for a solo
project).  Instead they verify the rules file has the EXPECTED
patterns: the deny-all default, the per-collection rules with the
right ``allow`` clauses, and explicit lockdown of the binance_key
subcollection.

What we pin here is the **doctrine** (per OWNER_BRIEF §3.9 + B18):

* Default DENY rule is present.
* ``users/{uid}/binance_key`` is fully locked down to clients —
  even the owning user cannot read or write from the SDK.
* ``kill_switch`` is fully locked down to clients.
* User-readable subcollections (positions, orders, anomalies) have
  ``allow read`` for the matching uid AND ``allow write: if false``
  — engine-write-only.
* User profile root document allows the matching uid to read+write.

A future edit that accidentally widens access (e.g. drops the deny-all
default, or grants client write to binance_key) fails these tests
loudly, NOT silently in production.

The actual rules enforcement happens server-side at Firebase's
infrastructure when a Lumin app SDK tries to read a doc — that's
tested manually + via the Firebase Rules emulator in operator setup
(see ``docs/server-side-execution-setup.md``).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def rules_text() -> str:
    """Load the rules file once per test module."""
    path = Path(__file__).resolve().parents[2] / "firestore.rules"
    return path.read_text()


# ---------------------------------------------------------------------------
# Top-level file structure
# ---------------------------------------------------------------------------


def test_rules_version_is_2(rules_text: str) -> None:
    """Firestore rules version 2 is the modern syntax we rely on
    (recursive ``=**`` wildcards, request.auth shape).  Downgrading
    would silently invalidate the wildcard rules below."""
    assert "rules_version = '2';" in rules_text


def test_service_cloud_firestore_block_present(rules_text: str) -> None:
    assert "service cloud.firestore" in rules_text


# ---------------------------------------------------------------------------
# Deny-all default
# ---------------------------------------------------------------------------


def test_default_deny_all_rule_present(rules_text: str) -> None:
    """The explicit deny-all rule.  Firestore's default IS deny, but
    pinning it in the rules file makes the doctrine readable in one
    place AND catches an accidental edit that removes it."""
    # The pattern: match /{document=**} { allow read, write: if false; }
    pattern = re.compile(
        r"match\s+/\{document=\*\*\}\s*\{\s*allow\s+read,\s*write\s*:\s*if\s+false\s*;\s*\}",
        re.MULTILINE | re.DOTALL,
    )
    assert pattern.search(rules_text), (
        "deny-all default rule missing — every new collection without an "
        "explicit match clause is now silently open"
    )


# ---------------------------------------------------------------------------
# The critical lockdown: binance_key
# ---------------------------------------------------------------------------


def test_binance_key_subcollection_fully_locked_to_clients(rules_text: str) -> None:
    """The most security-critical check.  ``users/{uid}/binance_key/**``
    must deny BOTH read AND write from any client.  Only the engine
    (via Admin SDK, which bypasses rules) may touch this collection.

    A regression that flips this to ``allow read: if request.auth.uid
    == uid`` would let a stolen Firebase ID token exfiltrate the
    encrypted blob + encrypted DEK — combined with a KMS service-
    account compromise that would be the entire breach chain.  This
    test catches that single-line regression."""
    pattern = re.compile(
        r"match\s+/users/\{uid\}/binance_key/\{doc=\*\*\}\s*\{\s*"
        r"allow\s+read,\s*write\s*:\s*if\s+false\s*;\s*\}",
        re.MULTILINE | re.DOTALL,
    )
    assert pattern.search(rules_text), (
        "users/{uid}/binance_key lockdown rule missing or wrong shape — "
        "this is the structural defense for the encrypted-key blob store"
    )


def test_binance_key_rule_does_not_use_request_auth(rules_text: str) -> None:
    """Defense-in-depth: the binance_key rule must not even MENTION
    ``request.auth`` — any rule that gates on auth state, even if it
    currently evaluates to false, is one typo away from granting
    access.  Locking with ``if false`` is structural.

    We scan the binance_key match block specifically and assert it
    contains no ``request.auth`` reference."""
    # Extract the binance_key match block (between its opening { and
    # matching closing }).
    m = re.search(
        r"match\s+/users/\{uid\}/binance_key/\{doc=\*\*\}\s*\{([^}]*)\}",
        rules_text,
        re.DOTALL,
    )
    assert m is not None, "binance_key match block missing"
    block = m.group(1)
    assert "request.auth" not in block, (
        "binance_key rule contains request.auth reference — "
        "a one-line typo could grant access; use 'if false' instead"
    )


# ---------------------------------------------------------------------------
# Kill switch — same total lockdown
# ---------------------------------------------------------------------------


def test_kill_switch_locked_to_clients(rules_text: str) -> None:
    """Global kill_switch doc is engine-only.  Clients cannot read
    (knowing engine state) or write (which would be the worst possible
    privilege escalation).  Operator flips via Telegram bot."""
    pattern = re.compile(
        r"match\s+/kill_switch/\{doc=\*\*\}\s*\{\s*"
        r"allow\s+read,\s*write\s*:\s*if\s+false\s*;\s*\}",
        re.MULTILINE | re.DOTALL,
    )
    assert pattern.search(rules_text), "kill_switch lockdown missing"


# ---------------------------------------------------------------------------
# User-readable subcollections — read by owner, write by engine
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "collection",
    ["positions", "orders", "anomalies"],
)
def test_per_user_subcollection_is_owner_read_engine_write(
    rules_text: str, collection: str
) -> None:
    """positions / orders / anomalies subcollections share a contract:
    the owning user can READ (so the app can show open positions,
    order history, tripwire history), but ALL writes come from the
    engine via Admin SDK (clients cannot tamper with their own
    history)."""
    pattern = re.compile(
        rf"match\s+/users/\{{uid\}}/{collection}/\{{[^}}]+\}}\s*\{{\s*"
        r"allow\s+read\s*:\s*if\s+request\.auth\s*!=\s*null\s*&&\s*"
        r"request\.auth\.uid\s*==\s*uid\s*;\s*"
        r"allow\s+write\s*:\s*if\s+false\s*;\s*\}",
        re.MULTILINE | re.DOTALL,
    )
    assert pattern.search(rules_text), (
        f"users/{{uid}}/{collection} rule missing or wrong — "
        f"expected owner-read + engine-write-only"
    )


# ---------------------------------------------------------------------------
# User profile root — owner read+write
# ---------------------------------------------------------------------------


def test_user_profile_doc_allows_owner_read_and_write(rules_text: str) -> None:
    """The root /users/{uid} document carries non-secret profile data
    that the user controls (display name, prefs, ToS acceptance).
    Owner can read+write; other users see nothing."""
    # ``match /users/{uid} {`` (note trailing space + brace).  Use a
    # negative-lookahead on ``/`` after ``{uid}`` so we don't match the
    # nested subcollection rules (``/users/{uid}/binance_key/...``).
    pattern = re.compile(
        r"match\s+/users/\{uid\}(?!/)\s*\{\s*"
        r"allow\s+read,\s*write\s*:\s*if\s+request\.auth\s*!=\s*null\s*&&\s*"
        r"request\.auth\.uid\s*==\s*uid\s*;\s*\}",
        re.MULTILINE | re.DOTALL,
    )
    assert pattern.search(rules_text), (
        "users/{uid} root-doc rule missing or wrong"
    )


# ---------------------------------------------------------------------------
# Sanity: the rules file is syntactically plausible
# ---------------------------------------------------------------------------


def test_braces_are_balanced(rules_text: str) -> None:
    """Trivial syntactic sanity check.  A typo that drops a closing
    brace would silently turn a deny rule into an allow rule depending
    on parser behaviour; better to fail the test loudly."""
    opens = rules_text.count("{")
    closes = rules_text.count("}")
    assert opens == closes, (
        f"unbalanced braces in firestore.rules: {opens} open, {closes} close"
    )
