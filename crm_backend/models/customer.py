from datetime import datetime
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


# Field(index=True) 会告诉 SQLModel 应该为此列创建一个 SQL 索引，这样在读取按此列过滤的数据时，程序能在数据库中进行更快的查找
class CustomerBase(SQLModel):
    name: str = Field(max_length=20, unique=True, description="客户名称", index=True)
    email: str = Field(max_length=255, unique=True, description="邮箱", index=True)
    tags: list[str] = Field(sa_column=Column(JSON), default=[], description="客户标签")


class Customer(CustomerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CustomerPublic(CustomerBase):
    tags: list[str] = Field(sa_column=Column(JSON), default=[], description="客户标签")
    created_at: datetime = Field(default=None, description="创建时间", index=True)
    updated_at: datetime = Field(default=None, description="更新时间", index=True)


class CustomerUpdate(CustomerBase):
    name: str | None = None
    email: str | None = None
    tags: list[str] | None = Field(
        sa_column=Column(JSON), default=None, description="客户标签"
    )
