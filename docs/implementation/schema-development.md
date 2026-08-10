# Schema Development Guide

For each schema change:

1. update controlled semantic prose;
2. update CDDL and optional JSON projection;
3. add valid/minimal/maximal examples;
4. add malformed, unknown-extension, duplicate-key, numeric-boundary, and resource fixtures;
5. produce reviewed canonical bytes and digests;
6. compare at least two implementations;
7. assess migrations and theorem/artifact effects;
8. regenerate bindings through the documented generator.

Never edit generated bindings by hand.

## Foundation structural v0

Status: Experimental. This is one data-free fixture, not the general IR.

The exact source, semantics, corpus, and reproduction commands are in
`schemas/v0/README.md`. Generation order is:

```bash
python3 scripts/schema/compile_schema_v0.py
python3 scripts/schema/run_schema_v0.py --cddl-bin /exact/path/to/cddl-0.10.6
python3 scripts/schema/build_evidence_manifest.py
```

Verification does not rewrite tracked files:

```bash
python3 scripts/schema/compile_schema_v0.py --check
cddl --ci compile-cddl --cddl schemas/v0/compiled/foundation-structural.cddl
python3 scripts/schema/run_schema_v0.py --verify --cddl-bin /exact/path/to/cddl-0.10.6
python3 scripts/schema/check_schema_v0.py
python3 -m unittest discover -s scripts/schema/tests -p 'test_*.py' -v
```

The CDDL validator is exact `cddl` 0.10.6, installed with Rust 1.97.1 and
`--locked`. It is an untrusted shape producer. The 154-package packaged lock,
MIT root license, normalized dependency-license inventory, limited direct OSV
observation, and hash-bound RustSec scan are retained under
`source-audits/schema/`. The first offline installation failure is retained;
unavailable dependencies are not described as a successful test.

Clean reproduction starts with absent paths created by `mktemp -d`: one
`CARGO_HOME` for the CDDL graph, one frozen-prototype `CARGO_HOME`, and separate
target/install roots. Rust 1.97.1 alone acquires each exact locked graph;
subsequent installation, prototype build, inventory, and conformance commands
set `CARGO_NET_OFFLINE=true`. The workflow asserts every path is absent before
creating it and binds rustc commit
`8bab26f4f68e0e26f0bb7960be334d5b520ea452` and Cargo commit
`c980f4866141969fab6254a680546a277789d6f0`.

The schema harness bounds JSON oracle and CDDL validation calls to 30 seconds,
the CDDL version check to 10 seconds, and the offline Rust prototype build to
180 seconds. On directly tested Linux it additionally limits child address
space to 2 GiB, CPU time to 240 seconds, file output to 16 MiB, and retained
stdout/stderr diagnostics to 65,536 bytes. A timeout is `operational.timeout`;
diagnostic overflow is `resource.diagnostic_bytes`. These are harness limits,
not general platform support claims.

The Python semantic validator uses only the standard library and consumes
typed map-entry sequences so duplicates remain observable. The frozen SQ-0005
Python and Rust implementations are executed read-only and compared with a
third direct standards recipe. No program may replace an expected golden merely
because its own output changed.

Results remain separate for profile decoding, deterministic bytes, CDDL shape,
schema semantics, and fixture digest. The schema-specific fixed text keys sort
the same under core and length-first ordering, so the retained SQ-0005 generic
integer-key case—not this fixture—discriminates those algorithms.

Any field-name, requiredness, literal, type, grammar, equality, cardinality, or
meaning change requires a new schema identity/version. Unknown fields fail
closed. A migration creates newly validated bytes and a new fixture digest; it
does not establish semantic equivalence. RFC-0007 retains responsibility for
general migration policy. The v0 identity and integer version form the exact
pair `("statqed.foundation-structural.v0", 0)`; neither field is negotiated or
accepted independently.

Update all semantic prose, CDDL, fixtures, both implementation observations,
goldens, digest frames, source/security evidence, corruption tests, workflow,
and independent reviews together. Rollback restores one complete reviewed
subject, never a mixture. The TCB is limited to the interpretation of the
Accepted profile and reviewed schema semantics; Python, Rust, CDDL tooling,
Cargo, SHA implementations, the operating system, CI, and agents remain
untrusted evidence producers.
