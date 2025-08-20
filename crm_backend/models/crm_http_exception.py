# 写个类继承HTTPException类，以便我们增加自定义的额外功能，例如使用日志记录报错的信息
from typing import Any, Dict
from fastapi import HTTPException
from loguru import logger


class CrmHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Dict[str, str] | None = None,
    ) -> None:
        logger.error(f"错误代码[{status_code}] {detail}")
        super().__init__(status_code, detail, headers)
