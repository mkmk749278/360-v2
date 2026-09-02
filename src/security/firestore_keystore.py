"""Firestore-backed per-user encrypted-key blob store.

Stores the **encrypted** Binance API secret + the **encrypted** DEK
for each user, in the ``users/{uid}/binance_key/current`` document
shape per ``OWNER_BRIEF §3.9``.

This module owns the schema (field names, base64 encoding, timestamps)
but **never** reads or writes plaintext.  All encryption / decryption
happens in :mod:`src.security.envelope_crypto` +
:mod:`src.security.kms_client`; this layer is a typed CRUD adapter.

Document shape (Firestore ``users/{uid}/binance_key/current``):

    {
      "encrypted_secret_b64": str,   # base64(EncryptedBlob.raw)
      "encrypted_dek_b64": str,      # base64(KMS-wrapped DEK)
      "api_key_full": str,           # full Binance API key (PUBLIC —
                                     # not secret; needed by signing
                                     # service for X-MBX-APIKEY header)
      "key_public_id_first8": str,   # first 8 chars of the Binance key
                                     # — used in admin/diagnostics + app UI
      "ip_whitelist_ok": bool,       # validated at connect time
      "withdraw_disabled_ok": bool,  # validated at connect time
      "connected_at": Timestamp,
      "last_validated_at": Timestamp,
    }

Firestore Security Rules (configured separately in ``firestore.rules``
when the connect flow lands in PR-3) must deny client reads/writes
to this subcollection — only the engine's Firebase Admin SDK service
account may touch it.  That rule pinning is the structural defence
that makes a stolen client ID-token useless for key exfiltration.

This module is intentionally **CRUD-only** scaffolding.  Validation
of withdraw / IP-whitelist / Futures-enable status happens in
``src/security/binance_connect_validator.py`` (PR-2).  Provisioning
of new keys (DEK generation, AES-GCM encryption, KMS-wrapping)
happens in the connect flow handler (PR-2).
"""

from __future__ import annotations

import base64
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from src import firestore_reads as _reads
from src.utils import get_logger

log = get_logger("security.firestore_keystore")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class FirestoreKeystoreError(Exception):
    """Base class for keystore errors surfaced to callers."""


class FirestoreKeystoreNotInitialisedError(FirestoreKeystoreError):
    """Read/write attempted before :func:`init_keystore` succeeded."""


class KeyBlobNotFoundError(FirestoreKeystoreError):
    """The requested user has no Binance key blob on file."""


# ---------------------------------------------------------------------------
# Document model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UserKeyBlob:
    """In-memory projection of the Firestore key document.

    ``encrypted_secret`` and ``encrypted_dek`` are the raw bytes
    (already base64-decoded from the wire format).  Callers feed
    these directly into
    :func:`src.security.envelope_crypto.decrypt_secret` +
    :meth:`src.security.kms_client.KmsClient.decrypt`.
    """

    uid: str
    encrypted_secret: bytes
    encrypted_dek: bytes
    api_key_full: str
    key_public_id_first8: str
    ip_whitelist_ok: bool
    withdraw_disabled_ok: bool
    connected_at: datetime
    last_validated_at: datetime


# ---------------------------------------------------------------------------
# Module-level singleton + init
# ---------------------------------------------------------------------------


_lock = threading.RLock()
_db: Any = None  # google.cloud.firestore.Client once initialised


