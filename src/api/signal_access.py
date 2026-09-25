"""Who may see an ACTIVE signal — the live-signal paywall (owner, 2026-09-25).

Owner direction, verbatim: *"hide active signals only show closed signals and
to active signals we will introduce User need to create Account and new plan
to see active signals and we give first 3 days free access to see active
signals too"*, resolved by AskUserQuestion to:

* **Signals plan**, tier ``signals``, ₹499/mo (Play ``lumin_signals_monthly``),
  below Assist: ``free < signals < assist < auto``. Every automation tier
  includes live signals.
* **3 days free** live access from sign-up, automatic (no tap). Accounts that
  existed before the paywall start get the same 3 days counted from the start.
* **Guests never** see a live signal. That is the guest mode's rule and holds
  whether or not the paywall is on.
* Non-subscribers get a **teaser push** (symbol only, no direction, no levels).

This reverses Business Rule B1 ("signals are free, in full") for ACTIVE
signals only. Closed signals, with their levels and outcomes, stay free.

One knob decides whether the paywall runs: the ``signals_paywall_start``
runtime tunable (ISO date; empty = off). There is deliberately no separate
on/off bool beside it, because a bool and a start date can disagree, and the
state "on, with no start" has no answer to "when do existing users' 3 days
end?".

**Fail direction.** An unparseable start date is reported as
``misconfigured`` and treated as OFF: a typo in ops must never lock every
paying user out of the product they bought, and everyone keeping access for
a day is the recoverable mistake. The one exception is the guest, who is
never shown a live signal, because the guest rule does not depend on this
knob.

This module is pure: it takes an identity and a clock and returns a verdict.
Every route that exposes an active signal asks it, so there is one writer of
the rule and one reader per surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from .auth import TokenClaims, can_see_live_signals_by_tier, effective_tier
from .users import User

# Reasons, surfaced to the app so it can pick its banner without guessing.
REASON_OWNER = "owner"                  # static admin token
REASON_PAYWALL_OFF = "paywall_off"      # no start set (or not reached yet)
REASON_MISCONFIGURED = "misconfigured"  # start set but unparseable → treated as off
REASON_PLAN = "plan"                    # signals / assist / auto (incl. trial + referral grants)
REASON_FREE_WINDOW = "free_window"      # within the 3 free days
REASON_GUEST = "guest"                  # anonymous: create an account first
REASON_LOCKED = "locked"                # free days used up, no plan


@dataclass(frozen=True)
class LiveAccess:
    allowed: bool
    reason: str
    #: When access ends: plan expiry (``plan``) or end of the free days
    #: (``free_window``). None when unbounded or not applicable.
    until: Optional[datetime] = None
    #: The paywall start the verdict was computed against (None = off).
    paywall_start: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "until": self.until.isoformat() if self.until else None,
            "paywall_start": self.paywall_start.isoformat() if self.paywall_start else None,
        }


def parse_start(raw: Any) -> tuple[Optional[datetime], bool]:
    """Parse the tunable. Returns ``(start, misconfigured)``.

    ``""`` / None → ``(None, False)``: paywall off. A value that does not
    parse → ``(None, True)``. A naive value is read as UTC, because the
    engine is UTC end to end.
    """
    text = str(raw or "").strip()
    if not text:
        return None, False
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None, True
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc), False


def _configured_start() -> tuple[Optional[datetime], bool]:
    try:
        from src import runtime_tunables as _rt

        raw = _rt.get("signals_paywall_start")
    except Exception:  # noqa: BLE001 — a tunable read must never 500 a feed
        import config

        raw = getattr(config, "SIGNALS_PAYWALL_START", "")
    return parse_start(raw)


def _free_days() -> int:
    import config

    return max(0, int(getattr(config, "SIGNALS_FREE_ACCESS_DAYS", 3)))


def is_guest(identity: Any) -> bool:
    return isinstance(identity, TokenClaims) and identity.sub.startswith("guest-")


def paywall_active(now: Optional[datetime] = None) -> bool:
    """True once the configured start has been reached."""
    start, _ = _configured_start()
    return start is not None and (now or datetime.now(timezone.utc)) >= start


def live_access(
    identity: Any,
    *,
    now: Optional[datetime] = None,
    start: Any = ...,
    free_days: Optional[int] = None,
) -> LiveAccess:
    """Decide whether ``identity`` may see ACTIVE signals right now.

    ``identity`` is what the ``user_claims`` dependency resolves to: None for
    the static owner token, a :class:`User` for a phone account, a
    :class:`TokenClaims` for a guest or a legacy HS256 token. ``start`` and
    ``free_days`` are injectable for tests; by default they are read from the
    tunable and config.
    """
    now = now or datetime.now(timezone.utc)
    if start is ...:
        start_dt, misconfigured = _configured_start()
    else:
        start_dt, misconfigured = parse_start(start)
    days = _free_days() if free_days is None else max(0, int(free_days))

    if identity is None:
        return LiveAccess(True, REASON_OWNER, paywall_start=start_dt)
    if is_guest(identity):
        return LiveAccess(False, REASON_GUEST, paywall_start=start_dt)
    if misconfigured:
        return LiveAccess(True, REASON_MISCONFIGURED)
    if start_dt is None or now < start_dt:
        return LiveAccess(True, REASON_PAYWALL_OFF, paywall_start=start_dt)

    if isinstance(identity, User):
        tier = effective_tier(identity.tier, identity.paid_until, now=now)
        if can_see_live_signals_by_tier(tier):
            return LiveAccess(True, REASON_PLAN, until=identity.paid_until, paywall_start=start_dt)
        created = identity.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        until = max(created, start_dt) + timedelta(days=days)
        if now < until:
            return LiveAccess(True, REASON_FREE_WINDOW, until=until, paywall_start=start_dt)
        return LiveAccess(False, REASON_LOCKED, until=until, paywall_start=start_dt)

    if isinstance(identity, TokenClaims):
        # Legacy HS256 tokens: the tier travels in the token. There is no
        # account creation time, so the free days count from the start.
        tier = effective_tier(identity.tier, identity.paid_until, now=now)
        if can_see_live_signals_by_tier(tier):
            return LiveAccess(True, REASON_PLAN, until=identity.paid_until, paywall_start=start_dt)
        until = start_dt + timedelta(days=days)
        if now < until and identity.sub.startswith("user-"):
            return LiveAccess(True, REASON_FREE_WINDOW, until=until, paywall_start=start_dt)
        return LiveAccess(False, REASON_LOCKED, until=until, paywall_start=start_dt)

    # An identity shape this module has never seen: refuse rather than guess,
    # because the paywall is on and "unknown" is not a plan.
    return LiveAccess(False, REASON_LOCKED, paywall_start=start_dt)


def item_is_open(item: Any) -> bool:
    """Open/closed for a ``SignalDetail`` (or dict), matching the feed filter.

    ``is_open`` is authoritative; a payload that predates it falls back to
    ``status == "ACTIVE"``, the same legacy rule ``filter_signal_items`` uses.
    """
    if isinstance(item, dict):
        v = item.get("is_open")
        return bool(v) if v is not None else item.get("status") == "ACTIVE"
    fields_set = getattr(item, "model_fields_set", None)
    if fields_set is not None and "is_open" not in fields_set:
        return getattr(item, "status", "") == "ACTIVE"
    v = getattr(item, "is_open", None)
    if v is None:
        return getattr(item, "status", "") == "ACTIVE"
    return bool(v)
