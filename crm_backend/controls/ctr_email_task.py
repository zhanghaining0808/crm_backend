from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import select

from crm_backend.db.db import SessionDep
from crm_backend.middleware.check_auth import check_auth_M
from crm_backend.middleware.request_loger import request_logger_M
from crm_backend.models.crm_http_exception import CrmHTTPException
from crm_backend.models.customer import Customer
from crm_backend.models.email_task import (
    EmailTask,
    EmailTaskUpdateReq,
)
from crm_backend.models.response import CrmResponse
from crm_backend.utils.email_task_execer import EmailTaskExecer


email_router = APIRouter(
    prefix="/email_tasks",
    dependencies=[Depends(request_logger_M), Depends(check_auth_M)],
)
email_task_execer = EmailTaskExecer()  # 实例化任务执行器


# 创建邮件任务
@email_router.post("/add", response_model=CrmResponse)
def create_email_task(request: Request, email_task: EmailTask, session: SessionDep):
    find_customer = session.get(Customer, email_task.send_to)

    if not find_customer:
        raise CrmHTTPException(status_code=404, detail="客户不存在")
    if find_customer.is_blacklist:
        raise CrmHTTPException(status_code=403, detail="客户在黑名单中，跳过邮件发送")

    email_task.send_by = request.state.user_email
    email_task.send_to = find_customer.email
    session.add(email_task)
    session.commit()
    session.refresh(email_task)
    email_task_execer.add_task(email_task)  # 添加任务到执行器并开始排队等待执行
    return CrmResponse(data={"email_task": email_task}, msg="邮件任务创建成功")


# 创建邮件任务(批量添加)
# @email_router.post("/add", response_model=CrmResponse)
# def create_email_tasks(
#     request: Request, email_task: CreateEmailTasks, session: SessionDep
# ):
#     email_task.send_by = request.state.user_id
#     session.add(email_task)
#     session.commit()
#     session.refresh(email_task)
#     email_task_execer.add_task(email_task)  # 添加任务到执行器
#     return CrmResponse(data={"email_task": email_task}, msg="邮件任务创建成功")


# 读取全部邮件任务
@email_router.get("/query", response_model=CrmResponse)
@email_router.post("/query", response_model=CrmResponse)
def read_all_email_tasks(
    request: Request,
    session: SessionDep,
    offset: int = Query(0, ge=0, description="偏移量(从0开始)"),
    limit: int = Query(10, ge=1, le=100, description="每页数量(1-100)"),
):
    email_tasks = session.exec(select(EmailTask).offset(offset).limit(limit)).all()
    if not request.state.is_admin:
        raise CrmHTTPException(
            status_code=403, detail="无权限查看其他邮件任务，请联系管理员！"
        )
    return CrmResponse(data=list(email_tasks), msg="查询邮件任务成功")


# 单个邮件任务查询
@email_router.get("/query/{task_id}", response_model=CrmResponse)
@email_router.post("/query/{task_id}", response_model=CrmResponse)
def read_email_task(request: Request, task_id: int, session: SessionDep):
    find_email_task = session.get(EmailTask, task_id)
    if not find_email_task:
        raise CrmHTTPException(status_code=404, detail="邮件任务不存在")
    if find_email_task.send_by != request.state.user_id and not request.state.is_admin:
        raise CrmHTTPException(
            status_code=403, detail="无权限查看此邮件任务，请联系管理员！"
        )
    return CrmResponse(data=find_email_task.model_dump(), msg="查询邮件任务成功")


# 更新邮件任务状态
@email_router.post("/update/{task_id}", response_model=CrmResponse)
def update_email_task(
    request: Request,
    task_id: int,
    email_task_update_req: EmailTaskUpdateReq,
    session: SessionDep,
):
    find_email_task = session.get(EmailTask, task_id)
    need_update_email_task = email_task_update_req.update_EmailTask.model_dump()
    if not need_update_email_task:
        raise CrmHTTPException(status_code=404, detail="邮件新任务数据未找到")
    if not find_email_task:
        raise CrmHTTPException(status_code=404, detail="邮件旧任务数据未找到")
    if find_email_task.send_by != request.state.user_id and not request.state.is_admin:
        raise CrmHTTPException(
            status_code=403, detail="无权限更新此邮件任务，请联系管理员！"
        )
    old_email_task = find_email_task.model_dump()
    new_email_task = old_email_task
    for need_update_key in email_task_update_req.update_key:
        if need_update_key in old_email_task.keys():
            new_email_task[need_update_key] = need_update_email_task[need_update_key]
    find_email_task.sqlmodel_update(new_email_task)
    session.commit()
    session.refresh(find_email_task)

    return CrmResponse(data=find_email_task.model_dump(), msg="更新单个邮件任务成功")


# 邮件任务删除


@email_router.post("/delete/{task_id}", response_model=CrmResponse)
def delete_email_task(request: Request, task_id: int, session: SessionDep):
    find_email_task = session.get(EmailTask, task_id)
    if not find_email_task:
        raise CrmHTTPException(status_code=404, detail="邮件任务未找到")
    if find_email_task.send_by != request.state.user_id and not request.state.is_admin:
        raise CrmHTTPException(
            status_code=403, detail="无权限删除此邮件任务，请联系管理员！"
        )
    session.delete(find_email_task)
    session.commit()
    return CrmResponse(data=find_email_task.model_dump(), msg="删除邮件任务成功")
