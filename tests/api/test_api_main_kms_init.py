"""Tests for the isolated api container's KMS boot init.

Regression pin for the production bug where the ``api`` container
(``API_PROCESS_ISOLATED=true``, live on VPS) never called
``init_kms_client`` at boot, so every ``POST /api/binance/connect``
died at the KMS preflight with HTTP 500 "Server misconfiguration —
KMS not initialised" — while single-process mode (engine-served HTTP,
KMS inited by ``bootstrap.py``) worked.  Session-14's isolation sweep
(#565–#569) wired ``init_keystore()`` and ``init_kill_switch()`` into
``src.api.main`` but left KMS out.

``_maybe_init_kms`` must mirror the engine's boot contract
(``bootstrap.py`` KMS block):

* all four ``GCP_KMS_*`` env vars set → init, credentials from the
  Firebase service-account path (ADC when empty);
* any var missing → skipped, no import of the KMS SDK;
* init failure → warn, never raise (api boot must survive).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.api import main as api_main
from src.security import kms_client

_KMS_ENV = {
    "GCP_KMS_PROJECT_ID": "test-project",
    "GCP_KMS_LOCATION": "asia-south1",
    "GCP_KMS_KEYRING": "lumin-keys",
    "GCP_KMS_KEY_NAME": "binance-kek",
}


@pytest.fixture(autouse=True)
def _isolate_kms(monkeypatch: pytest.MonkeyPatch):
    """Reset the KMS singleton + env between tests."""
    for var in _KMS_ENV:
        monkeypatch.delenv(var, raising=False)
    kms_client.reset_for_test()
    yield
    kms_client.reset_for_test()


def _set_all_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var, value in _KMS_ENV.items():
        monkeypatch.setenv(var, value)


def test_init_called_with_all_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """All four GCP_KMS_* set → init_kms_client called with exactly those
    values and the Firebase SA path, and the helper reports success."""
    _set_all_env(monkeypatch)
    mock_init = MagicMock()
    monkeypatch.setattr(kms_client, "init_kms_client", mock_init)

    assert api_main._maybe_init_kms("/data/firebase-service-account.json") is True
    mock_init.assert_called_once_with(
        project_id="test-project",
        location="asia-south1",
        keyring="lumin-keys",
        key_name="binance-kek",
        service_account_path="/data/firebase-service-account.json",
    )


@pytest.mark.parametrize("missing", sorted(_KMS_ENV))
def test_skipped_when_any_env_var_missing(
    monkeypatch: pytest.MonkeyPatch, missing: str
) -> None:
    """Any one of the four vars missing → no init attempt at all (the
    engine's bootstrap contract: partial config is treated as unset)."""
    _set_all_env(monkeypatch)
    monkeypatch.delenv(missing)
    mock_init = MagicMock()
    monkeypatch.setattr(kms_client, "init_kms_client", mock_init)

    assert api_main._maybe_init_kms("/data/firebase-service-account.json") is False
    mock_init.assert_not_called()


def test_init_failure_is_non_fatal(monkeypatch: pytest.MonkeyPatch) -> None:
    """A throwing GCP client build must not propagate — the api container
    still has to boot for read-only users when KMS is broken."""
    _set_all_env(monkeypatch)
    monkeypatch.setattr(
        kms_client,
        "init_kms_client",
        MagicMock(side_effect=RuntimeError("no such keyring")),
    )

    assert api_main._maybe_init_kms("/data/firebase-service-account.json") is False


def test_empty_sa_path_falls_back_to_adc(monkeypatch: pytest.MonkeyPatch) -> None:
    """No Firebase SA path configured → service_account_path=None so the
    KMS client falls back to ADC (mirrors bootstrap's ``or None``)."""
    _set_all_env(monkeypatch)
    mock_init = MagicMock()
    monkeypatch.setattr(kms_client, "init_kms_client", mock_init)

    assert api_main._maybe_init_kms("") is True
    assert mock_init.call_args.kwargs["service_account_path"] is None


def test_connect_route_500_without_kms_and_ok_after_init() -> None:
    """End-to-end contract: the connect route's KMS preflight is exactly
    ``kms_client.is_initialised()`` — False before init (the production
    500), True after a successful init."""
    assert kms_client.is_initialised() is False
    kms_client._client = kms_client.KmsClient(  # what init would register
        key_ref=kms_client.KmsKeyRef(
            project_id="p", location="l", keyring="r", key_name="k"
        ),
        client=MagicMock(),
    )
    assert kms_client.is_initialised() is True
