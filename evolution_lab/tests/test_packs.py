from cogym.schema import AgentGenome, BenchmarkResult
from cogym.packs import PackBuilder

def test_pack_integrity(tmp_path):
    g=AgentGenome(representation="bayesian")
    r=BenchmarkResult("b",g.genome_id,10,.1,0,.2,.1,1)
    p=PackBuilder.build("bayes","1",g,["Read these game theory notes."],[r])
    path=PackBuilder.save(p,tmp_path/"p.json")
    assert PackBuilder.verify_file(path)["valid"]
