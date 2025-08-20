from datetime import timedelta
from typing import Annotated
from sqlmodel import select
from fastapi import APIRouter, Depends, Query, Request
from crm_backend.db.db import SessionDep
from crm_backend.middleware.check_auth import check_auth_M
from crm_backend.middleware.request_loger import request_logger_M
from crm_backend.models.crm_http_exception import CrmHTTPException
from crm_backend.models.response import CrmResponse
from crm_backend.models.user import User, UserUpdateReq
from crm_backend.utils.jwt import jwt_decode, jwt_encode
from crm_backend.utils.security import get_passwd_hash, verify_passwd


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


# 读取全部用户
@user_router.get(
    "/query", response_model=CrmResponse, dependencies=[Depends(check_auth_M)]
)
@user_router.post(
    "/query", response_model=CrmResponse, dependencies=[Depends(check_auth_M)]
)
def read_all_users(
    request: Request,
    session: SessionDep,
    offset: int = Query(0, ge=0, description="偏移量（从0开始）"),
    limit: int = Query(10, ge=1, le=100, description="每页数量（1-100）"),
):
    if not request.state.is_admin:
        raise CrmHTTPException(
            status_code=403, detail="无权限修改其他用户信息，请联系管理员！"
        )
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return CrmResponse(data=list(users), msg="获取全部用户成功")


# 读取单个用户
@user_router.get("/query/{user_id}", response_model=CrmResponse)
@user_router.post("/query/{user_id}", response_model=CrmResponse)
def read_user(request: Request, user_id: int, session: SessionDep):
    find_user = session.get(User, user_id)
    if not find_user:
        raise CrmHTTPException(status_code=404, detail="用户不存在")

    if find_user.id != request.state.user_id and not request.state.is_admin:
        raise CrmHTTPException(
            status_code=403, detail="无权限查看其他用户信息，请联系管理员！"
        )

    return CrmResponse(data=list(find_user), msg="获取用户成功")


# 更新用户信息
@user_router.post(
    "/update/{user_id}",
    response_model=CrmResponse,
    dependencies=[Depends(check_auth_M)],
)
def update_user(
    request: Request, user_id: int, user_update_req: UserUpdateReq, session: SessionDep
):
    find_user = session.get(User, user_id)
    need_update_user = user_update_req.update_user.model_dump()
    if not need_update_user:
        raise CrmHTTPException(status_code=404, detail="用户新数据未找到！")
    if not find_user:
        raise CrmHTTPException(status_code=404, detail="用户旧数据未找到！")

    if find_user.id != request.state.user_id and not request.state.is_admin:
        raise CrmHTTPException(
            status_code=403, detail="无权限修改其他用户信息，请联系管理员！"
        )

    old_user = find_user.model_dump()
    new_user = old_user
    for need_update_key in user_update_req.update_key:
        print(need_update_key)
        if need_update_key in old_user.keys():
            new_user[need_update_key] = need_update_user[need_update_key]

    find_user.sqlmodel_update(new_user)
    session.commit()
    session.refresh(find_user)
    return CrmResponse(data=find_user.model_dump(), msg="更新单个用户成功")


# 删除用户
@user_router.post(
    "/delete/{user_id}",
    response_model=CrmResponse,
    dependencies=[Depends(check_auth_M)],
)
def delete_user(request: Request, user_id: int, session: SessionDep):
    find_user = session.get(User, user_id)
    if not find_user:
        raise CrmHTTPException(status_code=404, detail="用户不存在")
    if find_user.id != request.state.user_id and not request.state.is_admin:
        raise CrmHTTPException(
            status_code=403, detail="无权限修改其他用户信息，请联系管理员！"
        )
    session.delete(find_user)
    session.commit()
    return CrmResponse(data=find_user.model_dump(), msg="删除用户成功")


# 登录功能
@user_router.post("/login", response_model=CrmResponse)
async def login(user: User, session: SessionDep):
    find_user = session.exec(select(User).where(User.name == user.name)).first()
    if not find_user:
        raise CrmHTTPException(status_code=400, detail="用户或密码错误")
    if not verify_passwd(user.passwd, find_user.passwd):
        raise CrmHTTPException(status_code=400, detail="用户或密码错误")

    token = jwt_encode(
        {
            "user_id": find_user.id,
            "username": find_user.name,
            "is_admin": find_user.is_admin,
        },
        timedelta(days=1),
    )

    return CrmResponse(data={"user": find_user, "access_token": token}, msg="登录成功")


@user_router.post("/login/{token}", response_model=CrmResponse)
async def token_login(token: str, session: SessionDep):
    is_valid, decode_data = jwt_decode(token)
    if not decode_data:
        raise CrmHTTPException(status_code=400, detail="授权token不合法, 拒绝访问!!!")

    find_user = session.exec(
        select(User).where(decode_data["username"] == User.name)
    ).first()
    if not find_user:
        raise CrmHTTPException(status_code=400, detail="token错误或失效，请重新登录")
    if not is_valid:
        raise CrmHTTPException(status_code=400, detail="token错误或失效，请重新登录")

    return CrmResponse(
        data={"user": {"name": find_user.name}},
        msg="token登录成功，已验证身份有效",
    )
