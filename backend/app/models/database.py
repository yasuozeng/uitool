"""
数据库连接和会话管理
配置 SQLAlchemy 异步引擎和会话工厂
"""
# 从 sqlalchemy.ext.asyncio 导入异步会话、引擎创建器和会话工厂
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# 从 sqlalchemy.orm 导入声明式基类
from sqlalchemy.orm import DeclarativeBase
# 从本地配置模块导入数据库连接 URL
from app.config import DATABASE_URL

# 创建异步数据库引擎，用于连接 SQLite 数据库
engine = create_async_engine(
    DATABASE_URL,  # 数据库连接字符串，从配置文件读取
    echo=False,  # 是否打印 SQL 语句，False 不打印（开发时可设为 True 调试）
    future=True,  # 使用 SQLAlchemy 2.0 风格的 API
)

# 创建异步会话工厂，用于生成数据库会话
AsyncSessionLocal = async_sessionmaker(
    engine,  # 绑定到上面创建的引擎
    class_=AsyncSession,  # 指定会话类为异步会话
    expire_on_commit=False,  # 提交后不过期对象，允许访问提交后的数据
    autocommit=False,  # 不自动提交，需手动控制事务
    autoflush=False,  # 不自动刷新，手动控制何时发送 SQL 到数据库
)


# 声明式基类，所有 ORM 模型都继承此类
class Base(DeclarativeBase):
    """
    所有 ORM 模型的基类

    继承此类后，子类会被 SQLAlchemy 识别为数据模型
    """
    pass  # 基类无需额外实现


# 定义获取数据库会话的依赖注入函数
async def get_db() -> AsyncSession:
    """
    获取数据库会话

    用于 FastAPI 依赖注入，在每个请求中提供数据库会话

    Yields:
        AsyncSession: 数据库会话对象

    Examples:
        在 API 路由中使用：
        @app.get("/cases")
        async def get_cases(db: AsyncSession = Depends(get_db)):
            ...
    """
    # 使用异步上下文管理器创建会话
    async with AsyncSessionLocal() as session:
        try:
            # 生成会话给请求使用
            yield session
        finally:
            # 无论请求成功或失败，都关闭会话释放资源
            await session.close()


# 定义初始化数据库函数
async def init_db():
    """
    初始化数据库，创建所有表

    在应用启动时调用，根据已定义的 ORM 模型创建数据库表结构
    如果表已存在则跳过（不会删除已有数据）

    Examples:
        在 FastAPI lifespan 中调用：
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await init_db()
            yield
    """
    # 使用异步上下文管理器获取数据库连接
    async with engine.begin() as conn:
        # 在事务中同步执行表的创建（run_sync 用于在异步上下文中运行同步函数）
        await conn.run_sync(Base.metadata.create_all)


# 定义关闭数据库连接函数
async def close_db():
    """
    关闭数据库连接

    在应用关闭时调用，释放数据库连接池资源

    Examples:
        在 FastAPI lifespan 中调用：
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await init_db()
            yield
            await close_db()
    """
    # 释放数据库引擎及其连接池
    await engine.dispose()
