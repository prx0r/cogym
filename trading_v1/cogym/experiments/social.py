from __future__ import annotations

from dataclasses import dataclass

from ..agents.decision import Decision, parse_decision
from ..agents.model import ChatModel, Message
from ..agents.trader import market_query
from ..canonical import canonical_json
from ..market.schema import MarketPacket


@dataclass(frozen=True)
class SocialDecision:
    agent_id: str
    private: Decision
    revised: Decision
    changed: bool


def run_social_round(
    agents: dict[str, ChatModel],
    packet: MarketPacket,
    *,
    horizon_steps: int,
    visibility: str = "decision_confidence",
    seed: int = 0,
) -> tuple[SocialDecision, ...]:
    if visibility not in {"decision_only", "decision_confidence", "full_artifact"}:
        raise ValueError("invalid visibility")
    private: dict[str, Decision] = {}
    for n, (aid, model) in enumerate(sorted(agents.items())):
        raw = model.complete([Message("user", market_query(packet, horizon_steps))], temperature=0.2, seed=seed + n)
        private[aid] = parse_decision(raw)

    peer_payload = {}
    for aid, d in private.items():
        if visibility == "decision_only":
            peer_payload[aid] = {"stance": d.stance}
        elif visibility == "decision_confidence":
            peer_payload[aid] = {"stance": d.stance, "confidence": d.confidence, "p_up": d.p_up, "p_flat": d.p_flat, "p_down": d.p_down}
        else:
            peer_payload[aid] = {"stance": d.stance, "confidence": d.confidence, "crux": d.crux, "claims": d.claims, "falsifiers": d.falsifiers}

    out: list[SocialDecision] = []
    for n, (aid, model) in enumerate(sorted(agents.items())):
        prompt = (
            market_query(packet, horizon_steps)
            + "\nYou already made a private forecast. Here are peer outputs. Separate actual new evidence from social pressure. You may KEEP, AMEND, or REVERSE. Return the normal decision JSON only."
            + "\nYOUR_PRIVATE=" + canonical_json(private[aid])
            + "\nPEERS=" + canonical_json({k: v for k, v in peer_payload.items() if k != aid})
        )
        raw = model.complete([Message("user", prompt)], temperature=0.2, seed=seed + 100 + n)
        revised = parse_decision(raw)
        out.append(SocialDecision(aid, private[aid], revised, private[aid].stance != revised.stance or abs(private[aid].expected_return - revised.expected_return) > 1e-12))
    return tuple(out)
