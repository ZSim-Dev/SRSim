from dataclasses import dataclass
from typing import Iterable

from .unit import Unit


@dataclass
class Timeline:
    units: list[Unit]

    def alive_units(self) -> list[Unit]:
        return [unit for unit in self.units if not unit.is_defeated()]

    def next_actor(self) -> Unit | None:
        alive = self.alive_units()
        if not alive:
            return None
        next_unit = min(alive, key=lambda unit: unit.current_action_value)
        tick = next_unit.current_action_value
        for unit in alive:
            unit.speed_tick(tick)
        return next_unit

    def reschedule(self, unit: Unit, advance_ratio: float = 0.0, delay_ratio: float = 0.0) -> None:
        unit.reset_action_value(advance_ratio=advance_ratio, delay_ratio=delay_ratio)

    def fast_forward(self, amount: int) -> None:
        for unit in self.alive_units():
            unit.speed_tick(amount)

    def __iter__(self) -> Iterable[Unit]:
        return iter(self.units)
