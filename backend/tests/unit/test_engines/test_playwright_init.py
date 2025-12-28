"""
PlaywrightEngine 初始化测试
"""
# 导入 pytest 测试框架，用于编写测试用例和参数化测试装饰器
import pytest
# 从 unittest.mock 导入 patch 和 MagicMock，用于模拟外部依赖（如 async_playwright）
from unittest.mock import patch, MagicMock
# 导入 PlaywrightEngine 类进行测试
from app.engines.playwright_engine import PlaywrightEngine
# 导入浏览器类型枚举（虽然此测试中未直接使用，但保留以备将来扩展）
from app.config import BrowserType


class TestPlaywrightEngineInit:
    """测试 PlaywrightEngine 初始化"""

    def test_init_with_defaults(self):
        """测试使用默认参数初始化"""
        # 使用默认参数创建 PlaywrightEngine 实例
        engine = PlaywrightEngine()

        # 验证：默认浏览器类型为 "chromium"
        assert engine.browser_type == "chromium"
        # 验证：默认无头模式为 True
        assert engine.headless is True
        # 验证：默认窗口大小为 1920x1080
        assert engine.window_size == {"width": 1920, "height": 1080}
        # 验证：playwright 对象初始为 None
        assert engine.playwright is None
        # 验证：browser 对象初始为 None
        assert engine.browser is None
        # 验证：context 对象初始为 None
        assert engine.context is None
        # 验证：page 对象初始为 None
        assert engine.page is None

    def test_init_with_custom_browser_type(self):
        """测试自定义浏览器类型"""
        # 使用自定义浏览器类型创建引擎
        engine = PlaywrightEngine(browser_type="firefox")

        # 验证：浏览器类型为 "firefox"
        assert engine.browser_type == "firefox"
        # 验证：无头模式仍为默认值 True
        assert engine.headless is True

    def test_init_with_headless_false(self):
        """测试有头模式初始化"""
        # 创建有头模式的引擎（显示浏览器界面）
        engine = PlaywrightEngine(headless=False)

        # 验证：无头模式设置为 False
        assert engine.headless is False

    def test_init_with_custom_window_size(self):
        """测试自定义窗口大小"""
        # 使用自定义窗口大小创建引擎
        engine = PlaywrightEngine(window_size="1366x768")

        # 验证：窗口大小正确解析为字典
        assert engine.window_size == {"width": 1366, "height": 768}

    def test_init_with_all_custom_params(self):
        """测试所有自定义参数"""
        # 使用所有自定义参数创建引擎
        engine = PlaywrightEngine(
            browser_type="webkit",  # 浏览器类型
            headless=False,  # 有头模式
            window_size="2560x1440"  # 窗口大小
        )

        # 验证：所有参数正确设置
        assert engine.browser_type == "webkit"
        assert engine.headless is False
        assert engine.window_size == {"width": 2560, "height": 1440}

    def test_init_with_invalid_window_size(self):
        """测试无效窗口大小（使用默认值）"""
        # 使用无效的窗口大小字符串创建引擎
        engine = PlaywrightEngine(window_size="invalid")

        # 验证：无效窗口大小回退到默认值 1920x1080
        assert engine.window_size == {"width": 1920, "height": 1080}

    @pytest.mark.parametrize("browser_type", ["chromium", "firefox", "webkit"])  # 参数化测试
    def test_valid_browser_types(self, browser_type):
        """测试有效的浏览器类型"""
        # 使用参数化的浏览器类型创建引擎
        engine = PlaywrightEngine(browser_type=browser_type)
        # 验证：浏览器类型正确设置
        assert engine.browser_type == browser_type


class TestPlaywrightEngineAttributes:
    """测试 PlaywrightEngine 属性"""

    def test_playwright_attribute_initially_none(self):
        """测试 playwright 属性初始为 None"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 验证：playwright 属性初始为 None（未启动）
        assert engine.playwright is None

    def test_browser_attribute_initially_none(self):
        """测试 browser 属性初始为 None"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 验证：browser 属性初始为 None（未启动浏览器）
        assert engine.browser is None

    def test_context_attribute_initially_none(self):
        """测试 context 属性初始为 None"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 验证：context 属性初始为 None（未创建上下文）
        assert engine.context is None

    def test_page_attribute_initially_none(self):
        """测试 page 属性初始为 None"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 验证：page 属性初始为 None（未创建页面）
        assert engine.page is None
