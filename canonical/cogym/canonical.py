from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _normalize(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _normalize(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not canonical")
        return float(format(value, ".15g"))
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(_normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def commitment(domain: str, *parts: Any) -> str:
    h = hashlib.sha256()
    h.update(domain.encode("utf-8"))
    h.update(b"\0")
    for part in parts:
        h.update(canonical_json(part).encode("utf-8"))
        h.update(b"\0")
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()
