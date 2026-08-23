from __future__ import annotations

import json
import random
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class ChatModel(Protocol):
    model_id: str
    def complete(self, messages: list[Message], *, temperature: float = 0.0, seed: int | None = None) -> str: ...


class OpenAICompatible:
    """Minimal OpenAI-compatible chat-completions adapter.

    Provider-specific retries/routing deliberately stay outside the experiment core.
    Request seed is recorded by callers; providers may ignore unsupported seed fields.
    """
    def __init__(self, model_id: str, base_url: str, api_key: str, timeout: int = 300):
        self.model_id = model_id
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def complete(self, messages: list[Message], *, temperature: float = 0.0, seed: int | None = None) -> str:
        payload = {
            "model": self.model_id,
            "temperature": temperature,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if seed is not None:
            payload["seed"] = seed
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                 "User-Agent": "CogymLab/1.0", "Accept": "application/json"},
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    data = json.load(response)
                break
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 503) and attempt < 2:
                    import time
                    wait = 30 * (attempt + 1)
                    print(f"[model] HTTP {exc.code}, retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                body = exc.read().decode("utf-8", errors="replace")[-2000:]
                raise RuntimeError(f"model HTTP {exc.code}: {body}") from exc
            except urllib.error.URLError as exc:
                raise RuntimeError(f"model URL error: {exc}") from exc
        return data["choices"][0]["message"]["content"]


class HarnessTraderModel:
    """Deterministic/stochastic test double for exercising experiment plumbing only.

    It parses the supplied MarketPacket and reacts to explicit harness markers such as
    FOCUS:DOWNSIDE. It is NOT evidence that a real LLM can be induced into any state.
    """
    model_id = "harness-trader-v1"

    def complete(self, messages: list[Message], *, temperature: float = 0.0, seed: int | None = None) -> str:
        joined = "\n".join(m.content for m in messages)
        rng = random.Random(seed if seed is not None else 0)

        # Transform requests used by offline A-F tests.
        if "COGYM_TRANSFORM:PARAPHRASE_TRACE" in joined:
            source = joined.split("TRACE=", 1)[-1]
            return "PARAPHRASED_TRACE=" + re.sub(r"\s+", " ", source).strip()
        if "COGYM_TRANSFORM:SUMMARIZE_TRACE" in joined:
            source = joined.split("TRACE=", 1)[-1]
            words = source.split()
            return "SUMMARY=" + " ".join(words[:80])
        if "COGYM_MASTER:DESIGN_TRANSMISSION" in joined:
            return json.dumps({
                "diagnosis": "student underweights regime change",
                "prediction": "forcing explicit falsification before commitment should reduce stale-trend errors",
                "steps": [
                    {"id": "m1", "prompt": "Before forecasting, name the market belief most likely to be stale. FOCUS:REGIME"},
                    {"id": "m2", "prompt": "Construct the strongest downside counterfactual and say what evidence would falsify it. FOCUS:DOWNSIDE"},
                    {"id": "m3", "prompt": "Now reconcile both views and state what would make you change your position. FOCUS:FALSIFIERS"},
                ],
            })
        if "COGYM_MASTER:REFLECT" in joined:
            return "Teaching reflection: retain the three-step diagnosis→counterfactual→reconciliation sequence; vary examples, not the invariant."

        m = re.search(r"MARKET_PACKET=(\{.*\})", joined, flags=re.S)
        direction = 0.0
        dchange = 0.0
        volatility = 0.0
        drawdown = 0.0
        if m:
            try:
                packet = json.loads(m.group(1))
                f = packet.get("features", {})
                direction = float(f.get("direction", 0.0))
                dchange = float(f.get("direction_change", 0.0))
                volatility = float(f.get("volatility", 0.0))
                drawdown = float(f.get("drawdown", 0.0))
            except Exception:
                pass

        score = direction + 0.45 * dchange
        if "FOCUS:DOWNSIDE" in joined:
            score -= 0.25 + 0.25 * volatility
        if "FOCUS:UPSIDE" in joined:
            score += 0.25
        if "FOCUS:REGIME" in joined:
            score += 0.5 * dchange
        if "FOCUS:FALSIFIERS" in joined:
            score *= 0.9
        if temperature > 0:
            score += rng.gauss(0.0, min(0.25, temperature * 0.08))

        stance = "LONG" if score > 0.12 else "SHORT" if score < -0.12 else "FLAT"
        p_up = max(0.05, min(0.9, 0.5 + score * 0.35))
        p_down = max(0.05, min(0.9, 0.5 - score * 0.35))
        p_flat = max(0.05, 1.0 - p_up - p_down)
        total = p_up + p_flat + p_down
        p_up, p_flat, p_down = p_up / total, p_flat / total, p_down / total
        return json.dumps({
            "stance": stance,
            "p_up": p_up,
            "p_flat": p_flat,
            "p_down": p_down,
            "expected_return": score * 0.01,
            "confidence": min(0.95, 0.5 + abs(score) * 0.25),
            "risk": min(1.0, 0.25 + volatility + max(0.0, -drawdown)),
            "crux": "whether the current direction persists after the latest change",
            "claims": ["trend information is useful", "recent change can invalidate older trend"],
            "evidence": ["direction", "direction_change", "volatility"],
            "uncertainties": ["synthetic world future is hidden"],
            "falsifiers": ["direction_change reverses sign", "volatility regime changes"],
            "reasoning_summary": "Combine prevailing direction with recent regime change, then adjust aggressiveness for risk.",
        })
