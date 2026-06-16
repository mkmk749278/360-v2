"""Content engine — generates all non-signal Telegram content using GPT-4o-mini.

Falls back to template rendering when OpenAI is unavailable.

All prompts use a strong trader persona, forbidden phrases list, and real
engine context (regime, pairs, recent signals, session, performance).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from config import CONTENT_ENGINE_ENABLED, CONTENT_GPT_MODEL
from src import formatter as fmt
from src.utils import get_logger

log = get_logger("content_engine")

# ---------------------------------------------------------------------------
# GPT system prompt — baked in, never changes
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a professional crypto futures trader running a private signal service.
You have 8 years of experience trading Smart Money Concepts.
You write short, confident posts for your Telegram channel.
Your style: direct, minimal, never salesy, never hype.
You sound like a human analyst, not a bot.

FORBIDDEN PHRASES (never use these):
- "As an AI"
- "Great trade"
- "Setup detected"
- "Signal fired"
- "Please note"
- "It's important to"
- Any rocket emojis
- Multiple exclamation marks
- "To the moon"
- "DYOR"
- "NFA"

FORMAT RULES:
- Maximum 10 lines total
- One emoji maximum per message (at the start)
- Numbers must be exact — taken from context, never invented
- 1-2 sentence commentary maximum — rest is data
- Never start two consecutive sentences the same way
- Vary your opening on every call"""

# Prompt template directory
_PROMPTS_DIR = Path(__file__).parent / "prompts"

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_prompt_template(name: str) -> str:
    """Load a prompt template file, returning empty string on failure."""
    path = _PROMPTS_DIR / f"{name}.txt"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        log.warning("Prompt template not found: %s", path)
        return ""


def _fill_template(template: str, context: Dict[str, Any]) -> str:
    """Fill {placeholders} in a prompt template with context values."""
    try:
        return template.format(**context)
    except KeyError:
        # Partial fill — replace only the keys we have, leave the rest
        result = template
        for key, value in context.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result


async def _call_gpt(user_prompt: str) -> Optional[str]:
    """Call the OpenAI API and return the response text, or None on failure."""
    try:
        import openai  # type: ignore
    except ImportError:
        log.debug("openai package not installed — falling back to template")
        return None

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        log.debug("OPENAI_API_KEY not set — falling back to template")
        return None

    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=CONTENT_GPT_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.7,
        )
        text = response.choices[0].message.content
        if text:
            return text.strip()
    except Exception as exc:
        log.warning("OpenAI call failed: %s — using template fallback", exc)
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate_content(
    content_type: str,
    context: Dict[str, Any],
    template_variant: int = 0,
    use_gpt: bool = True,
) -> str:
    """Generate content for the given *content_type* using GPT or template fallback.

    Parameters
    ----------
    content_type:
        One of: "morning_brief", "london_open", "ny_open", "eod_wrap",
        "radar_alert", "signal_closed_tp", "signal_closed_sl",
        "market_watch", "weekly_card".
    context:
        Real data from the engine.  Keys vary by content type.
    template_variant:
        Which template variant to render (0-5 depending on type).
    use_gpt:
        When False, skip the GPT call and use template rendering only.
    """
    if not CONTENT_ENGINE_ENABLED:
        log.debug("Content engine disabled — skipping %s", content_type)
        return ""

    gpt_text: Optional[str] = None

    if use_gpt:
        template = _load_prompt_template(content_type)
        if template:
            user_prompt = _fill_template(template, context)
            try:
                gpt_text = await _call_gpt(user_prompt)
            except Exception as exc:
                log.warning("GPT call raised unexpectedly for %s: %s", content_type, exc)
                gpt_text = None

    # Inject gpt_text into context for template renderers that need it
    ctx = dict(context)
    if gpt_text:
        ctx["gpt_text"] = gpt_text
    elif "gpt_text" not in ctx:
        ctx["gpt_text"] = _fallback_gpt_text(content_type, ctx)

    return _render_template(content_type, ctx, template_variant)


