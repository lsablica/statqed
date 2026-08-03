module StatQEDProbe

using SHA

export probe_digest, structural_fixture

"""
    structural_fixture()

Return a data-free toy value for a package-native compatibility probe.

This prototype is not a normative StatQED IR implementation and does not
define canonical bytes, logical-data identity, or a statistical guarantee.
"""
structural_fixture() = (
    schema = "statqed.foundation_structural.probe",
    probability_context = :not_applicable,
    toy_proposition = true,
)

probe_digest() = bytes2hex(sha256(codeunits(structural_fixture().schema)))

end
