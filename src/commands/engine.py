"""Engine monitoring commands (admin) — /status, /dashboard, /scan, /pairs, /logs."""

from __future__ import annotations

import asyncio
import time
from typing import List, Optional

import psutil

from src.commands.registry import CommandContext, CommandRegistry
from src.logger import get_recent_logs

registry = CommandRegistry()

_TELEGRAM_LOG_MAX_CHARS: int = 3_500


@registry.command(
    "/status",
    aliases=["/engine_status"],
    admin=True,
    group="engine",
    help_text="Engine status + resource usage",
)
async def handle_status(args: List[str], ctx: CommandContext) -> None:
    uptime_s = time.monotonic() - ctx.boot_time
    hours, rem = divmod(int(uptime_s), 3600)
    minutes, secs = divmod(rem, 60)
    ws_healthy = (
        (ctx.ws_spot.is_healthy if ctx.ws_spot else True)
        and (ctx.ws_futures.is_healthy if ctx.ws_futures else True)
    )
    proc = psutil.Process()
    mem_info = proc.memory_info()
    cpu_pct = proc.cpu_percent(interval=0.1)
    lines = [
        "🔧 Engine Status",
        f"Uptime: {hours}h {minutes}m {secs}s",
        f"Running tasks: {sum(1 for t in ctx.tasks if not t.done())}",
        f"Queue size: {await ctx.signal_queue.qsize()}",
        f"Pairs: {len(ctx.pair_mgr.pairs)}",
        f"Active signals: {len(ctx.router.active_signals)}",
        f"WS healthy: {'✅' if ws_healthy else '❌'}",
        "",
        "🧠 Resources",
        f"RSS: {mem_info.rss / 1024 / 1024:.1f} MB",
        f"CPU: {cpu_pct:.1f}%",
    ]
    await ctx.reply("\n".join(lines))


@registry.command(
    "/dashboard",
    aliases=["/view_dashboard"],
    admin=True,
    group="engine",
    help_text="Telemetry dashboard",
)
async def handle_dashboard(args: List[str], ctx: CommandContext) -> None:
    await ctx.reply(ctx.telemetry.dashboard_text())


@registry.command(
    "/scan",
    aliases=["/force_scan"],
    admin=True,
    group="engine",
    help_text="Force an immediate scan",
)
async def handle_scan(args: List[str], ctx: CommandContext) -> None:
    if ctx.scanner is not None:
        ctx.scanner.force_scan = True
    await ctx.reply("⚡ Force scan triggered.")


@registry.command(
    "/pairs",
    aliases=["/view_pairs"],
    admin=True,
    group="engine",
    help_text="View pairs: /pairs [spot|futures]",
)
async def handle_pairs(args: List[str], ctx: CommandContext) -> None:
    market_filter: Optional[str] = args[0].lower() if args else None
    all_pairs = list(ctx.pair_mgr.pairs.values())
    if market_filter in ("spot", "futures"):
        all_pairs = [p for p in all_pairs if p.market == market_filter]
    sorted_pairs = sorted(all_pairs, key=lambda p: p.volume_24h_usd, reverse=True)
    top = sorted_pairs[:10]
    label = market_filter.capitalize() if market_filter else "All"
    lines = [f"📊 {label} Pairs: {len(all_pairs)} active\n\nTop 10 by volume:"]
    for i, p in enumerate(top, 1):
        lines.append(f"{i}. {p.symbol} ({p.market}) — ${p.volume_24h_usd:,.0f}")
    await ctx.reply("\n".join(lines))


@registry.command(
    "/logs",
    aliases=["/view_logs"],
    admin=True,
    group="engine",
    help_text="View recent logs: /logs [n]",
)
async def handle_logs(args: List[str], ctx: CommandContext) -> None:
    n_lines = 50
    if args:
        try:
            n_lines = int(args[0])
        except ValueError:
            pass
    n_lines = min(max(n_lines, 1), 200)
    logs = get_recent_logs(n_lines)
    if not logs:
        await ctx.reply("No log file found.")
    else:
        excerpt = logs[-_TELEGRAM_LOG_MAX_CHARS:]
        await ctx.reply(f"```\n{excerpt}\n```")


