import os
from collections.abc import Sequence
from http import HTTPStatus
from pathlib import Path
from typing import Any, ClassVar

from sqlalchemy.ext.asyncio import AsyncSession

from srsim.role_api.core.exceptions import AppException
from srsim.role_api.db.models import (
    CharacterModel,
    PromotionModel,
    RankModel,
    SkillModel,
    SkillTreeModel,
)
from srsim.role_api.db.repositories import (
    CharacterRepository,
    PromotionRepository,
    RankRepository,
    SkillRepository,
    SkillTreeRepository,
)
from srsim.role_api.models.base import ResponseBaseModel
from srsim.role_api.models.role_data import (
    CharacterBaseInfo,
    CharacterPromotion,
    CharacterRank,
    CharacterSkill,
    CharacterSkillTree,
)


class RoleDataLoader:
    _ENV_DATA_ROOT: ClassVar[str] = "SRSIM_ROLE_DATA_ROOT"
    _CHARACTERS_FILE: ClassVar[str] = "characters.json"

    def __init__(self, *, data_root: Path | None = None) -> None:
        default_data_root = Path(__file__).resolve().parents[4] / "index_new"
        env_data_root = os.getenv(self._ENV_DATA_ROOT)
        resolved_data_root = (
            Path(env_data_root).expanduser() if env_data_root is not None else default_data_root
        )
        self._data_root: Path = data_root or resolved_data_root

    @property
    def data_root(self) -> Path:
        return self._data_root

    def supported_languages(self) -> list[str]:
        if not self._data_root.is_dir():
            return []
        return sorted(
            path.name
            for path in self._data_root.iterdir()
            if path.is_dir() and (path / self._CHARACTERS_FILE).is_file()
        )

    async def list_characters(
        self,
        session: AsyncSession,
        language: str,
        offset: int = 0,
        limit: int = 20,
    ) -> list[ResponseBaseModel]:
        self._validate_pagination(offset=offset, limit=limit)
        repo = CharacterRepository(session)
        models = await repo.list_all(language=language, offset=offset, limit=limit)
        return [self._character_model_to_pydantic(m) for m in models]

    async def get_character(
        self,
        session: AsyncSession,
        language: str,
        role_id: str,
    ) -> ResponseBaseModel:
        repo = CharacterRepository(session)
        model = await repo.get_by_id(role_id, language)
        if model is None:
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40402,
                message=f"role not found: {role_id}",
            )
        return self._character_model_to_pydantic(model)

    async def get_skills_by_ids(
        self,
        session: AsyncSession,
        language: str,
        ids: Sequence[str],
    ) -> list[ResponseBaseModel]:
        if not ids:
            return []
        repo = SkillRepository(session)
        models = await repo.get_by_ids(list(ids), language)

        found_ids = {m.id for m in models}
        missing_ids = [i for i in ids if i not in found_ids]
        if missing_ids:
            preview = ", ".join(missing_ids[:5])
            suffix = "" if len(missing_ids) <= 5 else ", ..."
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40403,
                message=f"skills not found: {preview}{suffix}",
            )

        return [self._skill_model_to_pydantic(m) for m in models]

    async def get_ranks_by_ids(
        self,
        session: AsyncSession,
        language: str,
        ids: Sequence[str],
    ) -> list[ResponseBaseModel]:
        if not ids:
            return []
        repo = RankRepository(session)
        models = await repo.get_by_ids(list(ids), language)

        found_ids = {m.id for m in models}
        missing_ids = [i for i in ids if i not in found_ids]
        if missing_ids:
            preview = ", ".join(missing_ids[:5])
            suffix = "" if len(missing_ids) <= 5 else ", ..."
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40403,
                message=f"ranks not found: {preview}{suffix}",
            )

        return [self._rank_model_to_pydantic(m) for m in models]

    async def get_skill_trees_by_ids(
        self,
        session: AsyncSession,
        language: str,
        ids: Sequence[str],
    ) -> list[ResponseBaseModel]:
        if not ids:
            return []
        repo = SkillTreeRepository(session)
        models = await repo.get_by_ids(list(ids), language)

        found_ids = {m.id for m in models}
        missing_ids = [i for i in ids if i not in found_ids]
        if missing_ids:
            preview = ", ".join(missing_ids[:5])
            suffix = "" if len(missing_ids) <= 5 else ", ..."
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40403,
                message=f"skill trees not found: {preview}{suffix}",
            )

        return [self._skill_tree_model_to_pydantic(m) for m in models]

    async def get_promotion(
        self,
        session: AsyncSession,
        language: str,
        role_id: str,
    ) -> ResponseBaseModel:
        repo = PromotionRepository(session)
        model = await repo.get_by_id(role_id, language)
        if model is None:
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40403,
                message=f"promotion not found: {role_id}",
            )
        return self._promotion_model_to_pydantic(model)

    async def count_characters(self, session: AsyncSession, language: str) -> int:
        repo = CharacterRepository(session)
        return await repo.count(language)

    @staticmethod
    def _character_model_to_pydantic(model: CharacterModel) -> CharacterBaseInfo:
        return CharacterBaseInfo(
            id=model.id,
            name=model.name,
            tag=model.tag,
            rarity=model.rarity,
            path=model.path,
            element=model.element,
            max_sp=model.max_sp,
            ranks=model.get_ranks(),
            skills=model.get_skills(),
            skill_trees=model.get_skill_trees(),
            icon=model.icon,
            preview=model.preview,
            portrait=model.portrait,
        )

    @staticmethod
    def _skill_model_to_pydantic(model: SkillModel) -> CharacterSkill:
        return CharacterSkill(
            id=model.id,
            name=model.name,
            max_level=model.max_level,
            element=model.element,
            type=model.type,
            type_text=model.type_text,
            effect=model.effect,
            effect_text=model.effect_text,
            simple_desc=model.simple_desc,
            desc=model.desc,
            params=model.get_params(),
            icon=model.icon,
        )

    @staticmethod
    def _rank_model_to_pydantic(model: RankModel) -> CharacterRank:
        return CharacterRank(
            id=model.id,
            name=model.name,
            rank=model.rank,
            desc=model.desc,
            materials=model.get_materials(),
            icon=model.icon,
            level_up_skills=model.get_level_up_skills(),
        )

    @staticmethod
    def _skill_tree_model_to_pydantic(model: SkillTreeModel) -> CharacterSkillTree:
        return CharacterSkillTree(
            id=model.id,
            name=model.name,
            max_level=model.max_level,
            desc=model.desc,
            params=model.get_params(),
            anchor=model.anchor,
            pre_points=model.get_pre_points(),
            level_up_skills=model.get_level_up_skills(),
            levels=model.get_levels(),
            icon=model.icon,
        )

    @staticmethod
    def _promotion_model_to_pydantic(model: PromotionModel) -> CharacterPromotion:
        return CharacterPromotion(
            id=model.id,
            values=model.get_values(),
            materials=model.get_materials(),
        )

    @staticmethod
    def _validate_pagination(*, offset: int, limit: int) -> None:
        if offset < 0 or limit <= 0:
            raise AppException(
                status_code=HTTPStatus.BAD_REQUEST,
                code=40001,
                message="offset must be >= 0 and limit must be > 0",
            )

    def _convert_model_data(self, model: ResponseBaseModel) -> dict[str, Any]:
        return model.model_dump()
