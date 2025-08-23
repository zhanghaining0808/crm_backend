from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Email(SQLModel):
    subject: str = Field(max_length=255, description="邮件主题")
    body: str = Field(description="邮件内容(支持HTML格式)")

    def dict(self) -> Dict[str, Any]:
        return {"subject": self.subject, "body": self.body}


class EmailTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="推广任务名称")
    status: str = Field(
        default="待处理", description="任务状态(待处理/发送中/发送成功/发送失败)"
    )
    send_by: str = Field(description="用户邮箱")
    send_to: str = Field(
        description="发送对象邮箱",
    )
    email: Dict[str, Any] = Field(
        sa_column=Column(JSON), description="邮件内容，包含主题和正文"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    sended_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="发送时间(如果任务状态为发送成功或发送失败时才有值)",
    )

    # 添加便捷方法来处理 Email 对象
    def set_email(self, email: Email):
        """设置邮件内容"""
        self.email = email.dict()

    def get_email(self) -> Email:
        """获取邮件对象"""
        if self.email:
            return Email(**self.email)
        return Email(subject="", body="")


class BatchEmailTaskRequest(SQLModel):
    name: str = Field(max_length=100, description="推广任务名称")
    email: Email = Field(description="邮件内容，包含主题和正文")
    send_customer_by_tags: Optional[List[str]] = Field(
        default=[],
        description="按客户标签决定批量发送给对应包含了该标签的客户",
    )
    send_customer_by_emails: Optional[List[str]] = Field(
        default=[],
        description="按客户邮箱决定批量发送给对应的客户",
    )


class EmailTaskUpdate(SQLModel):
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[Email] = None


class EmailTaskUpdateReq(BaseModel):
    update_key: List[str] = Field(description="需要更新的字段列表")
    update_EmailTask: EmailTaskUpdate = Field(description="需要更新的邮件任务数据")
