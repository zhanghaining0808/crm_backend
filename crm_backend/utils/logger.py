import sys
from crm_backend.utils.config import Config

from loguru import logger


def init_logger(config: Config):
    # 先移除默认handler(避免重复输出)
    logger.remove()
    # 终端日志输出配置
    logger.add(
        sink=sys.stdout,
        format=config.LOG_CONSOLE_FORMAT,
        level=config.LOG_CONSOLE_LEVEL,
    )
    # 日志文件输出配置
    logger.add(
        config.LOG_FILE_PATH,
        format=config.LOG_CONSOLE_FORMAT,
        level=config.LOG_CONSOLE_LEVEL,
    )
