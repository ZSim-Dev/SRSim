import json
import os
from http import HTTPStatus
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from srsim.role_api.core.exceptions import AppException
from srsim.role_api.db.repositories import (
    CharacterRepository,
    PromotionRepository,
    RankRepository,
    SkillRepository,
    SkillTreeRepository,
)

_ENV_DATA_ROOT = "SRSIM_ROLE_DATA_ROOT"

_CHARACTERS_FILE = "characters.json"
_SKILLS_FILE = "character_skills.json"
_RANKS_FILE = "character_ranks.json"
_SKILL_TREES_FILE = "character_skill_trees.json"
_PROMOTIONS_FILE = "character_promotions.json"


class DbRebuildService:
    def __init__(self, session: AsyncSession, data_root: Path | None = None) -> None:
        self._session = session
        if data_root is None:
            env_data_root = os.getenv(_ENV_DATA_ROOT)
            if env_data_root is not None:
                data_root = Path(env_data_root).expanduser()
            else:
                project_root = Path(__file__).resolve().parents[4]
                data_root = project_root / "index_new"
        self._data_root = data_root

        self._character_repo = CharacterRepository(session)
        self._skill_repo = SkillRepository(session)
        self._rank_repo = RankRepository(session)
        self._skill_tree_repo = SkillTreeRepository(session)
        self._promotion_repo = PromotionRepository(session)

    def supported_languages(self) -> list[str]:
        if not self._data_root.is_dir():
            return []
        return sorted(
            path.name
            for path in self._data_root.iterdir()
            if path.is_dir() and (path / _CHARACTERS_FILE).is_file()
        )

    async def rebuild_all(self) -> dict[str, Any]:
        languages = self.supported_languages()
        if not languages:
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50010,
                message="No data found to rebuild",
            )

        results: dict[str, Any] = {"languages": {}, "total": 0}
        for language in languages:
            lang_result = await self.rebuild_language(language)
            results["languages"][language] = lang_result
            results["total"] += lang_result.get("total", 0)

        return results

    async def rebuild_language(self, language: str) -> dict[str, Any]:
        language_path = self._data_root / language
        if not language_path.is_dir() or not (language_path / _CHARACTERS_FILE).is_file():
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40401,
                message=f"unsupported language: {language}",
            )

        await self._character_repo.delete_by_language(language)
        await self._skill_repo.delete_by_language(language)
        await self._rank_repo.delete_by_language(language)
        await self._skill_tree_repo.delete_by_language(language)
        await self._promotion_repo.delete_by_language(language)

        characters = self._load_json(language_path / _CHARACTERS_FILE)
        skills = self._load_json(language_path / _SKILLS_FILE)
        ranks = self._load_json(language_path / _RANKS_FILE)
        skill_trees = self._load_json(language_path / _SKILL_TREES_FILE)
        promotions = self._load_json(language_path / _PROMOTIONS_FILE)

        counts = {
            "characters": 0,
            "skills": 0,
            "ranks": 0,
            "skill_trees": 0,
            "promotions": 0,
        }

        for char_id, char_data in characters.items():
            await self._character_repo.create(
                id=char_id,
                language=language,
                name=char_data.get("name", ""),
                tag=char_data.get("tag", ""),
                rarity=char_data.get("rarity", 0),
                path=char_data.get("path", ""),
                element=char_data.get("element", ""),
                max_sp=char_data.get("max_sp"),
                ranks=json.dumps(char_data.get("ranks", [])),
                skills=json.dumps(char_data.get("skills", [])),
                skill_trees=json.dumps(char_data.get("skill_trees", [])),
                icon=char_data.get("icon", ""),
                preview=char_data.get("preview", ""),
                portrait=char_data.get("portrait", ""),
            )
            counts["characters"] += 1

        for skill_id, skill_data in skills.items():
            await self._skill_repo.create(
                id=skill_id,
                language=language,
                name=skill_data.get("name", ""),
                max_level=skill_data.get("max_level", 1),
                element=skill_data.get("element", ""),
                type=skill_data.get("type", ""),
                type_text=skill_data.get("type_text", ""),
                effect=skill_data.get("effect", ""),
                effect_text=skill_data.get("effect_text", ""),
                simple_desc=skill_data.get("simple_desc", ""),
                desc=skill_data.get("desc", ""),
                params=json.dumps(skill_data.get("params", [])),
                icon=skill_data.get("icon"),
            )
            counts["skills"] += 1

        for rank_id, rank_data in ranks.items():
            await self._rank_repo.create(
                id=rank_id,
                language=language,
                name=rank_data.get("name", ""),
                rank=rank_data.get("rank", 0),
                desc=rank_data.get("desc", ""),
                materials=json.dumps(rank_data.get("materials", [])),
                icon=rank_data.get("icon", ""),
                level_up_skills=json.dumps(rank_data.get("level_up_skills", [])),
            )
            counts["ranks"] += 1

        for tree_id, tree_data in skill_trees.items():
            await self._skill_tree_repo.create(
                id=tree_id,
                language=language,
                name=tree_data.get("name", ""),
                max_level=tree_data.get("max_level", 1),
                desc=tree_data.get("desc", ""),
                params=json.dumps(tree_data.get("params", [])),
                anchor=tree_data.get("anchor", ""),
                pre_points=json.dumps(tree_data.get("pre_points", [])),
                level_up_skills=json.dumps(tree_data.get("level_up_skills", [])),
                levels=json.dumps(tree_data.get("levels", [])),
                icon=tree_data.get("icon", ""),
            )
            counts["skill_trees"] += 1

        for promo_id, promo_data in promotions.items():
            await self._promotion_repo.create(
                id=promo_id,
                language=language,
                values=json.dumps(promo_data.get("values", [])),
                materials=json.dumps(promo_data.get("materials", [])),
            )
            counts["promotions"] += 1

        counts["total"] = sum(counts.values()) - 1
        return counts

    def _load_json(self, file_path: Path) -> dict[str, Any]:
        if not file_path.is_file():
            return {}
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50011,
                message=f"invalid data payload: {file_path.name}",
            )
        return data
