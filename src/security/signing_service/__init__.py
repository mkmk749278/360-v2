"""Signing service — the security boundary for Binance request signing.

Per OWNER_BRIEF §3.9 + B18, the signing service is a **separate Python
process** running on the engine VPS under its own Linux user, listening
on a Unix-socket-based JSON RPC.  Engine workers (Position FSM, connect
flow, reconciliation loop) call this service whenever they need to make
a signed Binance request on behalf of a user.

The threat model in one paragraph:

  * Engine main process (FastAPI + scanners + workers) has Firestore
    Admin SDK read access AND aiohttp egress.  A compromise of this
    process yields ciphertext + the ability to send HTTP, but NOT the
    KMS Decrypt IAM permission — KMS access lives only on the signing
    service's Linux user.
  * Signing service has KMS Decrypt IAM + Firestore read AND aiohttp
    egress, but no other access — no signal data, no user database,
    no Telegram bot.  A compromise here yields the ability to sign
    orders, bounded by the symbol allowlist + position cap + global
    kill switch that the engine still enforces.

The plaintext API secret materialises ONLY inside the signing service
process, ONLY for the duration of one signing operation, and NEVER
crosses the Unix socket back to the engine.  The signing service
performs the actual HTTP call to Binance and returns just the
response bytes.

Modules
-------

* :mod:`src.security.signing_service.protocol` — RPC request/response
  dataclasses + JSON codec.  Shared by client + server so the wire
  format is single-sourced.
* :mod:`src.security.signing_service.handler` — the core signing +
  HTTP-call logic.  Where the encrypted blob is read, KMS-unwrapped,
  AES-GCM-decrypted, used to sign, and the call to Binance happens.
  Plaintext-secret lifetime is bounded to one function call here.
* :mod:`src.security.signing_service.server` — asyncio Unix-socket
  server that hosts the handler.
* :mod:`src.security.signing_service.client` — engine-side client
  that the FSM / connect flow / reconciliation call to make signed
  Binance requests.  Hides the Unix socket / JSON wire format from
  callers — they get a typed async function.
* :mod:`src.security.signing_service.__main__` — entry point so the
  service runs via ``python -m src.security.signing_service``.

Deployment
----------

For solo scale: run as a systemd unit under user ``lumin-signer``.
The engine main process runs as user ``lumin-engine``; the socket at
``/var/run/lumin/signing.sock`` is mode ``0660`` owned by
``lumin-signer:lumin-engine`` so only the engine user can connect.
A future hardening would put each process in its own container with a
shared Docker volume for the socket.
"""
