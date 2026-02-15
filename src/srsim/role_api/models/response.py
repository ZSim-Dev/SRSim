from srsim.role_api.models.base import ResponseBaseModel


class ResponseModel[T](ResponseBaseModel):
    code: int = 0
    message: str = "success"
    data: T | None = None
