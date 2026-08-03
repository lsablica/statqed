# Assurance Profile

Status: **Draft**.

StatQED rejects a single undifferentiated “verified” badge. An artifact reports independent dimensions.

| Dimension | Example statuses |
|---|---|
| Data binding | checked logical digest; commitment only; unbound |
| Transformations | formally evaluated; independently recomputed; adapter-attested; opaque |
| Numerical result | exact; interval-certified; residual-checked under named error premises; optimization-certified; replay-only; unchecked |
| Statistical guarantee | exact finite-sample; nonasymptotic bound; asymptotic; none |
| Identification | proved under named assumptions; partially identified; unattached; unresolved |
| External assumptions | protocol-attested declaration; declared; diagnostic-only judgment; unresolved |
| Frontend fidelity | native IR; checked adapter; conformance-tested adapter; opaque capture |
| Provenance | complete; partial; absent |
| Verification mode | kernel; compiled checker; structural |

Heuristics, replay traces, and diagnostics may be reported in their own non-guarantee categories. Statuses form a partially ordered assurance lattice only where formally defined. Reports must not average dimensions into a score that obscures a weak link.
