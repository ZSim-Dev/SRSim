from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, Path, Query
from pydantic import ValidationError

from srsim.role_api.core.exceptions import AppException
from srsim.role_api.models.base import ResponseBaseModel
from srsim.role_api.models.response import ResponseModel
from srsim.role_api.models.role_api import (
    RoleDetailData,
    RoleListData,
    RolePanelData,
    RolePromotionsData,
    RoleRanksData,
    RoleSearchRequest,
    RoleSkillDescriptionData,
    RoleSkillsData,
)
from srsim.role_api.services.role_service import RoleService


class Language(StrEnum):
    CHT = "cht"
    CN = "cn"
    DE = "de"
    EN = "en"
    ES = "es"
    FR = "fr"
    ID = "id"
    JP = "jp"
    KR = "kr"
    PT = "pt"
    RU = "ru"
    TH = "th"
    VI = "vi"


router = APIRouter(tags=["roles"])
_service = RoleService()


def _response_with_typed_data[T: ResponseBaseModel](
    data: ResponseBaseModel,
    data_type: type[T],
) -> ResponseModel[T]:
    try:
        typed_data = data_type.model_validate(data.model_dump())
    except ValidationError as exc:
        raise AppException(
            status_code=500,
            code=50022,
            message="invalid role api response payload",
        ) from exc
    return ResponseModel[T](data=typed_data)


@router.get("/roles", response_model=ResponseModel[RoleListData])
async def list_roles(
    language: Annotated[Language, Query()] = Language.EN,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0, le=200)] = 20,
) -> ResponseModel[ResponseBaseModel]:
    payload = _service.list_roles(
        language=language.value,
        offset=offset,
        limit=limit,
    )
    return _response_with_typed_data(payload, RoleListData)


@router.post("/roles/search", response_model=ResponseModel[RoleListData])
async def search_roles(
    request: RoleSearchRequest,
    language: Annotated[Language, Query()] = Language.EN,
) -> ResponseModel[ResponseBaseModel]:
    payload = _service.search_roles(
        language=language.value,
        path=request.path,
        element=request.element,
        name=request.name,
    )
    return _response_with_typed_data(payload, RoleListData)


@router.get(
    "/roles/{role_id}",
    response_model=ResponseModel[RoleDetailData],
)
async def get_role(
    role_id: Annotated[str, Path(min_length=1)],
    language: Annotated[Language, Query()] = Language.EN,
) -> ResponseModel[ResponseBaseModel]:
    payload = _service.get_role_detail(language=language.value, role_id=role_id)
    return _response_with_typed_data(payload, RoleDetailData)


@router.get(
    "/roles/{role_id}/skills",
    response_model=ResponseModel[RoleSkillsData],
)
async def get_role_skills(
    role_id: Annotated[str, Path(min_length=1)],
    language: Annotated[Language, Query()] = Language.EN,
) -> ResponseModel[ResponseBaseModel]:
    payload = _service.get_role_skills(language=language.value, role_id=role_id)
    return _response_with_typed_data(payload, RoleSkillsData)


@router.get(
    "/roles/{role_id}/skills/{skill_id}/description",
    response_model=ResponseModel[RoleSkillDescriptionData],
)
async def get_role_skill_description(
    role_id: Annotated[str, Path(min_length=1)],
    skill_id: Annotated[str, Path(min_length=1)],
    language: Annotated[Language, Query()] = Language.EN,
    skill_level: Annotated[int, Query(ge=1)] = 1,
) -> ResponseModel[ResponseBaseModel]:
    payload = _service.get_role_skill_description(
        language=language.value,
        role_id=role_id,
        skill_id=skill_id,
        skill_level=skill_level,
    )
    return _response_with_typed_data(payload, RoleSkillDescriptionData)


@router.get(
    "/roles/{role_id}/ranks",
    response_model=ResponseModel[RoleRanksData],
)
async def get_role_ranks(
    role_id: Annotated[str, Path(min_length=1)],
    language: Annotated[Language, Query()] = Language.EN,
) -> ResponseModel[ResponseBaseModel]:
    payload = _service.get_role_ranks(language=language.value, role_id=role_id)
    return _response_with_typed_data(payload, RoleRanksData)


@router.get(
    "/roles/{role_id}/promotions",
    response_model=ResponseModel[RolePromotionsData],
)
async def get_role_promotions(
    role_id: Annotated[str, Path(min_length=1)],
    language: Annotated[Language, Query()] = Language.EN,
) -> ResponseModel[ResponseBaseModel]:
    payload = _service.get_role_promotions(language=language.value, role_id=role_id)
    return _response_with_typed_data(payload, RolePromotionsData)


@router.get(
    "/roles/{role_id}/panel",
    response_model=ResponseModel[RolePanelData],
)
async def get_role_panel(
    role_id: Annotated[str, Path(min_length=1)],
    language: Annotated[Language, Query()] = Language.EN,
    level: Annotated[int, Query(ge=1, le=80)] = 1,
    promoted: Annotated[bool | None, Query()] = None,
) -> ResponseModel[ResponseBaseModel]:
    payload = _service.get_role_panel(
        language=language.value,
        role_id=role_id,
        level=level,
        promoted=promoted,
    )
    return _response_with_typed_data(payload, RolePanelData)