def _fallback_gpt_text(content_type: str, context: Dict[str, Any]) -> str:
    """Generate a minimal fallback commentary line when GPT is unavailable."""
    regime = context.get("regime", "RANGING")
    symbol = context.get("symbol", context.get("pair1", "BTC"))
    bias = context.get("bias", "NEUTRAL")

    fallbacks: Dict[str, str] = {
        "morning_brief": f"Market regime is {regime}. Watching for clean structure breaks.",
        "london_open": f"Regime {regime}, bias {bias}. Focus on reactive levels.",
        "ny_open": f"NY open. Regime {regime}. Trade the structure.",
        "eod_wrap": "Day completed. Review setups and rest.",
        "radar_alert": f"{symbol} is showing setup formation. Waiting for confirmation.",
        "signal_closed_tp": "Setup played out as anticipated.",
        "signal_closed_sl": "Price invalidated the thesis. Stopped out cleanly.",
        "market_watch": f"Waiting for clear structure on {symbol}. No clean setup yet.",
        "weekly_card": "Week reviewed. Stick to the process.",
    }
    return fallbacks.get(content_type, "")


def _render_template(content_type: str, ctx: Dict[str, Any], variant: int) -> str:
    """Dispatch to the correct formatter function."""
    try:
        if content_type == "morning_brief":
            return fmt.format_morning_brief(ctx)
        if content_type == "london_open":
            return fmt.format_london_open(ctx)
        if content_type == "ny_open":
            return fmt.format_ny_open(ctx)
        if content_type == "eod_wrap":
            return fmt.format_eod_wrap(ctx)
        if content_type == "radar_alert":
            return fmt.format_radar_alert(ctx, variant=variant if variant != 0 else None)
        if content_type == "signal_closed_tp":
            return fmt.format_signal_closed_tp(ctx, variant=variant if variant != 0 else None)
        if content_type == "signal_closed_sl":
            return fmt.format_signal_closed_sl(ctx, variant=variant if variant != 0 else None)
        if content_type == "market_watch":
            return fmt.format_market_watch(ctx, variant=variant if variant != 0 else None)
        if content_type == "weekly_card":
            return fmt.format_weekly_card(ctx)
        log.warning("Unknown content_type: %s", content_type)
        return ""
    except Exception as exc:
        log.error("Template render failed for %s: %s", content_type, exc)
        return ""


# ---------------------------------------------------------------------------
# Convenience wrappers used by the scheduler and trade_monitor
# ---------------------------------------------------------------------------


async def generate_morning_brief(engine_context: Dict[str, Any], use_gpt: bool = True) -> str:
    """Generate a morning briefing message."""
    ctx = _build_morning_context(engine_context)
    return await generate_content("morning_brief", ctx, use_gpt=use_gpt)


async def generate_london_open(engine_context: Dict[str, Any], use_gpt: bool = True) -> str:
    """Generate a London session open message."""
    ctx = _build_session_context(engine_context)
    return await generate_content("london_open", ctx, use_gpt=use_gpt)


async def generate_ny_open(engine_context: Dict[str, Any], use_gpt: bool = True) -> str:
    """Generate a NY session open message."""
    ctx = _build_session_context(engine_context)
    return await generate_content("ny_open", ctx, use_gpt=use_gpt)


async def generate_eod_wrap(engine_context: Dict[str, Any], use_gpt: bool = True) -> str:
    """Generate an end-of-day wrap message."""
    ctx = _build_eod_context(engine_context)
    return await generate_content("eod_wrap", ctx, use_gpt=use_gpt)


async def generate_market_watch(engine_context: Dict[str, Any], use_gpt: bool = True) -> str:
    """Generate a market watch / silence breaker message."""
    ctx = _build_market_watch_context(engine_context)
    return await generate_content("market_watch", ctx, use_gpt=use_gpt)


async def generate_weekly_card(engine_context: Dict[str, Any], use_gpt: bool = True) -> str:
    """Generate the weekly performance card message."""
    ctx = _build_weekly_context(engine_context)
    return await generate_content("weekly_card", ctx, use_gpt=use_gpt)


async def generate_signal_closed_post(
    signal_data: Dict[str, Any],
    is_tp: bool,
    engine_context: Optional[Dict[str, Any]] = None,
    use_gpt: bool = True,
) -> str:
    """Generate a signal-closed message (TP hit or SL hit).

    Parameters
    ----------
    signal_data:
        Data from the closed signal: symbol, direction, entry_price,
        close_price, sl_price, tp_label, r_multiple, pnl_pct, setup_name.
    is_tp:
        True = TP hit, False = SL hit.
    engine_context:
        Live engine context for week stats.
    use_gpt:
        GPT or template fallback.
    """
    perf = (engine_context or {}).get("performance", {})
    ctx = dict(signal_data)
    ctx.setdefault("wins", perf.get("wins_this_week", 0))
    ctx.setdefault("losses", perf.get("losses_this_week", 0))

    content_type = "signal_closed_tp" if is_tp else "signal_closed_sl"
    return await generate_content(content_type, ctx, use_gpt=use_gpt)


