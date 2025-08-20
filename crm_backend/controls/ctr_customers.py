from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from crm_backend.db.db import SessionDep
from crm_backend.models.crm_http_exception import CrmHTTPException
from crm_backend.models.customer import Customer, CustomerUpdateReq
from crm_backend.models.response import CrmResponse
from crm_backend.middleware.request_loger import request_logger_M
from crm_backend.utils.jwt import jwt_encode


customer_router = APIRouter(
    prefix="/api/customers", dependencies=[Depends(request_logger_M)]
)


# 创建客户(单个客户添加,可同时设置多个标签)
@customer_router.post("/add", response_model=CrmResponse)
def create_customer(customer: Customer, session: SessionDep):
    find_customer = session.exec(
        select(Customer).where(Customer.name == customer.name)
    ).first()
    if find_customer:
        raise CrmHTTPException(
            status_code=404, detail="相同客户名称已存在,请更换客户名"
        )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    token = jwt_encode({"customername": customer.name}, timedelta(days=1))
    return CrmResponse(
        data={"customer": customer, "access_token": token}, msg="创建用户成功"
    )


# 客户列表展示(支持分页,搜索,按标签筛选)
@customer_router.get("/query", response_model=CrmResponse)
def read_all_customers(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    customers = session.exec(select(Customer).offset(offset).limit(limit)).all()
    return CrmResponse(data=list(customers), msg="获取全部客户成功")


# 客户编辑(客户更新)
@customer_router.post("/update/{customer_id}", response_model=CrmResponse)
def update_customer(
    customer_id: int, customer_update_req: CustomerUpdateReq, session: SessionDep
):
    find_customer = session.get(Customer, customer_id)
    need_update_customer = customer_update_req.update_Customer.model_dump()
    if not find_customer:
        raise CrmHTTPException(status_code=404, detail="客户新数据未找到!")
    if not find_customer:
        raise CrmHTTPException(status_code=404, detail="客户旧数据未找到!")

    old_customer = find_customer.model_dump()
    new_customer = old_customer
    for need_update_key in customer_update_req.update_key:
        print(need_update_key)
        if need_update_key in old_customer.keys():
            new_customer[need_update_key] = need_update_customer[need_update_key]
    find_customer.sqlmodel_update(new_customer)
    session.commit()
    session.refresh(find_customer)
    return CrmResponse(data=find_customer.model_dump(), msg="更新单个客户成功")


#  客户删除
@customer_router.post("/delete/{customer_id}", response_model=CrmResponse)
def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise CrmHTTPException(status_code=404, detail="客户未找到")
    session.delete(customer)
    session.commit()
    return CrmResponse(data=customer.model_dump(), msg="删除客户成功")
