# StatQED Theorem Registry

Status: Experimental test-only v0.

The registry contains exactly one definitionally trivial `True` record used to
exercise identity, environment closure, proof/build, axiom observation,
authorization, and directional-compatibility plumbing.  It is not a public or
statistical theorem and is not a non-vacuity witness.

`registry.json` is a generated index.  The canonical record, independently
selected authorization policy, lock layers, and retained evidence are in the
adjacent directories.  Regenerate them with:

```bash
python3 scripts/registry/build_registry.py
```

Verification is bounded, deterministic, and offline after toolchain setup.
Internal hash consistency never gives a candidate registry governance
authority; the verifier selects the permitted root policy separately.
