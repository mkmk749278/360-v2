# Safe-Halt Runbook — stopping all live trading, for non-engineers

*Audit finding F-04 (2026-07-10). This page exists so that someone who is NOT
the owner-engineer — a family member, a friend with the continuity pack —
can put the system into a safe state in under five minutes, from a phone.*

## What "safe" means here

- Every user's open position already has a **stop-loss and take-profit
  resting on Binance itself**. Halting the engine does NOT strand anyone in
  an unprotected trade — the exchange executes those orders with or without us.
- The kill switch stops all **new** automated orders within 5 seconds.

## To halt everything (the only two steps that matter)

1. Open **https://ops.luminapp.org** in any browser and sign in
   (password + 6-digit code from the authenticator app — both are in the
   continuity pack).
2. Go to **Control** → press **ENGAGE KILL SWITCH** → confirm.

That's it. All server-side auto-trading is stopped. The switch is stored in
Google's cloud (Firestore), so it holds even if the server reboots.

## Verify it worked

The Control page re-reads the live state after every action — it should show
**Kill switch: ENGAGED**. If the page errors, retry once; if it still fails,
use the fallback below.

## Fallback (ops dashboard unreachable)

If you have the VPS SSH key (continuity pack):
```bash
ssh <user>@<vps-host>
cd 360-v2 && docker compose down
```
Stopping the containers stops all new orders. Resting stops on Binance
continue to protect open positions.

## What NOT to do

- Do **not** delete anything, run cleanup commands, or edit files.
- Do **not** disable the kill switch again — leave that to an engineer.
- Do **not** touch the Binance account itself; users' funds live in their
  own Binance accounts and need no action.

## Who to contact next

See the continuity pack (docs/CONTINUITY_PACK_TEMPLATE.md) for the current
emergency contacts and the engineer hand-over instructions.
