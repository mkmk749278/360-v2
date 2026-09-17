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


def _step_env_names() -> set[str]:
    """Names in the deploy step's `env:` block, i.e. what is available remotely."""
    text = WORKFLOW.read_text(encoding="utf-8")
    block = text[text.index("\n        env:\n"):text.index("\n        with:\n")]
    return set(re.findall(r"^\s+([A-Z0-9_]+): \$\{\{ secrets\.", block, re.M))


def _forwarded_names() -> set[str]:
    """Names in `envs:`, i.e. what the action actually ships to the remote."""
    text = WORKFLOW.read_text(encoding="utf-8")
    m = re.search(r"^\s+envs: (.+)$", text, re.M)
    assert m, "deploy.yml no longer declares `envs:` — secrets would not reach the script"
    return {n.strip() for n in m.group(1).split(",") if n.strip()}


def _script_text() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    return text[text.index("          script: |"):]


def test_every_referenced_secret_is_actually_written_into_the_env():
    """A reference without a write is a secret that reaches the box as nothing.

    This is the half-wired shape: the `${{ secrets.X }}` interpolation is
    there, so the diff looks complete, and no line ever lands in `.env`.
    """
    script = _script_text()
    missing = sorted(n for n in _referenced_secrets() if f"put_env {n} " not in script)
    assert not missing, (
        f"referenced by deploy.yml but never written into .env: {missing}. "
        "Add a `put_env NAME \"$NAME\"` line beside the others, or name it in "
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
    assert "put_env GEMINI_API_KEY " in text, (
        "deploy.yml no longer writes the key into .env"
    )


def test_no_secret_is_interpolated_into_the_remote_script_text():
    """The strongest property this workflow has, and the one worth pinning.

    **The premise of the guard this replaces was wrong, and I had told the
    owner otherwise three times.** That guard asserted an explicit
    `::add-mask::` for `GH_PAT` and was captioned as the thing keeping a
    write-capability secret out of the Actions log, with the other secrets
    named as "unmasked" and therefore exposed. The vendor says otherwise:

        GitHub Actions automatically redacts the contents of all GitHub
        secrets that are printed to workflow logs.

    So nothing was reaching the log in clear, and `::add-mask::` only
    re-registers a string the runner already holds. **Reading the file
    produced a hypothesis about behaviour, not a measurement of it** — and the
    measurement was one documentation page away.

    What the same reading *did* turn up is real, and it is what this file now
    guards. A secret interpolated into the script's TEXT has to survive shell
    quoting and then sed syntax, and two of those failures are silent (see
    `test_put_env_is_the_only_writer...` below). A value that never enters the
    command text cannot be mangled by the command text — which is also the
    only defence against the vendor's own caveat that redaction "is not
    guaranteed" once a value is transformed.
    """
    script = _script_text()
    leaked = sorted(set(_REFERENCED.findall(script)))
    assert not leaked, (
        f"{leaked} interpolated into the remote script's text. Add the secret "
        "to the step's `env:` block and to `envs:`, then reference it as "
        "\"$NAME\" so the value is a shell variable rather than source code."
    )


def test_every_forwarded_secret_is_defined_and_every_defined_one_is_forwarded():
    """`env:` and `envs:` are two halves of one contract, and they fail in
    opposite directions.

    Defined but not forwarded: the remote never receives it, `set -u` makes
    `"$NAME"` an unbound variable, and the deploy fails loudly. Recoverable.

    Forwarded but not defined: the action ships an EMPTY value, `put_env`
    writes `NAME=`, and the deploy prints "✅ Deploy complete" over a blanked
    credential. That is the dangerous direction and it is why this asserts both
    ways rather than one.
    """
    defined = _step_env_names()
    forwarded = _forwarded_names()
    assert defined, "the deploy step has no `env:` block"
    assert not (forwarded - defined), (
        f"forwarded in `envs:` but not defined in `env:`: "
        f"{sorted(forwarded - defined)} — these would arrive EMPTY and blank "
        "the credential silently"
    )
    assert not (defined - forwarded), (
        f"defined in `env:` but missing from `envs:`: "
        f"{sorted(defined - forwarded)} — these never reach the remote script"
    )


def test_put_env_is_the_only_writer_and_no_value_passes_through_a_sed_replacement():
    """Measured, not reasoned, on 2026-09-17.

    Every key used to be written with ``sed -i "s|^KEY=.*|KEY=$VALUE|" .env``,
    and in a sed REPLACEMENT `&` expands to the whole match while `\\`
    escapes. Run against real values:

        'abc&def'  -> BINANCE_API_SECRET=abcBINANCE_API_SECRET=olddef
        'a\\nb'     -> the line split in two, second entry bogus
        'abc|def'  -> sed: unknown option to `s' (loud, at least)

    The first two are **silent**: `set -e` never fires, the deploy reports
    success, and the engine then cannot authenticate with nothing anywhere
    saying why. A credential path whose corruption is invisible is the shape
    this repo has paid for under several names.

    `put_env` addresses only the KEY in its sed — a literal this workflow
    controls — and writes the value with `printf`, verbatim.
    """
    script = _script_text()
    assert "put_env()" in script, "the put_env helper is gone"
    assert "printf '%s=%s\\n'" in script, (
        "put_env no longer writes the value with printf — a value built into a "
        "sed replacement or an echo -e is back to interpreting `&` and `\\`"
    )
    # The defect itself: a sed substitution whose REPLACEMENT half contains an
    # expansion. Addressing a key (`/^KEY=/d`) is fine and is what put_env does.
    #
    # Comment lines are skipped deliberately: the block above DOCUMENTS the old
    # `sed -i "s|^KEY=.*|KEY=$VALUE|"` form, and a guard that cannot tell code
    # from the prose explaining it would force the next author to delete the
    # explanation to get green. Caught by this test firing on its own docs.
    offenders = [
        ln.strip() for ln in script.splitlines()
        if not ln.lstrip().startswith("#")
        and re.search(r'sed\s+-i\s+"s\|\^[A-Z0-9_]*=?\.\*\|.*\$', ln)
    ]
    assert not offenders, (
        "a secret is being written through a sed replacement again, which "
        f"silently corrupts any value containing `&` or a backslash: {offenders}"
    )


def test_the_pat_stays_masked_because_git_prints_the_url_it_dialled():
    """Narrowed, not deleted — the instance survives even though the general
    claim did not.

    Automatic redaction covers a verbatim appearance, so this is belt and
    braces rather than the only protection. It is kept for one specific reason:
    the PAT is embedded in a clone/remote URL, and git prints the URL it
    dialled in its own error messages. That is the transformed-value case the
    vendor says redaction cannot guarantee, on the one secret here that is
    embedded in a larger string.
    """
    script = _script_text()
    assert 'echo "::add-mask::$GH_PAT"' in script, (
        "the PAT is no longer masked before it is used in a URL"
    )
    mask_at = script.index("::add-mask::$GH_PAT")
    first_url_use = min(
        (script.index(frag) for frag in ("x-access-token:${GH_PAT}",) if frag in script),
        default=None,
    )
    assert first_url_use is not None, "the PAT is no longer used in a URL — is this guard stale?"
    assert mask_at < first_url_use, (
        "the mask must be registered BEFORE the first use that can echo the value"
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
