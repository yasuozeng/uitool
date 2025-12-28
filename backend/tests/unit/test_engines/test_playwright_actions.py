"""
PlaywrightEngine 操作执行测试
"""
# 导入 pytest 测试框架，用于编写测试用例和异步测试装饰器
import pytest
# 从 unittest.mock 导入模拟对象类，用于模拟 Playwright 对象
from unittest.mock import AsyncMock, MagicMock, patch
# 导入 PlaywrightEngine 类进行测试
from app.engines.playwright_engine import PlaywrightEngine


class TestExecuteNavigate:
    """测试页面跳转操作"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_navigate_success(self):
        """测试成功的页面跳转"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 goto 异步方法
        engine.page.goto = AsyncMock()

        # 调用 execute_navigate 方法
        result = await engine.execute_navigate("https://example.com")

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：消息包含"成功跳转到"
        assert "成功跳转到" in result["message"]
        # 验证：消息包含目标 URL
        assert "https://example.com" in result["message"]
        # 验证：调用了 page.goto 方法，等待 DOM 加载完成
        engine.page.goto.assert_called_once_with("https://example.com", wait_until="domcontentloaded")

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_navigate_failure(self):
        """测试失败的页面跳转"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 goto 方法抛出异常（网络错误）
        engine.page.goto = AsyncMock(side_effect=Exception("Network error"))

        # 调用 execute_navigate 方法
        result = await engine.execute_navigate("https://example.com")

        # 验证：返回失败状态
        assert result["success"] is False
        # 验证：消息包含"页面跳转失败"
        assert "页面跳转失败" in result["message"]
        # 验证：结果包含错误信息
        assert "error" in result


class TestExecuteClick:
    """测试点击操作"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_click_success(self):
        """测试成功的点击"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 click 异步方法
        mock_locator.click = AsyncMock()

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 调用 execute_click 方法
            result = await engine.execute_click("css", "#button")

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：消息包含"成功点击"
        assert "成功点击" in result["message"]
        # 验证：调用了 click 方法
        mock_locator.click.assert_called_once()

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_click_failure(self):
        """测试失败的点击"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 click 方法抛出异常（元素未找到）
        mock_locator.click = AsyncMock(side_effect=Exception("Element not found"))

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 调用 execute_click 方法
            result = await engine.execute_click("css", "#button")

        # 验证：返回失败状态
        assert result["success"] is False
        # 验证：消息包含"点击元素失败"
        assert "点击元素失败" in result["message"]


class TestExecuteInput:
    """测试输入操作"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_input_success(self):
        """测试成功的输入"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 fill 异步方法
        mock_locator.fill = AsyncMock()

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 调用 execute_input 方法
            result = await engine.execute_input("css", "#input", "test text")

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：消息包含"成功输入文本"
        assert "成功输入文本" in result["message"]
        # 验证：调用了 fill 方法并传入正确的文本
        mock_locator.fill.assert_called_once_with("test text")

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_input_failure(self):
        """测试失败的输入"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 fill 方法抛出异常
        mock_locator.fill = AsyncMock(side_effect=Exception("Input failed"))

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 调用 execute_input 方法
            result = await engine.execute_input("css", "#input", "test")

        # 验证：返回失败状态
        assert result["success"] is False


class TestExecuteClear:
    """测试清除操作"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_clear_success(self):
        """测试成功的清除"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 clear 异步方法
        mock_locator.clear = AsyncMock()

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 调用 execute_clear 方法
            result = await engine.execute_clear("css", "#input")

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：消息包含"成功清除内容"
        assert "成功清除内容" in result["message"]
        # 验证：调用了 clear 方法
        mock_locator.clear.assert_called_once()

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_clear_failure(self):
        """测试失败的清除"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 clear 方法抛出异常
        mock_locator.clear = AsyncMock(side_effect=Exception("Clear failed"))

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 调用 execute_clear 方法
            result = await engine.execute_clear("css", "#input")

        # 验证：返回失败状态
        assert result["success"] is False


