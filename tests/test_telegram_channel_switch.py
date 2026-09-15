"""The broadcast switch is applied at the identifier, not at each caller.

Owner, 2026-09-15: *"we are completely moved to app side … removing all
telegram Channels signals updates etc, of course we do use telegram bot for
commands and alerts"*.

There are ~14 places in this engine that post to the two public Telegram
channels — the router's daily-best and free-channel content, three
`trade_monitor` update posts, the pre-TP storytelling post, the AI-written
close post, the macro watchdog's HIGH/CRITICAL mirror, the boot test message.
Gating each one is the deny-list shape this repo has paid for under six names:
it is silent by construction on the fifteenth. So the switch blanks
``TELEGRAM_ACTIVE_CHANNEL_ID`` and ``TELEGRAM_FREE_CHANNEL_ID``, and every one
of those sites already refuses an unconfigured channel.

These load config in a fresh interpreter with a controlled environment, rather
than reloading the shared module — a half-reloaded config is exactly the kind
of cross-test damage this repo has recorded for ``asyncio.run``.
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_PROBE = """
import json, config
print("@@" + json.dumps({
    "flag": config.TELEGRAM_SIGNALS_ENABLED,
    "active": config.TELEGRAM_ACTIVE_CHANNEL_ID,
    "free": config.TELEGRAM_FREE_CHANNEL_ID,
    "admin": config.TELEGRAM_ADMIN_CHAT_ID,
    "map": sorted(set(config.CHANNEL_TELEGRAM_MAP.values())),
    "map_keys": sorted(config.CHANNEL_TELEGRAM_MAP),
}))
"""


def _load_config(**env):
    """Import `config` in a clean interpreter under `env`."""
    child = {
        k: v for k, v in os.environ.items()
        if not k.startswith("TELEGRAM_")
    }
    child.update(env)
    child["PYTHONPATH"] = str(ROOT)
    out = subprocess.run(
        [sys.executable, "-c", _PROBE],
        cwd=ROOT, env=child, capture_output=True, text=True, timeout=180,
    )
    assert out.returncode == 0, out.stderr[-3000:]
    line = next(ln for ln in out.stdout.splitlines() if ln.startswith("@@"))
    return json.loads(line[2:])


_IDS = {
    "TELEGRAM_ACTIVE_CHANNEL_ID": "-1001111111111",
    "TELEGRAM_FREE_CHANNEL_ID": "-1002222222222",
    "TELEGRAM_ADMIN_CHAT_ID": "987654321",
}


class TestTheSwitchBlanksTheChannels:
    def test_off_by_default_even_with_every_id_set(self):
        """The production `.env` keeps its ids; they simply stop being read.

        That is what makes this reversible by one variable instead of by a
        redeploy with secrets restored.
        """
        cfg = _load_config(**_IDS)
        assert cfg["flag"] is False
        assert cfg["active"] == ""
        assert cfg["free"] == ""

    def test_the_bot_is_untouched(self):
        """Admin alerts and commands are what the owner asked to KEEP.

        `TELEGRAM_ADMIN_CHAT_ID` is a chat, not a channel, and it is
        deliberately outside the switch.
        """
        cfg = _load_config(**_IDS)
        assert cfg["admin"] == _IDS["TELEGRAM_ADMIN_CHAT_ID"]

    def test_on_restores_both_ids(self):
        cfg = _load_config(TELEGRAM_SIGNALS_ENABLED="true", **_IDS)
        assert cfg["flag"] is True
        assert cfg["active"] == _IDS["TELEGRAM_ACTIVE_CHANNEL_ID"]
        assert cfg["free"] == _IDS["TELEGRAM_FREE_CHANNEL_ID"]


class TestTheEvaluatorMapInheritsTheSwitch:
    def test_every_channel_is_unconfigured_when_the_switch_is_off(self):
        cfg = _load_config(**_IDS)
        assert cfg["map_keys"], "the map must still list its channels"
        assert cfg["map"] == [""], (
            "an evaluator channel that still resolves to a chat id would post "
            "to a channel the switch says is off"
        )

    def test_every_channel_is_configured_when_it_is_on(self):
        cfg = _load_config(TELEGRAM_SIGNALS_ENABLED="true", **_IDS)
        assert cfg["map"] == [_IDS["TELEGRAM_ACTIVE_CHANNEL_ID"]]

    def test_the_map_is_derived_from_the_switched_id_not_from_env(self):
        """Pinned on the tree, because the behavioural test above passes for
        an incidental reason: all eight channels happen to share one id
        today. If `_build_channel_telegram_map` ever read `os.getenv` per
        channel, those channels would silently escape the switch."""
        tree = ast.parse((ROOT / "config" / "__init__.py").read_text())
        fn = next(
            n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef)
            and n.name == "_build_channel_telegram_map"
        )
        names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
        assert "TELEGRAM_ACTIVE_CHANNEL_ID" in names
        for node in ast.walk(fn):
            assert not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "getenv"
            ), (
                "reading the environment here bypasses the switch — the map "
                "must derive from the already-switched constant"
            )


class TestTheDropThisReplaces:
    def test_no_channel_configured_was_never_per_path(self):
        """The finding that decides how the counters are shaped.

        `no_channel_configured` reads like a per-evaluator configuration
        miss. It is not: all eight channels resolve to the one
        `TELEGRAM_ACTIVE_CHANNEL_ID`, so that drop fired only when that
        single variable was unset — and then for EVERY candidate in the
        engine, with nothing on any user-facing surface to say so. That is
        why the router counts bypasses and not "would have been unmapped":
        a counter that can only read 100% describes its own definition.
        """
        cfg = _load_config(TELEGRAM_SIGNALS_ENABLED="true", **_IDS)
        assert len(cfg["map"]) == 1, (
            "if evaluator channels ever route to different chats, the "
            "router's counter shape needs revisiting"
        )
