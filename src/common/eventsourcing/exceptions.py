from src.common.exceptions import GenericError
from fastapi import status

class AggregateNotFoundError(GenericError):
    def __init__(self, message : str = "", status_code : int = status.HTTP_404_NOT_FOUND) -> None:
        super().__init__(message, status_code)

class InvalidOperationError(GenericError):
    def __init__(self, message : str = "", status_code : int = status.HTTP_400_BAD_REQUEST) -> None:
        super().__init__(message, status_code)

class ArgumentError(GenericError):
    def __init__(self, message : str = "", status_code : int = status.HTTP_400_BAD_REQUEST) -> None:
        super().__init__(message, status_code)
        
class ConcurrencyError(GenericError):
    def __init__(self, message : str = "", status_code : int = status.HTTP_409_CONFLICT) -> None:
        super().__init__(message, status_code)