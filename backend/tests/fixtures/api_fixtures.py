"""
API 测试 Fixtures
提供测试用的 FastAPI 客户端、数据库会话覆盖和 Mock 对象
"""
# 导入 pytest 测试框架
import pytest
# 从 fastapi.testclient 导入测试客户端
from fastapi.testclient import TestClient
# 从 sqlalchemy.ext.asyncio 导入异步会话
from sqlalchemy.ext.asyncio import AsyncSession
# 从 unittest.mock 导入模拟对象类
from unittest.mock import MagicMock, AsyncMock
# 从 typing 模块导入类型注解
from typing import Generator

# 导入数据库 fixtures（复用数据库引擎和会话）
from tests.fixtures.db_fixtures import db_session, db_engine

# 导入 FastAPI 应用和数据库依赖
from app.main import app
from app.models.database import get_db

# 导入需要 Mock 的引擎类
from app.engines.playwright_engine import PlaywrightEngine


# 定义创建测试客户端的 fixture
@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """
    创建 FastAPI 测试客户端

    使用依赖注入覆盖，将真实的数据库会话替换为测试会话
    这样测试中的数据库操作会使用自动回滚的内存数据库

    Args:
        db_session: 数据库会话 fixture（自动回滚）

    Yields:
        TestClient: FastAPI 测试客户端实例
    """
    # 定义覆盖函数，返回测试数据库会话
    async def override_get_db():
        """覆盖数据库依赖注入"""
        yield db_session

    # 使用测试会话覆盖原始的 get_db 依赖
    app.dependency_overrides[get_db] = override_get_db

    # 创建测试客户端（不会启动真实的服务器）
    with TestClient(app) as test_client:
        # 生成测试客户端给测试使用
        yield test_client

    # 测试结束后清除依赖注入覆盖
    app.dependency_overrides.clear()


# 定义 Mock PlaywrightEngine 的 fixture
@pytest.fixture
def mock_playwright_engine() -> MagicMock:
    """
    创建 Mock PlaywrightEngine

    用于在服务层测试中模拟 Playwright 引擎行为
    避免测试时真实启动浏览器

    Returns:
        MagicMock: 模拟的 PlaywrightEngine 对象
    """
    # 创建 Mock 对象
    mock = MagicMock(spec=PlaywrightEngine)

    # 配置异步方法为 AsyncMock
    mock.start_browser = AsyncMock(return_value=None)
    mock.close_browser = AsyncMock(return_value=None)

    # 配置 execute_case 方法返回成功结果
    mock.execute_case = AsyncMock(return_value={
        "success": True,
        "total_steps": 1,
        "success_steps": 1,
        "failed_steps": 0,
        "step_results": [
            {
                "step_order": 1,
                "action_type": "navigate",
                "success": True,
                "message": "成功跳转到 https://example.com"
            }
        ]
    })

    # 配置 take_screenshot_on_error 方法返回截图路径
    mock.take_screenshot_on_error = AsyncMock(return_value="/screenshots/error_001.png")

    # 生成 Mock 对象给测试使用
    return mock


# 定义执行记录样本数据的 fixture
@pytest.fixture
def sample_execution_data():
    """
    执行记录样本数据

    用于测试执行相关的 API 和服务

    Returns:
        dict: 执行记录请求数据
    """
    return {
        "execution_type": "batch",
        "browser_type": "chrome",
        "headless": True,
        "window_size": "1920x1080",
        "case_ids": [1, 2, 3]
    }


# 定义单个执行样本数据的 fixture
@pytest.fixture
def sample_single_execution_data():
    """
    单个执行样本数据

    用于测试单个用例执行

    Returns:
        dict: 执行记录请求数据
    """
    return {
        "execution_type": "single",
        "browser_type": "firefox",
        "headless": False,
        "window_size": "1366x768",
        "case_ids": [1]
    }


