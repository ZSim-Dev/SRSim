import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Self

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from srsim.role_api.db.base import Base
from srsim.role_api.db.models import (  # noqa: F401 - Import to register models with Base
    CharacterModel,
    PromotionModel,
    RankModel,
    SkillModel,
    SkillTreeModel,
)

_ENV_DB_PATH = "SRSIM_ROLE_DB_PATH"


class DatabaseSessionManager:
    _engine: AsyncEngine | None = None
    _session_maker: async_sessionmaker[AsyncSession] | None = None

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is None:
            env_path = os.getenv(_ENV_DB_PATH)
            if env_path is not None:
                db_path = Path(env_path).expanduser()
            else:
                project_root = Path(__file__).resolve().parents[5]
                data_dir = project_root / "data"
                data_dir.mkdir(parents=True, exist_ok=True)
                db_path = data_dir / "role_api.db"

        self._db_path = db_path
        self._engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            echo=False,
        )
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    @classmethod
    def from_path(cls, db_path: Path) -> Self:
        return cls(db_path=db_path)

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("Database engine not initialized")
        return self._engine

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        if self._session_maker is None:
            raise RuntimeError("Session maker not initialized")
        return self._session_maker

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise RuntimeError("Session maker not initialized")
        session = self._session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


_session_manager: DatabaseSessionManager | None = None


def get_session_manager() -> DatabaseSessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = DatabaseSessionManager()
    return _session_manager


def set_session_manager(manager: DatabaseSessionManager) -> None:
    global _session_manager
    _session_manager = manager


async def get_db_session() -> AsyncIterator[AsyncSession]:
    manager = get_session_manager()
    async with manager.session() as session:
        yield session


get_db_session_dependency = Depends(get_db_session)
