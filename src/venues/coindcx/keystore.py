"""Encrypted CoinDCX key storage — the same custody as a Binance key.

Document: ``users/{uid}/coindcx_key/current``.  The secret is stored exactly
as a Binance secret is (OWNER_BRIEF B18): AES-GCM-encrypted under a per-user
DEK, the DEK wrapped by Cloud KMS, plaintext existing only inside the signing
service for one request.  This module never sees plaintext.

**What B18 cannot check on CoinDCX, and what replaces it.**  Binance reports a
key's permissions and IP restriction, so the engine *proves* withdraw is off
and our IP is bound.  CoinDCX exposes neither.  The owner's decision
(2026-09-27) is an explicit, versioned **attestation**: the user confirms they
bound the key to our server IP and that it cannot withdraw, the connect call
proves the key works from our server, and the document records what was
attested, when, and against which IP.  ``attestation`` is stored on the key
document so it can never be separated from the key it describes, and a key
without one is refused by the signing service.

Costs (the 1,000-member rule):

* **Roster** — one index document ``control/coindcx_active_uids`` answers
  "who has a CoinDCX key" in one read whatever the member count.  Cached, and
  invalidated across containers by ``control_generation.DOC_COINDCX_ACTIVE_UIDS``.
  An **absent** roster document means no key was ever stored (a connect writes
  it or fails), so it reads as empty; an **unreadable** one reads as ``None``
  and callers fan out to nobody rather than to a guess.
* **Blob** — the ciphertext is cached per uid against the Redis generation
  ``DOC_COINDCX_KEY_BLOBS``, exactly as the Binance blob cache is; when the
  generation cannot be read the cache is bypassed.
"""

from __future__ import annotations

import base64
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from src import firestore_reads as _reads
from src.utils import get_logger

log = get_logger("venues.coindcx.keystore")

_COLLECTION = "coindcx_key"
_DOC_ID = "current"
_ROSTER_DOC = ("control", "coindcx_active_uids")
_ROSTER_FIELD = "uids"

#: Bumped when the attestation wording changes, so a key attested under older
#: words can be asked to re-attest instead of being silently accepted.
ATTESTATION_VERSION = 1


class CoinDCXKeystoreError(Exception):
    """Base class."""


class CoinDCXKeystoreNotInitialisedError(CoinDCXKeystoreError):
    """The shared Firestore client has not been initialised."""


class CoinDCXKeyNotFoundError(CoinDCXKeystoreError):
    """The user has no CoinDCX key on file."""


@dataclass(frozen=True)
class CoinDCXKeyBlob:
    uid: str
    encrypted_secret: bytes
    encrypted_dek: bytes
    api_key_full: str
    key_public_id_first8: str
    attestation: dict = field(default_factory=dict)
    connected_at: Optional[datetime] = None
    last_validated_at: Optional[datetime] = None

    @property
    def attested(self) -> bool:
        """Both halves attested under a known wording version."""
        a = self.attestation or {}
        return (
            bool(a.get("ip_bound"))
            and bool(a.get("no_withdraw"))
            and int(a.get("version") or 0) >= 1
        )


_lock = threading.RLock()
_db_override: Any = None  # tests


def _db() -> Any:
    if _db_override is not None:
        return _db_override
    from src.security import firestore_keystore as _fk

    return _fk.firestore_client()


def is_initialised() -> bool:
    return _db() is not None


def _doc_ref(uid: str) -> Any:
    db = _db()
    if db is None:
        raise CoinDCXKeystoreNotInitialisedError("Firestore client not initialised")
    return db.collection("users").document(uid).collection(_COLLECTION).document(_DOC_ID)


# ---------------------------------------------------------------------------
# Write / delete
# ---------------------------------------------------------------------------


def put_key_blob(
    uid: str,
    *,
    encrypted_secret: bytes,
    encrypted_dek: bytes,
    api_key_full: str,
    attestation: dict,
) -> None:
    """Store (or replace) the user's encrypted CoinDCX key, then list the uid
    on the roster.  If the roster write fails the key document is removed and
    the error re-raised: a stored key that dispatch can never see would read
    as "connected" in the app while nothing trades."""
    now = datetime.now(timezone.utc)
    ref = _doc_ref(uid)
    ref.set(
        {
            "encrypted_secret_b64": base64.b64encode(encrypted_secret).decode("ascii"),
            "encrypted_dek_b64": base64.b64encode(encrypted_dek).decode("ascii"),
            "api_key_full": api_key_full,
            "key_public_id_first8": api_key_full[:8],
            "attestation": dict(attestation),
            "connected_at": now,
            "last_validated_at": now,
        }
    )
    _bump_blobs(uid)
    try:
        _roster_apply(uid, present=True)
    except Exception:
        try:
            ref.delete()
            _bump_blobs(uid)
        finally:
            _invalidate_has_key(uid)
        raise
    _set_has_key(uid, True)
    log.info("coindcx keystore: stored key uid={} key_id_prefix={}", uid, api_key_full[:8])


