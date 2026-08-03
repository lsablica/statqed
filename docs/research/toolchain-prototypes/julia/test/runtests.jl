using StatQEDProbe
using Test

@testset "StatQED Julia toolchain probe" begin
    fixture = structural_fixture()

    @test fixture.schema == "statqed.foundation_structural.probe"
    @test fixture.probability_context === :not_applicable
    @test fixture.toy_proposition === true
    @test propertynames(fixture) == (
        :schema,
        :probability_context,
        :toy_proposition,
    )
    @test probe_digest() ==
          "973ef04cced92e5da5b5f017ed0307be150b181b3b950ceaa25512cf7ca456b3"
end
