import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# 调试开关：为 True 时在响应中返回完整的异常堆栈信息
DEBUG = True


def exception_detail(exc: Exception) -> str:
    """获取异常的详细内容（包含完整堆栈信息），仅在 DEBUG 为 True 时返回"""
    return traceback.format_exc() if DEBUG else ""


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    捕获 HTTPException（如 404、401、403 等手动抛出的 HTTP 异常）
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": str(exc.detail),
            "type": "HTTPException",
            "detail": exception_detail(exc),
        },
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    捕获数据库约束错误（唯一约束、外键约束、非空约束、主键约束等）。

    通过底层数据库驱动返回的错误码 / 错误信息，判断具体约束类型：
    - 唯一约束（Duplicate / Unique）
    - 外键约束（Foreign Key）
    - 非空约束（Not Null）
    - 主键约束（Primary Key）
    - 其他约束
    """
    orig = exc.orig
    # 底层驱动错误码（MySQL/aiomysql 通过 args[0] 提供）
    args = getattr(orig, "args", None)
    errno = args[0] if args else None
    msg = str(orig).lower()

    # MySQL 错误码：1062 重复记录，1451/1452/1216/1217 外键，1048 非空，1062 主键冲突
    if errno in (1062,) or "duplicate" in msg or "unique" in msg:
        constraint_type = "唯一约束错误（Unique）"
    elif errno in (1451, 1452, 1216, 1217) or "foreign key" in msg:
        constraint_type = "外键约束错误（Foreign Key）"
    elif errno in (1048,) or "cannot be null" in msg or "not null" in msg:
        constraint_type = "非空约束错误（Not Null）"
    elif "primary key" in msg or "pk_" in msg:
        constraint_type = "主键约束错误（Primary Key）"
    else:
        constraint_type = "其他数据库约束错误"

    return JSONResponse(
        status_code=400,
        content={
            "code": 400,
            "message": f"数据库约束错误：{constraint_type}",
            "type": "IntegrityError",
            "detail": exception_detail(exc),
        },
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    捕获数据库通用异常（如连接失败、SQL 语法错误、超时等）
    """
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "数据库操作异常",
            "type": "SQLAlchemyError",
            "detail": exception_detail(exc),
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    捕获所有未处理的其他异常
    """
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "type": type(exc).__name__,
            "detail": exception_detail(exc),
        },
    )


def register_exception_handlers(app):
    """
    统一注册所有异常处理器到 FastAPI 应用，使异常捕获全局可用。

    :param app: FastAPI 实例
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(Exception, global_exception_handler)
