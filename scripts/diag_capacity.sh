#!/usr/bin/env bash
# diag_capacity.sh — one-shot VPS capacity + headroom report.
#
# Answers the question "how many pairs can this box actually scan?" with
# measured numbers instead of extrapolation:
#
#   1. What the VPS physically has        (cores, RAM, swap, disk)
#   2. What it is currently using         (load, RAM, disk)
#   3. What each container is allowed     (docker mem_limit / cpus)
#   4. What each container actually uses  (docker stats)
#   5. What the engine is doing           (pairs, scan cycle, Binance weight)
#   6. A headroom verdict                 (safe pair ceiling on THIS box)
#
# Written for docs/UNIVERSE_EXPANSION_AND_SECOND_IP_2026_07_27.md, which
# projected these numbers from a single 2026-06-04 datapoint. This script
# replaces the projection with a measurement.
#
# Read-only. Touches nothing, changes nothing, safe to run on production at
# any time. Every section degrades gracefully if its input is missing.
#
# Usage:  bash scripts/diag_capacity.sh
#         bash scripts/diag_capacity.sh > /tmp/capacity.txt 2>&1

set -uo pipefail   # deliberately NOT -e: a missing container must not abort the report

ENGINE="${ENGINE_CONTAINER:-360scalp-v2-engine}"
LOG_WINDOW="${LOG_WINDOW:-6h}"

hr()  { printf '%s\n' "────────────────────────────────────────────────────────────────"; }
sec() { printf '\n'; hr; printf '  %s\n' "$1"; hr; }
kv()  { printf '  %-34s %s\n' "$1" "$2"; }
note(){ printf '  %s\n' "$1"; }

printf '\n'
printf '  360 CE — VPS CAPACITY REPORT\n'
printf '  %s   host=%s\n' "$(date -u '+%Y-%m-%d %H:%M:%S UTC')" "$(hostname 2>/dev/null || echo '?')"

# ── 1. Physical hardware ────────────────────────────────────────────────
sec "1. WHAT THIS VPS PHYSICALLY HAS"

CORES="$(nproc 2>/dev/null || echo 0)"
kv "CPU cores"        "$CORES"
kv "CPU model"        "$(awk -F: '/model name/{gsub(/^ +/,"",$2); print $2; exit}' /proc/cpuinfo 2>/dev/null || echo '?')"

if command -v free >/dev/null 2>&1; then
    MEM_TOTAL_MB="$(free -m | awk '/^Mem:/{print $2}')"
    MEM_USED_MB="$(free -m  | awk '/^Mem:/{print $3}')"
    MEM_AVAIL_MB="$(free -m | awk '/^Mem:/{print $7}')"
    SWAP_TOTAL_MB="$(free -m | awk '/^Swap:/{print $2}')"
    SWAP_USED_MB="$(free -m  | awk '/^Swap:/{print $3}')"
    kv "RAM total"    "$(awk -v m="$MEM_TOTAL_MB" 'BEGIN{printf "%.1f GB (%d MB)", m/1024, m}')"
    kv "Swap total"   "$(awk -v m="$SWAP_TOTAL_MB" 'BEGIN{printf "%.1f GB (%d MB)", m/1024, m}')"
else
    MEM_TOTAL_MB=0; MEM_USED_MB=0; MEM_AVAIL_MB=0; SWAP_TOTAL_MB=0; SWAP_USED_MB=0
    note "free(1) unavailable — RAM figures skipped"
fi

kv "Disk (/)"         "$(df -h / 2>/dev/null | awk 'NR==2{print $2" total, "$3" used, "$4" free ("$5" full)"}')"
kv "Kernel"           "$(uname -sr 2>/dev/null || echo '?')"

# ── 2. Current utilisation ──────────────────────────────────────────────
sec "2. WHAT IT IS USING RIGHT NOW"

LOAD1="$(awk '{print $1}' /proc/loadavg 2>/dev/null || echo 0)"
LOAD5="$(awk '{print $2}' /proc/loadavg 2>/dev/null || echo 0)"
LOAD15="$(awk '{print $3}' /proc/loadavg 2>/dev/null || echo 0)"
kv "Load average (1/5/15 min)" "$LOAD1 / $LOAD5 / $LOAD15"

if [ "$CORES" -gt 0 ]; then
    LOADPCT="$(awk -v l="$LOAD15" -v c="$CORES" 'BEGIN{printf "%.0f", (l/c)*100}')"
    kv "→ CPU saturation (15 min avg)" "${LOADPCT}% of ${CORES} cores"
    if   [ "$LOADPCT" -ge 90 ]; then note "  ⚠  CPU is SATURATED. No headroom for more pairs."
    elif [ "$LOADPCT" -ge 70 ]; then note "  ⚠  CPU is tight. Little headroom."
    else                              note "  ✓  CPU has headroom."
    fi
