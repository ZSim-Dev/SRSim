from dataclasses import dataclass, field

from .abilities import UnitKit
from .elements import Element
from .enums import Faction
from .stats import Stats
from .statuses import StatusEffect, StatusInstance, StatusTemplate, TickTiming
from .toughness import ToughnessState


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
    element: Element = Element.PHYSICAL
    base_resistance: float = 0.0
    toughness: ToughnessState | None = None
    hp: int = field(init=False)
    energy: int = field(init=False)
    shield: int = field(init=False)
    statuses: list[StatusInstance] = field(default_factory=list)
    current_speed: int = field(init=False)
    base_action_value: int = field(init=False)
    current_action_value: int = field(init=False)

    def __post_init__(self) -> None:
        self.hp = self.base_stats.max_hp
        self.energy = 0
        self.shield = 0
        self.current_speed = self.base_stats.spd
        self.base_action_value = action_value_from_spd(self.current_speed)
        self.current_action_value = self.base_action_value

    def is_defeated(self) -> bool:
        return self.hp <= 0

    def reset_action_value(self, advance_ratio: float = 0.0, delay_ratio: float = 0.0) -> None:
        offset = self.base_action_value * (delay_ratio - advance_ratio)
        self.current_action_value = max(0, int(self.base_action_value + offset))

    def take_damage(self, amount: int) -> int:
        damage = max(0, amount)
        if self.shield > 0 and damage > 0:
            absorbed = min(self.shield, damage)
            self.shield -= absorbed
            damage -= absorbed
        self.hp = max(0, self.hp - damage)
        return damage

    def heal(self, amount: int) -> int:
        healed = min(self.base_stats.max_hp - self.hp, max(0, amount))
        self.hp += healed
        return healed

    def gain_energy(self, amount: int) -> int:
        requested_gain = max(0, amount)
        previous_energy = self.energy
        self.energy = min(self.base_stats.max_energy, self.energy + requested_gain)
        return self.energy - previous_energy

    def spend_energy(self, amount: int) -> None:
        if amount > self.energy:
            raise ValueError(f"{self.name} lacks energy: {self.energy} < {amount}")
        self.energy -= amount

    def energy_full(self) -> bool:
        return self.energy >= self.base_stats.max_energy

    def snapshot_stats(self) -> Stats:
        effects = self.active_effects()
        return Stats(
            max_hp=self.base_stats.max_hp,
            atk=max(1, int(round(self.base_stats.atk * (1.0 + effects.atk_pct)))),
            defense=max(0, int(round(self.base_stats.defense * (1.0 + effects.defense_pct)))),
            spd=max(1, int(round(self.base_stats.spd * (1.0 + effects.spd_pct)))),
            max_energy=self.base_stats.max_energy,
        )

    def speed_tick(self, delta: int) -> None:
        self.current_action_value = max(0, self.current_action_value - delta)

    def apply_shield(self, amount: int) -> int:
        shield_amount = max(0, amount)
        self.shield += shield_amount
        return shield_amount

    def apply_status(self, template: StatusTemplate, source_unit_id: str) -> StatusInstance:
        for status in self.statuses:
            if status.name == template.name:
                status.remaining_turns = template.duration
                self.refresh_speed_from_statuses()
                return status

        instance = StatusInstance.from_template(
            template,
            source_unit_id=source_unit_id,
            owner_unit_id=self.unit_id,
        )
        self.statuses.append(instance)
        self.refresh_speed_from_statuses()
        return instance

    def tick_statuses(self, timing: TickTiming) -> list[str]:
        expired: list[str] = []
        remaining: list[StatusInstance] = []
        for status in self.statuses:
            if status.should_tick(timing) and status.tick():
                expired.append(status.name)
                continue
            remaining.append(status)
        self.statuses = remaining
        self.refresh_speed_from_statuses()
        return expired

    def refresh_speed_from_statuses(self) -> None:
        new_speed = self.snapshot_stats().spd
        if new_speed == self.current_speed:
            return
        self.current_action_value = max(
            0,
            int(self.current_action_value * self.current_speed / new_speed),
        )
        self.current_speed = new_speed
        self.base_action_value = action_value_from_spd(new_speed)

    def active_effects(self) -> StatusEffect:
        effect = StatusEffect()
        for status in self.statuses:
            item = status.effect
            effect = StatusEffect(
                atk_pct=effect.atk_pct + item.atk_pct,
                defense_pct=effect.defense_pct + item.defense_pct,
                spd_pct=effect.spd_pct + item.spd_pct,
                dmg_boost=effect.dmg_boost + item.dmg_boost,
                weaken=effect.weaken + item.weaken,
                vulnerability=effect.vulnerability + item.vulnerability,
                mitigation=effect.mitigation + item.mitigation,
                res_pen=effect.res_pen + item.res_pen,
                defense_reduction=effect.defense_reduction + item.defense_reduction,
                crit_rate=effect.crit_rate + item.crit_rate,
                crit_dmg=effect.crit_dmg + item.crit_dmg,
                outgoing_healing_boost=(
                    effect.outgoing_healing_boost + item.outgoing_healing_boost
                ),
                incoming_healing_boost=(
                    effect.incoming_healing_boost + item.incoming_healing_boost
                ),
                incoming_healing_reduction=(
                    effect.incoming_healing_reduction + item.incoming_healing_reduction
                ),
                shield_bonus=effect.shield_bonus + item.shield_bonus,
                cannot_act=effect.cannot_act or item.cannot_act,
            )
        return effect

    def can_act(self) -> bool:
        return not self.active_effects().cannot_act

    def damage_boost(self) -> float:
        return self.active_effects().dmg_boost

    def weaken(self) -> float:
        return self.active_effects().weaken

    def vulnerability(self) -> float:
        return self.active_effects().vulnerability

    def damage_mitigation(self) -> float:
        remaining_ratio = 1.0
        for status in self.statuses:
            remaining_ratio *= 1.0 - status.effect.mitigation
        return 1.0 - max(0.0, remaining_ratio)

    def defense_reduction(self) -> float:
        return self.active_effects().defense_reduction

    def res_pen(self) -> float:
        return self.active_effects().res_pen

    def crit_rate(self) -> float:
        return self.active_effects().crit_rate

    def crit_dmg(self) -> float:
        return 0.5 + self.active_effects().crit_dmg

    def outgoing_healing_boost(self) -> float:
        return self.active_effects().outgoing_healing_boost

    def incoming_healing_boost(self) -> float:
        return self.active_effects().incoming_healing_boost

    def incoming_healing_reduction(self) -> float:
        return self.active_effects().incoming_healing_reduction

    def shield_bonus(self) -> float:
        return self.active_effects().shield_bonus

    def resistance_for(self, _: Element) -> float:
        return self.base_resistance

    def __repr__(self) -> str:
        return (
            f"{self.name}(HP={self.hp}, SH={self.shield}, EN={self.energy}, "
            f"AV={self.current_action_value})"
        )
