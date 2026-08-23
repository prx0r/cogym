# Cogym - Complete Reference
Every module documented. Last updated 2026-08-23.

## MARKET LAYER (cogym/market/)
Deterministic experimental substrate. Everything seeded and replayable.

### world.py
TradingWorld: the world object.
  manifest: WorldManifest (identity, digest, content-addressed)
  bars: list[Bar] (full price series, generated once, immutable)
  context: list[PointInTimeDatum] (extra data with available_at timestamps)
Key methods:
  .snapshot(index, lookback=72) -> MarketPacket (point-in-time view at step index)
  .fork(index, new_seed) -> new TradingWorld sharing history, diverging after
WorldManifest: immutable identity (name, instrument, bars_digest, dates).

### synthetic.py
level_world(level, seed) -> WorldSpec. Difficulty levels 0-6:
  Level 0: smooth trend | Level 1: bull-bear reversal | Level 2: calm + shocks
  Level 3: choppy + pattern break | Level 4: regime flip (main experiment world)
generate(spec) -> list[Bar]: deterministic OHLCV generation.

### schema.py
Bar: timestamp, OHLCV. PointInTimeDatum: contextual info with available_at enforcement.
MarketPacket: what agent sees at decision time. MarketFeatures: direction/volatility/drawdown.

### features.py
Computes MarketPacket from bars. Point-in-time safe.

### challenge.py
Commit-reveal anti-theatre protocol. ChallengeSpec + CommitRevealRound.

### csvio.py
Load real historical CSV data as alternative to synthetic worlds.

## AGENT LAYER (cogym/agents/)

### model.py
ChatModel: Protocol - .complete(messages, temperature, seed) -> str.
OpenAICompatible: points at any OpenAI-compatible endpoint.
  Currently ox-alpha-free via OpenCode Go endpoint.
  Requires User-Agent header ("CogymLab/1.0") or Cloudflare returns 403.
HarnessTraderModel: deterministic test double. Zero inference cost.

### decision.py
Decision: structured output per reasoning step.
  stance (LONG/SHORT/FLAT), probability distribution, expected_return,
  confidence, risk, crux, claims[], falsifiers[], uncertainties[].
parse_decision(raw): parses JSON from model output into Decision.
Malformed output is behavior, not an error.

### trader.py
market_query(packet): formats MarketPacket into prompt string.
decide(model, packet): calls model.complete(), parses into Decision.

### session.py
AgentSession: manages conversation history across decisions in one run.

## STATE LAYER (cogym/state/)

### pathway.py
ContextPathway: multi-step reasoning treatment (the intervention being tested).
PathwayStep: one step in the pathway (id, prompt, tags like hypothesis/falsification).
run_live_pathway(pathway, model): walks agent through all steps sequentially.
ContextCheckpoint: serialized state snapshot for transfer condition B.
replay_messages(checkpoint): reconstructs conversation from checkpoint.

### signature.py
BehaviorSignature: measurable behavioral fingerprint.
build_signature(decisions): computes accuracy/calibration/entropy/revision metrics.
signature_distance(a, b): distance between two signatures.

### pack.py
PackManifest: immutable cognitive pack (distilled principles + genome + memory seeds).

### transmission.py
Transmission: master-to-student state transfer artifact.
request_transmission(master): asks master to create teaching artifact.
parse_master_transmission(raw): parses master output into structured transfer.

### compiler.py
ablation_candidates(pack): generates ablation variants for testing.

## EXPERIMENT LAYER (cogym/experiments/)

### transfer.py
run_abcdef(): THE main experiment. Tests A-F transfer conditions:
  A live pathway | B checkpoint | C same-model trace | D other-model trace |
  E paraphrased | F summary. Returns StateTransferReport with per-condition results,
  fidelity scores and paired comparisons.

### dose.py
pathway_dose_response(): tests pathway depth 0-5 steps. Measures whether more
reasoning stages improve or degrade decisions.

### social.py
run_social_round(): tests social reveal conditions (peer decision only vs confidence
vs full reasoning artifact). Measures herding and revision quality.

### persistence.py
run_persistence_matrix(): tests persistent vs reset context across episodes.
Measures learning, negative transfer, washout.

### contagion.py
run_state_contagion(): tests whether induced state spreads through ordinary
conversation without explicit teaching.

### composition.py
compose(): tests pack collision and interleaving effects.

### team.py
run_team(): multi-agent team experiments with different topologies.

### convergence.py
teacher_reference_revision_loop(): measures whether agents converge toward teacher
behavior over multiple rounds.

### treatments.py
Treatment class + run_treatment_matrix(): runs the full treatment matrix.

### factory.py
synthetic_trading_world(level, seed): convenience function to create TradingWorld.

### runner.py
run_world(model, world, condition, ...): runs one agent on one world.
summarize_repeats(results): aggregates across stochastic samples.

### scoring.py
DecisionScore + score_decision() + outcome_class(): deterministic grading of
decisions against oracle outcomes.


## CORE LAYER (cogym/core/)

