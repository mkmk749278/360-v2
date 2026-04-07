"""Signal viewing commands — /signals, /history, /market, /performance, /ask."""

from __future__ import annotations

from typing import List

from config import TOP50_FUTURES_COUNT
from src.commands.registry import CommandContext, CommandRegistry

registry = CommandRegistry()


@registry.command("/signals", group="signals", help_text="Active trade setups being monitored")
async def handle_signals(args: List[str], ctx: CommandContext) -> None:
    sigs = list(ctx.router.active_signals.values())
    if not sigs:
        await ctx.reply(
            "📡 No active setups right now.\n\n"
            f"The scanner is running across {TOP50_FUTURES_COUNT} pairs — we only enter when conditions are right."
        )
        return
    lines = [f"📡 *{len(sigs)} Active Setup{'s' if len(sigs) != 1 else ''}*\n"]
    for s in sigs[:5]:
        direction_arrow = "↑" if str(s.direction.value).upper() in ("LONG", "BUY") else "↓"
        lines.append(
            f"{direction_arrow} *{s.symbol}* · Entry {s.entry:.4f} · Conf {s.confidence:.0f}%"
        )
    if len(sigs) > 5:
        lines.append(f"\n_+{len(sigs) - 5} more active_")
    await ctx.reply("\n".join(lines))


@registry.command(
    "/history",
    aliases=["/signal_history"],
    group="signals",
    help_text="Recent closed trades",
)
async def handle_history(args: List[str], ctx: CommandContext) -> None:
    recent = list(reversed(ctx.signal_history[-5:]))
    if not recent:
        await ctx.reply(
            "📜 No completed trades yet.\n\nSignals are tracked from the moment they fire — check back soon."
        )
        return
    wins = sum(1 for s in ctx.signal_history if hasattr(s, 'pnl_pct') and s.pnl_pct > 0)
    total_closed = len(ctx.signal_history)
    wr = (wins / total_closed * 100) if total_closed > 0 else 0.0
    lines = [f"📜 *Recent Trades* · {wr:.0f}% win rate ({wins}/{total_closed})\n"]
    for s in recent:
        outcome = "✅" if hasattr(s, 'pnl_pct') and s.pnl_pct > 0 else "❌"
        pnl_str = f"{s.pnl_pct:+.2f}%" if hasattr(s, 'pnl_pct') else "—"
        lines.append(f"{outcome} {s.symbol} {str(s.direction.value).upper()} · {pnl_str} · {s.status}")
    await ctx.reply("\n".join(lines))


@registry.command("/market", group="signals", help_text="Current market snapshot")
async def handle_market(args: List[str], ctx: CommandContext) -> None:
    # BTC price from data store
    btc_price = "—"
    btc_change = ""
    try:
        btc_candles = ctx.data_store.get_candles("BTCUSDT", "5m")
        if btc_candles and btc_candles.get("close"):
            closes = btc_candles["close"]
            if len(closes) >= 2:
                curr = float(closes[-1])
                prev = float(closes[-2])
                change_pct = (curr - prev) / prev * 100
                btc_price = f"${curr:,.0f}"
                btc_change = f" ({change_pct:+.2f}%)"
    except Exception:
        try:
            btc_candles = ctx.data_store.candles.get("BTCUSDT", {}).get("5m", {})
            if btc_candles and btc_candles.get("close"):
                closes = btc_candles["close"]
                if len(closes) >= 2:
                    curr = float(closes[-1])
                    prev = float(closes[-2])
                    change_pct = (curr - prev) / prev * 100
                    btc_price = f"${curr:,.0f}"
                    btc_change = f" ({change_pct:+.2f}%)"
        except Exception:
            pass

    active_count = len(ctx.router.active_signals)
    pairs_count = len(ctx.pair_mgr.pairs)
    scan_ms = getattr(ctx.telemetry, '_scan_latency_ms', 0)
    scanner_status = "active" if scan_ms < 60000 else "degraded"

    # Check if scanner is in protective mode by reading suppression tracker if available
    protective = ""
    try:
        tracker = getattr(ctx.scanner, "suppression_tracker", None)
        if tracker is not None:
            digest = tracker.format_telegram_digest()
            if "volatile" in digest.lower() or "spread" in digest.lower():
                protective = " · ⚠️ protective mode"
    except Exception:
        pass

    lines = [
        "📊 *Market Snapshot*\n",
        f"BTC   {btc_price}{btc_change}",
        f"Scanner   {scanner_status}{protective}",
        f"Pairs   {pairs_count} monitored",
        f"Active   {active_count} signal{'s' if active_count != 1 else ''}",
    ]
    await ctx.reply("\n".join(lines))


