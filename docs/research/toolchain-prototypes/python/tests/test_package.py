from __future__ import annotations

from importlib.metadata import metadata, version
from sys import version_info

from statqed_python_toolchain_probe import RuntimeIdentity, runtime_identity


def test_installed_distribution_metadata() -> None:
    dist = metadata("statqed-python-toolchain-probe")
    assert version("statqed-python-toolchain-probe") == "0.0.0"
    assert dist["Requires-Python"] == ">=3.11"
    assert dist["Name"] == "statqed-python-toolchain-probe"


def test_runtime_identity_uses_the_selected_interpreter() -> None:
    assert runtime_identity() == RuntimeIdentity(
        implementation="cpython",
        major=version_info.major,
        minor=version_info.minor,
        micro=version_info.micro,
    )
    assert (version_info.major, version_info.minor) in {(3, 11), (3, 14)}
