"""Tests for src.security.envelope_crypto.

Pure-Python AES-GCM, no GCP plumbing — every test is a real
round-trip with the real ``cryptography`` library.  No mocks.

What we pin here:

* ``generate_dek`` returns 32-byte buffers that vary across calls.
* ``encrypt_secret`` returns blobs whose wire format is
  ``nonce || ciphertext || tag`` and whose ``raw`` is bijectively
  recoverable via ``EncryptedBlob.unpack``.
* Round-trip: ``decrypt_secret(dek, encrypt_secret(dek, p)) == p``.
* Tampered ciphertext fails authentication (GCM tag check) — this
  is the property that protects against silent corruption of the
  blob in storage.
* Wrong DEK fails authentication — protects against per-user key
  mix-up (one user's blob can't be opened with another user's DEK).
* Nonce uniqueness — back-to-back encrypts of the same plaintext
  with the same DEK produce DIFFERENT ciphertexts (because each
  call draws a fresh random nonce).  This is the security-critical
  invariant; nonce reuse would catastrophically break GCM.
* Invalid DEK length rejected with a clear ``ValueError`` rather
  than a cryptography-library traceback that the user has to
  decode.
"""
from __future__ import annotations

import pytest
from cryptography.exceptions import InvalidTag

from src.security.envelope_crypto import (
    EncryptedBlob,
    decrypt_secret,
    encrypt_secret,
    generate_dek,
)


# ---------------------------------------------------------------------------
# generate_dek
# ---------------------------------------------------------------------------


def test_generate_dek_returns_32_bytes() -> None:
    dek = generate_dek()
    assert isinstance(dek, bytes)
    assert len(dek) == 32  # AES-256


def test_generate_dek_returns_different_bytes_across_calls() -> None:
    """Two consecutive DEK generations must not collide — they're drawn
    from the OS CSPRNG.  Collision probability is negligible; if it
    happens twice in CI it's a real bug, not flake."""
    a = generate_dek()
    b = generate_dek()
    assert a != b


# ---------------------------------------------------------------------------
# EncryptedBlob wire format
# ---------------------------------------------------------------------------


def test_encrypted_blob_raw_concatenates_nonce_then_ciphertext_and_tag() -> None:
    blob = EncryptedBlob(nonce=b"n" * 12, ciphertext_and_tag=b"X" * 32)
    assert blob.raw == b"n" * 12 + b"X" * 32


def test_encrypted_blob_unpack_round_trips() -> None:
    """``unpack(raw)`` is the inverse of ``raw`` — wire format is
    bijective so persistence doesn't need a separate codec."""
    original = EncryptedBlob(
        nonce=b"\x01" * 12, ciphertext_and_tag=b"\x02" * 48
    )
    recovered = EncryptedBlob.unpack(original.raw)
    assert recovered.nonce == original.nonce
    assert recovered.ciphertext_and_tag == original.ciphertext_and_tag


def test_encrypted_blob_unpack_rejects_too_short_input() -> None:
    """A buffer shorter than ``nonce + tag`` cannot possibly be a valid
    AES-GCM ciphertext — fail explicitly rather than letting the
    decrypt path emit a cryptography-library traceback."""
    with pytest.raises(ValueError, match="encrypted blob too short"):
        EncryptedBlob.unpack(b"\x00" * 27)  # 1 byte short of 12+16


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------


def test_round_trip_recovers_exact_plaintext() -> None:
    dek = generate_dek()
    plaintext = b"binance_api_secret_64_chars_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    blob = encrypt_secret(dek, plaintext)
    recovered = decrypt_secret(dek, blob)
    assert recovered == plaintext


def test_round_trip_handles_empty_plaintext() -> None:
    """Edge case — GCM is well-defined on empty plaintext (the tag
    still authenticates).  Test it explicitly because an off-by-one
    in the unpack length check would surface here."""
    dek = generate_dek()
    blob = encrypt_secret(dek, b"")
    recovered = decrypt_secret(dek, blob)
    assert recovered == b""


