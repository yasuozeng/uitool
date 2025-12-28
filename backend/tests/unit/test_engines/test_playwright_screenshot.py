"""
PlaywrightEngine 截图功能测试
"""
# 导入 pytest 测试框架，用于编写测试用例和异步测试装饰器
import pytest
# 导入 Path 路径处理类，用于路径验证和操作
from pathlib import Path
# 导入 datetime 时间类（此测试中未直接使用，但相关功能依赖时间戳）
from datetime import datetime
# 从 unittest.mock 导入模拟对象类和 patch 装饰器，用于模拟外部依赖
from unittest.mock import AsyncMock, MagicMock, patch
# 导入 PlaywrightEngine 类进行测试
from app.engines.playwright_engine import PlaywrightEngine
# 导入截图目录配置常量，用于路径验证
from app.config import SCREENSHOTS_DIR


class TestTakeScreenshot:
    """测试截图功能"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_take_screenshot_with_filename(self):
        """测试使用指定文件名截图"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 screenshot 异步方法
        engine.page.screenshot = AsyncMock()

        # 定义截图文件名
        filename = "test_screenshot.png"
        # 调用截图方法并获取结果路径
        result = await engine.take_screenshot(filename)

        # 构建期望的完整路径
        expected_path = str(SCREENSHOTS_DIR / filename)
        # 验证：返回路径与期望路径一致
        assert result == expected_path
        # 验证：screenshot 方法被调用且参数正确
        engine.page.screenshot.assert_called_once_with(path=expected_path)

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_take_screenshot_without_filename(self):
        """测试自动生成文件名截图"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 screenshot 异步方法
        engine.page.screenshot = AsyncMock()

        # 使用 patch 模拟 datetime 模块（控制时间戳）
        with patch('app.engines.playwright_engine.datetime') as mock_datetime:
            # 模拟时间戳格式化返回固定值
            mock_datetime.now.return_value.strftime.return_value = "20231227_120000_123456"
            # 调用截图方法（不传文件名，自动生成）
            result = await engine.take_screenshot()

        # 验证：返回路径以截图目录开头
        assert result.startswith(str(SCREENSHOTS_DIR))
        # 验证：返回路径以 .png 结尾
        assert result.endswith(".png")
        # 验证：screenshot 方法被调用了一次
        engine.page.screenshot.assert_called_once()

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_take_screenshot_raises_error_when_page_not_initialized(self):
        """测试页面未初始化时截图抛出错误"""
        # 创建引擎实例（未初始化 page）
        engine = PlaywrightEngine()

        # 验证：抛出 RuntimeError 异常
        with pytest.raises(RuntimeError) as exc_info:
            # 尝试截图（page 未初始化）
            await engine.take_screenshot()

        # 验证：异常信息包含 "页面未初始化"
        assert "页面未初始化" in str(exc_info.value)

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_take_screenshot_creates_file(self):
        """测试截图文件创建"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 screenshot 异步方法
        engine.page.screenshot = AsyncMock()

        # 定义截图文件名
        filename = "test_create.png"
        # 调用截图方法
        result = await engine.take_screenshot(filename)

        # 验证：返回路径的文件名与输入一致
        assert Path(result).name == filename
        # 验证：返回路径包含截图目录
        assert str(SCREENSHOTS_DIR) in result


class TestTakeScreenshotOnError:
    """测试失败时截图"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_take_screenshot_on_error(self):
        """测试错误时自动截图"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 screenshot 异步方法
        engine.page.screenshot = AsyncMock()

        # 使用 patch 模拟 datetime 模块
        with patch('app.engines.playwright_engine.datetime') as mock_datetime:
            # 模拟时间戳格式化返回固定值
            mock_datetime.now.return_value.strftime.return_value = "20231227_120000_123456"
            # 调用错误截图方法（传入错误信息）
            result = await engine.take_screenshot_on_error({"error": "Test error"})

        # 验证：文件名包含 error_ 前缀
        assert "error_" in Path(result).name
        # 验证：文件以 .png 结尾
        assert result.endswith(".png")

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_take_screenshot_on_error_generates_unique_names(self):
        """测试每次生成唯一的文件名"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 screenshot 异步方法
        engine.page.screenshot = AsyncMock()

        # 使用 patch 模拟 datetime 模块
        with patch('app.engines.playwright_engine.datetime') as mock_datetime:
            # 模拟不同的时间戳（side_effect 允许每次调用返回不同值）
            mock_datetime.now.return_value.strftime.side_effect = [
                "20231227_120000_100000",  # 第一个时间戳
                "20231227_120000_200000"  # 第二个时间戳
            ]

            # 调用错误截图方法两次
            result1 = await engine.take_screenshot_on_error({"error": "Error 1"})
            result2 = await engine.take_screenshot_on_error({"error": "Error 2"})

        # 验证：两次生成的文件名不同
        assert result1 != result2

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_take_screenshot_on_error_uses_take_screenshot(self):
        """测试错误截图调用基础截图方法"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 screenshot 异步方法
        engine.page.screenshot = AsyncMock()

        # 使用 patch.object 模拟引擎的 take_screenshot 方法
        with patch.object(engine, 'take_screenshot') as mock_take:
            # 设置模拟方法的返回值
            mock_take.return_value = "/screenshots/error_test.png"
            # 调用错误截图方法
            result = await engine.take_screenshot_on_error({"error": "Test"})

        # 验证：返回值与模拟的 take_screenshot 返回值一致
        assert result == "/screenshots/error_test.png"


class TestScreenshotIntegration:
    """截图功能集成测试"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_screenshot_directory_exists(self):
        """测试截图目录存在"""
        # 验证：截图目录实际存在
        assert SCREENSHOTS_DIR.exists()
        # 验证：截图路径确实是一个目录
        assert SCREENSHOTS_DIR.is_dir()

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_screenshot_path_is_absolute(self):
        """测试截图路径是绝对路径"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 screenshot 异步方法
        engine.page.screenshot = AsyncMock()

        # 调用截图方法
        result = await engine.take_screenshot("test.png")

        # 验证：返回的是绝对路径
        assert Path(result).is_absolute()

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_multiple_screenshots_same_session(self):
        """测试同一会话多次截图"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 screenshot 异步方法
        engine.page.screenshot = AsyncMock()

        # 使用 patch 模拟 datetime 模块
        with patch('app.engines.playwright_engine.datetime') as mock_datetime:
            # 模拟三个不同的时间戳
            mock_datetime.now.return_value.strftime.side_effect = [
                "20231227_120000_100000",  # 第一个截图时间戳
                "20231227_120000_200000",  # 第二个截图时间戳
                "20231227_120000_300000"  # 第三个截图时间戳
            ]

            # 调用截图方法三次
            result1 = await engine.take_screenshot()
            result2 = await engine.take_screenshot()
            result3 = await engine.take_screenshot()

        # 验证：所有截图路径都不同（集合长度为 3）
        assert len({result1, result2, result3}) == 3

        # 验证：screenshot 方法被调用了 3 次
        assert engine.page.screenshot.call_count == 3
