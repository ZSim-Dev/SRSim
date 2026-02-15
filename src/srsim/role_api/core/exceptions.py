from http import HTTPStatus


class AppException(Exception):
    status_code: int = HTTPStatus.BAD_REQUEST
    code: int = 40000
    message: str = "application error"

    def __init__(
        self,
        *,
        status_code: int | None = None,
        code: int | None = None,
        message: str | None = None,
    ) -> None:
        self.status_code = self.__class__.status_code if status_code is None else status_code
        self.code = self.__class__.code if code is None else code
        self.message = self.__class__.message if message is None else message
        super().__init__(self.message)
