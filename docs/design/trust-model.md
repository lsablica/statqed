# Trust Model

Status: **Draft; artifact-level kernel claims blocked on RFC-0003**.

## Trust categories

**Logical kernel TCB:** the Lean kernel and the exact mechanisms whose defect could make it accept a non-derivable proposition.

**Semantic review base:** pinned definitions, theorem statements, source mappings, and interpretations. Kernel execution does not establish their correspondence to intended statistics.

**Artifact-binding TCB or checked obligation:** the decoder, canonicalization, bridge, and byte-to-term mapping relied upon to connect artifact bytes to checked propositions. A component remains untrusted only when its output is independently rebound and checked.

**Operational TCB:** compilers, runtimes, platforms, native checkers, generators, and bridges relied upon by the named mode.

**Cryptographic assumptions:** collision/second-preimage properties and exact algorithms/domain separation used for content commitments. A digest match is not a proof that arbitrary messages are equal.

**External premises:** collection, measurement, protocol adherence, provenance truth, and scientific-world assumptions remain external regardless of verification mode.

## Explicitly untrusted by default

- R, Python, Julia, Rust producers, C/C++, BLAS/LAPACK, optimization solvers;
- AI agents and generated prose, unless an unchecked output is relied upon by the named mode;
- report renderers;
- package registries, network services, and mutable caches;
- the machine that originally produced the certificate.

## Verification modes

**Kernel:** final exact proposition accepted by Lean under locked dependencies and an actual axiom report, after an RFC-0003 byte-to-term adequacy path. Until then, only the proposition—not a `.statqed` artifact—may be called kernel-checked.

**Compiled checker:** compiled verifier executes reviewed checkers; compiler/runtime/platform join the operational TCB.

**Structural:** schema, version, digest, and reference validation only; no mathematical guarantee.

## Threats

- source theorem misformalization;
- hidden or inconsistent assumptions;
- vacuous definitions;
- canonicalization differentials;
- data substitution;
- theorem-lock substitution;
- malformed or adversarial artifacts;
- certificate type confusion;
- resource exhaustion;
- report overclaiming;
- stale or compromised dependencies.

Every verification-result record names exactly one mode, exact versions, accepted propositions/claims, assumptions, unresolved nodes, each trust category, actual axiom report, cryptographic assumptions, and nonclaims. A document may contain several separately identified results but never unions their evidence or emits an overall stronger status. Formal checking establishes a conditional proposition; it does not validate external premises, physical data identity, provenance truth, source fidelity, or interpretation.
