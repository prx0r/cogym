from __future__ import annotations
import csv, math
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Bar:
    timestamp:int; open:float; high:float; low:float; close:float; volume:float


def load_csv_bars(path:str|Path)->list[Bar]:
    out=[]
    with open(path,newline="") as f:
        rd=csv.DictReader(f)
        for r in rd:
            # accepts common upper/lower case conventions
            low={k.lower():v for k,v in r.items()}
            out.append(Bar(int(float(low["timestamp"])),float(low["open"]),float(low["high"]),
                           float(low["low"]),float(low["close"]),float(low.get("volume",0) or 0)))
    return out


def resample_bars(bars:list[Bar],seconds:int)->list[Bar]:
    if not bars: return []
    buckets={}
    for b in bars:
        key=(b.timestamp//seconds)*seconds
        buckets.setdefault(key,[]).append(b)
    out=[]
    for k in sorted(buckets):
        xs=buckets[k]
        out.append(Bar(k,xs[0].open,max(x.high for x in xs),min(x.low for x in xs),xs[-1].close,sum(x.volume for x in xs)))
    return out
