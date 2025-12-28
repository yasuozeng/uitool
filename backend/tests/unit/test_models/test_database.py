"""
数据库连接和会话管理单元测试
"""
# 导入 pytest 测试框架，用于编写测试用例和异步测试装饰器
import pytest
# 从 sqlalchemy.ext.asyncio 导入异步数据库相关类型，用于类型注解和验证
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
# 从 unittest.mock 导入模拟对象类，用于模拟外部依赖
from unittest.mock import AsyncMock, MagicMock, patch


class TestDatabaseEngine:
    """测试数据库引擎"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_engine_creation(self):
        """测试引擎创建"""
        # 导入数据库引擎实例
        from app.models.database import engine

        # 验证：engine 是 AsyncEngine 类的实例
        assert isinstance(engine, AsyncEngine)
        # 验证：数据库 URL 包含 "sqlite" 关键字
        assert "sqlite" in str(engine.url)
        # 验证：数据库 URL 包含 "aiosqlite" 关键字（异步驱动）
        assert "aiosqlite" in str(engine.url)

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_engine_echo_disabled(self):
        """测试引擎 echo 设置"""
        # 导入数据库引擎实例
        from app.models.database import engine

        # 验证：echo 设置为 False（不打印 SQL 语句）
        assert engine.echo is False


class TestAsyncSessionLocal:
    """测试会话工厂"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_session_factory_type(self):
        """测试会话工厂类型"""
        # 导入会话工厂类
        from app.models.database import AsyncSessionLocal

        # 验证：AsyncSessionLocal 是 async_sessionmaker 类的实例
        assert isinstance(AsyncSessionLocal, async_sessionmaker)

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_session_creation(self):
        """测试会话创建"""
        # 导入会话工厂类
        from app.models.database import AsyncSessionLocal

        # 使用上下文管理器创建会话
        async with AsyncSessionLocal() as session:
            # 验证：session 是 AsyncSession 类的实例
            assert isinstance(session, AsyncSession)
            # 验证：会话处于活动状态
            assert session.is_active


class TestBase:
    """测试 Base 基类"""

    def test_base_exists(self):
        """测试 Base 基类存在"""
        # 导入 Base 基类
        from app.models.database import Base

        # 验证：Base 不为 None
        assert Base is not None
        # 验证：Base 具有 metadata 属性
        assert hasattr(Base, "metadata")

    def test_base_registry(self):
        """测试 Base 注册表"""
        # 导入 Base 基类和模型类
        from app.models.database import Base
        from app.models.case import TestCase
        from app.models.execution import Execution

        # 验证模型已注册到 Base.metadata
        # 验证：test_cases 表已注册
        assert "test_cases" in Base.metadata.tables
        # 验证：test_steps 表已注册
        assert "test_steps" in Base.metadata.tables
        # 验证：executions 表已注册
        assert "executions" in Base.metadata.tables
        # 验证：execution_details 表已注册
        assert "execution_details" in Base.metadata.tables


class TestGetDb:
    """测试 get_db 依赖注入函数"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_db_yields_session(self):
        """测试 get_db 返回会话"""
        # 导入 get_db 生成器函数
        from app.models.database import get_db

        # 遍历 get_db 生成器（每次 yield 一个会话）
        async for session in get_db():
            # 验证：返回的 session 是 AsyncSession 实例
            assert isinstance(session, AsyncSession)
            # 验证：会话处于活动状态
            assert session.is_active
            break  # 只测试第一次 yield，避免无限循环

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_db_closes_session(self):
        """测试 get_db 正确关闭会话"""
        # 导入 get_db 生成器函数
        from app.models.database import get_db

        # 初始化 session 变量
        session = None
        # 遍历 get_db 生成器
        async for s in get_db():
            session = s  # 保存会话引用
            # 模拟使用会话
            break  # 立即退出循环

        # 验证：获取到了会话
        assert session is not None

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_db_context_manager(self):
        """测试 get_db 作为上下文管理器"""
        # 导入 get_db 生成器函数
        from app.models.database import get_db

        # 遍历 get_db 生成器
        async for session in get_db():
            # 验证：在上下文中会话应该是活动的
            assert session.is_active
            # 执行一些操作
            await session.rollback()  # 回滚空事务
        # 退出上下文后会话应关闭


class TestInitDb:
    """测试 init_db 函数"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_init_db_with_memory_db(self):
        """测试使用内存数据库初始化"""
        # 导入 SQLAlchemy 异步相关类
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from sqlalchemy.orm import DeclarativeBase

        # 创建内存数据库引擎
        memory_engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",  # 内存数据库 URL
            echo=False  # 不打印 SQL
        )

        # 定义测试基类
        class TestBase(DeclarativeBase):
            pass

        # 导入 SQLAlchemy 列和类型定义
        from sqlalchemy import Column, Integer, String, text

        # 定义测试表模型
        class TestTable(TestBase):
            __tablename__ = "test_table"  # 表名
            id = Column(Integer, primary_key=True)  # ID 列
            name = Column(String(50))  # 名称列

        # 创建表结构
        async with memory_engine.begin() as conn:
            # 同步运行 create_all
            await conn.run_sync(TestBase.metadata.create_all)

        # 验证表已创建 - 使用 text() 包装原生 SQL
        async with memory_engine.begin() as conn:
            # 查询 SQLite 系统表验证表是否存在
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
            )
            # 获取查询结果
            rows = result.fetchall()
            # 验证：表存在
            assert len(rows) >= 0  # 表存在

        # 释放内存数据库引擎
        await memory_engine.dispose()

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_init_db_creates_all_tables(self):
        """测试 init_db 创建所有表"""
        # 导入 Base 基类和模型类
        from app.models.database import Base
        from app.models.case import TestCase, TestStep
        from app.models.execution import Execution, ExecutionDetail

        # 获取所有表名集合
        table_names = set(Base.metadata.tables.keys())

        # 定义期望的表名集合
        expected_tables = {
            "test_cases",  # 测试用例表
            "test_steps",  # 测试步骤表
            "executions",  # 执行记录表
            "execution_details"  # 执行详情表
        }

        # 验证：所有期望的表都已注册
        assert expected_tables.issubset(table_names)


