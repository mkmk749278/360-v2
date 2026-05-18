"""Tests for src.security.binance_connect_validator.

We mock at the ``_signed_get`` boundary rather than mocking aiohttp
end-to-end — keeps tests focused on the validation logic without
fragile HTTP plumbing.  The signed-request helper itself is exercised
by the apiRestrictions / fapi-balance roundtrip in production via the
operator smoke-test (``docs/server-side-execution-setup.md``).

What we pin here:

* Each failure mode (withdraw=true, futures=false, ip_restrict=false,
  ip-not-whitelisted -2014, bad-key -2015) raises the EXACT typed
  exception the route handler maps to a specific HTTP 400.
* On success: the validator runs both calls (apiRestrictions +
  fapi-balance) — proving futures access actually works, not just
  the flag being on.
* The plaintext api_key / api_secret pass through unmodified to the
  signed-request helper (no accidental truncation or encoding bug
  that would silently break signing).
* Network errors / 5xx surface as ``BinanceUnreachableError`` so the
  route returns 503 (retry) rather than 400 (user error).
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.security import binance_connect_validator as validator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _restrictions_response(
    *,
    enable_withdrawals: bool = False,
    enable_futures: bool = True,
    ip_restrict: bool = True,
) -> dict:
    """Build a realistic ``/sapi/v1/account/apiRestrictions`` response."""
    return {
        "ipRestrict": ip_restrict,
        "createTime": 1623840271000,
        "enableWithdrawals": enable_withdrawals,
        "enableInternalTransfer": True,
        "permitsUniversalTransfer": True,
        "enableVanillaOptions": False,
        "enableReading": True,
        "enableFutures": enable_futures,
        "enableMargin": False,
        "enableSpotAndMarginTrading": False,
    }


def _balance_response() -> list:
    """``/fapi/v2/balance`` returns a list of asset balances."""
    return [
        {"asset": "USDT", "balance": "100.00000000", "availableBalance": "100.00"},
    ]


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_success_runs_both_calls_and_returns_ok() -> None:
    """Compliant key: both calls succeed, all three flags come back True
    on the returned dataclass.  Verify both calls were invoked — proves
    we don't short-circuit after just the flag check."""
    with patch.object(
        validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.side_effect = [
            _restrictions_response(),
            _balance_response(),
        ]
        result = await validator.validate_binance_key(
            api_key="user_api_key_abc",
            api_secret="user_api_secret_xyz",
        )
    assert result.withdraw_disabled_ok is True
    assert result.futures_enabled_ok is True
    assert result.ip_whitelist_ok is True
    assert mock_signed.call_count == 2
    # apiRestrictions first, then balance — order matters because the
    # flag checks must run before we exercise the futures wallet.
    first_call_path = mock_signed.call_args_list[0].kwargs["path"]
    second_call_path = mock_signed.call_args_list[1].kwargs["path"]
    assert first_call_path == "/sapi/v1/account/apiRestrictions"
    assert second_call_path == "/fapi/v2/balance"


@pytest.mark.asyncio
async def test_validate_passes_credentials_unmodified_to_signed_get() -> None:
    """The api_key / api_secret values must pass through to the
    signed-request helper UNCHANGED.  Any truncation / encoding bug
    here would silently break signing and surface as KEY_INVALID,
    far from the bug."""
    with patch.object(
        validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.side_effect = [
            _restrictions_response(),
            _balance_response(),
        ]
        await validator.validate_binance_key(
            api_key="K" * 64,
            api_secret="S" * 64,
        )
    for call in mock_signed.call_args_list:
        assert call.kwargs["api_key"] == "K" * 64
        assert call.kwargs["api_secret"] == "S" * 64


# ---------------------------------------------------------------------------
# Failure mode: withdraw enabled
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_withdraw_enabled_raises_typed_error() -> None:
    """The single most important blast-radius check.  A withdraw-enabled
    key MUST NEVER be persisted, no permissive mode, no admin override.
    Test pins the typed exception so route changes can't silently
    downgrade this to a generic warning."""
    with patch.object(
        validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.return_value = _restrictions_response(
            enable_withdrawals=True
        )
        with pytest.raises(validator.WithdrawEnabledError):
            await validator.validate_binance_key(
                api_key="k", api_secret="s"
            )
        # Critically — after the withdraw check fails, we MUST NOT
        # make the fapi/v2/balance call (it would consume rate budget
        # for a key we're about to reject).  Verify only one call.
        assert mock_signed.call_count == 1


# ---------------------------------------------------------------------------
# Failure mode: futures disabled
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_futures_disabled_raises_typed_error() -> None:
    with patch.object(
        validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.return_value = _restrictions_response(
            enable_futures=False
        )
        with pytest.raises(validator.FuturesDisabledError):
            await validator.validate_binance_key(api_key="k", api_secret="s")


# ---------------------------------------------------------------------------
# Failure mode: ip_restrict disabled
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ip_restrict_disabled_raises_typed_error() -> None:
    """The key has Futures + no withdraw, but IP whitelist isn't on.
    B18 requires IP restrict — this is the "mobile-IP unusable" case
    Binance forced on us in late 2023."""
    with patch.object(
        validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.return_value = _restrictions_response(
            ip_restrict=False
        )
        with pytest.raises(validator.IpRestrictDisabledError):
            await validator.validate_binance_key(api_key="k", api_secret="s")


# ---------------------------------------------------------------------------
# Failure mode: -2014 (IP not whitelisted)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ip_not_whitelisted_raises_typed_error() -> None:
    """Binance returns -2014 when the engine VPS IP isn't on the
    user's whitelist.  We propagate that as the specific typed
    exception so the route can echo back the engine IP for the user
    to add."""
    with patch.object(
        validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.side_effect = validator.IpNotWhitelistedError(
            validator.IpNotWhitelistedError.user_message
        )
        with pytest.raises(validator.IpNotWhitelistedError):
            await validator.validate_binance_key(api_key="k", api_secret="s")


# ---------------------------------------------------------------------------
# Failure mode: invalid key
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invalid_key_raises_typed_error() -> None:
    """-2015 / wrong key → KeyInvalidError so the route returns 400
    with a "double-check the values" message rather than 503."""
    with patch.object(
        validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.side_effect = validator.KeyInvalidError(
            validator.KeyInvalidError.user_message
        )
        with pytest.raises(validator.KeyInvalidError):
            await validator.validate_binance_key(api_key="k", api_secret="s")


# ---------------------------------------------------------------------------
# Failure mode: network / Binance down
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_binance_unreachable_raises_typed_error() -> None:
    """5xx / network — propagate as the unreachable type so the route
    returns 503 (retry) instead of 400 (user-blame)."""
    with patch.object(
        validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.side_effect = validator.BinanceUnreachableError(
            "Binance returned 503"
        )
        with pytest.raises(validator.BinanceUnreachableError):
            await validator.validate_binance_key(api_key="k", api_secret="s")


@pytest.mark.asyncio
async def test_unreachable_on_balance_call_after_restrictions_pass() -> None:
    """Edge case: apiRestrictions succeeds (flags fine) but the
    fapi-balance call falls over.  Must propagate, not silently
    succeed — futures-wallet not activated is a legit reason to fail
    validation and we don't want to discover it at first auto-trade."""
    with patch.object(
        validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.side_effect = [
            _restrictions_response(),
            validator.BinanceUnreachableError("Binance returned 503"),
        ]
        with pytest.raises(validator.BinanceUnreachableError):
            await validator.validate_binance_key(api_key="k", api_secret="s")


# ---------------------------------------------------------------------------
# Signature helper — pure function, easy to test
# ---------------------------------------------------------------------------


def test_sign_query_is_deterministic_hmac_sha256() -> None:
    """HMAC-SHA256 of a known input must produce a known output —
    pinning this catches a future refactor that accidentally swaps
    the hash algorithm or changes the input encoding."""
    secret = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"
    query = "symbol=BTCUSDT&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&timestamp=1499827319559"
    # Computed deterministically from the inputs above — pinned so any
    # future code change that swaps the hash algorithm, the secret
    # encoding, or the byte ordering will fail this test loudly
    # rather than silently produce keys Binance can't verify.
    expected = "9495fce965f74f4818f29ede2b9667a87f0a4972565671cc458abf4ff179b9ae"
    assert validator._sign_query(secret, query) == expected
