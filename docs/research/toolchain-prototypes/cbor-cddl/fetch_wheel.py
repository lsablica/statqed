#!/usr/bin/env python3
"""Fetch one immutable probe wheel and verify its expected SHA-256."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import urllib.request


URL = "https://files.pythonhosted.org/packages/c8/cb/6bd33461e8be8ded7ebb0fa38994a63752aefae2b4fcd1b2cc71ee3c06f1/cbor2-6.1.3-cp314-cp314-manylinux_2_28_x86_64.whl"
FILENAME = "cbor2-6.1.3-cp314-cp314-manylinux_2_28_x86_64.whl"
EXPECTED = "ad4f3c6dfc6b83331eb04c6975efb2839ab65a3aa81502bc2b3f7945d4c4aa44"


def main() -> None:
    destination = Path(sys.argv[1])
    destination.mkdir(parents=True, exist_ok=True)
    payload = urllib.request.urlopen(URL, timeout=60).read()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != EXPECTED:
        raise SystemExit(f"wheel SHA-256 mismatch: expected {EXPECTED}, got {actual}")
    (destination / FILENAME).write_bytes(payload)
    print(f"wheel_filename={FILENAME}")
    print(f"wheel_sha256={actual}")


if __name__ == "__main__":
    main()
