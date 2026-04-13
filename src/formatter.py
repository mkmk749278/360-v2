"""Formatter — minimalist message rendering for all Telegram content types.

All formats follow the design rules:
- Maximum 10 lines per message
- One emoji maximum per message, always at the start
- Numbers aligned vertically using spaces
- One separator style only: the · dot
- No labels that shout
- Template fallback is production-quality

Variant selection is context-driven: urgency, time of day, recent post frequency.
"""

from __future__ import annotations

import random
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Setup emoji map
# ---------------------------------------------------------------------------

SETUP_EMOJIS: Dict[str, str] = {
    "LIQUIDITY_SWEEP_REVERSAL": "⚡",
    "RANGE_FADE": "📊",
    "WHALE_MOMENTUM": "🐋",
    "FVG_RETEST": "⚡",
    "FVG_RETEST_HTF_CONFLUENCE": "⚡",
    "CVD_DIVERGENCE": "📉",
    "ORDERBLOCK_BOUNCE": "◈",
    "DIVERGENCE_REVERSAL": "🔄",
    "OBI_IMBALANCE": "📊",
    "SUPERTREND_SIGNAL": "📈",
    "ICHIMOKU_SIGNAL": "◈",
    "VWAP_EXTENSION": "📏",
    "CONTINUATION_LIQUIDITY_SWEEP": "🔁",
}


# ---------------------------------------------------------------------------
# Confidence bar
# ---------------------------------------------------------------------------

def render_conf_bar(confidence: int) -> str:
    """Render confidence as ████████░░ style bar (10 chars)."""
    filled = round(confidence / 10)
    filled = max(0, min(10, filled))
    return "█" * filled + "░" * (10 - filled)


# ---------------------------------------------------------------------------
# Percentage formatting helpers
# ---------------------------------------------------------------------------

def _pct(entry: float, target: float) -> str:
    """Return signed percentage move from entry to target as string."""
    if entry == 0:
        return "0.00%"
    pct = (target - entry) / entry * 100.0
    return f"{pct:+.2f}%"


def _rr_str(entry: float, tp: float, sl: float) -> str:
    """Return R:R ratio string (e.g. '2.1R')."""
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    if risk == 0:
        return "—"
    return f"{reward / risk:.1f}R"


# ---------------------------------------------------------------------------
# Signal formatter
# ---------------------------------------------------------------------------

def format_signal(ctx: Dict[str, Any], variant: Optional[int] = None) -> str:
    """Render a live signal message.

    Parameters
    ----------
    ctx:
        Dictionary with keys: symbol, direction, entry, tp1, tp2, tp3,
        sl, confidence, valid_min, setup_name (optional).
    variant:
        0=standard, 1=with setup name+bar, 2=ultra minimal.
        When None the variant is chosen by context logic.
    """
    symbol: str = ctx.get("symbol", "???")
    direction: str = ctx.get("direction", "LONG").upper()
    entry: float = float(ctx.get("entry", 0))
    tp1: float = float(ctx.get("tp1", 0))
    tp2: float = float(ctx.get("tp2", 0))
    tp3: Optional[float] = ctx.get("tp3")
    if tp3 is not None:
        tp3 = float(tp3)
    sl: float = float(ctx.get("sl", 0))
    conf: int = int(ctx.get("confidence", 0))
    valid_min: int = int(ctx.get("valid_min", 15))
    setup_name: str = ctx.get("setup_name", "")
    signals_last_hour: int = int(ctx.get("signals_last_hour", 0))
    is_first_signal: bool = bool(ctx.get("is_first_signal", False))

    if variant is None:
        variant = _select_signal_variant(conf, signals_last_hour, is_first_signal)

    tp3_line = f"TP3     {tp3:.4f}  · {_pct(entry, tp3)}" if tp3 else ""
    rr = _rr_str(entry, tp2 if tp2 else tp1, sl)
    setup_emoji = SETUP_EMOJIS.get(setup_name, "⚡")

    if variant == 1:
        conf_bar = render_conf_bar(conf)
        setup_label = setup_name.replace("_", " ").title() if setup_name else "Setup"
        tp_line = f"  TP    {tp1:.4f}  /  {tp2:.4f}" + (f"  /  {tp3:.4f}" if tp3 else "")
        lines = [
            f"{symbol}  ·  {direction}  ·  Futures",
            f"{setup_emoji} {setup_label}",
            "",
            f"  In    {entry:.4f}",
            tp_line,
            f"  SL    {sl:.4f}",
            "",
            f"  {conf}/100  {conf_bar}  ·  {rr}",
        ]
        return "\n".join(lines)

    if variant == 2:
        tp_targets = f"{tp1:.4f}  ·  {tp2:.4f}" + (f"  ·  {tp3:.4f}" if tp3 else "")
        lines = [
            f"◈ {symbol} {direction}",
            "",
            f"{entry:.4f} → {tp_targets}",
            f"Stop: {sl:.4f}",
            "",
            f"Conf {conf}  ·  R:R {rr}  ·  {valid_min}min",
        ]
        return "\n".join(lines)

    # Variant 0 — standard
    lines = [
        f"⚡ {symbol} — {direction}",
        "",
        f"Entry   {entry:.4f}",
        f"TP1     {tp1:.4f}  · {_pct(entry, tp1)}",
        f"TP2     {tp2:.4f}  · {_pct(entry, tp2)}",
    ]
    if tp3:
        lines.append(f"TP3     {tp3:.4f}  · {_pct(entry, tp3)}")
    lines.append(f"SL      {sl:.4f}   · {_pct(entry, sl)}")
    lines.append("")
    lines.append(f"R:R {rr}  ·  Conf {conf}  ·  {valid_min}min")
    return "\n".join(lines)


