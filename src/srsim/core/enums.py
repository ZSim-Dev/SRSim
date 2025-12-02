from enum import Enum


class Faction(Enum):
    ALLY = "ally"
    ENEMY = "enemy"


class ActionType(Enum):
    BASIC = "basic"
    SKILL = "skill"
    ULTIMATE = "ultimate"
    FOLLOW_UP = "follow_up"
