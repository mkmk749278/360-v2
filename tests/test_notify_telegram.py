"""scripts/notify_telegram.py — the phone-paging channel.

The module is stdlib-only and lives outside the package tree (it is piped
around by workflows and imported by the watchdog), so tests import it via
an explicit sys.path entry and never touch the network: the sendable path
is covered by payload construction + the unconfigured no-op contract.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import notify_telegram  # noqa: E402


class TestConfiguration:
    def test_unconfigured_is_not_configured(self, monkeypatch):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("ALERT_TELEGRAM_CHAT_ID", raising=False)
        monkeypatch.delenv("TELEGRAM_ADMIN_CHAT_ID", raising=False)
        assert not notify_telegram.is_configured()

    def test_admin_chat_is_fallback(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
        monkeypatch.delenv("ALERT_TELEGRAM_CHAT_ID", raising=False)
        monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "123")
        assert notify_telegram.is_configured()
        assert notify_telegram._alert_chat_id() == "123"

    def test_dedicated_alert_chat_wins(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
        monkeypatch.setenv("ALERT_TELEGRAM_CHAT_ID", "999")
        monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "123")
        assert notify_telegram._alert_chat_id() == "999"

    def test_dedicated_alert_bot_wins(self, monkeypatch):
        # A separate alert bot keeps paging off the signal bot's rate-limit
        # budget and out of the paid channels — when set, it must win.
        monkeypatch.setenv("ALERT_TELEGRAM_BOT_TOKEN", "alert-bot")
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "signal-bot")
        assert notify_telegram._bot_token() == "alert-bot"

    def test_signal_bot_is_token_fallback(self, monkeypatch):
        monkeypatch.delenv("ALERT_TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "signal-bot")
        assert notify_telegram._bot_token() == "signal-bot"

    def test_alert_bot_alone_is_configured(self, monkeypatch):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.setenv("ALERT_TELEGRAM_BOT_TOKEN", "alert-bot")
        monkeypatch.setenv("ALERT_TELEGRAM_CHAT_ID", "999")
        assert notify_telegram.is_configured()


class TestPayload:
    def test_payload_shape(self):
        body = json.loads(notify_telegram.build_payload("hello", "42"))
        assert body == {
            "chat_id": "42",
            "text": "hello",
            "disable_web_page_preview": True,
        }

    def test_overlong_message_truncated_within_telegram_limit(self):
        body = json.loads(notify_telegram.build_payload("x" * 10_000, "42"))
        assert len(body["text"]) <= 4096
        assert body["text"].endswith("[truncated]")


class TestSendContract:
    def test_unconfigured_send_returns_false_without_network(self, monkeypatch):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("ALERT_TELEGRAM_CHAT_ID", raising=False)
        monkeypatch.delenv("TELEGRAM_ADMIN_CHAT_ID", raising=False)
        assert notify_telegram.send_telegram("boom") is False

    def test_send_never_raises_on_transport_failure(self, monkeypatch):
        # Point at a token+chat so the code takes the network path, then
        # make the opener explode — the alert contract is "never raise".
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
        monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "1")

        def _boom(*a, **k):
            raise OSError("no route to host")

        monkeypatch.setattr(notify_telegram.urllib.request, "urlopen", _boom)
        assert notify_telegram.send_telegram("boom") is False

    def test_failure_output_never_contains_token(self, monkeypatch, capsys):
        secret = "123456:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", secret)
        monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "1")

        def _boom(*a, **k):
            raise ValueError(f"url was https://api.telegram.org/bot{secret}/x")

        monkeypatch.setattr(notify_telegram.urllib.request, "urlopen", _boom)
        assert notify_telegram.send_telegram("boom") is False
        assert secret not in capsys.readouterr().out


class TestCli:
    def _run(self, *args: str, stdin: str = "") -> subprocess.CompletedProcess:
        env = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith(("TELEGRAM", "ALERT_TELEGRAM"))
        }
        return subprocess.run(
            [sys.executable, str(_SCRIPTS / "notify_telegram.py"), *args],
            input=stdin,
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )

    def test_no_args_is_usage_error(self):
        assert self._run().returncode == 2

    def test_unconfigured_send_is_soft_success(self):
        # Alerting must never fail a calling workflow step by default.
        proc = self._run("engine down")
        assert proc.returncode == 0
        assert "not configured" in proc.stdout

    def test_strict_flag_propagates_failure(self):
        assert self._run("--strict", "engine down").returncode == 1

    def test_stdin_mode(self):
        proc = self._run("-", stdin="from a pipe")
        assert proc.returncode == 0
