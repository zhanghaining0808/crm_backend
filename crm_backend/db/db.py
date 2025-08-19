from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session
from crm_backend.utils.config import load_config


config = load_config()

# 创建引擎
sqlite_file_name = config.SQLITE_FILE_NAME
sqlite_url = f"sqlite:///{sqlite_file_name}"  # 通常是"sqlite:///your_database.db""

connect_args = {"check_same_thread": False}
# 使用check_same_thread=False可以让FastAPI在不同线程中使用同一个SQLite数据库
# 这很有必要,因为单个请求可能会使用多个线程 （例如在依赖项中）
# 不用担心 我们会按照代码结构确保每个请求使用一个单独的sqlmodel会话,这实际上就是check_same_thread想要实现的
engine = create_engine(
    sqlite_url, connect_args=connect_args
)  # 这是传给底层SQLite驱动的参数


# 添加一个为所有表模型创建表
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Session 会存储内存中的对象并跟踪数据所需更改的内容,然后它使用engine与数据库进行通信
# 我们会使用yield创建一个FastAPI依赖项,为每个请求提供一个新的Session 这确保我们每个请求使用一个单独的对话
# 然后我们创建一个Annotated的依赖项SessionDep来简化其他也会用到此依赖的代码
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
