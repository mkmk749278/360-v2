"""Execution venues beside Binance.

Binance keeps its own modules (``src/execution``, ``src/security``) unchanged.
A second venue lives here in its own package with its own key store, its own
position store and its own reconciler, so no Binance consumer — the FSM, the
reconciler, the pre-TP dispatcher, the trail governor, the worker manager —
can ever send a Binance call for a position that lives somewhere else.

See ``docs/COINDCX_VENUE_PLAN_2026_09_27.md``.
"""

#: Venues a user may choose for execution.  ``binance`` is the default and the
#: only value an existing user can hold until they choose otherwise.
VENUE_BINANCE = "binance"
VENUE_COINDCX = "coindcx"
VENUES = (VENUE_BINANCE, VENUE_COINDCX)
