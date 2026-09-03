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


def test_every_exemption_carries_a_reason():
    """An exemption nobody had to justify is how a list grows past what it was
    approved for."""
    for name, reason in NOT_ENV_LINES.items():
        assert reason.strip(), f"{name} is exempt with no reason given"
