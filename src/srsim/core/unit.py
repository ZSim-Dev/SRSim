from dataclasses import dataclass, field

from .abilities import UnitKit
from .enums import Faction
from .stats import Stats


def action_value_from_spd(spd: int) -> int:
    base = max(1, int(10000 / max(1, spd)))
    return base


@dataclass
class Unit:
    unit_id: str
    name: str
    faction: Faction
    level: int
    base_stats: Stats
    kit: UnitKit
    hp: int = field(init=False)
    energy: int = field(init=False)
    base_action_value: int = field(init=False)
    current_action_value: int = field(init=False)

    def __post_init__(self) -> None:
        self.hp = self.base_stats.max_hp
        self.energy = 0
        self.base_action_value = action_value_from_spd(self.base_stats.spd)
        self.current_action_value = self.base_action_value

    def is_defeated(self) -> bool:
        return self.hp <= 0

    def reset_action_value(self, advance_ratio: float = 0.0, delay_ratio: float = 0.0) -> None:
        offset = self.base_action_value * (delay_ratio - advance_ratio)
        self.current_action_value = max(0, int(self.base_action_value + offset))

    def take_damage(self, amount: int) -> int:
        damage = max(0, amount)
        self.hp = max(0, self.hp - damage)
        return damage

    def heal(self, amount: int) -> int:
        healed = min(self.base_stats.max_hp - self.hp, max(0, amount))
        self.hp += healed
        return healed

    def gain_energy(self, amount: int) -> int:
        gained = max(0, amount)
        self.energy = min(self.base_stats.max_energy, self.energy + gained)
        return gained

    def spend_energy(self, amount: int) -> None:
        if amount > self.energy:
            raise ValueError(f"{self.name} lacks energy: {self.energy} < {amount}")
        self.energy -= amount

    def energy_full(self) -> bool:
        return self.energy >= self.base_stats.max_energy

    def snapshot_stats(self) -> Stats:
        # Placeholder for future buff system, currently return base.
        return self.base_stats.copy()

    def speed_tick(self, delta: int) -> None:
        self.current_action_value = max(0, self.current_action_value - delta)

    def __repr__(self) -> str:
        return f"{self.name}(HP={self.hp}, EN={self.energy}, AV={self.current_action_value})"
