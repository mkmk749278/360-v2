"""Tests for the Telegram OTP delivery provider (OWNER_BRIEF B13)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
from unittest.mock import patch

import pytest

from src.api.otp_delivery import (
    DeliveryStatus,
    TelegramOtpProvider,
    build_provider_from_env,
)


@dataclass
class _FakeUser:
    """Minimal stand-in for ``api.users.User`` — only the field the
    provider touches (``telegram_chat_id``) needs to be present."""
    phone_e164: str
    telegram_chat_id: Optional[str]


class _FakeUserStore:
    """Test double mirroring the subset of ``UserStore`` the provider uses."""

    def __init__(self, users_by_phone: Optional[dict] = None) -> None:
        self._users = users_by_phone or {}

    def get_by_phone(self, phone_e164: str):
        return self._users.get(phone_e164)


class _FakeTelegramBot:
    """Test double for ``TelegramBot`` — records each ``send_message``
    invocation and lets a test rig configure the return value or an
    exception per call."""

    def __init__(
        self,
        return_value: bool = True,
        raise_on_send: Optional[Exception] = None,
    ) -> None:
        self.calls: List[Tuple[str, str]] = []
        self._return_value = return_value
        self._raise = raise_on_send

    async def send_message(
        self, chat_id: str, text: str, parse_mode: str = "Markdown"
    ) -> bool:
        self.calls.append((chat_id, text))
        if self._raise is not None:
            raise self._raise
        return self._return_value


class TestTelegramOtpProvider:
    @pytest.mark.asyncio
    async def test_send_ok_when_user_has_chat_id(self):
        bot = _FakeTelegramBot()
        users = _FakeUserStore({
            "+15551234567": _FakeUser(
                phone_e164="+15551234567", telegram_chat_id="710718010",
            ),
        })
        provider = TelegramOtpProvider(telegram_bot=bot, user_store=users)

        result = await provider.send("+15551234567", "123456")

        assert result.status == DeliveryStatus.OK
        assert result.channel_used == "telegram"
        # One DM sent to the user's chat_id; OTP code present in body
        assert bot.calls == [("710718010", bot.calls[0][1])]
        assert "123456" in bot.calls[0][1]
        # Don't leak the full chat_id in the detail string (only prefix)
        assert "710718010" not in result.detail

    @pytest.mark.asyncio
    async def test_missing_chat_id_returns_unsupported(self):
        """Phone lookup succeeds but ``telegram_chat_id`` is None — user
        hasn't completed the bot-bind step.  Must return
        ``UNSUPPORTED_CHANNEL`` so the chain falls through to fallback."""
        bot = _FakeTelegramBot()
        users = _FakeUserStore({
            "+15551234567": _FakeUser(
                phone_e164="+15551234567", telegram_chat_id=None,
            ),
        })
        provider = TelegramOtpProvider(telegram_bot=bot, user_store=users)

        result = await provider.send("+15551234567", "123456")

        assert result.status == DeliveryStatus.UNSUPPORTED_CHANNEL
        assert result.channel_used == "telegram"
        # No DM attempted when chat_id is missing
        assert bot.calls == []

    @pytest.mark.asyncio
    async def test_user_not_found_returns_unsupported(self):
        """Phone not in UserStore at all — same fall-through behaviour."""
        bot = _FakeTelegramBot()
        users = _FakeUserStore({})  # empty store
        provider = TelegramOtpProvider(telegram_bot=bot, user_store=users)

        result = await provider.send("+15551234567", "123456")

        assert result.status == DeliveryStatus.UNSUPPORTED_CHANNEL
        assert bot.calls == []

    @pytest.mark.asyncio
    async def test_send_returns_false_surfaces_provider_error(self):
        """Telegram refused the DM (chat blocked, rate-limited, 4xx).
        Must surface as ``PROVIDER_ERROR`` (no fallthrough — SMS won't
        rescue a broken Telegram chat)."""
        bot = _FakeTelegramBot(return_value=False)
        users = _FakeUserStore({
            "+15551234567": _FakeUser(
                phone_e164="+15551234567", telegram_chat_id="710718010",
            ),
        })
        provider = TelegramOtpProvider(telegram_bot=bot, user_store=users)

        result = await provider.send("+15551234567", "123456")

        assert result.status == DeliveryStatus.PROVIDER_ERROR
        assert "False" in result.detail or "rate-limit" in result.detail

    @pytest.mark.asyncio
    async def test_send_exception_surfaces_provider_error(self):
        """``send_message`` raised an exception — surface as
        ``PROVIDER_ERROR``, do not fall through."""
        bot = _FakeTelegramBot(raise_on_send=RuntimeError("boom"))
        users = _FakeUserStore({
            "+15551234567": _FakeUser(
                phone_e164="+15551234567", telegram_chat_id="710718010",
            ),
        })
        provider = TelegramOtpProvider(telegram_bot=bot, user_store=users)

        result = await provider.send("+15551234567", "123456")

        assert result.status == DeliveryStatus.PROVIDER_ERROR
        assert "boom" in result.detail


class TestFactoryWiresTelegram:
    @pytest.mark.asyncio
    async def test_factory_builds_telegram_primary_when_injected(self):
        bot = _FakeTelegramBot()
        users = _FakeUserStore({
            "+15551234567": _FakeUser(
                phone_e164="+15551234567", telegram_chat_id="710718010",
            ),
        })
        with patch("config.OTP_PRIMARY_CHANNEL", "telegram"), \
             patch("config.OTP_FALLBACK_CHANNEL", "log"):
            provider = build_provider_from_env(
                telegram_bot=bot, user_store=users,
            )
        # Should be a chain (telegram primary + log fallback)
        # Sending against a known user routes via Telegram (primary)
        result = await provider.send("+15551234567", "424242")
        assert result.channel_used == "telegram"
        assert result.status == DeliveryStatus.OK
        # Sending against an unknown phone falls through to LogOnly
        result2 = await provider.send("+19999999999", "424243")
        assert result2.channel_used == "log"
        assert result2.status == DeliveryStatus.OK

    def test_factory_raises_when_telegram_selected_without_injectables(self):
        """Misconfiguration — ``OTP_PRIMARY_CHANNEL=telegram`` but
        bootstrap forgot to pass telegram_bot/user_store.  Crash at boot
        with a clear error message rather than silently misroute."""
        with patch("config.OTP_PRIMARY_CHANNEL", "telegram"), \
             patch("config.OTP_FALLBACK_CHANNEL", ""):
            with pytest.raises(ValueError, match="telegram_bot / user_store"):
                build_provider_from_env(
                    telegram_bot=None, user_store=None,
                )