# 定义用例样本数据的 fixture
@pytest.fixture
def sample_case_data():
    """
    用例样本数据

    用于测试用例相关的 API 和服务

    Returns:
        dict: 用例请求数据
    """
    return {
        "name": "登录测试",
        "description": "测试用户登录功能",
        "priority": "P1",
        "tags": "auth,smoke",
        "steps": [
            {
                "step_order": 1,
                "action_type": "navigate",
                "action_params": {"url": "https://example.com/login"}
            },
            {
                "step_order": 2,
                "action_type": "input",
                "element_locator": "#username",
                "locator_type": "css",
                "action_params": {"text": "testuser"}
            },
            {
                "step_order": 3,
                "action_type": "input",
                "element_locator": "#password",
                "locator_type": "css",
                "action_params": {"text": "testpass"}
            },
            {
                "step_order": 4,
                "action_type": "click",
                "element_locator": "button[type='submit']",
                "locator_type": "css"
            },
            {
                "step_order": 5,
                "action_type": "verify_text",
                "action_params": {"text": "欢迎"}
            }
        ]
    }


# 定义用例更新样本数据的 fixture
@pytest.fixture
def sample_case_update_data():
    """
    用例更新样本数据

    用于测试用例更新功能

    Returns:
        dict: 用例更新请求数据
    """
    return {
        "name": "登录测试（已更新）",
        "description": "更新后的描述",
        "priority": "P0",
        "tags": "auth,critical"
    }


# 定义批量删除样本数据的 fixture
@pytest.fixture
def sample_batch_delete_data():
    """
    批量删除样本数据

    用于测试批量删除功能

    Returns:
        dict: 批量删除请求数据
    """
    return {
        "case_ids": [1, 2, 3, 4, 5]
    }


# ========================================
# 报告接口测试 Fixtures
# ========================================

# 定义临时报告目录的 fixture
@pytest.fixture
def temp_reports_dir(tmp_path):
    """
    临时报告目录

    用于测试报告生成和下载功能
    每个测试使用独立的临时目录，测试结束后自动清理

    Args:
        tmp_path: pytest 提供的临时路径 fixture

    Returns:
        Path: 临时报告目录路径
    """
    # 创建临时报告目录
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(exist_ok=True)
    return reports_dir


# 定义示例报告文件的 fixture
@pytest.fixture
def sample_report_file(temp_reports_dir):
    """
    示例报告文件

    创建一个用于测试的 HTML 报告文件

    Args:
        temp_reports_dir: 临时报告目录 fixture

    Returns:
        str: 报告文件名
    """
    # 生成报告文件名（使用固定时间戳便于测试）
    report_filename = "report_1_20251228.html"
    report_path = temp_reports_dir / report_filename

    # 写入示例 HTML 内容
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>测试报告</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>uiTool1.0 测试报告</h1>
        <div class="summary">
            <p>执行时间: 2025-12-28 12:00:00</p>
            <p>用例总数: 10</p>
            <p>成功: 8</p>
            <p>失败: 2</p>
        </div>
    </body>
    </html>
    """
    report_path.write_text(html_content.strip(), encoding='utf-8')

    return report_filename


# 定义多个示例报告文件的 fixture
@pytest.fixture
def sample_report_files(temp_reports_dir):
    """
    多个示例报告文件

    创建多个不同时间的报告文件，用于测试列表查询和排序

    Args:
        temp_reports_dir: 临时报告目录 fixture

    Returns:
        list: 报告文件名列表
    """
    # 创建多个报告文件
    report_files = []

    # 报告 1（最早）
    report1_name = "report_1_20251228_100000.html"
    (temp_reports_dir / report1_name).write_text(
        f"<html><body>报告1 - 2025-12-28 10:00:00</body></html>",
        encoding='utf-8'
    )
    report_files.append(report1_name)

    # 报告 2（中间）
    report2_name = "report_2_20251228_120000.html"
    (temp_reports_dir / report2_name).write_text(
        f"<html><body>报告2 - 2025-12-28 12:00:00</body></html>",
        encoding='utf-8'
    )
    report_files.append(report2_name)

    # 报告 3（最新）
    report3_name = "report_3_20251228_140000.html"
    (temp_reports_dir / report3_name).write_text(
        f"<html><body>报告3 - 2025-12-28 14:00:00</body></html>",
        encoding='utf-8'
    )
    report_files.append(report3_name)

    return report_files


# 定义包含截图的报告文件 fixture
@pytest.fixture
def sample_report_with_screenshots(temp_reports_dir):
    """
    包含截图引用的报告文件

    创建一个引用了截图的 HTML 报告，用于测试报告包含截图功能

    Args:
        temp_reports_dir: 临时报告目录 fixture

    Returns:
        str: 报告文件名
    """
    # 创建截图目录和文件
    screenshots_dir = temp_reports_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

    # 创建示例截图文件（使用模拟的 PNG 数据）
    screenshot_path = screenshots_dir / "error_screenshot_1.png"
    # 模拟 PNG 文件数据（头部 + 简单内容）
    png_data = b"\x89PNG\r\n\x1a\n...simulated PNG data"
    screenshot_path.write_bytes(png_data)

    # 创建包含截图引用的报告
    report_filename = "report_with_screenshots.html"
    report_path = temp_reports_dir / report_filename

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>包含截图的报告</title></head>
    <body>
        <h1>测试报告</h1>
        <div class="failure">
            <p>步骤失败</p>
            <img src="../screenshots/{screenshot_path.name}" alt="错误截图" />
        </div>
    </body>
    </html>
    """
    report_path.write_text(html_content.strip(), encoding='utf-8')

    return report_filename