def delete_key_blob(uid: str) -> None:
    """Remove the key, then drop the uid from the roster (idempotent)."""
    _doc_ref(uid).delete()
    _bump_blobs(uid)
    _set_has_key(uid, False)
    try:
        _roster_apply(uid, present=False)
    except Exception:
        # A uid left on the roster with no key is skipped by dispatch (no blob
        # → the signing service answers KEY_BLOB_NOT_FOUND); counted, not raised.
        _fail_open("coindcx.keystore.roster_remove")
    log.info("coindcx keystore: deleted key uid={}", uid)


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------


def get_key_blob(uid: str) -> CoinDCXKeyBlob:
    snap = _doc_ref(uid).get()
    _reads.record("coindcx.keystore.get_key_blob", 1)
    if not snap.exists:
        _set_has_key(uid, False)
        raise CoinDCXKeyNotFoundError(f"no coindcx key for uid={uid}")
    _set_has_key(uid, True)
    data = snap.to_dict() or {}
    return CoinDCXKeyBlob(
        uid=uid,
        encrypted_secret=base64.b64decode(data["encrypted_secret_b64"]),
        encrypted_dek=base64.b64decode(data["encrypted_dek_b64"]),
        api_key_full=str(data.get("api_key_full", "")),
        key_public_id_first8=str(data.get("key_public_id_first8", "")),
        attestation=dict(data.get("attestation") or {}),
        connected_at=data.get("connected_at"),
        last_validated_at=data.get("last_validated_at"),
    )


def get_status(uid: str) -> Optional[dict]:
    """Public, non-secret view of the key for the app, or ``None``."""
    try:
        blob = get_key_blob(uid)
    except CoinDCXKeyNotFoundError:
        return None
    return {
        "key_public_id_first8": blob.key_public_id_first8,
        "attested": blob.attested,
        "attestation": {
            k: blob.attestation.get(k)
            for k in ("ip_bound", "no_withdraw", "version", "engine_ip", "attested_at")
        },
        "connected_at": blob.connected_at,
        "last_validated_at": blob.last_validated_at,
    }


def _blob_ttl() -> float:
    raw = os.environ.get("COINDCX_KEY_BLOB_CACHE_TTL_SEC", "").strip()
    try:
        return max(0.0, float(raw)) if raw else 3600.0
    except (TypeError, ValueError):
        return 3600.0


_blob_cache: dict[str, tuple] = {}  # uid -> (blob, generation, read_at)
_blob_stats = {"hits": 0, "misses": 0, "bypassed": 0}


def get_key_blob_cached(uid: str) -> CoinDCXKeyBlob:
    """:func:`get_key_blob`, from the ciphertext cache when provably fresh."""
    ttl = _blob_ttl()
    if ttl <= 0:
        return get_key_blob(uid)
    gen = _generation(_gen_doc_blobs())
    if gen is None:
        with _lock:
            _blob_stats["bypassed"] += 1
        return get_key_blob(uid)
    now = time.monotonic()
    with _lock:
        hit = _blob_cache.get(uid)
        if hit is not None and hit[1] == gen and (now - hit[2]) < ttl:
            _blob_stats["hits"] += 1
            return hit[0]
        _blob_stats["misses"] += 1
    blob = get_key_blob(uid)
    with _lock:
        _blob_cache[uid] = (blob, gen, now)
    return blob


def invalidate_key_blob(uid: Optional[str] = None) -> None:
    with _lock:
        if uid is None:
            _blob_cache.clear()
        else:
            _blob_cache.pop(uid, None)


# -- has_key: the cheap question the app's status card asks ------------------

_has_key_cache: dict[str, tuple] = {}  # uid -> (present, read_at)
_HAS_KEY_TTL_S = 300.0


def _set_has_key(uid: str, present: bool) -> None:
    with _lock:
        _has_key_cache[uid] = (present, time.monotonic())


def _invalidate_has_key(uid: str) -> None:
    with _lock:
        _has_key_cache.pop(uid, None)


