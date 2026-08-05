# Julia/Pkg compatibility prototype

Status: **Draft research evidence**. This is not `frontends/julia`, package
publication approval, or a semantic interface.

The development candidate is the official Julia 1.12.6 Linux x86-64 archive
(`sha256:bbabf3bef19421a9dbd24a767d807606ab85e444323b5a1c73ffe293fa3d079a`).
The support-floor candidate follows the maintained LTS line at exact Julia
1.10.11 (`sha256:fb49c6b174600cd2051e37ba3f7330f8acf06dd00bce609bab6611387fdb37bf`).
Both are MIT source distributions whose binary bundles may include components
under other compatible licenses; official release/support/license/security
records are retained in `../sources/sources.json`.

On Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic, x86_64, both exact archives
passed `--version`, `versioninfo`, `Pkg.resolve`, offline `Pkg.instantiate`,
strict precompile, `Pkg.test`, and project/manifest status in fresh isolated
depots. Each depot contains a fixed empty local registry sentinel so Pkg does
not bootstrap the mutable General registry for a package with stdlib-only
dependencies. The sentinel contains no packages and its source is generated
by `run_probes.py`. Each fresh generated manifest must match the exact retained
bytes in `locks/Manifest-1.12.6.toml` or `locks/Manifest-1.10.11.toml`; ordinary
verification cannot refresh those locks and fails closed on drift.

Three earlier fresh-depot attempts (`122700Z`, `123100Z`, and `123700Z`) failed
because Pkg tried to clone General despite offline variables. They remain in
`../logs/julia/` as failures. The corrected `124500Z` run succeeded without
General or external package downloads. A mutated project requiring Julia 1.13
was rejected by Julia 1.12.6 as expected.

The exact official archive locators are
`https://julialang-s3.julialang.org/bin/linux/x64/1.12/julia-1.12.6-linux-x86_64.tar.gz`
and
`https://julialang-s3.julialang.org/bin/linux/x64/1.10/julia-1.10.11-linux-x86_64.tar.gz`.
After downloading and checking the digests above, run:

```sh
/usr/bin/bash docs/research/toolchain-prototypes/julia/verify-probe.sh development
/usr/bin/bash docs/research/toolchain-prototypes/julia/verify-probe.sh floor
```

Preparation is networked and checksum-gated. The actual Pkg probe is offline,
single-threaded, uses `C.UTF-8`, disables startup/history and automatic
precompile, and writes all depots/workspaces under a fresh `/tmp` directory
that is removed on exit. Direct evidence is
Linux x86-64 only. macOS, Windows, ARM, registry publication, and packages with
non-stdlib dependencies require later validation; no support is inferred.
