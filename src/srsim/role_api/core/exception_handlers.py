from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from srsim.role_api.core.exceptions import AppException
from srsim.role_api.models.response import ResponseModel


def _json_content[T](response: ResponseModel[T]) -> dict[str, object]:
    return response.model_dump(by_alias=True)


async def app_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    app_exc = cast(AppException, exc)
    payload = ResponseModel[None](
        code=app_exc.code,
        message=app_exc.message,
        data=None,
    )
    return JSONResponse(status_code=app_exc.status_code, content=_json_content(payload))


async def validation_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    validation_exc = cast(RequestValidationError, exc)
    payload = ResponseModel[object](
        code=42200,
        message="request validation failed",
        data=validation_exc.errors(),
    )
    return JSONResponse(status_code=422, content=_json_content(payload))


async def http_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    http_exc = cast(HTTPException, exc)
    payload = ResponseModel[object](
        code=http_exc.status_code,
        message=http_exc.detail,
        data=None,
    )
    return JSONResponse(status_code=http_exc.status_code, content=_json_content(payload))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
