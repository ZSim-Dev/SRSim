from ..enums.path import PathTypeEnum
from .base import GameDataModel


class Path(GameDataModel):
    id: PathTypeEnum
    name: str
    description: str
