from __future__ import annotations

from dataclasses import dataclass
import math
import statistics

from ..agents.decision import Decision
from ..agents.model import ChatModel, Message
from ..canonical import commitment
from ..market.world import TradingWorld
from ..state.pathway import ContextCheckpoint, ContextPathway, run_live_pathway
from ..state.signature import lexical_artifact_similarity, signature_distance
from .runner import RunResult, run_world, summarize_repeats


@dataclass(frozen=True)
class TransferConditionResult:
    label: str
    runs: tuple[RunResult, ...]
    source_checkpoint_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StateTransferReport:
    experiment_id: str
    conditions: tuple[TransferConditionResult, ...]
    decision_fidelity: dict[str, float]
    behavior_distance: dict[str, float]
    artifact_similarity: dict[str, float]
    notes: tuple[str, ...]


def _transform_trace(model: ChatModel, checkpoint: ContextCheckpoint, mode: str, seed: int) -> list[Message]:
    transcript = "\n".join(f"{m.role.upper()}: {m.content}" for m in checkpoint.messages)
    if mode == "paraphrase":
        prompt = "COGYM_TRANSFORM:PARAPHRASE_TRACE\nPreserve propositions and ordering but rewrite wording. Return transformed trace text only.\nTRACE=" + transcript
    elif mode == "summary":
        prompt = "COGYM_TRANSFORM:SUMMARIZE_TRACE\nSummarize lessons only, removing dialogue trajectory. Return summary only.\nTRACE=" + transcript
    else:
        raise ValueError(mode)
    raw = model.complete([Message("user", prompt)], temperature=0.0, seed=seed)
    return [Message("system", f"Imported {mode} of a prior training trajectory."), Message("user", raw)]


def _decision_distance(a: Decision, b: Decision) -> float:
    stance = 0.0 if a.stance == b.stance else 1.0
    probs = math.sqrt(((a.p_up-b.p_up)**2 + (a.p_flat-b.p_flat)**2 + (a.p_down-b.p_down)**2) / 3.0)
    return (stance + probs + min(1.0, abs(a.expected_return-b.expected_return) * 20.0) + abs(a.confidence-b.confidence) + abs(a.risk-b.risk)) / 5.0


def _pair_fidelity(reference: list[RunResult], candidate: list[RunResult]) -> tuple[float, float]:
    ds: list[float] = []
    arts: list[float] = []
    for ra, rb in zip(reference, candidate):
        for aa, bb in zip(ra.records, rb.records):
            ds.append(_decision_distance(aa.decision, bb.decision))
            arts.append(lexical_artifact_similarity(aa.decision, bb.decision))
    return 1.0 - statistics.mean(ds) if ds else 0.0, statistics.mean(arts) if arts else 0.0


def run_abcdef(
    target_model: ChatModel,
    world: TradingWorld,
    pathway: ContextPathway,
    *,
    repeats: int = 3,
    donor_model: ChatModel | None = None,
    transform_model: ChatModel | None = None,
    indices: list[int] | None = None,
    temperature: float = 0.2,
    base_seed: int = 100,
) -> StateTransferReport:
    """Run the canonical A-F state-transfer experiment.

    A live self-path
    B exact own-trace replay
    C same-model other-trace replay
    D other-model trace replay (or same donor if omitted, explicitly noted)
    E paraphrased trace
    F summary-only trace
    """
    donor_model = donor_model or target_model
    transform_model = transform_model or target_model
    labels = "ABCDEF"
    buckets: dict[str, list[RunResult]] = {x: [] for x in labels}
    checkpoint_ids: dict[str, list[str]] = {x: [] for x in labels}

    live_checkpoints: list[ContextCheckpoint] = []
    donor_checkpoints: list[ContextCheckpoint] = []
    for rep in range(repeats):
        seed = base_seed + rep * 10000
        live = run_live_pathway(pathway, target_model, temperature=temperature, seed=seed)
        donor = run_live_pathway(pathway, donor_model, temperature=temperature, seed=seed + 777)
        live_checkpoints.append(live)
        donor_checkpoints.append(donor)
        buckets["A"].append(run_world(target_model, world, condition="A_live_self_path", history=list(live.messages), indices=indices, temperature=temperature, sample_seed=seed + 1000))
        checkpoint_ids["A"].append(live.checkpoint_id)

    for rep in range(repeats):
        seed = base_seed + rep * 10000
        own = live_checkpoints[rep]
        other = live_checkpoints[(rep + 1) % repeats] if repeats > 1 else live_checkpoints[rep]
        donor = donor_checkpoints[rep]
        buckets["B"].append(run_world(target_model, world, condition="B_exact_own_trace", history=list(own.messages), indices=indices, temperature=temperature, sample_seed=seed + 2000))
        buckets["C"].append(run_world(target_model, world, condition="C_same_model_other_trace", history=list(other.messages), indices=indices, temperature=temperature, sample_seed=seed + 3000))
        buckets["D"].append(run_world(target_model, world, condition="D_other_model_trace", history=list(donor.messages), indices=indices, temperature=temperature, sample_seed=seed + 4000))
        buckets["E"].append(run_world(target_model, world, condition="E_paraphrased_trace", history=_transform_trace(transform_model, own, "paraphrase", seed + 500), indices=indices, temperature=temperature, sample_seed=seed + 5000))
        buckets["F"].append(run_world(target_model, world, condition="F_summary", history=_transform_trace(transform_model, own, "summary", seed + 600), indices=indices, temperature=temperature, sample_seed=seed + 6000))
        checkpoint_ids["B"].append(own.checkpoint_id)
        checkpoint_ids["C"].append(other.checkpoint_id)
        checkpoint_ids["D"].append(donor.checkpoint_id)

    ref = buckets["A"]
    decision_fidelity: dict[str, float] = {"A": 1.0}
    behavior_distance: dict[str, float] = {"A": 0.0}
    artifact_similarity: dict[str, float] = {"A": 1.0}
    ref_summary = summarize_repeats(ref, "A")
    for label in "BCDEF":
        fidelity, art = _pair_fidelity(ref, buckets[label])
        decision_fidelity[label] = fidelity
        artifact_similarity[label] = art
        behavior_distance[label] = signature_distance(ref_summary.mean_signature, summarize_repeats(buckets[label], label).mean_signature)

    experiment_id = commitment("COGYM:ABCDEF:v1", world.manifest.world_id, pathway.pathway_id, target_model.model_id, donor_model.model_id, repeats, base_seed)
    notes = (
        "LLM sampling is treated as experimental variance; exact token equality is not required.",
        "Trace fidelity uses observable structured artifacts, not private chain-of-thought.",
        "D uses target_model as donor if no separate donor_model is supplied.",
    )
    return StateTransferReport(
        experiment_id,
        tuple(TransferConditionResult(label, tuple(buckets[label]), tuple(checkpoint_ids[label])) for label in labels),
        decision_fidelity,
        behavior_distance,
        artifact_similarity,
        notes,
    )
