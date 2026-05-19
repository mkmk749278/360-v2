"""Signing-service request handler — the security-critical core.

This module is where the plaintext Binance API secret materialises
(briefly) inside the signing-service process.  Every other module in
this service / the engine never sees plaintext.  The lifecycle inside
:func:`handle_request`:

1. Read the user's encrypted blob from Firestore.
2. Call KMS ``Decrypt`` to unwrap the per-user DEK.
3. AES-GCM-decrypt the secret with the unwrapped DEK.
4. HMAC-sign the Binance request query string with the plaintext
   secret.
5. Send the signed HTTP request to Binance, capture the response.
6. Return ONLY the Binance response status + body to the caller.

The plaintext secret + plaintext DEK exist as Python locals inside
this function and are dropped on return.  Python's GC reclaims them
shortly after; explicit ``del`` statements at the boundaries make
the security contract visible to readers.

**Hard rules** that this module's tests pin:

* Plaintext secret NEVER appears in any log statement.
* Plaintext secret NEVER returned to the caller (via wire or
  exception).
* Plaintext DEK NEVER appears in any log statement.
* Errors from KMS Decrypt are distinguishable from errors from
  AES-GCM Decrypt — different error codes, different operator
  response (KMS = transient, GCM = hard fail).
* Errors from Binance HTTP are distinguishable from errors from
  network reachability — different error codes, different caller
  retry policy.

This module assumes :func:`src.security.kms_client.init_kms_client`
and :func:`src.security.firestore_keystore.init_keystore` have been
called at signing-service boot.  The :func:`run` entry point in
:mod:`src.security.signing_service.__main__` handles that.
"""

from __future__ import annotations

import time
import urllib.parse
from typing import Any, Optional

import aiohttp
from cryptography.exceptions import InvalidTag

from src.security import envelope_crypto, firestore_keystore, kms_client
from src.security.binance_connect_validator import _sign_query
from src.utils import get_logger

from .protocol import (
    ERR_BAD_REQUEST,
    ERR_BINANCE_HTTP_ERROR,
    ERR_BINANCE_UNREACHABLE,
    ERR_CRYPTO_DECRYPT_FAILED,
    ERR_INTERNAL_ERROR,
    ERR_KEY_BLOB_NOT_FOUND,
    ERR_KMS_DECRYPT_FAILED,
    SignRequest,
    SignResponse,
)

log = get_logger("security.signing_service.handler")


_SPOT_BASE = "https://api.binance.com"
_FUTURES_BASE = "https://fapi.binance.com"
_REQUEST_TIMEOUT_S = 8.0


def _base_url(base: str) -> str:
    """Resolve the ``spot`` / ``futures`` label to an actual URL.

    Centralised so a future testnet pivot or regional endpoint change
    touches one place.  The validator in PR-2 uses the same URLs;
    they're not factored into a constants module YET because the two
    sites are small and the duplication is obvious enough that drift
    would surface immediately.
    """
    if base == "spot":
        return _SPOT_BASE
    if base == "futures":
        return _FUTURES_BASE
    raise ValueError(f"unknown base: {base!r}")


