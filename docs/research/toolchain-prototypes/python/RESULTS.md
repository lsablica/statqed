# SQ-0002 Python compatibility findings

Status: **Experimental**. Evidence cutoff: 2026-08-05. This recommends a
later frontend bootstrap policy; it does not create or publish a production
package and does not put Python in a trusted verification path.

## Recommendation

- Development/reference interpreter: exact CPython 3.14.7, released
  2026-08-05. The official source release has XZ-tarball SHA-256
  `3b48dac8fb59f62eaa67ac83c1eb12bda1b7a08406dd286e252c11a66be27f81`.
  The directly tested runtime is the distinct python-build-standalone 20260805
  x86-64 GNU/Linux asset from target commit
  `76b41240bc8dfe753a54b2e32c8941e536568be8`, SHA-256
  `a3a4e4b81b138960c7c546694df8a77578c0b6aa46d47e96f49b9e10e8f860c9`.
- Minimum supported minor: Python 3.11. The exact tested floor is CPython
  3.11.15, signed-tag commit
  `2340a037f7450e70fccfe411e6531afb4d57a312`, in source-only security
  maintenance until approximately October 2027. Its directly tested
  python-build-standalone 20260718 asset has SHA-256
  `23ccae6f1ff73e8aa8378436f869da003b8eb7d6c95f2bc706f494115ba1447d`.
- Package metadata candidate: `Requires-Python: >=3.11`. Production CI should
  test every supported minor, 3.11 through 3.14; only the endpoints were run
  here, so 3.12 and 3.13 remain planned validation.
- Exact packaging-test snapshot: pip 26.2, build 1.5.0, Hatchling 1.31.0,
  packaging 26.2, pytest 9.1.1, and all transitives in the universal
  `--require-hashes` lock, SHA-256
  `0fcf65ff2348ef6356caad22169b7b907f6899069749b70660ef76e7ba7730b3`.

Python 3.14.6 passed the earlier probe but was superseded on the evidence date;
it remains successful historical evidence and is not the recommendation.

## Direct results

Host: Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86_64, `C.UTF-8`.

| Candidate | Result | Package-native evidence |
|---|---|---|
| CPython 3.14.7 | success | isolated PEP 517 sdist/wheel build, separate wheel install, `pip check`, two pytest tests, and metadata acceptance |
| CPython 3.11.15 | success | same fresh, offline sequence and assertions as 3.14.7 |
| CPython 3.10.20 | expected failure | pip rejected the wheel because 3.10.20 is outside `Requires-Python >=3.11` |

Both owned successful reruns produced the same prototype wheel SHA-256
`ed8a6dd1bda481a30dfa4a1fc04672a0c9276a12dc1492ed0e5a43f1e4218071`
and sdist SHA-256
`ec80e423866a1915cd82206a8caa078f1c91cf10ab47949be35565db6c15bac1`.
The exact uv 0.11.32 executable has SHA-256
`da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb`.

Preparation downloads the immutable, digest-checked runtime, uv, and wheel
assets. Verification is offline after preparation: it uses a fresh extracted
runtime, HOME/XDG/cache directories, build and install environments, and
`PIP_NO_INDEX=1`, then removes them. Missing prepared assets return 77 and are
not classified as success.

## Exact reproduction

After preparing the assets named in `README.md`, run:

```bash
/usr/bin/bash docs/research/toolchain-prototypes/python/verify-probe.sh development
/usr/bin/bash docs/research/toolchain-prototypes/python/verify-probe.sh floor
```

The original negative and cache/network failures remain under
`../logs/python/run-20260803/`. They show that cold uv seeding, an ordinary pip
cache, and an incomplete PEP 517 cache are not offline evidence. The current
owned dispatcher results are retained under `../logs/python/run-20260805/`.

## License, maintenance, security, and limits

- CPython is PSF-2.0. python-build-standalone is MPL-2.0 and bundles CPython
  and other components under their own notices; its binary provenance is kept
  distinct from the official CPython source release.
- uv is MIT OR Apache-2.0 and is a probe orchestrator, not a runtime
  dependency. The locked Python tooling is under the licenses recorded in the
  matrix source and lock evidence.
- The 2026-08-05 OSV point-in-time query returned zero vulnerability records
  for the 12 exact PyPI package versions. That is not a security guarantee;
  mutable advisories must be re-queried before integration or update.
- macOS, Windows, Linux arm64, Python 3.12, and Python 3.13 were not directly
  executed. Test exact runner images, architectures, runtime assets, build,
  install, metadata, positive tests, and the support-floor rejection before
  claiming those combinations.

Primary records are in `../sources/python.yaml` and `../sources/sources.json`,
including `python-release-v3.14.7`, `python-build-standalone-20260805`,
`python-release-v3.11.15`, `python-supported-versions`, and
`python-packaging-flow`.
