"""CoinDCX tests set the venue's LIVE switches, not config.

Since 2026-09-27 the master switch, the allow-list and open-to-all are
runtime tunables set from ops.  Patching ``config.COINDCX_*`` would change a
boot default the registry has already read — inert, and a test pinned on it
passes for an incidental reason (CLAUDE.md, the tunable-pin lesson).  This
patches ``src.runtime_tunables.get`` for the ``coindcx_*`` keys only and lets
every other key fall through to the real accessor.
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

#: The live values a test sees.  Reset before every test to the shipped
#: defaults: off, nobody allowed, not open.
DCX: Dict[str, Any] = {}

_DEFAULTS = {
    "coindcx_execution_enabled": False,
    "coindcx_execution_allowed_uids": "",
    "coindcx_open_to_all": False,
}


@pytest.fixture(autouse=True)
def _coindcx_live_switches(monkeypatch):
    from src import runtime_tunables as _rt

    DCX.clear()
    DCX.update(_DEFAULTS)
    real_get = _rt.get

    def _get(key: str) -> Any:
        if key in DCX:
            return DCX[key]
        return real_get(key)

    monkeypatch.setattr(_rt, "get", _get)
    yield DCX
