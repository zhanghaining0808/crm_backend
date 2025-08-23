import os
from fastapi import FastAPI
import uvicorn
from crm_backend.controls.ctr_users import user_router
from crm_backend.controls.ctr_customers import customer_router
from crm_backend.controls.ctr_email_task import email_router
from fastapi.middleware.cors import CORSMiddleware
from crm_backend.db.db import create_db_and_tables
from crm_backend.db.init_data import init_all_sample_data
from loguru import logger

from crm_backend.utils.config import load_config
from crm_backend.utils.logger import init_logger

app = FastAPI()

# 设置允许的源列表
origins = [
    "http://localhost:5173",  # Vue 开发服务器
    "http://127.0.0.1:5173",  # 有时浏览器会使用这个地址
    # 可以添加其他需要的前端地址
]
# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 或使用 ["*"] 允许所有源（不推荐生产环境）
    # 设置允许哪些"来源"(域名)可以访问你的API
    # 示例：origins = ["http://localhost:3000", "https://yourfrontend.com"]
    # 使用["*"]表示允许所有网站访问(不安全，仅建议开发用)
    allow_credentials=True,
    # 允许浏览器在跨域请求中发送凭证(如cookies, HTTP认证等)
    allow_methods=["*"],  # 允许所有方法
    # 允许所有HTTP方法(GET, POST, PUT等)
    # 也可以指定具体方法：["GET", "POST"]
    allow_headers=["*"],  # 允许所有头
    # 允许请求中携带所有类型的头信息
)

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
    
    # 根据配置决定是否初始化示例数据
    config = load_config()
    if config.INIT_SAMPLE_DATA:
        logger.info("开始初始化示例数据...")
        init_all_sample_data()
        logger.info("示例数据初始化完成")
    else:
        logger.info("跳过示例数据初始化（配置中已禁用）")


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
