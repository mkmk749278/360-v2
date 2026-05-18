"""AES-256-GCM envelope-encryption helpers for per-user Binance API secrets.

This module provides the **inner** half of the envelope: a per-user
data encryption key (DEK) AES-GCM-encrypts the Binance API secret.
The DEK itself is wrapped by Cloud KMS (the **outer** half) — see
:mod:`src.security.kms_client`.

Wire format for the encrypted-secret blob:

    nonce (12 B) || ciphertext (variable) || tag (16 B)

Packed as a single ``bytes`` so a caller stores or transports one
opaque buffer.  Decryption splits the buffer back into the three
fields.  The 12-byte nonce length is the GCM-recommended size (96
bits); the 16-byte tag is the default authentication-tag length.

The DEK is always 32 bytes (AES-256).  Callers should generate a
fresh DEK per user via :func:`generate_dek` and never reuse it
across users.

This module has zero GCP dependency — it's pure ``cryptography``
primitives so the unit tests run without any mocking infrastructure.
The GCP KMS interaction lives in :mod:`src.security.kms_client`.

Security notes for callers:

* **Never** log the DEK, the plaintext API secret, or the decrypted
  blob.  ``OWNER_BRIEF B18`` and ``CLAUDE.md § Hard Limits``
  forbid this absolutely.
* The plaintext DEK must be wiped from local variables as soon as
  the signing operation completes.  Python ``bytes`` is immutable
  so explicit zeroing isn't possible; minimise the lifetime of the
  variable and let it go out of scope quickly.
* :func:`decrypt_secret` raises on tampered ciphertext / wrong DEK
  — the GCM tag verification will fail with
  :class:`cryptography.exceptions.InvalidTag`.  Callers should
  treat that as a hard failure (corrupted blob or wrong DEK) and
  surface a "key blob unreadable — please reconnect" error rather
  than silently retrying.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Lazy import isn't needed here — ``cryptography`` is already a
# transitive dependency of ``firebase-admin`` (via google-auth) so
# the import cost is paid regardless.  Pinning explicitly in
# requirements.txt to surface it as a first-class dep.
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Standard AES-GCM parameters.
_DEK_BYTES = 32  # AES-256
_NONCE_BYTES = 12  # 96-bit GCM nonce (NIST SP 800-38D recommendation)
_TAG_BYTES = 16  # Default GCM tag length


@dataclass(frozen=True)
class EncryptedBlob:
    """Packed AES-GCM ciphertext: nonce || ciphertext || tag.

    ``raw`` is the wire-format buffer suitable for storing in
    Firestore (after base64) or transporting across a Unix socket.
    Use :meth:`pack` / :meth:`unpack` to convert between the
    structured form and the wire-format bytes.
    """

    nonce: bytes
    ciphertext_and_tag: bytes  # AES-GCM emits ciphertext || tag as one buffer

    @property
    def raw(self) -> bytes:
        """Concatenated wire-format bytes: ``nonce || ciphertext || tag``."""
        return self.nonce + self.ciphertext_and_tag

    @classmethod
    def unpack(cls, raw: bytes) -> "EncryptedBlob":
        """Split a wire-format buffer back into nonce + ciphertext-and-tag.

        Raises :class:`ValueError` if ``raw`` is shorter than the
        minimum legal length (``nonce + tag`` with empty plaintext).
        """
        if len(raw) < _NONCE_BYTES + _TAG_BYTES:
            raise ValueError(
                f"encrypted blob too short: got {len(raw)} bytes, "
                f"need at least {_NONCE_BYTES + _TAG_BYTES}"
            )
        return cls(
            nonce=raw[:_NONCE_BYTES],
            ciphertext_and_tag=raw[_NONCE_BYTES:],
        )


def generate_dek() -> bytes:
    """Return a fresh 32-byte data encryption key from the OS CSPRNG.

    Each user gets one DEK at provisioning time, KMS-wrapped, and
    persisted in encrypted form alongside their encrypted secret.
    Never reuse a DEK across users.
    """
    return os.urandom(_DEK_BYTES)


def encrypt_secret(dek: bytes, plaintext: bytes) -> EncryptedBlob:
    """AES-GCM-encrypt ``plaintext`` using ``dek``.

    ``dek`` must be exactly 32 bytes (``generate_dek`` output).  The
    nonce is freshly random per call — never reuse a nonce with the
    same key (GCM catastrophically fails under nonce reuse).

    Caller is responsible for serialising :attr:`EncryptedBlob.raw`
    (e.g. base64) for storage.
    """
    if len(dek) != _DEK_BYTES:
        raise ValueError(f"DEK must be {_DEK_BYTES} bytes; got {len(dek)}")
    aesgcm = AESGCM(dek)
    nonce = os.urandom(_NONCE_BYTES)
    ct_and_tag = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    return EncryptedBlob(nonce=nonce, ciphertext_and_tag=ct_and_tag)


def decrypt_secret(dek: bytes, blob: EncryptedBlob) -> bytes:
    """AES-GCM-decrypt ``blob`` using ``dek``.

    Raises :class:`cryptography.exceptions.InvalidTag` if the blob
    was tampered with or the wrong DEK was supplied — caller should
    treat both as a hard failure (do not retry, do not log details
    that could leak ciphertext properties).
    """
    if len(dek) != _DEK_BYTES:
        raise ValueError(f"DEK must be {_DEK_BYTES} bytes; got {len(dek)}")
    aesgcm = AESGCM(dek)
    return aesgcm.decrypt(blob.nonce, blob.ciphertext_and_tag, associated_data=None)
