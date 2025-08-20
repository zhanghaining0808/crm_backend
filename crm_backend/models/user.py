from datetime import datetime
from sqlmodel import Field, SQLModel


# table=True 会告诉SQLModel这是一个表模型,它应该表示SQL数据库中的一个表,而不仅仅是一个数据类型(就像其他常规的Pydantic类一样)
# Field(primary_key=True)会告诉SQLModel id是SQL数据库中的主键
# 把类型设置为int|None SQLModel应该为此列创建一个SQL索引,这样在读取按此列过滤的数据时,程序能在数据库中进行更快的查找
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    # unique 唯一约束 表里不能出现同名
    passwd: str
    # is_admin: bool = Field(default=False)
    # created_at: datetime = Field(default_factory=datetime.utcnow)
    # updated_at: datetime = Field(default_factory=datetime.utcnow)
    # last_login: datetime = Field(default_factory=datetime.utcnow)
