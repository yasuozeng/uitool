"""
PlaywrightEngine 测试 fixtures
"""
# 导入 pytest 测试框架，用于创建 fixture
import pytest
# 从 unittest.mock 导入模拟对象类，用于模拟外部依赖
from unittest.mock import AsyncMock, MagicMock, Mock
# 从 playwright.async_api 导入类型注解，用于类型提示
from playwright.async_api import Browser, Page, BrowserContext, Locator


@pytest.fixture  # 标记为 pytest fixture，可在测试中作为参数使用
def mock_browser():
    """模拟 Browser 对象"""
    # 创建 AsyncMock 对象，模拟 Browser 接口的异步方法
    browser = AsyncMock(spec=Browser)
    # 模拟 close 异步方法，用于关闭浏览器
    browser.close = AsyncMock()
    # 返回模拟的浏览器对象供测试使用
    return browser


@pytest.fixture  # 标记为 pytest fixture
def mock_context():
    """模拟 BrowserContext 对象"""
    # 创建 AsyncMock 对象，模拟浏览器上下文接口
    context = AsyncMock(spec=BrowserContext)
    # 模拟 close 异步方法，用于关闭上下文
    context.close = AsyncMock()
    # 模拟 new_page 异步方法，用于创建新页面
    context.new_page = AsyncMock()
    # 模拟 set_default_timeout 同步方法，用于设置默认超时
    context.set_default_timeout = MagicMock()
    # 返回模拟的上下文对象
    return context


@pytest.fixture  # 标记为 pytest fixture
def mock_page():
    """模拟 Page 对象"""
    # 创建 AsyncMock 对象，模拟 Playwright Page 接口
    page = AsyncMock(spec=Page)
    # 模拟 goto 异步方法，用于页面跳转
    page.goto = AsyncMock()
    # 模拟 close 异步方法，用于关闭页面
    page.close = AsyncMock()
    # 模拟 locator 同步方法，用于查找页面元素
    page.locator = MagicMock()
    # 模拟 wait_for_selector 异步方法，用于等待元素出现
    page.wait_for_selector = AsyncMock()
    # 模拟 set_default_timeout 同步方法，设置默认超时时间
    page.set_default_timeout = MagicMock()
    # 模拟 set_default_navigation_timeout 同步方法，设置导航超时时间
    page.set_default_navigation_timeout = MagicMock()
    # 模拟 screenshot 异步方法，用于页面截图
    page.screenshot = AsyncMock()
    # 返回模拟的页面对象
    return page


@pytest.fixture  # 标记为 pytest fixture
def mock_locator():
    """模拟 Locator 对象"""
    # 创建 MagicMock 对象，模拟 Playwright Locator 接口
    locator = MagicMock(spec=Locator)
    # 模拟 click 异步方法，用于点击元素
    locator.click = AsyncMock()
    # 模拟 fill 异步方法，用于输入文本
    locator.fill = AsyncMock()
    # 模拟 clear 异步方法，用于清空输入框
    locator.clear = AsyncMock()
    # 模拟 wait_for 异步方法，用于等待元素状态
    locator.wait_for = AsyncMock()
    # 模拟 count 同步属性，返回元素数量（默认为 1）
    locator.count = MagicMock(return_value=1)
    # 返回模拟的定位器对象
    return locator


@pytest.fixture  # 标记为 pytest fixture
def mock_playwright():
    """模拟 Playwright 对象"""
    # 创建 MagicMock 对象，模拟 Playwright 控制器
    playwright = MagicMock()
    # 模拟 start 异步方法，用于启动 Playwright
    playwright.start = AsyncMock()

    # 模拟 chromium 浏览器启动器对象
    playwright.chromium = MagicMock()
    # 模拟 launch 异步方法，用于启动 Chromium 浏览器
    playwright.chromium.launch = AsyncMock()

    # 模拟 firefox 浏览器启动器对象
    playwright.firefox = MagicMock()
    # 模拟 launch 异步方法，用于启动 Firefox 浏览器
    playwright.firefox.launch = AsyncMock()

    # 模拟 webkit 浏览器启动器对象
    playwright.webkit = MagicMock()
    # 模拟 launch 异步方法，用于启动 Webkit 浏览器
    playwright.webkit.launch = AsyncMock()

    # 模拟 stop 异步方法，用于停止 Playwright
    playwright.stop = AsyncMock()
    # 返回模拟的 Playwright 对象
    return playwright


@pytest.fixture  # 标记为 pytest fixture
def sample_test_step():
    """示例测试步骤"""
    # 返回一个标准的测试步骤字典
    return {
        "step_order": 1,  # 步骤顺序号
        "action_type": "click",  # 操作类型：点击
        "element_locator": "#submit-button",  # 元素定位符
        "locator_type": "css",  # 定位类型：CSS 选择器
        "action_params": None  # 操作参数（点击操作无需参数）
    }


@pytest.fixture  # 标记为 pytest fixture
def sample_test_case():
    """示例测试用例"""
    # 返回一个包含多个步骤的完整测试用例字典
    return {
        "id": 1,  # 用例 ID
        "name": "登录测试",  # 用例名称
        "steps": [  # 测试步骤列表
            {
                "step_order": 1,  # 第 1 步
                "action_type": "navigate",  # 操作类型：页面跳转
                "action_params": {"url": "https://example.com"}  # 参数：目标 URL
            },
            {
                "step_order": 2,  # 第 2 步
                "action_type": "input",  # 操作类型：输入文本
                "element_locator": "#username",  # 定位用户名输入框
                "locator_type": "css",  # CSS 选择器定位
                "action_params": {"text": "testuser"}  # 参数：输入的文本
            },
            {
                "step_order": 3,  # 第 3 步
                "action_type": "click",  # 操作类型：点击
                "element_locator": "#submit",  # 定位提交按钮
                "locator_type": "css"  # CSS 选择器定位
            }
        ]
    }
