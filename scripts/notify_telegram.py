#!/usr/bin/env python3
"""Owner paging via Telegram — the phone-level alert channel (audit §9.3-2).

Telegram is operational in-region again (owner confirmation, 2026-07-10),
so it replaces GitHub issues as the *minutes-level* page for money-path
invariants; the issues remain as the durable morning-review record.

Stdlib-only on purpose: this runs inside the engine/watchdog containers,
piped over ``docker exec`` from workflows, and on the bare VPS host —
none of which are guaranteed a requests/httpx install.

Contract (mirrors src/execution/telegram_alerts.py):

* Never raises.  A failed page must not break the caller — worst case the
  owner misses one page and the GitHub-issue path still fires.
* Never logs, prints, or embeds the bot token in an error message.  The
  token is part of the request URL, so exceptions are reported by class
  name only.

Env:

* ``TELEGRAM_BOT_TOKEN``      — the engine's existing bot.
* ``ALERT_TELEGRAM_CHAT_ID``  — dedicated alert chat (optional).
* ``TELEGRAM_ADMIN_CHAT_ID``  — fallback chat (the engine admin chat).

CLI::

    python scripts/notify_telegram.py "message text"
    echo "message" | python scripts/notify_telegram.py -
    python scripts/notify_telegram.py --strict "message"   # exit 1 on failure
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

_TELEGRAM_MESSAGE_LIMIT = 4096
_DEFAULT_TIMEOUT_SEC = 10.0


def _alert_chat_id() -> str:
    """Dedicated alert chat if configured, else the engine admin chat."""
    return (
        os.environ.get("ALERT_TELEGRAM_CHAT_ID", "").strip()
        or os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "").strip()
    )


def is_configured() -> bool:
    return bool(os.environ.get("TELEGRAM_BOT_TOKEN", "").strip() and _alert_chat_id())


def build_payload(text: str, chat_id: str) -> bytes:
    """JSON body for sendMessage — split out for tests (no network)."""
    if len(text) > _TELEGRAM_MESSAGE_LIMIT:
        text = text[: _TELEGRAM_MESSAGE_LIMIT - 15] + "\n…[truncated]"
    return json.dumps(
        {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    ).encode("utf-8")


def send_telegram(text: str, *, timeout: float = _DEFAULT_TIMEOUT_SEC) -> bool:
    """Send ``text`` to the alert chat.  Returns True on success.

    Never raises; never surfaces the token (it is embedded in the URL, so
    failures are reported by exception class only).
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = _alert_chat_id()
    if not token or not chat_id:
        print("notify_telegram: not configured (missing token or chat id); skipped")
        return False
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=build_payload(text, chat_id),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ok = 200 <= resp.status < 300
            if not ok:
                print(f"notify_telegram: send failed (HTTP {resp.status})")
            return ok
    except urllib.error.HTTPError as exc:  # has a status but no token in str(exc.code)
        print(f"notify_telegram: send failed (HTTP {exc.code})")
        return False
    except Exception as exc:  # noqa: BLE001 — alert path must never raise
        print(f"notify_telegram: send failed ({type(exc).__name__})")
        return False


def _main(argv: list[str]) -> int:
    strict = "--strict" in argv
    args = [a for a in argv if a != "--strict"]
    if not args:
        print("usage: notify_telegram.py [--strict] <message | ->", file=sys.stderr)
        return 2
    text = sys.stdin.read() if args[0] == "-" else " ".join(args)
    text = text.strip()
    if not text:
        print("notify_telegram: empty message; nothing sent")
        return 1 if strict else 0
    ok = send_telegram(text)
    return 0 if ok or not strict else 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
