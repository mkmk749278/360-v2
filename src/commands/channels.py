"""Channel & safety commands (admin) — /pause, /resume, /confidence, /breaker, /stats, /gem, /diag."""

from __future__ import annotations

import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from src.commands.registry import CommandContext, CommandRegistry
from src.signal_history_store import save_history

registry = CommandRegistry()


@registry.command(
    "/pause",
    aliases=["/pause_channel"],
    admin=True,
    group="channels",
    help_text="Pause a channel: /pause <name>",
)
async def handle_pause(args: List[str], ctx: CommandContext) -> None:
    if not args:
        await ctx.reply("Usage: /pause <channel_name>")
        return
    name = args[0]
    ctx.paused_channels.add(name)
    await ctx.reply(f"⏸ Channel `{name}` paused.")


@registry.command(
    "/resume",
    aliases=["/resume_channel"],
    admin=True,
    group="channels",
    help_text="Resume a channel: /resume <name>",
)
async def handle_resume(args: List[str], ctx: CommandContext) -> None:
    if not args:
        await ctx.reply("Usage: /resume <channel_name>")
        return
    name = args[0]
    ctx.paused_channels.discard(name)
    await ctx.reply(f"▶️ Channel `{name}` resumed.")


@registry.command(
    "/confidence",
    aliases=["/set_confidence_threshold"],
    admin=True,
    group="channels",
    help_text="Set confidence threshold: /confidence <channel> <value>",
)
async def handle_confidence(args: List[str], ctx: CommandContext) -> None:
    if len(args) < 2:
        await ctx.reply("Usage: /confidence <channel> <value>")
        return
    channel = args[0]
    try:
        value = float(args[1])
    except ValueError:
        await ctx.reply("❌ Value must be a number.")
        return
    ctx.confidence_overrides[channel] = value
    await ctx.reply(f"✅ Confidence threshold for `{channel}` set to {value:.2f}")


@registry.command(
    "/breaker",
    admin=True,
    group="channels",
    help_text="Circuit breaker status or reset: /breaker [reset]",
)
async def handle_breaker(args: List[str], ctx: CommandContext) -> None:
    if ctx.circuit_breaker is None:
        await ctx.reply("ℹ️ Circuit breaker is not enabled.")
        return
    if args and args[0].lower() == "reset":
        ctx.circuit_breaker.reset()
        await ctx.reply(
            "✅ Circuit breaker reset. Rolling breaker history cleared and signal generation resumed."
        )
    else:
        await ctx.reply(ctx.circuit_breaker.status_text())


@registry.command(
    "/stats",
    aliases=["/real_stats"],
    admin=True,
    group="channels",
    help_text="Performance stats: /stats [channel]",
)
async def handle_stats(args: List[str], ctx: CommandContext) -> None:
    if ctx.performance_tracker is None:
        await ctx.reply("ℹ️ Performance tracker is not enabled.")
        return
    channel_arg = args[0] if args else None
    msg = ctx.performance_tracker.format_stats_message(channel=channel_arg)
    await ctx.reply(msg)


@registry.command(
    "/reset_stats",
    admin=True,
    group="channels",
    help_text="Reset performance stats: /reset_stats [channel]",
)
async def handle_reset_stats(args: List[str], ctx: CommandContext) -> None:
    if ctx.performance_tracker is None:
        await ctx.reply("ℹ️ Performance tracker is not enabled.")
        return
    channel_arg = args[0] if args else None
    cleared = ctx.performance_tracker.reset_stats(channel=channel_arg)
    label = channel_arg or "all channels"
    await ctx.reply(f"🗑 Performance stats reset: {cleared} records cleared for {label}.")


