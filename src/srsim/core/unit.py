from dataclasses import dataclass, field

from .abilities import UnitKit
from .enums import Faction
from .stats import Stats

ACTION_GAUGE_BASE = 10000.0


@dataclass
class SpeedState:
    current_spd: float
    current_av: float
    current_ag: float


@dataclass
class CombatModifiers:
    damage_boost: float = 0.0
    weaken: float = 0.0
    defense_bonus: float = 0.0
    defense_reduction: float = 0.0
    defense_ignore: float = 0.0
    resistance: float = 0.0
    res_pen: float = 0.0
    vulnerability: float = 0.0
    mitigation: float = 0.0


@dataclass
class ToughnessState:
    current: int
    maximum: int
    broken: bool = False


def action_value_from_spd(spd: float) -> float:
    return ACTION_GAUGE_BASE / max(1.0, spd)


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
    speed_state: SpeedState = field(init=False)
    modifiers: CombatModifiers = field(default_factory=CombatModifiers)
    toughness: ToughnessState | None = None
    spawn_order: int = 0

    def __post_init__(self) -> None:
        self.hp = self.base_stats.max_hp
        self.energy = 0
        base_av = action_value_from_spd(self.base_stats.spd)
        self.speed_state = SpeedState(
            current_spd=float(self.base_stats.spd),
            current_av=base_av,
            current_ag=base_av * float(self.base_stats.spd),
        )

    @property
    def base_action_value(self) -> float:
        return action_value_from_spd(self.base_stats.spd)

    @property
    def current_action_value(self) -> float:
        return self.speed_state.current_av

    def is_defeated(self) -> bool:
        return self.hp <= 0

    def reset_action_value(self, advance_ratio: float = 0.0, delay_ratio: float = 0.0) -> None:
        self.speed_state.current_av = action_value_from_spd(self.speed_state.current_spd)
        self.speed_state.current_ag = self.speed_state.current_av * self.speed_state.current_spd
        if advance_ratio != 0.0 or delay_ratio != 0.0:
            self.modify_action_gauge(advance_ratio=advance_ratio, delay_ratio=delay_ratio)

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
        stats = self.base_stats.copy()
        stats.spd = int(round(self.speed_state.current_spd))
        stats.dmg_boost += self.modifiers.damage_boost
        stats.resistance += self.modifiers.resistance
        return stats

    def speed_tick(self, delta: float) -> None:
        self.speed_state.current_av = max(0.0, self.speed_state.current_av - delta)
        self.speed_state.current_ag = self.speed_state.current_av * self.speed_state.current_spd

    def set_speed(self, new_spd: float) -> None:
        bounded_spd = max(1.0, new_spd)
        current_av = self.speed_state.current_av
        current_spd = self.speed_state.current_spd
        self.speed_state.current_av = current_av * current_spd / bounded_spd
        self.speed_state.current_spd = bounded_spd
        self.speed_state.current_ag = self.speed_state.current_av * bounded_spd

    def modify_action_gauge(self, advance_ratio: float = 0.0, delay_ratio: float = 0.0) -> None:
        new_ag = max(
            0.0,
            self.speed_state.current_ag - ACTION_GAUGE_BASE * (advance_ratio - delay_ratio),
        )
        self.speed_state.current_ag = new_ag
        self.speed_state.current_av = new_ag / self.speed_state.current_spd

    def mark_broken(self, broken: bool) -> None:
        if self.toughness is None:
            return
        self.toughness.broken = broken

    def is_broken(self) -> bool:
        return self.toughness is not None and self.toughness.broken

    def __repr__(self) -> str:
        return (
            f"{self.name}(HP={self.hp}, EN={self.energy}, SPD={self.speed_state.current_spd}, "
            f"AV={self.speed_state.current_av:.2f})"
        )