def _select_signal_variant(conf: int, signals_last_hour: int, is_first_signal: bool) -> int:
    """Context-driven variant selection for signal messages."""
    if signals_last_hour >= 4:
        return 2
    if is_first_signal:
        return 0
    if conf > 85:
        return 1
    return random.randint(0, 2)


# ---------------------------------------------------------------------------
# Radar alert formatter
# ---------------------------------------------------------------------------

def format_radar_alert(ctx: Dict[str, Any], variant: Optional[int] = None) -> str:
    """Render a radar alert (setup forming, not yet a live signal).

    Variants 0-5 as specified in the design doc.
    """
    symbol: str = ctx.get("symbol", "???")
    bias: str = ctx.get("bias", "NEUTRAL").upper()
    conf: int = int(ctx.get("confidence", 0))
    gpt_text: str = ctx.get("gpt_text", "")
    waiting_for: str = ctx.get("waiting_for", "confirmation")
    level: str = ctx.get("level", "")
    is_active_market: bool = bool(ctx.get("is_active_market", False))

    if variant is None:
        variant = _select_radar_variant(conf, is_active_market)

    # Split gpt_text into sentences for templates that need 1 vs 2 sentences
    sentences = [s.strip() for s in gpt_text.split(".") if s.strip()]
    sent1 = sentences[0] + "." if sentences else ""
    sent2 = (sentences[1] + "." if len(sentences) > 1 else "") if len(sentences) > 1 else ""
    gpt_2 = f"{sent1} {sent2}".strip() if sent2 else sent1

    if variant == 1:
        lines = [
            f"📍 {symbol}  ·  {bias} bias",
            "",
            sent1,
            f"Waiting: {waiting_for}",
            "",
            "🔒 Full entry in Active Trading",
        ]
        return "\n".join(l for l in lines)

    if variant == 2:
        swept_line = f"📍 {symbol} swept {level}." if level else f"📍 {symbol} at key level."
        return f"{swept_line}\n{sent1} 🔒"

    if variant == 3:
        lines = [
            f"👁 {symbol}  ·  watching closely",
            "",
            gpt_2,
            "",
            f"Conf {conf}/100  ·  not live yet",
            "🔒 Active Trading when it triggers",
        ]
        return "\n".join(lines)

    if variant == 4:
        lines = [
            "📡 What we're watching —",
            "",
            gpt_2,
            "",
            f"{symbol} is the pair. Not a signal yet. 🔒",
        ]
        return "\n".join(lines)

    if variant == 5:
        lines = [
            f"⚡ {symbol}  ·  setup forming NOW",
            "",
            sent1,
            "",
            "🔒 If confirmation — signal incoming",
        ]
        return "\n".join(lines)

    # Variant 0 — analyst callout
    lines = [
        f"👁 {symbol}",
        "",
        gpt_2 if gpt_2 else sent1,
        "",
        "🔒 Signal fires in Active Trading",
    ]
    return "\n".join(lines)


def _select_radar_variant(conf: int, is_active_market: bool) -> int:
    """Context-driven variant selection for radar alerts."""
    if is_active_market:
        return 2
    if conf >= 70:
        return 3
    return random.choice([0, 1, 4])


# ---------------------------------------------------------------------------
# Signal closed — TP hit
# ---------------------------------------------------------------------------

