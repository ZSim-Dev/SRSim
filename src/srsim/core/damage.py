from dataclasses import dataclass
from math import floor

from .unit import Unit


@dataclass
class DamageContext:
    attacker: Unit
    defender: Unit
    multiplier: float
    flat_damage: float = 0.0
    can_crit: bool = True
    force_crit: bool = False


def calculate_damage(context: DamageContext) -> int:
    attacker_stats = context.attacker.snapshot_stats()
    defender_stats = context.defender.snapshot_stats()

    base_damage = attacker_stats.atk * context.multiplier + context.flat_damage
    crit_multiplier = _calc_crit_multiplier(context, attacker_stats.crit_rate, attacker_stats.crit_dmg)
    dmg_boost_multiplier = 1.0 + max(0.0, attacker_stats.dmg_boost)
    weaken_multiplier = 1.0 - _clamp(context.attacker.modifiers.weaken, 0.0, 1.0)
    defense_multiplier = _calc_def_multiplier(context)
    resistance_multiplier = _calc_res_multiplier(context, defender_stats.resistance)
    vulnerability_multiplier = 1.0 + max(0.0, context.defender.modifiers.vulnerability)
    mitigation_multiplier = 1.0 - _clamp(context.defender.modifiers.mitigation, 0.0, 1.0)
    broken_multiplier = 1.0 if context.defender.is_broken() else 0.9

    damage = (
        base_damage
        * crit_multiplier
        * dmg_boost_multiplier
        * weaken_multiplier
        * defense_multiplier
        * resistance_multiplier
        * vulnerability_multiplier
        * mitigation_multiplier
        * broken_multiplier
    )
    return int(floor(max(0.0, damage)))


def _calc_crit_multiplier(
    context: DamageContext,
    crit_rate: float,
    crit_dmg: float,
) -> float:
    if not context.can_crit:
        return 1.0
    if context.force_crit or crit_rate >= 1.0:
        return 1.0 + crit_dmg
    return 1.0


def _calc_def_multiplier(context: DamageContext) -> float:
    attacker_level = context.attacker.level
    defender_level = context.defender.level
    effective_def_modifier = max(
        0.0,
        1.0
        + context.defender.modifiers.defense_bonus
        - context.defender.modifiers.defense_reduction
        - context.attacker.modifiers.defense_ignore,
    )
    numerator = attacker_level + 20
    denominator = (defender_level + 20) * effective_def_modifier + attacker_level + 20
    return numerator / denominator


def _calc_res_multiplier(context: DamageContext, target_resistance: float) -> float:
    effective_res = _clamp(target_resistance - context.attacker.modifiers.res_pen, -1.0, 0.9)
    return 1.0 - effective_res


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))
