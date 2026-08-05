# R toolchain compatibility prototype

Status: **Draft research evidence**.

This disposable source package tests R's native package path only. It is not
the planned `frontends/r` package, does not define StatQED semantics, and does
not imply CRAN acceptance.

## Candidates

- Development: exact R 4.6.1 release on Ubuntu x86_64, with `testthat` 3.3.2
  and its exact 24-package CRAN/Archive source closure bound by URL+SHA-256 in
  `development-cran-source-lock.tsv` and installed into a fresh library.
- Support-floor candidate: `Depends: R (>= 4.4.0)`, tested with exact R 4.4.3
  and `testthat` 3.2.3 in an isolated conda-forge prefix. The 4.4 series is a
  project-defined compatibility floor covering the current feature series and
  two preceding feature series at the 2026-08-03 decision point. This is a CI
  cost/compatibility policy, not an assertion that R Core supports old series.

R 4.4.3 is the exact runtime used to exercise the declared 4.4 floor; passing
one patch release cannot establish that every 4.4.x build or every platform
works. The floor must be reviewed on each R feature release and immediately
when a relevant security or dependency issue cannot be fixed on it.

## Probe contract

For each available runtime, `run-probes.sh`:

1. captures exact runtime, platform, package, repository, license data, the
   development CRAN source lock, and a complete conda explicit lock whose
   artifact URLs carry SHA-256 fragments;
2. runs `R CMD build` on the source tree;
3. runs `R CMD check --no-manual` on that built tarball;
4. installs the built tarball into a fresh library;
5. invokes `testthat::test_local()` with the exact installed testthat version;
6. runs a smoke call from the installed package; and
7. records `sessionInfo()` and tarball/input digests.

The deliberate rejection copies the package only under `/tmp`, changes its
declaration to `Depends: R (>= 4.7.0)`, builds it with R 4.6.1, and confirms
that `R CMD check` rejects the built tarball. The mutated package is never
stored in the repository.

The current direct evidence is Ubuntu 24.04.4 LTS on x86_64 only. Exact R
4.6.1 jobs on macOS and Windows are mandatory before those platforms can be
claimed supported; an R 4.4.3 Linux job exercises the floor. Runner labels and
binary availability must be rechecked when CI is implemented.

## Reproduction

The floor setup used for this run was:

```sh
env XDG_CACHE_HOME=/tmp/statqed-sq0002-r/cache \
  CONDA_PKGS_DIRS=/tmp/statqed-sq0002-r/pkgs \
  CONDA_ENVS_PATH=/tmp/statqed-sq0002-r/envs \
  conda create --yes --solver libmamba --override-channels -c conda-forge \
  --prefix /tmp/statqed-sq0002-r/envs/r-4.4.3 \
  'r-base=4.4.3=h14df4e6_4' \
  'r-testthat=3.2.3=r44h3697838_2'
```

After the exact source/conda artifacts have been prepared, the owned reruns are:

```sh
/usr/bin/bash docs/research/toolchain-prototypes/r/verify-probe.sh development
/usr/bin/bash docs/research/toolchain-prototypes/r/verify-probe.sh floor
```

Each verifier uses a fresh task directory and removes its prefix, libraries,
build trees, `.Rcheck` directories, and transient logs on exit. The external
prepared source and conda artifact caches are digest-checked and retained for
network-independent reruns; missing preparation returns 77. The initial conda
solve and artifact acquisition required the network.
The retained full explicit lock is content-addressed and includes per-artifact
SHA-256 fragments. A new conda prefix was recreated offline from that exact
lock and passed the floor probe. The development dependency closure was also
fetched and source-installed fresh from its SHA-256 lock; no host library was
copied in the final run. conda-forge could not solve R 4.6.1 with its available
testthat 3.3.2 builds, and that failed candidate is retained. `R CMD check`
repository-index warnings are preserved rather than normalized away.

## License, maintenance, and security boundary

R is GPL-2 | GPL-3 according to the official R material. The prototype and
testthat are MIT-licensed; the exact recursive test-only package inventories
record their own declared licenses. `testthat` is a suggested development/test
dependency, not a runtime dependency of the probe package.

R Core publishes release, maintenance, and SDLC material, but the reviewed
official sources do not promise a fixed support horizon for earlier R series.
Neither CRAN checks nor this prototype are a security audit. The floor carries
a stale-runtime risk, and no claim is made that a passing package check means
the runtime, conda build, or transitive packages are free of vulnerabilities.
