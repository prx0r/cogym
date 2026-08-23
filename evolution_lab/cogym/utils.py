from __future__ import annotations
import hashlib, json, math
from dataclasses import asdict, is_dataclass
from typing import Any


def _normalize(obj: Any) -> Any:
    if is_dataclass(obj):
        return _normalize(asdict(obj))
    if isinstance(obj, dict):
        return {str(k): _normalize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_normalize(v) for v in obj]
    if isinstance(obj, set):
        return sorted(_normalize(v) for v in obj)
    return obj

def canonical_json(obj: Any) -> str:
    return json.dumps(_normalize(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_id(*parts: Any, prefix: str = "") -> str:
    payload = "|".join(canonical_json(p) if not isinstance(p, str) else p for p in parts)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"{prefix}{digest}"


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    z = math.exp(x)
    return z / (1 + z)
