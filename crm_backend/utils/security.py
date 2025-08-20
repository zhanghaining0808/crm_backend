from passlib.context import CryptContext

# 配置密码哈希方式 推荐bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_passwd(plain_passwd: str, hashed_passwd: str) -> bool:
    """验证密码是否正确"""
    return pwd_context.verify(plain_passwd, hashed_passwd)


def get_passwd_hash(passwd: str) -> str:
    """生成密码的哈希值"""
    return pwd_context.hash(passwd)
