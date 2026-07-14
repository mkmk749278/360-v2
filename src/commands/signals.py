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
        # numpy-truthiness class (2026-07-14): the store's arrays raise in
        # bool context; BOTH the primary and fallback branch used the same
        # pattern, so /market showed "—" for BTC forever.
        btc_candles = ctx.data_store.get_candles("BTCUSDT", "5m") or {}
        closes = btc_candles.get("close")
        if closes is not None and len(closes) >= 2:
            curr = float(closes[-1])
            prev = float(closes[-2])
            change_pct = (curr - prev) / prev * 100
            btc_price = f"${curr:,.0f}"
            btc_change = f" ({change_pct:+.2f}%)"
    except Exception:
        try:
            btc_candles = ctx.data_store.candles.get("BTCUSDT", {}).get("5m", {})
            closes = btc_candles.get("close")
            if closes is not None and len(closes) >= 2:
                curr = float(closes[-1])
                prev = float(closes[-2])
                change_pct = (curr - prev) / prev * 100
                btc_price = f"${curr:,.0f}"
                btc_change = f" ({change_pct:+.2f}%)"
        except Exception as exc:
            from src import fail_open
            fail_open.record("commands.market_btc_price", exc)

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


@registry.command("/why", group="signals", help_text="Gate-by-gate diagnostic: /why BTCUSDT")
async def handle_why(args: List[str], ctx: CommandContext) -> None:
    if not args:
        await ctx.reply("Usage: /why <symbol>  e.g. /why BTCUSDT")
        return
    symbol = args[0].upper().strip()
    if not symbol.endswith("USDT"):
        symbol = symbol + "USDT"

    if ctx.scanner is None:
        await ctx.reply("❌ Scanner not available.")
        return

    diagnose_fn = getattr(ctx.scanner, "diagnose_pair", None)
    if diagnose_fn is None:
        await ctx.reply("❌ diagnose_pair not available on scanner.")
        return

    try:
        result = await diagnose_fn(symbol)
    except Exception as exc:
        await ctx.reply(f"❌ Error running diagnostics: {exc}")
        return

    if result.get("error"):
        await ctx.reply(f"❌ {result['error']}")
        return

    gates = result.get("gates", {})
    paths = result.get("signal_paths", {})

    def fmt_pass(p: bool) -> str:
        return "✅" if p else "❌"

    lines = [f"🔍 *Diagnostic: {symbol}*\n"]

    regime_g = gates.get("regime", {})
    lines.append(f"Regime: {regime_g.get('value', '?')}")

    spread_g = gates.get("spread", {})
    lines.append(f"Spread: {spread_g.get('value', '?'):.4f}% {fmt_pass(spread_g.get('pass', False))} (< {spread_g.get('threshold', 0.02):.2f}%)")

    vol_g = gates.get("volume", {})
    vol_val = vol_g.get("value", 0)
    vol_floor = vol_g.get("floor", 0)
    lines.append(f"Volume: ${vol_val:,.0f} {fmt_pass(vol_g.get('pass', False))} (floor ${vol_floor:,.0f})")

    smc_g = gates.get("smc", {})
    lines.append(f"SMC: {smc_g.get('sweeps', 0)} sweeps, {smc_g.get('fvgs', 0)} FVG {fmt_pass(smc_g.get('pass', False))}")

    ema_g = gates.get("ema", {})
    ema9 = ema_g.get("ema9")
    ema21 = ema_g.get("ema21")
    if ema9 and ema21:
        ema_dir = "ema9 > ema21" if ema9 > ema21 else "ema9 < ema21"
    else:
        ema_dir = "?"
    lines.append(f"EMA: {ema_dir}")

    mom_g = gates.get("momentum", {})
    lines.append(f"Momentum: {mom_g.get('value', '?')}")

    macd_g = gates.get("macd", {})
    lines.append(f"MACD: {macd_g.get('direction', '?')}")

    rsi_g = gates.get("rsi", {})
    lines.append(f"RSI: {rsi_g.get('value', '?')}")

    of_g = gates.get("order_flow", {})
    fund = of_g.get("funding_rate")
    fund_str = f"{fund:.4f}" if fund is not None else "N/A"
    lines.append(f"Order Flow: CVD {'✅' if of_g.get('cvd_available') else '❌'} | Funding: {fund_str}")

    kz_g = gates.get("kill_zone", {})
    kz_str = "active ✅" if kz_g.get("active") else "inactive ⚠️"
    lines.append(f"Kill Zone: {kz_str} (UTC {kz_g.get('hour_utc', '?')}:xx)")

    lines.append("\n*Signal paths tried:*")
    for path_name, path_result in paths.items():
        short_name = path_name.replace("_evaluate_", "").upper()
        if path_result.get("fired"):
            conf = path_result.get("confidence", 0)
            direction = path_result.get("direction", "?")
            lines.append(f"✅ {short_name}: {direction} conf={conf:.0f}")
        else:
            err = path_result.get("error", "")
            err_str = f" ({err})" if err else ""
            lines.append(f"❌ {short_name}: None{err_str}")

    await ctx.reply("\n".join(lines))


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