def init_keystore(service_account_path: Optional[str] = None) -> None:
    """Initialise the Firestore Admin SDK client.

    Idempotent.  Lazy-imports ``google.cloud.firestore`` to avoid
    paying the grpc/protobuf cost on installs that don't use
    server-side execution.

    ``service_account_path`` is optional; when omitted the client
    falls back to ADC.  In production the engine shares one
    service-account JSON across Firebase Admin + KMS + Firestore.
    """
    global _db
    with _lock:
        if _db is not None:
            log.info("Firestore keystore already initialised")
            return
        from google.cloud import firestore  # type: ignore[import-not-found]
        from google.oauth2 import service_account  # type: ignore[import-not-found]

        if service_account_path:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path
            )
            _db = firestore.Client(credentials=credentials)
        else:
            _db = firestore.Client()
        log.info(
            "Firestore keystore initialised: service_account={}",
            service_account_path or "ADC",
        )
    # Cross-process invalidation for the roster.  Registered outside the lock
    # because ``control_generation`` takes its own.
    try:
        from src import control_generation as _gen

        _gen.register(_gen.DOC_ACTIVE_UIDS, invalidate_roster)
    except Exception:  # pragma: no cover - defensive
        log.exception(
            "keystore: could not register roster generation listener — a "
            "connect in the other container converges on the defensive TTL"
        )


def is_initialised() -> bool:
    """Return True iff :func:`init_keystore` has been called successfully."""
    with _lock:
        return _db is not None


def _doc_ref(uid: str) -> Any:
    """Resolve the Firestore document ref for the user's key blob.

    Path: ``users/{uid}/binance_key/current``.  ``current`` is a
    fixed document name (not auto-id) so each user has at most one
    active key at a time; rotation REPLACES this document and the
    old version is dropped (no history retained).
    """
    with _lock:
        if _db is None:
            raise FirestoreKeystoreNotInitialisedError(
                "Firestore keystore not initialised — call init_keystore at boot"
            )
        return (
            _db.collection("users")
            .document(uid)
            .collection("binance_key")
            .document("current")
        )


# ---------------------------------------------------------------------------
# CRUD — all callers operate on already-encrypted bytes; this module
# never sees plaintext secrets.
# ---------------------------------------------------------------------------


def put_key_blob(
    uid: str,
    *,
    encrypted_secret: bytes,
    encrypted_dek: bytes,
    api_key_full: str,
    ip_whitelist_ok: bool,
    withdraw_disabled_ok: bool,
) -> None:
    """Insert or replace the user's encrypted key blob.

    Overwrites any prior key.  Used at first-connect AND at user-
    initiated key rotation.  ``connected_at`` is set to now;
    ``last_validated_at`` likewise (the caller has just validated
    the key with Binance via the connect flow).

    ``api_key_full`` is the user's Binance API key — the PUBLIC half
    of the pair (not secret).  Stored plaintext because the signing
    service needs it for the ``X-MBX-APIKEY`` header on every signed
    request and there's no security benefit to encrypting a public
    value.  ``key_public_id_first8`` is derived from this for the
    app's at-a-glance display.

    Callers are responsible for: encrypting the secret + KMS-
    wrapping the DEK BEFORE calling this function.  This module
    never sees plaintext secret material.
    """
    now = datetime.now(timezone.utc)
    _doc_ref(uid).set(
        {
            "encrypted_secret_b64": base64.b64encode(encrypted_secret).decode("ascii"),
            "encrypted_dek_b64": base64.b64encode(encrypted_dek).decode("ascii"),
            "api_key_full": api_key_full,
            "key_public_id_first8": api_key_full[:8],
            "ip_whitelist_ok": ip_whitelist_ok,
            "withdraw_disabled_ok": withdraw_disabled_ok,
            "connected_at": now,
            "last_validated_at": now,
        }
    )
    _invalidate_has_key(uid)
    _roster_apply(uid, present=True)
    log.info(
        "Stored encrypted Binance key blob: uid={}, key_id_prefix={}",
        uid,
        api_key_full[:8],
    )


