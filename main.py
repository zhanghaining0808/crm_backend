import os
from fastapi import FastAPI
import uvicorn
from crm_backend.controls.ctr_users import user_router
from crm_backend.controls.ctr_customers import customer_router
from crm_backend.controls.ctr_email_task import email_router
from crm_backend.db.db import create_db_and_tables
from loguru import logger

from crm_backend.utils.config import load_config
from crm_backend.utils.logger import init_logger

app = FastAPI()

app.include_router(prefix="/api", router=user_router)
app.include_router(prefix="/api", router=customer_router)
app.include_router(prefix="/api", router=email_router)


# 在启动时创建数据库表
@app.on_event("startup")
def on_startup():
    logger.info("服务启动成功")
    logger.info("开始初始化数据表...")
    create_db_and_tables()
    logger.info("数据表初始化成功")


if __name__ == "__main__":
    config = load_config()
    init_logger(config=config)
    logger.info(f"{8*'*'} CRM WEB Backend {8*'*'}")
    logger.info("启动服务中...")
    print(os.environ["HOSTNAME"])
    print(config.HOSTNAME)
    uvicorn.run(
        "main:app",
        host=config.HOSTNAME,
        port=config.PORT,
    )
