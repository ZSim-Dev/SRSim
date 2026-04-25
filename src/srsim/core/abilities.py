from dataclasses import dataclass

from .elements import Element
from .enums import ActionType
from .statuses import StatusTemplate


@dataclass
class ActionConfig:
    name: str
    multiplier: float
    element: Element | None = None
    toughness_damage: int = 0
    sp_cost: int = 0
    sp_gain: int = 0
    energy_cost: int = 0
    energy_gain: int = 0
    self_heal_multiplier: float = 0.0
    self_heal_flat: int = 0
    self_shield_multiplier: float = 0.0
    self_shield_flat: int = 0
    actor_statuses: tuple[StatusTemplate, ...] = ()
    target_statuses: tuple[StatusTemplate, ...] = ()
    action_type: ActionType = ActionType.BASIC


@dataclass
class UnitKit:
    basic: ActionConfig
    skill: ActionConfig
    ultimate: ActionConfig
