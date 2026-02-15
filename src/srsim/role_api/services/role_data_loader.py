import json
import os
from collections.abc import Sequence
from http import HTTPStatus
from pathlib import Path
from typing import ClassVar, cast

from srsim.role_api.core.exceptions import AppException
from srsim.role_api.models.base import ResponseBaseModel
from srsim.role_api.models.role_data import (
    CharacterBaseInfo,
    CharacterPromotion,
    CharacterRank,
    CharacterSkill,
    CharacterSkillTree,
)


class RoleDataLoader:
    _CHARACTERS_FILE: ClassVar[str] = "characters.json"
    _SKILLS_FILE: ClassVar[str] = "character_skills.json"
    _RANKS_FILE: ClassVar[str] = "character_ranks.json"
    _SKILL_TREES_FILE: ClassVar[str] = "character_skill_trees.json"
    _PROMOTIONS_FILE: ClassVar[str] = "character_promotions.json"
    _ENV_DATA_ROOT: ClassVar[str] = "SRSIM_ROLE_DATA_ROOT"

    def __init__(self, *, data_root: Path | None = None) -> None:
        default_data_root = Path(__file__).resolve().parents[4] / "index_new"
        env_data_root = os.getenv(self._ENV_DATA_ROOT)
        resolved_data_root = (
            Path(env_data_root).expanduser() if env_data_root is not None else default_data_root
        )
        self._data_root: Path = data_root or resolved_data_root
        self._file_cache: dict[tuple[str, str], dict[str, ResponseBaseModel]] = {}

    def supported_languages(self) -> list[str]:
        if not self._data_root.is_dir():
            return []
        return sorted(
            path.name
            for path in self._data_root.iterdir()
            if path.is_dir() and (path / self._CHARACTERS_FILE).is_file()
        )

    def list_characters(
        self,
        language: str,
        offset: int = 0,
        limit: int = 20,
    ) -> list[ResponseBaseModel]:
        self._validate_pagination(offset=offset, limit=limit)
        characters = list(self._load_characters(language).values())
        return characters[offset : offset + limit]

    def get_character(self, language: str, role_id: str) -> ResponseBaseModel:
        character = self._load_characters(language).get(role_id)
        if character is None:
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40402,
                message=f"role not found: {role_id}",
            )
        return character

    def get_skills_by_ids(self, language: str, ids: Sequence[str]) -> list[ResponseBaseModel]:
        return self._collect_by_ids(
            resource_name="skills",
            ids=ids,
            resource_map=self._load_skills(language),
        )

    def get_ranks_by_ids(self, language: str, ids: Sequence[str]) -> list[ResponseBaseModel]:
        return self._collect_by_ids(
            resource_name="ranks",
            ids=ids,
            resource_map=self._load_ranks(language),
        )

    def get_skill_trees_by_ids(
        self,
        language: str,
        ids: Sequence[str],
    ) -> list[ResponseBaseModel]:
        return self._collect_by_ids(
            resource_name="skill trees",
            ids=ids,
            resource_map=self._load_skill_trees(language),
        )

    def get_promotion(self, language: str, role_id: str) -> ResponseBaseModel:
        promotion = self._load_promotions(language).get(role_id)
        if promotion is None:
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40403,
                message=f"promotion not found: {role_id}",
            )
        return promotion

    def _load_characters(self, language: str) -> dict[str, ResponseBaseModel]:
        return self._load_file_map(
            language=language,
            filename=self._CHARACTERS_FILE,
            model_class=CharacterBaseInfo,
        )

    def _load_skills(self, language: str) -> dict[str, ResponseBaseModel]:
        return self._load_file_map(
            language=language,
            filename=self._SKILLS_FILE,
            model_class=CharacterSkill,
        )

    def _load_ranks(self, language: str) -> dict[str, ResponseBaseModel]:
        return self._load_file_map(
            language=language,
            filename=self._RANKS_FILE,
            model_class=CharacterRank,
        )

    def _load_skill_trees(self, language: str) -> dict[str, ResponseBaseModel]:
        return self._load_file_map(
            language=language,
            filename=self._SKILL_TREES_FILE,
            model_class=CharacterSkillTree,
        )

    def _load_promotions(self, language: str) -> dict[str, ResponseBaseModel]:
        return self._load_file_map(
            language=language,
            filename=self._PROMOTIONS_FILE,
            model_class=CharacterPromotion,
        )

    def _language_path(self, language: str) -> Path:
        language_path = self._data_root / language
        if not language_path.is_dir() or not (language_path / self._CHARACTERS_FILE).is_file():
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40401,
                message=f"unsupported language: {language}",
            )
        return language_path

    def _load_file_map(
        self,
        *,
        language: str,
        filename: str,
        model_class: type[ResponseBaseModel],
    ) -> dict[str, ResponseBaseModel]:
        cache_key = (language, filename)
        cached = self._file_cache.get(cache_key)
        if cached is not None:
            return cached

        file_path = self._language_path(language) / filename
        if not file_path.is_file():
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50010,
                message=f"missing data file: {file_path.name}",
            )

        with file_path.open("r", encoding="utf-8") as file:
            payload = cast(object, json.load(file))

        if not isinstance(payload, dict):
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50011,
                message=f"invalid data payload: {file_path.name}",
            )

        payload_map = cast(dict[object, object], payload)
        model_map: dict[str, ResponseBaseModel] = {}
        for item_id, item_payload in payload_map.items():
            if not isinstance(item_id, str):
                raise AppException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    code=50012,
                    message=f"invalid data key in: {file_path.name}",
                )
            model_map[item_id] = model_class.model_validate(item_payload)

        self._file_cache[cache_key] = model_map
        return model_map

    def _collect_by_ids(
        self,
        *,
        resource_name: str,
        ids: Sequence[str],
        resource_map: dict[str, ResponseBaseModel],
    ) -> list[ResponseBaseModel]:
        if not ids:
            return []

        missing_ids = [item_id for item_id in ids if item_id not in resource_map]
        if missing_ids:
            preview = ", ".join(missing_ids[:5])
            suffix = "" if len(missing_ids) <= 5 else ", ..."
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40403,
                message=f"{resource_name} not found: {preview}{suffix}",
            )

        return [resource_map[item_id] for item_id in ids]

    @staticmethod
    def _validate_pagination(*, offset: int, limit: int) -> None:
        if offset < 0 or limit <= 0:
            raise AppException(
                status_code=HTTPStatus.BAD_REQUEST,
                code=40001,
                message="offset must be >= 0 and limit must be > 0",
            )
