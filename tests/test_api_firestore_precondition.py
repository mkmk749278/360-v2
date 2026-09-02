"""The api container must not be blinder than the engine (2026-09-02).

`src/api/main.py` initialised the keystore, the kill switch, the runtime
tunables and the dispatch log inside the Firebase-Admin conditional, which
requires BOTH ``FIREBASE_PROJECT_ID`` and ``FIREBASE_SERVICE_ACCOUNT_PATH``.
``src/bootstrap.py`` requires only the project and falls back to ADC.

That is not a deployment detail.  It meant the api container could be blind to
Firestore while the engine traded perfectly — and every surface the owner and
the subscriber read is served by the blind one.  It rendered as "kill switch
never initialised" on /control, "Trading briefly paused for everyone — trading
resumes automatically" on a paying user's Trade tab, and a 503 on the
emergency stop, against B18's five-second requirement.

Asserted on the TREE rather than by reading the file, because the failure is a
condition being one token stricter in one of two places, which is exactly what
a reviewer's eye slides over.
"""
from __future__ import annotations

import ast
import inspect


def _guard_names_over(module, marker: str) -> set:
    """Names appearing in every ``if`` enclosing the call to *marker*."""
    tree = ast.parse(inspect.getsource(module))
    parents: dict = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    target = None
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == marker
        ):
            target = node
            break
    assert target is not None, f"no call to {marker} found"
    names: set = set()
    cur = target
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, ast.If):
            names |= {
                n.id for n in ast.walk(cur.test) if isinstance(n, ast.Name)
            }
    return names


def test_the_api_container_gates_the_keystore_on_the_project_alone():
    """The service-account path must NOT be part of the condition — ADC is the
    credential fallback, exactly as the engine does it."""
    import src.api.main as api_main

    guards = _guard_names_over(api_main, "init_keystore")
    assert "firebase_project_id" in guards
    assert "firebase_sa_path" not in guards, (
        "requiring the SA path here is what made the api container blind while "
        "the engine traded — the kill switch and the app's Trade tab both read "
        "from this process"
    )


def test_the_engine_and_the_api_container_agree_on_the_precondition():
    """One precondition, two call sites.  A future credential change must not
    be able to make them diverge without somebody seeing that there are two."""
    import src.api.main as api_main
    import src.bootstrap as bootstrap

    api = _guard_names_over(api_main, "init_keystore")
    engine = _guard_names_over(bootstrap, "init_keystore")
    assert ("firebase_sa_path" in api) == ("firebase_sa_path" in engine)
    assert ("firebase_project_id" in api) == ("firebase_project_id" in engine)


def test_the_keystore_is_given_none_not_an_empty_path_for_adc():
    """``init_keystore("")`` is not ADC — it is a credentials error.  The
    fallback only works if the empty string becomes ``None``."""
    import src.api.main as api_main

    src = inspect.getsource(api_main)
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "init_keystore"
        ):
            arg = node.keywords[0].value
            assert isinstance(arg, ast.BoolOp) and isinstance(arg.op, ast.Or), (
                "the service-account path must be passed as `path or None`"
            )
            return
    raise AssertionError("no init_keystore call found")
