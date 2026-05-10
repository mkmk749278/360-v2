"""OtpStore tests — issue + verify with rate limiting."""
from __future__ import annotations

import time
from datetime import timedelta

import pytest

from src.api.otp import (
    DEFAULT_TTL,
    IssueStatus,
    OtpStore,
    VerifyStatus,
)


@pytest.fixture
def store() -> OtpStore:
    # Tight limits so rate-limit + attempt-cap behaviours can be tested
    # without burning real time.
    return OtpStore(
        ttl=DEFAULT_TTL,
        max_attempts_per_code=3,
        max_issues_per_hour=2,
    )


# ---------------------------------------------------------------------------
# issue()
# ---------------------------------------------------------------------------


def test_issue_returns_six_digit_code(store: OtpStore) -> None:
    result = store.issue("+15551110000")
    assert result.status is IssueStatus.OK
    assert result.code is not None
    assert len(result.code) == 6
    assert result.code.isdigit()
    assert result.expires_in_seconds == int(DEFAULT_TTL.total_seconds())


def test_issue_replaces_existing_code(store: OtpStore) -> None:
    a = store.issue("+15551110000")
    b = store.issue("+15551110000")
    assert a.code != b.code  # extremely high probability with secrets.randbelow
    # Old code should no longer verify.
    assert store.verify("+15551110000", a.code).status is VerifyStatus.WRONG_CODE


def test_issue_rate_limited_after_max_per_hour(store: OtpStore) -> None:
    store.issue("+15551110000")
    store.issue("+15551110000")
    blocked = store.issue("+15551110000")
    assert blocked.status is IssueStatus.RATE_LIMITED
    assert blocked.code is None
    assert blocked.retry_after_seconds > 0


def test_issue_rate_limit_independent_per_phone(store: OtpStore) -> None:
    store.issue("+15551110000")
    store.issue("+15551110000")
    # Different phone — should still get a code.
    other = store.issue("+15551110001")
    assert other.status is IssueStatus.OK
    assert other.code is not None


# ---------------------------------------------------------------------------
# verify()
# ---------------------------------------------------------------------------


def test_verify_success_consumes_record(store: OtpStore) -> None:
    issued = store.issue("+15551110000")
    ok = store.verify("+15551110000", issued.code)
    assert ok.status is VerifyStatus.OK
    # Single-use: re-verifying the same code returns NO_RECORD.
    again = store.verify("+15551110000", issued.code)
    assert again.status is VerifyStatus.NO_RECORD


def test_verify_no_record_for_unknown_phone(store: OtpStore) -> None:
    res = store.verify("+15559999999", "123456")
    assert res.status is VerifyStatus.NO_RECORD


def test_verify_wrong_code_decrements_attempts(store: OtpStore) -> None:
    issued = store.issue("+15551110000")
    bad = store.verify("+15551110000", "000000" if issued.code != "000000" else "999999")
    assert bad.status is VerifyStatus.WRONG_CODE
    assert bad.attempts_remaining == 2  # max_attempts=3, used 1


def test_verify_too_many_attempts_drops_record(store: OtpStore) -> None:
    issued = store.issue("+15551110000")
    wrong = "000000" if issued.code != "000000" else "999999"
    a = store.verify("+15551110000", wrong)
    b = store.verify("+15551110000", wrong)
    c = store.verify("+15551110000", wrong)
    assert a.status is VerifyStatus.WRONG_CODE
    assert b.status is VerifyStatus.WRONG_CODE
    # Third wrong attempt drops the record entirely.
    assert c.status is VerifyStatus.TOO_MANY_ATTEMPTS
    # Even the correct code can't be redeemed any more.
    after = store.verify("+15551110000", issued.code)
    assert after.status is VerifyStatus.NO_RECORD


def test_verify_expired_code_returns_expired() -> None:
    # Custom store with sub-second TTL so we can deterministically expire.
    s = OtpStore(
        ttl=timedelta(milliseconds=50),
        max_attempts_per_code=3,
        max_issues_per_hour=10,
    )
    issued = s.issue("+15551110000")
    time.sleep(0.1)
    res = s.verify("+15551110000", issued.code)
    assert res.status is VerifyStatus.EXPIRED


# ---------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------


def test_pending_count_tracks_records(store: OtpStore) -> None:
    assert store.pending_count() == 0
    store.issue("+15551110000")
    store.issue("+15551110001")
    assert store.pending_count() == 2
    issued = store.issue("+15551110000")  # same phone — replaces
    assert store.pending_count() == 2
    store.verify("+15551110000", issued.code)
    assert store.pending_count() == 1


def test_issue_rejects_empty_phone(store: OtpStore) -> None:
    with pytest.raises(ValueError):
        store.issue("")
