from typing import Any, Optional


class CustomException(Exception):
    def __init__(
        self,
        message: str,
        code: int = 400,
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.code = code
        self.detail = detail
        super().__init__(message)


class DocumentProcessingError(CustomException):
    def __init__(
        self,
        message: str = "Error processing document",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, code=422, detail=detail)


class DocumentNotFoundError(CustomException):
    def __init__(
        self,
        message: str = "Document not found",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, code=404, detail=detail)


class AuthenticationError(CustomException):
    def __init__(
        self,
        message: str = "Authentication failed",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, code=401, detail=detail)


class AuthorizationError(CustomException):
    def __init__(
        self,
        message: str = "Not authorized to perform this action",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, code=403, detail=detail)


class OpenAIError(CustomException):
    def __init__(
        self,
        message: str = "Error communicating with OpenAI",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, code=500, detail=detail) 