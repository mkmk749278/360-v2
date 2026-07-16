"""``POST /api/binance/connect`` — server-side execution onboarding endpoint.

Carved out of ``server.py`` mirroring the ``paper_trade_routes`` pattern.
Wired by :func:`register` against a built FastAPI app.

What this endpoint does (the B18 connect flow in one place):

1. **Auth**: Firebase ID token required.  Static-token bypass is NOT
   accepted — keys are per-Firebase-uid; an owner-token cannot connect
   on behalf of a user.
2. **Geoblock**: rejects US users via :func:`geoblock.assert_country_allowed`.
   Defence-in-depth on top of the Firebase signup-flow block.
3. **Validate against Binance** via :func:`binance_connect_validator.validate_binance_key`:
   withdraw=false, futures=true, ip_restrict=true, engine VPS IP on
   whitelist, futures wallet actually accessible.  Each failure mode
   maps to a specific HTTP 400 with a ``code`` token + human-readable
   ``detail`` so the app can render targeted fix-up UI.
4. **Encrypt + persist**: on validation success, generate a per-user DEK,
   AES-GCM-encrypt the plaintext secret, KMS-wrap the DEK, persist the
   ciphertext + encrypted DEK + at-connect validation flags to Firestore
   via :func:`firestore_keystore.put_key_blob`.  Plaintext secret +
   plaintext DEK are wiped immediately.

The plaintext API secret:

* Arrives in the request body (HTTPS only — TLS termination at the
  ingress).
* Flows into the validator's signed-request helper for the duration
  of two signed GETs.
* Is AES-GCM-encrypted with the freshly-generated DEK.
* Is dropped (local variable goes out of scope) BEFORE the response
  is built.
* Is NEVER logged at any level.
* Is NEVER returned to the caller.
* Is NEVER written to disk in the clear.

Subsequent PRs (signing service, FSM workers) read the encrypted blob
back from Firestore and unwrap it inside the signing service's process
boundary — see ``OWNER_BRIEF §3.9`` for the full lifecycle.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status

from src.utils import get_logger

from .schemas import (
    BinanceConnectInfoResponse,
    BinanceConnectRequest,
    BinanceConnectResponse,
    BinanceConnectStatusResponse,
)

log = get_logger("api.binance_connect_routes")


def _engine_vps_ip() -> Optional[str]:
    """The IP users must whitelist on their Binance API key.

    Read from env at request-time rather than module-load-time so
    deployment can flip the value (e.g. VPS migration) without an
    engine restart of the API process.  Returns None if unset — in
    that case the route refuses to operate (we cannot give the user
    accurate whitelist instructions without knowing our own IP).
    """
    return os.environ.get("ENGINE_VPS_PUBLIC_IP") or None


def register(
    app: FastAPI,
    *,
    auth: Callable,
    identity_dep: Callable,
) -> None:
    """Wire ``POST /api/binance/connect`` onto the given app.

    ``auth`` — the standard auth dependency from ``build_app``.
    ``identity_dep`` — resolves the request to a User row (we need
        the Firebase uid to key the encrypted blob in Firestore).

    Idempotent in behaviour: calling twice would register duplicate
    routes (FastAPI would raise), so the caller calls exactly once
    per ``build_app`` invocation.
    """

    @app.post(
        "/api/binance/connect",
        response_model=BinanceConnectResponse,
        tags=["binance"],
        dependencies=[Depends(auth)],
        # Don't document the rate-limit path or the error schema in OpenAPI
        # — keep the surface intentionally small so attackers probing don't
        # learn about specific error codes.
    )
    async def binance_connect(
        request: Request,
        body: BinanceConnectRequest,
        identity: Any = Depends(identity_dep),
    ) -> BinanceConnectResponse:
        """Validate the user's Binance key against B18 rules + persist it.

        Returns 200 ``BinanceConnectResponse`` on success.

        Returns 400 with a typed error code on validation failure:
        ``WITHDRAW_ENABLED`` / ``FUTURES_DISABLED`` /
        ``IP_RESTRICT_DISABLED`` / ``IP_NOT_WHITELISTED`` / ``KEY_INVALID``.

        Returns 403 if the request originates from a blocked country
        (per :mod:`src.security.geoblock`).

        Returns 503 if Binance is unreachable — the user should retry.

        Returns 500 if KMS / Firestore are not initialised — operator
        action required.
        """
        # Imports are inside the handler so the route can register even
        # in test harnesses that haven't wired KMS / Firestore.  The
        # handler refuses at runtime if the dependencies aren't ready.
        from src.security import (
            binance_connect_validator,
            envelope_crypto,
            firestore_keystore,
            geoblock,
            kms_client,
        )

        # --- 1. Geoblock ---------------------------------------------------
        try:
            geoblock.assert_country_allowed(dict(request.headers))
        except geoblock.GeoblockError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=exc.user_message,
            )

        # --- 2. Resolve Firebase uid ---------------------------------------
        firebase_uid = _resolve_firebase_uid(identity)
        if firebase_uid is None:
            # Static-token / legacy-JWT auth landed here — the connect
            # flow requires a Firebase identity because Firestore key
            # blobs are keyed by Firebase uid (not the SQLite user_id).
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Binance key connect requires Firebase sign-in. "
                    "Sign in with your Lumin account and try again."
                ),
            )

        # --- 3. Refuse if dependencies aren't wired ------------------------
        engine_ip = _engine_vps_ip()
        if not engine_ip:
            log.error(
                "binance_connect refused: ENGINE_VPS_PUBLIC_IP not configured"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Server misconfiguration — ENGINE_VPS_PUBLIC_IP unset. "
                    "Operator must set this env var before connect flow can work."
                ),
            )
        if not kms_client.is_initialised():
            log.error("binance_connect refused: KMS client not initialised")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server misconfiguration — KMS not initialised.",
            )
        if not firestore_keystore.is_initialised():
            log.error(
                "binance_connect refused: Firestore keystore not initialised"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server misconfiguration — Firestore not initialised.",
            )

        # --- 4. Validate against Binance -----------------------------------
        # The plaintext secret enters this scope here and exits when
        # the variable goes out of scope at function return.  No log
        # statements between this point and the wipe at the end may
        # include ``body.api_secret`` or any derivative.
        try:
            validation = await binance_connect_validator.validate_binance_key(
                api_key=body.api_key,
                api_secret=body.api_secret,
            )
        except binance_connect_validator.WithdrawEnabledError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exc.user_message,
                headers={"X-Connect-Error-Code": "WITHDRAW_ENABLED"},
            )
        except binance_connect_validator.FuturesDisabledError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exc.user_message,
                headers={"X-Connect-Error-Code": "FUTURES_DISABLED"},
            )
        except binance_connect_validator.IpRestrictDisabledError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"{exc.user_message} Engine IP to whitelist: {engine_ip}"
                ),
                headers={
                    "X-Connect-Error-Code": "IP_RESTRICT_DISABLED",
                    "X-Engine-VPS-IP": engine_ip,
                },
            )
        except binance_connect_validator.IpNotWhitelistedError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"{exc.user_message} Engine IP to whitelist: {engine_ip}"
                ),
                headers={
                    "X-Connect-Error-Code": "IP_NOT_WHITELISTED",
                    "X-Engine-VPS-IP": engine_ip,
                },
            )
        except binance_connect_validator.KeyInvalidError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exc.user_message,
                headers={"X-Connect-Error-Code": "KEY_INVALID"},
            )
        except binance_connect_validator.BinanceUnreachableError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=exc.user_message,
                headers={"X-Connect-Error-Code": "BINANCE_UNREACHABLE"},
            )
        except binance_connect_validator.BinanceConnectValidationError as exc:
            # Unknown validation failure — surface as 400 so the app can
            # show the generic message rather than crashing.
            log.warning("binance_connect: unmapped validation error: {}", exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Binance rejected the key validation. Please try again.",
                headers={"X-Connect-Error-Code": "VALIDATION_UNKNOWN"},
            )

        # --- 5. Encrypt + persist -----------------------------------------
        # Generate a fresh per-user DEK, AES-GCM-encrypt the plaintext
        # secret, KMS-wrap the DEK, persist to Firestore.  Both
        # plaintext_dek and body.api_secret are dropped at function
        # return (Python locals + function-arg-bound dataclass).
        plaintext_dek = envelope_crypto.generate_dek()
        try:
            encrypted_blob = envelope_crypto.encrypt_secret(
                plaintext_dek, body.api_secret.encode("utf-8")
            )
            kms = kms_client.get_client()
            # KMS wrap is a blocking network round-trip to Cloud KMS — keep
            # it off the shared event loop so a slow KMS call doesn't stall
            # every other user's in-flight request.
            wrapped_dek = await asyncio.to_thread(kms.encrypt, plaintext_dek)
            # Firestore write is likewise a blocking network call.
            await asyncio.to_thread(
                firestore_keystore.put_key_blob,
                firebase_uid,
                encrypted_secret=encrypted_blob.raw,
                encrypted_dek=wrapped_dek,
                api_key_full=body.api_key,
                ip_whitelist_ok=validation.ip_whitelist_ok,
                withdraw_disabled_ok=validation.withdraw_disabled_ok,
            )
        except Exception:
            log.exception(
                "binance_connect: failed to encrypt+persist after validation"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Validated your Binance key but failed to securely "
                    "store it. Please try again; if this persists, contact "
                    "support."
                ),
            )
        finally:
            # Explicit dereference — Python's GC will collect the bytes
            # once the local goes out of scope, but the explicit del
            # makes the security boundary visible to anyone reading
            # the code.  The plaintext secret in ``body.api_secret``
            # follows when the request finishes and FastAPI releases
            # the pydantic model.
            del plaintext_dek

        # --- 6. Success response ------------------------------------------
        # Log success WITHOUT the api_key full value — only the first 8
        # chars (which the app will display anyway).  No secret material
        # in any log path.
        log.info(
            "binance_connect ok: firebase_uid={}, key_public_id_first8={}",
            firebase_uid,
            body.api_key[:8],
        )
        return BinanceConnectResponse(
            ok=True,
            key_public_id_first8=body.api_key[:8],
            withdraw_disabled_ok=validation.withdraw_disabled_ok,
            futures_enabled_ok=validation.futures_enabled_ok,
            ip_whitelist_ok=validation.ip_whitelist_ok,
        )

    @app.get(
        "/api/binance/connect/status",
        response_model=BinanceConnectStatusResponse,
        tags=["binance"],
        dependencies=[Depends(auth)],
    )
    async def binance_connect_status(
        identity: Any = Depends(identity_dep),
    ) -> BinanceConnectStatusResponse:
        """Return the current user's connection state.

        Returns ``connected=False`` (with all other fields null) when no
        Firestore key blob exists for the requesting Firebase uid.  When
        a blob exists, returns the non-secret metadata the Server-side
        execution page needs to render the connected-state UI — the
        first-8 key chars, connect timestamp, and at-connect validation
        flags.  Plaintext / encrypted secret material never round-trips.
        """
        from src.security import firestore_keystore

        firebase_uid = _resolve_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Binance connect status requires Firebase sign-in. "
                    "Sign in with your Lumin account and try again."
                ),
            )

        if not firestore_keystore.is_initialised():
            log.error(
                "binance_connect_status refused: Firestore keystore not "
                "initialised"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server misconfiguration — Firestore not initialised.",
            )

        try:
            # Firestore read is a blocking network round-trip — dispatch it
            # to a worker thread so the status poll doesn't stall the loop.
            blob = await asyncio.to_thread(
                firestore_keystore.get_key_blob, firebase_uid
            )
        except firestore_keystore.KeyBlobNotFoundError:
            return BinanceConnectStatusResponse(connected=False)
        except Exception:
            log.exception(
                "binance_connect_status: Firestore read failed for uid={}",
                firebase_uid,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not reach the key store. Please retry.",
            )

        return BinanceConnectStatusResponse(
            connected=True,
            key_public_id_first8=blob.key_public_id_first8,
            connected_at=blob.connected_at.isoformat(),
            withdraw_disabled_ok=blob.withdraw_disabled_ok,
            ip_whitelist_ok=blob.ip_whitelist_ok,
        )

    @app.get(
        "/api/binance/connect/info",
        response_model=BinanceConnectInfoResponse,
        tags=["binance"],
        dependencies=[Depends(auth)],
    )
    async def binance_connect_info() -> BinanceConnectInfoResponse:
        """Return the non-secret onboarding info the connect screen needs.

        Right now that is just the engine's public VPS IP — the address
        the user must add to their Binance API-key IP whitelist.  The app
        surfaces it *up front* (with one-tap copy) so the user can
        whitelist it BEFORE attempting to connect, breaking the
        chicken-and-egg where a connect can only succeed once the IP is
        already whitelisted.

        Deliberately depends on **neither KMS nor Firestore** — the IP is
        a plain env var (``ENGINE_VPS_PUBLIC_IP``).  This is the whole
        point: when KMS/Firestore are misconfigured (the connect flow
        502/500s), the user can still retrieve the whitelist IP here and
        prepare their Binance key.  Returns ``engine_vps_ip=null`` (HTTP
        200, not 500) when the operator hasn't set the env var, so the app
        degrades gracefully rather than showing an error.

        The IP is not a secret — it is *meant* to be shared for
        whitelisting — but the route stays behind the auth gate so only
        signed-in app users can read it, never the open internet.
        """
        return BinanceConnectInfoResponse(engine_vps_ip=_engine_vps_ip())

    @app.delete(
        "/api/binance/connect",
        status_code=status.HTTP_204_NO_CONTENT,
        # Explicit no-body: a 204 must not declare a response model.  Without
        # this, FastAPI infers the model from the ``-> None`` return annotation
        # (as NoneType), which trips its "204 must not have a response body"
        # assertion at app-construction time on some versions.  Being explicit
        # keeps the route correct across FastAPI versions.
        response_model=None,
        tags=["binance"],
        dependencies=[Depends(auth)],
    )
    async def binance_connect_delete(
        identity: Any = Depends(identity_dep),
    ) -> None:
        """Disconnect the user's Binance key.

        Hard-deletes the Firestore blob — both the encrypted secret and
        the KMS-wrapped DEK — so the engine has no path back to signed
        Binance calls for this user until they connect again.  Any
        positions already open on Binance are NOT closed; the user must
        close them on Binance directly (the engine has no live order
        path to them once the key is gone, by design).

        Idempotent: calling on a not-connected user returns 204 the
        same as calling on a connected user — the wire effect is
        identical (post-call there is no blob for this uid).
        """
        from src.security import firestore_keystore

        firebase_uid = _resolve_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Binance disconnect requires Firebase sign-in. "
                    "Sign in with your Lumin account and try again."
                ),
            )

        if not firestore_keystore.is_initialised():
            log.error(
                "binance_connect_delete refused: Firestore keystore not "
                "initialised"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server misconfiguration — Firestore not initialised.",
            )

        try:
            # Firestore delete is a blocking network round-trip — thread it
            # (mirrors account_routes.py, which already threads this call).
            await asyncio.to_thread(
                firestore_keystore.delete_key_blob, firebase_uid
            )
        except Exception:
            log.exception(
                "binance_connect_delete: Firestore delete failed for uid={}",
                firebase_uid,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not reach the key store. Please retry.",
            )

        log.info("binance_connect_delete ok: firebase_uid={}", firebase_uid)
        return None


def _resolve_firebase_uid(identity: Any) -> Optional[str]:
    """Extract the Firebase uid from an identity-dep resolution.

    Returns the uid string when the request authenticated via Firebase
    (``User`` row with a ``firebase_uid`` column populated).  Returns
    ``None`` for static-token bypass (no user identity) or legacy-JWT
    paths (no Firebase uid attached) — the route refuses both.

    Kept private to this module because the resolution rules are
    connect-flow-specific: other endpoints accept legacy JWT happily,
    but the connect flow demands a Firebase identity (Firestore key
    blobs are keyed by Firebase uid, not SQLite user_id).
    """
    if identity is None:
        return None  # static-token bypass
    # Try ``firebase_uid`` attribute (UserStore User row).  Falling back
    # to ``sub`` (legacy JWT TokenClaims) explicitly returns None — we
    # do NOT silently accept legacy-JWT auth on this route.
    firebase_uid = getattr(identity, "firebase_uid", None)
    if isinstance(firebase_uid, str) and firebase_uid:
        return firebase_uid
    return None