def test_round_trip_via_wire_format() -> None:
    """Encrypt → serialise to ``raw`` → unpack → decrypt.  Mirrors
    the production path: encrypt at provision time, persist
    ``base64(raw)`` to Firestore, base64-decode at sign time, unpack,
    decrypt."""
    dek = generate_dek()
    plaintext = b"hello binance"
    blob = encrypt_secret(dek, plaintext)
    raw = blob.raw
    # Persistence boundary — only the bytes survive, the dataclass
    # instance does not.
    recovered_blob = EncryptedBlob.unpack(raw)
    assert decrypt_secret(dek, recovered_blob) == plaintext


# ---------------------------------------------------------------------------
# Security invariants
# ---------------------------------------------------------------------------


def test_nonce_is_fresh_across_calls() -> None:
    """Critical: encrypting the same plaintext twice with the same
    DEK must produce DIFFERENT ciphertexts.  Nonce reuse would
    break GCM's confidentiality + integrity guarantees catastrophically
    (recovers the XOR of two plaintexts; forges arbitrary
    ciphertexts).  This test is the canary that catches a future
    refactor that 'optimises' the nonce."""
    dek = generate_dek()
    plaintext = b"identical plaintext"
    first = encrypt_secret(dek, plaintext)
    second = encrypt_secret(dek, plaintext)
    assert first.nonce != second.nonce
    assert first.ciphertext_and_tag != second.ciphertext_and_tag
    # And both decrypt to the original.
    assert decrypt_secret(dek, first) == plaintext
    assert decrypt_secret(dek, second) == plaintext


def test_tampered_ciphertext_fails_authentication() -> None:
    """Flip one byte of the ciphertext-and-tag — GCM's tag check must
    reject it.  This is the property that protects against silent
    blob corruption between Firestore and the signing service."""
    dek = generate_dek()
    blob = encrypt_secret(dek, b"a secret")
    tampered_ct_and_tag = bytearray(blob.ciphertext_and_tag)
    tampered_ct_and_tag[0] ^= 0x01
    tampered = EncryptedBlob(
        nonce=blob.nonce, ciphertext_and_tag=bytes(tampered_ct_and_tag)
    )
    with pytest.raises(InvalidTag):
        decrypt_secret(dek, tampered)


def test_tampered_nonce_fails_authentication() -> None:
    """Flip one byte of the nonce — same outcome.  This protects
    against an attacker who can read the wire format and tries to
    swap nonces between blobs to confuse the recipient."""
    dek = generate_dek()
    blob = encrypt_secret(dek, b"a secret")
    tampered_nonce = bytearray(blob.nonce)
    tampered_nonce[0] ^= 0x01
    tampered = EncryptedBlob(
        nonce=bytes(tampered_nonce), ciphertext_and_tag=blob.ciphertext_and_tag
    )
    with pytest.raises(InvalidTag):
        decrypt_secret(dek, tampered)


def test_wrong_dek_fails_authentication() -> None:
    """User A's encrypted blob cannot be opened with user B's DEK.
    Protects against per-user key mix-ups in the Firestore lookup
    path (defence in depth — the Firestore lookup is already
    keyed by uid, but if a bug ever mismatches blob-to-uid the
    crypto layer still rejects)."""
    dek_a = generate_dek()
    dek_b = generate_dek()
    blob = encrypt_secret(dek_a, b"user A's secret")
    with pytest.raises(InvalidTag):
        decrypt_secret(dek_b, blob)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def test_encrypt_rejects_wrong_dek_length() -> None:
    """A 16-byte DEK (e.g. AES-128) is rejected with a clear error
    rather than producing an inconsistent ciphertext that decrypts
    fine until the production AES-256 path is wired."""
    with pytest.raises(ValueError, match="DEK must be 32 bytes"):
        encrypt_secret(b"x" * 16, b"plaintext")


def test_decrypt_rejects_wrong_dek_length() -> None:
    with pytest.raises(ValueError, match="DEK must be 32 bytes"):
        decrypt_secret(b"x" * 16, EncryptedBlob(b"n" * 12, b"x" * 32))
