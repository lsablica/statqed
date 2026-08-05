"""Data-free package/toolchain probe for SQ-0002.

This module deliberately exposes no StatQED production interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from sys import version_info

__all__ = ["RuntimeIdentity", "runtime_identity"]


@dataclass(frozen=True, slots=True)
class RuntimeIdentity:
    """Exact interpreter identity observed by the packaging smoke test."""

    implementation: str
    major: int
    minor: int
    micro: int


def runtime_identity() -> RuntimeIdentity:
    """Return a small immutable value that tests installed-wheel imports."""

    return RuntimeIdentity(
        implementation="cpython",
        major=version_info.major,
        minor=version_info.minor,
        micro=version_info.micro,
    )
