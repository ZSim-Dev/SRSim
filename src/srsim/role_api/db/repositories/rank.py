from sqlalchemy.ext.asyncio import AsyncSession

from srsim.role_api.db.models import RankModel
from srsim.role_api.db.repositories.base import BaseRepository


class RankRepository(BaseRepository[RankModel]):
    _model = RankModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
