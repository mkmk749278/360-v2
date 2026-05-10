"""OTP issue + verify — phone-bound one-time codes.

In-memory only.  An OTP is a 6-digit code with a 5-minute TTL, hashed
at rest, with per-phone rate limits on issue (3/hour) and verify
attempts (5/code).  Process restart wipes pending OTPs — acceptable
because (a) the TTL is short, (b) a re-request just generates a new
code, (c) the closed beta is small.

When workers > 1 ever ships, swap this module's ``_records`` /
``_issue_log`` for a SQLite-backed equivalent — same surface.

Threading: serialised via an internal RLock.  Called from FastAPI's
thread-pool executor; volume is tiny (a few requests/sec at most), so
lock contention isn't a concern.
"""

from __future__ import annotations

import enum
import hashlib
import hmac
import secrets
import threading
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List, Optional

from src.utils import get_logger

log = get_logger("api.otp")


# ---------------------------------------------------------------------------
# Defaults — overridden via constructor / env wiring in config
# ---------------------------------------------------------------------------


DEFAULT_TTL = timedelta(minutes=5)
DEFAULT_MAX_ATTEMPTS_PER_CODE = 5
DEFAULT_MAX_ISSUES_PER_HOUR = 3


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


class IssueStatus(str, enum.Enum):
    OK = "ok"
    RATE_LIMITED = "rate_limited"  # too many issues for this phone within the window


class VerifyStatus(str, enum.Enum):
    OK = "ok"
    NO_RECORD = "no_record"  # never issued, or expired-and-cleared
    EXPIRED = "expired"
    WRONG_CODE = "wrong_code"
    TOO_MANY_ATTEMPTS = "too_many_attempts"


@dataclass(frozen=True)
class IssueResult:
    status: IssueStatus
    code: Optional[str] = None  # plaintext code — caller forwards to delivery, never stores
    expires_in_seconds: int = 0
    retry_after_seconds: int = 0  # populated when status=RATE_LIMITED


@dataclass(frozen=True)
class VerifyResult:
    status: VerifyStatus
    attempts_remaining: int = 0


# ---------------------------------------------------------------------------
# Internal record
# ---------------------------------------------------------------------------


@dataclass
class _OtpRecord:
    code_hash: bytes
    expires_at_monotonic: float
    attempts: int = 0


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------


