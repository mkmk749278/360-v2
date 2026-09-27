"""CoinDCX connect-time validation — what can be proved, and nothing more.

Runs once when a user submits a CoinDCX key (``POST /api/coindcx/connect``).
The plaintext secret is a parameter here, used for one signed call, and never
logged, stored or returned.

What this proves:

* **The key works for futures from our server.**  A signed call to the
  futures wallet endpoint, made from the engine's host, succeeds.  If the user
  bound the key to a *different* IP it fails here, which is the one IP mistake
  we can catch.

What it cannot prove, and why the caller also requires an attestation:

* whether the key is bound to our IP at all (an unbound key also succeeds);
* whether it can withdraw.

CoinDCX's API reports neither.  The owner's decision (2026-09-27) is that the
user attests both, the route records the attestation on the key document,
and the signing service refuses any key without one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import aiohttp

from src.utils import get_logger
from src.venues.coindcx import signing as _sign

log = get_logger("venues.coindcx.connect_validator")

_WALLETS_PATH = "/exchange/v1/derivatives/futures/wallets"
_TIMEOUT_S = 8.0


class CoinDCXConnectError(Exception):
    """Base — ``user_message`` is safe to show; ``code`` goes in a header."""

    code = "VALIDATION_UNKNOWN"

    def __init__(self, user_message: str) -> None:
        super().__init__(user_message)
        self.user_message = user_message


class KeyRejectedError(CoinDCXConnectError):
    code = "KEY_REJECTED"


class FuturesUnavailableError(CoinDCXConnectError):
    code = "FUTURES_UNAVAILABLE"


class CoinDCXUnreachableError(CoinDCXConnectError):
    code = "COINDCX_UNREACHABLE"


@dataclass(frozen=True)
class CoinDCXValidation:
    futures_wallet_ok: bool
    #: ``{"USDT": 12.3, "INR": 0.0}`` — free balance per futures wallet, for
    #: the app's first screen after connect.  Never used to size anything.
    balances: Dict[str, float] = field(default_factory=dict)


def _wallet_balances(body: Any) -> Optional[Dict[str, float]]:
    if not isinstance(body, list):
        return None
    out: Dict[str, float] = {}
    for row in body:
        if not isinstance(row, dict):
            continue
        ccy = str(row.get("currency_short_name") or "").upper()
        if not ccy:
            continue
        try:
            out[ccy] = float(row.get("balance") or 0.0)
        except (TypeError, ValueError):
            out[ccy] = 0.0
    return out


async def validate_coindcx_key(
    *,
    api_key: str,
    api_secret: str,
    session: Optional[aiohttp.ClientSession] = None,
) -> CoinDCXValidation:
    """Prove the key reaches the futures wallet from this host."""
    if not api_key or not api_secret:
        raise KeyRejectedError("Enter both the API key and the secret.")
    body_text, headers = _sign.signed_request(api_key, api_secret, {})
    own = session is None
    if session is None:
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=_TIMEOUT_S))
    try:
        async with session.get(
            _sign.BASE_URL + _WALLETS_PATH, data=body_text, headers=headers,
        ) as resp:
            status = resp.status
            try:
                body = await resp.json(content_type=None)
            except (aiohttp.ContentTypeError, ValueError):
                body = None
    except (aiohttp.ClientError, TimeoutError) as exc:
        raise CoinDCXUnreachableError(
            "Could not reach CoinDCX to check your key. Please try again."
        ) from exc
    finally:
        if own:
            await session.close()

    if status in (401, 403):
        raise KeyRejectedError(
            "CoinDCX rejected this key. Check the key and secret, and that the "
            "key is bound to our server IP (not to another address)."
        )
    if not (200 <= status < 300):
        log.warning("coindcx connect: wallets returned HTTP {}", status)
        raise CoinDCXUnreachableError(
            f"CoinDCX answered {status}. Please try again in a moment."
        )
    balances = _wallet_balances(body)
    if balances is None:
        raise FuturesUnavailableError(
            "This key cannot read a CoinDCX futures wallet. Enable futures on "
            "your CoinDCX account and create the key with futures trading on."
        )
    return CoinDCXValidation(futures_wallet_ok=True, balances=balances)
