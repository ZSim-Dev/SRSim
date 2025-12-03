from ..enums.elements import ElementEnum
from .base import GameDataModel


class Element(GameDataModel):
    id: ElementEnum
    name: str
    description: str
    color: str
