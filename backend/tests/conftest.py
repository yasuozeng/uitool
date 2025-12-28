"""
全局 pytest 配置和 fixtures
"""
# 导入 pytest 测试框架，用于编写和运行测试
import pytest
# 导入 asyncio 异步库，用于异步测试支持
import asyncio
# 导入 Path 路径处理类，用于文件路径操作
from pathlib import Path

# 获取项目根目录：当前文件的上上级目录（backend 目录）
BASE_DIR = Path(__file__).resolve().parent.parent

# 导入数据库 fixtures（使所有测试都可以使用 db_session 和 db_engine）
from tests.fixtures.db_fixtures import db_session, db_engine
# 导入引擎 fixtures
from tests.fixtures.engine_fixtures import mock_playwright


@pytest.fixture(scope="session")  # fixture 作用域为整个测试会话（所有测试共享）
def event_loop():
    """创建事件循环（用于异步测试）"""
    # 创建新的事件循环对象
    loop = asyncio.new_event_loop()
    # 将事件循环提供给测试使用（yield 前是 setup）
    yield loop
    # 测试结束后关闭事件循环（yield 后是 teardown）
    loop.close()


@pytest.fixture(scope="session")  # fixture 作用域为整个测试会话
def project_root():
    """项目根目录"""
    # 返回项目根目录路径对象
    return BASE_DIR


# 配置 pytest-asyncio：使用 auto 模式，自动为异步测试函数添加事件循环
pytest_plugins = ('pytest_asyncio',)
