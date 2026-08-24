"""World registry: kind string -> factory. The only place domains are named.

cogym worlds                          # lists registered kinds (factminer.md §53)
create("toy.search_game", n_boxes=10) -> World
"""
from __future__ import annotations
from typing import Callable

_FACTORIES: dict[str, tuple[Callable[..., object], str]] = {}


def register(kind: str, description: str = ""):
    def deco(fn: Callable[..., object]):
        if kind in _FACTORIES:
            raise ValueError(f"world kind already registered: {kind}")
        _FACTORIES[kind] = (fn, description)
        return fn
    return deco


def create(kind: str, **kwargs) -> object:
    if kind not in _FACTORIES:
        raise KeyError(f"unknown world kind '{kind}'. known: {sorted(_FACTORIES)}")
    return _FACTORIES[kind][0](**kwargs)


def kinds() -> dict[str, str]:
    return {k: desc for k, (_, desc) in sorted(_FACTORIES.items())}


# ---------- built-in registrations (lazy imports keep core import-light) ----------

@register("toy.search_game", "10 hidden boxes; find prize at minimum probe cost")
def _toy(n_boxes: int = 10):
    from .toy.search_game import SearchGameWorld
    return SearchGameWorld(n_boxes=n_boxes)


@register("trading.synthetic", "walk-forward stance decisions over a deterministic synthetic market")
def _trading(level: int = 1, seed: int = 42, instrument: str = "SYNTH",
             horizon: int = 5, start_index: int = 60):
    from .trading.adapter import TradingWorldAdapter
    from ..experiments.factory import synthetic_trading_world
    return TradingWorldAdapter(
        synthetic_trading_world(level, seed, instrument),
        horizon=horizon)
