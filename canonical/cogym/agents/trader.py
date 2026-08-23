from __future__ import annotations

from dataclasses import asdict

from ..canonical import canonical_json
from ..market.schema import MarketPacket
from .decision import Decision, parse_decision
from .model import ChatModel, Message


DECISION_CONTRACT = """You are participating in a paper-trading cognition benchmark. Use only supplied point-in-time information; no real trades are executed.
Return JSON only with:
stance LONG|FLAT|SHORT; p_up,p_flat,p_down; expected_return; confidence; risk;
crux; claims[]; evidence[]; uncertainties[]; falsifiers[]; reasoning_summary.
Probabilities refer to the supplied horizon and should sum to 1. Keep reasoning_summary concise; do not expose hidden chain-of-thought."""


def market_query(packet: MarketPacket, horizon_steps: int) -> str:
    return (
        DECISION_CONTRACT
        + f"\nFORECAST_HORIZON_STEPS={horizon_steps}"
        + "\nMARKET_PACKET="
        + canonical_json(asdict(packet))
    )


def decide(
    model: ChatModel,
    history: list[Message],
    packet: MarketPacket,
    *,
    horizon_steps: int,
    temperature: float = 0.0,
    seed: int | None = None,
) -> tuple[Decision, Message]:
    query = Message("user", market_query(packet, horizon_steps))
    raw = model.complete([*history, query], temperature=temperature, seed=seed)
    return parse_decision(raw), Message("assistant", raw)