@registry.command(
    "/reset_full",
    admin=True,
    group="channels",
    help_text=(
        "Reset ALL signal stores: performance stats + signal history "
        "(app feed) + invalidation records.  Use to start a clean cycle "
        "(e.g. after a doctrinal change) so app + /stats reflect only "
        "post-reset signals."
    ),
)
async def handle_reset_full(args: List[str], ctx: CommandContext) -> None:
    """Atomic clean-slate reset across all signal-data stores.

    Clears, in order:
      1. PerformanceTracker records (driving /stats)
      2. In-memory _signal_history + data/signal_history.json (driving the app)
      3. data/invalidation_records.json (truth source for INVALIDATED status)

    Active signals (router.active_signals) are NOT cleared — those are
    in-flight trades and would orphan auto-trade broker positions if wiped.
    """
    perf_cleared = 0
    if ctx.performance_tracker is not None:
        perf_cleared = ctx.performance_tracker.reset_stats(channel=None)

    history_cleared = len(ctx.signal_history)
    ctx.signal_history.clear()
    try:
        save_history(ctx.signal_history)
    except Exception as e:
        await ctx.reply(f"⚠️ signal_history.json flush failed: {e}")

    inv_path = Path("data/invalidation_records.json")
    inv_cleared = 0
    if inv_path.exists():
        try:
            existing = json.loads(inv_path.read_text(encoding="utf-8"))
            inv_cleared = len(existing) if isinstance(existing, list) else 0
        except (OSError, json.JSONDecodeError):
            inv_cleared = 0
        try:
            inv_path.write_text("[]", encoding="utf-8")
        except OSError as e:
            await ctx.reply(f"⚠️ invalidation_records.json clear failed: {e}")

    await ctx.reply(
        "🗑 Full reset complete:\n"
        f"  • Performance stats: {perf_cleared} records\n"
        f"  • Signal history (app): {history_cleared} signals\n"
        f"  • Invalidation records: {inv_cleared} records\n"
        f"\nActive in-flight signals were NOT cleared (would orphan broker positions)."
    )


