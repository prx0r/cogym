# Cogym Handover — 2026-08-23, 17:00 UTC

## What cogym IS now
A deterministic reasoning laboratory using simulated trading as the experimental organism.
Tests WHICH REASONING PATTERNS causally improve decisions and survive transfer.
NOT a trading bot. NOT a generic agent framework.

## Canonical repo: /root/cogym/canonical/
trading_v1 core (16/16 tests) + evolution_lab improvements merged additively.

## Three running experiments (all ox-alpha-free)
| ID | What it tests | Status |
|----|--------------|--------|
| E01 baseline | Natural performance on 3 world types | ✅ COMPLETE |
| E02 persistence | reset vs persistent vs outcomes | 🔄 Running |
| E03 dose | pathway depth 0-5 | 🔄 Running |
| E04 social | peer reveal conditions | 🔄 Running |

## Key results so far
### E01 baseline (muse-spark fallback — ox-alpha was 503)
smooth_trend: log=-1.012, utility=+0.002
shock_jumps: log=-1.045, utility=-0.001  
regime_flip: log=-1.206, utility=-0.006 ← HARDEST

Harder worlds = worse performance. Confirms difficulty scaling works.

### STX-002 (ox-alpha-free)
checkpoint/pack: 100% accuracy on hard worlds
control: 87%
live pathway: 73% (overthinking hurts on single-shot probes)
base_rate_shift is hardest family

**IMPORTANT**: This was a STATIC CONTEXT pilot, not real state transfer.
The "live" condition read a static file, not a live pathway generation.
Reclassified as STATIC-REPRESENTATION-PILOT. Do not interpret as transfer result.

## Infrastructure working
- Deterministic market worlds (6 levels, seeded, forkable, point-in-time safe)
- ExperimentRunner with reset/persistent history modes
- PaperTradingEngine with full portfolio tracking + Sharpe/drawdown/win-rate
- InteractiveRegimeShiftWorld (30 steps, hidden change point, evidence costs)
- SkillRegistry w/ counterfactual gating + lifecycle + lineage
- EventLedger (hash-chained append-only)
- Hermes proposal adapter + deterministic validation
- PatternStore for HydraDB-ready projection

## Known bugs fixed this session
1. delta_rec UnboundLocalError when champion=None → initialized upfront
2. {failures} interpolation bug in hermes_proposals prompt
3. PatternStore duplication (dev suite evaluated twice per gen)
4. PatternStore wrong "improved" definition → now requires improvement vs control
5. API key hardcoded in experiment scripts → moved to env var only
6. model.py User-Agent header added (Cloudflare was blocking urllib)
7. model timeout increased 180→300s with retry on 429/503
8. skill_registry evaluate() signature updated to match test expectations

## Known issues remaining
1. Docker daemon failed due to broken volume mount at /mnt/HC_Volume_106427611
   → Fixed by changing data-root to /var/lib/docker in /etc/docker/daemon.json
2. HydraDB running but Cypher write support limited (early-stage Rust project)
   → Use SQLite PatternStore now; project to HydraDB when mature
3. lablab.ai CF-walled against curl → manual entries or hermes browser-use needed
4. STX-002 needs n=5 per treatment for significance (McNemar p≈0.5 at n=15 paired)

## What to build next (IN ORDER)
1. Wait for E02-E04 to complete (~30 min)
2. Cross-experiment analysis: compare persistence vs dose vs social effects
3. Write STX-003 proposal informed by findings
4. Run STX-003 with n=5 on worlds where control scores 30-50% (room for improvement)
5. Add falsification world family to hardworlds
6. Wire HydraDB projection once patterns are validated

## Do NOT build yet
Social contagion topologies · Pack composition chemistry · Reputation systems ·
Evolution algorithm bake-off · Kanban orchestration · MCP server · Dashboards ·
Cross-domain transfer · Weight training · Agent economies

## Model configuration
ox-alpha-free via https://opencode.ai/zen/go/v1
API key: OPENCODE_GO_API_KEY in ~/.bashrc
LOCKED by daemon: /root/.hermes/lock-ox-alpha.sh (checks every 30s)
Fallback: muse-spark-1.2-contributor (same endpoint)

## File locations
canonical/           # ACTIVE CODE — all experiments run from here
evolution_lab/       # REFERENCE — sealed evaluator, pool, campaign runner
experiments/stx-001/ # pilot data
experiments/stx-002/ # renamed to static-representation-pilot-001  
experiments/e01-baseline/ # baseline results
docs/NORTHSTAR.md    # long-term vision
docs/TRADING-COGYM-CANONICAL.md # current direction
AGENTS.md            # conventions and rules
