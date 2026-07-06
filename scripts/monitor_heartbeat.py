import os
import time
import json
p = '/app/data/scanner_heartbeat'
if os.path.exists(p):
    age = int(time.time() - os.path.getmtime(p))
    print(f'Heartbeat age: {age}s')
    if age > 120:
        print(f'WARNING: Heartbeat is STALE ({age}s > 120s) — scanner loop may be hung')
    else:
        print('OK: Heartbeat fresh — scanner loop is alive')
else:
    print('NOT FOUND: /app/data/scanner_heartbeat does not exist inside container')
    print('Scanner has not completed its first cycle yet, or _touch_heartbeat() is failing silently')

# Circuit-breaker state — lets the truth report tell a *protective halt* apart
# from a *hung loop* (both otherwise show a stale heartbeat). Published by the
# scanner every cycle, including while halted.
bp = '/app/data/circuit_breaker_status.json'
if os.path.exists(bp):
    try:
        with open(bp) as fh:
            cb = json.load(fh)
        status_age = int(time.time() - cb.get('updated_at', 0))
        if cb.get('tripped'):
            print(
                'Circuit breaker: TRIPPED '
                f'mode={cb.get("status_mode")} '
                f'reason="{cb.get("trip_reason")}" '
                f'cooldown_remaining={cb.get("cooldown_remaining_s")}s '
                f'daily_drawdown={cb.get("daily_drawdown_pct")}%/{cb.get("max_daily_drawdown_pct")}% '
                f'(status_age={status_age}s)'
            )
        else:
            print(f'Circuit breaker: healthy (status_age={status_age}s)')
    except Exception as exc:  # noqa: BLE001 — diagnostic script, report and move on
        print(f'Circuit breaker: status unreadable ({exc})')
else:
    print('Circuit breaker: status file not found (pre-first-cycle or pre-observability build)')
