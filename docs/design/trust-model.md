# Trust Model

Status: **Draft; RFC required before Candidate release**.

## Intended trusted base in kernel mode

- Lean kernel;
- pinned formal definitions and theorem statements;
- trusted artifact decoder/bridge needed to construct checked terms;
- certificate checkers and their soundness proofs;
- cryptographic and logical-data binding definitions named by the artifact.

## Explicitly untrusted by default

- R, Python, Julia, Rust producers, C/C++, BLAS/LAPACK, optimization solvers;
- AI agents and generated prose;
- report renderers;
- package registries, network services, and mutable caches;
- the machine that originally produced the certificate.

## Verification modes

**Kernel:** final proof term/checked structure accepted by Lean kernel.

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

Every verification report names mode, exact versions, accepted claims, assumptions, unresolved nodes, TCB, and nonclaims.
