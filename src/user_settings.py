"""User-controllable settings persisted to disk.

The Lumin app's settings screens write to this module via the API
(``/api/settings/...``); the engine reads through the public accessors
on every relevant decision tick.  The first concern wired is the
``pretp`` page (regime allowlist, thresholds, setup allowlist); other
pages will plug into the same module incrementally.

Storage:
- Single JSON file at ``DEFAULT_PATH`` (override via ``USER_SETTINGS_PATH``
  env var per B8).
- Atomic writes (tmp + ``os.replace``) so a partial flush is never visible.
- Hot-reload: each accessor stat()s the file and reloads when ``mtime``
  changes — so an API write on one process is observed by the engine
  loop without restart.

Defaults:
- Every accessor falls back to the engine's existing config-constant
  default when the user has not set the corresponding key.  Behaviour
  for unconfigured users is therefore identical to the pre-wiring
  state.

Thread safety:
- Reads use a file-mtime check and an in-memory dict.  Writes use
  read-modify-write under a lock.  The engine is asyncio-single-threaded;
  the API server reads/writes from the same event loop via FastAPI.
  The lock guards against the API server's thread-pool executor that
  FastAPI uses for sync route handlers.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, FrozenSet, Optional

from .utils import get_logger

log = get_logger(__name__)


DEFAULT_PATH = "data/user_settings.json"


# ---------------------------------------------------------------------------
# Pre-TP defaults (mirror config/__init__.py — single source of truth lives
# there; we lazy-import to avoid a hard cycle and to keep this module
# usable from tests that monkeypatch config).
# ---------------------------------------------------------------------------

_PRETP_KEYS = frozenset({
    "enabled",
    "regime_allowlist",
    "setup_allowlist",
    "threshold_pct",
    "atr_multiplier",
    "fee_floor_pct",
    "min_age_sec",
    "max_age_sec",
})

# Valid regime tokens accepted from the API.  The 5 backend regime labels
# collapse into 3 UI buckets (Trending / Ranging / Choppy) — the API
# accepts either form and normalises to the backend set.
_REGIME_UI_TO_BACKEND: Dict[str, FrozenSet[str]] = {
    "TRENDING": frozenset({"TRENDING_UP", "TRENDING_DOWN"}),
    "RANGING": frozenset({"RANGING"}),
    "CHOPPY": frozenset({"VOLATILE", "QUIET"}),
}
_VALID_BACKEND_REGIMES: FrozenSet[str] = frozenset({
    "TRENDING_UP", "TRENDING_DOWN", "RANGING", "VOLATILE", "QUIET",
})


def _resolve_path(path: Optional[str]) -> Path:
    if path:
        return Path(path)
    env_path = os.environ.get("USER_SETTINGS_PATH", "").strip()
    return Path(env_path) if env_path else Path(DEFAULT_PATH)


class _Store:
    """Thread-safe in-memory cache backed by an mtime-watched JSON file."""

    def __init__(self, path: Optional[str] = None) -> None:
        self._path: Path = _resolve_path(path)
        self._lock = threading.RLock()
        self._cache: Dict[str, Any] = {}
        self._cached_mtime: Optional[float] = None

    def _load_locked(self) -> Dict[str, Any]:
        if not self._path.exists():
            self._cache = {}
            self._cached_mtime = None
            return self._cache
        try:
            current_mtime = self._path.stat().st_mtime
        except OSError as exc:
            log.warning("user_settings: stat(%s) failed (%s)", self._path, exc)
            return self._cache
        if self._cached_mtime is not None and current_mtime == self._cached_mtime:
            return self._cache
        try:
            with self._path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("user_settings: load(%s) failed (%s)", self._path, exc)
            return self._cache
        if not isinstance(raw, dict):
            log.warning("user_settings: %s is not a dict; ignoring", self._path)
            return self._cache
        self._cache = raw
        self._cached_mtime = current_mtime
        return self._cache

    def _save_locked(self, payload: Dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(prefix=".user_settings_", dir=str(self._path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, separators=(",", ":"), sort_keys=True)
            os.replace(tmp_path, self._path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        self._cache = payload
        try:
            self._cached_mtime = self._path.stat().st_mtime
        except OSError:
            self._cached_mtime = None

    def get(self, key: str) -> Any:
        with self._lock:
            return self._load_locked().get(key)

    def update(self, key: str, value: Dict[str, Any]) -> Dict[str, Any]:
        """Merge ``value`` into ``payload[key]`` and persist atomically."""
        with self._lock:
            current = dict(self._load_locked())
            existing = dict(current.get(key) or {})
            existing.update(value)
            current[key] = existing
            self._save_locked(current)
            return existing


# Module-level singleton.  Tests can construct their own ``_Store`` against
# a tmp path and monkeypatch ``_STORE`` to swap it in.
_STORE: _Store = _Store()


def reset_for_test(path: Optional[str] = None) -> None:
    """Replace the module singleton — for tests that need an isolated store.

    Tests should call this with a tmp path during setup and reset to the
    default afterwards (or use monkeypatch).
    """
    global _STORE
    _STORE = _Store(path=path)


# ---------------------------------------------------------------------------
# Pre-TP accessors
# ---------------------------------------------------------------------------


def _normalise_regime_input(items: Any) -> FrozenSet[str]:
    """Convert either UI tokens (TRENDING / RANGING / CHOPPY) or backend
    tokens (TRENDING_UP / ...) into the backend regime set."""
    if items is None:
        return frozenset()
    if isinstance(items, str):
        items = [items]
    out: set = set()
    for raw in items:
        if not isinstance(raw, str):
            continue
        tok = raw.strip().upper()
        if not tok:
            continue
        if tok in _REGIME_UI_TO_BACKEND:
            out.update(_REGIME_UI_TO_BACKEND[tok])
        elif tok in _VALID_BACKEND_REGIMES:
            out.add(tok)
        else:
            log.warning("user_settings: unknown regime token %r — ignoring", raw)
    return frozenset(out)


def _coerce_pretp_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Validate + normalise an inbound Pre-TP settings payload.

    Unknown keys are dropped.  Type-mismatched values are dropped with a
    warning.  Returns the cleaned dict ready to merge into the store.
    """
    out: Dict[str, Any] = {}
    for key, value in raw.items():
        if key not in _PRETP_KEYS:
            log.warning("user_settings.pretp: dropping unknown key %r", key)
            continue
        if key == "enabled":
            if isinstance(value, bool):
                out[key] = value
        elif key in ("threshold_pct", "atr_multiplier", "fee_floor_pct"):
            if isinstance(value, (int, float)) and value >= 0:
                out[key] = float(value)
        elif key in ("min_age_sec", "max_age_sec"):
            if isinstance(value, int) and value >= 0:
                out[key] = int(value)
        elif key == "regime_allowlist":
            normalised = _normalise_regime_input(value)
            out[key] = sorted(normalised)
        elif key == "setup_allowlist":
            if isinstance(value, list):
                out[key] = sorted(
                    s.strip().upper() for s in value
                    if isinstance(s, str) and s.strip()
                )
    return out


