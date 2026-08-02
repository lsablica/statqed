# Frontend Assurance Modes

## Native declarative mode

The user constructs typed StatQED objects directly. Highest source-language fidelity within supported semantics.

## Checked adapter mode

An adapter inspects a common model/result object and extracts a canonical normal form. The artifact records adapter ID, source package version, and conformance version. Unknown semantics fail explicitly.

## Opaque capture mode

Unsupported external code produces a committed derived table/result. StatQED verifies only downstream claims. The assurance graph displays the opaque edge.

Frontends must expose row selection, missingness policy, categorical coding, transformations, weights meaning, offsets, targets, covariance convention, degrees of freedom, optimizer/tolerance, hypothesis direction, and multiplicity rules as applicable.
