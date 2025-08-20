from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlmodel import select
from crm_backend.db.db import SessionDep
from crm_backend.models.crm_http_exception import CrmHTTPException
from crm_backend.models.customer import Customer
from crm_backend.models.response import CrmResponse
from crm_backend.middleware.request_loger import request_logger_M
from crm_backend.utils.jwt import jwt_encode


customer_router = APIRouter(
    prefix="/api/customers", dependencies=[Depends(request_logger_M)]
)


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
