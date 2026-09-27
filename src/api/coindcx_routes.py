"""CoinDCX venue API — connect a key, choose a platform, see positions.

User routes (Firebase identity):

* ``GET    /api/coindcx/info``            — what the app needs to render the
  connect guide (our IP, the attestation wording, margin + leverage ranges).
* ``POST   /api/coindcx/connect``         — validate, attest, encrypt, store.
* ``GET    /api/coindcx/connect/status``  — connected / attested, tri-state.
* ``DELETE /api/coindcx/connect``         — remove the key (refused while a
  CoinDCX position is live: nothing could then close or protect it).
* ``GET    /api/venue`` / ``PUT /api/venue`` — the user's platform choice,
  margin currency and leverage.  Choosing CoinDCX requires an attested key.
* ``GET    /api/coindcx/positions``       — the user's CoinDCX positions.

Owner routes:

* ``POST /api/admin/coindcx/self-test``  — queue the real-account checklist.
* ``GET  /api/admin/coindcx/status``     — the engine's status file + the last
  self-test report (both written by the engine on the shared data volume).

Readability rule (CLAUDE.md, *unknown is not a value*): every field a user
reads carries whether we could observe it.  ``readable: false`` never renders
as "not connected".
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field

from src.utils import get_logger

log = get_logger("api.coindcx_routes")

#: The wording the user confirms.  Versioned: changing it bumps
#: ``keystore.ATTESTATION_VERSION`` so older attestations can be re-asked.
ATTESTATION_ITEMS = (
    "I created this CoinDCX API key only for Lumin and bound it to the server "
    "IP shown on this screen.",
    "This key cannot withdraw funds.",
    "I understand Lumin can place and close futures orders on my CoinDCX "
    "account with this key, within my Auto Trade settings.",
)


class CoinDCXConnectRequest(BaseModel):
    api_key: str = Field(min_length=8, max_length=256)
    api_secret: str = Field(min_length=8, max_length=256)
    attest_ip_bound: bool = False
    attest_no_withdraw: bool = False
    attest_trading_consent: bool = False


class VenueUpdateRequest(BaseModel):
    venue: Optional[str] = None
    margin_currency: Optional[str] = None
    leverage: Optional[float] = None


class SelfTestRequest(BaseModel):
    uid: str = Field(min_length=4, max_length=128)
    symbol: str = Field(default="DOGEUSDT", max_length=40)
    margin_currency: str = Field(default="USDT", max_length=8)


def _engine_ip() -> Optional[str]:
    return os.environ.get("ENGINE_VPS_PUBLIC_IP") or None


def _uid(identity: Any) -> Optional[str]:
    uid = getattr(identity, "firebase_uid", None)
    return str(uid) if uid else None


def _user_id(identity: Any) -> Optional[int]:
    uid = getattr(identity, "user_id", None)
    try:
        return int(uid) if uid is not None else None
    except (TypeError, ValueError):
        return None


def _read_json(path: str) -> Optional[dict]:
    try:
        with open(path) as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def _key_status(uid: str) -> dict:
    """``{readable, connected, attested, ...}`` — never guesses."""
    from src.venues.coindcx import keystore as _keys

    try:
        st = _keys.get_status(uid)
    except Exception as exc:  # noqa: BLE001
        log.warning("coindcx status read failed uid={}: {}", uid, type(exc).__name__)
        return {"readable": False, "connected": None, "attested": None}
    if st is None:
        return {"readable": True, "connected": False, "attested": False}
    out = {"readable": True, "connected": True, **st}
    for k in ("connected_at", "last_validated_at"):
        v = out.get(k)
        if isinstance(v, datetime):
            out[k] = v.isoformat()
    return out


def _live_positions(uid: str) -> Optional[int]:
    from src.venues.coindcx import positions as _pos

    try:
        return sum(1 for p in _pos.get_store().for_user(uid, limit=200) if p.live)
    except Exception:  # noqa: BLE001
        return None


def register(
    app: FastAPI,
    *,
    auth: Callable,
    identity_dep: Callable,
    owner_required: Callable,
    engine: Any = None,
) -> None:
    """Register every CoinDCX route (idempotent per ``build_app``)."""

    @app.get("/api/coindcx/info", tags=["coindcx"], dependencies=[Depends(auth)])
    async def coindcx_info() -> dict:
        from config import COINDCX_EXECUTION_ENABLED
        from src.api import user_overrides as _uo
        from src.venues.coindcx import instruments as _inst
        from src.venues.coindcx import keystore as _keys

        try:
            inr = await _inst.get_registry().inr_per_usdt()
        except Exception:  # noqa: BLE001
            inr = None
        return {
            "engine_ip": _engine_ip(),
            "attestation_version": _keys.ATTESTATION_VERSION,
            "attestation_items": list(ATTESTATION_ITEMS),
            "margin_currencies": list(_uo.COINDCX_MARGIN_VALUES),
            "margin_default": _uo.COINDCX_MARGIN_DEFAULT,
            "leverage_min": _uo.COINDCX_LEVERAGE_MIN,
            "leverage_max": _uo.COINDCX_LEVERAGE_MAX,
            "leverage_default": _uo.COINDCX_LEVERAGE_DEFAULT,
            "inr_per_usdt": inr,
            "execution_enabled": bool(COINDCX_EXECUTION_ENABLED),
            "exit_profile": (
                "On CoinDCX every trade uses one exit: the whole position closes "
                "at TP1 or at the stop, placed on CoinDCX the moment the entry "
                "fills. Pre-TP partials, TP2/TP3 and trailing exits are "
                "Binance-only."
            ),
        }

    @app.post("/api/coindcx/connect", tags=["coindcx"], dependencies=[Depends(auth)])
    async def coindcx_connect(
        request: Request, body: CoinDCXConnectRequest, identity: Any = Depends(identity_dep),
    ) -> dict:
        from src.security import envelope_crypto, geoblock, kms_client
        from src.venues.coindcx import connect_validator as _cv
        from src.venues.coindcx import keystore as _keys

        try:
            geoblock.assert_country_allowed(dict(request.headers))
        except geoblock.GeoblockError as exc:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail=exc.user_message)
        uid = _uid(identity)
        if uid is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                                detail="CoinDCX connect requires Lumin sign-in.")
        if not (body.attest_ip_bound and body.attest_no_withdraw and body.attest_trading_consent):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Confirm every item on the safety checklist to connect.",
                headers={"X-Connect-Error-Code": "ATTESTATION_REQUIRED"},
            )
        engine_ip = _engine_ip()
        if not engine_ip:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Server misconfiguration — ENGINE_VPS_PUBLIC_IP unset.")
        if not kms_client.is_initialised() or not _keys.is_initialised():
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Server misconfiguration — key storage not ready.")
        try:
            validation = await _cv.validate_coindcx_key(
                api_key=body.api_key.strip(), api_secret=body.api_secret.strip(),
            )
        except _cv.CoinDCXConnectError as exc:
            code = (status.HTTP_503_SERVICE_UNAVAILABLE
                    if isinstance(exc, _cv.CoinDCXUnreachableError)
                    else status.HTTP_400_BAD_REQUEST)
            raise HTTPException(
                code, detail=exc.user_message,
                headers={"X-Connect-Error-Code": exc.code, "X-Engine-VPS-IP": engine_ip},
            )
        plaintext_dek = envelope_crypto.generate_dek()
        try:
            blob = envelope_crypto.encrypt_secret(
                plaintext_dek, body.api_secret.strip().encode("utf-8"),
            )
            wrapped = await asyncio.to_thread(kms_client.get_client().encrypt, plaintext_dek)
            await asyncio.to_thread(
                _keys.put_key_blob, uid,
                encrypted_secret=blob.raw, encrypted_dek=wrapped,
                api_key_full=body.api_key.strip(),
                attestation={
                    "ip_bound": True, "no_withdraw": True, "trading_consent": True,
                    "version": _keys.ATTESTATION_VERSION, "engine_ip": engine_ip,
                    "attested_at": datetime.now(timezone.utc).isoformat(),
                    "items": list(ATTESTATION_ITEMS),
                },
            )
        except Exception:
            log.exception("coindcx_connect: encrypt+persist failed uid={}", uid)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Validated your key but could not store it securely. "
                                       "Please try again.")
        finally:
            del plaintext_dek
        log.info("coindcx_connect ok uid={} key_prefix={}", uid, body.api_key[:8])
        return {
            "ok": True,
            "key_public_id_first8": body.api_key.strip()[:8],
            "futures_wallet_ok": validation.futures_wallet_ok,
            "balances": validation.balances,
        }

    @app.get("/api/coindcx/connect/status", tags=["coindcx"], dependencies=[Depends(auth)])
    async def coindcx_status(identity: Any = Depends(identity_dep)) -> dict:
        uid = _uid(identity)
        if uid is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sign in required.")
        out = await asyncio.to_thread(_key_status, uid)
        out["engine_ip"] = _engine_ip()
        return out

    @app.delete("/api/coindcx/connect", tags=["coindcx"], dependencies=[Depends(auth)])
    async def coindcx_disconnect(identity: Any = Depends(identity_dep)) -> dict:
        from src.venues.coindcx import keystore as _keys

        uid = _uid(identity)
        if uid is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sign in required.")
        live = await asyncio.to_thread(_live_positions, uid)
        if live is None:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Could not check your open CoinDCX positions. Try again.")
        if live > 0:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Close your open CoinDCX positions first — without the key "
                       "we could not protect or close them.",
            )
        await asyncio.to_thread(_keys.delete_key_blob, uid)
        return {"ok": True}

    @app.get("/api/venue", tags=["coindcx"], dependencies=[Depends(auth)])
    async def get_venue(identity: Any = Depends(identity_dep)) -> dict:
        from config import COINDCX_EXECUTION_ENABLED
        from src.api import user_overrides as _uo
        from src.venues.coindcx import dispatch as _dcx

        uid = _uid(identity)
        if uid is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sign in required.")
        settings = await asyncio.to_thread(_uo.resolve_venue_settings_uid, uid)
        key = await asyncio.to_thread(_key_status, uid)
        allowed = _dcx._allowed_uids()
        return {
            **settings,
            "readable": settings.get("reason") == _uo.VENUE_REASON_OK
            or settings.get("reason") == _uo.VENUE_REASON_NO_USER,
            "coindcx": {
                **{k: key.get(k) for k in ("readable", "connected", "attested",
                                           "key_public_id_first8")},
                "execution_enabled": bool(COINDCX_EXECUTION_ENABLED),
                "allow_listed": (allowed is None) or (uid in allowed),
            },
        }

    @app.put("/api/venue", tags=["coindcx"], dependencies=[Depends(auth)])
    async def put_venue(body: VenueUpdateRequest, identity: Any = Depends(identity_dep)) -> dict:
        from src.api import user_overrides as _uo

        uid, user_id = _uid(identity), _user_id(identity)
        if uid is None or user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sign in required.")
        store = _uo.get_singleton()
        if store is None:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Settings store unavailable.")
        partial = body.model_dump(exclude_unset=True)
        if str(partial.get("venue") or "").lower() == "coindcx":
            key = await asyncio.to_thread(_key_status, uid)
            if key.get("readable") is not True:
                raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                    detail="Could not check your CoinDCX key. Try again.")
            if not (key.get("connected") and key.get("attested")):
                raise HTTPException(status.HTTP_409_CONFLICT,
                                    detail="Connect your CoinDCX API key before choosing CoinDCX.")
            # Choosing CoinDCX takes the user OFF the Binance fan-out.  While
            # CoinDCX execution is not live for them, that choice would leave
            # them trading on neither exchange without a word — refuse it.
            from config import COINDCX_EXECUTION_ENABLED
            from src.venues.coindcx import dispatch as _dcx

            allowed = _dcx._allowed_uids()
            if not COINDCX_EXECUTION_ENABLED or (allowed is not None and uid not in allowed):
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    detail="CoinDCX auto-trade is not open yet. Your key is saved; "
                           "you can switch as soon as it opens. Until then you keep "
                           "trading on Binance.",
                    headers={"X-Venue-Error-Code": "COINDCX_NOT_OPEN"},
                )
        try:
            await asyncio.to_thread(store.update_venue_settings, user_id, partial)
        except ValueError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))
        # Read back what is stored — never echo the request.
        return await get_venue(identity)

    @app.get("/api/coindcx/positions", tags=["coindcx"], dependencies=[Depends(auth)])
    async def coindcx_positions(identity: Any = Depends(identity_dep), limit: int = 50) -> dict:
        from src.venues.coindcx import positions as _pos

        uid = _uid(identity)
        if uid is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sign in required.")
        try:
            rows = await asyncio.to_thread(_pos.get_store().for_user, uid, limit=limit)
        except Exception as exc:  # noqa: BLE001
            log.warning("coindcx positions read failed: {}", exc)
            return {"readable": False, "positions": []}
        return {"readable": True, "positions": [p.to_api() for p in rows]}

    @app.post("/api/admin/coindcx/self-test", tags=["admin"],
              dependencies=[Depends(owner_required)])
    async def coindcx_self_test(body: SelfTestRequest) -> dict:
        request_id = uuid.uuid4().hex
        is_facade = type(engine).__name__ == "RedisEngineFacade"
        if is_facade:
            ok = await engine.enqueue_coindcx_self_test(
                request_id=request_id, uid=body.uid.strip(),
                symbol=body.symbol.strip().upper(),
                margin_currency=body.margin_currency.strip().upper(),
            )
            if not ok:
                raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                    detail="Engine bridge unavailable — try again.")
        else:
            from src.venues.coindcx import self_test as _st

            asyncio.create_task(_st.run(
                body.uid.strip(), symbol=body.symbol.strip().upper(),
                margin_currency=body.margin_currency.strip().upper(),
            ))
        log.info("coindcx self-test queued request_id={} uid={}", request_id, body.uid)
        return {"queued": True, "request_id": request_id}

    @app.get("/api/admin/coindcx/status", tags=["admin"],
             dependencies=[Depends(owner_required)])
    async def coindcx_admin_status() -> dict:
        from src.venues.coindcx import reconciler as _rec
        from src.venues.coindcx import self_test as _st

        return {
            "status": await asyncio.to_thread(_read_json, _rec.STATUS_PATH),
            "self_test": await asyncio.to_thread(_read_json, _st.REPORT_PATH),
        }
