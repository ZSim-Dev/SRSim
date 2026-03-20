from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .abilities import ActionConfig
from .damage import DamageContext, calculate_damage, calculate_healing, calculate_shield
from .events import EventType
from .enums import ActionType
from .unit import Unit

if TYPE_CHECKING:
    from .battle_state import BattleState


@dataclass
class ActionResult:
    name: str
    actor: str
    damage_done: dict[str, int]
    shield_absorbed: dict[str, int]
    healing_done: dict[str, int]
    shields_added: dict[str, int]
    statuses_applied: dict[str, list[str]]
    toughness_damage_done: dict[str, int]
    broken_targets: list[str]
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
        if not self.actor.can_act():
            raise ValueError(f"{self.actor.name} is unable to act")
        if self.config.sp_cost > skill_points:
            raise ValueError(f"Insufficient skill points for {self.config.name}")
        if self.config.energy_cost > self.actor.energy:
            raise ValueError(f"Insufficient energy for {self.config.name}")

    def execute(self, battle_state: "BattleState | int") -> ActionResult:
        state = battle_state if not isinstance(battle_state, int) else None
        skill_points = battle_state if isinstance(battle_state, int) else battle_state.skill_points
        self.validate(skill_points)

        self.actor.spend_energy(self.config.energy_cost)
        damage_done: dict[str, int] = {}
        shield_absorbed: dict[str, int] = {}
        healing_done: dict[str, int] = {}
        shields_added: dict[str, int] = {}
        statuses_applied: dict[str, list[str]] = {}
        toughness_damage_done: dict[str, int] = {}
        broken_targets: list[str] = []
        defeated: list[str] = []
        energy_changes: dict[str, int] = {}
        kill_energy_gain = 0
        action_element = self.config.element or self.actor.element

        for target in self.targets:
            if target.is_defeated():
                continue

            if self.config.multiplier > 0:
                ctx = DamageContext(
                    attacker=self.actor,
                    defender=target,
                    multiplier=self.config.multiplier,
                    element=action_element,
                )
                damage = calculate_damage(ctx)
                previous_shield = target.shield
                hp_damage = target.take_damage(damage)
                absorbed = max(0, previous_shield - target.shield)
                if absorbed > 0:
                    shield_absorbed[target.name] = absorbed
                total_damage = absorbed + hp_damage
                damage_done[target.name] = total_damage
                if state is not None:
                    state.events.emit(
                        EventType.HIT,
                        actor_id=self.actor.unit_id,
                        target_id=target.unit_id,
                        payload={"amount": total_damage, "action": self.config.name},
                    )
                    state.events.emit(
                        EventType.DAMAGE_DEALT,
                        actor_id=self.actor.unit_id,
                        target_id=target.unit_id,
                        payload={"amount": total_damage},
                    )

            if target.toughness is not None:
                break_outcome = target.toughness.apply(
                    self.config.toughness_damage,
                    action_element,
                    self.actor.level,
                )
                if break_outcome.toughness_damage > 0:
                    toughness_damage_done[target.name] = break_outcome.toughness_damage
                    if state is not None:
                        state.events.emit(
                            EventType.TOUGHNESS_DAMAGE,
                            actor_id=self.actor.unit_id,
                            target_id=target.unit_id,
                            payload={"amount": break_outcome.toughness_damage},
                        )
                if break_outcome.broken:
                    target.current_action_value += max(1, int(target.base_action_value * 0.25))
                    break_damage = target.take_damage(break_outcome.break_damage)
                    damage_done[target.name] = damage_done.get(target.name, 0) + break_damage
                    broken_targets.append(target.name)
                    if state is not None:
                        state.events.emit(
                            EventType.WEAKNESS_BREAK,
                            actor_id=self.actor.unit_id,
                            target_id=target.unit_id,
                            payload={"break_damage": break_damage},
                        )

            for template in self.config.target_statuses:
                instance = target.apply_status(template, self.actor.unit_id)
                statuses_applied.setdefault(target.name, []).append(instance.name)
                if state is not None:
                    state.events.emit(
                        EventType.STATUS_APPLY,
                        actor_id=self.actor.unit_id,
                        target_id=target.unit_id,
                        payload={"status": instance.name},
                    )

            if target.is_defeated():
                defeated.append(target.name)
                kill_energy_gain += self.actor.gain_energy(10)
                if state is not None:
                    state.events.emit(
                        EventType.KILL,
                        actor_id=self.actor.unit_id,
                        target_id=target.unit_id,
                    )
                    state.events.emit(
                        EventType.UNIT_DOWNED,
                        actor_id=self.actor.unit_id,
                        target_id=target.unit_id,
                    )

        if self.config.self_heal_multiplier > 0 or self.config.self_heal_flat > 0:
            heal_amount = calculate_healing(
                self.actor,
                self.actor,
                self.config.self_heal_multiplier,
                self.config.self_heal_flat,
            )
            actual_heal = self.actor.heal(heal_amount)
            healing_done[self.actor.name] = actual_heal
            if state is not None:
                state.events.emit(
                    EventType.HEAL_DONE,
                    actor_id=self.actor.unit_id,
                    target_id=self.actor.unit_id,
                    payload={"amount": actual_heal},
                )

        if self.config.self_shield_multiplier > 0 or self.config.self_shield_flat > 0:
            shield_amount = calculate_shield(
                self.actor,
                self.config.self_shield_multiplier,
                self.config.self_shield_flat,
            )
            actual_shield = self.actor.apply_shield(shield_amount)
            shields_added[self.actor.name] = actual_shield
            if state is not None:
                state.events.emit(
                    EventType.SHIELD_APPLIED,
                    actor_id=self.actor.unit_id,
                    target_id=self.actor.unit_id,
                    payload={"amount": actual_shield},
                )

        for template in self.config.actor_statuses:
            instance = self.actor.apply_status(template, self.actor.unit_id)
            statuses_applied.setdefault(self.actor.name, []).append(instance.name)
            if state is not None:
                state.events.emit(
                    EventType.STATUS_APPLY,
                    actor_id=self.actor.unit_id,
                    target_id=self.actor.unit_id,
                    payload={"status": instance.name},
                )

        sp_delta = self.config.sp_gain - self.config.sp_cost
        energy_gained = self.actor.gain_energy(self.config.energy_gain)
        energy_changes[self.actor.name] = energy_gained + kill_energy_gain - self.config.energy_cost

        return ActionResult(
            name=self.config.name,
            actor=self.actor.name,
            damage_done=damage_done,
            shield_absorbed=shield_absorbed,
            healing_done=healing_done,
            shields_added=shields_added,
            statuses_applied=statuses_applied,
            toughness_damage_done=toughness_damage_done,
            broken_targets=broken_targets,
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
