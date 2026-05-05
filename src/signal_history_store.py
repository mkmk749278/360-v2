"""Persistence layer for ``_signal_history``.

The closed-signal feed shown in the Lumin app and used by API/`commands`
must survive engine restarts.  Without persistence, every redeploy
(`git push origin main` → ~45s GH-Actions deploy → fresh container)
wipes the in-memory list and the app reads as a freshly-booted engine
with zero history — which is misleading to subscribers and breaks B3
("SL hits posted honestly — same visual weight as TP hits") at the
app layer.

Storage:
- Single JSON array on disk at ``DEFAULT_PATH`` (override via
  ``SIGNAL_HISTORY_PATH`` env var per B8).
- Cap mirrors the in-memory cap (``HISTORY_CAP``).
- Atomic writes via ``tmp + os.replace``: a partial file is never
  visible to readers, so a crashed flush at worst loses the most
  recent terminal-state transition.
- Best-effort load: malformed or schema-drifted records are skipped
  with a warning, never crash boot.

Round-trip:
- ``Signal`` is a stdlib dataclass; ``vars(sig)`` gives a shallow dict.
- ``datetime`` fields are emitted as ISO-8601 strings; the ``Direction``
  enum (a ``str, Enum`` subclass) emits its string value.
- All other fields are JSON-native (numbers, strings, bools, dicts of
  the same).  Nested types like ``order_book`` are dicts of lists of
  numbers — already JSON-safe.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List, Optional

from .channels.base import Signal
from .smc import Direction
from .utils import get_logger

log = get_logger(__name__)


DEFAULT_PATH = "data/signal_history.json"
HISTORY_CAP = 500


# Datetime fields on the Signal dataclass — needed for ISO round-trip.
_DATETIME_FIELDS = (
    "timestamp",
    "dispatch_timestamp",
    "first_sl_touch_timestamp",
    "first_tp_touch_timestamp",
    "terminal_outcome_timestamp",
    "pre_tp_timestamp",
    "dca_timestamp",
)


def _signal_to_dict(sig: Signal) -> dict:
    out: dict = {}
    for k, v in vars(sig).items():
        if isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, Direction):
            out[k] = v.value
        elif v is None or isinstance(v, (str, int, float, bool, list, dict)):
            out[k] = v
        else:
            out[k] = str(v)
    return out


def _dict_to_signal(record: dict) -> Optional[Signal]:
    payload = dict(record)
    try:
        for k in _DATETIME_FIELDS:
            v = payload.get(k)
            if isinstance(v, str):
                payload[k] = datetime.fromisoformat(v)
        direction = payload.get("direction")
        if isinstance(direction, str):
            payload["direction"] = Direction(direction)
        return Signal(**payload)
    except (TypeError, ValueError, KeyError) as e:
        log.warning(f"signal_history_store: skipping malformed record ({e})")
        return None


def _resolve_path(path: Optional[str]) -> Path:
    if path:
        return Path(path)
    env_path = os.environ.get("SIGNAL_HISTORY_PATH", "").strip()
    return Path(env_path) if env_path else Path(DEFAULT_PATH)


def load_history(path: Optional[str] = None) -> List[Signal]:
    p = _resolve_path(path)
    if not p.exists():
        return []
    try:
        with p.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        log.warning(f"signal_history_store: load from {p} failed ({e})")
        return []
    if not isinstance(raw, list):
        log.warning(f"signal_history_store: {p} is not a list; ignoring")
        return []
    out: List[Signal] = []
    for record in raw[-HISTORY_CAP:]:
        if not isinstance(record, dict):
            continue
        sig = _dict_to_signal(record)
        if sig is not None:
            out.append(sig)
    log.info(f"signal_history_store: loaded {len(out)} records from {p}")
    return out


def save_history(history: Iterable[Any], path: Optional[str] = None) -> None:
    p = _resolve_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    capped = [s for s in list(history)[-HISTORY_CAP:] if s is not None]
    serializable: List[dict] = []
    for s in capped:
        try:
            serializable.append(_signal_to_dict(s))
        except Exception as e:
            log.warning(f"signal_history_store: drop unserialisable signal ({e})")
    fd, tmp_path = tempfile.mkstemp(prefix=".sig_hist_", dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(serializable, f, separators=(",", ":"))
        os.replace(tmp_path, p)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