### agent_spec.py
AgentSpec: typed, frozen organism definition. Content-hash ID.
Extends AgentGenome with context_modules, skills, tools_policy.
Use .with_changes(**kw) to create mutated copies. Use .from_genome(genome) to convert.

### episode.py
Episode: immutable record of one subject-in-world interaction.
Contains: world_name, world_seed, agent_spec_id, treatment, decisions tuple, metrics.

### events.py
EventLedger: append-only hash-chained audit trail. Each event links to previous.
Event kinds: campaign_created, candidate_proposed, episode_finished, etc.
NEVER rewrite history. New interpretations are new events.

## REASONING INTELLIGENCE (cogym/ root modules)

### hardworlds.py
Generates worlds where naive policy != oracle policy. 5 families:
  difficulty_weighted_rank: raw success vs deployment-weighted quality disagree
  base_rate_shift: salient recent evidence conflicts with base rate
  confounded_choice: correlation suggests A, causation says B
  regime_flip: historically optimal rule becomes harmful
  costly_evidence: information helps but costs more than improvement
Each world carries oracle_choice + naive_choice. Hardness invariant enforced.

### skill_registry.py
SkillRegistry: skills enter population ONLY after paired probe evidence.
SkillArtifact: content + creator + parents + hypothesis + status.
SkillEvaluation: paired delta receipt with evidence_layer tracking.
Lifecycle: PROPOSED -> DEV_USEFUL -> SECRET_CONFIRMED -> REPLAY_SAFE -> TRANSFERRED -> REPLICATED
Terminal states: REJECTED / REGRESSED / STALE / INVALIDATED (never eligible).
Evidence-layer specific transitions prevent DEV-only spoofing of higher states.
MIN_PROBES = 5. MIN_MEAN_DELTA = 0.02. Regression on unrelated probes blocks acceptance.

### sealed_eval.py
SealedRun + SandboxGrant: sandbox contract for subject isolation.
Canary identifiers detect attempted access to forbidden paths.
Violations invalidate the run. Currently skeleton - needs actual enforcement.

### orchestration/hermes_proposals.py
propose_mutations(parents, failures, n): sends DEV failure data to hermes/mimo,
receives mutation proposals, validates against enum spaces. Drops invalid changes.
apply_mutations(parents, proposals): creates mutated genomes with hypothesis metadata.


## CULTURE LAYER (cogym/culture/)

### hydra.py
HydraProjectionRecord + write_hydra_projection(): projects validated findings into
HydraDB graph format. Only validated relationships should be projected.

### lore.py
LoreArtifact: accumulated cultural knowledge artifact.

### store.py
EvidenceGraph: stores validated reasoning-pattern relationships.

## DOJO LAYER (cogym/dojo/)

### master.py
PersistentMaster: a master agent that accumulates experience across curricula.
StudentEvaluation: paired evaluation of student after teaching.

### chain.py
transmission_chain(): A teaches B, B teaches C, etc. Tracks fidelity per hop.
ChainHop: one link in the chain with source/target/fidelity metrics.

### curriculum.py
CurriculumSplit: designs diagnostic world sequences for training.

### population.py
MasterScore + score_master(): ranks multiple masters by student improvement.
faculty_roundtable(): multiple masters exchange techniques.

## PROOFS LAYER (cogym/proofs/)

### receipt.py
ExperimentReceipt: immutable proof that an experiment was run.
ModelExecutionClaim: claim about a specific model inference.

### deep_prove.py
External zkML proof boundary. Never fakes a proof.

## CLI (cogym/cli.py)
  cogym smoke          runs a single experiment (infrastructure check)
  cogym dojo-demo      runs master->student demonstration
  cogym evolve <yaml>  runs an evolution campaign

---

## QUICK START FOR NEW AGENTS

1. Read this file top to bottom.
2. Read AGENTS.md for conventions and rules.
3. Run: cd /root/cogym/canonical && source .venv/bin/activate && pytest tests/ -q
   Should show 16 passed. If not, something is broken - fix before proceeding.
4. To run a real experiment:
   ```python
   from cogym.agents.model import OpenAICompatible, Message
   from cogym.experiments.transfer import run_abcdef
   from cogym.experiments.factory import synthetic_trading_world
   from cogym.state.pathway import ContextPathway, PathwayStep

   model = OpenAICompatible(
       model_id="ox-alpha-free",
       base_url="https://opencode.ai/zen/go/v1",
       api_key=os.environ["OPENCODE_GO_API_KEY"],
   )
   world = synthetic_trading_world(level=4, seed=42)
   pathway = ContextPathway(name="test", steps=(
       PathwayStep(id="s1", prompt="What would falsify your hypothesis?"),
   ))
   report = run_abcdef(target_model=model, world=world, pathway=pathway, repeats=1)
   ```

5. To extract a contract from a hackathon page:
   ```bash
   cd /root/cogym && HERMES_MODEL=ox-alpha-free scripts/extract-contract.sh <slug> <url>
   ```

6. To import ChatGPT-discovered candidates:
   ```bash
   node scripts/import-candidates.mjs data/candidates/<file>.json
   ```
