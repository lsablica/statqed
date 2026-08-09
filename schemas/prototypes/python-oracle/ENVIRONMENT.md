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
conda-forge interpreter on Linux x86-64. CI separately exercises the reviewed
CPython 3.14.7 interpreter; that run is not inferred from this local result.
No conda package was added or changed for this oracle.

CPython is licensed under the Python Software Foundation License Version 2 and
additional historical/component terms in its upstream distribution. The PSF
License Version 2 text used for this inventory is retained in
`PSF-LICENSE-2.0.txt`. It is a runtime-license record and does not relicense the
MIT repository source.

No network access, package installer, locale data, timezone, randomness, clock,
hostname, environment-specific path, or mutable registry is used to determine
accepted bytes or result codes. Operational memory and timeout enforcement is
the responsibility of the outer conformance harness and must be recorded per
executed platform.