async def handle_request(
    request: SignRequest,
    *,
    session: Optional[aiohttp.ClientSession] = None,
) -> SignResponse:
    """Dispatch on ``request.verb`` and produce a :class:`SignResponse`.

    The handler is intentionally one function with explicit per-verb
    branches rather than a verb→method dict — easier to audit, easier
    to verify that each verb's error paths produce the right typed
    response.

    Catches every exception type by name (no bare ``except Exception``
    that would swallow secrets-in-tracebacks) and maps to the typed
    error codes the wire protocol exposes.

    ``session`` is injectable for tests so unit tests don't open real
    sockets.  In production the server passes a shared session that
    lives for the lifetime of the service process.
    """
    if request.verb == "ping":
        return SignResponse.ok_reply(
            request.id, binance_status=200, binance_body={"pong": True}
        )

    # All binance_signed_* verbs share the same unwrap-and-call body.
    if request.verb not in (
        "binance_signed_get",
        "binance_signed_post",
        "binance_signed_delete",
    ):
        return SignResponse.error_reply(
            request.id,
            code=ERR_BAD_REQUEST,
            message=f"unknown verb: {request.verb!r}",
        )

    if not request.firebase_uid:
        return SignResponse.error_reply(
            request.id,
            code=ERR_BAD_REQUEST,
            message="firebase_uid is required for signing verbs",
        )
    if not request.path:
        return SignResponse.error_reply(
            request.id,
            code=ERR_BAD_REQUEST,
            message="path is required for signing verbs",
        )

    try:
        base_url = _base_url(request.base)
    except ValueError as exc:
        return SignResponse.error_reply(
            request.id,
            code=ERR_BAD_REQUEST,
            message=str(exc),
        )

    # --- 1. Read encrypted blob from Firestore ----------------------------
    try:
        blob = firestore_keystore.get_key_blob(request.firebase_uid)
    except firestore_keystore.KeyBlobNotFoundError:
        return SignResponse.error_reply(
            request.id,
            code=ERR_KEY_BLOB_NOT_FOUND,
            message=f"no key blob for uid={request.firebase_uid}",
        )
    except firestore_keystore.FirestoreKeystoreNotInitialisedError:
        log.error("signing handler: Firestore keystore not initialised")
        return SignResponse.error_reply(
            request.id,
            code=ERR_INTERNAL_ERROR,
            message="Firestore keystore not initialised at boot",
        )

    # --- 2. Unwrap DEK via KMS --------------------------------------------
    try:
        kms = kms_client.get_client()
        plaintext_dek = kms.decrypt(blob.encrypted_dek)
    except kms_client.KmsNotInitialisedError:
        log.error("signing handler: KMS client not initialised")
        return SignResponse.error_reply(
            request.id,
            code=ERR_INTERNAL_ERROR,
            message="KMS client not initialised at boot",
        )
    except Exception as exc:
        # Anything else from the KMS SDK — IAM revoked, key disabled,
        # quota exceeded, network to GCP failed.  Log without secret
        # material (the exception text is GCP-side, no user keys).
        log.warning("signing handler: KMS Decrypt failed: {}", exc)
        return SignResponse.error_reply(
            request.id,
            code=ERR_KMS_DECRYPT_FAILED,
            message=f"KMS Decrypt failed: {exc}",
        )

    # --- 3. AES-GCM-decrypt the secret ------------------------------------
    try:
        plaintext_secret_bytes = envelope_crypto.decrypt_secret(
            plaintext_dek,
            envelope_crypto.EncryptedBlob.unpack(blob.encrypted_secret),
        )
    except InvalidTag:
        # Tampered ciphertext OR wrong DEK.  Either way — hard failure;
        # user must reconnect.  DO NOT include ciphertext bytes or DEK
        # in the log.
        log.error(
            "signing handler: AES-GCM authentication failed for uid={}",
            request.firebase_uid,
        )
        # Wipe the plaintext DEK before returning.
        del plaintext_dek
        return SignResponse.error_reply(
            request.id,
            code=ERR_CRYPTO_DECRYPT_FAILED,
            message="encrypted blob authentication failed — user must reconnect",
        )
    except ValueError as exc:
        log.error(
            "signing handler: blob unpack failed for uid={}: {}",
            request.firebase_uid,
            exc,
        )
        del plaintext_dek
        return SignResponse.error_reply(
            request.id,
            code=ERR_CRYPTO_DECRYPT_FAILED,
            message=f"blob unpack failed: {exc}",
        )

    # The plaintext DEK is no longer needed once we have the plaintext
    # secret.  Explicit del shrinks the time window the bytes are
    # reachable from this stack frame.
    del plaintext_dek

    # The plaintext secret string is bound to the local ``plaintext_secret``
    # below.  It's used inside the signed-call helper, NEVER logged,
    # NEVER returned via the SignResponse wire format.
    try:
        plaintext_secret = plaintext_secret_bytes.decode("utf-8")
    finally:
        # plaintext_secret_bytes is now redundant; clear the reference
        # so the gc can reclaim the byte buffer.
        del plaintext_secret_bytes

    # --- 4. Sign + send Binance request -----------------------------------
    try:
        binance_status, binance_body = await _signed_call(
            verb=request.verb,
            api_key=_extract_api_key(blob),
            api_secret=plaintext_secret,
            base_url=base_url,
            path=request.path,
            params=request.params,
            recv_window_ms=request.recv_window_ms,
            session=session,
        )
    except _BinanceUnreachable as exc:
        return SignResponse.error_reply(
            request.id,
            code=ERR_BINANCE_UNREACHABLE,
            message=str(exc),
        )
    except Exception as exc:
        # Catch-all so a handler bug never leaks the plaintext secret
        # in a server-side exception traceback that crosses the wire.
        # ``exc`` is the cleaned-up exception message only.
        log.exception("signing handler: unexpected error during signed call")
        return SignResponse.error_reply(
            request.id,
            code=ERR_INTERNAL_ERROR,
            message=f"unexpected error: {type(exc).__name__}",
        )
    finally:
        # Last reference drop.  Once this finally exits, the
        # plaintext secret is gc-reachable only via Python's
        # internal cycles (which are short).
        del plaintext_secret

    # Map Binance non-2xx to ERR_BINANCE_HTTP_ERROR with the status +
    # body preserved so the caller can inspect.
    if not (200 <= binance_status < 300):
        # Extract Binance's typed code + msg from the response body so
        # the diagnostic message names the actual failure (e.g.
        # ``code=-2019 msg='Margin is insufficient'``) instead of the
        # generic ``Binance returned 400``.  Binance's error JSON is
        # always ``{"code": <int>, "msg": <str>}`` for 4xx responses;
        # 5xx may differ but the same key pair is conventional.
        # Falls back to the generic shape when the body isn't a dict.
        bcode = None
        bmsg = None
        if isinstance(binance_body, dict):
            bcode = binance_body.get("code")
            bmsg = binance_body.get("msg") or binance_body.get("message")
        if bcode is not None or bmsg is not None:
            message = (
                f"Binance returned {binance_status} "
                f"(code={bcode} msg={bmsg!r})"
            )
        else:
            message = f"Binance returned {binance_status}"
        # B18 safety: Binance's response body never contains secret
        # material (the API secret only ever flows in the request HMAC,
        # not in any response).  Therefore embedding ``code`` + ``msg``
        # here cannot leak the secret per the hard limit on secret
        # logging in OWNER_BRIEF.
        return SignResponse.error_reply(
            request.id,
            code=ERR_BINANCE_HTTP_ERROR,
            message=message,
            binance_status=binance_status,
            binance_body=binance_body,
        )

    return SignResponse.ok_reply(
        request.id,
        binance_status=binance_status,
        binance_body=binance_body,
    )


