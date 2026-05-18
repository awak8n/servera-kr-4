from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# Модели ответов на ошибки
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    detail: str = ""


# Кастомные исключения
class CustomExceptionA(Exception):
    """Вызывается когда не выполняется бизнес-условие (например, цена <= 0)."""
    def __init__(self, detail: str = "Business rule violated"):
        self.detail = detail


class CustomExceptionB(Exception):
    """Вызывается когда ресурс не найден."""
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class InsufficientStockException(Exception):
    """Вызывается при нехватке товара на складе."""
    def __init__(self, detail: str = "Insufficient stock"):
        self.detail = detail


# Обработчики исключений
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA):
    print(f"[ERROR] CustomExceptionA: {exc.detail} | path={request.url.path}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="BUSINESS_RULE_VIOLATED",
            message="A business rule was violated.",
            detail=exc.detail,
        ).model_dump(),
    )


async def custom_exception_b_handler(request: Request, exc: CustomExceptionB):
    print(f"[ERROR] CustomExceptionB: {exc.detail} | path={request.url.path}")
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error_code="RESOURCE_NOT_FOUND",
            message="The requested resource was not found.",
            detail=exc.detail,
        ).model_dump(),
    )


async def insufficient_stock_handler(request: Request, exc: InsufficientStockException):
    print(f"[ERROR] InsufficientStockException: {exc.detail} | path={request.url.path}")
    return JSONResponse(
        status_code=409,
        content=ErrorResponse(
            error_code="INSUFFICIENT_STOCK",
            message="Not enough items in stock.",
            detail=exc.detail,
        ).model_dump(),
    )
