from typing import Any, ClassVar, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from srsim.role_api.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    _model: ClassVar[type[Base]]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, item_id: str, language: str) -> ModelType | None:
        stmt = select(self._model).where(
            self._model.id == item_id,
            self._model.language == language,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, ids: list[str], language: str) -> list[ModelType]:
        if not ids:
            return []
        stmt = select(self._model).where(
            self._model.id.in_(ids),
            self._model.language == language,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self, language: str, offset: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = (
            select(self._model).where(self._model.language == language).offset(offset).limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, language: str) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self._model).where(self._model.language == language)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def create(self, **kwargs: Any) -> ModelType:
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def delete_by_language(self, language: str) -> int:
        from sqlalchemy import delete

        stmt = delete(self._model).where(self._model.language == language)
        result = await self._session.execute(stmt)
        return result.rowcount
