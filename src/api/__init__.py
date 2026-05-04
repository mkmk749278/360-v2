"""FastAPI service exposing engine state to the Lumin Android app.

Read-only HTTP adapter that runs alongside the engine inside the same
asyncio event loop.  No duplicate state — every endpoint reads directly
from the live ``Engine`` instance via :mod:`src.api.snapshot`.

Activation is opt-in via ``API_ENABLED=true`` in the env so an existing
production deploy doesn't unexpectedly start listening on a port.
"""

from .server import serve_api

__all__ = ["serve_api"]
