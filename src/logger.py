"""Enhanced logging configuration using loguru.

Provides:
  - Rotating file logs (50 MB, 30-day retention)
  - Structured JSON output option (enabled via ``LOG_JSON=true`` in .env)
  - Log level from ``LOG_LEVEL`` env var
  - Separate error-only log file
  - ``get_recent_logs(n)`` helper for the ``/view_logs`` Telegram command

NOTE 2026-05-14 (PR #389 + this hotfix):
``src/utils.py`` ALSO calls ``_loguru_logger.remove()`` and adds its own
sinks (including the WS-trace sink for ``logs/ws_trace.log``).  In
production import order, ``src/logger.py._configure()`` runs AFTER
``src/utils.py``, so its bare ``remove()`` was silently wiping the
trace sink registered by utils.  Result: ``/ws_log`` Telegram replies
showed "exists but empty" because the file was opened during utils
init, then orphaned when this module's remove() killed the sink.

Fix: after the existing add() calls below, ALSO register the trace
sink here (importing helpers from src/utils so the filter logic stays
in one place).  And add the inverse-trace filter to the stderr +
engine sinks so per-second WS events don't flood the operator's main
log.

This is a hotfix; the proper unification (one configure module, not
two) is queued as separate cleanup work.
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
    """Admit only records that carry ``extra[ws_trace]=True``.

    Defined here (and duplicated in src/utils.py with the same logic)
    so both module paths can register the trace sink without one
    importing the other — avoids a circular-import risk at boot.
    """
    return bool(record["extra"].get("ws_trace"))


def _exclude_ws_trace_filter(record: Any) -> bool:
    """Reject ``extra[ws_trace]=True`` records on stderr + engine sinks.

    Without this, every ``stream_summary`` / ``first_data`` event would
    also print to the operator's main log — defeating the dedicated
    trace-file design.
    """
    return not record["extra"].get("ws_trace")


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def _configure() -> None:
    """Configure loguru sinks.  Called once at import time.

    Wipes any sinks registered by an earlier-loaded module (notably
    ``src/utils.py``) via ``_loguru_logger.remove()``, then re-installs
    a clean set including the WS-trace sink so it survives this
    module's wipe.
    """
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    _loguru_logger.remove()  # remove default handler

    # Console sink — excludes WS-trace records so they don't flood
    # stderr when the trace summary fires every 60 s.
    _loguru_logger.add(
        sys.stderr,
        format=_CONSOLE_FORMAT,
        level=LOG_LEVEL.upper(),
        filter=_exclude_ws_trace_filter,
    )

    # Rotating file sink (all levels, also excluding WS-trace).
    serialize = _LOG_JSON
    _loguru_logger.add(
        str(_LOG_FILE),
        rotation="50 MB",
        retention="30 days",
        format=_FILE_FORMAT,
        level="DEBUG",
        serialize=serialize,
        enqueue=True,
        filter=_exclude_ws_trace_filter,
    )

    # Separate error-only sink (also excludes WS-trace — errors there
    # would show up if we ever emit ws_trace.error(), but operators want
    # the error file to focus on engine-internal errors, not the
    # potentially-noisy WS-protocol-layer events).
    _loguru_logger.add(
        str(_ERROR_LOG_FILE),
        rotation="20 MB",
        retention="30 days",
        format=_FILE_FORMAT,
        level="ERROR",
        serialize=serialize,
        enqueue=True,
        filter=_exclude_ws_trace_filter,
    )

    # WS-trace sink — admits ONLY records with ``extra[ws_trace]=True``.
    # Re-registered here after _loguru_logger.remove() above so it
    # survives this module's wipe even when src/utils.py's earlier
    # add() got cleared.  Single-line format (no name column, since
    # all trace records are produced by the same logger).
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

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def get_logger(name: str) -> Any:
    """Return a loguru logger bound with *name* context."""
    return _loguru_logger.bind(name=name)


def get_recent_logs(n: int = 50) -> str:
    """Return the last *n* lines from the most recent engine log file.

    Used by the ``/view_logs`` Telegram command.  Returns an empty string
    if no log file exists yet.
    """
    log_files = sorted(_LOG_DIR.glob("engine_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not log_files:
        return ""
    try:
        with open(log_files[0], "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        return "".join(lines[-n:])
    except OSError:
        return ""
