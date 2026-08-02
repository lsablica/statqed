# Canonicalization Specification

Status: **Research required before acceptance**.

Canonicalization covers logical values, maps, arrays, identifiers, Unicode, numeric tags, intervals, missingness, categorical levels, table schema, and extension ordering.

Requirements:

- one byte representation for one accepted semantic object;
- explicit distinction among integer, rational, decimal, IEEE bit pattern, and interval;
- no NaN payload or signed-zero ambiguity without specified bit semantics;
- duplicate map keys rejected;
- Unicode normalization policy fixed;
- canonical logical data digest independent of Arrow physical layout;
- test vectors produced independently by at least two implementations;
- versioned migration for any semantic change.

RFC-0001 will settle the initial encoding after prototyping.