def has_key(uid: str) -> bool:
    with _lock:
        cached = _has_key_cache.get(uid)
    if cached is not None and (time.monotonic() - cached[1]) < _HAS_KEY_TTL_S:
        return cached[0]
    present = bool(_doc_ref(uid).get().exists)
    _reads.record("coindcx.keystore.has_key", 1)
    _set_has_key(uid, present)
    return present


# ---------------------------------------------------------------------------
# Roster
# ---------------------------------------------------------------------------

_roster_cache: Optional[tuple] = None  # (uids list, read_at)
_ROSTER_TTL_S = 3600.0


def invalidate_roster() -> None:
    global _roster_cache
    with _lock:
        _roster_cache = None


def list_active_uids() -> Optional[list[str]]:
    """Every uid with a CoinDCX key.  ``None`` = could not read (fan out to
    nobody); ``[]`` = nobody has connected."""
    global _roster_cache
    with _lock:
        cached = _roster_cache
    if cached is not None and (time.monotonic() - cached[1]) < _ROSTER_TTL_S:
        return list(cached[0])
    db = _db()
    if db is None:
        return None
    try:
        snap = db.collection(_ROSTER_DOC[0]).document(_ROSTER_DOC[1]).get()
        _reads.record("coindcx.keystore.roster", 1)
    except Exception as exc:
        log.warning("coindcx keystore: roster read failed: {}", exc)
        return None
    raw = (snap.to_dict() or {}).get(_ROSTER_FIELD) if snap.exists else []
    if not isinstance(raw, list):
        return None
    uids = sorted({str(u) for u in raw})
    with _lock:
        _roster_cache = (uids, time.monotonic())
    return list(uids)


def _roster_apply(uid: str, *, present: bool) -> None:
    """Add/remove one uid with an atomic array transform (no read-modify-write
    race between two connects), then signal the other container."""
    global _roster_cache
    db = _db()
    if db is None:
        raise CoinDCXKeystoreNotInitialisedError("Firestore client not initialised")
    from google.cloud import firestore  # type: ignore[import-not-found]

    transform = firestore.ArrayUnion([uid]) if present else firestore.ArrayRemove([uid])
    db.collection(_ROSTER_DOC[0]).document(_ROSTER_DOC[1]).set(
        {_ROSTER_FIELD: transform, "updated_at": datetime.now(timezone.utc)},
        merge=True,
    )
    with _lock:
        _roster_cache = None
    _bump(_gen_doc_roster())


# ---------------------------------------------------------------------------
# Generation plumbing
# ---------------------------------------------------------------------------


def _gen_doc_blobs() -> str:
    from src import control_generation as _gen

    return _gen.DOC_COINDCX_KEY_BLOBS


def _gen_doc_roster() -> str:
    from src import control_generation as _gen

    return _gen.DOC_COINDCX_ACTIVE_UIDS


def _generation(doc: str) -> Optional[int]:
    try:
        from src import control_generation as _gen

        return _gen.current(doc)
    except Exception:  # noqa: BLE001 — cannot tell → no cache
        return None


def _bump(doc: str) -> None:
    try:
        from src import control_generation as _gen

        for attempt in range(3):
            if _gen.bump(doc):
                return
            time.sleep(0.2 * (attempt + 1))
        raise RuntimeError(f"generation bump failed 3x: {doc}")
    except Exception as exc:  # noqa: BLE001 — never break a key write
        _fail_open(f"coindcx.keystore.bump:{doc}", exc)


def _bump_blobs(uid: str) -> None:
    invalidate_key_blob(uid)
    _bump(_gen_doc_blobs())


def _fail_open(site: str, exc: Optional[BaseException] = None) -> None:
    try:
        from src import fail_open as _fo

        _fo.record(site, exc or RuntimeError(site))
    except Exception:  # pragma: no cover
        log.exception("coindcx keystore: fail_open record failed at {}", site)


def register_generation_listeners() -> None:
    """Hook the roster cache to the cross-container generation (call at boot)."""
    try:
        from src import control_generation as _gen

        _gen.register(_gen.DOC_COINDCX_ACTIVE_UIDS, invalidate_roster)
    except Exception:  # pragma: no cover
        log.exception("coindcx keystore: roster generation listener not registered")


def cache_stats() -> dict:
    with _lock:
        return {
            **_blob_stats,
            "blob_entries": len(_blob_cache),
            "roster_cached": _roster_cache is not None,
        }


def set_db_for_test(db: Any) -> None:
    global _db_override
    _db_override = db


def reset_for_test() -> None:
    global _roster_cache, _db_override
    with _lock:
        _blob_cache.clear()
        _has_key_cache.clear()
        _roster_cache = None
        _db_override = None
        for k in _blob_stats:
            _blob_stats[k] = 0