# ---------------------------------------------------------------------------
# Key-presence cache (2026-09-02)
# ---------------------------------------------------------------------------
#
# ``CLAUDE.md``'s Cost Discipline section said "the keystore ... reads are
# already cached (30s)".  That was never true of this module: the 30s belongs
# to ``signal_dispatch._ACTIVE_UIDS_TTL_S``, and ``get_key_blob`` was a bare
# ``.get()`` on every call.  ``/api/auto-trade/runtime-status`` called it purely
# to answer ``binance_key_connected`` — a question about whether the document
# EXISTS — fetching an encrypted secret it then threw away.
#
# The figure first written here, "~8,600 reads a day from one open Trade tab",
# was INFERRED from an assumed 10s poll and is wrong: ``grep -rn Timer.periodic
# lib/`` in ``lumin-app`` returns no runtime-status poll at all — the Trade tab
# fetches on open and on pull-to-refresh behind a 60s SWR cache.  The cut is
# still right (an existence check must not fetch a secret) but the number
# attached to it was a story, and this repo already carries the rule that
# reading code produces a hypothesis about behaviour, never a measurement of
# it.  What these reads actually cost is counted per call site now.
#
# So the presence answer is cached and the blob is not.  Caching the blob would
# hold key material in memory for a TTL to save reads on a path that runs a few
# times a day; caching a boolean costs nothing and removes the whole poll.  The
# order path keeps calling ``get_key_blob`` and keeps reading through.
#
# Every writer invalidates, so a connect or disconnect is visible immediately
# rather than after a TTL — a user who has just linked a key must not be told
# for another minute that they have not.

_HAS_KEY_TTL_S: float = 60.0
_has_key_cache: dict[str, tuple[bool, float]] = {}


def _set_has_key(uid: str, present: bool) -> None:
    """Record what a real read just proved about *uid*'s key document."""
    with _lock:
        _has_key_cache[uid] = (bool(present), time.monotonic())


def _invalidate_has_key(uid: str) -> None:
    """Drop the cached presence answer — called by every writer."""
    with _lock:
        _has_key_cache.pop(uid, None)


def has_key(uid: str) -> bool:
    """True iff *uid* has a connected Binance key document.

    The cheap question behind ``binance_key_connected``.  Cached for
    :data:`_HAS_KEY_TTL_S`; invalidated by every writer, so the TTL bounds only
    how long a change made OUTSIDE this process stays unseen.

    Raises :class:`FirestoreKeystoreNotInitialisedError` if the keystore is not
    wired, rather than answering False — "we could not ask" and "the user has
    no key" are different facts, and today the app told a subscriber whose key
    IS connected to go and connect one because they were rendered the same.
    """
    with _lock:
        if _db is None:
            raise FirestoreKeystoreNotInitialisedError(
                "Firestore keystore not initialised — call init_keystore at boot"
            )
        cached = _has_key_cache.get(uid)
        if cached is not None and (time.monotonic() - cached[1]) < _HAS_KEY_TTL_S:
            return cached[0]
    present = bool(_doc_ref(uid).get().exists)
    _reads.record("keystore.has_key", 1)
    _set_has_key(uid, present)
    return present


def get_key_blob(uid: str) -> UserKeyBlob:
    """Load the user's encrypted key blob.

    Raises :class:`KeyBlobNotFoundError` if the user has not yet
    connected a Binance key.  Callers feed the returned encrypted
    bytes into the KMS + envelope-decrypt chain in the signing
    service — never log or surface the encrypted bytes outside that
    flow.
    """
    snap = _doc_ref(uid).get()
    _reads.record("keystore.get_key_blob", 1)
    if not snap.exists:
        _set_has_key(uid, False)
        raise KeyBlobNotFoundError(f"no key blob for uid={uid}")
    _set_has_key(uid, True)
    data = snap.to_dict() or {}
    return UserKeyBlob(
        uid=uid,
        encrypted_secret=base64.b64decode(data["encrypted_secret_b64"]),
        encrypted_dek=base64.b64decode(data["encrypted_dek_b64"]),
        api_key_full=str(data.get("api_key_full", "")),
        key_public_id_first8=data.get("key_public_id_first8", ""),
        ip_whitelist_ok=bool(data.get("ip_whitelist_ok", False)),
        withdraw_disabled_ok=bool(data.get("withdraw_disabled_ok", False)),
        connected_at=data["connected_at"],
        last_validated_at=data["last_validated_at"],
    )