def format_signal_closed_tp(ctx: Dict[str, Any], variant: Optional[int] = None) -> str:
    """Render a TP-hit closure message."""
    symbol: str = ctx.get("symbol", "???")
    direction: str = ctx.get("direction", "LONG").upper()
    tp_label: str = ctx.get("tp_label", "TP")
    close_price: float = float(ctx.get("close_price", 0))
    entry_price: float = float(ctx.get("entry_price", 0))
    r_multiple: float = float(ctx.get("r_multiple", 0))
    pct: float = float(ctx.get("pnl_pct", 0))
    gpt_text: str = ctx.get("gpt_text", "")
    wins: int = int(ctx.get("wins", 0))
    losses: int = int(ctx.get("losses", 0))

    if variant is None:
        variant = random.randint(0, 2)

    if variant == 1:
        lines = [
            f"✅ {symbol}  ·  {tp_label} hit",
            "",
            f"+{pct:.2f}%  /  +{r_multiple:.1f}R",
            f"{entry_price:.4f} → {close_price:.4f}",
            "",
            gpt_text,
        ]
        return "\n".join(l for l in lines if l is not None)

    if variant == 2:
        return f"✅ {symbol} {direction}  +{r_multiple:.1f}R\n\n{tp_label}  ·  {close_price:.4f}"

    # Variant 0
    lines = [
        f"✅ {symbol} {direction}  ·  +{r_multiple:.1f}R",
        "",
        f"Closed at {tp_label} — {close_price:.4f}",
        f"Entry was {entry_price:.4f}",
        "",
    ]
    if gpt_text:
        lines.append(gpt_text)
        lines.append("")
    lines.append(f"Week  ·  {wins}W  {losses}L")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Signal closed — SL hit
# ---------------------------------------------------------------------------

def format_signal_closed_sl(ctx: Dict[str, Any], variant: Optional[int] = None) -> str:
    """Render a stop-loss hit closure message."""
    symbol: str = ctx.get("symbol", "???")
    direction: str = ctx.get("direction", "LONG").upper()
    sl_price: float = float(ctx.get("sl_price", 0))
    entry_price: float = float(ctx.get("entry_price", 0))
    pct: float = float(ctx.get("pnl_pct", 0))
    gpt_text: str = ctx.get("gpt_text", "")
    wins: int = int(ctx.get("wins", 0))
    losses: int = int(ctx.get("losses", 0))

    if variant is None:
        variant = random.randint(0, 1)

    if variant == 1:
        lines = [
            f"🛑 {symbol}  ·  stopped out",
            "",
            f"{entry_price:.4f} → {sl_price:.4f}  ({pct:.2f}%)",
        ]
        if gpt_text:
            lines.append(gpt_text)
        return "\n".join(lines)

    # Variant 0
    lines = [
        f"🛑 {symbol} {direction}  ·  −1R",
        "",
        f"Stopped at {sl_price:.4f}",
    ]
    if gpt_text:
        lines.append(gpt_text)
    lines.append("")
    lines.append(f"Week  ·  {wins}W  {losses}L")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Morning brief
# ---------------------------------------------------------------------------

def format_morning_brief(ctx: Dict[str, Any]) -> str:
    """Render a morning market briefing."""
    day: str = ctx.get("day", "")
    date: str = ctx.get("date", "")
    gpt_text: str = ctx.get("gpt_text", "")
    pair1: str = ctx.get("pair1", "BTC")
    pair2: str = ctx.get("pair2", "ETH")
    session: str = ctx.get("session", "Asian")
    session_mood: str = ctx.get("session_mood", "active")

    lines = [
        f"☀️ {day}  ·  {date}",
        "",
        gpt_text,
        "",
        f"Watching {pair1} and {pair2} today.",
        f"{session} open looks {session_mood}.",
    ]
    return "\n".join(l for l in lines)


# ---------------------------------------------------------------------------
# Session open — London
# ---------------------------------------------------------------------------

def format_london_open(ctx: Dict[str, Any]) -> str:
    """Render a London session open message."""
    gpt_text: str = ctx.get("gpt_text", "")
    pair1: str = ctx.get("pair1", "BTCUSDT")
    pair2: str = ctx.get("pair2", "ETHUSDT")
    pair3: str = ctx.get("pair3", "SOLUSDT")

    lines = [
        "🇬🇧 London open.",
        "",
        gpt_text,
        f"Top pairs: {pair1}, {pair2}, {pair3}.",
    ]
    return "\n".join(l for l in lines)


# ---------------------------------------------------------------------------
# Session open — NY
# ---------------------------------------------------------------------------

def format_ny_open(ctx: Dict[str, Any]) -> str:
    """Render a New York session open message."""
    gpt_text: str = ctx.get("gpt_text", "")
    bias: str = ctx.get("bias", "NEUTRAL").upper()

    lines = [
        "🇺🇸 New York open.",
        "",
        gpt_text,
        f"Bias: {bias}.",
    ]
    return "\n".join(l for l in lines)


