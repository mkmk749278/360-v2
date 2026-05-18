"""``python -m src.security.signing_service`` — production entry point.

Invoked from systemd or the equivalent process supervisor.  Reads
config from env (same GCP_KMS_* + FIREBASE_SERVICE_ACCOUNT_PATH env
vars the engine uses), initialises KMS + Firestore, then runs the
Unix-socket server until SIGTERM / SIGINT.

Operator setup details are in ``docs/server-side-execution-setup.md``
§5 (added in the PR that wires the production deployment).
"""

from __future__ import annotations

import asyncio
import sys

from .server import run


def main() -> int:
    try:
        asyncio.run(run())
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as exc:  # pragma: no cover - top-level guard
        # Last-resort traceback printer so a misconfigured operator
        # setup (missing env vars, bad SA JSON path, no KMS IAM)
        # surfaces a clear error in systemd's journal rather than
        # silently restarting in a loop.
        print(f"signing service failed to start: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
