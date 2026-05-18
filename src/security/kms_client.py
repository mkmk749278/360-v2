"""Google Cloud KMS client wrapper — the outer envelope-encryption layer.

Wraps :class:`google.cloud.kms_v1.KeyManagementServiceClient` to give
the engine a tiny, focused API surface:

* :meth:`KmsClient.encrypt` — wrap a DEK (or any small secret) with
  the configured KMS key.  Used at user-key-provisioning time.
* :meth:`KmsClient.decrypt` — unwrap a previously-KMS-encrypted blob.
  Used at signing time, every order.

The master key (KEK) is created **once per GCP project** by the
operator (see ``docs/server-side-execution-setup.md``).  The engine
never creates or rotates KEKs at runtime — that's an explicit ops
action so accidental code paths can't churn keys mid-flight.

Lifecycle mirrors :mod:`src.api.firebase_auth`:

* :func:`init_kms_client` is called once at boot from
  :mod:`src.bootstrap` after Firebase Admin is up (they share the
  same GCP service account).  Idempotent.
* :func:`is_initialised` lets call sites probe whether KMS is wired
  without raising — failed init at boot is recoverable for everything
  except the signing service, which refuses to start without KMS.
* :func:`get_client` returns the singleton :class:`KmsClient` or
  raises :class:`KmsNotInitialisedError` if init never succeeded.

Threading: the module-level state is set once at boot and read many
times per signing operation.  An :class:`threading.RLock` guards
:func:`init_kms_client` so test harnesses spawning multiple engines
don't race on the singleton.

The KMS SDK is **lazy-imported** so installs that don't enable
server-side execution don't pay the import cost.  Mirrors the
pattern in :mod:`src.api.firebase_auth`.

Security notes:

* The plaintext returned by :meth:`KmsClient.decrypt` must be wiped
  from local variables as quickly as possible.  Never log it,
  never persist it, never return it to a caller outside the
  signing service.
* KMS audit-logs every Decrypt call.  Anomalous decrypt rates
  (e.g. a sudden burst from a single user) are visible in Cloud
  Logging and should fire an operator alert via the engine's
  Telegram channel.  Wiring that alert is a later-PR concern.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Optional

from src.utils import get_logger

log = get_logger("security.kms_client")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class KmsError(Exception):
    """Base class for KMS client errors surfaced to callers."""


class KmsNotInitialisedError(KmsError):
    """:func:`get_client` called before :func:`init_kms_client` succeeded."""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KmsKeyRef:
    """Fully-qualified reference to a single KMS key.

    GCP KMS keys are addressed by
    ``projects/{project}/locations/{location}/keyRings/{keyring}/cryptoKeys/{key}``
    — :meth:`resource_name` builds that string from the four parts.
    """

    project_id: str
    location: str
    keyring: str
    key_name: str

    @property
    def resource_name(self) -> str:
        return (
            f"projects/{self.project_id}/locations/{self.location}/"
            f"keyRings/{self.keyring}/cryptoKeys/{self.key_name}"
        )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class KmsClient:
    """Thin wrapper around ``KeyManagementServiceClient``.

    The constructor accepts an explicit ``client`` so tests can inject
    a mock without touching :mod:`google.cloud.kms_v1`.  In production
    :func:`init_kms_client` builds the real GCP client and passes it
    here.
    """

    def __init__(self, key_ref: KmsKeyRef, client: Any) -> None:
        self._key_ref = key_ref
        self._client = client

    @property
    def key_ref(self) -> KmsKeyRef:
        return self._key_ref

    def encrypt(self, plaintext: bytes) -> bytes:
        """Wrap ``plaintext`` (typically a 32-byte DEK) with the KMS key.

        Returns the opaque KMS ciphertext bytes suitable for
        persisting in Firestore.  The plaintext is sent over TLS to
        Google's KMS service and never persists in our memory beyond
        the caller's local variable.
        """
        response = self._client.encrypt(
            request={
                "name": self._key_ref.resource_name,
                "plaintext": plaintext,
            }
        )
        return bytes(response.ciphertext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Unwrap a previously-encrypted DEK.  Returns plaintext bytes.

        Callers MUST drop references to the returned plaintext as
        soon as the signing operation completes.  Logging or
        persisting the plaintext violates ``OWNER_BRIEF B18``.
        """
        response = self._client.decrypt(
            request={
                "name": self._key_ref.resource_name,
                "ciphertext": ciphertext,
            }
        )
        return bytes(response.plaintext)


# ---------------------------------------------------------------------------
# Module-level singleton + init
# ---------------------------------------------------------------------------


_lock = threading.RLock()
_client: Optional[KmsClient] = None


def init_kms_client(
    project_id: str,
    location: str,
    keyring: str,
    key_name: str,
    service_account_path: Optional[str] = None,
) -> None:
    """Build and register the singleton KMS client.

    Idempotent — a second call is a no-op (logs the existing config).
    Loads :mod:`google.cloud.kms_v1` lazily so engines that don't
    enable server-side execution don't pay the import cost.

    ``service_account_path`` is optional; when provided it overrides
    the default ``GOOGLE_APPLICATION_CREDENTIALS`` discovery.  When
    omitted the client falls back to ADC (Application Default
    Credentials), which is what the engine uses in production with
    the same service-account JSON that Firebase Admin loads.
    """
    global _client
    with _lock:
        if _client is not None:
            log.info(
                "KMS client already initialised: key={}",
                _client.key_ref.resource_name,
            )
            return
        # Lazy import — google-cloud-kms pulls in grpc + protobuf, a
        # non-trivial cost we shouldn't impose on installs that don't
        # use server-side execution.
        from google.cloud import kms_v1  # type: ignore[import-not-found]
        from google.oauth2 import service_account  # type: ignore[import-not-found]

        if service_account_path:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path
            )
            gcp_client = kms_v1.KeyManagementServiceClient(credentials=credentials)
        else:
            gcp_client = kms_v1.KeyManagementServiceClient()
        key_ref = KmsKeyRef(
            project_id=project_id,
            location=location,
            keyring=keyring,
            key_name=key_name,
        )
        _client = KmsClient(key_ref=key_ref, client=gcp_client)
        log.info(
            "KMS client initialised: key={}, service_account={}",
            key_ref.resource_name,
            service_account_path or "ADC",
        )


def is_initialised() -> bool:
    """Return True iff :func:`init_kms_client` has been called successfully."""
    with _lock:
        return _client is not None


def get_client() -> KmsClient:
    """Return the singleton :class:`KmsClient` or raise.

    The signing service calls this on every order.  Engine startup
    paths that aren't security-critical should probe via
    :func:`is_initialised` instead so a missing KMS configuration
    doesn't crash boot.
    """
    with _lock:
        if _client is None:
            raise KmsNotInitialisedError(
                "KMS client not initialised — call init_kms_client at boot"
            )
        return _client


def reset_for_test() -> None:
    """Test-only: drop the singleton so the next test starts uninitialised."""
    global _client
    with _lock:
        _client = None
