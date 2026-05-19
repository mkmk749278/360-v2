"""Auto-trade admin commands (admin) — operator-side flip for
``auto_trade_globally_enabled`` in the Firestore kill-switch doc.

Server-side execution doctrine (OWNER_BRIEF §3.9 + B18) has the global
enable/disable as a Firestore-doc-driven flag — the FSM gates every
order on it.  Before this command shipped, the only way to flip the
flag was a direct Firestore console edit or a custom Python script with
KMS-service-account credentials.  That's risky (one wrong field name
silently disables every user) and not discoverable in an incident.

This command exposes the flip from the same Telegram surface operators
already use for ``/pause`` / ``/resume`` / ``/automode``.  ``admin=True``
restricts to ``TELEGRAM_ADMIN_CHAT_ID``.  Re-enables emit a follow-up
Telegram alert via :func:`alert_kill_switch_engaged`-style fire-and-
forget so the audit trail in the channel mirrors the FSM gate state.
"""

from __future__ import annotations

from typing import List

from src.commands.registry import CommandContext, CommandRegistry
from src.utils import get_logger

registry = CommandRegistry()

log = get_logger("commands.auto_trade_admin")


@registry.command(
    "/auto_trade_global",
    aliases=["/auto_global"],
    admin=True,
    group="engine",
    help_text=(
        "/auto_trade_global [on|off] — flip auto_trade_globally_enabled. "
        "No argument: print current state."
    ),
)
async def handle_auto_trade_global(
    args: List[str], ctx: CommandContext
) -> None:
    """Read or flip the global auto-trade enable flag.

    Usage:
      /auto_trade_global         → reports current state
      /auto_trade_global on      → ENABLE
      /auto_trade_global off     → DISABLE
    """
    from src.execution import kill_switch as ks

    if not ks.is_initialised():
        await ctx.reply(
            "❌ Kill switch not initialised — engine is missing GCP env "
            "(FIREBASE_SERVICE_ACCOUNT_PATH / GCP_KMS_* in .env).  See "
            "OWNER_BRIEF §3.9 boot order.  No flip applied."
        )
        return

    client = ks.get_client()

    if not args:
        try:
            enabled = client.is_globally_enabled()
            engaged = client.is_global_engaged()
        except Exception as exc:
            log.exception("read global state failed")
            await ctx.reply(f"❌ Read failed: {exc}")
            return
        flag = "ENABLED" if enabled else "DISABLED"
        kill = "ENGAGED (kill switch tripped)" if engaged else "off"
        await ctx.reply(
            f"🛡 Global auto-trade: *{flag}*\n"
            f"    Kill switch: {kill}"
        )
        return

    arg = args[0].strip().lower()
    if arg in ("on", "enable", "enabled", "true"):
        try:
            client.enable_global_auto_trade()
        except Exception as exc:
            log.exception("enable failed")
            await ctx.reply(f"❌ Enable failed: {exc}")
            return
        log.warning("operator enabled global auto-trade via Telegram command")
        await ctx.reply(
            "✅ Global auto-trade ENABLED.\n"
            "    New orders are allowed engine-wide subject to per-user "
            "disable + kill switch checks."
        )
        return

    if arg in ("off", "disable", "disabled", "false"):
        try:
            client.disable_global_auto_trade()
        except Exception as exc:
            log.exception("disable failed")
            await ctx.reply(f"❌ Disable failed: {exc}")
            return
        log.warning("operator disabled global auto-trade via Telegram command")
        await ctx.reply(
            "🛑 Global auto-trade DISABLED.\n"
            "    New orders halted engine-wide.  Existing positions on "
            "Binance are NOT cancelled — use /kill_switch for that."
        )
        return

    await ctx.reply(
        "Usage: /auto_trade_global [on|off]\n"
        "  no arg → print current state"
    )
