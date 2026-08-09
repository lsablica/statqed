# Independent Python encoding oracle

Status: **Experimental**.

This directory contains a direct-from-specification reference oracle for the
candidate `statqed.cbor-core.v1` profile. It uses only the CPython standard
library. It is independent interoperability evidence, not normative authority,
a production decoder, or statistical or kernel verification.

The implementation accepts only direct-range integers, byte strings, exact
Unicode scalar strings, arrays, ordered-entry maps, booleans, and null. It
implements RFC 8949 core ordering directly, retains raw map entry sequences
before duplicate validation, rejects non-preferred input rather than repairing
it, rejects every tag and float, and implements the candidate six-component
SHA-256 length-prefix digest frame.

The framing commands validate canonical profile bytes and bind the caller's
exact object-class/schema identifier. They do not resolve that identifier or
validate schema conformance; a schema-owning caller must perform that separate
check before composing a stronger result.

## Run

From the repository root, with the pinned interpreter:

```bash
PYTHONPATH=schemas/prototypes/python-oracle \
  /home/lukas/miniconda3/envs/stats/bin/python -m unittest discover \
  -s schemas/prototypes/python-oracle/tests -p 'test_*.py' -v

PYTHONPATH=schemas/prototypes/python-oracle \
  /home/lukas/miniconda3/envs/stats/bin/python -m statqed_oracle.cli encode <<'JSON'
{"type":"map","entries":[{"key":{"type":"integer","value":"-1"},"value":{"type":"null"}},{"key":{"type":"integer","value":"100"},"value":{"type":"null"}}]}
JSON

PYTHONPATH=schemas/prototypes/python-oracle \
  /home/lukas/miniconda3/envs/stats/bin/python -m statqed_oracle.cli decode <<'JSON'
{"cbor_hex":"a21864f620f6"}
JSON
```

The CLI has four commands: `encode`, `decode`, `frame`, and `verify-digest`.
It reads one strict JSON value from standard input and writes canonical JSON to
standard output. JSON duplicate members and non-finite JSON numbers fail
closed. Rejections exit 1; acceptance exits 0; argument-parser misuse exits 2.
Results contain stable `result_class` and `code` fields and contain no clock,
hostname, process identifier, or filesystem path.

## Typed JSON

Integers are decimal strings so the projection cannot pass through an IEEE
number. Maps are entry arrays so duplicates remain representable:

```json
{"type":"integer","value":"18446744073709551615"}
{"type":"bytes","hex":"00ff"}
{"type":"text","value":"é"}
{"type":"array","items":[{"type":"boolean","value":false},{"type":"null"}]}
{"type":"map","entries":[{"key":{"type":"text","value":"x"},"value":{"type":"null"}}]}
```

The diagnostic interface also recognizes explicitly unsupported `bignum`,
`rational`, `decimal`, `ieee_bits`, `interval`, `extension`, and
`extension_sequence` constructors so that producer failures receive the
candidate `semantic.*` codes instead of a fallback encoding.

Diagnostic rendering is limited to 4,096 UTF-8 bytes. If a full projection is
larger, the CLI emits a bounded `resource.diagnostic_bytes` summary while
retaining the separate underlying validation class and code. Library callers
receive full `Result` objects and exact encoded/frame bytes.

## Boundaries

The logical limits are constants in `statqed_oracle/oracle.py`: 1,048,576
input bytes, 1,048,576 output bytes, 65,536 bytes per string, 1,024 array
items, 1,024 map entries, 4,096 total CBOR items, 32 open array/map/tag levels,
4,096 diagnostic bytes, zero accepted tags, and zero accepted extensions. A
digest frame has a conservative 1,049,255-byte allocation cap. With the fixed
7-byte algorithm, 20-byte profile, and 20-byte framing identifiers, two
128-byte caller-owned identifiers, and a maximum payload, the largest frame
that can actually validate is 1,048,918 bytes. The operational 5-second and
128-MiB harness ceilings belong to the external conformance runner; they are
not replaced by a wall-clock check inside this deterministic oracle.

Empty CBOR input is `wellformed.truncated`; bytes after the first complete
item are `expected.trailing_bytes`. There is deliberately no overlapping
`expected.single_item` result. Likewise, finite profile input cannot produce a
public `wellformed.length_overflow` result; a defensive host-arithmetic failure
is classified as operational evidence rather than accepted profile behavior.

See [LINEAGE.md](LINEAGE.md) and [ENVIRONMENT.md](ENVIRONMENT.md) for the
independence, toolchain, dependency, and license record.
