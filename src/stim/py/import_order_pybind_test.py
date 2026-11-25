"""Regression tests for importing Deltakit-Stim after other pybind11 extensions.

Deltakit-Stim must not share pybind11's internals registry with other extension
modules. If it does, whichever module is imported first owns the registry and, on
macOS, exceptions raised from Deltakit-Stim (e.g. ``pybind11::stop_iteration`` while
iterating a ``PauliString``) surface as ``RuntimeError: Caught an unknown exception!``.
See https://github.com/Deltakit/deltakit/issues/310.

Each case runs in a fresh interpreter because the registry is owned by the first
extension imported in the process.
"""

import importlib.util
import subprocess
import sys

import pytest

_SNIPPET = """
import {first}
import deltakit_stim
assert list(deltakit_stim.PauliString("XYZ")) == [1, 2, 3]
assert [int(p) for p in deltakit_stim.PauliString("_X")] == [0, 1]
t = deltakit_stim.Tableau.from_named_gate("H")
assert list(t.z_output(0)) == [1]
"""


@pytest.mark.parametrize("first", ["stim", "contourpy", "matplotlib"])
def test_import_after_other_pybind11_extension(first: str) -> None:
    if importlib.util.find_spec(first) is None:
        pytest.skip(f"{first} is not installed")
    result = subprocess.run(
        [sys.executable, "-c", _SNIPPET.format(first=first)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
