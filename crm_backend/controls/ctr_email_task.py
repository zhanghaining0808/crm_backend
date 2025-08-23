from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import select, text

from crm_backend.db.db import SessionDep
from crm_backend.middleware.check_auth import check_auth_M
from crm_backend.middleware.request_loger import request_logger_M
from crm_backend.models.crm_http_exception import CrmHTTPException
from crm_backend.models.customer import Customer
from crm_backend.models.email_task import (
    BatchEmailTaskRequest,
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
    find_customer = session.exec(
        select(Customer).where(Customer.email == email_task.send_to)
    ).first()

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
@email_router.post("/batch_add", response_model=CrmResponse)
def create_batch_email_tasks(
    request: Request, batch_request: BatchEmailTaskRequest, session: SessionDep
):
    created_tasks = []
    skipped_emails = []
    processed_emails = set()  # 用于去重

    try:
        # 1. 按标签获取客户 - 使用简化的查询方法
        customers_by_tags = []
        if batch_request.send_customer_by_tags:
            print(f"开始按标签查询客户: {batch_request.send_customer_by_tags}")

            # 首先获取所有客户，然后在Python中过滤
            print("使用Python过滤方法查询标签客户...")
            all_customers_for_tags = session.exec(select(Customer)).all()
            print(f"数据库中总共有 {len(all_customers_for_tags)} 个客户")

            for tag in batch_request.send_customer_by_tags:
                print(f"正在查找标签: '{tag}'")
                tag_customers = []

                for customer in all_customers_for_tags:
                    if customer.tags:
                        # 检查标签是否匹配
                        if isinstance(customer.tags, list):
                            if tag in customer.tags:
                                tag_customers.append(customer)
                                print(f"  ✅ 客户 {customer.email} 匹配标签 '{tag}'")
                        elif isinstance(customer.tags, str):
                            # 尝试解析JSON字符串
                            try:
                                import json

                                tags_list = json.loads(customer.tags)
                                if isinstance(tags_list, list) and tag in tags_list:
                                    tag_customers.append(customer)
                                    print(
                                        f"  ✅ 客户 {customer.email} 匹配标签 '{tag}' (JSON解析)"
                                    )
                            except json.JSONDecodeError:
                                # 如果不是JSON，尝试字符串包含
                                if tag in customer.tags:
                                    tag_customers.append(customer)
                                    print(
                                        f"  ✅ 客户 {customer.email} 匹配标签 '{tag}' (字符串包含)"
                                    )
                            except Exception as e:
                                print(
                                    f"  ❌ 解析客户 {customer.email} 的标签时出错: {e}"
                                )
                        else:
                            print(
                                f"  ⚠️ 客户 {customer.email} 的标签格式未知: {type(customer.tags)}"
                            )
                    else:
                        print(f"  ❌ 客户 {customer.email} 没有标签")

                print(f"标签 '{tag}' 找到 {len(tag_customers)} 个客户")
                customers_by_tags.extend(tag_customers)

        # 2. 按邮箱获取客户
        customers_by_emails = []
        if batch_request.send_customer_by_emails:
            try:
                customers = session.exec(
                    select(Customer).where(
                        Customer.email.in_(batch_request.send_customer_by_emails)  # type: ignore
                    )
                ).all()
                customers_by_emails.extend(customers)
                print(f"按邮箱查询找到 {len(customers_by_emails)} 个客户")
            except Exception as e:
                print(f"按邮箱查询客户时出错: {e}")
                raise CrmHTTPException(
                    status_code=500, detail=f"查询客户信息失败: {str(e)}"
                )

        # 3. 合并所有客户并去重（基于邮箱地址）
        all_customers = []
        for customer in customers_by_tags + customers_by_emails:
            if customer.email not in processed_emails:
                all_customers.append(customer)
                processed_emails.add(customer.email)

        print(f"标签查询找到: {len(customers_by_tags)} 个客户")
        print(f"邮箱查询找到: {len(customers_by_emails)} 个客户")
        print(f"去重后总共: {len(all_customers)} 个客户")

        if not all_customers:
            # 提供更详细的错误信息
            error_msg = f"未找到符合条件的客户。"
            if batch_request.send_customer_by_tags:
                error_msg += f" 请求的标签: {batch_request.send_customer_by_tags}"
            if batch_request.send_customer_by_emails:
                error_msg += f" 请求的邮箱: {batch_request.send_customer_by_emails}"
            error_msg += (
                f" 数据库中总共有 {len(session.exec(select(Customer)).all())} 个客户。"
            )

            raise CrmHTTPException(status_code=404, detail=error_msg)

        # 4. 为每个客户创建邮件任务
        for customer in all_customers:
            # 检查客户是否在黑名单中
            if customer.is_blacklist:
                skipped_emails.append(
                    {"email": customer.email, "reason": "客户在黑名单中"}
                )
                continue

            # 创建邮件任务，将 Email 对象转换为字典
            email_task = EmailTask(
                name=batch_request.name,
                email=batch_request.email.dict(),
                send_by=request.state.user_email,
                send_to=customer.email,
                status="待处理",
            )

            session.add(email_task)
            created_tasks.append(email_task)

        # 5. 提交所有任务
        session.commit()

        # 6. 刷新所有任务以获取ID
        for task in created_tasks:
            session.refresh(task)
            # 添加到任务执行器
            email_task_execer.add_task(task)

        # 7. 返回结果
        result = {
            "created_tasks": [task.model_dump() for task in created_tasks],
            "total_created": len(created_tasks),
            "skipped_emails": skipped_emails,
            "total_skipped": len(skipped_emails),
            "total_customers_found": len(all_customers),
            "debug_info": {
                "customers_by_tags": len(customers_by_tags),
                "customers_by_emails": len(customers_by_emails),
                "tags_requested": batch_request.send_customer_by_tags,
                "emails_requested": batch_request.send_customer_by_emails,
                "total_customers_in_db": len(session.exec(select(Customer)).all()),
            },
        }

        return CrmResponse(
            data=result,
            msg=f"批量创建邮件任务成功，共创建 {len(created_tasks)} 个任务，跳过 {len(skipped_emails)} 个黑名单客户",
        )

    except CrmHTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        session.rollback()
        print(f"批量创建邮件任务时发生未知错误: {e}")
        raise CrmHTTPException(
            status_code=500, detail=f"批量创建邮件任务失败: {str(e)}"
        )


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
