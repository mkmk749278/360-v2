"""Guards on the test suite itself (2026-09-26 test-suite audit).

Each rule below is a defect the audit found in this tree, fixed, and then
pinned here so it cannot come back quietly. They read the tests' own syntax
trees — a rule stated only in CLAUDE.md is a rule the next test forgets.

* ``if sig is None: pytest.skip(...)`` — a fixture that stops producing a
  signal turned into a green run. Two liquidation-reversal geometry tests
  skipped on EVERY run for months after a threshold change, hiding that the
  fallback TP geometry was untested.
* ``asyncio.run`` inside a test leaves the main thread with no event loop and
  breaks tests in OTHER files, only in full-suite order (CLAUDE.md, 2026-09-02).
* a real ``time.sleep`` of half a second or more is either a timing race or
  wasted suite time; the one that existed (1s, JWT refresh) also hid a weak
  ``>=`` assertion. Use an injectable clock.
* drawing from the GLOBAL random state without seeding it in the same file
  makes the test's data depend on whatever ran before it.
"""
from __future__ import annotations

import ast
import functools
from pathlib import Path

TESTS = Path(__file__).resolve().parent

_GLOBAL_RANDOM = {"uniform", "random", "choice", "choices", "randint", "gauss",
                  "shuffle", "sample"}
_GLOBAL_NP_RANDOM = {"rand", "randn", "normal", "uniform", "random", "choice",
                     "randint", "shuffle", "permutation"}


@functools.lru_cache(maxsize=1)
def _findings() -> dict:
    """ONE walk over every test file, all rules at once (~160k lines)."""
    found: dict[str, list[str]] = {
        "skip_on_none": [], "asyncio_run": [], "long_sleep": [], "unseeded": [],
    }
    for path in sorted(TESTS.rglob("*.py")):
        rel = str(path.relative_to(TESTS))
        tree = ast.parse(path.read_text(encoding="utf-8"))
        draws = seeds = False
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and _is_none_test(node.test):
                if any(_is_skip(c) for stmt in node.body for c in ast.walk(stmt)):
                    found["skip_on_none"].append(f"{rel}:{node.lineno}")
                continue
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            f = node.func
            owner = f.value.id if isinstance(f.value, ast.Name) else None
            if owner == "asyncio" and f.attr == "run":
                found["asyncio_run"].append(f"{rel}:{node.lineno}")
            elif (owner == "time" and f.attr == "sleep" and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, (int, float))
                    and node.args[0].value >= 0.5):
                found["long_sleep"].append(f"{rel}:{node.lineno}")
            elif owner == "random" and f.attr in _GLOBAL_RANDOM:
                draws = True
            elif (isinstance(f.value, ast.Attribute) and f.value.attr == "random"
                    and isinstance(f.value.value, ast.Name)
                    and f.value.value.id in ("np", "numpy")
                    and f.attr in _GLOBAL_NP_RANDOM):
                draws = True
            if f.attr == "seed":
                seeds = True
        if draws and not seeds and path.name != Path(__file__).name:
            found["unseeded"].append(rel)
    return found


def _is_none_test(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Compare)
        and len(node.ops) == 1
        and isinstance(node.ops[0], ast.Is)
        and isinstance(node.comparators[0], ast.Constant)
        and node.comparators[0].value is None
    )


def _is_skip(call: ast.AST) -> bool:
    return (
        isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "skip"
    )


def test_no_skip_when_the_code_under_test_returned_nothing() -> None:
    offenders = _findings()["skip_on_none"]
    assert not offenders, (
        "`if x is None: pytest.skip(...)` turns a broken fixture into a pass — "
        "assert it is not None instead:\n  " + "\n  ".join(offenders)
    )


def test_no_asyncio_run_in_tests() -> None:
    offenders = _findings()["asyncio_run"]
    assert not offenders, "write `async def test_…` and await:\n  " + "\n  ".join(offenders)


def test_no_long_real_sleeps() -> None:
    offenders = _findings()["long_sleep"]
    assert not offenders, "inject a clock instead of sleeping:\n  " + "\n  ".join(offenders)


def test_global_random_draws_are_seeded_in_the_same_file() -> None:
    offenders = _findings()["unseeded"]
    assert not offenders, (
        "draws from the global random state with no seed in the file — use "
        "np.random.default_rng(seed) / random.Random(seed):\n  " + "\n  ".join(offenders)
    )
