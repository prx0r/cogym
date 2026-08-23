from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Decision:
    stance: str
    p_up: float
    p_flat: float
    p_down: float
    expected_return: float
    confidence: float
    risk: float
    crux: str = ""
    claims: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    uncertainties: tuple[str, ...] = ()
    falsifiers: tuple[str, ...] = ()
    reasoning_summary: str = ""
    raw: str = ""


def neutral_decision(raw: str = "") -> Decision:
    return Decision("FLAT", 1 / 3, 1 / 3, 1 / 3, 0.0, 0.0, 0.5, raw=raw)


def parse_decision(text: str) -> Decision:
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        obj = json.loads(text[start:end])
        stance = str(obj.get("stance", "FLAT")).upper()
        if stance not in {"LONG", "FLAT", "SHORT"}:
            stance = "FLAT"
        probs = [max(0.0, float(obj.get(k, 0.0))) for k in ("p_up", "p_flat", "p_down")]
        total = sum(probs) or 1.0
        probs = [p / total for p in probs]
        return Decision(
            stance=stance,
            p_up=probs[0],
            p_flat=probs[1],
            p_down=probs[2],
            expected_return=float(obj.get("expected_return", 0.0)),
            confidence=max(0.0, min(1.0, float(obj.get("confidence", 0.5)))),
            risk=max(0.0, min(1.0, float(obj.get("risk", 0.5)))),
            crux=str(obj.get("crux", "")),
            claims=tuple(map(str, obj.get("claims", []))),
            evidence=tuple(map(str, obj.get("evidence", []))),
            uncertainties=tuple(map(str, obj.get("uncertainties", []))),
            falsifiers=tuple(map(str, obj.get("falsifiers", []))),
            reasoning_summary=str(obj.get("reasoning_summary", obj.get("thesis", ""))),
            raw=text,
        )
    except Exception:
        return neutral_decision(text)