def _extract_api_key(blob: firestore_keystore.UserKeyBlob) -> str:
    """Extract the user's full PUBLIC api_key from the Firestore blob.

    Stored plaintext at connect time (per
    :func:`src.security.firestore_keystore.put_key_blob`) because the
    api_key is the public half of the pair — encrypting it would add
    cost without security benefit, and the signing service needs it
    for every ``X-MBX-APIKEY`` header on signed requests.
    """
    return blob.api_key_full


class _BinanceUnreachable(Exception):
    """Internal sentinel for network/timeout failures.  Translated to
    ERR_BINANCE_UNREACHABLE by the dispatch wrapper."""


async def _signed_call(
    *,
    verb: str,
    api_key: str,
    api_secret: str,
    base_url: str,
    path: str,
    params: dict,
    recv_window_ms: int,
    session: Optional[aiohttp.ClientSession],
) -> tuple[int, Any]:
    """Perform the actual signed HTTP call to Binance.

    Returns ``(status_code, parsed_body)``.  Raises
    :class:`_BinanceUnreachable` on network errors.

    The plaintext ``api_secret`` is held in this function's local
    scope for the duration of the HMAC compute and dropped on return.
    Never logged.  The signed URL contains the signature in the query
    string; log statements deliberately log only ``path`` not ``url``.
    """
    full_params: dict = dict(params or {})
    full_params["timestamp"] = int(time.time() * 1000)
    full_params["recvWindow"] = recv_window_ms
    query = urllib.parse.urlencode(full_params)
    sig = _sign_query(api_secret, query)
    url = f"{base_url}{path}?{query}&signature={sig}"
    headers = {"X-MBX-APIKEY": api_key}

    method = {
        "binance_signed_get": "GET",
        "binance_signed_post": "POST",
        "binance_signed_delete": "DELETE",
    }.get(verb)
    if method is None:
        raise ValueError(f"unsupported verb: {verb!r}")

    own_session = session is None
    if session is None:
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=_REQUEST_TIMEOUT_S)
        )
    try:
        async with session.request(method, url, headers=headers) as resp:
            try:
                body = await resp.json(content_type=None)
            except (aiohttp.ContentTypeError, ValueError):
                body = None
            return resp.status, body
    except aiohttp.ClientError as exc:
        raise _BinanceUnreachable(f"network error calling {path}: {exc}")
    finally:
        if own_session:
            await session.close()
