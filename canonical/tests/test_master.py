from cogym.agents.model import HarnessTraderModel
from cogym.dojo.curriculum import CurriculumSplit
from cogym.dojo.master import PersistentMaster
from cogym.dojo.population import score_master
from cogym.experiments.factory import synthetic_trading_world


def test_persistent_master_teaches_successive_students():
    m = HarnessTraderModel()
    master = PersistentMaster("m1", m)
    c = CurriculumSplit(
        training_worlds=(synthetic_trading_world(1, 1),),
        validation_worlds=(synthetic_trading_world(3, 2),),
        hidden_test_worlds=(synthetic_trading_world(5, 3),),
    )
    e1 = master.teach_one("s1", m, c, seed=10, indices=[35,65,95])
    e2 = master.teach_one("s2", m, c, seed=20, indices=[35,65,95])
    assert len(master.student_history) == 2
    assert e1.transmission_id and e2.transmission_id
    assert score_master(master).students == 2
    assert len(master.history) > 0
