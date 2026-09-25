# Pre-registered hypotheses — crypto short edges from market structure

Written 2026-09-25, **before any test was run.**

**The starting question.** In crypto, who is *forced* or *mechanically obliged*
to sell, and when can we know in advance? A short edge can only exist where
selling pressure is predictable and not already priced. Priced means paid away
in funding, or already in the price.

**Data.** Public Binance archive only (`data.binance.vision`), plus the
DefiLlama emissions dataset for unlock schedules. The engine and its books are
not used and nothing is compared against them.

**Costs, charged on every trade:**
- 0.07% round-trip fee;
- 0.05% adverse slippage per fill (0.10% per round trip);
- funding carry at the actual settlement rates for any hold that spans a
  settlement.

**Split:**
- in-sample (IS): 2025-09-08 → 2026-04-30;
- out-of-sample (OOS): 2026-05-01 → 2026-09-23.

**Pass bar:**
- a hypothesis passes only if its net mean is **negative for the short
  (i.e. profitable) in both halves**;
- the day-clustered 95% interval on the full sample must exclude zero;
- each result is also reported against a **control** that differs only in
  the hypothesised condition. If the control does as well, the condition is
  not the edge.

**Universe for the intraday tests.**
- Crypto perps (TradFi perps excluded structurally: weekend/weekday volume
  < 0.35).
- Point-in-time liquidity: trailing-7d mean quote volume ≥ $10M at the
  decision time.

## H1 — Cliff unlocks to insiders (supply)

*Mechanism.* Team and investors receive tokens on a known date and a share of
them sell. The date is public, so the market front-runs it (Keyrock: pressure
starts ~30d before).

- **Event:** a cliff unlock in DefiLlama `unlockEvents`.
  - Categories: `insiders`, `privateSale`, or recipient naming team/investors/advisors.
  - Size ≥ 0.5% of max supply.
  - Token has a Binance USDT perp trading on the entry date.
- **Primary window:** short at the close of T−14d, cover at the close of T+2d.
- **Secondary windows (reported, not selected):** [T−30, T], [T−7, T+7],
  [T, T+14].
- **Results reported:** raw short PnL, and BTC-hedged (short token / long BTC,
  equal notional).
- **Control:** the same tokens on dates ≥ 45 days from any cliff unlock.

## H2 — Post-listing decay (supply + insider distribution)

*Mechanism.* New tokens list with low float and high FDV. Airdrop recipients
and early holders distribute into the listing liquidity.

- **Event:** a USDT perp whose first archive kline falls inside the window.
- **Primary:** short at the close of listing day +7, cover at day +60.
- **Secondary:** entry at +3/+14, exit at +30/+90.
- **Funding is critical here** (new listings often carry negative funding),
  so the net result is the headline.
- **Results reported:** raw and BTC-hedged.

## H3 — Leverage without progress, then breakdown (forced long liquidation)

*Mechanism.* OI builds while price goes nowhere, so late longs are trapped.
Breaking the range puts their stops and liquidations below price, and forced
selling feeds the move.

- **Setup at 1h close:**
  - OI change over 24h ≥ its own trailing-30d 80th percentile, and ≥ +5%;
  - |price change 24h| ≤ 3%;
  - last settled funding ≥ 0.
- **Trigger:** a 1h close below the prior 24h low.
- **Trade:** short at the next open, stop 1.0× ATR(24h, 1h) above entry,
  time exit at 12h.
- **Control:** the same trigger with OI change ≤ its trailing-30d median.

## H4 — Perp-led rally, spot not buying (fragile leverage rally)

*Mechanism.* A rally bought with leverage and no spot demand leaves longs with
nobody to sell to, so it retraces.

- **Setup at 1h close:**
  - 24h return ≥ +8%;
  - perp 24h taker net buy (buy − sell) / volume ≥ +4%;
  - spot 24h taker net buy / volume ≤ 0 (Binance spot, same base asset);
  - OI 24h change > 0.
- **Trigger:** within the next 12h, a 1h close below the previous 1h low.
- **Trade:** short at the next open, stop at the post-setup high + 0.2%,
  time exit at 24h.
- **Control:** the same rally with spot taker net ≥ +4% (spot-led).

## H5 — Perp premium dislocation (arbitrage pulls the perp down)

*Mechanism.* When the perp trades far above spot, arbitrageurs sell the perp
and buy spot, and funding charges the longs.

- **Setup at 1h close:**
  - premium index close ≥ 0.25%;
  - above the symbol's trailing-30d 99th percentile.
- **Trade:** short at the next open, exit after 8h.
- **Results reported:** perp price return, funding received, and net.
- **Control:** premium between its 40th and 60th percentile.

## H6 — Funding settlement de-risking (mechanical flow into the timestamp)

*Mechanism.* With funding high, longs close before paying it, so price sags
into the settlement.

- **Setup:** the funding rate that will settle at T (the realised rate is the
  one charged) is ≥ 0.05% per interval.
- **Trade:** short at T−60m (5m open), cover at T+5m. Funding is received at T
  and included.
- **Control:** the same timing with settled funding in [−0.005%, +0.01%].

## H7 — Retail crowding against smart money

*Mechanism.* Retail accounts crowd long while top traders reduce, and retail
is the liquidity that gets liquidated.

- **Setup at 1h:**
  - global long/short *account* ratio ≥ its own trailing-30d 90th percentile;
  - top-trader *position* ratio fell over the last 24h.
- **Trade:** short at the next open, exit at 24h.
- **Control:** account ratio in its 40th–60th percentile.

## H8 — Cross-sectional loser momentum (slow drift, weekly)

*Mechanism.* Literature finds crypto momentum out to 2–4 weeks. Losers keep
losing as holders capitulate and supply keeps unlocking.

- **Weekly rebalance (Monday 00:00 UTC):** among the liquid universe, short the
  bottom decile by 14d return and hold 7d.
- **Reported:**
  - the short leg alone (raw);
  - the short leg vs an equal-weight universe long (market-neutral);
  - vs the top decile.

## H9 — Time of day

- **Pre-registered cells only:**
  - US equity open, 13:30–15:30 UTC: short the equal-weight alt basket;
  - Monday Asia open (Sun 23:00 – Mon 23:00 UTC), expected positive, so
    **avoid** for shorts.
- Nothing else is mined from the 24×7 grid.

## H10 — Liquidation burst: continuation or exhaustion?

- **Event at 5m:**
  - OI falls ≥ 1.5% within 15 minutes;
  - price falls ≥ 2% within the same 15 minutes;
  - this is a proxy for a long-liquidation burst.
- **Test A (continuation):** short at the next 5m open and hold 1h.
- **Test B (exhaustion):** the same, long.
- Reported as a **map of what happens after a cascade**, so we know whether
  shorts must avoid chasing one.