fi

if [ "$MEM_TOTAL_MB" -gt 0 ]; then
    MEMPCT="$(awk -v u="$MEM_USED_MB" -v t="$MEM_TOTAL_MB" 'BEGIN{printf "%.0f", (u/t)*100}')"
    kv "RAM used"        "${MEM_USED_MB} MB / ${MEM_TOTAL_MB} MB (${MEMPCT}%)"
    kv "RAM available"   "${MEM_AVAIL_MB} MB"
    kv "Swap used"       "${SWAP_USED_MB} MB / ${SWAP_TOTAL_MB} MB"
    if [ "${SWAP_USED_MB:-0}" -gt 100 ]; then
        note "  ⚠  Swap in active use — the box is already under memory pressure."
    fi
fi

# ── 3 + 4. Container limits vs actual usage ─────────────────────────────
sec "3. CONTAINER LIMITS vs ACTUAL USAGE"

if ! command -v docker >/dev/null 2>&1; then
    note "docker not found — skipping container sections."
elif ! docker info >/dev/null 2>&1; then
    note "docker present but not reachable (permissions?) — try: sudo bash scripts/diag_capacity.sh"
else
    printf '  %-26s %10s %10s %8s %10s %8s\n' CONTAINER "MEM USED" "MEM LIMIT" "MEM%" "CPU LIMIT" "CPU%"
    printf '  %-26s %10s %10s %8s %10s %8s\n' "--------------------------" "----------" "----------" "--------" "----------" "--------"

    # docker stats gives live usage; docker inspect gives the configured cap.
    # Joined per container so "using 380MB of a 1024MB cap" reads in one row.
    docker ps --format '{{.Names}}' 2>/dev/null | sort | while read -r C; do
        [ -z "$C" ] && continue
        STATS="$(docker stats --no-stream --format '{{.MemUsage}}|{{.MemPerc}}|{{.CPUPerc}}' "$C" 2>/dev/null)"
        MEM_USE="$(printf '%s' "$STATS" | cut -d'|' -f1 | awk '{print $1}')"
        MEM_PCT="$(printf '%s' "$STATS" | cut -d'|' -f2)"
        CPU_PCT="$(printf '%s' "$STATS" | cut -d'|' -f3)"

        LIM_BYTES="$(docker inspect --format '{{.HostConfig.Memory}}' "$C" 2>/dev/null || echo 0)"
        NANO_CPU="$(docker inspect  --format '{{.HostConfig.NanoCpus}}' "$C" 2>/dev/null || echo 0)"
        if [ "${LIM_BYTES:-0}" -gt 0 ] 2>/dev/null; then
            MEM_LIM="$(awk -v b="$LIM_BYTES" 'BEGIN{printf "%dMB", b/1048576}')"
        else
            MEM_LIM="none"
        fi
        if [ "${NANO_CPU:-0}" -gt 0 ] 2>/dev/null; then
            CPU_LIM="$(awk -v n="$NANO_CPU" 'BEGIN{printf "%.2f", n/1000000000}')"
        else
            CPU_LIM="none"
        fi
        printf '  %-26s %10s %10s %8s %10s %8s\n' \
            "$C" "${MEM_USE:-?}" "$MEM_LIM" "${MEM_PCT:-?}" "$CPU_LIM" "${CPU_PCT:-?}"
    done

    printf '\n'
    note "MEM% is against the container's own limit, not the host."
    note "The ENGINE row is the one that decides how many pairs we can add."

    # ── 5. Engine internals ─────────────────────────────────────────────
    sec "5. WHAT THE ENGINE IS ACTUALLY DOING"

    if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$ENGINE"; then
        note "Engine container '$ENGINE' not running — skipping."
        note "Override with: ENGINE_CONTAINER=<name> bash scripts/diag_capacity.sh"
    else
        ENG_MEM_RAW="$(docker stats --no-stream --format '{{.MemUsage}}' "$ENGINE" 2>/dev/null)"
        ENG_MEM_MB="$(printf '%s' "$ENG_MEM_RAW" | awk '{
            v=$1; u=$1;
            sub(/[A-Za-z]+$/,"",v); sub(/^[0-9.]+/,"",u);
            if (u ~ /^G/) printf "%.0f", v*1024;
            else if (u ~ /^M/) printf "%.0f", v;
            else if (u ~ /^k|^K/) printf "%.0f", v/1024;
            else printf "0";
        }')"
        ENG_LIM_MB="$(docker inspect --format '{{.HostConfig.Memory}}' "$ENGINE" 2>/dev/null \
                      | awk '{ if ($1>0) printf "%d", $1/1048576; else print 0 }')"
        kv "Engine memory in use"  "${ENG_MEM_MB:-?} MB"
        kv "Engine memory limit"   "$( [ "${ENG_LIM_MB:-0}" -gt 0 ] && echo "${ENG_LIM_MB} MB" || echo 'unlimited' )"
        kv "Engine uptime"         "$(docker ps --format '{{.Status}}' --filter "name=^${ENGINE}$" 2>/dev/null)"

        # Pairs currently in the scan set.
        PAIRS="$(docker logs "$ENGINE" --since "$LOG_WINDOW" 2>&1 \
                 | grep -oE 'TOP50_FUTURES_COUNT=[0-9]+' | tail -1 | cut -d= -f2)"
        PROMOTED="$(docker logs "$ENGINE" --since "$LOG_WINDOW" 2>&1 \
                 | grep -c 'dynamically promoted' || true)"
        kv "Core pairs (TOP50_FUTURES_COUNT)" "${PAIRS:-unknown}"
        kv "Mover-promotion events (${LOG_WINDOW})" "${PROMOTED:-0}"

        # Scan cycle wall-time — the number the capacity projection scales from.
        CYCLES="$(docker logs "$ENGINE" --since "$LOG_WINDOW" 2>&1 \
                  | grep -oE 'cycle=[0-9]+\.[0-9]+s' | grep -oE '[0-9]+\.[0-9]+' || true)"
        if [ -n "$CYCLES" ]; then
            SCAN_STATS="$(printf '%s\n' "$CYCLES" | awk '
                {n++; s+=$1; if($1>mx)mx=$1; a[n]=$1}
                END{
                    if(n==0){print "0 0 0 0"; exit}
                    asort(a);
                    p95=a[int(n*0.95)]; if(p95=="")p95=mx;
                    printf "%d %.1f %.1f %.1f", n, s/n, p95, mx
                }' 2>/dev/null)"
            # gawk's asort() is not in mawk/busybox — fall back to sort(1).
            if [ -z "$SCAN_STATS" ] || [ "${SCAN_STATS%% *}" = "0" ]; then
                N="$(printf '%s\n' "$CYCLES" | wc -l | tr -d ' ')"
                AVG="$(printf '%s\n' "$CYCLES" | awk '{s+=$1} END{printf "%.1f", (NR?s/NR:0)}')"
                MAX="$(printf '%s\n' "$CYCLES" | sort -n | tail -1)"
                P95="$(printf '%s\n' "$CYCLES" | sort -n | awk -v n="$N" 'NR==int(n*0.95)+0{print; exit}')"
                [ -z "$P95" ] && P95="$MAX"
                SCAN_STATS="$N $AVG $P95 $MAX"
            fi
            set -- $SCAN_STATS
            SCAN_N="$1"; SCAN_AVG="$2"; SCAN_P95="$3"; SCAN_MAX="$4"
            kv "Scan cycles sampled"   "$SCAN_N (last ${LOG_WINDOW})"
            kv "Scan cycle — average"  "${SCAN_AVG}s"
            kv "Scan cycle — p95"      "${SCAN_P95}s"
            kv "Scan cycle — WORST"    "${SCAN_MAX}s   ← capacity is set by this"
        else
            SCAN_MAX=""
            note "No 'cycle=' lines found. Per-stage timing may be off."
            note "Enable with SCAN_STAGE_TIMING_ENABLED=true in .env, then re-run."
        fi

        # Binance weight — the "Binance minutes" question.
        WEIGHT="$(docker logs "$ENGINE" --since "$LOG_WINDOW" 2>&1 \
                  | grep -iE 'used=[0-9]+, budget=[0-9]+|weight' | tail -3 || true)"
        printf '\n'
        kv "Binance weight (recent log lines)" ""
        if [ -n "$WEIGHT" ]; then
            printf '%s\n' "$WEIGHT" | sed 's/^/      /'
        else
            note "    (none — the limiter only logs at >90% of budget,"
            note "     so silence here means we are nowhere near the cap)"
        fi

        # Health signals that would break first under load.
        printf '\n'
        OOM="$(docker inspect --format '{{.State.OOMKilled}}' "$ENGINE" 2>/dev/null)"
        RESTARTS="$(docker inspect --format '{{.RestartCount}}' "$ENGINE" 2>/dev/null)"
        kv "OOM-killed?"      "${OOM:-?}"
        kv "Restart count"    "${RESTARTS:-?}"
        WS_DEG="$(docker logs "$ENGINE" --since "$LOG_WINDOW" 2>&1 | grep -c 'WS health degraded' || true)"
        kv "WS-degraded events (${LOG_WINDOW})" "${WS_DEG:-0}"
        if [ "${OOM:-false}" = "true" ]; then
            note "  ⚠  The engine HAS been OOM-killed. Do not add pairs — reduce or upgrade."
        fi
    fi

    # ── 6. Verdict ──────────────────────────────────────────────────────
    sec "6. HEADROOM VERDICT — SAFE PAIR CEILING FOR THIS BOX"

    if [ -n "${SCAN_MAX:-}" ] && [ -n "${PAIRS:-}" ] && [ "${PAIRS:-0}" -gt 0 ] 2>/dev/null; then
        note "Method: scan cost is ~linear in pair count. A cycle must finish"
        note "well inside the 60s 1m-candle close, or the scanner falls behind"
        note "and the staleness gate discards the signals it just computed."
        note "Ceiling below uses a 40s budget (67% of 60s) for safety margin."
        printf '\n'
        PER_PAIR="$(awk -v m="$SCAN_MAX" -v p="$PAIRS" 'BEGIN{printf "%.4f", m/p}')"
        CPU_CEIL="$(awk -v pp="$PER_PAIR" 'BEGIN{printf "%d", 40/pp}')"
        kv "Measured worst-case per pair" "${PER_PAIR}s"
        kv "→ CPU-based safe ceiling"     "~${CPU_CEIL} pairs"

        if [ "${ENG_LIM_MB:-0}" -gt 0 ] 2>/dev/null && [ "${ENG_MEM_MB:-0}" -gt 0 ] 2>/dev/null; then
            # Assume ~40% of RSS is fixed overhead (interpreter, libs, code)
            # and ~60% scales with pair count. Conservative; refine if we ever
            # measure a second pair-count datapoint.
            MEM_CEIL="$(awk -v used="$ENG_MEM_MB" -v lim="$ENG_LIM_MB" -v p="$PAIRS" 'BEGIN{
                fixed = used*0.40; per = (used*0.60)/p;
                usable = lim*0.80;                 # leave 20% headroom
                if (per<=0) { print 0; exit }
                c = (usable-fixed)/per; if (c<0) c=0;
                printf "%d", c
            }')"
            kv "→ RAM-based safe ceiling" "~${MEM_CEIL} pairs (est.)"
            CEIL="$CPU_CEIL"; [ "${MEM_CEIL:-0}" -lt "$CEIL" ] 2>/dev/null && CEIL="$MEM_CEIL"
            BIND="CPU"; [ "$CEIL" = "${MEM_CEIL:-}" ] && BIND="RAM"
        else
            CEIL="$CPU_CEIL"; BIND="CPU"
        fi

        printf '\n'
        kv "SAFE CEILING ON THIS BOX"  "~${CEIL} pairs   (binding constraint: ${BIND})"
        kv "Currently scanning"        "${PAIRS} core + up to 30 promoted"
        printf '\n'
        if [ "${CEIL:-0}" -ge 400 ] 2>/dev/null; then
            note "✓ This box could take a much larger universe. Re-read the"
            note "  business case in docs/UNIVERSE_EXPANSION_AND_SECOND_IP_2026_07_27.md"
            note "  §8 first — the router still caps delivery at 3 same-direction."
        elif [ "${CEIL:-0}" -ge 150 ] 2>/dev/null; then
            note "✓ Room to widen mover promotion (30 → 50) with margin to spare."
            note "  Full universe (~500) still needs a bigger box."
        else
            note "⚠ Little or no headroom. Do NOT widen the universe on this box."
            note "  An upgrade is required before any expansion."
        fi
    else
        note "Not enough data for a verdict — need both a pair count and scan"
        note "cycle times. Ensure SCAN_STAGE_TIMING_ENABLED=true and re-run"
        note "after the engine has been up for at least an hour."
    fi
fi

sec "REFERENCE — what the doc projected (now replaceable with the above)"
note "75 pairs   → 16s worst case   (measured 2026-06-04, one datapoint)"
note "150 pairs  → ~32s             (projected)"
note "280 pairs  → ~60s  = the wall (projected)"
note "500 pairs  → ~107s            (projected — never completes in time)"
printf '\n'
note "Full analysis: docs/UNIVERSE_EXPANSION_AND_SECOND_IP_2026_07_27.md"
printf '\n'
