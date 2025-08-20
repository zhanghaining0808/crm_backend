from datetime import timedelta
from sqlmodel import select
from fastapi import APIRouter, Depends, HTTPException

from crm_backend.db.db import SessionDep
from crm_backend.middleware.request_loger import request_logger_M
from crm_backend.models.crm_http_exception import CrmHTTPException
from crm_backend.models.response import CrmResponse
from crm_backend.models.user import User
from crm_backend.utils.jwt import jwt_encode
from crm_backend.utils.security import get_passwd_hash


user_router = APIRouter(prefix="/api/users", dependencies=[Depends(request_logger_M)])


@user_router.post("/add", response_model=CrmResponse)
def create_user(user: User, session: SessionDep):
    find_user = session.exec(select(User).where(user.name == User.name)).first()
    if find_user:
        raise CrmHTTPException(
            status_code=404, detail="相同用户名称已存在, 请更换用户名!"
        )
    user.passwd = get_passwd_hash(user.passwd)

    session.add(user)
    session.commit()
    session.refresh(user)
    token = jwt_encode({"username": user.name}, timedelta(days=1))
    return CrmResponse(data={"user": user, "access_token": token}, msg="创建用户成功")
