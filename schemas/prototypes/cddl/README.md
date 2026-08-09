# Experimental CDDL structural view

Status: **Experimental**. This standalone file uses only published RFC 8610
syntax as updated by RFC 9682. It deliberately avoids module/import draft
syntax, tags, floats, `any`, open application extensions, and optional control
operators.

`profile-v1.cddl` is applied only after the strict CBOR profile decoder has
validated raw entries, duplicates, preferred heads, map order, Unicode, and
resource limits. A match therefore checks only the small recursive structural
subset. It does not establish deterministic bytes, semantic normalization,
digest identity, provenance, statistical validity, or kernel verification.

The conformance runner validates this source and its positive and negative
typed fixtures with the independent restricted-subset checker. That checker
is intentionally not presented as a general CDDL implementation. CDDL
module/import experiments remain separately pinned Work in Progress evidence
and are not a dependency of this candidate.
