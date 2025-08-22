from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


# Field(index=True) 会告诉 SQLModel 应该为此列创建一个 SQL 索引，这样在读取按此列过滤的数据时，程序能在数据库中进行更快的查找
class CustomerBase(SQLModel):
    name: str = Field(max_length=20, unique=True, description="客户名称", index=True)


class Customer(CustomerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_blacklist: bool = Field(default=False, description="是否黑名单")
    email: str = Field(max_length=255, unique=True, description="邮箱", index=True)
    created_by: int
    tags: list[str] = Field(sa_column=Column(JSON), default=[], description="客户标签")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )


class CustomerPublic(CustomerBase):
    id: int
    name: str
    email: str
    tags: list[str] = Field(sa_column=Column(JSON), default=[], description="客户标签")
    created_at: datetime
    updated_at: datetime


class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    email: Optional[str] = None
    is_blacklist: Optional[bool] = None
    tags: list[str] | None = Field(
        sa_column=Column(JSON), default=None, description="客户标签"
    )


class CustomerUpdateReq(BaseModel):
    update_key: List[str] = Field(description="需要更新的字段列表")
    update_Customer: CustomerUpdate = Field(description="需要更新的用户数据")


# TODO 黑名单邮箱展示
