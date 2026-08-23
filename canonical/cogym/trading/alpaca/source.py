"""Fetch historical bars from Alpaca data API → Bar objects for TradingWorld."""
from __future__ import annotations
import os, urllib.request, json
from datetime import datetime, timedelta

BASE = "https://data.alpaca.markets/v2"

def fetch_bars(symbol: str, start: str, end: str, timeframe: str = "1Day",
               api_key_id: str = "", api_secret_key: str = "", feed: str = "iex",
               limit: int = 10000) -> list[dict]:
    """Fetch OHLCV bars. Returns list of dicts with t,o,h,l,c,v."""
    url = f"{BASE}/stocks/{symbol}/bars?timeframe={timeframe}&start={start}&end={end}&limit={limit}&feed={feed}"
    req = urllib.request.Request(url, headers={
        "APCA-API-KEY-ID": api_key_id,
        "APCA-API-SECRET-KEY": api_secret_key,
        "User-Agent": "CogymLab/1.0",
    })
    bars = []
    page_token = None
    while True:
        u = url + (f"&page_token={page_token}" if page_token else "")
        req = urllib.request.Request(u, headers={
            "APCA-API-KEY-ID": api_key_id,
            "APCA-API-SECRET-KEY": api_secret_key,
            "User-Agent": "CogymLab/1.0",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
        except Exception as e:
            print(f"Alpaca fetch error: {e}"); break
        for b in d.get("bars", []):
            bars.append({"t": b["t"], "o": b["o"], "h": b["h"],
                        "l": b["l"], "c": b["c"], "v": b["v"]})
        pt = d.get("next_page_token")
        if not pt: break
        page_token = pt
    return bars
