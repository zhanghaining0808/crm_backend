from fastapi import Request
from loguru import logger


def request_logger_M(request: Request):
    logger.debug(f"[{request.method.upper()}]{request.url}")
    # request.method.upper() 把 HTTP 方法转为大写
    return request
