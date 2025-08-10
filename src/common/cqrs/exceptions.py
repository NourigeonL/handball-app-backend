from src.common.exceptions import GenericError
from fastapi import status

class UnauthorizedError(GenericError):
    def __init__(self, message : str = "", status_code : int = status.HTTP_401_UNAUTHORIZED) -> None:
        super().__init__(message, status_code)