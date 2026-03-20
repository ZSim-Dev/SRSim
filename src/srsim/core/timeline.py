from dataclasses import dataclass
from typing import Iterable

from .unit import Unit


@dataclass
class Timeline:
    units: list[Unit]

    def __post_init__(self) -> None:
        for index, unit in enumerate(self.units):
            unit.spawn_order = index

    def alive_units(self) -> list[Unit]:
        return [unit for unit in self.units if not unit.is_defeated()]

    def next_actor(self) -> Unit | None:
        alive = self.alive_units()
        if not alive:
            return None
        next_unit = min(alive, key=lambda unit: (unit.current_action_value, unit.spawn_order))
        tick = next_unit.current_action_value
        for unit in alive:
            unit.speed_tick(tick)
        return next_unit

    def reschedule(self, unit: Unit, advance_ratio: float = 0.0, delay_ratio: float = 0.0) -> None:
        unit.reset_action_value(advance_ratio=advance_ratio, delay_ratio=delay_ratio)

    def fast_forward(self, amount: float) -> None:
        for unit in self.alive_units():
            unit.speed_tick(amount)

    def __iter__(self) -> Iterable[Unit]:
        return iter(self.units)
