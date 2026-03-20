from dataclasses import dataclass
from math import floor

from .elements import Element
from .unit import Unit


@dataclass
class DamageContext:
    attacker: Unit
    defender: Unit
    multiplier: float
    element: Element
    can_crit: bool = True
    flat_extra_damage: float = 0.0


def calculate_damage(context: DamageContext) -> int:
    attacker_stats = context.attacker.snapshot_stats()
    defender_stats = context.defender.snapshot_stats()

    base_damage = attacker_stats.atk * context.multiplier + context.flat_extra_damage
    crit_multiplier = 1.0
    if context.can_crit and context.attacker.crit_rate() >= 1.0:
        crit_multiplier = 1.0 + context.attacker.crit_dmg()

    dmg_boost_multiplier = 1.0 + context.attacker.damage_boost()
    weaken_multiplier = 1.0 - context.attacker.weaken()

    effective_def_modifier = max(
        0.0,
        1.0 + defender_stats.defense / 100.0 - context.attacker.defense_reduction(),
    )
    defense_multiplier = (context.attacker.level + 20) / (
        (context.defender.level + 20) * effective_def_modifier + context.attacker.level + 20
    )

    effective_resistance = min(
        0.9,
        max(-1.0, context.defender.resistance_for(context.element) - context.attacker.res_pen()),
    )
    resistance_multiplier = 1.0 - effective_resistance
    vulnerability_multiplier = 1.0 + context.defender.vulnerability()
    mitigation_multiplier = max(0.0, 1.0 - context.defender.damage_mitigation())

    broken_multiplier = 1.0
    if context.defender.toughness is not None:
        broken_multiplier = 1.0 if context.defender.toughness.broken else 0.9

    dmg = max(
        0.0,
        base_damage
        * crit_multiplier
        * dmg_boost_multiplier
        * weaken_multiplier
        * defense_multiplier
        * resistance_multiplier
        * vulnerability_multiplier
        * mitigation_multiplier
        * broken_multiplier,
    )
    return int(floor(dmg))


def calculate_healing(actor: Unit, target: Unit, ratio: float, flat_heal: int) -> int:
    actor_stats = actor.snapshot_stats()
    amount = actor_stats.atk * ratio + flat_heal
    multiplier = (
        1.0
        + actor.outgoing_healing_boost()
        + target.incoming_healing_boost()
        - target.incoming_healing_reduction()
    )
    return max(0, int(floor(amount * multiplier)))


def calculate_shield(actor: Unit, ratio: float, flat_shield: int) -> int:
    actor_stats = actor.snapshot_stats()
    amount = actor_stats.atk * ratio + flat_shield
    multiplier = 1.0 + actor.shield_bonus()
    return max(0, int(floor(amount * multiplier)))