# 定义 Mock 报告服务的 fixture
@pytest.fixture
def mock_report_service():
    """
    Mock 报告服务

    模拟 report_service 的行为，避免测试时实际生成报告文件

    Returns:
        AsyncMock: 模拟的报告服务对象
    """
    from unittest.mock import AsyncMock, patch
    from datetime import datetime

    # 创建 Mock 对象
    with patch('app.api.reports.report_service') as mock:
        # 配置 generate_report 方法
        async def mock_generate(execution_id, include_screenshots=True, include_logs=True):
            """模拟生成报告"""
            # 返回生成的报告信息
            return {
                "report_id": f"report_{execution_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "execution_id": execution_id,
                "html_path": f"/reports/report_{execution_id}.html",
                "download_url": f"/api/v1/reports/download/report_{execution_id}.html",
                "include_screenshots": include_screenshots,
                "include_logs": include_logs,
                "generated_at": datetime.now().isoformat()
            }

        # 配置 get_report_list 方法
        async def mock_get_list():
            """模拟获取报告列表"""
            return [
                {
                    "filename": "report_1_20251228.html",
                    "size": 1024,
                    "created_at": "2025-12-28T10:00:00"
                },
                {
                    "filename": "report_2_20251228.html",
                    "size": 2048,
                    "created_at": "2025-12-28T12:00:00"
                }
            ]

        # 设置异步方法
        mock.generate_report = mock_generate
        mock.get_report_list = mock_get_list

        yield mock


# ========================================
# 基础接口测试 Fixtures
# ========================================

# 定义示例截图文件的 fixture
@pytest.fixture
def sample_screenshot_file(tmp_path):
    """
    示例截图文件

    创建一个用于测试的 PNG 截图文件

    Args:
        tmp_path: pytest 提供的临时路径 fixture

    Returns:
        tuple: (截图目录路径, 截图文件名)
    """
    # 创建截图目录
    screenshots_dir = tmp_path / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

    # 创建示例 PNG 文件（模拟真实的 PNG 头部）
    screenshot_filename = "test_screenshot_1.png"
    screenshot_path = screenshots_dir / screenshot_filename

    # 写入模拟的 PNG 数据（PNG 文件头部 + 简单内容）
    png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82"
    screenshot_path.write_bytes(png_data)

    return screenshots_dir, screenshot_filename


# 定义健康检查响应时间阈值 fixture
@pytest.fixture
def health_check_response_time_threshold():
    """
    健康检查响应时间阈值（毫秒）

    用于验证健康检查接口的响应时间性能

    Returns:
        int: 响应时间阈值（毫秒）
    """
    return 100  # 100毫秒
