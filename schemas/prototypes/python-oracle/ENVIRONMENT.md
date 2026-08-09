# Environment and dependency record

Status: **Experimental; direct execution evidence is Linux x86-64 only**.

| Component | Exact tested identity |
|---|---|
| Python | conda-forge CPython 3.12.13 build `hd63d673_0_cpython`, cache tag `cpython-312` |
| Directly invoked interpreter | `/home/lukas/miniconda3/envs/stats/bin/python` |
| Compiler recorded by Python | GCC 14.3.0 |
| Operating system | Ubuntu 24.04.4 LTS |
| Kernel | Linux 7.0.0-28-generic, x86-64 |
| C library | glibc 2.39 |
| `_hashlib` backend | conda-forge OpenSSL 3.6.3 build `h35e630c_0`; FIPS mode 0 |
| Runtime libraries | conda-forge `libgcc-ng` 15.2.0 build `h69a702a_19`; `libstdcxx-ng` 15.2.0 build `hdf11a46_19` |
| Unicode database shipped by CPython | 15.0.0; not used for normalization |
| Byte order | little-endian host; all CBOR and frame integers use explicit big-endian operations |

The exact interpreter selection is recorded in `.python-version`. The oracle
has zero third-party Python dependencies; `requirements.txt` is intentionally
empty. Imports are limited to the standard library: `argparse`, `dataclasses`,
`fractions`, `hashlib`, `hmac`, `json`, `math`, `re`, `struct`, `sys`, and
`typing`. Unit tests additionally use standard-library `os`, `pathlib`,
`subprocess`, and `unittest`.

The direct evidence in this directory is limited to the listed CPython 3.12.13
conda-forge interpreter on Linux x86-64. CPython 3.14.7 is a planned SQ-0005
CI coverage point, not a reproduced oracle result at this subject. It becomes
direct evidence only when the serialization-prototype workflow actually runs
this oracle and records the runner metadata. No conda package was added or
changed for this oracle.

CPython is licensed under the Python Software Foundation License Version 2 and
additional historical/component terms in its upstream distribution. The
retained `PSF-LICENSE-2.0.txt` is only the PSF License Version 2 portion and is
not represented as the complete runtime distribution license. The exact
installed CPython 3.12.13 `lib/python3.12/LICENSE.txt` has SHA-256
`3b2f81fe21d181c499c59a256c8e1968455d6689d269aa85373bfb6af41da3bf` and
contains the full history, PSF terms through 2023, historical licenses, and
component notices. The interpreter is an execution dependency, not
redistributed by this prototype; its complete upstream license must be
re-audited if redistribution is proposed. None of these runtime terms
relicense the MIT repository source.

No network access, package installer, locale data, timezone, randomness, clock,
hostname, environment-specific path, or mutable registry is used to determine
accepted bytes or result codes. Operational memory and timeout enforcement is
the responsibility of the outer conformance harness and must be recorded per
executed platform.
