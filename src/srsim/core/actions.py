from dataclasses import dataclass
from typing import Iterable

from .abilities import ActionConfig
from .damage import DamageContext, calculate_damage
from .enums import ActionType
from .unit import Unit


@dataclass
class ActionResult:
    name: str
    actor: str
    damage_done: dict[str, int]
    defeated: list[str]
    sp_delta: int
    energy_delta: dict[str, int]


class BaseAction:
    def __init__(self, actor: Unit, targets: Iterable[Unit], config: ActionConfig) -> None:
        self.actor = actor
        self.targets = list(targets)
        self.config = config

    @property
    def action_type(self) -> ActionType:
        return self.config.action_type

    def validate(self, skill_points: int) -> None:
        if self.actor.is_defeated():
            raise ValueError(f"{self.actor.name} is defeated and cannot act")
        if self.config.sp_cost > skill_points:
            raise ValueError(f"Insufficient skill points for {self.config.name}")
        if self.config.energy_cost > self.actor.energy:
            raise ValueError(f"Insufficient energy for {self.config.name}")

    def execute(self, skill_points: int) -> ActionResult:
        self.validate(skill_points)

        self.actor.spend_energy(self.config.energy_cost)
        damage_done: dict[str, int] = {}
        defeated: list[str] = []
        energy_changes: dict[str, int] = {}

        for target in self.targets:
            if target.is_defeated():
                continue
            ctx = DamageContext(
                attacker=self.actor, defender=target, multiplier=self.config.multiplier
            )
            damage = calculate_damage(ctx)
            damage_done[target.name] = target.take_damage(damage)
            if target.is_defeated():
                defeated.append(target.name)

        sp_delta = self.config.sp_gain - self.config.sp_cost
        energy_gained = self.actor.gain_energy(self.config.energy_gain)
        energy_changes[self.actor.name] = energy_gained - self.config.energy_cost

        return ActionResult(
            name=self.config.name,
            actor=self.actor.name,
            damage_done=damage_done,
            defeated=defeated,
            sp_delta=sp_delta,
            energy_delta=energy_changes,
        )


class BasicAttackAction(BaseAction):
    def __init__(self, actor: Unit, targets: Iterable[Unit], config: ActionConfig) -> None:
        super().__init__(actor, targets, config)


class SkillAction(BaseAction):
    def __init__(self, actor: Unit, targets: Iterable[Unit], config: ActionConfig) -> None:
        super().__init__(actor, targets, config)


class UltimateAction(BaseAction):
    def __init__(self, actor: Unit, targets: Iterable[Unit], config: ActionConfig) -> None:
        super().__init__(actor, targets, config)