class TestExecuteWait:
    """测试等待操作"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_wait_success(self):
        """测试成功的等待"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 wait_for 异步方法
        mock_locator.wait_for = AsyncMock()

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 调用 execute_wait 方法，超时时间为 5000 毫秒
            result = await engine.execute_wait("css", "#element", 5000)

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：消息包含"元素已可见"
        assert "元素已可见" in result["message"]
        # 验证：调用了 wait_for 方法，状态为 visible，超时时间为 5000
        mock_locator.wait_for.assert_called_once_with(state="visible", timeout=5000)

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_wait_default_timeout(self):
        """测试使用默认超时时间"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 wait_for 异步方法
        mock_locator.wait_for = AsyncMock()

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 调用 execute_wait 方法，不指定超时时间（使用默认值）
            result = await engine.execute_wait("css", "#element")

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：调用了 wait_for 方法
        mock_locator.wait_for.assert_called_once()

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_wait_failure(self):
        """测试等待超时"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 wait_for 方法抛出超时异常
        mock_locator.wait_for = AsyncMock(side_effect=Exception("Timeout"))

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 调用 execute_wait 方法
            result = await engine.execute_wait("css", "#element", 5000)

        # 验证：返回失败状态
        assert result["success"] is False
        # 验证：消息包含"等待元素超时"
        assert "等待元素超时" in result["message"]


class TestExecuteVerifyText:
    """测试验证文本操作"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_verify_text_success(self):
        """测试成功验证文本"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 wait_for_selector 异步方法
        engine.page.wait_for_selector = AsyncMock()

        # 调用 execute_verify_text 方法
        result = await engine.execute_verify_text("Welcome")

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：消息包含"成功验证文本存在"
        assert "成功验证文本存在" in result["message"]
        # 验证：调用了 wait_for_selector 方法
        engine.page.wait_for_selector.assert_called_once()

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_verify_text_failure(self):
        """测试验证文本失败"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 wait_for_selector 方法抛出异常（文本未找到）
        engine.page.wait_for_selector = AsyncMock(
            side_effect=Exception("Text not found")
        )

        # 调用 execute_verify_text 方法
        result = await engine.execute_verify_text("NotFound")

        # 验证：返回失败状态
        assert result["success"] is False
        # 验证：消息包含"验证文本失败"
        assert "验证文本失败" in result["message"]


class TestExecuteVerifyElement:
    """测试验证元素操作"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_verify_element_exists(self):
        """测试元素存在"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 定义模拟的 _get_locator 异步函数
        async def mock_get_locator(*args, **kwargs):
            mock_locator = MagicMock()
            # 模拟 count 属性返回 2（元素存在）
            mock_locator.count = AsyncMock(return_value=2)
            return mock_locator

        # 模拟 _get_locator 方法
        with patch.object(engine, '_get_locator', side_effect=mock_get_locator):
            # 调用 execute_verify_element 方法
            result = await engine.execute_verify_element("css", "#element")

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：消息包含"元素存在"
        assert "元素存在" in result["message"]

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_verify_element_not_exists(self):
        """测试元素不存在"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 定义模拟的 _get_locator 异步函数
        async def mock_get_locator(*args, **kwargs):
            mock_locator = MagicMock()
            # 模拟 count 属性返回 0（元素不存在）
            mock_locator.count = AsyncMock(return_value=0)
            return mock_locator

        # 模拟 _get_locator 方法
        with patch.object(engine, '_get_locator', side_effect=mock_get_locator):
            # 调用 execute_verify_element 方法
            result = await engine.execute_verify_element("css", "#element")

        # 验证：返回失败状态
        assert result["success"] is False
        # 验证：消息包含"元素不存在"
        assert "元素不存在" in result["message"]

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_verify_element_error(self):
        """测试验证元素时出错"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 定义模拟的 _get_locator 异步函数
        async def mock_get_locator(*args, **kwargs):
            mock_locator = MagicMock()
            # 模拟 count 方法抛出异常
            mock_locator.count = AsyncMock(side_effect=Exception("Error"))
            return mock_locator

        # 模拟 _get_locator 方法
        with patch.object(engine, '_get_locator', side_effect=mock_get_locator):
            # 调用 execute_verify_element 方法
            result = await engine.execute_verify_element("css", "#element")

        # 验证：返回失败状态
        assert result["success"] is False
        # 验证：消息包含"验证元素失败"
        assert "验证元素失败" in result["message"]
