from cogym.agents.model import HarnessTraderModel
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.social import run_social_round

world = synthetic_trading_world(3, 123)
packet = world.snapshot(100)
agents = {f"agent-{i}": HarnessTraderModel() for i in range(4)}
for row in run_social_round(agents, packet, horizon_steps=5, visibility="full_artifact", seed=5):
    print(row.agent_id, row.private.stance, "->", row.revised.stance, "changed", row.changed)
