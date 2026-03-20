from dataclasses import dataclass, field
from enum import Enum


class StatusKind(Enum):
    BUFF = "buff"
    DEBUFF = "debuff"
    CONTROL = "control"


class TickTiming(Enum):
    OWNER_TURN_START = "owner_turn_start"
    OWNER_TURN_END = "owner_turn_end"


@dataclass(frozen=True)
class StatusEffect:
    atk_pct: float = 0.0
    defense_pct: float = 0.0
    spd_pct: float = 0.0
    dmg_boost: float = 0.0
    weaken: float = 0.0
    vulnerability: float = 0.0
    mitigation: float = 0.0
    res_pen: float = 0.0
    defense_reduction: float = 0.0
    crit_rate: float = 0.0
    crit_dmg: float = 0.0
    outgoing_healing_boost: float = 0.0
    incoming_healing_boost: float = 0.0
    incoming_healing_reduction: float = 0.0
    shield_bonus: float = 0.0
    cannot_act: bool = False


@dataclass(frozen=True)
class StatusTemplate:
    name: str
    kind: StatusKind
    duration: int
    tick_timing: TickTiming
    effect: StatusEffect = field(default_factory=StatusEffect)
    dispellable: bool = True
    removable_by_cleanse: bool = True


@dataclass
class StatusInstance:
    template: StatusTemplate
    source_unit_id: str
    owner_unit_id: str
    remaining_turns: int

    @classmethod
    def from_template(
        cls,
        template: StatusTemplate,
        *,
        source_unit_id: str,
        owner_unit_id: str,
    ) -> "StatusInstance":
        return cls(
            template=template,
            source_unit_id=source_unit_id,
            owner_unit_id=owner_unit_id,
            remaining_turns=template.duration,
        )

    @property
    def name(self) -> str:
        return self.template.name

    @property
    def effect(self) -> StatusEffect:
        return self.template.effect

    def should_tick(self, timing: TickTiming) -> bool:
        return self.template.tick_timing == timing and self.remaining_turns > 0

    def tick(self) -> bool:
        self.remaining_turns -= 1
        return self.remaining_turns <= 0
