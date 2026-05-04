"""FastAPI app + uvicorn launcher.

The app instance is built lazily by ``build_app(engine)`` so tests can
construct one against a stub engine without booting the runtime.  In
production, ``serve_api(engine)`` is awaited as a long-running asyncio
task spawned from ``Bootstrap.launch_runtime_tasks``.

Auth: when ``API_AUTH_TOKEN`` is set, every endpoint requires
``Authorization: Bearer <token>``.  When the var is empty, the API is
unauthenticated — fine for local development, never for production.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils import get_logger

from .schemas import (
    ActivityResponse,
    AgentsResponse,
    AutoModeChangeRequest,
    AutoModeChangeResponse,
    AutoModeStatus,
    HealthResponse,
    PositionsResponse,
    PulseSnapshot,
    SignalDetail,
    SignalsResponse,
)
from .snapshot import (
    build_activity,
    build_agents,
    build_auto_mode,
    build_positions,
    build_pulse,
    build_signals,
)

log = get_logger("api.server")

_API_VERSION = "0.0.1"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


_bearer = HTTPBearer(auto_error=False)


def _make_auth_dep(token: str):
    """Return a FastAPI dependency that enforces a static bearer token."""

    async def _verify(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    ) -> None:
        if not token:
            return  # auth disabled
        if credentials is None or credentials.credentials != token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid or missing bearer token",
            )

    return _verify


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def build_app(
    engine: Any,
    *,
    auth_token: str = "",
    cors_origins: Optional[List[str]] = None,
) -> FastAPI:
    """Build the FastAPI app bound to a live engine instance."""
    app = FastAPI(
        title="360 Crypto Eye API",
        version=_API_VERSION,
        description="Read-only HTTP adapter for the Lumin app.",
    )
    app.state.engine = engine
    app.state.boot_monotonic = time.monotonic()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    auth = _make_auth_dep(auth_token)

    # ---- Health (no auth — used by Docker/k8s probes) ----

    @app.get("/api/health", response_model=HealthResponse, tags=["meta"])
    async def health() -> HealthResponse:
        boot = getattr(engine, "_boot_time", 0.0) or 0.0
        uptime = time.monotonic() - boot if boot else 0.0
        return HealthResponse(uptime_seconds=max(0.0, uptime), version=_API_VERSION)

    # ---- Pulse ----

    @app.get(
        "/api/pulse",
        response_model=PulseSnapshot,
        tags=["pulse"],
        dependencies=[Depends(auth)],
    )
    async def pulse() -> PulseSnapshot:
        return build_pulse(engine)

    # ---- Signals ----

    @app.get(
        "/api/signals",
        response_model=SignalsResponse,
        tags=["signals"],
        dependencies=[Depends(auth)],
    )
    async def signals(
        status: str = Query("all", pattern="^(all|open|closed)$"),
        limit: int = Query(50, ge=1, le=500),
    ) -> SignalsResponse:
        items = build_signals(engine, status=status, limit=limit)
        return SignalsResponse(items=items, total=len(items))

    @app.get(
        "/api/signals/{signal_id}",
        response_model=SignalDetail,
        tags=["signals"],
        dependencies=[Depends(auth)],
    )
    async def signal_detail(signal_id: str) -> SignalDetail:
        # Search all known signals — small cost (≤500 history + active).
        items = build_signals(engine, status="all", limit=1000)
        for it in items:
            if it.signal_id == signal_id:
                return it
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"signal {signal_id!r} not found",
        )

    # ---- Positions ----

    @app.get(
        "/api/positions",
        response_model=PositionsResponse,
        tags=["positions"],
        dependencies=[Depends(auth)],
    )
    async def positions() -> PositionsResponse:
        items = build_positions(engine)
        return PositionsResponse(items=items, total=len(items))

    # ---- Activity ----

    @app.get(
        "/api/activity",
        response_model=ActivityResponse,
        tags=["activity"],
        dependencies=[Depends(auth)],
    )
    async def activity(
        limit: int = Query(50, ge=1, le=500),
    ) -> ActivityResponse:
        items = build_activity(engine, limit=limit)
        return ActivityResponse(items=items, total=len(items))

    # ---- Auto-mode ----

    @app.get(
        "/api/auto-mode",
        response_model=AutoModeStatus,
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def auto_mode_get() -> AutoModeStatus:
        return build_auto_mode(engine)

    @app.post(
        "/api/auto-mode",
        response_model=AutoModeChangeResponse,
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def auto_mode_set(req: AutoModeChangeRequest) -> AutoModeChangeResponse:
        ok, msg = engine.set_auto_execution_mode(req.mode)
        if not ok:
            # Surface the engine's reason as a 409 — the request was valid
            # but the engine refused (open positions, missing creds, etc.)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=msg,
            )
        return AutoModeChangeResponse(
            success=True,
            message=msg,
            mode=req.mode,
        )

    # ---- Agents ----

    @app.get(
        "/api/agents",
        response_model=AgentsResponse,
        tags=["agents"],
        dependencies=[Depends(auth)],
    )
    async def agents() -> AgentsResponse:
        items = build_agents(engine)
        return AgentsResponse(items=items, total=len(items))

    return app


# ---------------------------------------------------------------------------
# Server entry-point (used by Bootstrap)
# ---------------------------------------------------------------------------


async def serve_api(
    engine: Any,
    *,
    host: str,
    port: int,
    auth_token: str = "",
    cors_origins: Optional[List[str]] = None,
) -> None:
    """Run the API server forever.  Cancellation stops it cleanly."""
    import uvicorn  # imported lazily so optional dep stays optional

    app = build_app(engine, auth_token=auth_token, cors_origins=cors_origins)
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False,
        loop="asyncio",
    )
    server = uvicorn.Server(config)
    log.info("API server listening on http://{}:{}", host, port)
    try:
        await server.serve()
    except asyncio.CancelledError:
        log.info("API server cancelled — shutting down")
        server.should_exit = True
        raise
