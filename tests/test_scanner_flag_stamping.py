"""Regression tests for the soft-gate flag-stamping contract.

The scanner's per-cycle gate chain accumulates flags into a local list
(``_fired_gates``) starting at ~line 3655 of ``src/scanner/__init__.py``.
At the end of the chain (~line 4471) it stamps the joined result onto
``sig.soft_gate_flags`` with a destructive overwrite::

    sig.soft_gate_flags = ",".join(_fired_gates)

That overwrite means **any direct write to ``sig.soft_gate_flags``
between the init and the join is silently lost**.

Pre-fix, the funding-rate gate (~line 4009) and the cross-asset gate
(~line 4045) wrote directly to ``sig.soft_gate_flags`` before the join
fired, so their flags never made it onto the dispatched signal —
subscribers and downstream telemetry never saw FUNDING_BOOST,
FUNDING_PENALTY, or CROSS_ASSET tags even when those gates fired.

The fix routed both writes through ``_fired_gates.append(...)`` so they
flow through the canonical join.  This file guards against the
regression returning by AST-scanning the scanner module:

  * Walks the source file
  * Finds the function containing the ``_fired_gates: list = []`` init
  * Asserts that no ``sig.soft_gate_flags = ...`` assignment exists
    between that init and the canonical join

Writes that happen *after* the join (e.g. ``distribution_long_penalty``
at ~line 4714) are fine — they read the joined value first and append
with comma-strip.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


_SCANNER_PATH = (
    Path(__file__).parent.parent / "src" / "scanner" / "__init__.py"
)


def _scanner_source() -> str:
    return _SCANNER_PATH.read_text()


def _find_init_and_join_lines(source: str) -> tuple[int, int]:
    """Locate the ``_fired_gates: list = []`` init and the canonical
    ``sig.soft_gate_flags = ",".join(_fired_gates)`` overwrite.

    Returns ``(init_line, join_line)`` 1-indexed line numbers.
    """
    init_line = None
    join_line = None
    for i, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if init_line is None and stripped.startswith("_fired_gates: list = []"):
            init_line = i
        # Match the canonical join — ".join(_fired_gates)" rules out the
        # later append patterns that legitimately write to soft_gate_flags.
        if (
            join_line is None
            and "sig.soft_gate_flags" in stripped
            and '","' in stripped
            and ".join(_fired_gates)" in stripped
        ):
            join_line = i
    assert init_line is not None, (
        "Could not locate `_fired_gates: list = []` init in scanner source"
    )
    assert join_line is not None, (
        "Could not locate the canonical "
        "`sig.soft_gate_flags = \",\".join(_fired_gates)` overwrite"
    )
    assert join_line > init_line, "Join must come after init"
    return init_line, join_line


def test_no_direct_soft_gate_flags_writes_between_init_and_join():
    """The flag-stamping contract: every gate flag between the
    ``_fired_gates`` init and the canonical join MUST go through
    ``_fired_gates.append(...)``.  Direct ``sig.soft_gate_flags = ...``
    assignments in that window are silently overwritten by the join.

    Pre-2026-05-08: funding-rate + cross-asset gates wrote directly,
    so their flags never reached dispatched signals."""
    source = _scanner_source()
    init_line, join_line = _find_init_and_join_lines(source)

    tree = ast.parse(source)
    offending: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not (init_line < node.lineno < join_line):
            continue
        for target in node.targets:
            # Match `sig.soft_gate_flags = ...` writes.
            if (
                isinstance(target, ast.Attribute)
                and target.attr == "soft_gate_flags"
                and isinstance(target.value, ast.Name)
                and target.value.id == "sig"
            ):
                snippet = source.splitlines()[node.lineno - 1].strip()
                offending.append((node.lineno, snippet))

    assert not offending, (
        "Direct `sig.soft_gate_flags = ...` writes found between the "
        "_fired_gates init (line {init}) and the canonical join (line "
        "{join}).  These writes will be silently overwritten by the join. "
        "Route them through `_fired_gates.append(...)` instead.\n\n"
        "Offending lines:\n  {offs}".format(
            init=init_line,
            join=join_line,
            offs="\n  ".join(f"line {ln}: {snip}" for ln, snip in offending),
        )
    )


def test_funding_rate_gate_routes_through_fired_gates():
    """Spot-check: the funding-rate gate must call
    ``_fired_gates.append(_fr_flag)`` rather than writing
    ``sig.soft_gate_flags`` directly."""
    source = _scanner_source()
    # Locate the funding-gate block.  We don't pin to exact lines (they
    # drift); instead we check that within the funding-rate handling
    # context (`_fr_flag` is local to it), the only assignment path
    # uses _fired_gates.append.
    assert "_fired_gates.append(_fr_flag)" in source, (
        "Funding-rate gate must route _fr_flag through _fired_gates.append "
        "so the join at end-of-chain preserves it."
    )
    # Negative: no `sig.soft_gate_flags + f",{_fr_flag}"` pattern.
    assert 'sig.soft_gate_flags + f",{_fr_flag}"' not in source, (
        "Direct sig.soft_gate_flags concat for funding flag should be "
        "removed — it gets overwritten by the join."
    )


def test_cross_asset_gate_routes_through_fired_gates():
    """Same contract for the cross-asset gate."""
    source = _scanner_source()
    # The cross-asset adjust uses `CROSS_ASSET:{...:+.0f}` — verify it
    # appends to _fired_gates.  Source-wide check rather than per-line so
    # multi-line append calls are matched.
    assert (
        '_fired_gates.append(\n                                f"CROSS_ASSET:'
        in source
        or '_fired_gates.append(f"CROSS_ASSET:' in source
    ), (
        "Cross-asset gate must route its flag through _fired_gates.append "
        "so the join at end-of-chain preserves it."
    )
    # Negative guard: no direct soft_gate_flags concat for the cross-asset flag.
    assert 'sig.soft_gate_flags + f",CROSS_ASSET:' not in source, (
        "Direct sig.soft_gate_flags concat for cross-asset flag should "
        "be removed — it gets overwritten by the join."
    )