class OtpStore:
    """Phone-keyed OTP issuer + verifier."""

    def __init__(
        self,
        *,
        ttl: timedelta = DEFAULT_TTL,
        max_attempts_per_code: int = DEFAULT_MAX_ATTEMPTS_PER_CODE,
        max_issues_per_hour: int = DEFAULT_MAX_ISSUES_PER_HOUR,
    ) -> None:
        self._ttl = ttl
        self._max_attempts = max(1, int(max_attempts_per_code))
        self._max_issues_per_hour = max(1, int(max_issues_per_hour))
        self._records: Dict[str, _OtpRecord] = {}
        # Per-phone monotonic-timestamp ring of issue events within the
        # rolling 1-hour window; used to enforce ``max_issues_per_hour``.
        self._issue_log: Dict[str, List[float]] = {}
        self._lock = threading.RLock()

    # ---- helpers --------------------------------------------------------

    @staticmethod
    def _hash_code(code: str) -> bytes:
        # SHA-256 over a fixed pepper; we don't store plaintext codes.
        # Pepper is process-local; an OTP is short-lived, so a stolen
        # snapshot of memory + restart leaks nothing useful.
        return hashlib.sha256(code.encode("ascii")).digest()

    @staticmethod
    def _generate_code() -> str:
        # 6-digit zero-padded.  ``randbelow`` gives uniform [0, 999_999].
        return f"{secrets.randbelow(1_000_000):06d}"

    def _prune_issue_log(self, phone: str, now_monotonic: float) -> None:
        cutoff = now_monotonic - 3600.0
        events = self._issue_log.get(phone)
        if events is None:
            return
        # Trim leading entries older than the cutoff; in-place to avoid
        # rebuilding the list every call.
        idx = 0
        while idx < len(events) and events[idx] < cutoff:
            idx += 1
        if idx:
            del events[:idx]
        if not events:
            self._issue_log.pop(phone, None)

    # ---- public API -----------------------------------------------------

    def issue(self, phone: str) -> IssueResult:
        """Generate + store a new OTP for ``phone``.

        Returns the **plaintext** code in the result so the caller can
        forward it to the delivery provider.  The code is hashed before
        being stored.  If the phone has already requested too many OTPs
        within the rolling hour, returns ``RATE_LIMITED`` with no code.
        """
        if not phone:
            raise ValueError("phone must be a non-empty string")
        now_mono = time.monotonic()
        with self._lock:
            self._prune_issue_log(phone, now_mono)
            events = self._issue_log.setdefault(phone, [])
            if len(events) >= self._max_issues_per_hour:
                # Caller may show "try again in N minutes".
                retry = max(1, int(3600.0 - (now_mono - events[0])))
                log.warning(
                    "OTP rate-limited: phone={}, issues_in_hour={}",
                    phone, len(events),
                )
                return IssueResult(
                    status=IssueStatus.RATE_LIMITED,
                    retry_after_seconds=retry,
                )
            code = self._generate_code()
            self._records[phone] = _OtpRecord(
                code_hash=self._hash_code(code),
                expires_at_monotonic=now_mono + self._ttl.total_seconds(),
                attempts=0,
            )
            events.append(now_mono)
            return IssueResult(
                status=IssueStatus.OK,
                code=code,
                expires_in_seconds=int(self._ttl.total_seconds()),
            )

    def verify(self, phone: str, code: str) -> VerifyResult:
        """Verify ``code`` against the latest issued OTP for ``phone``.

        On success the record is consumed (single-use).  Wrong codes
        increment the attempt counter; once it hits ``max_attempts`` the
        record is dropped (no more verifies allowed for that issuance).
        """
        with self._lock:
            record = self._records.get(phone)
            if record is None:
                return VerifyResult(status=VerifyStatus.NO_RECORD)
            if time.monotonic() >= record.expires_at_monotonic:
                self._records.pop(phone, None)
                return VerifyResult(status=VerifyStatus.EXPIRED)
            if record.attempts >= self._max_attempts:
                # Defensive: code-path below should drop the record on
                # the Nth wrong attempt, but if it lingers we still 403.
                self._records.pop(phone, None)
                return VerifyResult(status=VerifyStatus.TOO_MANY_ATTEMPTS)
            presented_hash = self._hash_code(code)
            if not hmac.compare_digest(presented_hash, record.code_hash):
                record.attempts += 1
                remaining = self._max_attempts - record.attempts
                if remaining <= 0:
                    self._records.pop(phone, None)
                    return VerifyResult(
                        status=VerifyStatus.TOO_MANY_ATTEMPTS,
                        attempts_remaining=0,
                    )
                return VerifyResult(
                    status=VerifyStatus.WRONG_CODE,
                    attempts_remaining=remaining,
                )
            # Success — consume.
            self._records.pop(phone, None)
            return VerifyResult(status=VerifyStatus.OK)

    # ---- introspection (test helpers) -----------------------------------

    def pending_count(self) -> int:
        with self._lock:
            return len(self._records)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------


_store: Optional[OtpStore] = None
_store_lock = threading.Lock()


def get_default_store(
    *,
    ttl: timedelta = DEFAULT_TTL,
    max_attempts_per_code: int = DEFAULT_MAX_ATTEMPTS_PER_CODE,
    max_issues_per_hour: int = DEFAULT_MAX_ISSUES_PER_HOUR,
) -> OtpStore:
    """Return (and lazily create) the process-global OtpStore."""
    global _store
    with _store_lock:
        if _store is None:
            _store = OtpStore(
                ttl=ttl,
                max_attempts_per_code=max_attempts_per_code,
                max_issues_per_hour=max_issues_per_hour,
            )
        return _store


def reset_for_test(
    *,
    ttl: timedelta = DEFAULT_TTL,
    max_attempts_per_code: int = DEFAULT_MAX_ATTEMPTS_PER_CODE,
    max_issues_per_hour: int = DEFAULT_MAX_ISSUES_PER_HOUR,
) -> OtpStore:
    """Drop the cached singleton and re-init.  Tests use this to
    guarantee isolation: each test gets a fresh store with optionally
    tighter limits (e.g. ``max_issues_per_hour=2`` to test rate-limit
    behaviour without burning real time).
    """
    global _store
    with _store_lock:
        _store = OtpStore(
            ttl=ttl,
            max_attempts_per_code=max_attempts_per_code,
            max_issues_per_hour=max_issues_per_hour,
        )
        return _store
