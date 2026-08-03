# Provenance Specification

Status: **Draft**.

StatQED extends rather than replaces general provenance standards.

The artifact maps analyses to W3C PROV entities, activities, and agents and may package research objects using RO-Crate conventions.

StatQED-specific provenance includes:

- frontend/adapter and conformance version;
- source package/toolchain versions;
- data commitments and transformation IDs;
- certificate producer and parameters;
- agent/model/tool records for generated contributions;
- theorem/method locks;
- verification mode and platform;
- report-generation activity;
- citations and source audits.

Provenance records an assertion about entities, activities, agents, and lineage. Mechanical validation can establish that a record exists and is structurally bound; it does not prove that described external events occurred or that the record is truthful.

RFC-0008/SQ-0010 must define allowlisted required/optional capture and exclude tokens, secrets, raw environment dumps, unnecessary user paths, and private identifiers. Commitments may enable linkability or guessing of low-entropy values. Changing or redacting committed or normative provenance always creates a new normative artifact identity and, where applicable, a new verification-result identity. Redacting only an inert non-normative report leaves the normative artifact identity unchanged, but changes the physical bundle bytes/file commitment and records the report/disclosure transformation. An unresolved leaf is permitted only for an external/uncommitted reference or inside a newly identified normative object/result; it never preserves the identity or dependency closure of changed committed bytes.
