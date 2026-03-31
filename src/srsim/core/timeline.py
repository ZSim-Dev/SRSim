from dataclasses import dataclass, field
from typing import Iterable

from .unit import Unit


@dataclass
class Timeline:
    units: list[Unit]
    spawn_order: dict[str, int] = field(init=False)

    def __post_init__(self) -> None:
        self.spawn_order = {unit.unit_id: index for index, unit in enumerate(self.units)}

    def alive_units(self) -> list[Unit]:
        return [unit for unit in self.units if not unit.is_defeated()]

    def next_actor(self) -> Unit | None:
        alive = self.alive_units()
        if not alive:
            return None
        next_unit = min(
            alive,
            key=lambda unit: (
                unit.current_action_value,
                self.spawn_order.get(unit.unit_id, len(self.units)),
            ),
        )
        tick = next_unit.current_action_value
        for unit in alive:
            unit.speed_tick(tick)
        return next_unit

    def reschedule(self, unit: Unit) -> None:
        unit.reset_action_value()

    def fast_forward(self, amount: int) -> None:
        for unit in self.alive_units():
            unit.speed_tick(amount)

    def __iter__(self) -> Iterable[Unit]:
        return iter(self.units)
