from ..enums.path import PathTypeEnum
from .base import GameDataModel


class LightConeSuperimposition(GameDataModel):
    effect: str
    params: list[float]


class LightCone(GameDataModel):
    id: str
    name: str
    path_type: PathTypeEnum
    path_type_text: str
    effect_name: str
    effect_template: str
    superimpositions: list[LightConeSuperimposition]
