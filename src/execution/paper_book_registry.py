"""Per-user paper book registry + fan-out facade (2026-06-20).

The engine historically ran ONE shared :class:`PaperOrderManager` as
``TradeMonitor._order_manager`` in paper mode — a single simulated book all
users viewed.  That made "individual paper selection" impossible: there was
no per-user paper execution to attach a per-user eligibility filter to.

This module makes paper genuinely per-user **without touching the live money
path** (the owner-chosen "isolated paper registry" design):

* :class:`PaperBookRegistry` — one :class:`PaperOrderManager` per ``user_id``,
  lazily created, each persisting its own PnL ledger so books are isolated.
* :class:`PaperBookFanout` — implements the same coroutine surface as
  :class:`PaperOrderManager` / :class:`OrderManager`, so it is a drop-in for
  ``TradeMonitor._order_manager``.  Each lifecycle call TradeMonitor makes
  (``execute_signal`` at entry; ``close_partial`` for pre-TP/TP; ``close_full``
  for SL / invalidation / expiry) is fanned out to every paper/both user whose
  per-user **paper** eligibility (symbol / path / regime) admits the signal,
  honouring each user's per-symbol management mode (``full`` vs ``entry``).

Because the facade plugs in exactly where the single book did, TradeMonitor's
tested lifecycle/timing logic is reused unchanged — it just talks to N books.

Entry-only paper semantics mirror live entry-only: the position opens (entry),
closes on SL / expiry / cancel (protective), but is NOT pre-TP'd, NOT TP-laddered
and SURVIVES engine invalidation — the user manages the upside.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Set

from config import MAX_POSITION_USD, POSITION_SIZE_PCT
from src.paper_order_manager import PaperOrderManager
from src.utils import get_logger

log = get_logger("execution.paper_book_registry")

# Modes that opt a user into paper simulation.
_PAPER_MODES: frozenset = frozenset({"paper", "both"})

# Close reasons that an entry-only position must SURVIVE (the engine hands
# the exit to the user).  Everything else (sl_hit, expired, cancelled,
# full_tp_hit) still closes it — the protective SL is honoured.
_ENTRY_ONLY_SURVIVES: frozenset = frozenset({"invalidated"})


def _setup_token(signal: Any) -> str:
    raw = getattr(signal, "setup_class", None)
    if raw is None:
        return ""
    val = getattr(raw, "value", raw)
    return str(val).upper()


def _regime_token(signal: Any) -> str:
    return str(getattr(signal, "entry_regime", "") or "").upper()


def _symbol_token(signal: Any) -> str:
    return str(getattr(signal, "symbol", "") or "").upper()


class PaperBookRegistry:
    """Lazily holds one :class:`PaperOrderManager` per ``user_id``.

    Each book persists to ``<books_dir>/paper_pnl_user_<id>.json`` so per-user
    cumulative paper PnL survives restarts, isolated from every other user and
    from the legacy shared ledger.
    """

    def __init__(
        self,
        *,
        books_dir: Path | str = Path("data") / "paper_books",
        starting_equity_usd: float = 1000.0,
        position_size_pct: float = POSITION_SIZE_PCT,
        max_position_usd: float = MAX_POSITION_USD,
        risk_manager_factory: Optional[Any] = None,
        factory: Optional[Any] = None,
    ) -> None:
        self._books_dir = Path(books_dir)
        self._starting_equity = starting_equity_usd
        self._position_size_pct = position_size_pct
        self._max_position_usd = max_position_usd
        # ``risk_manager_factory(user_id) -> RiskManager`` gives each user
        # book its OWN risk manager so one user's daily-loss breaker / open
        # concurrency never trips another's.  None → books run without a risk
        # manager (paper sandbox, no per-user limits) — same as the shared
        # book did before its risk_manager was wired.
        self._risk_manager_factory = risk_manager_factory
        # Injectable for tests: factory(user_id, pnl_path) -> manager-like.
        self._factory = factory
        self._books: Dict[int, PaperOrderManager] = {}

    def _pnl_path_for(self, user_id: int) -> Path:
        return self._books_dir / f"paper_pnl_user_{int(user_id)}.json"

    def _trades_db_path_for(self, user_id: int) -> Path:
        return self._books_dir / f"paper_trades_user_{int(user_id)}.sqlite"

    @staticmethod
    def pnl_history_mode_for(user_id: int) -> str:
        """The daily-bucket key for a user's paper history (``paper:<uid>``).
        Engine-wide paper = aggregate of every ``paper:*`` bucket."""
        return f"paper:{int(user_id)}"

    def get(self, user_id: int) -> PaperOrderManager:
        uid = int(user_id)
        book = self._books.get(uid)
        if book is None:
            if self._factory is not None:
                book = self._factory(uid, self._pnl_path_for(uid))
            else:
                rm = (
                    self._risk_manager_factory(uid)
                    if self._risk_manager_factory is not None
                    else None
                )
                book = PaperOrderManager(
                    position_size_pct=self._position_size_pct,
                    max_position_usd=self._max_position_usd,
                    starting_equity_usd=self._starting_equity,
                    risk_manager=rm,
                    pnl_path=self._pnl_path_for(uid),
                    trades_db_path=self._trades_db_path_for(uid),
                    pnl_history_mode=self.pnl_history_mode_for(uid),
                )
            self._books[uid] = book
        return book

    def get_if_exists(self, user_id: int) -> Optional[PaperOrderManager]:
        return self._books.get(int(user_id))

    def all_books(self) -> Dict[int, PaperOrderManager]:
        return dict(self._books)


class PaperBookFanout:
    """``OrderManager``-compatible facade fanning lifecycle calls out to the
    per-user paper books in a :class:`PaperBookRegistry`.

    Drop-in replacement for the single ``PaperOrderManager`` as
    ``TradeMonitor._order_manager`` when the engine runs in paper mode.
    """

    def __init__(
        self,
        registry: PaperBookRegistry,
        *,
        overrides_store: Optional[Any] = None,
        user_store: Optional[Any] = None,
    ) -> None:
        self._registry = registry
        # Injected for tests; default to the live singletons at call time so
        # boot order doesn't matter.
        self._overrides_store = overrides_store
        self._user_store = user_store
        # signal_id -> {user_id: management_mode}  — who took each signal and how.
        self._holders: Dict[str, Dict[int, str]] = {}

    # -- store accessors (late-bound to the singletons) --------------------

    def _stores(self):
        ov = self._overrides_store
        us = self._user_store
        if ov is None or us is None:
            try:
                from src.api import user_overrides as _uo
                from src.api import users as _users
                ov = ov or _uo.get_singleton()
                us = us or _users.get_singleton()
            except Exception:
                return None, None
        return ov, us

    def _paper_users(self) -> Dict[int, str]:
        """``{user_id: firebase_uid}`` for every paper/both user."""
        ov, us = self._stores()
        if ov is None or us is None:
            return {}
        try:
            uids = ov.list_user_ids_with_mode(_PAPER_MODES)
        except Exception:
            return {}
        out: Dict[int, str] = {}
        for uid in uids:
            try:
                user = us.get_by_id(int(uid))
            except Exception:
                user = None
            fb = getattr(user, "firebase_uid", None) if user else None
            if fb:
                out[int(uid)] = fb
        return out

    def _eligible(self, firebase_uid: str, signal: Any) -> bool:
        """Apply the user's PAPER eligibility (symbol / path / regime)."""
        try:
            from src.api import user_overrides as _uo
            sym_fs, path_fs, regime_fs = _uo.resolve_paper_preferences_uid(
                firebase_uid
            )
        except Exception:
            return True  # soft-fail toward including the signal
        if sym_fs is not None and _symbol_token(signal) not in sym_fs:
            return False
        if path_fs is not None and _setup_token(signal) not in path_fs:
            return False
        if regime_fs is not None and _regime_token(signal) not in regime_fs:
            return False
        return True

    def _management_mode(self, firebase_uid: str, signal: Any) -> str:
        try:
            from src.api import user_overrides as _uo
            return _uo.resolve_symbol_management_uid(
                firebase_uid, _symbol_token(signal)
            )
        except Exception:
            return "full"

    # -- OrderManager-compatible surface -----------------------------------

    @property
    def is_enabled(self) -> bool:
        return True

    async def execute_signal(self, signal: Any) -> Optional[str]:
        return await self.place_market_order(signal)

    async def place_market_order(
        self, signal: Any, *, quantity: Optional[float] = None
    ) -> Optional[str]:
        signal_id = str(getattr(signal, "signal_id", "") or "")
        if not signal_id:
            return None
        opened_any = False
        holders: Dict[int, str] = self._holders.setdefault(signal_id, {})
        for uid, fb in self._paper_users().items():
            if not self._eligible(fb, signal):
                continue
            mode = self._management_mode(fb, signal)
            book = self._registry.get(uid)
            try:
                oid = await book.place_market_order(signal, quantity=quantity)
            except Exception as exc:  # one user's failure never blocks others
                log.warning(
                    "paper fanout: place_market_order failed uid=%s sig=%s: %s",
                    uid, signal_id, exc,
                )
                continue
            if oid is not None:
                holders[uid] = mode
                opened_any = True
        if not holders:
            self._holders.pop(signal_id, None)
        # Synthetic id so TradeMonitor marks the signal active when ANY book
        # took it; None when nobody did (so it isn't tracked needlessly).
        return f"paper-fanout-{signal_id}" if opened_any else None

    async def close_partial(
        self,
        signal: Any,
        fraction: float,
        tp_level: int = 0,
        *,
        current_price: Optional[float] = None,
    ) -> Optional[str]:
        signal_id = str(getattr(signal, "signal_id", "") or "")
        holders = self._holders.get(signal_id)
        if not holders:
            return None
        any_closed = False
        for uid, mode in list(holders.items()):
            # Entry-only books are NOT pre-TP'd or TP-laddered — the user owns
            # the exit (the protective SL close still fires via close_full).
            if mode == "entry":
                continue
            book = self._registry.get_if_exists(uid)
            if book is None:
                continue
            try:
                res = await book.close_partial(
                    signal, fraction, tp_level, current_price=current_price
                )
                any_closed = any_closed or (res is not None)
            except Exception as exc:
                log.warning(
                    "paper fanout: close_partial failed uid=%s sig=%s: %s",
                    uid, signal_id, exc,
                )
        return f"paper-fanout-{signal_id}" if any_closed else None

    async def close_full(
        self,
        signal: Any,
        *,
        reason: str,
        current_price: Optional[float] = None,
    ) -> Optional[str]:
        signal_id = str(getattr(signal, "signal_id", "") or "")
        holders = self._holders.get(signal_id)
        if not holders:
            return None
        any_closed = False
        survivors: Dict[int, str] = {}
        for uid, mode in list(holders.items()):
            # Entry-only positions survive engine invalidation — the user
            # manages that exit.  All other reasons (sl_hit, expired,
            # cancelled, full_tp_hit) close every holder.
            if mode == "entry" and reason in _ENTRY_ONLY_SURVIVES:
                survivors[uid] = mode
                continue
            book = self._registry.get_if_exists(uid)
            if book is None:
                continue
            try:
                res = await book.close_full(
                    signal, reason=reason, current_price=current_price
                )
                any_closed = any_closed or (res is not None)
            except Exception as exc:
                log.warning(
                    "paper fanout: close_full failed uid=%s sig=%s reason=%s: %s",
                    uid, signal_id, reason, exc,
                )
        # Keep only entry-only survivors on the books; drop everyone we closed.
        if survivors:
            self._holders[signal_id] = survivors
        else:
            self._holders.pop(signal_id, None)
        return f"paper-fanout-{signal_id}" if any_closed else None

    async def add_dca_entry(
        self, signal: Any, *, current_price: Optional[float] = None
    ) -> Optional[str]:
        signal_id = str(getattr(signal, "signal_id", "") or "")
        holders = self._holders.get(signal_id)
        if not holders:
            return None
        any_added = False
        for uid in list(holders.keys()):
            book = self._registry.get_if_exists(uid)
            if book is None:
                continue
            try:
                res = await book.add_dca_entry(signal, current_price=current_price)
                any_added = any_added or (res is not None)
            except Exception as exc:
                log.warning(
                    "paper fanout: add_dca_entry failed uid=%s sig=%s: %s",
                    uid, signal_id, exc,
                )
        return f"paper-fanout-{signal_id}" if any_added else None

    async def close_all_open_positions(
        self, reason: str = "user_close_all"
    ) -> Dict[str, Any]:
        """Flatten every user's paper book.

        Mirrors :meth:`PaperOrderManager.close_all_open_positions`'s
        contract exactly — same ``reason`` parameter, same
        ``{"closed_count", "realised_pnl_total"}`` return shape — because
        the API close-all route calls whichever of the two is installed
        as the engine's order manager.  (2026-07-16 audit: the old
        signature took no reason — TypeError from the route — and did
        ``int += dict`` on the book result, so the fanout close-all had
        never actually closed anything.)
        """
        closed_count = 0
        realised_pnl_total = 0.0
        for book in self._registry.all_books().values():
            try:
                res = await book.close_all_open_positions(reason)
                if isinstance(res, dict):
                    closed_count += int(res.get("closed_count", 0))
                    realised_pnl_total += float(res.get("realised_pnl_total", 0.0))
            except Exception as exc:
                log.warning("paper fanout: close_all_open_positions failed: %s", exc)
        self._holders.clear()
        return {
            "closed_count": closed_count,
            "realised_pnl_total": realised_pnl_total,
        }

    def reset_state(self) -> None:
        for book in self._registry.all_books().values():
            try:
                book.reset_state()
            except Exception as exc:
                log.warning("paper fanout: reset_state failed: %s", exc)
        self._holders.clear()

    # -- aggregate status (engine-wide view across all per-user books) -----

    @property
    def simulated_pnl_total(self) -> float:
        return round(
            sum(b.simulated_pnl_total for b in self._registry.all_books().values()),
            4,
        )

    @property
    def current_equity_usd(self) -> float:
        return round(
            sum(b.current_equity_usd for b in self._registry.all_books().values()),
            4,
        )

    @property
    def open_position_count(self) -> int:
        return sum(
            b.open_position_count for b in self._registry.all_books().values()
        )

    # -- per-user accessors (for the read API) -----------------------------

    def book_for_user(self, user_id: int) -> Optional[PaperOrderManager]:
        return self._registry.get_if_exists(user_id)

    def pnl_history_mode_for(self, user_id: int) -> str:
        """``paper:<uid>`` — the pnl_history bucket key for a user's book."""
        return self._registry.pnl_history_mode_for(user_id)

    def trades_db_path_for(self, user_id: int):
        """Filesystem path to a user's own paper-trades SQLite DB — the
        read API lists ``/api/trades`` straight from here when books are on."""
        return self._registry._trades_db_path_for(user_id)

    def holders_for_signal(self, signal_id: str) -> Set[int]:
        return set(self._holders.get(str(signal_id), {}).keys())

    def positions_for_user(self, user_id: int) -> Dict[str, Any]:
        """The ``signal_id -> _PaperPosition`` dict for one user's book (or
        empty).  The snapshot open-positions builder uses this as the
        per-user 'is this signal open for me?' filter — the per-user book IS
        the visibility boundary (replacing subscription-window filtering)."""
        book = self._registry.get_if_exists(user_id)
        pos = getattr(book, "_positions", None) if book is not None else None
        return pos if isinstance(pos, dict) else {}

    @property
    def _positions(self) -> Dict[str, Any]:
        """Engine-wide merged open-positions view across every per-user book —
        keeps legacy/engine-wide callers (phantom-row filter) working.  On a
        signal_id collision across users, last book wins; that's acceptable
        for the boolean 'is this signal open anywhere?' use."""
        merged: Dict[str, Any] = {}
        for book in self._registry.all_books().values():
            bp = getattr(book, "_positions", None)
            if isinstance(bp, dict):
                merged.update(bp)
        return merged
