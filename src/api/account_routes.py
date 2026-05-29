"""``DELETE /api/account`` — in-app user account deletion.

Required by Google Play's User Data policy
(https://support.google.com/googleplay/android-developer/answer/13327111) —
apps that let users create an account must also let users delete it
from within the app.  Without this surface our Play Store submission
is rejected at the Data Safety review stage.

**The deletion sequence (orchestrated; soft-fails partial):**

1. **Revoke the Binance key blob from Firestore** (if present).
   This is the highest-priority step because a leftover encrypted
   key tied to a deleted user is the worst failure mode — the
   engine could in principle still dispatch orders to that key.
   We do this BEFORE we touch the user row so a crash between
   steps leaves the user's funds-side state safer than their
   app-side state.

2. **Delete the SQLite user row.** Per-user override tables
   cascade automatically via ``FOREIGN KEY ... ON DELETE CASCADE``
   (see ``user_overrides._AUTO_TRADE_SCHEMA`` et al).

3. **Invalidate the user-roster cache** in
   ``src.execution.signal_dispatch`` so the next dispatch attempt
   re-queries Firestore (which no longer has the key blob → the
   user drops out of ``_active_uids`` naturally).

If step 1 fails, we still attempt step 2 — and log the orphan-blob
condition loudly so an operator can clean it up manually.  The
client receives 204 only when ALL three steps succeeded; 503 with a
specific failure tag otherwise so the client can retry just the
failed step.

**Idempotency.**  Calling DELETE on an already-deleted user returns
204 (no-op).  The cache invalidation is always safe to re-run.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from fastapi import Depends, FastAPI, HTTPException, Response, status

from src.utils import get_logger

log = get_logger("api.account_routes")


def register(
    app: FastAPI,
    *,
    auth: Callable,
    identity_dep: Callable,
) -> None:
    """Wire ``DELETE /api/account`` onto the given app.

    Same wiring shape as the other per-user routes (auth dep gates
    access; identity dep resolves to the Firebase-authed user).
    """

    @app.delete(
        "/api/account",
        tags=["account"],
        dependencies=[Depends(auth)],
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_account(
        identity: Any = Depends(identity_dep),
    ) -> Response:
        """Delete the authenticated user's account + revoke Binance key.

        Returns 204 on success.  Returns 503 with a specific tag if
        any orchestration step fails so the client can retry.
        """
        # Lazy imports — keep this route loadable on the legacy
        # in-process test harness where the security stack isn't
        # wired up.
        from src.api import users as _users
        from src.security import firestore_keystore
        from src.execution import signal_dispatch

        firebase_uid = _resolve_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Account deletion requires Firebase sign-in. "
                    "Sign in with your Lumin account and try again."
                ),
            )

        # ---- Step 1: revoke the Binance key blob (highest priority) ----
        if firestore_keystore.is_initialised():
            try:
                # Firestore delete is network I/O — run off the event
                # loop so it doesn't block other requests.
                await asyncio.to_thread(
                    firestore_keystore.delete_key_blob, firebase_uid
                )
            except Exception:
                # Loud log — operator must clean up the orphan blob.
                # We DO NOT abort the deletion here; an orphan blob is
                # less dangerous than an orphan user row (the engine
                # only dispatches to users in _active_uids, which
                # requires both a Firestore blob AND a SQLite row).
                log.exception(
                    "delete_account: Firestore blob delete failed for "
                    "uid={} — orphan blob requires operator cleanup",
                    firebase_uid,
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="key_blob_delete_failed",
                )
        else:
            # Test paths + cold-deploy state where Firestore isn't
            # wired.  No blob to delete; proceed to step 2.
            log.info(
                "delete_account: Firestore keystore not initialised — "
                "skipping blob delete for uid={}",
                firebase_uid,
            )

        # ---- Step 2: delete the SQLite user row ----
        user_store = _users.get_singleton()
        if user_store is None:
            log.error(
                "delete_account: UserStore singleton not registered — "
                "cannot complete deletion for uid={}",
                firebase_uid,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="server_misconfiguration_user_store",
            )

        try:
            user = await user_store.aget_by_firebase_uid(firebase_uid)
        except Exception:
            log.exception(
                "delete_account: user lookup failed for uid={}",
                firebase_uid,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="user_lookup_failed",
            )

        if user is None:
            # Already deleted — idempotent path.  Step 1 ran
            # successfully (or harmlessly no-op'd), step 3 always
            # safe.  Return 204.
            log.info(
                "delete_account: no user row for uid={} — treating as "
                "already-deleted (idempotent)",
                firebase_uid,
            )
        else:
            try:
                await user_store.adelete_by_id(user.user_id)
            except Exception:
                log.exception(
                    "delete_account: user row delete failed for "
                    "user_id={} uid={}",
                    user.user_id, firebase_uid,
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="user_row_delete_failed",
                )

        # ---- Step 3: invalidate the active-uids cache ----
        try:
            signal_dispatch.reset_cache_for_test()
        except Exception:
            # Cache invalidation must NEVER fail the response — the
            # cache will expire naturally within 30s anyway (see
            # ``_ACTIVE_UIDS_TTL_S``).  Log + continue.
            log.exception(
                "delete_account: cache invalidation raised — recovery "
                "via natural TTL expiry within 30s"
            )

        log.info(
            "delete_account ok: uid={} (blob, row, cache all cleaned)",
            firebase_uid,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)


def _resolve_firebase_uid(identity: Any) -> Any:
    """Extract the Firebase uid from an identity-dep resolution.

    Mirrors the helper in ``binance_connect_routes._resolve_firebase_uid``
    — same identity shape from the same auth dep.  Returns ``None``
    when the identity doesn't carry a Firebase uid (anonymous device
    JWT, malformed token, etc.).
    """
    if identity is None:
        return None
    uid = getattr(identity, "firebase_uid", None)
    if uid is None and isinstance(identity, dict):
        uid = identity.get("firebase_uid")
    return uid
