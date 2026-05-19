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
        # Print BOTH the message AND the full traceback so a
        # misconfigured operator setup (missing env vars, bad SA JSON
        # path, no KMS IAM, socket-bind blocked by AppArmor, etc.)
        # surfaces enough detail in systemd's / docker-compose's
        # journal to actually diagnose, not just a one-line "failed
        # to start" with the error class swallowed.
        import traceback

        print(f"signing service failed to start: {exc!r}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
