"""CI guard: the isolated api container must init the Firestore subsystems
its own endpoints read directly.

Bug class (isolated-mode init gap). In isolated mode
(``API_PROCESS_ISOLATED=true``, live on the VPS) the api container runs
``src/api/main.py`` — a boot path SEPARATE from the engine's
``src/bootstrap.py``. Several Firestore-backed singletons are read
*directly in the api process* by request handlers, so they must be
initialised there too, sharing the keystore's Firestore client. When one
is missed the endpoint silently degrades to its "not initialised" empty
value while the engine container is happily writing to the same Firestore
collection — an all-green-but-empty failure that's invisible without VPS
log access. This family has bitten repeatedly:

* KMS connect-flow init (#736)
* pairs-snapshot allowlist (runtime-status "Watching 0 symbols")
* dispatch_log (2026-07-18): auto-trades executing on Binance, Recent
  Activity showing "NO TRADES YET" because ``dispatch_log._db`` was None in
  the api process → ``list_recent_events`` short-circuited to ``[]``.

The runtime defense is the endpoints' soft-fail (they return empty rather
than 500); THIS test is the build-time defense — it pins that every such
subsystem's init call is present in ``src/api/main.py`` so a future edit
can't drop one and reopen the gap.

If this fails on new code: you added a request handler that reads a
Firestore singleton directly in the api process. Add its ``init_*`` call to
the keystore-init block in ``src/api/main.py`` (sharing ``_fk._db``), then
add its init symbol to ``_REQUIRED_API_CONTAINER_INITS`` below.
"""
from __future__ import annotations

import pathlib

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_API_MAIN = _ROOT / "src" / "api" / "main.py"

# Init calls the isolated api container MUST make because a request handler
# in this process reads the corresponding Firestore-backed singleton
# directly (not via the Redis engine facade).
_REQUIRED_API_CONTAINER_INITS = (
    # binance_key_connected (runtime-status / connect-status)
    "init_keystore",
    # engine-wide enable + per-user disable flags (runtime-status)
    "init_kill_switch",
    # Trade-tab Recent Activity feed (GET /api/auto-trade/recent-events)
    "init_dispatch_log",
)


def test_api_container_inits_directly_read_firestore_subsystems() -> None:
    source = _API_MAIN.read_text(encoding="utf-8")
    missing = [name for name in _REQUIRED_API_CONTAINER_INITS if name not in source]
    assert not missing, (
        "src/api/main.py is missing Firestore init call(s) "
        f"{missing} — the isolated api container reads these subsystems "
        "directly, so without init the matching endpoint returns an empty/"
        "default value while the engine container writes real data (see this "
        "file's docstring for the isolated-mode init-gap bug class)."
    )
