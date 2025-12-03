from typing import Annotated, Literal

from pydantic import Field

from .base import GameDataModel


class RelicSetPiece(GameDataModel): ...


class InnerRelicEffect(GameDataModel):
    pieces2: Annotated[str, Field(description="2件套效果")]


class OuterRelicEffect(GameDataModel):
    pieces4: Annotated[str, Field(description="4件套效果")]


class InnerRelicSet(GameDataModel):
    id: str
    name: str
    is_planar_ornament: Literal[True] = True
    set_effects: InnerRelicEffect
    pieces: dict[str, RelicSetPiece]


class OuterRelicSet(GameDataModel):
    id: str
    name: str
    is_planar_ornament: Literal[False] = False
    set_effects: OuterRelicEffect
    pieces: dict[str, RelicSetPiece]


RelicSet = Annotated[InnerRelicSet | OuterRelicSet, Field(discriminator="is_planar_ornament")]


class RelicSetMap(GameDataModel):
    relic_sets: dict[str, RelicSet]