@registry.command(
    "/update_pairs",
    admin=True,
    group="engine",
    help_text="Refresh pair list: /update_pairs [spot|futures] [n]",
)
async def handle_update_pairs(args: List[str], ctx: CommandContext) -> None:
    market: Optional[str] = args[0].lower() if args else None
    count: Optional[int] = None
    if len(args) >= 2:
        try:
            count = int(args[1])
        except ValueError:
            pass
    await ctx.pair_mgr.refresh_pairs(market=market, count=count)
    await ctx.reply(f"✅ Pairs refreshed: {len(ctx.pair_mgr.pairs)} active")


@registry.command(
    "/subscribe_alerts",
    admin=True,
    group="engine",
    help_text="Subscribe to admin alerts",
)
async def handle_subscribe_alerts(args: List[str], ctx: CommandContext) -> None:
    ctx.alert_subscribers.add(ctx.chat_id)
    await ctx.reply("✅ You are subscribed to admin alerts.")


@registry.command(
    "/view_active_signals",
    admin=True,
    group="engine",
    help_text="All active signals (admin)",
)
async def handle_view_active_signals(args: List[str], ctx: CommandContext) -> None:
    sigs = list(ctx.router.active_signals.values())
    if not sigs:
        await ctx.reply("No active signals.")
        return
    lines = [f"📡 Active Signals ({len(sigs)}):"]
    for s in sigs:
        lines.append(
            f"• [{s.signal_id}] {s.symbol} {s.direction.value} | "
            f"Entry {s.entry:.4f} | SL {s.stop_loss:.4f} | "
            f"Conf {s.confidence:.0f}% | {s.status}"
        )
    await ctx.reply("\n".join(lines))


@registry.command(
    "/force_update_ai",
    admin=True,
    group="engine",
    help_text="Refresh AI/sentiment cache",
)
async def handle_force_update_ai(args: List[str], ctx: CommandContext) -> None:
    try:
        count = 0
        symbols = list(ctx.symbols_fn())[:5] if ctx.symbols_fn else []
        for sym in symbols:
            try:
                if ctx.ai_insight_fn:
                    await asyncio.wait_for(ctx.ai_insight_fn(sym), timeout=3)
                count += 1
            except Exception:
                pass
        await ctx.reply(f"✅ AI/sentiment cache refreshed for {count} symbols.")
    except Exception as exc:
        await ctx.reply(f"❌ AI refresh error: {exc}")


@registry.command(
    "/set_free_channel_limit",
    admin=True,
    group="engine",
    help_text="Set free channel daily signal limit",
)
async def handle_set_free_channel_limit(args: List[str], ctx: CommandContext) -> None:
    if not args:
        await ctx.reply("Usage: /set\\_free\\_channel\\_limit <n>")
        return
    try:
        limit = int(args[0])
        ctx.free_channel_limit = max(0, limit)
        ctx.router.set_free_limit(ctx.free_channel_limit)
        await ctx.reply(f"✅ Free channel daily signal limit set to {ctx.free_channel_limit}")
    except ValueError:
        await ctx.reply("❌ Value must be an integer.")


@registry.command(
    "/suppressed",
    aliases=["/suppression"],
    admin=True,
    group="engine",
    help_text="Show suppressed signal digest for the last 4h",
)
async def handle_suppressed(args: List[str], ctx: CommandContext) -> None:
    """Send a rolling-window suppression digest to the admin chat."""
    tracker = getattr(ctx.scanner, "suppression_tracker", None)
    if tracker is None:
        await ctx.reply("⚠️ Suppression tracker not available.")
        return
    digest = tracker.format_telegram_digest()
    await ctx.reply(digest)


# ---------------------------------------------------------------------------
# Auto-execution mode runtime control (Phase A2 / A3 / A4 — Telegram bridge)
# ---------------------------------------------------------------------------


