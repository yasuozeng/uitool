"""
数据库测试 Fixtures
提供测试用的数据库引擎、会话和模型工厂函数
"""
# 导入 pytest 异步支持
import pytest
# 导入异步会话和引擎工厂
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# 从 sqlalchemy.orm 导入会话
from sqlalchemy.orm import Session
# 从本地模型模块导入所有 ORM 模型
from app.models.case import TestCase, TestStep
from app.models.execution import Execution, ExecutionDetail
# 从本地数据库模块导入 Base 基类
from app.models.database import Base
# 从 datetime 模块导入 datetime 类
from datetime import datetime


# 定义创建测试数据库引擎的 fixture
@pytest.fixture(scope="session")
async def db_engine():
    """
    创建内存数据库引擎

    使用 SQLite 内存数据库进行测试，每个会话（session scope）创建一次
    所有测试函数共享同一个引擎实例，但使用不同的会话（通过 db_session fixture）
    """
    # 创建异步引擎，使用内存 SQLite 数据库
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",  # 内存数据库 URL
        echo=False,  # 不打印 SQL 语句
        future=True,  # 使用 SQLAlchemy 2.0 风格 API
    )

    # 创建所有表结构
    async with engine.begin() as conn:
        # 在事务中同步执行表的创建
        await conn.run_sync(Base.metadata.create_all)

    # 生成引擎给测试使用
    yield engine

    # 测试结束后释放引擎
    await engine.dispose()


# 定义创建数据库会话的 fixture
@pytest.fixture(scope="function")
async def db_session(db_engine):
    """
    创建数据库会话（自动回滚）

    每个测试函数使用独立的会话，测试结束后自动回滚所有更改
    这样可以保证每个测试之间的数据隔离，不会相互影响
    """
    # 创建异步会话工厂
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # 使用上下文管理器创建会话
    async with async_session_maker() as session:
        # 开始嵌套事务（SAVEPOINT）
        await session.begin_nested()

        # 生成会话给测试使用
        yield session

        # 测试结束后回滚事务（撤销所有更改）
        await session.rollback()


# ========== 模型工厂函数 ==========

# 定义创建测试用例工厂函数
def create_test_case_factory(
    name: str = "测试用例",
    description: str = "这是一个测试用例",
    priority: str = "P1",
    tags: str = "smoke",
    id: int = None
) -> TestCase:
    """
    创建测试用例模型对象

    Args:
        name: 用例名称
        description: 用例描述
        priority: 优先级
        tags: 标签
        id: 指定 ID（可选）

    Returns:
        TestCase 对象（未持久化到数据库）
    """
    # 创建用例对象
    case = TestCase(
        name=name,
        description=description,
        priority=priority,
        tags=tags,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    # 如果指定了 ID，手动设置（仅用于测试）
    if id is not None:
        case.id = id
    return case


# 定义创建测试步骤工厂函数
def create_test_step_factory(
    case_id: int = 1,
    step_order: int = 1,
    action_type: str = "navigate",
    element_locator: str = "#button",
    locator_type: str = "css",
    action_params: dict = None,
    expected_result: str = "页面跳转成功",
    description: str = "打开首页",
    id: int = None
) -> TestStep:
    """
    创建测试步骤模型对象

    Args:
        case_id: 所属用例 ID
        step_order: 步骤顺序
        action_type: 操作类型
        element_locator: 元素定位符
        locator_type: 定位类型
        action_params: 操作参数字典
        expected_result: 期望结果
        description: 步骤描述
        id: 指定 ID（可选）

    Returns:
        TestStep 对象（未持久化到数据库）
    """
    # 创建步骤对象
    step = TestStep(
        case_id=case_id,
        step_order=step_order,
        action_type=action_type,
        element_locator=element_locator,
        locator_type=locator_type,
        expected_result=expected_result,
        description=description,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    # 如果提供了参数，转换为 JSON 字符串存储
    if action_params:
        step.set_params(action_params)
    # 如果指定了 ID，手动设置
    if id is not None:
        step.id = id
    return step


# 定义创建执行记录工厂函数
def create_execution_factory(
    execution_type: str = "batch",
    browser_type: str = "chrome",
    headless: bool = True,
    window_size: str = "1920x1080",
    total_count: int = 1,
    status: str = "pending",
    id: int = None
) -> Execution:
    """
    创建执行记录模型对象

    Args:
        execution_type: 执行类型（single/batch）
        browser_type: 浏览器类型
        headless: 无头模式
        window_size: 窗口大小
        total_count: 总用例数
        status: 执行状态
        id: 指定 ID（可选）

    Returns:
        Execution 对象（未持久化到数据库）
    """
    # 创建执行记录对象
    execution = Execution(
        execution_type=execution_type,
        browser_type=browser_type,
        headless=headless,
        window_size=window_size,
        total_count=total_count,
        status=status,
        start_time=datetime.now(),
        created_at=datetime.now(),
    )
    # 如果指定了 ID，手动设置
    if id is not None:
        execution.id = id
    return execution


# 定义创建执行详情工厂函数
def create_execution_detail_factory(
    execution_id: int = 1,
    case_id: int = 1,
    case_name: str = "测试用例",
    status: str = "success",
    error_message: str = None,
    screenshot_path: str = None,
    step_logs: list = None,
    duration: int = 1000,
    id: int = None
) -> ExecutionDetail:
    """
    创建执行详情模型对象

    Args:
        execution_id: 所属执行记录 ID
        case_id: 用例 ID
        case_name: 用例名称
        status: 执行状态
        error_message: 错误消息
        screenshot_path: 截图路径
        step_logs: 步骤日志列表
        duration: 执行时长（毫秒）
        id: 指定 ID（可选）

    Returns:
        ExecutionDetail 对象（未持久化到数据库）
    """
    # 创建执行详情对象
    detail = ExecutionDetail(
        execution_id=execution_id,
        case_id=case_id,
        case_name=case_name,
        status=status,
        error_message=error_message,
        screenshot_path=screenshot_path,
        duration=duration,
        start_time=datetime.now(),
        end_time=datetime.now(),
        created_at=datetime.now(),
    )
    # 如果提供了日志，转换为 JSON 字符串存储
    if step_logs:
        detail.set_logs(step_logs)
    # 如果指定了 ID，手动设置
    if id is not None:
        detail.id = id
    return detail
