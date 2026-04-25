from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .abilities import ActionConfig
from .damage import DamageContext, calculate_damage, calculate_healing, calculate_shield
from .enums import ActionType
from .events import EventType
from .unit import Unit

if TYPE_CHECKING:
    from .battle_state import BattleState


@dataclass
class TargetAmountResult:
    target_id: str
    target_name: str
    amount: int


@dataclass
class TargetStatusesResult:
    target_id: str
    target_name: str
    statuses: list[str]


@dataclass
class ActionResult:
    name: str
    actor: str
    damage_done: list[TargetAmountResult]
    shield_absorbed: list[TargetAmountResult]
    healing_done: list[TargetAmountResult]
    shields_added: list[TargetAmountResult]
    statuses_applied: list[TargetStatusesResult]
    toughness_damage_done: list[TargetAmountResult]
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

    def has_living_target(self) -> bool:
        return any(not target.is_defeated() for target in self.targets)

    def validate(self, skill_points: int) -> None:
        if self.actor.is_defeated():
            raise ValueError(f"{self.actor.name} is defeated and cannot act")
        if not self.actor.can_act():
            raise ValueError(f"{self.actor.name} is unable to act")
        if self.config.sp_cost > skill_points:
            raise ValueError(f"Insufficient skill points for {self.config.name}")
        if self.config.energy_cost > self.actor.energy:
            raise ValueError(f"Insufficient energy for {self.config.name}")

    def execute(self, battle_state: "BattleState") -> ActionResult:
        state = battle_state
        self.validate(battle_state.skill_points)

        self.actor.spend_energy(self.config.energy_cost)
        damage_done: dict[str, TargetAmountResult] = {}
        shield_absorbed: dict[str, TargetAmountResult] = {}
        healing_done: dict[str, TargetAmountResult] = {}
        shields_added: dict[str, TargetAmountResult] = {}
        statuses_applied: dict[str, TargetStatusesResult] = {}
        toughness_damage_done: dict[str, TargetAmountResult] = {}
        broken_targets: list[str] = []
        defeated: list[str] = []
        energy_changes: dict[str, int] = {}
        kill_energy_gain = 0
        action_element = self.config.element or self.actor.element
        defeated_unit_ids: set[str] = set()

        def record_defeat(target: Unit) -> None:
            nonlocal kill_energy_gain
            if target.unit_id in defeated_unit_ids:
                return
            defeated_unit_ids.add(target.unit_id)
            defeated.append(target.name)
            kill_energy_gain += self.actor.gain_energy(10)
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

        def add_amount(
            bucket: dict[str, TargetAmountResult],
            target: Unit,
            amount: int,
        ) -> None:
            current = bucket.get(target.unit_id)
            if current is None:
                bucket[target.unit_id] = TargetAmountResult(
                    target_id=target.unit_id,
                    target_name=target.name,
                    amount=amount,
                )
                return
            bucket[target.unit_id] = TargetAmountResult(
                target_id=current.target_id,
                target_name=current.target_name,
                amount=current.amount + amount,
            )

        def add_status(target: Unit, status_name: str) -> None:
            current = statuses_applied.get(target.unit_id)
            if current is None:
                statuses_applied[target.unit_id] = TargetStatusesResult(
                    target_id=target.unit_id,
                    target_name=target.name,
                    statuses=[status_name],
                )
                return
            current.statuses.append(status_name)

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
                    add_amount(shield_absorbed, target, absorbed)
                total_damage = absorbed + hp_damage
                add_amount(damage_done, target, total_damage)
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
                if target.is_defeated():
                    record_defeat(target)
                    continue

            if target.toughness is not None:
                break_outcome = target.toughness.apply(
                    self.config.toughness_damage,
                    action_element,
                    self.actor.level,
                )
                if break_outcome.toughness_damage > 0:
                    add_amount(toughness_damage_done, target, break_outcome.toughness_damage)
                    state.events.emit(
                        EventType.TOUGHNESS_DAMAGE,
                        actor_id=self.actor.unit_id,
                        target_id=target.unit_id,
                        payload={"amount": break_outcome.toughness_damage},
                    )
                if break_outcome.broken:
                    target.delay_action(0.25)
                    break_damage = target.take_damage(break_outcome.break_damage)
                    add_amount(damage_done, target, break_damage)
                    broken_targets.append(target.name)
                    state.events.emit(
                        EventType.WEAKNESS_BREAK,
                        actor_id=self.actor.unit_id,
                        target_id=target.unit_id,
                        payload={"break_damage": break_damage},
                    )
                    if target.is_defeated():
                        record_defeat(target)
                        continue

            for template in self.config.target_statuses:
                instance = target.apply_status(template, self.actor.unit_id)
                add_status(target, instance.name)
                state.events.emit(
                    EventType.STATUS_APPLY,
                    actor_id=self.actor.unit_id,
                    target_id=target.unit_id,
                    payload={"status": instance.name},
                )

            if target.is_defeated():
                record_defeat(target)

        if self.config.self_heal_multiplier > 0 or self.config.self_heal_flat > 0:
            heal_amount = calculate_healing(
                self.actor,
                self.actor,
                self.config.self_heal_multiplier,
                self.config.self_heal_flat,
            )
            actual_heal = self.actor.heal(heal_amount)
            add_amount(healing_done, self.actor, actual_heal)
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
            add_amount(shields_added, self.actor, actual_shield)
            state.events.emit(
                EventType.SHIELD_APPLIED,
                actor_id=self.actor.unit_id,
                target_id=self.actor.unit_id,
                payload={"amount": actual_shield},
            )

        for template in self.config.actor_statuses:
            instance = self.actor.apply_status(template, self.actor.unit_id)
            add_status(self.actor, instance.name)
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
            damage_done=list(damage_done.values()),
            shield_absorbed=list(shield_absorbed.values()),
            healing_done=list(healing_done.values()),
            shields_added=list(shields_added.values()),
            statuses_applied=list(statuses_applied.values()),
            toughness_damage_done=list(toughness_damage_done.values()),
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
