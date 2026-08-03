# Python toolchain compatibility prototype

Status: **Experimental**.

This is the package-native SQ-0002 Python packaging probe. It is not the
StatQED Python frontend, is not intended for publication, and defines no
StatQED API or semantics.

The proposed package metadata floor is Python 3.11. The probe builds an sdist
and wheel, installs the wheel into a separate environment, checks metadata,
and runs pytest on exact CPython 3.14.6 and 3.11.15 runtimes. A CPython 3.10.20
installation attempt is retained as the intentional `Requires-Python`
rejection.

Run `python3 run_probes.py --help` for the isolated `/tmp` cache/runtime setup
and the exact probe commands. Preparation needs network access to obtain the
managed runtimes and hash-locked wheelhouse. Subsequent probes use standard
`venv` plus `PIP_NO_INDEX=1` and were rerun without network access.

The checked-in results and limitations are summarized in `RESULTS.md`;
command stdout, stderr, timestamps, and environments are retained under
`../logs/python/run-20260803/`. Runtimes, virtual environments, downloaded
wheels, sdists, and package caches are intentionally not versioned.