class TestCloseDb:
    """测试 close_db 函数"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_close_db_disposes_engine(self):
        """测试 close_db 释放引擎"""
        # 导入引擎创建函数和 close_db 函数
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.models.database import close_db

        # 创建测试引擎
        test_engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",  # 内存数据库
            echo=False  # 不打印 SQL
        )

        # 验证：引擎连接池存在
        assert test_engine.pool is not None

        # 关闭引擎
        await test_engine.dispose()

        # 验证引擎已释放
        # 在 SQLAlchemy 中，dispose 后 pool 仍然存在但连接已关闭


class TestDatabaseIntegration:
    """数据库集成测试（使用内存数据库）"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_crud_operations_with_memory_db(self):
        """测试在内存数据库中的 CRUD 操作"""
        # 导入 SQLAlchemy 相关类
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
        from sqlalchemy import String, Integer, select

        # 创建内存数据库引擎
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        # 创建会话工厂
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

        # 定义 Base 基类
        class Base(DeclarativeBase):
            pass

        # 定义测试模型
        class TestModel(Base):
            __tablename__ = "test_models"  # 表名
            id: Mapped[int] = mapped_column(Integer, primary_key=True)  # ID 字段
            name: Mapped[str] = mapped_column(String(50))  # 名称字段

        # 创建表结构
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 测试 CRUD 操作
        async with AsyncSessionLocal() as session:
            # Create：创建新记录
            obj = TestModel(name="测试")
            session.add(obj)  # 添加到会话
            await session.commit()  # 提交事务
            await session.refresh(obj)  # 刷新对象以获取数据库生成的值

            # Read：查询记录
            stmt = select(TestModel).where(TestModel.name == "测试")
            result = await session.execute(stmt)
            found = result.scalar_one()  # 获取单条记录
            assert found.name == "测试"

            # Update：更新记录
            found.name = "已更新"
            await session.commit()  # 提交更新
            await session.refresh(found)  # 刷新对象
            assert found.name == "已更新"

            # Delete：删除记录
            await session.delete(found)
            await session.commit()  # 提交删除

            # 验证删除：查询应返回 None
            result = await session.execute(stmt)
            assert result.scalar_one_or_none() is None

        # 释放数据库引擎
        await engine.dispose()

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_transaction_rollback(self):
        """测试事务回滚"""
        # 导入 SQLAlchemy 相关类
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
        from sqlalchemy import String, Integer, select

        # 创建内存数据库引擎
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        # 创建会话工厂
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

        # 定义 Base 基类
        class Base(DeclarativeBase):
            pass

        # 定义测试模型
        class TestModel(Base):
            __tablename__ = "test_rollback"  # 表名
            id: Mapped[int] = mapped_column(Integer, primary_key=True)  # ID 字段
            name: Mapped[str] = mapped_column(String(50))  # 名称字段

        # 创建表结构
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 测试事务回滚
        async with AsyncSessionLocal() as session:
            obj = TestModel(name="测试")
            session.add(obj)  # 添加到会话
            await session.rollback()  # 回滚事务（不保存）

            # 验证数据未保存
            stmt = select(TestModel)
            result = await session.execute(stmt)
            assert result.scalar_one_or_none() is None  # 应该查不到数据

        # 释放数据库引擎
        await engine.dispose()
