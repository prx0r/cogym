from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from .schema import Bar


def _parse_ts(value: str) -> datetime:
    value = value.strip()
    if value.isdigit():
        n = int(value)
        if n > 10_000_000_000:
            n = n / 1000
        return datetime.fromtimestamp(n, tz=timezone.utc)
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def read_ohlcv(path: str | Path, instrument: str | None = None) -> list[Bar]:
    """Read canonical OHLCV CSV.

    Required columns: timestamp/open/high/low/close. Optional: volume,instrument.
    Historical source provenance belongs in the surrounding WorldManifest, not inferred here.
    """
    out: list[Bar] = []
    with Path(path).open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            inst = instrument or row.get("instrument") or "UNKNOWN"
            out.append(Bar(
                inst,
                _parse_ts(row["timestamp"]),
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
                float(row.get("volume") or 0.0),
            ))
    out.sort(key=lambda b: b.ts)
    return out
