from sqlalchemy.ext.asyncio import AsyncSession

from srsim.role_api.db.models import SkillTreeModel
from srsim.role_api.db.repositories.base import BaseRepository


class SkillTreeRepository(BaseRepository[SkillTreeModel]):
    _model = SkillTreeModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
