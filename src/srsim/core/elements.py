from enum import Enum


class Element(Enum):
    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    WIND = "wind"
    QUANTUM = "quantum"
    IMAGINARY = "imaginary"


_BREAK_DAMAGE_MULTIPLIER: dict[Element, float] = {
    Element.PHYSICAL: 1.0,
    Element.FIRE: 1.2,
    Element.ICE: 1.0,
    Element.LIGHTNING: 1.1,
    Element.WIND: 1.0,
    Element.QUANTUM: 1.3,
    Element.IMAGINARY: 1.2,
}


def calculate_break_damage(element: Element, attacker_level: int, max_toughness: int) -> int:
    multiplier = _BREAK_DAMAGE_MULTIPLIER[element]
    return max(1, int((attacker_level + 20) * max_toughness * multiplier / 20))
