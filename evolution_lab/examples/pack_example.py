from cogym.schema import AgentGenome, BenchmarkResult
from cogym.packs import PackBuilder

g=AgentGenome(reasoning_policy="scenario_tree",representation="bayesian",memory_policy="failures_first",memory_depth=6)
r=BenchmarkResult("example",g.genome_id,100,0.001,-0.002,0.12,0.03,2.0)
pack=PackBuilder.build("game-theory-specialist","0.1",g,[
    "Separate private belief from public signal.",
    "Model peers as strategic information sources whose reliability is learned over repeated interaction.",
    "Before following consensus, estimate whether observations are conditionally independent."
],[r],provenance={"purpose":"simulation benchmark only"})
PackBuilder.save(pack,"game_theory_pack.json")
print(pack.pack_id)