def _format_auto_status(status: dict) -> str:
    """Render the auto-execution status dict as a Telegram message."""
    mode = str(status.get("mode", "unknown")).upper()
    emoji = {"OFF": "⚪", "PAPER": "🧪", "LIVE": "🔴"}.get(mode, "❓")
    lines = [
        f"{emoji} *Auto-Execution Mode:* `{mode}`",
        "",
        f"Open positions:    {status.get('open_positions', 0)}",
        f"Daily PnL:         ${status.get('daily_pnl_usd', 0.0):+.2f} ({status.get('daily_loss_pct', 0.0):+.2f}%)",
        f"Current equity:    ${status.get('current_equity_usd', 0.0):.2f}",
    ]
    if status.get("daily_kill_tripped"):
        lines.append("⚠️ Daily-loss kill TRIPPED — no new opens until UTC midnight")
    if status.get("manual_paused"):
        lines.append("⏸️ Manual pause active")
    if "simulated_pnl_usd" in status:
        lines.append(f"Paper session PnL: ${status['simulated_pnl_usd']:+.4f}")
    return "\n".join(lines)


@registry.command(
    "/automode",
    aliases=["/auto", "/exec_mode"],
    admin=True,
    group="engine",
    help_text="Show or change auto-execution mode: /automode [off|paper|live]",
)
async def handle_automode(args: List[str], ctx: CommandContext) -> None:
    """Show or change the engine's auto-execution mode at runtime.

    Usage:
        /automode             — show current mode and status
        /automode paper       — switch to paper-trade mode (simulated fills)
        /automode live        — switch to live (real orders, requires API keys)
        /automode off         — disable auto-execution entirely

    Safety: refuses to switch while open positions exist.  Live mode
    requires EXCHANGE_API_KEY + EXCHANGE_API_SECRET in env.  Changes are
    ephemeral — engine restart reverts to AUTO_EXECUTION_MODE env var.
    """
    if ctx.get_auto_execution_status_fn is None or ctx.set_auto_execution_mode_fn is None:
        await ctx.reply("⚠️ Auto-execution control not wired into this engine instance.")
        return

    # No args → show status only
    if not args:
        try:
            status = ctx.get_auto_execution_status_fn() or {}
        except Exception as exc:
            await ctx.reply(f"❌ Failed to read auto-execution status: {exc}")
            return
        await ctx.reply(_format_auto_status(status))
        return

    requested = args[0].strip().lower()
    if requested not in ("off", "paper", "live"):
        await ctx.reply(
            "❌ Mode must be one of: `off`, `paper`, `live`.\n"
            "Usage: `/automode [off|paper|live]`"
        )
        return

    # Live-mode confirmation guard — extra friction before the only mode
    # that actually risks money.  Owner must type "live confirm" rather
    # than just "live" to flip on real-money execution.
    if requested == "live" and (len(args) < 2 or args[1].lower() != "confirm"):
        await ctx.reply(
            "⚠️ *Live-mode confirmation required.*\n\n"
            "Live mode places real orders on Binance Futures with real funds. "
            "Type `/automode live confirm` to proceed.\n\n"
            "Pre-flight reminders:\n"
            "• `EXCHANGE_API_KEY` + `EXCHANGE_API_SECRET` must be set\n"
            "• API key should have *trade-only* permission (no withdraw)\n"
            "• VPS IP must be whitelisted on Binance\n"
            "• Start with a small `RISK_STARTING_EQUITY_USD` (e.g. 50)"
        )
        return

    try:
        success, message = ctx.set_auto_execution_mode_fn(requested)
    except Exception as exc:
        await ctx.reply(f"❌ Mode change failed: {exc}")
        return

    if success:
        # Show the new status alongside the success message.
        try:
            status = ctx.get_auto_execution_status_fn() or {}
            await ctx.reply(f"✅ {message}\n\n{_format_auto_status(status)}")
        except Exception:
            await ctx.reply(f"✅ {message}")
    else:
        await ctx.reply(f"❌ {message}")
