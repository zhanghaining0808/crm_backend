# 用于加密Token的密匙(生产环境要用更复杂的值)
from datetime import datetime, timedelta
from typing import Dict
from jose import JWTError, jwt

SECRET_KEY = "abcdefg"
# 加密算法(HMAC + SHA256)
ALGORITHM = "HS256"


def jwt_encode(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()  # 复制数据 避免修改原数据
    expire = datetime.utcnow() + expires_delta  # 计算过期时间(当前时间＋有效期)
    to_encode.update({"exp": expire})  # 添加过期时间字段
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # 生成Token


def jwt_decode(token: str) -> tuple[bool, Dict | None]:
    is_valid = True
    decode_data = None
    try:
        decode_data = jwt.decode(token=token, key=SECRET_KEY)
    except JWTError:
        is_valid = False
    return is_valid, decode_data
