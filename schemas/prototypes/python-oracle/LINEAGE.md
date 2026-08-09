# Implementation lineage

Status: **Experimental evidence record**.

Implementation source: `89af5a7dbb837ea7d1557d1a715b34a814afdf95`,
independent reference-oracle engineer. The final candidate inputs are bound
below. The implementation commit incorporates the reviewed distinction between
complete invalid digest identifiers and truncated length-prefixed components.

The implementation was written directly from these reviewed candidate inputs:

| Input | SHA-256 |
|---|---|
| `docs/research/serialization/semantic-value-model.md` | `a94588e54fdc3e2aa08e73f5f6e76bb71128940bb245305b2dec9dffa2ffcfb2` |
| `docs/research/serialization/profile-candidate.md` | `6cbf0f686a1f35b5c6fac8411ef5abc708c9c4410b5fdb2ee510c513df067d2f` |

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
