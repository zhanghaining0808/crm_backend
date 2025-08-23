from fastapi import Request

from crm_backend.models.crm_http_exception import CrmHTTPException
from crm_backend.utils.jwt import jwt_decode


def check_auth_M(request: Request):
    # X-Auth-Token随便取的, 可以任意修改
    token = request.headers.get("X-Auth-Token", None)
    if not token:
        raise CrmHTTPException(status_code=400, detail="授权token不存在, 拒绝访问!!!")

    # 只判断是否没过期合法, 解析出来的值暂时用不上, 用_表示忽略
    is_valid, decodedata = jwt_decode(token)

    if not is_valid:
        raise CrmHTTPException(status_code=400, detail="授权token合法, 拒绝访问!!!")

    if not decodedata:
        raise CrmHTTPException(status_code=400, detail="授权token解析失败, 拒绝访问!!!")

    request.state.user_id = decodedata.get("user_id", None)
    request.state.user_email = decodedata.get("user_email", None)
    request.state.username = decodedata.get("username", None)
    request.state.is_admin = decodedata.get("is_admin", None)

    return request
