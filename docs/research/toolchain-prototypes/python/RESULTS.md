# SQ-0002 Python compatibility findings

Status: **Experimental**.

Evidence cutoff: 2026-08-03. These findings recommend a later frontend
bootstrap policy; they do not create a production package, reserve a package
name, publish a distribution, or make Python part of a trusted verification
path.

## Recommendation

- Development/reference interpreter: CPython 3.14.6, the released current
  stable observed at the cutoff. The upstream tag is `v3.14.6` at
  `c63aec69bd59c55314c06c23f4c22c03de76fe45`.
- Minimum supported minor: Python 3.11. The exact floor probe used CPython
  3.11.15, upstream tag `v3.11.15` at
  `2340a037f7450e70fccfe411e6531afb4d57a312`. Python 3.11 remains in
  source-only security maintenance until approximately October 2027; each new
  security patch must replace 3.11.15 after the same probe.
- Prototype metadata: `Requires-Python: >=3.11`. This is a declared floor, not
  evidence for untested interpreters. Production CI should cover every
  supported minor (3.11, 3.12, 3.13, 3.14), with 3.11 and 3.14 as required
  endpoints. Only the endpoints were tested here.
- Exact packaging-test snapshot: pip 26.2, build 1.5.0, Hatchling 1.31.0,
  packaging 26.2, and pytest 9.1.1. The universal hash lock also records all
  transitives. These are development/test pins, not runtime dependencies.

The floor choice avoids beginning a new package on Python 3.10, whose upstream
security window ends around October 2026, while retaining a substantially
wider adoption window than a 3.13 or 3.14 floor. Raise the floor before Python
3.11 reaches end of life. Advance development and floor patch releases only
after refreshing primary sources, regenerating the hash lock, and rerunning
the complete build/install/test/metadata probes.

## Direct results

Host: Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86_64, `C.UTF-8`.

| Candidate | Result | Package-native evidence |
|---|---|---|
| CPython 3.14.6 | success | sdist and wheel built in PEP 517 isolation; wheel installed into a distinct venv; `pip check`; 2 pytest tests; metadata accepted runtime |
| CPython 3.11.15 | success | same sequence and assertions as 3.14.6 |
| CPython 3.10.20 | expected failure | pip 26.2 rejected the wheel: `3.10.20 not in '>=3.11'` |

The final fresh rerun from the exact 20260718 release assets produced
byte-identical prototype artifacts on both successful interpreters:

- wheel SHA-256:
  `99137bdaa71c96a9fce94ee7a141c8c9c7b4ddc3c4b3df6257d6e09a47b4a643`;
- sdist SHA-256:
  `90a82f656fc6782326537c9c54b0314cc61a7d8240be50edb4868a49aca0cb0c`;
- hash-lock SHA-256:
  `0fcf65ff2348ef6356caad22169b7b907f6899069749b70660ef76e7ba7730b3`.

Preparation-chain identities retained by the manager are:

- uv 0.11.32 Linux x86-64 executable SHA-256:
  `da15297d6879b2cfbe5ea3cb03725c1613d51ba72892cc996468d871f0a532fb`;
- installed 3.14.6 runtime-tree manifest SHA-256:
  `0a7e8d480cec7c5bb4fd8614b911dde57c484068d04fde006ea56b09ef1a32f3`;
- installed 3.11.15 runtime-tree manifest SHA-256:
  `2e6821e603c0347a1e855204ce35fd64169ca05f1a8504e6e7c59c08366da00a`;
- installed 3.10.20 runtime-tree manifest SHA-256:
  `f1b5dfab0b58f4b2a90e8de2352404db05c63c3a2e4f3d57578c2464ab2d5af0`.

