"""A secret referenced by the deploy workflow must actually be written to .env.

**Paid for on 2026-09-03.** `GEMINI_API_KEY` was added to the repository's
GitHub secrets and nothing happened, because `deploy.yml` writes a
**hand-maintained list** of secrets into the VPS `.env` and the new one was not
on it. The key sat in GitHub, correct and useless, while the ops page read
`NOT CONFIGURED` — a state indistinguishable from nobody having set it.

The workflow's own comment already said it, six lines above where the block
belonged:

    GitHub secrets don't reach the engine unless injected here (same pattern
    as Binance/OpenAI above).

What this guard can and cannot check — stated, because the first cut got it
wrong
--------------------------------------------------------------------------
The tempting check is "every secret the engine reads must be injected here".
It was written, and it failed against **thirteen** names — `NEWS_API_KEY`,
`TWILIO_AUTH_TOKEN`, `EXCHANGE_API_SECRET` and the rest — every one of which is
set directly in the VPS `.env` and has no GitHub secret at all. Making them
pass would have meant a thirteen-entry exemption list asserting a property
about thirteen subsystems nobody had checked: a hand-kept list defended by
another hand-kept list.

**The repository cannot see which GitHub secrets exist**, so the broad
invariant is not checkable from here, and a guard that claims a property it
cannot verify is the defect this repo has recorded under several names. So
this file checks the two things that ARE derivable:

1. every ``${{ secrets.X }}`` the deploy step references is also *written*
   into `.env` — the half-wired case, where somebody adds the reference and
   forgets the write, or renames one side;
2. the Gemini key specifically, pinned by name at both ends, because it is the
   one this cost.
"""
from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = REPO / ".github" / "workflows" / "deploy.yml"

#: `${{ secrets.NAME }}` references in the workflow.
_REFERENCED = re.compile(r"secrets\.([A-Z0-9_]+)")

#: Secrets the workflow references for something other than writing a .env
#: line — the SSH transport itself, and the runner's own credentials. Each is
#: named so the exemption is a decision rather than an oversight.
NOT_ENV_LINES: dict[str, str] = {
    "VPS_HOST": "ssh target, not an engine value",
    "VPS_USER": "ssh user, not an engine value",
    "VPS_SSH_KEY": "ssh private key, consumed by the action",
    "VPS_PORT": "ssh port, not an engine value",
    "GH_PAT": "used to clone/push from the runner",
    "BACKUP_PASSPHRASE": "consumed by the backup workflow, not written to .env",
    "VPS_DEPLOY_PUBKEY": "re-authorised into ~/.ssh/authorized_keys so the deploy key survives an OS reinstall",
}


def _referenced_secrets() -> set[str]:
    text = WORKFLOW.read_text(encoding="utf-8")
    return {n for n in _REFERENCED.findall(text) if n not in NOT_ENV_LINES}


def test_every_referenced_secret_is_actually_written_into_the_env():
    """A reference without a write is a secret that reaches the box as nothing.

    This is the half-wired shape: the `${{ secrets.X }}` interpolation is
    there, so the diff looks complete, and no line ever lands in `.env`.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    missing = sorted(n for n in _referenced_secrets() if f"^{n}=" not in text)
    assert not missing, (
        f"referenced by deploy.yml but never written into .env: {missing}. "
        "Add the grep/sed/echo block beside the others, or name it in "
        "NOT_ENV_LINES with the reason it is used another way."
    )


def test_the_gemini_key_is_injected_at_both_ends():
    """Pinned by name, because this is the one that cost a round trip.

    The derived check above would pass again if the injection block were
    deleted along with the reference; this one fails if the engine still wants
    the key and the workflow has stopped delivering it.
    """
    reads_it = "GEMINI_API_KEY" in (REPO / "src" / "llm_client.py").read_text(encoding="utf-8")
    text = WORKFLOW.read_text(encoding="utf-8")
    assert reads_it, "llm_client no longer reads GEMINI_API_KEY — is this guard stale?"
    assert "secrets.GEMINI_API_KEY" in text, "deploy.yml no longer reads the GitHub secret"
    assert "^GEMINI_API_KEY=" in text, "deploy.yml no longer writes the key into .env"


def test_a_write_capability_secret_is_masked_in_the_deploy_log():
    """The derived check above proves a secret is DELIVERED. It says nothing
    about whether delivering it prints it.

    This guard was written for `SLACK_PACKET_WEBHOOK_URL`, which was a write
    capability on the owner's channel. That lane was deleted on 2026-09-16, so
    the instance is gone and the PROPERTY is not: the deploy step interpolates
    secrets into a shell script whose stdout is relayed back into the Actions
    log, and a capability secret must be masked before it can be echoed.

    Re-pointed at `GH_PAT` rather than deleted — narrow an invariant whose
    subject changed, do not drop it. Pinned by name rather than derived,
    because "which secrets are capabilities" is a judgement about each one and
    not a property of the file.

    Known gap, deliberately NOT fixed here: `BINANCE_API_SECRET`,
    `TELEGRAM_BOT_TOKEN` and `NOWPAYMENTS_IPN_SECRET` are delivered by this
    same workflow and are NOT masked. That is a finding about the deploy, and a
    finding and a fix are separate deliverables — widening the mask set touches
    the deploy for a live trading box and wants its own change.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "secrets.GH_PAT" in text, (
        "deploy.yml no longer delivers GH_PAT — is this guard stale?"
    )
    assert "::add-mask::${{ secrets.GH_PAT }}" in text, (
        "a write-capability secret reaches the deploy log unmasked"
    )


def test_the_slack_lane_is_gone_and_the_box_is_purged():
    """The Slack packet lane was deleted on 2026-09-16 (owner: the app is the
    only surface, "no need of slack too").

    Two halves, and the second is the one a deletion normally forgets.
    Removing the injection stops the secret being DELIVERED; it does not clean
    the box, because the last deploy already wrote
    `SLACK_PACKET_WEBHOOK_URL` into the VPS `.env` and that URL is a write
    capability on the channel. A credential no code reads is exactly the one
    nobody audits, so the deploy purges the keys it used to write.

    This is also the guard against a silent re-arm: re-adding the injection
    without re-adding the lane would put a live capability back on a box whose
    engine has no reader for it.
    """
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "secrets.SLACK_PACKET_WEBHOOK_URL" not in workflow, (
        "the deploy delivers a webhook for a lane that no longer exists"
    )
    assert "sed -i '/^SLACK_PACKET_/d' .env" in workflow, (
        "the deploy no longer purges the stale Slack keys from the VPS .env"
    )
    assert not (REPO / "src" / "slack_packet.py").exists(), (
        "src/slack_packet.py is back — the lane was deleted, not disabled"
    )
    env_example = (REPO / ".env.example").read_text(encoding="utf-8")
    assert "SLACK_PACKET" not in env_example, (
        "the bootstrap .env still declares the deleted lane's keys"
    )


def test_every_exemption_carries_a_reason():
    """An exemption nobody had to justify is how a list grows past what it was
    approved for."""
    for name, reason in NOT_ENV_LINES.items():
        assert reason.strip(), f"{name} is exempt with no reason given"
