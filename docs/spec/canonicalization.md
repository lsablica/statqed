# Canonicalization Specification

Status: **Draft; blocked on RFC-0001 and RFC-0006**.

Canonicalization covers logical values, maps, arrays, identifiers, Unicode, numeric tags, intervals, missingness, categorical levels, table schema, and extension ordering.

Requirements:

- one byte representation for one accepted semantic object;
- explicit distinction among integer, rational, decimal, IEEE bit pattern, and interval;
- no NaN payload or signed-zero ambiguity without specified bit semantics;
- duplicate map keys rejected;
- Unicode normalization policy fixed;
- a separately governed logical-data model/digest independent of Arrow physical layout;
- test vectors produced independently by at least two implementations;
- versioned migration for any semantic change.

RFC-0001 will settle the initial encoding after prototyping. RFC-0006 governs logical-data lowering and digest semantics. CDDL shape validation alone is not canonical-byte, semantic, or inferential verification.