# ---------------------------------------------------------------------------
# The active-key roster (2026-09-02) — the read that grew with subscribers
# ---------------------------------------------------------------------------
#
# ``list_active_uids`` is a ``collection_group`` scan, and Firestore bills per
# DOCUMENT RETURNED: at the 1,000-member auto-trade target one call costs 1,000
# reads.  ``worker_manager._tick`` called it uncached every 60 seconds — 1,440
# calls a day — so that one loop alone projects to **1.44 million reads a day
# at 1,000 users**, roughly thirty times the entire free-tier allowance, for a
# roster that changes only when somebody connects or disconnects a key.
#
# So the answer is maintained on ONE document instead of recomputed by scanning
# every user.  The blobs stay the record of record; this is an index over them,
# amended by the same two functions that write a blob and rebuilt from a real
# scan at boot and on a slow timer, so it cannot drift indefinitely.
#
# **The failure direction is the whole design.**  An empty roster means every
# signal fans out to zero users — the 2026-09-02 blackout signature exactly —
# so "the index does not exist" and "the index says nobody" must never be the
# same answer.  A missing document, or one whose list field is absent or is not
# a list, falls back to the scan it replaced and repairs itself on the way
# past.  Absence of knowledge is not permission.

_ROSTER_DOC = ("control", "active_uids")
_ROSTER_FIELD = "uids"


def _roster_ttl_from_env() -> float:
    """Defensive TTL for the roster cache.  Cross-process freshness arrives on
    the generation signal; this only bounds a dropped bump."""
    raw = os.environ.get("KEYSTORE_ROSTER_CACHE_TTL_SEC", "").strip()
    if not raw:
        return 300.0
    try:
        return max(float(raw), 5.0)
    except (TypeError, ValueError):
        return 300.0


_ROSTER_TTL_S = _roster_ttl_from_env()
#: ``(uids, read_at_monotonic)`` or ``None``.  A ``uids`` of ``None`` means the
#: roster document was absent or unusable — never that the roster is empty.
_roster_cache: Optional[tuple] = None


def invalidate_roster() -> None:
    """Drop the cached roster — the generation listener's entry point."""
    global _roster_cache
    with _lock:
        _roster_cache = None


def _read_roster() -> Optional[list]:
    """One document read.  ``None`` = no usable index, fall back to the scan."""
    global _roster_cache
    with _lock:
        cached = _roster_cache
        if cached is not None and (time.monotonic() - cached[1]) < _ROSTER_TTL_S:
            return cached[0]
        db = _db
    if db is None:
        return None
    try:
        snap = db.collection(_ROSTER_DOC[0]).document(_ROSTER_DOC[1]).get()
        _reads.record("keystore.roster_doc", 1)
        raw = (snap.to_dict() or {}).get(_ROSTER_FIELD) if snap.exists else None
        uids = [str(u) for u in raw] if isinstance(raw, list) else None
    except Exception as exc:
        log.warning("keystore: roster read failed ({}) — falling back to scan", exc)
        return None
    with _lock:
        _roster_cache = (uids, time.monotonic())
    return uids


def _write_roster(uids) -> None:
    """Persist the index and tell the other container that it moved."""
    global _roster_cache
    with _lock:
        db = _db
    if db is None:
        return
    ordered = sorted({str(u) for u in uids})
    try:
        db.collection(_ROSTER_DOC[0]).document(_ROSTER_DOC[1]).set(
            {_ROSTER_FIELD: ordered, "updated_at": datetime.now(timezone.utc)},
            merge=True,
        )
    except Exception:
        log.exception("keystore: roster write failed — readers stay on the scan")
        return
    with _lock:
        _roster_cache = (ordered, time.monotonic())
    try:
        from src import control_generation as _gen

        _gen.bump(_gen.DOC_ACTIVE_UIDS)
    except Exception:  # pragma: no cover - never break a key write
        log.exception("keystore: roster generation bump failed")


