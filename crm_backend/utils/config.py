import os
from dotenv import load_dotenv
from pydantic import BaseModel


class Config(BaseModel):
    HOSTNAME: str
    PORT: int
    JWT_KEY: str
    SQLITE_FILE_NAME: str
    LOG_CONSOLE_LEVEL: str
    LOG_CONSOLE_FORMAT: str
    LOG_FILE_LEVEL: str
    LOG_FILE_PATH: str
    LOG_FILE_FORMAT: str


def load_config() -> Config:
    load_dotenv(".env")
    envs = os.environ

    return Config(**dict(envs))  # type: ignore
