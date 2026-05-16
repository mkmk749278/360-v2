"""Loguru sink configuration — single source of truth for the engine.

All loguru sinks (stderr, rotating engine log, error-only log, dedicated
WS-trace log) are registered here at import time.  No other module
should call ``_loguru_logger.remove()`` or ``add()`` — see "History"
below for why.

Public surface:

  - ``get_loguru_logger()`` — the bare configured loguru logger.
    Application code should NOT call this directly; use
    ``src.utils.get_logger(name)``, which wraps the loguru logger in
    a ``%``/``{}``-tolerant bridge.
  - ``get_ws_trace_logger()`` — bound logger for WS-trace events.
    Records carry ``extra[ws_trace]=True`` so they are admitted to the
    dedicated trace file and excluded from the operator-visible sinks.
  - ``get_recent_logs(n)`` — last ``n`` lines of the most recent
    rotating engine log file, for the ``/view_logs`` Telegram command.

Tunables (env-overridable):

  - ``LOG_DIR``     — directory for ``engine_*.log`` and
                      ``engine_errors.log`` (default ``logs``).
  - ``LOG_JSON``    — if truthy, file sinks emit serialised JSON.
  - ``LOG_LEVEL``   — stderr threshold (file sink is always DEBUG).

History:

  Until 2026-05-14, sink configuration lived in BOTH ``src/utils.py``
  and a private ``_configure()`` here.  Each module called
  ``_loguru_logger.remove()`` then ``add(...)``; whichever ran last
  won.  Production import order ran utils first, then this module via
  ``src.commands.engine``, so the second ``remove()`` silently wiped
  the WS-trace sink registered by utils — ``/ws_log`` Telegram replies
  came back "exists but empty".  PR #389 + a follow-up hotfix worked
  around it by re-registering the trace sink here after the
  ``remove()``.  This module is now the proper unification: utils no
  longer touches sinks and imports its loguru handles from here.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from loguru import logger as _loguru_logger

from config import (
    LOG_LEVEL,
    WS_TRACE_LOG_PATH,
    WS_TRACE_LOG_RETENTION,
    WS_TRACE_LOG_ROTATION,
)

# ---------------------------------------------------------------------------
# Configuration constants (override via environment variables)
# ---------------------------------------------------------------------------
_LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
_LOG_JSON: bool = os.getenv("LOG_JSON", "false").lower() in ("1", "true", "yes")
_LOG_FILE = _LOG_DIR / "engine_{time}.log"
_ERROR_LOG_FILE = _LOG_DIR / "engine_errors.log"

_CONSOLE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | {extra[name]:<24} | {level:<7} | {message}"
)
_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | {extra[name]:<24} | {level:<7} | {message}"
)
_WS_TRACE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS!UTC} | {message}"


def _ws_trace_filter(record: Any) -> bool:
    """Admit only records that carry ``extra[ws_trace]=True``."""
    return bool(record["extra"].get("ws_trace"))


def _exclude_ws_trace_filter(record: Any) -> bool:
    """Reject ``extra[ws_trace]=True`` records on operator-visible sinks.

    Without this, every ``stream_summary`` / ``first_data`` event would
    flood the operator's main log, defeating the dedicated trace-file
    design.
    """
    return not record["extra"].get("ws_trace")


# ---------------------------------------------------------------------------
# Bootstrap — runs once at module import
# ---------------------------------------------------------------------------

def _configure() -> None:
    """Register all loguru sinks for the engine.

    Called exactly once at module import.  Wipes loguru's default
    stderr handler, then installs:

      * stderr console sink (LOG_LEVEL threshold, excludes WS-trace)
      * rotating engine log file (DEBUG, 50 MB / 30 days, excludes WS-trace)
      * rotating error-only log file (ERROR, 20 MB / 30 days, excludes WS-trace)
      * dedicated WS-trace log file (admits ONLY WS-trace records)
    """
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    _loguru_logger.remove()

    _loguru_logger.add(
        sys.stderr,
        format=_CONSOLE_FORMAT,
        level=LOG_LEVEL.upper(),
        filter=_exclude_ws_trace_filter,
    )

    _loguru_logger.add(
        str(_LOG_FILE),
        rotation="50 MB",
        retention="30 days",
        format=_FILE_FORMAT,
        level="DEBUG",
        serialize=_LOG_JSON,
        enqueue=True,
        filter=_exclude_ws_trace_filter,
    )

    _loguru_logger.add(
        str(_ERROR_LOG_FILE),
        rotation="20 MB",
        retention="30 days",
        format=_FILE_FORMAT,
        level="ERROR",
        serialize=_LOG_JSON,
        enqueue=True,
        filter=_exclude_ws_trace_filter,
    )

    try:
        os.makedirs(os.path.dirname(WS_TRACE_LOG_PATH) or ".", exist_ok=True)
    except OSError:
        pass

    _loguru_logger.add(
        WS_TRACE_LOG_PATH,
        rotation=WS_TRACE_LOG_ROTATION,
        retention=WS_TRACE_LOG_RETENTION,
        format=_WS_TRACE_FORMAT,
        level="INFO",
        filter=_ws_trace_filter,
        enqueue=False,
    )


_configure()


# Bound logger that all WS-trace events route through.  Records carry
# ``extra[ws_trace]=True`` so the trace-file sink admits them and the
# operator-visible sinks reject them.
_ws_trace_logger = _loguru_logger.bind(ws_trace=True, name="ws_trace")


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_loguru_logger() -> Any:
    """Return the bare configured loguru logger.

    Internal helper for ``src.utils.get_logger`` — application code
    should use ``src.utils.get_logger(name)`` (the formatting bridge).
    """
    return _loguru_logger


def get_ws_trace_logger() -> Any:
    """Return the loguru logger bound for WS-trace events.

    Callers emit structured ``<WS:LABEL> event_name k=v ...`` records via
    standard ``info()`` / ``warning()`` calls.  Records are routed by
    the ``_ws_trace_filter`` sink to the dedicated file and excluded
    from stderr / engine log.  See ``src/websocket_manager.py`` for
    the canonical use sites.
    """
    return _ws_trace_logger


def get_recent_logs(n: int = 50) -> str:
    """Return the last *n* lines from the most recent engine log file.

    Used by the ``/view_logs`` Telegram command.  Returns an empty
    string if no log file exists yet, or on I/O error.
    """
    log_files = sorted(
        _LOG_DIR.glob("engine_*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not log_files:
        return ""
    try:
        with open(log_files[0], "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        return "".join(lines[-n:])
    except OSError:
        return ""
