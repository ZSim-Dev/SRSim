from sqlalchemy.ext.asyncio import AsyncSession

from srsim.role_api.db.models import SkillModel
from srsim.role_api.db.repositories.base import BaseRepository


class SkillRepository(BaseRepository[SkillModel]):
    _model = SkillModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
