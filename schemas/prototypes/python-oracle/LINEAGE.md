# Implementation lineage

Status: **Experimental evidence record**.

Implementation source: `14f1ffb0646b280fea805fbec6ba6bb8b3d1a282`,
independent reference-oracle engineer.  The final candidate inputs are bound
below; later profile-only result-taxonomy clarification did not add an
implementation dependency.

The implementation was written directly from these reviewed candidate inputs:

| Input | SHA-256 |
|---|---|
| `docs/research/serialization/semantic-value-model.md` | `a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2` |
| `docs/research/serialization/profile-candidate.md` | `c164816bb1d7c8bb1dd0683343d25b018964e2da417aa17a9bb366490d8b2679` |

The candidate documents cite RFC 8949 for CBOR well-formedness, validity,
preferred serialization, and core deterministic ordering, and FIPS 180-4 for
SHA-256. The implementation contains its own head parser, ordered raw map
entry model, semantic conversion, canonical encoder, UTF-8 checks, resource
counters, and unsigned-32-bit big-endian digest framing.

No Rust prototype source, Rust-produced byte stream, Rust test vector, CBOR
package, canonicalization package, or shared encoder was read, imported,
called, or used as expected truth. Positive bytes in unit tests were derived
from the candidate tables and the RFC head rules. The digest-frame test builds
the six length-prefixed components independently and checks their SHA-256
result against the oracle function.

The implementation shares only the language-neutral candidate specification
and ubiquitous algorithm definitions with another implementation. Agreement
must still be established by the separately owned differential harness. A
change to either content-addressed candidate input invalidates this lineage
record until the oracle is reviewed and retested.

No generated source is present. No external code was copied into the oracle.
Repository source remains under the root MIT license; the CPython runtime has
the separately recorded PSF License Version 2 terms.
