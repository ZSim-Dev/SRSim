from sqlalchemy.ext.asyncio import AsyncSession

from srsim.role_api.db.models import PromotionModel
from srsim.role_api.db.repositories.base import BaseRepository


class PromotionRepository(BaseRepository[PromotionModel]):
    _model = PromotionModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
