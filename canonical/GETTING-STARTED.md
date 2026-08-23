# Cogym Getting Started Guide
For a new agent or human starting from scratch.

## What is Cogym?
A deterministic experimental laboratory for testing whether reasoning strategies
(like "seek falsifying evidence" or "weight hard tasks more") actually improve
decisions. Trading is the lab organism — objective, sequential, adversarial.

## Quick start (5 minutes)

```bash
cd /root/cogym/canonical
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest pyyaml

# Run tests
pytest tests/ -q   # should show 16 passed

# Run demo
cogym smoke        # runs a single experiment
cogym dojo-demo    # runs master→student demo
```

## Running a real LLM transfer experiment

```python
import os
from cogym.agents.model import OpenAICompatible, Message
from cogym.experiments.transfer import run_abcdef
from cogym.experiments.factory import synthetic_trading_world
from cogym.state.pathway import ContextPathway, PathwayStep

# 1. Create model (ox-alpha-free = unlimited free inference)
model = OpenAICompatible(
    model_id="ox-alpha-free",
    base_url="https://opencode.ai/zen/go/v1",
    api_key=os.environ["OPENCODE_GO_API_KEY"],
)

# 2. Create world (level 4 = regime flip territory)
world = synthetic_trading_world(level=4, seed=42)

# 3. Define reasoning pathway (the treatment)
pathway = ContextPathway(
    name="falsification_first",
    steps=(
        PathwayStep(id="s1", prompt="What does the market believe?", tags=("hypothesis",)),
        PathwayStep(id="s2", prompt="What would FALSIFY that belief?", tags=("falsification",)),
        PathwayStep(id="s3", prompt="Check evidence, revise if needed.", tags=("revision",)),
    ),
    system="You are a careful trader who values falsification.",
)

# 4. Run the A-F transfer experiment
report = run_abcdef(
    target_model=model,
    world=world,
    pathway=pathway,
    repeats=1,
    base_seed=42,
)

# 5. Inspect results
for k, v in vars(report).items():
    print(k, v)
```

## Key concepts

| Object | What it is |
|--------|-----------|
| **TradingWorld** | Deterministic price series + point-in-time data |
| **ContextPathway** | Multi-step reasoning treatment injected before decision |
| **AgentSpec** | Typed organism definition (model + cognition + memory) |
| **BehaviorSignature** | Measurable behavioral fingerprint |
| **SkillRegistry** | Skills enter population only after paired probe evidence |
| **HardWorlds** | Worlds where naive policy ≠ oracle policy |
| **EventLedger** | Append-only hash-chained audit trail |

## The A-F conditions
| Code | Meaning | What subject receives |
|------|---------|----------------------|
| A | Live pathway | Personally walks through full reasoning |
| B | Exact checkpoint | Serialized state from A's traversal |
| C | Structured Pack | Distilled principles/rules |
| D | Generated teaching | Master explains conversationally |
| E | Static primer | Fixed instruction text |
| F | Summary | Brief summary |

Plus G = naive control (no treatment).

## API endpoints (machine-readable)
```
/api/v1/top.json         # top opportunities
/api/v1/opportunities.json # all data
/api/v1/changes.json     # what changed
/api/v1/portfolio.json   # best path chain
/rss.xml                 # feed
/sitemap.xml             # all pages
```

## Model configuration
Ox-alpha-free via OpenCode Go endpoint. Locked by daemon.
API key: OPENCODE_GO_API_KEY in ~/.bashrc.
Endpoint: https://opencode.ai/zen/go/v1
Cost: $0 (free tier)