def _roster_apply(uid: str, *, present: bool) -> None:
    """Add or remove one uid without a scan.

    A roster we could not read is left alone rather than rewritten from a
    guess: amending an index we failed to load would replace a full roster
    with a one-element one and take every other subscriber off the fan-out.
    """
    current = _read_roster()
    if current is None:
        return
    amended = set(current)
    if present:
        amended.add(uid)
    else:
        amended.discard(uid)
    if amended != set(current):
        _write_roster(amended)


def rebuild_active_roster() -> int:
    """Rebuild ``control/active_uids`` from a real scan and persist it.

    Costs one ``collection_group`` scan — the expensive call, now run at boot
    and on a slow timer instead of once a minute.  Returns the roster size.
    """
    uids = _scan_active_uids()
    _write_roster(uids)
    return len(uids)


def _scan_active_uids() -> list[str]:
    """The original ``collection_group`` enumeration.

    One Firestore read per document RETURNED, which is why this must never sit
    on a loop.  Kept as the roster's source of truth and its fallback.
    """
    with _lock:
        if _db is None:
            return []
        db = _db
    try:

        query = db.collection_group("binance_key")
        uids: list[str] = []
        _query_docs = 0
        for snap in query.stream():
            _query_docs += 1
            # snap.id is the doc id within binance_key; only
            # 'current' is our convention.  snap.reference.parent.parent
            # is the user document.
            if snap.id != "current":
                continue
            user_ref = snap.reference.parent.parent
            if user_ref is None:
                continue
            uids.append(user_ref.id)
        _reads.record("keystore.list_active_uids", max(_query_docs, 1))
        return uids
    except Exception as exc:
        log.warning("list_active_uids scan failed: {}", exc)
        return []


def list_active_uids() -> list[str]:
    """Return every firebase_uid that currently has a connected Binance key.

    Answered from the one-document roster — a single read whatever the
    subscriber count — falling back to the ``collection_group`` scan when that
    index has never been written, and repairing it on the way past.

    Returns an empty list if the keystore isn't initialised so the
    signal-dispatch path no-ops cleanly in dev contexts that haven't booted the
    full server-side execution stack.  Callers still cache: this is a Firestore
    read, cheap rather than free, and ``signal_dispatch`` keeps its 30s TTL.
    """
    with _lock:
        if _db is None:
            return []
    roster = _read_roster()
    if roster is not None:
        return list(roster)
    uids = _scan_active_uids()
    # Self-healing: the first boot after this shipped has no index, so the
    # first caller pays for one scan and every caller after it does not.
    # Writing an EMPTY roster from a scan that returned nothing is deliberate —
    # that is a real answer about a project with no connected keys, and the
    # fallback above is what keeps it distinct from an index nobody wrote.
    _write_roster(uids)
    return uids


def delete_key_blob(uid: str) -> None:
    """Remove the user's key blob.

    Used by: user-initiated disconnect, password-reset trigger (the
    3Commas Oct-2023 lesson), permission-drift detector after the
    user's Binance key permissions changed underneath us.

    Idempotent — no error if the document doesn't exist.
    """
    _invalidate_has_key(uid)
    _doc_ref(uid).delete()
    # Amend the roster AFTER the delete lands.  A crash between the two leaves
    # a uid on the roster whose blob is gone, which dispatch already handles
    # (the per-user path finds no key and skips); the opposite ordering would
    # drop a user who still has one, which is a silent loss of service.
    _roster_apply(uid, present=False)
    log.info("Deleted encrypted Binance key blob: uid={}", uid)


def update_last_validated(uid: str) -> None:
    """Bump ``last_validated_at`` after a periodic permissions re-check.

    Cheap, common operation — used by the nightly drift detector to
    record "we re-checked this key's Binance permissions and they're
    still compliant" without rewriting the encrypted blob fields.
    """
    _doc_ref(uid).update({"last_validated_at": datetime.now(timezone.utc)})


def reset_for_test() -> None:
    """Test-only: drop the singleton so the next test starts uninitialised."""
    global _db, _roster_cache
    with _lock:
        _db = None
        _has_key_cache.clear()
        _roster_cache = None
