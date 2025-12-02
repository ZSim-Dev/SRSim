from dataclasses import dataclass
from math import floor

from .unit import Unit


@dataclass
class DamageContext:
    attacker: Unit
    defender: Unit
    multiplier: float


def calculate_damage(context: DamageContext) -> int:
    attacker_stats = context.attacker.snapshot_stats()
    defender_stats = context.defender.snapshot_stats()

    base = attacker_stats.atk * context.multiplier
    # Simple defense mitigation; placeholder for full formula.
    mitigation = defender_stats.defense * 0.3
    dmg = max(0.0, base - mitigation)
    return int(floor(dmg))
