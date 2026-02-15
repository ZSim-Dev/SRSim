from enum import StrEnum
from typing import Annotated

from pydantic import Field

from srsim.role_api.models.base import RequestModel, ResponseBaseModel


class RolePath(StrEnum):
    Warrior = "Warrior"
    Rogue = "Rogue"
    Mage = "Mage"
    Shaman = "Shaman"
    Warlock = "Warlock"
    Knight = "Knight"
    Priest = "Priest"
    Memory = "Memory"
    Elation = "Elation"


class RoleElement(StrEnum):
    Physical = "Physical"
    Fire = "Fire"
    Ice = "Ice"
    Thunder = "Thunder"
    Wind = "Wind"
    Quantum = "Quantum"
    Imaginary = "Imaginary"


class SkillLevelUpItem(ResponseBaseModel):
    id: str
    num: int


class PromotionValueItem(ResponseBaseModel):
    base: int | float
    step: int | float


class RoleBasicData(ResponseBaseModel):
    id: str
    name: str
    tag: str
    rarity: int
    path: str
    element: str
    max_sp: int | None
    ranks: list[str]
    skills: list[str]
    skill_trees: list[str]
    icon: str
    preview: str
    portrait: str


class RoleSkillData(ResponseBaseModel):
    id: str
    name: str
    max_level: int
    element: str
    type: str
    type_text: str
    effect: str
    effect_text: str
    simple_desc: str
    desc: str
    params: list[list[int | float]]
    icon: str | None


class RoleRankData(ResponseBaseModel):
    id: str
    name: str
    rank: int
    desc: str
    materials: list[SkillLevelUpItem]
    icon: str
    level_up_skills: list[SkillLevelUpItem]


class RoleSkillTreeLevelInfo(ResponseBaseModel):
    promotion: int
    level: int
    properties: list[dict[str, object]]
    materials: list[SkillLevelUpItem]


class RoleSkillTreeData(ResponseBaseModel):
    id: str
    name: str
    max_level: int
    desc: str
    params: list[list[int | float]]
    anchor: str
    pre_points: list[str]
    level_up_skills: list[SkillLevelUpItem]
    levels: list[RoleSkillTreeLevelInfo]
    icon: str


class RoleListItem(ResponseBaseModel):
    id: str
    name: str
    tag: str
    rarity: int
    path: str
    element: str
    max_sp: int | None
    icon: str
    preview: str
    portrait: str


class RoleListData(ResponseBaseModel):
    items: list[RoleListItem]
    total: int
    offset: int
    limit: int


class RoleSearchRequest(RequestModel):
    path: RolePath | None = None
    element: RoleElement | None = None
    name: Annotated[str, Field(min_length=1)] | None = None


class RoleDetailData(ResponseBaseModel):
    basic: RoleBasicData
    skills: list[RoleSkillData]
    ranks: list[RoleRankData]
    skill_trees: list[RoleSkillTreeData]


class RoleSkillsData(ResponseBaseModel):
    role_id: str
    skills: list[RoleSkillData]


class SkillDescriptionRender(ResponseBaseModel):
    plain_text: str
    rich_text: str


class RoleSkillDescriptionData(ResponseBaseModel):
    role_id: str
    skill_id: str
    skill_level: int
    name: str
    desc: SkillDescriptionRender
    simple_desc: SkillDescriptionRender


class RoleRanksData(ResponseBaseModel):
    role_id: str
    ranks: list[RoleRankData]


class RolePromotionsData(ResponseBaseModel):
    role_id: str
    values: list[dict[str, PromotionValueItem]]
    materials: list[list[SkillLevelUpItem]]


class RolePanelData(ResponseBaseModel):
    role_id: str
    level: int
    promoted: bool | None
    promotion: int
    stats: dict[str, int | float]
