"""Telegram cannot gate the money path, because there is no Telegram left in it.

Replaces `test_telegram_not_in_front_of_dispatch.py` (2026-09-15), which pinned
the same property one step weaker. That file asserted the two Telegram drops
sat *behind* `TELEGRAM_SIGNALS_ENABLED` and that the order fan-out sat outside
it — correct while the machinery existed, and its last guard ended with

    raise AssertionError("no `if TELEGRAM_SIGNALS_ENABLED:` branch in _process
                          — the fix has been reverted")

so once the branch was deleted it failed *claiming the fix had been reverted*.
An assertion whose premise the diff removes does not merely stop protecting
anything; it reports the opposite of what happened. That is this repo's own
rule — when a diff changes an invariant, grep the suite for the invariant's
old words and read every hit as a reviewer, not as an author.

The property is now structural rather than flag-guarded: a chat service cannot
stand in front of a paying user's order because `_process` contains no chat
call to stand there. These guards are on the AST, so a substring cannot satisfy
them and a re-introduction has to fail here first.

History, because it is why this spot is sensitive: until 2026-09-15 a channel
send sat between the risk gate and everything else, and both its failure modes
`return`ed — so a failed send took the dispatch log, the order fan-out, the
active book and the app's own push with it.
"""
from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

#: Every name by which the engine could reach the broadcast channels. Each was
#: deleted on 2026-09-16; the BOT names (`send_message`, `send_admin_alert`,
#: `poll_commands`) are deliberately absent — the owner kept those, and they
#: address his own chat rather than a channel.
FORBIDDEN_IN_ROUTER = (
    "TELEGRAM_ACTIVE_CHANNEL_ID",
    "TELEGRAM_FREE_CHANNEL_ID",
    "TELEGRAM_SIGNALS_ENABLED",
    "CHANNEL_TELEGRAM_MAP",
    "post_to_active_channel",
    "post_to_free_channel",
    "_send_telegram",
    "format_cornix_signal",
)


def _router_tree() -> ast.Module:
    return ast.parse((SRC / "signal_router.py").read_text(encoding="utf-8"))


def _process_node() -> ast.AsyncFunctionDef:
    for node in ast.walk(_router_tree()):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_process":
            return node
    raise AssertionError("SignalRouter._process not found")


def _names_used(node: ast.AST) -> set[str]:
    """Every identifier and attribute name reachable under *node*."""
    out: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


class TestTheRouterCannotReachAChannel:
    def test_process_names_no_channel_identifier(self):
        used = _names_used(_process_node())
        leaked = sorted(n for n in FORBIDDEN_IN_ROUTER if n in used)
        assert not leaked, (
            "SignalRouter._process can reach a Telegram broadcast channel "
            f"again via {leaked} — the money path must not sit behind a chat "
            "service. See this module's docstring."
        )

    def test_the_whole_router_module_names_no_channel_identifier(self):
        """Not just `_process`: a helper it calls would be just as fatal."""
        used = _names_used(_router_tree())
        leaked = sorted(n for n in FORBIDDEN_IN_ROUTER if n in used)
        assert not leaked, f"signal_router reaches a broadcast channel via {leaked}"

    def test_the_money_path_is_still_there(self):
        """The inverse guard, and it is the one that makes the others mean
        something: a file that had simply lost `_process` would satisfy every
        assertion above.
        """
        used = _names_used(_process_node())
        assert "_write_dispatch_log" in used, "the dispatch log left _process"
        src = ast.unparse(_process_node())
        assert "dispatch_signal_to_active_users" in src, (
            "the order fan-out left _process — the money path is what this "
            "guard exists to protect, not the absence of Telegram"
        )


class TestTheMonitorCannotReachAChannel:
    def test_no_channel_identifier_in_trade_monitor(self):
        used = _names_used(ast.parse((SRC / "trade_monitor.py").read_text(encoding="utf-8")))
        for name in ("CHANNEL_TELEGRAM_MAP", "TELEGRAM_ACTIVE_CHANNEL_ID",
                     "TELEGRAM_FREE_CHANNEL_ID"):
            assert name not in used, (
                f"trade_monitor reaches a broadcast channel via {name}; the "
                "four channel posters were deleted on 2026-09-16"
            )


class TestTheBotTheOwnerKeptIsUntouched:
    """The other half of the owner's instruction: *keep only two bots to use
    commands, know liveness, etc*. A cleanup that took the pager with it would
    be worse than the clutter it removed — a dead pager sends no message.
    """

    def test_the_bot_still_has_its_command_and_alert_surface(self):
        tree = ast.parse((SRC / "telegram_bot.py").read_text(encoding="utf-8"))
        defined = {
            n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for kept in ("send_message", "send_admin_alert", "send_document", "poll_commands"):
            assert kept in defined, (
                f"TelegramBot.{kept} was removed — the owner kept the bot for "
                "commands, liveness and OTP; only the channels were deleted"
            )

    def test_the_channel_posters_are_gone(self):
        tree = ast.parse((SRC / "telegram_bot.py").read_text(encoding="utf-8"))
        defined = {
            n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for gone in ("post_to_active_channel", "post_to_free_channel"):
            assert gone not in defined, f"TelegramBot.{gone} is back"

    def test_the_admin_chat_id_is_still_configured(self):
        import config
        assert hasattr(config, "TELEGRAM_BOT_TOKEN")
        assert hasattr(config, "TELEGRAM_ADMIN_CHAT_ID")
        for gone in ("TELEGRAM_ACTIVE_CHANNEL_ID", "TELEGRAM_FREE_CHANNEL_ID",
                     "TELEGRAM_SIGNALS_ENABLED", "CHANNEL_TELEGRAM_MAP"):
            assert not hasattr(config, gone), f"config.{gone} is back"