def get_pretp() -> Dict[str, Any]:
    """Return the user-set Pre-TP settings dict (may be partial / empty).

    Defaults are NOT filled in here — the accessors below resolve defaults
    from the engine's config constants on read.  Callers that need a
    "fully-resolved view" (e.g. the API endpoint returning the current
    state to the app) should compose this with ``pretp_*`` accessors.
    """
    raw = _STORE.get("pretp")
    return dict(raw) if isinstance(raw, dict) else {}


def update_pretp(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Merge a partial Pre-TP settings payload into the store."""
    cleaned = _coerce_pretp_payload(payload)
    return _STORE.update("pretp", cleaned)


def pretp_regime_allowlist() -> FrozenSet[str]:
    """Engine accessor: regimes in which Pre-TP is allowed to fire.

    Returns the user-set value if present, else falls back to the
    config default (``PRE_TP_REGIME_ALLOWLIST``).  All values are upper-
    cased backend regime tokens (TRENDING_UP / TRENDING_DOWN / RANGING /
    VOLATILE / QUIET).
    """
    raw = _STORE.get("pretp")
    if isinstance(raw, dict):
        configured = raw.get("regime_allowlist")
        if isinstance(configured, list):
            return _normalise_regime_input(configured)
    from config import PRE_TP_REGIME_ALLOWLIST
    return frozenset(PRE_TP_REGIME_ALLOWLIST)
