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
# ``.get()`` on every call.  ``/api/auto-trade/runtime-status`` calls it once
# per 10s per polling user purely to answer ``binance_key_connected`` — a
# question about whether the document EXISTS — so an app left open on the Trade
# tab bought ~8,600 reads a day, each one fetching an encrypted secret it threw
# away.
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


def list_active_uids() -> list[str]:
    """Return every firebase_uid that currently has a connected
    Binance key blob.

    Implementation: collection-group query on the ``binance_key``
    subcollection, filtered to documents named ``current`` (our
    naming convention from PR-1).  Returns the parent user's uid
    for each match.

    Cost: one Firestore query per call.  Caller should cache the
    result for a short TTL (~30s) rather than enumerating on every
    signal — there's no need for sub-second freshness here (a
    newly-connected user can wait one cycle for the engine to
    notice them, and disconnection takes effect immediately on
    blob delete via the engine's own action).

    Returns an empty list if the keystore isn't initialised so the
    signal-dispatch path no-ops cleanly in dev contexts that
    haven't booted the full server-side execution stack.
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
        log.warning("list_active_uids failed: {}", exc)
        return []


def delete_key_blob(uid: str) -> None:
    """Remove the user's key blob.

    Used by: user-initiated disconnect, password-reset trigger (the
    3Commas Oct-2023 lesson), permission-drift detector after the
    user's Binance key permissions changed underneath us.

    Idempotent — no error if the document doesn't exist.
    """
    _invalidate_has_key(uid)
    _doc_ref(uid).delete()
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
    global _db
    with _lock:
        _db = None
        _has_key_cache.clear()
