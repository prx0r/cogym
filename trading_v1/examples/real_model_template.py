"""Template only: supply your own provider credentials and never commit keys."""
import os

from cogym.agents.model import OpenAICompatible
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.transfer import run_abcdef
from cogym.state.pack import load_pack

model = OpenAICompatible(
    model_id=os.environ["COGYM_MODEL"],
    base_url=os.environ["COGYM_BASE_URL"],
    api_key=os.environ["COGYM_API_KEY"],
)
world = synthetic_trading_world(4, 2026)
pathway = load_pack("packs/trading_falsification_v1.json").pathway
report = run_abcdef(model, world, pathway, repeats=5)
print(report)
