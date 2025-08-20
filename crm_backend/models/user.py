from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# table=True 会告诉SQLModel这是一个表模型,它应该表示SQL数据库中的一个表,而不仅仅是一个数据类型(就像其他常规的Pydantic类一样)
# Field(primary_key=True)会告诉SQLModel id是SQL数据库中的主键
# 把类型设置为int|None SQLModel应该为此列创建一个SQL索引,这样在读取按此列过滤的数据时,程序能在数据库中进行更快的查找
class UserBase(SQLModel):
    name: str = Field(max_length=20, unique=True, description="用户名称", index=True)
    email: str = Field(max_length=255, unique=True, description="邮箱", index=True)
    phone: Optional[str] = Field(
        max_length=20, default=None, description="电话", index=True
    )
    passwd: str = Field(max_length=128, description="密码")


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class UserPublic(UserBase):
    is_active: bool = Field(default=True, description="是否激活", index=True)
    is_admin: bool = Field(default=False, description="是否为管理员", index=True)
    created_at: Optional[datetime] = Field(
        default=None, description="创建时间", index=True
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="更新时间", index=True
    )
    last_login: Optional[datetime] = Field(
        default=None, description="最后登录", index=True
    )


class UserUpdate(UserBase):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    passwd: str | None = None


class UserUpdateReq(BaseModel):
    update_key: List[str]
    update_user: UserUpdate
