# Python toolchain compatibility prototype

Status: **Experimental**.

This is the package-native SQ-0002 Python packaging probe. It is not the
StatQED Python frontend, is not intended for publication, and defines no
StatQED API or semantics.

The proposed package metadata floor is Python 3.11. The probe builds an sdist
and wheel, installs the wheel into a separate environment, checks metadata,
and runs pytest on exact CPython 3.14.7 and 3.11.15 runtimes. A CPython 3.10.20
installation attempt is retained as the intentional `Requires-Python`
rejection.

The retained preparation uses python-build-standalone release `20260805` for
the exact CPython 3.14.7 development archive and release `20260718` for the
exact CPython 3.11.15 floor archive, uv 0.11.32, and the checked-in
`--require-hashes` wheel lock. The two runtime archives are bound to SHA-256
`a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9`
and `23ccae6f1ff73e8aa8378436f869da003b8eb7d6c95f2bc706f494115ba1447d`.
Python 3.14.6 remains historical evidence because 3.14.7 superseded it on
2026-08-05; it is no longer the proposed development pin. The owned reruns are:

```sh
/usr/bin/bash verify-probe.sh development
/usr/bin/bash verify-probe.sh floor
```

Each dispatcher rechecks the runtime, uv, and lock digests, extracts into a
fresh task-specific directory, runs standard `venv` plus `PIP_NO_INDEX=1`, and
removes the extracted runtime, environments, logs, and caches on exit. Missing
prepared assets return 77 and are not treated as successful tests.

The checked-in results and limitations are summarized in `RESULTS.md`;
command stdout, stderr, timestamps, and environments are retained under
`../logs/python/run-20260803/` and `../logs/python/run-20260805/`. Runtimes, virtual environments, downloaded
wheels, sdists, and package caches are intentionally not versioned.
