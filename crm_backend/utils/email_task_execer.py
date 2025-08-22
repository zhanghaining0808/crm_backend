import asyncio
import random
import threading
from typing import List
from crm_backend.db.db import engine
from sqlmodel import Session
from crm_backend.models.crm_http_exception import CrmHTTPException
from crm_backend.models.email_task import EmailTask
from loguru import logger


# 单例装饰器-确保类只有一个实例
# 避免创建多个任务执行器导致状态不一致
def singleton(cls):
    instances = {}  # 存储已创建的实例

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


# 使用单例装饰器
@singleton
class EmailTaskExecer:
    """
    任务执行器，用于处理任务的执行逻辑
    """

    def __init__(self, task_list: List[EmailTask] = []):
        self.task_list: List[EmailTask] = task_list  # 待执行的任务列表
        self._loop = None
        self._thread = None
        # 获取数据库会话，用于操作数据库数据
        self._session = Session(engine)
        self._start_background_loop()

    def _start_background_loop(self):
        """启动后台事件循环"""

        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

    def _update_task_status(self, task: EmailTask, new_status: str):
        find_email_task = self._session.get(EmailTask, task.id)
        if not find_email_task:
            raise CrmHTTPException(
                status_code=404,
                detail=f"更新Task {task.id} - {task.name}失败，数据库没有该邮件任务",
            )
        new_task = find_email_task
        new_task.status = new_status
        find_email_task.sqlmodel_update(new_task)
        self._session.commit()
        self._session.refresh(find_email_task)

    def add_task(self, task: EmailTask):
        """
        添加任务到待执行列表
        :param task: EmailTask 实例
        """
        self.task_list.append(task)
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._delayed_execute(), self._loop)
        logger.debug(f"任务队列添加任务: {task.name}")

    async def _delayed_execute(self):
        """延迟执行任务"""
        # 两秒之后开始执行任务
        await asyncio.sleep(2)  # 两秒后执行
        await self.execute()

    async def execute(self):
        # 这里可以添加任务执行的具体逻辑
        if not self.task_list:
            raise ValueError("任务列表为空，无法执行任务。")
        task = self.task_list.pop(0)  # 获取并移除第一个任务

        # 执行任务的逻辑
        # 例如发送邮件、记录日志等锁屏
        # 这里只是一个示例，实际执行逻辑需要根据业务需求来实现
        # 例如发送邮件
        logger.info(f"开始执行任务: {task.name}")
        self._update_task_status(task, "发送中")
        # 这里可以调用发送邮件的函数
        email = task.get_email()
        is_success = await self.send_email(
            email.subject,
            email.body,
            task.send_by,
            task.send_to,
        )
        if is_success:
            logger.info(f"任务 {task.name} 执行成功.")
            self._update_task_status(task, "发送成功")

        else:
            logger.error(f"任务 {task.name} 执行失败!(网络问题，请稍后重试).")
            self._update_task_status(task, "发送失败")

    async def send_email(
        self, subject: str, body: str, send_by: str, send_to: str
    ) -> bool:
        """
        模拟发送邮件的函数
        :param subject: 邮件主题
        :param body: 邮件内容
        """
        is_success = False  # 默认表示没有发送成功
        delay = random.randint(2, 10)  # 模拟发送邮件的延迟

        # 这里可以集成实际的邮件发送逻辑
        logger.info(f"邮件主题: {subject}")
        logger.info(f"邮件内容: {body}")
        logger.info(f"发送者: {send_by}")
        logger.info(f"接收者: {send_to}")

        # 模拟实际网络延迟 (2~10秒)
        await asyncio.sleep(delay)  # 模拟发送邮件的延迟

        # 模拟可能会发送成功或失败
        # 这里假设如果发送时长超过了7秒，则认定为失败
        if delay > 7:
            is_success = False
        else:
            is_success = True

        if is_success:
            return True

        return False
