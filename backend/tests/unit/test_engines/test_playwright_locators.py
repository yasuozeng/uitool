"""
PlaywrightEngine 元素定位测试
"""
# 导入 pytest 测试框架，用于编写测试用例和 fixture
import pytest
# 从 unittest.mock 导入模拟对象类，用于模拟 Playwright 对象
from unittest.mock import MagicMock, AsyncMock
# 导入 PlaywrightEngine 类进行测试
from app.engines.playwright_engine import PlaywrightEngine


class TestGetLocator:
    """测试元素定位器解析"""

    @pytest.fixture  # 定义 fixture，用于在多个测试中复用
    def engine_with_page(self):
        """创建带有模拟页面的引擎"""
        # 创建 PlaywrightEngine 实例
        engine = PlaywrightEngine()
        # 创建模拟的页面对象
        mock_page = AsyncMock()
        # 模拟 locator 方法，返回一个 MagicMock 对象
        mock_page.locator = MagicMock(return_value=MagicMock())
        # 将模拟页面设置到引擎上
        engine.page = mock_page
        # 返回配置好的引擎
        return engine

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_id_without_hash(self, engine_with_page):
        """测试 ID 定位（不带 # 前缀）"""
        # 调用 _get_locator 方法，定位类型为 "id"
        locator = await engine_with_page._get_locator("id", "username")
        # 验证：自动添加 # 前缀，调用 page.locator("#username")
        engine_with_page.page.locator.assert_called_once_with("#username")

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_id_with_hash(self, engine_with_page):
        """测试 ID 定位（带 # 前缀）"""
        # 调用 _get_locator 方法，定位符已包含 # 前缀
        locator = await engine_with_page._get_locator("id", "#username")
        # 验证：不会重复添加 #，直接使用原始定位符
        engine_with_page.page.locator.assert_called_once_with("#username")

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_xpath(self, engine_with_page):
        """测试 XPath 定位"""
        # 调用 _get_locator 方法，定位类型为 "xpath"
        locator = await engine_with_page._get_locator("xpath", "//input[@id='username']")
        # 验证：添加 "xpath=" 前缀
        engine_with_page.page.locator.assert_called_once_with("xpath=//input[@id='username']")

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_css(self, engine_with_page):
        """测试 CSS Selector 定位"""
        # 调用 _get_locator 方法，定位类型为 "css"
        locator = await engine_with_page._get_locator("css", "input#username")
        # 验证：直接使用 CSS 选择器，不加前缀
        engine_with_page.page.locator.assert_called_once_with("input#username")

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_name(self, engine_with_page):
        """测试 Name 属性定位"""
        # 调用 _get_locator 方法，定位类型为 "name"
        locator = await engine_with_page._get_locator("name", "username")
        # 验证：转换为 [name="username"] 选择器
        engine_with_page.page.locator.assert_called_once_with('[name="username"]')

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_class_without_dot(self, engine_with_page):
        """测试 Class 定位（不带 . 前缀）"""
        # 调用 _get_locator 方法，定位类型为 "class"
        locator = await engine_with_page._get_locator("class", "form-control")
        # 验证：自动添加 . 前缀
        engine_with_page.page.locator.assert_called_once_with(".form-control")

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_class_with_dot(self, engine_with_page):
        """测试 Class 定位（带 . 前缀）"""
        # 调用 _get_locator 方法，定位符已包含 . 前缀
        locator = await engine_with_page._get_locator("class", ".form-control")
        # 验证：不会重复添加 .
        engine_with_page.page.locator.assert_called_once_with(".form-control")

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_invalid_type(self, engine_with_page):
        """测试无效的定位类型"""
        # 使用断言验证抛出 ValueError
        with pytest.raises(ValueError) as exc_info:
            await engine_with_page._get_locator("invalid", "selector")
        # 验证：错误消息包含"不支持的定位类型"
        assert "不支持的定位类型" in str(exc_info.value)

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_raises_error_when_page_not_initialized(self):
        """测试页面未初始化时抛出错误"""
        # 创建未初始化页面的引擎
        engine = PlaywrightEngine()
        # 使用断言验证抛出 RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            await engine._get_locator("id", "test")
        # 验证：错误消息包含"页面未初始化"
        assert "页面未初始化" in str(exc_info.value)

    @pytest.mark.parametrize("locator_type,locator_str,expected", [  # 参数化测试数据
        ("id", "username", "#username"),  # ID 不带 #
        ("id", "#user", "#user"),  # ID 带 #
        ("xpath", "//div[@class='test']", "xpath=//div[@class='test']"),  # XPath
        ("css", "div.test", "div.test"),  # CSS 选择器
        ("name", "email", '[name="email"]'),  # Name 属性
        ("class", "btn-primary", ".btn-primary"),  # Class 不带 .
        ("class", ".btn", ".btn"),  # Class 带 .
    ])
    @pytest.mark.asyncio  # 标记为异步测试
    async def test_get_locator_parametrized(
        self, engine_with_page, locator_type, locator_str, expected
    ):
        """参数化测试各种定位类型"""
        # 使用参数化的定位类型和定位符调用方法
        locator = await engine_with_page._get_locator(locator_type, locator_str)
        # 验证：调用了预期的选择器
        engine_with_page.page.locator.assert_called_with(expected)
