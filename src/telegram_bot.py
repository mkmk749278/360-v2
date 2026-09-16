"""Telegram bot – rich signal formatting, admin commands, free/premium routing.

Uses aiohttp to call the Telegram Bot API directly (no heavy library needed).
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Optional

import aiohttp

from config import (
    TELEGRAM_ADMIN_CHAT_ID,
    TELEGRAM_BOT_TOKEN,
)
from src.utils import get_logger

log = get_logger("telegram")


class TelegramBot:
    """Lightweight async Telegram sender + command poller."""

    def __init__(self) -> None:
        self._token = TELEGRAM_BOT_TOKEN
        self._base = f"https://api.telegram.org/bot{self._token}"
        self._session: Optional[aiohttp.ClientSession] = None
        self._offset: int = 0
        self._running = False

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------

    async def send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown") -> bool:
        """Send a message to *chat_id*. Returns True on success.

        Retry behaviour:
        * **Markdown parse error** (400 + "can't parse entities"): retried once
          as plain text so the user still receives the signal.
        * **Rate limit** (429): waits ``parameters.retry_after`` seconds from
          the response body, then retries (up to 3 total attempts).
        * **Server errors** (5xx): exponential back-off (1 s, 2 s, 4 s) with up
          to 3 total attempts.
        * **Timeout**: exponential back-off, up to 3 total attempts.
        * **Other 4xx**: returned immediately as False (not recoverable).
        """
        if not self._token:
            log.debug("Telegram token not configured – message not sent")
            return False
        if parse_mode == "Markdown":
            text = self._sanitize_markdown(text)
        session = await self._ensure_session()
        url = f"{self._base}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return True
                    body = await resp.text()
                    log.warning("Telegram send failed (%s): %s", resp.status, body)

                    # Retry as plain text if Markdown parsing failed (400 only)
                    if resp.status == 400 and "can't parse entities" in body:
                        log.info("Retrying message as plain text after Markdown parse failure")
                        plain_payload = {"chat_id": chat_id, "text": text}
                        async with session.post(
                            url, json=plain_payload, timeout=aiohttp.ClientTimeout(total=10)
                        ) as retry_resp:
                            if retry_resp.status == 200:
                                return True
                            retry_body = await retry_resp.text()
                            log.warning("Telegram plain-text retry failed (%s): %s", retry_resp.status, retry_body)
                        return False  # 400 errors are not retried further

                    # HTTP 429: rate limited – honor Retry-After from response body
                    if resp.status == 429:
                        try:
                            data = json.loads(body)
                            retry_after = float(data.get("parameters", {}).get("retry_after", 1))
                        except (json.JSONDecodeError, AttributeError, TypeError):
                            retry_after = 1.0
                        log.info(
                            "Telegram rate limit (429) – waiting %.1fs before retry (attempt %d/%d)",
                            retry_after, attempt + 1, max_attempts,
                        )
                        await asyncio.sleep(retry_after)
                        continue

                    # HTTP 5xx: server error – exponential back-off
                    if resp.status >= 500:
                        wait = 2 ** attempt  # 1 s, 2 s, 4 s
                        log.info(
                            "Telegram server error (%d) – retrying in %ds (attempt %d/%d)",
                            resp.status, wait, attempt + 1, max_attempts,
                        )
                        await asyncio.sleep(wait)
                        continue

                    # Other 4xx: not recoverable
                    return False

            except asyncio.TimeoutError:
                wait = 2 ** attempt
                log.warning(
                    "Telegram send timeout – retrying in %ds (attempt %d/%d)",
                    wait, attempt + 1, max_attempts,
                )
                await asyncio.sleep(wait)
                continue
            except Exception as exc:
                log.error("Telegram send error: %s", exc)
                return False

        return False

    async def send_admin_alert(self, text: str) -> bool:
        """Send a message to the admin chat."""
        if TELEGRAM_ADMIN_CHAT_ID:
            return await self.send_message(TELEGRAM_ADMIN_CHAT_ID, f"🔔 *Admin Alert*\n{text}")
        return False

    async def send_document(
        self,
        chat_id: str,
        document: bytes,
        filename: str,
        caption: Optional[str] = None,
    ) -> bool:
        """Upload a file to *chat_id* via the Bot API ``sendDocument`` endpoint.

        ``document`` is the raw file bytes.  ``filename`` is the name the user
        sees on the Telegram side (and the filetype Telegram infers from).
        Returns True on success, False on any failure (token missing, network
        error, 4xx).  Used by ``/report`` and ``/diag``.
        """
        if not self._token:
            log.debug("Telegram token not configured – document not sent")
            return False
        session = await self._ensure_session()
        url = f"{self._base}/sendDocument"
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                form = aiohttp.FormData()
                form.add_field("chat_id", str(chat_id))
                if caption:
                    form.add_field("caption", caption)
                form.add_field(
                    "document",
                    document,
                    filename=filename,
                    content_type="application/octet-stream",
                )
                async with session.post(
                    url, data=form, timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        return True
                    body = await resp.text()
                    log.warning("Telegram sendDocument failed (%s): %s", resp.status, body)
                    if resp.status == 429:
                        try:
                            data = await resp.json()
                            wait = int(data.get("parameters", {}).get("retry_after", 1))
                        except Exception:
                            wait = 2 ** attempt
                        await asyncio.sleep(wait)
                        continue
                    if 500 <= resp.status < 600:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return False
            except asyncio.TimeoutError:
                await asyncio.sleep(2 ** attempt)
                continue
            except Exception as exc:
                log.error("Telegram sendDocument error: %s", exc)
                return False
        return False




    # ------------------------------------------------------------------
    # Rich signal formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _escape_md(text: str) -> str:
        """Escape Markdown V1 special characters in dynamic text fields.

        Telegram's legacy MarkdownV1 uses ``*``, ``_``, `` ` ``, and ``[``
        as formatting markers.  Dynamic values such as ``liquidity_info``
        may contain these characters and must be escaped so they are rendered
        as literal text rather than misinterpreted as entity boundaries.
        """
        for ch in ("\\", "*", "_", "`", "["):
            text = text.replace(ch, f"\\{ch}")
        return text

    @staticmethod
    def _sanitize_markdown(text: str) -> str:
        """Ensure Markdown V1 entity markers are properly paired in *text*.

        Counts unescaped occurrences of ``*``, ``_``, and `` ` ``.  If any
        character has an odd count (i.e. an unmatched opener or closer),
        **all** unescaped occurrences of that character are escaped so that
        Telegram's parser never encounters an unterminated entity boundary.

        This is applied to the fully-composed message just before sending,
        acting as a safety net for dynamic content that may slip through
        individual :meth:`_escape_md` call-sites.
        """
        for ch in ("*", "_", "`"):
            pattern = r"(?<!\\)" + re.escape(ch)
            count = len(re.findall(pattern, text))
            if count % 2 != 0:
                text = re.sub(pattern, f"\\{ch}", text)
        return text

    # Channel display names (strip 360_ prefix, use friendly names)

    # Estimated hold time per channel
    _ESTIMATED_HOLD = {
        "360_SCALP":            "~1-2h",
        "360_SCALP_FVG":        "~1-2h",
        "360_SCALP_CVD":        "~1-2h",
        "360_SCALP_VWAP":       "~1-2h",
        "360_SCALP_DIVERGENCE": "~1-2h",
        "360_SCALP_SUPERTREND": "~1-2h",
        "360_SCALP_ICHIMOKU":   "~1-2h",
        "360_SCALP_ORDERBLOCK": "~1-2h",
    }



    # format_watchlist_signal removed in app-era doctrine reset.  Sub-65
    # confidence signals no longer reach Telegram formatting; the free
    # channel keeps macro / regime-shift / signal-close storytelling but
    # no preview signals.




    # ------------------------------------------------------------------
    # Admin command polling
    # ------------------------------------------------------------------

    async def poll_commands(self, handler, on_new_member=None) -> None:
        """Long-poll for commands from any chat that starts with ``/``.

        Admin-only commands are gated inside the *handler* by comparing
        ``chat_id`` against ``TELEGRAM_ADMIN_CHAT_ID``.

        Parameters
        ----------
        handler:
            Async callable ``(text, chat_id)`` that handles ``/`` commands.
        on_new_member:
            Optional async callable ``(user_id)`` invoked when a user joins
            one of the bot's channels (``my_chat_member`` update with status
            changing from ``left``/``kicked`` to ``member``).
        """
        self._running = True
        _allowed: str = json.dumps(["message", "my_chat_member"])
        _consecutive_errors: int = 0
        _MAX_POLL_BACKOFF: float = 60.0
        # Clear stale updates before starting to poll so commands queued
        # during a long boot (pair seeding, etc.) are not re-processed.
        try:
            session = await self._ensure_session()
            url = f"{self._base}/getUpdates"
            params: dict[str, str] = {"offset": "-1", "timeout": "0", "allowed_updates": _allowed}
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("result", [])
                    if results:
                        self._offset = results[-1]["update_id"] + 1
                        log.info("Cleared %d stale Telegram updates", len(results))
        except Exception as exc:
            log.debug("Failed to clear stale updates: %s", exc)
        while self._running:
            try:
                if not self._token:
                    await asyncio.sleep(30)
                    continue
                session = await self._ensure_session()
                url = f"{self._base}/getUpdates"
                params = {"offset": str(self._offset), "timeout": "20", "allowed_updates": _allowed}
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        _consecutive_errors += 1
                        backoff = min(5 * (2 ** _consecutive_errors), _MAX_POLL_BACKOFF)
                        await asyncio.sleep(backoff)
                        continue
                    data = await resp.json()
                _consecutive_errors = 0  # Reset on success
                for update in data.get("result", []):
                    self._offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    text = msg.get("text", "")
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    if text.startswith("/"):
                        log.info("Telegram command received: %r from chat_id=%s", text.split()[0], chat_id)
                        _t = asyncio.create_task(handler(text, chat_id))
                        def _cmd_done(t: asyncio.Task, _cmd: str = text, _cid: str = chat_id) -> None:
                            if t.cancelled():
                                log.warning("Command task cancelled: cmd=%r chat_id=%s", _cmd, _cid)
                            elif t.exception() is not None:
                                log.error(
                                    "Command handler error: cmd=%r chat_id=%s error=%s",
                                    _cmd, _cid, t.exception(),
                                )
                        _t.add_done_callback(_cmd_done)
                    # Handle channel subscription events
                    mcm = update.get("my_chat_member", {})
                    if mcm and on_new_member is not None:
                        new_status = mcm.get("new_chat_member", {}).get("status", "")
                        old_status = mcm.get("old_chat_member", {}).get("status", "")
                        if new_status == "member" and old_status in ("left", "kicked"):
                            user_id = str(mcm.get("from", {}).get("id", ""))
                            if user_id:
                                try:
                                    await on_new_member(user_id)
                                except Exception as exc:
                                    log.debug("Welcome DM failed for user %s: %s", user_id, exc)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                _consecutive_errors += 1
                backoff = min(5 * (2 ** _consecutive_errors), _MAX_POLL_BACKOFF)
                log.debug("Command poll error (retry in %.0fs): %s", backoff, exc)
                await asyncio.sleep(backoff)

    async def stop(self) -> None:
        self._running = False
        if self._session and not self._session.closed:
            await self._session.close()
