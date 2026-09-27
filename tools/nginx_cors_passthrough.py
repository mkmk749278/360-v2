#!/usr/bin/env python3
"""Stop nginx answering CORS preflight for the Lumin API — on the live box.

Why this exists (owner, 2026-09-27).  Choosing CoinDCX in the web app came
back "no reply arrived in time" every time, even after ops opened CoinDCX to
every user.  The engine never saw the request.  ``tools/setup-vps-api.sh``
had written an nginx block that answered every ``OPTIONS`` itself::

    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        ...
        return 204;
    }

so the browser was told PUT and DELETE are not allowed, and refused to send
``PUT /api/venue`` (platform, margin, leverage) and ``DELETE
/api/coindcx/connect`` / Binance key removal.  FastAPI's CORSMiddleware
already allowed both (#1079 even made its errors CORS-safe) — it was simply
never reached.  Measured from outside: the preflight came back ``204`` with
``GET, POST, OPTIONS``, where FastAPI answers ``200`` and lists PUT/DELETE.

The setup script ran once, by hand, and no deploy ever re-applied nginx, so
fixing the script alone changes nothing on the running box.  This tool is the
deploy-time half: it removes that block from the live site file, idempotently.

Safety (the whole API sits behind this file):

* only an ``if ($request_method = 'OPTIONS') { ... }`` block that sets
  ``Access-Control-Allow-Methods`` is removed — nothing else is touched;
* a timestamped backup is written first;
* ``nginx -t`` must pass, or the backup is restored and nginx is NOT reloaded
  — a broken edit can never take the API down;
* ``reload``, never ``restart``: in-flight requests finish on the old workers.

Exit codes: 0 = changed or already clean or nothing to do; 1 = the edit was
refused by ``nginx -t`` and rolled back (the deploy warns, the API is as it
was).
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_SITE = "/etc/nginx/sites-available/lumin-api"

# The comment the setup script wrote above the block — removed with it so the
# live file does not keep describing behaviour it no longer has.
_OLD_COMMENT = re.compile(
    r"[ \t]*# CORS preflight for the Lumin app\.[^\n]*\n"
    r"(?:[ \t]*#[^\n]*\n)*?"
    r"(?=[ \t]*if \(\$request_method = 'OPTIONS'\))"
)

# ``if ($request_method = 'OPTIONS') { ... }`` — nginx ``if`` bodies here hold
# only directives, never a nested block, so "up to the first closing brace" is
# the whole body.  The match is refused unless it sets Allow-Methods.
_OPTIONS_BLOCK = re.compile(
    r"[ \t]*if \(\$request_method = 'OPTIONS'\) \{[^{}]*\}[ \t]*\n"
)


def strip_preflight(text: str) -> tuple[str, int]:
    """``(new_text, blocks_removed)``.  Pure, so it is unit-tested."""
    removed = 0

    def _drop(m: re.Match) -> str:
        nonlocal removed
        if "Access-Control-Allow-Methods" not in m.group(0):
            return m.group(0)
        removed += 1
        return ""

    text = _OLD_COMMENT.sub("", text)
    text = _OPTIONS_BLOCK.sub(_drop, text)
    return text, removed


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--site", default=DEFAULT_SITE)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    site = Path(args.site).resolve()  # sites-enabled is usually a symlink
    if not site.exists():
        print(f"nginx-cors: {site} not present — nothing to do")
        return 0
    original = site.read_text()
    new, removed = strip_preflight(original)
    if removed == 0:
        print(f"nginx-cors: {site} already passes preflight to the API")
        return 0
    if args.dry_run:
        print(f"nginx-cors: would remove {removed} preflight block(s) from {site}")
        return 0

    backup = site.with_name(f"{site.name}.bak-{time.strftime('%Y%m%dT%H%M%S')}")
    shutil.copy2(site, backup)
    site.write_text(new)
    test = _run(["nginx", "-t"])
    if test.returncode != 0:
        shutil.copy2(backup, site)
        print(f"nginx-cors: nginx -t refused the edit — restored {site} from "
              f"{backup}; nginx NOT reloaded.\n{test.stderr}")
        return 1
    reload_ = _run(["systemctl", "reload", "nginx"])
    if reload_.returncode != 0:
        reload_ = _run(["nginx", "-s", "reload"])
    print(f"nginx-cors: removed {removed} preflight block(s) from {site} "
          f"(backup {backup}); reload rc={reload_.returncode}")
    return 0 if reload_.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
