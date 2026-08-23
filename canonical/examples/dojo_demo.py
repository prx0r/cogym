from cogym.agents.model import HarnessTraderModel
from cogym.dojo.curriculum import CurriculumSplit
from cogym.dojo.master import PersistentMaster
from cogym.experiments.factory import synthetic_trading_world

model = HarnessTraderModel()
master = PersistentMaster("master-a", model)
curriculum = CurriculumSplit(
    training_worlds=(synthetic_trading_world(1, 10), synthetic_trading_world(2, 11)),
    validation_worlds=(synthetic_trading_world(3, 12), synthetic_trading_world(4, 13)),
    hidden_test_worlds=(synthetic_trading_world(5, 14), synthetic_trading_world(6, 15)),
)
for i in range(3):
    result = master.teach_one(f"student-{i}", model, curriculum, seed=1000+i*100000, indices=[35,65,95,125,155])
    print(result.student_id, result.log_score_gain, result.utility_gain, result.transmission_id)
