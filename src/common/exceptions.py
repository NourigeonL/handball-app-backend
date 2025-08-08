class GenericError(Exception):
    def __init__(self, message : str = "", status_code : int = 500) -> None:
        self.message = message
        self.status_code = status_code

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.message})"

    def json(self) -> dict:
        return {"ErrorType" : self.__class__.__name__, "message":self.message}