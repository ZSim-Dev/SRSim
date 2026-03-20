from dataclasses import dataclass, field

from .elements import Element, calculate_break_damage


@dataclass
class BreakOutcome:
    toughness_damage: int = 0
    break_damage: int = 0
    broken: bool = False


@dataclass
class ToughnessState:
    max_toughness: int
    weaknesses: frozenset[Element] = field(default_factory=frozenset)
    current_toughness: int = 0
    broken: bool = False
    broken_by: Element | None = None

    def __post_init__(self) -> None:
        if self.current_toughness == 0:
            self.current_toughness = self.max_toughness

    def apply(self, amount: int, element: Element, attacker_level: int) -> BreakOutcome:
        if self.broken or amount <= 0 or element not in self.weaknesses:
            return BreakOutcome()

        actual_damage = min(self.current_toughness, amount)
        self.current_toughness -= actual_damage
        if self.current_toughness > 0:
            return BreakOutcome(toughness_damage=actual_damage)

        self.broken = True
        self.broken_by = element
        return BreakOutcome(
            toughness_damage=actual_damage,
            break_damage=calculate_break_damage(element, attacker_level, self.max_toughness),
            broken=True,
        )

    def restore(self) -> None:
        self.current_toughness = self.max_toughness
        self.broken = False
        self.broken_by = None
