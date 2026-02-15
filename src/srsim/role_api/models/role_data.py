from srsim.role_api.models.base import ResponseBaseModel


class SkillLevelUpItem(ResponseBaseModel):
    id: str
    num: int


class PromotionValueItem(ResponseBaseModel):
    base: int | float
    step: int | float


class CharacterBaseInfo(ResponseBaseModel):
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


class CharacterSkill(ResponseBaseModel):
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


class CharacterRank(ResponseBaseModel):
    id: str
    name: str
    rank: int
    desc: str
    materials: list[SkillLevelUpItem]
    icon: str
    level_up_skills: list[SkillLevelUpItem]


class SkillTreeLevelInfo(ResponseBaseModel):
    promotion: int
    level: int
    properties: list[dict[str, object]]
    materials: list[SkillLevelUpItem]


class CharacterSkillTree(ResponseBaseModel):
    id: str
    name: str
    max_level: int
    desc: str
    params: list[list[int | float]]
    anchor: str
    pre_points: list[str]
    level_up_skills: list[SkillLevelUpItem]
    levels: list[SkillTreeLevelInfo]
    icon: str


class CharacterPromotion(ResponseBaseModel):
    id: str
    values: list[dict[str, PromotionValueItem]]
    materials: list[list[SkillLevelUpItem]]
