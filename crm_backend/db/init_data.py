from datetime import datetime
from sqlmodel import Session, select
from crm_backend.models.user import User
from crm_backend.models.customer import Customer
from crm_backend.models.email_task import EmailTask, Email
from crm_backend.db.db import engine
from loguru import logger

from crm_backend.utils.security import get_passwd_hash


def init_sample_users():
    """初始化示例用户数据"""
    with Session(engine) as session:
        # 检查是否已有用户数据
        existing_users = session.exec(select(User)).all()
        if existing_users:
            logger.info("用户数据已存在，跳过初始化")
            return

        # 创建示例用户
        sample_users = [
            User(
                name="admin",
                passwd="admin123",  # 实际项目中应该使用加密密码
                email="admin@example.com",
                is_active=True,
                is_admin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
            ),
            User(
                name="sales1",
                passwd="sales123",
                email="sales1@example.com",
                is_active=True,
                is_admin=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
            ),
            User(
                name="marketing1",
                passwd="marketing123",
                email="marketing1@example.com",
                is_active=True,
                is_admin=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
            ),
        ]

        for user in sample_users:
            user.passwd = get_passwd_hash(user.passwd)
            session.add(user)

        session.commit()
        logger.info(f"成功创建 {len(sample_users)} 个示例用户")


def init_sample_customers():
    """初始化示例客户数据"""
    with Session(engine) as session:
        # 检查是否已有客户数据
        existing_customers = session.exec(select(Customer)).all()
        if existing_customers:
            logger.info("客户数据已存在，跳过初始化")
            return

        # 获取用户ID作为创建者
        users = session.exec(select(User)).all()
        if not users:
            logger.warning("没有找到用户，无法创建客户数据")
            return

        admin_user = next((u for u in users if u.is_admin), users[0])

        if not admin_user.id:
            return

        # 创建示例客户
        sample_customers = [
            Customer(
                name="张三",
                email="zhangsan@company.com",
                is_blacklist=False,
                created_by=admin_user.id,
                tags=["VIP客户", "企业客户"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Customer(
                name="李四",
                email="lisi@company.com",
                is_blacklist=False,
                created_by=admin_user.id,
                tags=["普通客户", "个人客户"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Customer(
                name="王五",
                email="wangwu@company.com",
                is_blacklist=False,
                created_by=admin_user.id,
                tags=["潜在客户", "企业客户"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Customer(
                name="赵六",
                email="zhaoliu@company.com",
                is_blacklist=True,
                created_by=admin_user.id,
                tags=["黑名单"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Customer(
                name="钱七",
                email="qianqi@company.com",
                is_blacklist=False,
                created_by=admin_user.id,
                tags=["VIP客户", "长期合作"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]

        for customer in sample_customers:
            session.add(customer)

        session.commit()
        logger.info(f"成功创建 {len(sample_customers)} 个示例客户")


def init_sample_email_tasks():
    """初始化示例邮件任务数据"""
    with Session(engine) as session:
        # 检查是否已有邮件任务数据
        existing_tasks = session.exec(select(EmailTask)).all()
        if existing_tasks:
            logger.info("邮件任务数据已存在，跳过初始化")
            return

        # 获取用户和客户数据
        users = session.exec(select(User)).all()
        customers = session.exec(select(Customer)).all()

        if not users or not customers:
            logger.warning("没有找到用户或客户，无法创建邮件任务数据")
            return

        admin_user = next((u for u in users if u.is_admin), users[0])

        # 创建示例邮件任务
        sample_tasks = [
            EmailTask(
                name="欢迎新客户邮件",
                status="待处理",
                send_by=admin_user.email,
                send_to="zhangsan@company.com",
                email={
                    "subject": "欢迎加入我们的大家庭！",
                    "body": "<h1>欢迎！</h1><p>感谢您选择我们的服务，我们将为您提供最优质的产品和服务。</p>",
                },
                created_at=datetime.utcnow(),
                sended_at=datetime.utcnow(),
            ),
            EmailTask(
                name="产品推广邮件",
                status="发送成功",
                send_by=admin_user.email,
                send_to="lisi@company.com",
                email={
                    "subject": "新产品上线通知",
                    "body": "<h1>新产品发布！</h1><p>我们刚刚发布了全新的产品系列，快来了解一下吧！</p>",
                },
                created_at=datetime.utcnow(),
                sended_at=datetime.utcnow(),
            ),
            EmailTask(
                name="客户关怀邮件",
                status="待处理",
                send_by=admin_user.email,
                send_to="wangwu@company.com",
                email={
                    "subject": "客户满意度调查",
                    "body": "<h1>您的意见很重要</h1><p>我们非常重视您的使用体验，请花几分钟时间完成满意度调查。</p>",
                },
                created_at=datetime.utcnow(),
                sended_at=datetime.utcnow(),
            ),
        ]

        for task in sample_tasks:
            session.add(task)

        session.commit()
        logger.info(f"成功创建 {len(sample_tasks)} 个示例邮件任务")


def init_all_sample_data():
    """初始化所有示例数据"""
    logger.info("开始初始化示例数据...")

    try:
        init_sample_users()
        init_sample_customers()
        init_sample_email_tasks()
        logger.info("所有示例数据初始化完成！")
        logger.info("默认管理员账户: admin@example.com / admin123")
        logger.info("默认销售账户: sales1@example.com / sales123")
        logger.info("默认营销账户: marketing1@example.com / marketing123")

    except Exception as e:
        logger.error(f"初始化示例数据时发生错误: {e}")
        raise