# ---------------------------------------------------------------------------
# Context builder helpers
# ---------------------------------------------------------------------------


def _build_morning_context(engine_ctx: Dict[str, Any]) -> Dict[str, Any]:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    pairs = engine_ctx.get("top_pairs", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    return {
        "day": now.strftime("%A"),
        "date": now.strftime("%d %b %Y"),
        "btc_price": engine_ctx.get("btc_price", "—"),
        "regime": engine_ctx.get("regime", "RANGING"),
        "btc_change_pct": engine_ctx.get("btc_change_pct", 0),
        "pair1": pairs[0] if len(pairs) > 0 else "BTCUSDT",
        "pair2": pairs[1] if len(pairs) > 1 else "ETHUSDT",
        "session": "Asian",
        "session_desc": "Low volatility window",
        "session_mood": "active" if engine_ctx.get("regime") == "TRENDING_UP" else "quiet",
    }


def _build_session_context(engine_ctx: Dict[str, Any]) -> Dict[str, Any]:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    pairs = engine_ctx.get("top_pairs", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    regime = engine_ctx.get("regime", "RANGING")
    bias_map = {"TRENDING_UP": "LONG", "TRENDING_DOWN": "SHORT"}
    return {
        "time_utc": now.strftime("%H:%M"),
        "regime": regime,
        "btc_price": engine_ctx.get("btc_price", "—"),
        "bias": bias_map.get(regime, "NEUTRAL"),
        "pair1": pairs[0] if len(pairs) > 0 else "BTCUSDT",
        "pair2": pairs[1] if len(pairs) > 1 else "ETHUSDT",
        "pair3": pairs[2] if len(pairs) > 2 else "SOLUSDT",
        "signals_today": engine_ctx.get("signals_today", 0),
    }


def _build_eod_context(engine_ctx: Dict[str, Any]) -> Dict[str, Any]:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    perf = engine_ctx.get("performance", {})
    pairs = engine_ctx.get("top_pairs", ["BTCUSDT"])
    return {
        "day": now.strftime("%A"),
        "signals_count": engine_ctx.get("signals_today", 0),
        "wins": perf.get("wins_this_week", 0),
        "losses": perf.get("losses_this_week", 0),
        "best_trade": perf.get("best_trade_today", "—"),
        "overnight_pair": pairs[0] if pairs else "BTCUSDT",
    }


def _build_market_watch_context(engine_ctx: Dict[str, Any]) -> Dict[str, Any]:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    pairs = engine_ctx.get("top_pairs", ["BTCUSDT"])
    return {
        "time_utc": now.strftime("%H:%M"),
        "regime": engine_ctx.get("regime", "RANGING"),
        "btc_price": engine_ctx.get("btc_price", "—"),
        "btc_1h_change_pct": engine_ctx.get("btc_1h_change_pct", 0),
        "hours_since_signal": engine_ctx.get("hours_since_signal", 3),
        "key_level": engine_ctx.get("key_level", "—"),
        "symbol": pairs[0] if pairs else "BTCUSDT",
    }


def _build_weekly_context(engine_ctx: Dict[str, Any]) -> Dict[str, Any]:
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    perf = engine_ctx.get("performance", {})
    wins = int(perf.get("wins_this_week", 0))
    losses = int(perf.get("losses_this_week", 0))
    total = wins + losses
    winrate = (wins / total * 100) if total > 0 else 0.0
    return {
        "date_range": f"{week_start.strftime('%d %b')} – {now.strftime('%d %b')}",
        "total": total,
        "wins": wins,
        "losses": losses,
        "winrate": winrate,
        "avg_rr": perf.get("avg_rr_this_week", 0.0),
        "best_symbol": perf.get("best_symbol_this_week", "—"),
        "best_r": perf.get("best_r_this_week", 0.0),
        "worst_symbol": perf.get("worst_symbol_this_week", ""),
        "worst_r": perf.get("worst_r_this_week", 0.0),
        "month_label": now.strftime("%B"),
        "month_winrate": perf.get("month_winrate", 0.0),
        "streak": perf.get("streak_label", ""),
    }
