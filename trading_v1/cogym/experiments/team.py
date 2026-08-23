from __future__ import annotations

from dataclasses import dataclass

from ..agents.decision import Decision, parse_decision
from ..agents.model import ChatModel, Message
from ..agents.trader import market_query
from ..canonical import canonical_json
from ..market.schema import MarketPacket


@dataclass(frozen=True)
class TeamResult:
    private_decisions: tuple[Decision, ...]
    final_decision: Decision
    architecture: str


def run_team(
    members: list[ChatModel],
    packet: MarketPacket,
    *,
    horizon_steps: int,
    synthesizer: ChatModel | None = None,
    architecture: str = "independent_then_synthesize",
    seed: int = 0,
) -> TeamResult:
    if not members:
        raise ValueError("members required")
    if architecture not in {"independent_then_synthesize", "sequential_debate"}:
        raise ValueError("invalid architecture")
    private: list[Decision] = []
    raws: list[str] = []
    for i, model in enumerate(members):
        raw = model.complete([Message("user", market_query(packet, horizon_steps))], temperature=0.2, seed=seed+i)
        raws.append(raw)
        private.append(parse_decision(raw))

    synth = synthesizer or members[0]
    if architecture == "independent_then_synthesize":
        prompt = market_query(packet, horizon_steps) + "\nYou are the team synthesizer. These were independent private forecasts. Reconcile evidence, not personalities or majority size. Return the normal JSON only.\nMEMBER_OUTPUTS=" + canonical_json(raws)
        final_raw = synth.complete([Message("user", prompt)], temperature=0.2, seed=seed+1000)
    else:
        transcript: list[Message] = [Message("user", market_query(packet, horizon_steps))]
        for i, raw in enumerate(raws):
            transcript.append(Message("assistant", f"Member {i} private proposal: {raw}"))
        transcript.append(Message("user", "Debate the strongest disagreement once, then produce one final forecast JSON. Do not defer to majority count."))
        final_raw = synth.complete(transcript, temperature=0.2, seed=seed+1000)
    return TeamResult(tuple(private), parse_decision(final_raw), architecture)
