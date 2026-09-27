"""CoinDCX futures execution venue.

What CoinDCX's futures API is, measured and read from its own documentation
(2026-09-27, ``docs/COINDCX_VENUE_PLAN_2026_09_27.md``), and the design each
fact forces:

* **Instruments are Binance's list.**  Every ``B-<BASE>_USDT`` perpetual carries
  its Binance twin in the live price feed (``"mkt": "AVAUSDT"``), and the feed's
  own glossary calls ``btST`` the third-party exchange's tick time.  Signals are
  therefore priced for CoinDCX by the same levels, with no rebasing.
* **One net position per pair.**  A position id is fixed per pair and margin
  currency, so our entry would merge with anything the user already holds there.
  An entry is refused unless the pair is flat.
* **No client order id and no reduce-only flag on order create.**  A standalone
  take-profit order could open a reverse position after the stop has closed the
  trade.  So the only exit orders this venue places are the **position-level**
  TP/SL (``positions/create_tpsl``), which close the entire position and are
  what the engine's default exit profile (TP1-full against a fixed stop) is.
* **Cross margin exists only for USDT margin.**  INR-margined positions are
  isolated, so every CoinDCX position is placed isolated: one rule, a bounded
  loss per position, and a liquidation price the entry checks against the stop.
* **INR margin trades the same USDT-priced contracts**; only margin and P&L
  settle in rupees, at CoinDCX's published conversion price.
"""