@registry.command(
    "/diag",
    aliases=["/diagnostic", "/chartist_diag"],
    admin=True,
    group="channels",
    help_text=(
        "Snapshot the chartist-eye runtime state — LevelBook coverage, "
        "VolumeProfile / StructureTracker counts, MA-cross cooldown registry, "
        "active-signal soft-gate-flag distribution, and the last suppression "
        "summary.  Replies with the full report as a Telegram document."
    ),
)
async def handle_diag(args: List[str], ctx: CommandContext) -> None:
    """Snapshot the chartist-eye stack live state and reply as a document."""
    sections: List[str] = []
    now = time.time()
    iso_now = datetime.now(timezone.utc).isoformat()
    sections.append(f"=== CHARTIST-EYE DIAGNOSTIC @ {iso_now} ===\n")

    scanner = ctx.scanner
    router = ctx.router

    # --- Engine boot time + uptime ---
    sections.append("--- ENGINE ---")
    boot_ts = float(getattr(ctx, "boot_time", 0.0) or 0.0)
    if boot_ts > 0:
        boot_iso = datetime.fromtimestamp(boot_ts, tz=timezone.utc).isoformat()
        uptime_s = max(0.0, now - boot_ts)
        h = int(uptime_s // 3600)
        m = int((uptime_s % 3600) // 60)
        sections.append(f"Boot: {boot_iso}")
        sections.append(f"Uptime: {h}h {m}m")
    else:
        sections.append("Boot time not available (ctx.boot_time = 0)")
    sections.append("")

    # --- Effective confidence thresholds per channel ---
    # Surfaces the actual min_confidence each channel is filtering against
    # (channel default + any /confidence override).  This is the answer to
    # "why is SR_FLIP showing threshold=80 in logs" — we read the live
    # number from the running scanner, not config defaults.
    sections.append("--- EFFECTIVE THRESHOLDS PER CHANNEL ---")
    overrides = dict(getattr(ctx, "confidence_overrides", {}) or {})
    if overrides:
        sections.append(f"Active /confidence overrides: {overrides}")
    else:
        sections.append("Active /confidence overrides: (none)")
    channels = list(getattr(scanner, "channels", []) or [])
    if channels:
        sections.append("Channel → min_confidence (effective):")
        for ch in channels:
            cfg = getattr(ch, "config", None)
            if cfg is None:
                continue
            chan_name = getattr(cfg, "name", "?")
            default_mc = getattr(cfg, "min_confidence", "?")
            override = overrides.get(chan_name)
            if override is not None:
                sections.append(
                    f"  {chan_name}: {override} (override; default {default_mc})"
                )
            else:
                sections.append(f"  {chan_name}: {default_mc}")
    sections.append("")

    # --- LevelBook ---
    sections.append("--- LEVEL BOOK ---")
    lb = getattr(scanner, "level_book", None)
    if lb is None:
        sections.append("scanner.level_book: NOT PRESENT (PR #315 not deployed?)")
    else:
        levels_map = getattr(lb, "_levels", {}) or {}
        refresh_ts = getattr(lb, "_refresh_ts", {}) or {}
        sections.append(f"Symbols populated: {len(levels_map)}")
        if refresh_ts:
            most_recent = max(refresh_ts.values())
            sections.append(f"Most-recent refresh: {now - most_recent:.0f}s ago")
        per_symbol_count = sorted(
            ((sym, len(lvls)) for sym, lvls in levels_map.items()),
            key=lambda x: x[1], reverse=True,
        )
        sections.append("Top-10 symbols by level count:")
        for sym, n in per_symbol_count[:10]:
            try:
                stats = lb.stats(sym)
                sections.append(f"  {sym}: {n} levels, {stats}")
            except Exception:
                sections.append(f"  {sym}: {n} levels")
    sections.append("")

    # --- Volume Profile (micro + macro) ---
    sections.append("--- VOLUME PROFILE ---")
    for store_name, label in (
        ("volume_profile_store", "micro (1h × 200)"),
        ("volume_profile_store_macro", "macro (1d × 200)"),
    ):
        store = getattr(scanner, store_name, None)
        if store is None:
            sections.append(f"  {label}: NOT PRESENT")
            continue
        results = getattr(store, "_results", {}) or {}
        sections.append(f"  {label}: {len(results)} symbols populated")
        for sym in sorted(results.keys())[:3]:
            try:
                s = store.stats(sym)
                sections.append(f"    {sym}: {s}")
            except Exception:
                pass
    sections.append("")

    # --- Structure Tracker ---
    sections.append("--- STRUCTURE TRACKER ---")
    st = getattr(scanner, "structure_tracker", None)
    if st is None:
        sections.append("scanner.structure_tracker: NOT PRESENT")
    else:
        states = getattr(st, "_state", {}) or {}
        sections.append(f"States populated: {len(states)}")
        leg_counter: Counter = Counter(
            getattr(s, "state", "?") for s in states.values()
        )
        sections.append(f"Distribution: {dict(leg_counter)}")
        bull_examples = [
            (k[0], getattr(v, "confidence", 0))
            for k, v in states.items()
            if getattr(v, "state", "") == "BULL_LEG"
        ][:5]
        bear_examples = [
            (k[0], getattr(v, "confidence", 0))
            for k, v in states.items()
            if getattr(v, "state", "") == "BEAR_LEG"
        ][:5]
        if bull_examples:
            sections.append(f"BULL_LEG sample: {bull_examples}")
        if bear_examples:
            sections.append(f"BEAR_LEG sample: {bear_examples}")
    sections.append("")

    # --- MA-cross cooldown ---
    sections.append("--- MA-CROSS COOLDOWN ---")
    scalp_ch = next(
        (
            ch for ch in getattr(scanner, "channels", [])
            if hasattr(ch, "_ma_cross_last_fire_ts")
        ),
        None,
    )
    if scalp_ch is None:
        sections.append("ScalpChannel not found")
    else:
        cd = scalp_ch._ma_cross_last_fire_ts
        sections.append(f"Cooldown entries: {len(cd)}")
        sorted_cd = sorted(cd.items(), key=lambda x: x[1], reverse=True)
        for (sym, dir_), ts in sorted_cd[:15]:
            age_h = (now - ts) / 3600
            sections.append(f"  {sym} {dir_}: {age_h:.1f}h ago")
    cd_path = Path("data/ma_cross_cooldown.json")
    if cd_path.exists():
        sections.append(f"On-disk file: {cd_path} ({cd_path.stat().st_size} bytes)")
    else:
        sections.append("On-disk file: not yet written (no MA-cross fired since deploy)")
    sections.append("")

    # --- Active signals: soft-gate-flag distribution ---
    sections.append("--- ACTIVE SIGNAL FLAGS ---")
    active = list(getattr(router, "active_signals", {}).values()) if router else []
    sections.append(f"Active signals: {len(active)}")
    flag_counter: Counter = Counter()
    for sig in active:
        flags = (getattr(sig, "soft_gate_flags", "") or "").split(",")
        for f in flags:
            f = f.strip()
            if not f:
                continue
            base = f.split(":")[0].split("×")[0]
            flag_counter[base] += 1
    if flag_counter:
        sections.append(f"Flag distribution: {dict(flag_counter)}")
    else:
        sections.append("No flags on any active signal")
    sections.append("")

    # --- Recent terminal-state signal flags (last 50 of signal_history) ---
    sections.append("--- RECENT TERMINAL FLAGS (last 50) ---")
    history = list(ctx.signal_history)[-50:] if ctx.signal_history else []
    sections.append(f"Sample size: {len(history)}")

    # Timestamp range so we can tell pre- from post-deploy samples.
    def _sig_ts(sig: object) -> Optional[float]:
        ts = getattr(sig, "timestamp", None)
        if ts is None:
            return None
        if hasattr(ts, "timestamp"):
            try:
                return float(ts.timestamp())
            except Exception:
                return None
        try:
            return float(ts)
        except (TypeError, ValueError):
            return None

    timestamps = [t for t in (_sig_ts(s) for s in history) if t is not None]
    pre_deploy_count = 0
    post_deploy_count = 0
    if timestamps:
        ts_min = min(timestamps)
        ts_max = max(timestamps)
        sections.append(
            f"Timestamp range: {datetime.fromtimestamp(ts_min, tz=timezone.utc).isoformat()}"
            f" → {datetime.fromtimestamp(ts_max, tz=timezone.utc).isoformat()}"
        )
        # Use boot_time as the "post-deploy" cutoff if available — anything
        # signalled before the running build started cannot have chartist-eye
        # flags by definition.
        if boot_ts > 0:
            post_deploy_count = sum(1 for t in timestamps if t >= boot_ts)
            pre_deploy_count = len(timestamps) - post_deploy_count
            sections.append(
                f"Pre-deploy: {pre_deploy_count} signals; "
                f"post-deploy: {post_deploy_count} signals"
            )

    history_flag_counter: Counter = Counter()
    confluence_seen = 0
    struct_seen = 0
    for sig in history:
        flags = (getattr(sig, "soft_gate_flags", "") or "").split(",")
        for f in flags:
            f = f.strip()
            if not f:
                continue
            base = f.split(":")[0].split("×")[0]
            history_flag_counter[base] += 1
            if base.startswith("CONFLUENCE"):
                confluence_seen += 1
            elif base.startswith("STRUCT_ALIGN"):
                struct_seen += 1
    if history_flag_counter:
        sections.append(f"Flag distribution: {dict(history_flag_counter)}")
    sections.append(
        f"CONFLUENCE_BONUS fired on: {confluence_seen}/{len(history)} recent signals"
    )
    sections.append(
        f"STRUCTURE_ALIGN_BONUS fired on: {struct_seen}/{len(history)} recent signals"
    )
    sections.append("")

    # --- Last suppression summary (from telemetry) ---
    sections.append("--- LAST SUPPRESSION SUMMARY ---")
    suppression = getattr(scanner, "_suppression_counters", None)
    if suppression:
        # Top 25 most-frequent suppression reasons.
        items = sorted(suppression.items(), key=lambda x: x[1], reverse=True)[:25]
        for k, v in items:
            sections.append(f"  {k}: {v}")
    else:
        sections.append("scanner._suppression_counters not exposed")
    sections.append("")

    # --- Wiring health ---
    sections.append("--- WIRING HEALTH (quick check) ---")
    sections.append(
        f"  level_book present:          {lb is not None}"
    )
    sections.append(
        f"  volume_profile_store present: "
        f"{getattr(scanner, 'volume_profile_store', None) is not None}"
    )
    sections.append(
        f"  volume_profile_store_macro present: "
        f"{getattr(scanner, 'volume_profile_store_macro', None) is not None}"
    )
    sections.append(
        f"  structure_tracker present:   {st is not None}"
    )
    sections.append(
        f"  ScalpChannel + MA-cross cooldown registry: "
        f"{scalp_ch is not None}"
    )
    # ⚠ warnings only fire when we have a meaningful post-deploy sample.
    # If every signal in `history` predates the running build's boot, the
    # absence of chartist-eye flags is expected (the wiring didn't exist
    # when those signals ran through scoring).  ``boot_ts > 0`` plus
    # ``post_deploy_count > 5`` is the threshold for "this is a real
    # diagnostic signal, not a stale-history artifact".
    _have_meaningful_sample = (
        boot_ts > 0 and post_deploy_count > 5
    ) or (boot_ts == 0 and len(history) > 5)
    if confluence_seen == 0 and _have_meaningful_sample:
        sample_label = (
            f"{post_deploy_count} post-deploy"
            if post_deploy_count > 0
            else f"{len(history)}"
        )
        sections.append(
            f"  ⚠ NO CONFLUENCE bonuses across {sample_label} signals — investigate "
            "(empty LevelBook, no clusters near entries, or wiring bug)."
        )
    if struct_seen == 0 and _have_meaningful_sample:
        sample_label = (
            f"{post_deploy_count} post-deploy"
            if post_deploy_count > 0
            else f"{len(history)}"
        )
        sections.append(
            f"  ⚠ NO STRUCT_ALIGN bonuses across {sample_label} signals — same "
            "(no trend-path signals or structure not aligning)."
        )
    if (
        boot_ts > 0
        and post_deploy_count == 0
        and len(history) > 0
    ):
        sections.append(
            "  ℹ All recent signals predate the running build — no "
            "post-deploy sample yet.  Wait for fresh signals to verify "
            "chartist-eye wiring."
        )
    sections.append("")

    body = "\n".join(sections)
    filename = f"chartist_eye_diag_{int(now)}.txt"
    caption = f"🔍 Chartist-eye diagnostic snapshot ({len(body)} bytes)"

    sent = False
    try:
        if hasattr(ctx.telegram, "send_document"):
            sent = await ctx.telegram.send_document(
                ctx.chat_id,
                document=body.encode("utf-8"),
                filename=filename,
                caption=caption,
            )
    except Exception as exc:
        await ctx.reply(f"⚠ send_document raised: {exc}")
        sent = False

    if not sent:
        # Fallback: send as a (chunked) text message.
        await ctx.reply(
            "⚠ Document upload failed — sending raw output as text:\n\n```\n"
            + body[:3500]
            + ("\n…(truncated)" if len(body) > 3500 else "")
            + "\n```"
        )


@registry.command(
    "/gem",
    aliases=["/gem_mode"],
    admin=True,
    group="channels",
    help_text="Gem scanner control: /gem [on|off|status]",
)
async def handle_gem(args: List[str], ctx: CommandContext) -> None:
    if ctx.gem_scanner is None:
        await ctx.reply("❌ Gem scanner is not initialized.")
        return
    sub = args[0].lower() if args else "status"
    if sub == "on":
        ctx.gem_scanner.enable()
        await ctx.reply(
            "💎 Gem scanner ON — macro reversal signals will publish to 360\\_GEM channel"
        )
    elif sub == "off":
        ctx.gem_scanner.disable()
        await ctx.reply("🔘 Gem scanner OFF — 360\\_GEM channel paused")
    else:
        await ctx.reply(ctx.gem_scanner.status_text())


@registry.command(
    "/gem_config",
    admin=True,
    group="channels",
    help_text="Configure gem scanner: /gem_config <key> <value>",
)
async def handle_gem_config(args: List[str], ctx: CommandContext) -> None:
    if ctx.gem_scanner is None:
        await ctx.reply("❌ Gem scanner is not initialized.")
        return
    if len(args) < 2:
        await ctx.reply("Usage: /gem\\_config <key> <value>")
        return
    _success, msg = ctx.gem_scanner.update_config(args[0], args[1])
    await ctx.reply(msg)


@registry.command(
    "/report",
    aliases=["/performance_report"],
    admin=True,
    group="channels",
    help_text="Generate HTML performance dashboard: /report",
)
async def handle_report(args: List[str], ctx: CommandContext) -> None:
    """Generate and optionally send an HTML performance report."""
    if ctx.performance_tracker is None:
        await ctx.reply("ℹ️ Performance tracker is not enabled.")
        return
    try:
        from src.performance_report import generate_html_report
        path = generate_html_report(ctx.performance_tracker)
        await ctx.reply(f"✅ Performance report generated: `{path}`")
        # Send the HTML file as a Telegram document if the API supports it
        try:
            report_bytes = open(path, "rb").read()
            await ctx.telegram.send_document(
                ctx.chat_id,
                document=report_bytes,
                filename="performance_report.html",
                caption="📊 360 Crypto — Performance Dashboard",
            )
        except Exception:
            # send_document may not be implemented in all TelegramBot versions;
            # the text confirmation above is sufficient.
            pass
    except Exception as exc:
        await ctx.reply(f"❌ Report generation failed: {exc}")


@registry.command(
    "/digest",
    aliases=["/ai_report", "/ai_digest"],
    admin=True,
    group="channels",
    help_text="On-demand AI trade digest: /digest [hours]",
)
async def handle_digest(args: List[str], ctx: CommandContext) -> None:
    """Trigger an on-demand AI trade observer digest."""
    if ctx.trade_observer is None:
        await ctx.reply("ℹ️ Trade Observer is not enabled.")
        return

    lookback_hours = None
    if args:
        try:
            lookback_hours = int(args[0])
            if lookback_hours < 1:
                lookback_hours = 1
            elif lookback_hours > 168:  # cap at 7 days
                lookback_hours = 168
        except ValueError:
            await ctx.reply("Usage: /digest [hours]  (e.g. /digest 12)")
            return

    await ctx.reply("⏳ Generating AI trade digest…")
    try:
        message = await ctx.trade_observer.run_digest_on_demand(lookback_hours)
        await ctx.reply(message)
    except Exception as exc:
        await ctx.reply(f"❌ Digest generation failed: {exc}")


@registry.command(
    "/statstats",
    admin=True,
    group="channels",
    help_text="Win-rate stats per (channel, pair, regime): /statstats",
)
async def handle_statstats(args: List[str], ctx: CommandContext) -> None:
    """Show rolling win-rate statistics for all tracked signal combinations."""
    if ctx.stat_filter is None:
        await ctx.reply("ℹ️ Statistical filter is not enabled.")
        return
    await ctx.reply(ctx.stat_filter.format_statstats())


