"""
PlaywrightEngine 执行控制器测试
"""
# 导入 pytest 测试框架，用于编写测试用例和异步测试装饰器
import pytest
# 从 unittest.mock 导入模拟对象类和 patch 装饰器，用于模拟外部依赖
from unittest.mock import AsyncMock, MagicMock, patch
# 导入 PlaywrightEngine 类进行测试
from app.engines.playwright_engine import PlaywrightEngine


class TestExecuteStep:
    """测试单步执行"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_navigate(self):
        """测试执行 navigate 步骤"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 goto 异步方法
        engine.page.goto = AsyncMock()

        # 定义测试步骤（跳转操作）
        step = {
            "action_type": "navigate",  # 操作类型：页面跳转
            "action_params": '{"url": "https://example.com"}'  # 参数：JSON 字符串
        }

        # 执行步骤
        result = await engine.execute_step(step)

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：消息包含"成功跳转到"
        assert "成功跳转到" in result["message"]

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_navigate_dict_params(self):
        """测试 navigate 步骤（字典参数）"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 goto 异步方法
        engine.page.goto = AsyncMock()

        # 定义测试步骤（使用字典格式参数）
        step = {
            "action_type": "navigate",  # 操作类型
            "action_params": {"url": "https://example.com"}  # 参数：字典格式
        }

        # 执行步骤
        result = await engine.execute_step(step)

        # 验证：返回成功状态
        assert result["success"] is True

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_click(self):
        """测试执行 click 步骤"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 click 异步方法
        mock_locator.click = AsyncMock()

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 定义测试步骤（点击操作）
            step = {
                "action_type": "click",  # 操作类型：点击
                "element_locator": "#button",  # 元素定位符
                "locator_type": "css"  # 定位类型
            }
            # 执行步骤
            result = await engine.execute_step(step)

        # 验证：返回成功状态
        assert result["success"] is True

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_input(self):
        """测试执行 input 步骤"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 fill 异步方法（输入文本）
        mock_locator.fill = AsyncMock()

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 定义测试步骤（输入操作）
            step = {
                "action_type": "input",  # 操作类型：输入文本
                "element_locator": "#input",  # 元素定位符
                "locator_type": "css",  # 定位类型
                "action_params": {"text": "test"}  # 参数：输入的文本
            }
            # 执行步骤
            result = await engine.execute_step(step)

        # 验证：返回成功状态
        assert result["success"] is True

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_clear(self):
        """测试执行 clear 步骤"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 clear 异步方法
        mock_locator.clear = AsyncMock()

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 定义测试步骤（清除操作）
            step = {
                "action_type": "clear",  # 操作类型：清除输入框内容
                "element_locator": "#input",  # 元素定位符
                "locator_type": "css"  # 定位类型
            }
            # 执行步骤
            result = await engine.execute_step(step)

        # 验证：返回成功状态
        assert result["success"] is True

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_wait(self):
        """测试执行 wait 步骤"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 wait_for 异步方法
        mock_locator.wait_for = AsyncMock()

        # 模拟 _get_locator 方法返回模拟定位器
        with patch.object(engine, '_get_locator', return_value=mock_locator):
            # 定义测试步骤（等待操作）
            step = {
                "action_type": "wait",  # 操作类型：等待元素
                "element_locator": "#element",  # 元素定位符
                "locator_type": "css",  # 定位类型
                "action_params": {"timeout": 5000}  # 参数：超时时间 5 秒
            }
            # 执行步骤
            result = await engine.execute_step(step)

        # 验证：返回成功状态
        assert result["success"] is True

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_verify_text(self):
        """测试执行 verify_text 步骤"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 wait_for_selector 异步方法
        engine.page.wait_for_selector = AsyncMock()

        # 定义测试步骤（验证文本操作）
        step = {
            "action_type": "verify_text",  # 操作类型：验证文本存在
            "action_params": {"text": "Welcome"}  # 参数：要验证的文本
        }

        # 执行步骤
        result = await engine.execute_step(step)

        # 验证：返回成功状态
        assert result["success"] is True

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_verify_element(self):
        """测试执行 verify_element 步骤"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 定义模拟的 _get_locator 异步函数
        async def mock_get_locator(*args, **kwargs):
            # 创建模拟的定位器对象
            mock_locator = MagicMock()
            # 模拟 count 属性返回 1（元素存在）
            mock_locator.count = AsyncMock(return_value=1)
            return mock_locator

        # 模拟 _get_locator 方法
        with patch.object(engine, '_get_locator', side_effect=mock_get_locator):
            # 定义测试步骤（验证元素操作）
            step = {
                "action_type": "verify_element",  # 操作类型：验证元素存在
                "element_locator": "#element",  # 元素定位符
                "locator_type": "css"  # 定位类型
            }
            # 执行步骤
            result = await engine.execute_step(step)

        # 验证：返回成功状态
        assert result["success"] is True

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_invalid_action_type(self):
        """测试无效的操作类型"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 定义测试步骤（无效的操作类型）
        step = {
            "action_type": "invalid_action",  # 不支持的操作类型
        }

        # 执行步骤
        result = await engine.execute_step(step)

        # 验证：返回失败状态
        assert result["success"] is False
        # 验证：消息包含"不支持的操作类型"
        assert "不支持的操作类型" in result["message"]

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_missing_required_param(self):
        """测试缺少必需参数"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 定义测试步骤（缺少必需参数）
        step = {
            "action_type": "navigate",  # 操作类型
            # 缺少 url 参数（navigate 必需）
        }

        # 执行步骤
        result = await engine.execute_step(step)

        # 验证：返回失败状态
        assert result["success"] is False

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_exception(self):
        """测试步骤执行异常"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 goto 方法抛出异常（浏览器崩溃）
        engine.page.goto = AsyncMock(side_effect=RuntimeError("Browser crash"))

        # 定义测试步骤
        step = {
            "action_type": "navigate",
            "action_params": {"url": "https://example.com"}
        }

        # 执行步骤
        result = await engine.execute_step(step)

        # 验证：返回失败状态
        assert result["success"] is False
        # 验证：结果包含错误信息
        assert "error" in result

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_step_default_locator_type(self):
        """测试默认定位类型"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 创建模拟的定位器对象
        mock_locator = MagicMock()
        # 模拟 click 异步方法
        mock_locator.click = AsyncMock()

        # 模拟 _get_locator 方法，并获取 mock 对象
        with patch.object(engine, '_get_locator', return_value=mock_locator) as mock_get:
            # 定义测试步骤（未指定 locator_type）
            step = {
                "action_type": "click",
                "element_locator": "#button",
                # 未指定 locator_type，应使用默认值 "css"
            }
            # 执行步骤
            result = await engine.execute_step(step)

        # 验证：返回成功状态
        assert result["success"] is True
        # 验证：_get_locator 被调用时使用了默认定位类型 "css"
        mock_get.assert_called_once_with("css", "#button")


class TestExecuteCase:
    """测试用例执行"""

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_case_all_success(self):
        """测试所有步骤都成功"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 goto 异步方法
        engine.page.goto = AsyncMock()
        # 模拟 wait_for_selector 异步方法
        engine.page.wait_for_selector = AsyncMock()

        # 定义测试用例数据
        case_data = {
            "id": 1,  # 用例 ID
            "name": "测试用例",  # 用例名称
            "steps": [  # 测试步骤列表
                {
                    "step_order": 1,  # 步骤顺序
                    "action_type": "navigate",  # 操作类型：页面跳转
                    "action_params": {"url": "https://example.com"}  # 参数：URL
                },
                {
                    "step_order": 2,  # 步骤顺序
                    "action_type": "verify_text",  # 操作类型：验证文本
                    "action_params": {"text": "Welcome"}  # 参数：要验证的文本
                }
            ]
        }

        # 执行测试用例
        result = await engine.execute_case(case_data)

        # 验证：整体成功状态为 True
        assert result["success"] is True
        # 验证：总步骤数为 2
        assert result["total_steps"] == 2
        # 验证：成功步骤数为 2
        assert result["success_steps"] == 2
        # 验证：失败步骤数为 0
        assert result["failed_steps"] == 0
        # 验证：步骤结果列表长度为 2
        assert len(result["step_results"]) == 2

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_case_with_failure(self):
        """测试有失败的用例"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 goto 异步方法
        engine.page.goto = AsyncMock()
        # 模拟 wait_for_selector 方法抛出超时异常
        engine.page.wait_for_selector = AsyncMock(
            side_effect=Exception("Timeout")
        )
        # 模拟错误截图方法
        engine.take_screenshot_on_error = AsyncMock(return_value="/path/to/screenshot.png")

        # 定义测试用例数据（第二步会失败）
        case_data = {
            "id": 1,
            "name": "测试用例",
            "steps": [
                {
                    "step_order": 1,
                    "action_type": "navigate",
                    "action_params": {"url": "https://example.com"}
                },
                {
                    "step_order": 2,
                    "action_type": "verify_text",
                    "action_params": {"text": "NotFound"}  # 文本不存在，会超时
                }
            ]
        }

        # 执行测试用例
        result = await engine.execute_case(case_data)

        # 验证：整体成功状态为 False
        assert result["success"] is False
        # 验证：总步骤数为 2
        assert result["total_steps"] == 2
        # 验证：成功步骤数为 1
        assert result["success_steps"] == 1
        # 验证：失败步骤数为 1
        assert result["failed_steps"] == 1

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_case_empty_steps(self):
        """测试空步骤用例"""
        # 创建引擎实例
        engine = PlaywrightEngine()

        # 定义空步骤的测试用例
        case_data = {
            "id": 1,
            "name": "空用例",
            "steps": []  # 空步骤列表
        }

        # 执行测试用例
        result = await engine.execute_case(case_data)

        # 验证：空用例也视为成功
        assert result["success"] is True
        # 验证：总步骤数为 0
        assert result["total_steps"] == 0
        # 验证：成功步骤数为 0
        assert result["success_steps"] == 0
        # 验证：失败步骤数为 0
        assert result["failed_steps"] == 0

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_case_step_results_include_order(self):
        """测试步骤结果包含顺序"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 goto 异步方法
        engine.page.goto = AsyncMock()

        # 定义测试用例（步骤顺序为 5）
        case_data = {
            "id": 1,
            "name": "测试用例",
            "steps": [
                {
                    "step_order": 5,  # 步骤顺序为 5（非连续）
                    "action_type": "navigate",
                    "action_params": {"url": "https://example.com"}
                }
            ]
        }

        # 执行测试用例
        result = await engine.execute_case(case_data)

        # 验证：步骤结果中保留了原始的 step_order
        assert result["step_results"][0]["step_order"] == 5
        # 验证：步骤结果中包含 action_type
        assert result["step_results"][0]["action_type"] == "navigate"

    @pytest.mark.asyncio  # 标记为异步测试
    async def test_execute_case_screenshot_on_failure(self):
        """测试失败时截图"""
        # 创建引擎实例
        engine = PlaywrightEngine()
        # 设置模拟的页面对象
        engine.page = AsyncMock()
        # 模拟 goto 方法抛出异常
        engine.page.goto = AsyncMock(side_effect=Exception("Error"))
        # 模拟错误截图方法，返回截图路径
        engine.take_screenshot_on_error = AsyncMock(return_value="/screenshots/error.png")

        # 定义测试用例（第一步就会失败）
        case_data = {
            "id": 1,
            "name": "测试用例",
            "steps": [
                {
                    "step_order": 1,
                    "action_type": "navigate",
                    "action_params": {"url": "https://example.com"}
                }
            ]
        }

        # 执行测试用例
        result = await engine.execute_case(case_data)

        # 验证：整体成功状态为 False
        assert result["success"] is False
        # 验证：步骤结果中包含 screenshot 字段
        assert "screenshot" in result["step_results"][0]
        # 验证：截图路径正确
        assert result["step_results"][0]["screenshot"] == "/screenshots/error.png"
