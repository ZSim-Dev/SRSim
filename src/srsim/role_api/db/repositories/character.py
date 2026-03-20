from sqlalchemy.ext.asyncio import AsyncSession

from srsim.role_api.db.models import CharacterModel
from srsim.role_api.db.repositories.base import BaseRepository


class CharacterRepository(BaseRepository[CharacterModel]):
    _model = CharacterModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
