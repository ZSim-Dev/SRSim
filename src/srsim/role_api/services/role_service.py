import re
from http import HTTPStatus
from typing import ClassVar, cast

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from srsim.role_api.core.exceptions import AppException
from srsim.role_api.models.base import ResponseBaseModel
from srsim.role_api.models.role_api import (
    RoleBasicData,
    RoleDetailData,
    RoleListData,
    RoleListItem,
    RolePanelData,
    RolePromotionsData,
    RoleRankData,
    RoleRanksData,
    RoleSkillData,
    RoleSkillDescriptionData,
    RoleSkillsData,
    RoleSkillTreeData,
    SkillDescriptionRender,
)
from srsim.role_api.services.role_data_loader import RoleDataLoader


class RoleService:
    _TOTAL_SCAN_LIMIT: int = 1_000_000
    _PROMOTION_BOUNDARY_LEVELS: tuple[int, ...] = (20, 30, 40, 50, 60, 70)
    _SKILL_PLACEHOLDER_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"#(?P<index>\d+)\[(?P<format>i|f1|f2)\]"
    )
    _RICH_TEXT_VALUE_COLOR: ClassVar[str] = "#F29E38"
    _loader: RoleDataLoader

    def __init__(self, loader: RoleDataLoader | None = None) -> None:
        self._loader = RoleDataLoader() if loader is None else loader

    async def list_roles(
        self,
        session: AsyncSession,
        language: str,
        offset: int,
        limit: int,
    ) -> ResponseBaseModel:
        characters = await self._loader.list_characters(
            session=session,
            language=language,
            offset=offset,
            limit=limit,
        )
        items = [
            self._to_role_list_item(
                character=self._convert_model(
                    item,
                    RoleBasicData,
                    resource_name="character",
                ),
            )
            for item in characters
        ]
        total = await self._loader.count_characters(session=session, language=language)
        return self._convert_from_payload(
            payload={
                "items": items,
                "total": total,
                "offset": offset,
                "limit": limit,
            },
            target_type=RoleListData,
            resource_name="role list",
        )

    async def search_roles(
        self,
        session: AsyncSession,
        *,
        language: str,
        path: str | None,
        element: str | None,
        name: str | None,
    ) -> ResponseBaseModel:
        characters = await self._loader.list_characters(
            session=session,
            language=language,
            offset=0,
            limit=self._TOTAL_SCAN_LIMIT,
        )
        path_filter = path.lower() if path is not None else None
        element_filter = element.lower() if element is not None else None
        name_filter = name.lower() if name is not None else None

        items: list[ResponseBaseModel] = []
        for character_data in characters:
            character = self._convert_model(
                character_data,
                RoleBasicData,
                resource_name="character",
            )
            if path_filter is not None and character.path.lower() != path_filter:
                continue
            if element_filter is not None and character.element.lower() != element_filter:
                continue
            if name_filter is not None and name_filter not in character.name.lower():
                continue
            items.append(self._to_role_list_item(character=character))

        total = len(items)
        return self._convert_from_payload(
            payload={
                "items": items,
                "total": total,
                "offset": 0,
                "limit": total,
            },
            target_type=RoleListData,
            resource_name="role list",
        )

    async def get_role_detail(
        self,
        session: AsyncSession,
        language: str,
        role_id: str,
    ) -> ResponseBaseModel:
        basic = await self._get_role_basic(
            session=session,
            language=language,
            role_id=role_id,
        )
        skills = self._convert_model_list(
            await self._loader.get_skills_by_ids(
                session=session,
                language=language,
                ids=self._as_str_list(basic, "skills"),
            ),
            RoleSkillData,
            resource_name="skill",
        )
        ranks = self._convert_model_list(
            await self._loader.get_ranks_by_ids(
                session=session,
                language=language,
                ids=self._as_str_list(basic, "ranks"),
            ),
            RoleRankData,
            resource_name="rank",
        )
        skill_trees = self._convert_model_list(
            await self._loader.get_skill_trees_by_ids(
                session=session,
                language=language,
                ids=self._as_str_list(basic, "skill_trees"),
            ),
            RoleSkillTreeData,
            resource_name="skill tree",
        )
        return self._convert_from_payload(
            payload={
                "basic": basic,
                "skills": skills,
                "ranks": ranks,
                "skill_trees": skill_trees,
            },
            target_type=RoleDetailData,
            resource_name="role detail",
        )

    async def get_role_skills(
        self,
        session: AsyncSession,
        language: str,
        role_id: str,
    ) -> ResponseBaseModel:
        basic = await self._get_role_basic(
            session=session,
            language=language,
            role_id=role_id,
        )
        skills = self._convert_model_list(
            await self._loader.get_skills_by_ids(
                session=session,
                language=language,
                ids=self._as_str_list(basic, "skills"),
            ),
            RoleSkillData,
            resource_name="skill",
        )
        return self._convert_from_payload(
            payload={
                "role_id": self._as_str_value(basic, "id"),
                "skills": skills,
            },
            target_type=RoleSkillsData,
            resource_name="role skills",
        )

    async def get_role_skill_description(
        self,
        session: AsyncSession,
        language: str,
        role_id: str,
        skill_id: str,
        skill_level: int,
    ) -> ResponseBaseModel:
        basic = await self._get_role_basic(
            session=session,
            language=language,
            role_id=role_id,
        )
        skill_ids = self._as_str_list(basic, "skills")
        if skill_id not in skill_ids:
            raise AppException(
                status_code=HTTPStatus.NOT_FOUND,
                code=40403,
                message=f"skill not found for role: role_id={role_id}, skill_id={skill_id}",
            )

        skill = self._convert_model(
            (await self._loader.get_skills_by_ids(
                session=session, language=language, ids=[skill_id]
            ))[0],
            RoleSkillData,
            resource_name="skill",
        )
        if skill_level < 1 or skill_level > skill.max_level:
            raise AppException(
                status_code=HTTPStatus.BAD_REQUEST,
                code=40002,
                message=(
                    f"invalid skill_level: {skill_level}, must be between 1 and {skill.max_level}"
                ),
            )

        param_row_index = skill_level - 1
        if param_row_index >= len(skill.params):
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50020,
                message=(
                    f"missing params row for skill: skill_id={skill_id}, skill_level={skill_level}"
                ),
            )
        level_params = skill.params[param_row_index]

        desc = self._render_skill_text_block(
            text=skill.desc,
            params=level_params,
            skill_id=skill_id,
            skill_level=skill_level,
        )
        simple_desc = self._render_skill_text_block(
            text=skill.simple_desc,
            params=level_params,
            skill_id=skill_id,
            skill_level=skill_level,
        )
        return self._convert_from_payload(
            payload={
                "role_id": self._as_str_value(basic, "id"),
                "skill_id": skill.id,
                "skill_level": skill_level,
                "name": skill.name,
                "desc": desc,
                "simple_desc": simple_desc,
            },
            target_type=RoleSkillDescriptionData,
            resource_name="role skill description",
        )

    async def get_role_ranks(
        self,
        session: AsyncSession,
        language: str,
        role_id: str,
    ) -> ResponseBaseModel:
        basic = await self._get_role_basic(
            session=session,
            language=language,
            role_id=role_id,
        )
        ranks = self._convert_model_list(
            await self._loader.get_ranks_by_ids(
                session=session,
                language=language,
                ids=self._as_str_list(basic, "ranks"),
            ),
            RoleRankData,
            resource_name="rank",
        )
        return self._convert_from_payload(
            payload={
                "role_id": self._as_str_value(basic, "id"),
                "ranks": ranks,
            },
            target_type=RoleRanksData,
            resource_name="role ranks",
        )

    async def get_role_promotions(
        self,
        session: AsyncSession,
        language: str,
        role_id: str,
    ) -> ResponseBaseModel:
        basic = await self._get_role_basic(
            session=session,
            language=language,
            role_id=role_id,
        )
        promotion = await self._loader.get_promotion(
            session=session, language=language, role_id=role_id
        )
        promotion_payload = promotion.model_dump()
        return self._convert_from_payload(
            payload={
                "role_id": self._as_str_value(basic, "id"),
                "values": promotion_payload.get("values"),
                "materials": promotion_payload.get("materials"),
            },
            target_type=RolePromotionsData,
            resource_name="role promotions",
        )

    async def get_role_panel(
        self,
        session: AsyncSession,
        language: str,
        role_id: str,
        level: int,
        promoted: bool | None,
    ) -> ResponseBaseModel:
        basic = await self._get_role_basic(
            session=session,
            language=language,
            role_id=role_id,
        )
        promotion = await self._loader.get_promotion(
            session=session, language=language, role_id=role_id
        )
        promotion_payload = promotion.model_dump()
        promotion_values = promotion_payload.get("values")
        if not isinstance(promotion_values, list):
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50020,
                message="invalid role promotion values payload type",
            )

        promotion_stage = self._resolve_promotion_stage(level=level, promoted=promoted)
        if promotion_stage < 0 or promotion_stage >= len(promotion_values):
            raise AppException(
                status_code=HTTPStatus.BAD_REQUEST,
                code=40002,
                message=f"invalid promotion stage for level: {level}",
            )

        stats = self._build_role_panel_stats(
            promotion_values[promotion_stage],
            level=level,
        )
        return self._convert_from_payload(
            payload={
                "role_id": self._as_str_value(basic, "id"),
                "level": level,
                "promoted": promoted,
                "promotion": promotion_stage,
                "stats": stats,
            },
            target_type=RolePanelData,
            resource_name="role panel",
        )

    async def _get_role_basic(
        self,
        *,
        session: AsyncSession,
        language: str,
        role_id: str,
    ) -> ResponseBaseModel:
        return self._convert_model(
            await self._loader.get_character(session=session, language=language, role_id=role_id),
            RoleBasicData,
            resource_name="character",
        )

    @classmethod
    def _to_role_list_item(
        cls,
        *,
        character: ResponseBaseModel,
    ) -> ResponseBaseModel:
        return cls._convert_from_payload(
            payload={
                "id": cls._as_str_value(character, "id"),
                "name": cls._as_str_value(character, "name"),
                "tag": cls._as_str_value(character, "tag"),
                "rarity": cls._as_int_value(character, "rarity"),
                "path": cls._as_str_value(character, "path"),
                "element": cls._as_str_value(character, "element"),
                "max_sp": cls._as_optional_int_value(character, "max_sp"),
                "icon": cls._as_str_value(character, "icon"),
                "preview": cls._as_str_value(character, "preview"),
                "portrait": cls._as_str_value(character, "portrait"),
            },
            target_type=RoleListItem,
            resource_name="role list item",
        )

    @staticmethod
    def _convert_model[T: ResponseBaseModel](
        model: ResponseBaseModel,
        target_type: type[T],
        *,
        resource_name: str,
    ) -> T:
        return RoleService._convert_from_payload(
            payload=model.model_dump(),
            target_type=target_type,
            resource_name=resource_name,
        )

    @classmethod
    def _convert_model_list[T: ResponseBaseModel](
        cls,
        models: list[ResponseBaseModel],
        target_type: type[T],
        *,
        resource_name: str,
    ) -> list[T]:
        return [
            cls._convert_model(
                model,
                target_type,
                resource_name=resource_name,
            )
            for model in models
        ]

    @staticmethod
    def _convert_from_payload[T: ResponseBaseModel](
        *,
        payload: object,
        target_type: type[T],
        resource_name: str,
    ) -> T:
        try:
            return target_type.model_validate(payload)
        except ValidationError as exc:
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50020,
                message=f"invalid {resource_name} payload type",
            ) from exc

    @staticmethod
    def _as_str_value(model: ResponseBaseModel, name: str) -> str:
        value = getattr(model, name, None)
        if isinstance(value, str):
            return value
        raise AppException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            code=50021,
            message=f"invalid role field type: {name}",
        )

    @staticmethod
    def _as_int_value(model: ResponseBaseModel, name: str) -> int:
        value = getattr(model, name, None)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        raise AppException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            code=50021,
            message=f"invalid role field type: {name}",
        )

    @staticmethod
    def _as_optional_int_value(model: ResponseBaseModel, name: str) -> int | None:
        value = getattr(model, name, None)
        if value is None:
            return None
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        raise AppException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            code=50021,
            message=f"invalid role field type: {name}",
        )

    @staticmethod
    def _as_str_list(model: ResponseBaseModel, name: str) -> list[str]:
        value = getattr(model, name, None)
        if isinstance(value, list):
            items = cast(list[object], value)
            if all(isinstance(item, str) for item in items):
                return cast(list[str], items)
        raise AppException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            code=50021,
            message=f"invalid role field type: {name}",
        )

    @classmethod
    def _resolve_promotion_stage(cls, *, level: int, promoted: bool | None) -> int:
        if level in cls._PROMOTION_BOUNDARY_LEVELS:
            if promoted is None:
                raise AppException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    code=40002,
                    message=("promoted is required when level is one of 20/30/40/50/60/70"),
                )
            return cls._PROMOTION_BOUNDARY_LEVELS.index(level) + (1 if promoted else 0)
        return sum(boundary < level for boundary in cls._PROMOTION_BOUNDARY_LEVELS)

    @staticmethod
    def _build_role_panel_stats(
        promotion_values: object,
        *,
        level: int,
    ) -> dict[str, int | float]:
        if not isinstance(promotion_values, dict):
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50020,
                message="invalid role panel values payload type",
            )

        stats: dict[str, int | float] = {}
        for stat_name, stat_value in promotion_values.items():
            if not isinstance(stat_name, str) or not isinstance(stat_value, dict):
                raise AppException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    code=50020,
                    message="invalid role panel stat payload type",
                )

            base = stat_value.get("base")
            step = stat_value.get("step")
            if (
                isinstance(base, bool)
                or not isinstance(base, (int, float))
                or isinstance(step, bool)
                or not isinstance(step, (int, float))
            ):
                raise AppException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    code=50020,
                    message="invalid role panel stat value payload type",
                )
            stats[stat_name] = base + step * (level - 1)
        return stats

    @classmethod
    def _render_skill_text_block(
        cls,
        *,
        text: str,
        params: list[int | float],
        skill_id: str,
        skill_level: int,
    ) -> SkillDescriptionRender:
        plain_text = cls._render_skill_text(
            text=text,
            params=params,
            skill_id=skill_id,
            skill_level=skill_level,
            rich=False,
        )
        rich_text = cls._render_skill_text(
            text=text,
            params=params,
            skill_id=skill_id,
            skill_level=skill_level,
            rich=True,
        )
        return cls._convert_from_payload(
            payload={
                "plain_text": plain_text,
                "rich_text": rich_text,
            },
            target_type=SkillDescriptionRender,
            resource_name="skill description render",
        )

    @classmethod
    def _render_skill_text(
        cls,
        *,
        text: str,
        params: list[int | float],
        skill_id: str,
        skill_level: int,
        rich: bool,
    ) -> str:
        def replacer(match: re.Match[str]) -> str:
            value_text = cls._resolve_placeholder_value(
                text=text,
                match=match,
                params=params,
                skill_id=skill_id,
                skill_level=skill_level,
            )
            if not rich:
                return value_text
            return f'<span style="color:{cls._RICH_TEXT_VALUE_COLOR}">{value_text}</span>'

        return cls._SKILL_PLACEHOLDER_PATTERN.sub(replacer, text)

    @staticmethod
    def _resolve_placeholder_value(
        *,
        text: str,
        match: re.Match[str],
        params: list[int | float],
        skill_id: str,
        skill_level: int,
    ) -> str:
        placeholder_index = int(match.group("index"))
        param_index = placeholder_index - 1
        if param_index < 0 or param_index >= len(params):
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50020,
                message=(
                    "placeholder index out of range: "
                    f"skill_id={skill_id}, skill_level={skill_level}, "
                    f"placeholder=#{placeholder_index}, params_len={len(params)}"
                ),
            )

        value = params[param_index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise AppException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                code=50020,
                message=(
                    "invalid placeholder value type: "
                    f"skill_id={skill_id}, skill_level={skill_level}, "
                    f"placeholder=#{placeholder_index}"
                ),
            )

        placeholder_format = match.group("format")
        is_percent_value = match.end() < len(text) and text[match.end()] in {"%", "％"}
        display_value = float(value) * (100.0 if is_percent_value else 1.0)
        if placeholder_format == "i":
            return str(int(display_value))
        if placeholder_format == "f1":
            return f"{display_value:.1f}"
        return f"{display_value:.2f}"