@registry.command("/performance", aliases=["/perf"], group="signals", help_text="Recent performance stats")
async def handle_performance(args: List[str], ctx: CommandContext) -> None:
    if ctx.performance_tracker is None:
        # Fallback: compute from signal_history
        total = len(ctx.signal_history)
        if not total:
            await ctx.reply(
                "📈 *Performance*\n\nNo completed trades tracked yet. Results will appear here as signals close."
            )
            return
        wins = sum(1 for s in ctx.signal_history if hasattr(s, 'pnl_pct') and s.pnl_pct > 0)
        losses = total - wins
        wr = wins / total * 100
        avg_pnl = sum(s.pnl_pct for s in ctx.signal_history if hasattr(s, 'pnl_pct')) / total
        lines = [
            "📈 *Performance*\n",
            f"Trades   {total}",
            f"Win rate   {wr:.0f}%  ({wins}W · {losses}L)",
            f"Avg PnL   {avg_pnl:+.2f}%",
        ]
        await ctx.reply("\n".join(lines))
        return
    msg = ctx.performance_tracker.format_stats_message()
    await ctx.reply(msg)


@registry.command("/ask", group="signals", help_text="Ask about a pair: /ask BTCUSDT")
async def handle_ask(args: List[str], ctx: CommandContext) -> None:
    if not args:
        await ctx.reply("Usage: /ask <symbol>  e.g. /ask BTCUSDT")
        return
    symbol = args[0].upper().strip()
    if not symbol.endswith("USDT"):
        symbol = symbol + "USDT"

    # Check active signals
    active = [s for s in ctx.router.active_signals.values() if s.symbol == symbol]
    if active:
        sig = active[0]
        direction_word = "Long" if str(sig.direction.value).upper() in ("LONG", "BUY") else "Short"
        lines = [
            f"📡 *{symbol} — Active Signal*\n",
            f"Direction   {direction_word}",
            f"Entry        {sig.entry:.4f}",
            f"SL             {sig.stop_loss:.4f}",
            f"Confidence {sig.confidence:.0f}%",
            f"Status        {sig.status}",
        ]
        await ctx.reply("\n".join(lines))
        return

    # Check recent history
    recent = [s for s in reversed(ctx.signal_history) if s.symbol == symbol]
    if recent:
        last = recent[0]
        direction_word = "Long" if str(last.direction.value).upper() in ("LONG", "BUY") else "Short"
        outcome = "TP hit ✅" if hasattr(last, 'pnl_pct') and last.pnl_pct > 0 else "SL hit ❌"
        pnl_str = f"{last.pnl_pct:+.2f}%" if hasattr(last, 'pnl_pct') else "—"
        lines = [
            f"📋 *{symbol} — Last Signal*\n",
            f"Direction   {direction_word}",
            f"Outcome   {outcome} ({pnl_str})",
            f"Status       {last.status}",
            "\n_No active signal. Scanner continues to watch._",
        ]
        await ctx.reply("\n".join(lines))
        return

    # No data
    await ctx.reply(
        f"📋 *{symbol}*\n\nNo active signal and no recent history for this pair.\n\n"
        f"_We scan {TOP50_FUTURES_COUNT} pairs continuously — a setup will appear here when conditions align._"
    )


@registry.command("/signal_stats", admin=True, group="signals", help_text="Signal quality stats")
async def handle_signal_stats(args: List[str], ctx: CommandContext) -> None:
    if ctx.performance_tracker is None:
        await ctx.reply("ℹ️ Performance tracker is not enabled.")
        return
    channel_arg = args[0] if args else None
    msg = ctx.performance_tracker.format_signal_quality_stats_message(channel=channel_arg)
    await ctx.reply(msg)


@registry.command("/tp_stats", admin=True, group="signals", help_text="TP hit statistics")
async def handle_tp_stats(args: List[str], ctx: CommandContext) -> None:
    if ctx.performance_tracker is None:
        await ctx.reply("ℹ️ Performance tracker is not enabled.")
        return
    channel_arg = args[0] if args else None
    msg = ctx.performance_tracker.format_tp_stats_message(channel=channel_arg)
    await ctx.reply(msg)

