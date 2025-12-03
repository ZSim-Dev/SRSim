from decimal import Decimal

from ..enums.elements import ElementEnum
from .base import GameDataModel


class EnemySkill(GameDataModel):
    id: str
    name: str
    skill_desc: str
    skill_type_desc: str
    element_type: ElementEnum


class Enemy(GameDataModel):
    id: str
    name: str
    elemental_weaknesses: list[ElementEnum]
    elemental_resistances: dict[ElementEnum, Decimal]
    skills: list[EnemySkill]
