#!/usr/bin/env python3
"""Fetch one immutable probe wheel and verify its expected SHA-256."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import urllib.request


URL = "https://files.pythonhosted.org/packages/6a/29/0ed312ec800fb536f93783215126cee4b8977dcfeccba6f0f44df0cc87d7/pyarrow-25.0.0-cp314-cp314-manylinux_2_28_x86_64.whl"
FILENAME = "pyarrow-25.0.0-cp314-cp314-manylinux_2_28_x86_64.whl"
EXPECTED = "447df764beb07c544f0178a5f6b70ef44b9ecf382b3cdfad4c2d7867353c3887"


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
