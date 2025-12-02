from dataclasses import dataclass
from typing import Callable

from .enums import ActionType


@dataclass
class ActionConfig:
    name: str
    multiplier: float
    sp_cost: int = 0
    sp_gain: int = 0
    energy_cost: int = 0
    energy_gain: int = 0
    action_type: ActionType = ActionType.BASIC
    target_selector: Callable[..., int] | None = None


@dataclass
class UnitKit:
    basic: ActionConfig
    skill: ActionConfig
    ultimate: ActionConfig
