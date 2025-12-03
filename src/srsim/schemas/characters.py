from decimal import Decimal
from typing import Annotated

from pydantic import Field

from srsim.enums.elements import ElementEnum
from srsim.enums.path import PathTypeEnum

from .base import GameDataModel


class Eidolon(GameDataModel):
    id: str
    name: str
    effect: str


class Character(GameDataModel):
    id: str
    name: str
    element_type: ElementEnum
    element_type_text: str
    path_type: PathTypeEnum
    path_type_text: str
    eidolons: list[Eidolon]
    skills: SkillMap[CharacterSkill]


class CharacterSkillLevel(GameDataModel):
    effect_values: list[Decimal]


class CharacterSkill(GameDataModel):
    id: str
    name: str
    trigger_key: str
    tag_type: str
    tag_type_text: str
    skill_type_text: str
    max_level: int
    effect_raw: str
    abridged_effect: str
    element_type: str
    levels: dict[str, CharacterSkillLevel]


class SkillMap[T](GameDataModel):
    basic_atk: Annotated[T | None, Field(description="普攻")] = None
    enhanced_basic_atk: Annotated[T | None, Field(description="强化普攻")] = None
    skill: Annotated[T | None, Field(description="战技")] = None
    enhanced_skill: Annotated[T | None, Field(description="强化战技")] = None
    ultimate: Annotated[T | None, Field(description="终结技")] = None
    enhanced_ultimate: Annotated[T | None, Field(description="强化终结技")] = None
    talent: Annotated[T | None, Field(description="天赋")] = None
    technique: Annotated[T | None, Field(description="秘技")] = None
