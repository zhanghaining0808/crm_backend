from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# table=True 会告诉SQLModel这是一个表模型,它应该表示SQL数据库中的一个表,而不仅仅是一个数据类型(就像其他常规的Pydantic类一样)
# Field(primary_key=True)会告诉SQLModel id是SQL数据库中的主键
# 把类型设置为int|None SQLModel应该为此列创建一个SQL索引,这样在读取按此列过滤的数据时,程序能在数据库中进行更快的查找
class UserBase(SQLModel):
    name: str = Field(max_length=20, unique=True, description="用户名称", index=True)


# Optional 是 Python 类型注解中的一个重要概念，它表示一个值可能是某种类型，也可能是 None。
# 它是 Python 类型系统中表示"可为空值"的主要方式。
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    passwd: str = Field(max_length=128, description="密码")
    is_active: bool = Field(default=True, description="是否激活", index=True)
    is_admin: bool = Field(default=False, description="是否为管理员", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间", index=True
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间", index=True
    )
    last_login: datetime = Field(
        default_factory=datetime.utcnow, description="最后登录", index=True
    )


class UserPublic(UserBase):
    id: int
    name: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class UserUpdate(UserBase):
    name: Optional[str] = None
    passwd: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserUpdateReq(BaseModel):
    update_key: List[str] = Field(description="需要更新的字段列表")
    update_user: UserUpdate = Field(description="需要更新的用户数据")