The final run additionally bound the exact `python-build-standalone` 20260718
release assets: CPython 3.14.6
`sha256:86bf107f65fc30b56f2b263b26797fcbb1661f5315910cdbf27f733eb8738b74`
and CPython 3.11.15
`sha256:23ccae6f1ff73e8aa8378436f869da003b8eb7d6c95f2bc706f494115ba1447d`.
The inspected uv 0.11.32 release archive is
`sha256:aab924fd522efd06f1c5f3b93a243864fc453132c94b2dc49f1371b528a4b967`.
All values matched GitHub's release-asset digest fields before extraction.
These remain third-party distributions rather than official CPython binaries.

The final fresh-directory rerun used an isolated `/tmp` wheelhouse and
`PIP_NO_INDEX=1`; the execution environment had no working DNS. Preparation
is networked, while the package build/install/test phase is offline after the
wheelhouse exists.

## Exact reproduction

Install the inspected uv 0.11.32 binary into a task-local directory, then:

```bash
SQ0002_UV=/tmp/statqed-sq0002-python-tools/uv \
  python3 run_probes.py --prepare --probe all
```

`--prepare` installs managed CPython 3.14.6, 3.11.15, and 3.10.20 under
`/tmp/statqed-sq0002-python-runtimes`, generates the universal hash lock, and
downloads the locked Linux wheels to `/tmp/statqed-sq0002-python-wheelhouse`.
After preparation, the successful endpoint reruns are:

```bash
python3 run_probes.py --probe development
python3 run_probes.py --probe floor
```

The negative probe intentionally exits 1:

```bash
python3 run_probes.py --probe rejected
```

## Failed attempts retained

- A cold, network-denied uv seed on 3.11.15 failed because seed packages were
  absent from the uv cache.
- Pinning pip on 3.10.20 with an ordinary pip cache still tried to retrieve
  index metadata and failed without DNS.
- A PEP 517 build with only the ordinary pip cache still queried the index for
  Hatchling and failed without DNS.
- A later uv seed for 3.14.6 again demonstrated that uv seed availability is
  interpreter/cache specific.

The final harness addresses these failures by using the selected interpreter's
standard `venv`, installing all pinned tools from a hash-checked wheelhouse,
and passing that wheelhouse into the PEP 517 sandbox. The failure logs remain
part of the evidence rather than being normalized to success.

## License, maintenance, and security limits

- CPython: PSF License Version 2. The uv-managed Linux runtimes are Astral
  `python-build-standalone` distributions, not official CPython binaries and
  not proven byte-identical to the upstream tag. Their direct runtime behavior
  is evidence for this host only; the upstream tag commit and managed binary
  identity are separate facts.
- uv: MIT OR Apache-2.0; probe orchestrator only, not a package dependency.
- build, Hatchling, pip, pytest, iniconfig, pluggy, and pyproject-hooks: MIT.
- packaging: Apache-2.0 OR BSD-2-Clause; Pygments: BSD-2-Clause; pathspec:
  MPL-2.0; trove-classifiers: Apache-2.0. The universal lock includes
  Windows-only colorama (BSD-3-Clause), which was not installed on this Linux
  probe.
- The prototype itself declares MIT consistently with the repository policy
  and has no runtime dependencies.

No authoritative current-vulnerability absence claim is made here. Package
index versions and local license metadata were reviewed, but mutable advisory
databases and release/security policy require the distinct SQ-0002
release/security review. Exact pins reduce drift but do not make registries,
downloads, Python, build backends, or test tools trusted.

macOS, Windows, non-x86_64 architectures, Python 3.12, and Python 3.13 were not
executed by this role and remain unknown direct-runtime combinations. Validate
all supported minors on the intended GitHub-hosted operating systems before
SQ-0014 claims frontend support.

## Source anchors

Primary source records used by this probe are
`../sources/python.yaml` and the entries `python-release-v3.14.6`,
`python-supported-versions`, `python-pyproject-guide`,
`python-packaging-flow`, and `python-security-policy` in
`../sources/sources.json`. Direct official release locators additionally used
for the floor/rejection patch identities were the CPython `v3.11.15` and
`v3.10.20` GitHub releases and PEP 664/PEP 619.