# ---------------------------------------------------------------------------
# End of day wrap
# ---------------------------------------------------------------------------

def format_eod_wrap(ctx: Dict[str, Any]) -> str:
    """Render an end-of-day wrap message."""
    day: str = ctx.get("day", "")
    signals_count: int = int(ctx.get("signals_count", 0))
    wins: int = int(ctx.get("wins", 0))
    losses: int = int(ctx.get("losses", 0))
    gpt_text: str = ctx.get("gpt_text", "")
    overnight_pair: str = ctx.get("overnight_pair", "BTCUSDT")

    lines = [
        f"🌙 {day} wrap.",
        "",
        f"{signals_count} signals today · {wins}W {losses}L",
        gpt_text,
        "",
        f"Overnight watch: {overnight_pair}.",
    ]
    return "\n".join(l for l in lines)


# ---------------------------------------------------------------------------
# Market watch / silence breaker
# ---------------------------------------------------------------------------

def format_market_watch(ctx: Dict[str, Any], variant: Optional[int] = None) -> str:
    """Render a market watch / silence breaker message."""
    symbol: str = ctx.get("symbol", "")
    gpt_text: str = ctx.get("gpt_text", "")

    sentences = [s.strip() for s in gpt_text.split(".") if s.strip()]
    sent1 = sentences[0] + "." if sentences else ""
    sent2 = (sentences[1] + "." if len(sentences) > 1 else "") if len(sentences) > 1 else ""
    gpt_2 = f"{sent1} {sent2}".strip() if sent2 else sent1

    if variant is None:
        variant = random.randint(0, 2)

    if variant == 1 and symbol:
        lines = [
            f"📍 {symbol} at a key level.",
            "",
            gpt_2,
            "",
            "Watching.",
        ]
        return "\n".join(lines)

    if variant == 2:
        return f"📡 Quiet market. Patience.\n\n{sent1}"

    # Variant 0
    lines = [
        "📡 Markets consolidating.",
        "",
        gpt_2,
        "",
        "No clean setup yet. Waiting.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Weekly performance card
# ---------------------------------------------------------------------------

def format_weekly_card(ctx: Dict[str, Any]) -> str:
    """Render the weekly performance summary card."""
    date_range: str = ctx.get("date_range", "")
    total: int = int(ctx.get("total", 0))
    wins: int = int(ctx.get("wins", 0))
    losses: int = int(ctx.get("losses", 0))
    winrate: float = float(ctx.get("winrate", 0))
    avg_rr: float = float(ctx.get("avg_rr", 0))
    best_symbol: str = ctx.get("best_symbol", "")
    best_r: float = float(ctx.get("best_r", 0))
    worst_symbol: str = ctx.get("worst_symbol", "")
    worst_r: float = float(ctx.get("worst_r", 0))
    month_label: str = ctx.get("month_label", "")
    month_winrate: float = float(ctx.get("month_winrate", 0))
    streak: str = ctx.get("streak", "")

    lines = [
        f"📊 Week of {date_range}",
        "",
        f"Signals    {total}",
        f"Win rate   {winrate:.0f}%   ·   {wins}W  {losses}L",
        f"Avg R:R    {avg_rr:.1f}",
        "",
        f"Best       {best_symbol}  +{best_r:.1f}R",
    ]
    if worst_symbol and worst_r < 0:
        lines.append(f"Worst      {worst_symbol}  {worst_r:.1f}R")
    lines.append("")
    streak_str = f"  {streak}" if streak else ""
    lines.append(f"{month_label}  {month_winrate:.0f}%{streak_str}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Radar watch lifecycle follow-ups (free channel only — no premium details)
# ---------------------------------------------------------------------------

def format_radar_watch_resolved_paid(
    symbol: str,
    bias: str,
    setup_name: str,
) -> str:
    """Free-channel follow-up: radar watch rolled into a live paid signal.

    Intentionally omits entry, TP, and SL values — those are premium details.
    """
    bias_label = bias.capitalize()
    lines = [
        f"🔔 {symbol}  ·  {bias_label} setup triggered",
        "",
        f"The {setup_name} radar watch we flagged earlier has rolled into a live signal.",
        "",
        "🔒 Full entry details in Active Trading.",
    ]
    return "\n".join(lines)


def format_radar_watch_expired(
    symbol: str,
    bias: str,
    setup_name: str,
) -> str:
    """Free-channel follow-up: radar watch expired / no trigger."""
    bias_label = bias.capitalize()
    lines = [
        f"⏱ {symbol}  ·  {bias_label} watch expired",
        "",
        f"The {setup_name} setup we were watching did not trigger within the session window.",
        "No trade. Staying patient.",
    ]
    return "\n".join(lines)
