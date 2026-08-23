from __future__ import annotations

from dataclasses import dataclass

from ..market.world import TradingWorld


@dataclass(frozen=True)
class CurriculumSplit:
    training_worlds: tuple[TradingWorld, ...]
    validation_worlds: tuple[TradingWorld, ...]
    hidden_test_worlds: tuple[TradingWorld, ...] = ()

    def __post_init__(self):
        train_ids = {w.manifest.world_id for w in self.training_worlds}
        val_ids = {w.manifest.world_id for w in self.validation_worlds}
        test_ids = {w.manifest.world_id for w in self.hidden_test_worlds}
        if train_ids & val_ids or train_ids & test_ids or val_ids & test_ids:
            raise ValueError("curriculum splits must be disjoint")
