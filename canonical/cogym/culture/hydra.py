from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HydraProjectionRecord:
    kind: str
    text: str
    metadata: dict
    relations: tuple[dict, ...] = ()


def write_hydra_projection(records: list[HydraProjectionRecord], path: str | Path) -> Path:
    """Write a provider-neutral import file for a HydraDB adapter.

    We intentionally do not hard-code unstable remote API shapes into the deterministic core.
    A deployment adapter should map these records to the currently installed HydraDB schema.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps({"kind": r.kind, "text": r.text, "metadata": r.metadata, "relations": list(r.relations)}, sort_keys=True) + "\n")
    return p
