"""
Playwright执行引擎
负责执行自动化测试用例，封装浏览器操作和测试步骤执行逻辑
"""
# 从 typing 模块导入类型注解工具
from typing import Any, Optional
# 从 playwright.async_api 导入异步 API 相关类
from playwright.async_api import async_playwright, Browser, Page, BrowserContext, Locator
# 导入 asyncio 异步编程模块
import asyncio
# 导入 json 模块用于解析 JSON 字符串
import json
# 从 datetime 模块导入 datetime 类，用于生成时间戳文件名
from datetime import datetime
# 从 pathlib 导入 Path 类，用于路径操作
from pathlib import Path
# 从本地配置模块导入浏览器类型、窗口大小、超时时间、截图目录等配置
from app.config import (
    BrowserType,  # 浏览器类型字面量类型
    get_window_size,  # 窗口大小获取函数
    DEFAULT_STEP_TIMEOUT,  # 默认步骤超时时间
    DEFAULT_NAVIGATION_TIMEOUT,  # 默认导航超时时间
    SCREENSHOTS_DIR,  # 截图保存目录
)


# 定义 Playwright 执行引擎类
class PlaywrightEngine:
    """
    Playwright 执行引擎

    负责浏览器管理和测试步骤执行，提供统一的自动化测试接口
    """

    def __init__(
        self,
        browser_type: BrowserType = "chromium",  # 浏览器类型：chromium/firefox/webkit
        headless: bool = True,  # 无头模式：True 不显示浏览器窗口，False 显示窗口
        window_size: str = "1920x1080",  # 窗口大小字符串，如 "1920x1080"
    ):
        """
        初始化执行引擎

        Args:
            browser_type: 浏览器类型 (chromium/firefox/webkit)
            headless: 是否无头模式
            window_size: 窗口大小
        """
        # 保存浏览器类型配置
        self.browser_type = browser_type
        # 保存无头模式配置
        self.headless = headless
        # 解析并保存窗口大小配置（转换为字典格式）
        self.window_size = get_window_size(window_size)
        # Playwright 实例，后续启动时赋值
        self.playwright = None
        # 浏览器实例，后续启动时赋值
        self.browser: Optional[Browser] = None
        # 浏览器上下文实例，后续创建时赋值
        self.context: Optional[BrowserContext] = None
        # 页面实例，后续创建时赋值
        self.page: Optional[Page] = None

    # 定义启动浏览器的异步方法
    async def start_browser(self):
        """
        启动浏览器

        初始化 Playwright 实例，启动浏览器，创建上下文并配置页面
        """
        # ========== Windows 平台事件循环修复 ==========
        # 在启动浏览器前检查并确保使用正确的事件循环策略
        # 这对于 Playwright 在 Windows 上的子进程操作至关重要
        import sys
        if sys.platform == 'win32':
            # 获取当前事件循环
            try:
                loop = asyncio.get_running_loop()
                # 检查当前事件循环是否使用正确的策略
                from asyncio import WindowsProactorEventLoopPolicy
                if not isinstance(loop, asyncio.ProactorEventLoop):
                    # 打印警告信息
                    print(f"[WARNING] 当前事件循环类型: {type(loop).__name__}, 需要 ProactorEventLoop")
                    print("[INFO] 尝试修复事件循环策略...")
                    # 注意：不能在运行时更换事件循环策略
                    # 如果策略错误，需要在启动应用前设置
            except Exception as e:
                print(f"[ERROR] 事件循环检查失败: {e}")

        # 启动 Playwright 实例
        self.playwright = await async_playwright().start()

        # 根据浏览器类型选择对应的浏览器启动器
        browser_launcher = {
            "chromium": self.playwright.chromium,  # Chromium 浏览器
            "firefox": self.playwright.firefox,  # Firefox 浏览器
            "webkit": self.playwright.webkit,  # WebKit 浏览器（Safari）
        }.get(self.browser_type, self.playwright.chromium)  # 默认使用 Chromium

        # 启动浏览器实例
        self.browser = await browser_launcher.launch(
            headless=self.headless,  # 无头模式配置
            args=[
                "--no-sandbox",  # 禁用沙箱模式（在 Docker 环境中需要）
                "--disable-setuid-sandbox",  # 禁用 setuid 沙箱
                "--disable-dev-shm-usage",  # 禁用 /dev/shm 使用（避免内存问题）
            ] if self.browser_type == "chromium" else []  # 仅 Chromium 需要这些参数
        )

        # 创建浏览器上下文（类似于隐身模式窗口）
        self.context = await self.browser.new_context(
            viewport=self.window_size,  # 设置视口大小
            ignore_https_errors=True,  # 忽略 HTTPS 错误
            java_script_enabled=True,  # 启用 JavaScript
        )

        # 设置上下文的默认超时时间（所有操作都适用）
        self.context.set_default_timeout(DEFAULT_STEP_TIMEOUT)

        # 在上下文中创建新页面
        self.page = await self.context.new_page()
        # 设置页面的默认超时时间
        self.page.set_default_timeout(DEFAULT_STEP_TIMEOUT)
        # 设置页面导航的默认超时时间
        self.page.set_default_navigation_timeout(DEFAULT_NAVIGATION_TIMEOUT)

    # 定义关闭浏览器的异步方法
    async def close_browser(self):
        """
        关闭浏览器

        按顺序关闭页面、上下文、浏览器和 Playwright 实例，释放资源
        """
        try:
            # 如果页面存在，关闭页面
            if self.page:
                await self.page.close()
                self.page = None  # 清空页面引用
            # 如果上下文存在，关闭上下文
            if self.context:
                await self.context.close()
                self.context = None  # 清空上下文引用
            # 如果浏览器存在，关闭浏览器
            if self.browser:
                await self.browser.close()
                self.browser = None  # 清空浏览器引用
            # 如果 Playwright 实例存在，停止 Playwright
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None  # 清空 Playwright 引用
        except Exception as e:
            # 捕获关闭时的异常，打印错误信息
            print(f"关闭浏览器时出错: {e}")

    # 定义创建新页面的异步方法
    async def new_page(self) -> Page:
        """
        创建新页面

        Returns:
            Page: 新创建的页面对象

        Raises:
            RuntimeError: 如果浏览器上下文未初始化
        """
        # 检查上下文是否已初始化
        if not self.context:
            raise RuntimeError("浏览器上下文未初始化，请先调用 start_browser()")
        # 在上下文中创建新页面
        self.page = await self.context.new_page()
        # 设置页面的默认超时时间
        self.page.set_default_timeout(DEFAULT_STEP_TIMEOUT)
        # 设置页面导航的默认超时时间
        self.page.set_default_navigation_timeout(DEFAULT_NAVIGATION_TIMEOUT)
        # 返回新创建的页面
        return self.page

    # 定义关闭当前页面的异步方法
    async def close_page(self):
        """
        关闭当前页面

        关闭当前活动页面并清空引用
        """
        # 如果页面存在，关闭页面
        if self.page:
            await self.page.close()
            self.page = None  # 清空页面引用

    # ========== 元素定位 ==========

    # 定义获取元素定位器的私有异步方法
    async def _get_locator(self, locator_type: str, locator: str) -> Locator:
        """
        根据定位类型获取定位器

        Args:
            locator_type: 定位类型 (id/xpath/css/name/class)
            locator: 定位符

        Returns:
            Locator对象

        Raises:
            ValueError: 不支持的定位类型
            RuntimeError: 页面未初始化
        """
        # 检查页面是否已初始化
        if not self.page:
            raise RuntimeError("页面未初始化")

        # 根据定位类型构建 Playwright 选择器
        if locator_type == "id":
            # ID 定位: #id 或 [id="value"]
            if locator.startswith("#"):
                # 如果已经包含 # 前缀，直接使用
                selector = locator
            else:
                # 否则添加 # 前缀
                selector = f"#{locator}"
        elif locator_type == "xpath":
            # XPath 定位：添加 xpath= 前缀
            selector = f"xpath={locator}"
        elif locator_type == "css":
            # CSS Selector 定位：直接使用
            selector = locator
        elif locator_type == "name":
            # Name 属性定位：构建属性选择器
            selector = f"[name=\"{locator}\"]"
        elif locator_type == "class":
            # Class 名称定位：.classname
            if locator.startswith("."):
                # 如果已经包含 . 前缀，直接使用
                selector = locator
            else:
                # 否则添加 . 前缀
                selector = f".{locator}"
        else:
            # 不支持的定位类型，抛出异常
            raise ValueError(f"不支持的定位类型: {locator_type}")

        # 返回页面定位器对象
        return self.page.locator(selector)

    # ========== 步骤执行方法 ==========

    # 定义执行页面跳转的异步方法
    async def execute_navigate(self, url: str) -> dict:
        """
        执行页面跳转

        Args:
            url: 目标URL

        Returns:
            执行结果字典，包含 success 和 message
        """
        try:
            # 跳转到指定 URL，等待 DOM 内容加载完成
            await self.page.goto(url, wait_until="domcontentloaded")
            # 返回成功结果
            return {
                "success": True,  # 执行成功
                "message": f"成功跳转到: {url}",  # 成功消息
            }
        except Exception as e:
            # 捕获异常，返回失败结果
            return {
                "success": False,  # 执行失败
                "message": f"页面跳转失败: {str(e)}",  # 失败消息
                "error": str(e),  # 错误详情
            }

    # 定义执行点击操作的异步方法
    async def execute_click(self, locator_type: str, locator: str) -> dict:
        """
        执行点击操作

        Args:
            locator_type: 定位类型
            locator: 定位符

        Returns:
            执行结果字典
        """
        try:
            # 获取元素定位器
            element = await self._get_locator(locator_type, locator)
            # 点击元素，使用默认超时时间
            await element.click(timeout=DEFAULT_STEP_TIMEOUT)
            # 返回成功结果
            return {
                "success": True,  # 执行成功
                "message": f"成功点击元素: {locator}",  # 成功消息
            }
        except Exception as e:
            # 捕获异常，返回失败结果
            return {
                "success": False,  # 执行失败
                "message": f"点击元素失败: {locator}",  # 失败消息
                "error": str(e),  # 错误详情
            }

    # 定义执行输入文本的异步方法
    async def execute_input(self, locator_type: str, locator: str, text: str) -> dict:
        """
        执行输入文本操作

        Args:
            locator_type: 定位类型
            locator: 定位符
            text: 输入文本

        Returns:
            执行结果字典
        """
        try:
            # 获取元素定位器
            element = await self._get_locator(locator_type, locator)
            # 使用 fill 方法填充文本（会先清空原有内容）
            await element.fill(text)
            # 返回成功结果
            return {
                "success": True,  # 执行成功
                "message": f"成功输入文本: {text}",  # 成功消息
            }
        except Exception as e:
            # 捕获异常，返回失败结果
            return {
                "success": False,  # 执行失败
                "message": f"输入文本失败: {locator}",  # 失败消息
                "error": str(e),  # 错误详情
            }

    # 定义执行清除内容的异步方法
    async def execute_clear(self, locator_type: str, locator: str) -> dict:
        """
        执行清除内容操作

        Args:
            locator_type: 定位类型
            locator: 定位符

        Returns:
            执行结果字典
        """
        try:
            # 获取元素定位器
            element = await self._get_locator(locator_type, locator)
            # 清空元素内容
            await element.clear()
            # 返回成功结果
            return {
                "success": True,  # 执行成功
                "message": f"成功清除内容: {locator}",  # 成功消息
            }
        except Exception as e:
            # 捕获异常，返回失败结果
            return {
                "success": False,  # 执行失败
                "message": f"清除内容失败: {locator}",  # 失败消息
                "error": str(e),  # 错误详情
            }

    # 定义执行等待元素的异步方法
    async def execute_wait(self, locator_type: str, locator: str, timeout: int = DEFAULT_STEP_TIMEOUT) -> dict:
        """
        执行等待元素操作

        Args:
            locator_type: 定位类型
            locator: 定位符
            timeout: 超时时间（毫秒）

        Returns:
            执行结果字典
        """
        try:
            # 获取元素定位器
            element = await self._get_locator(locator_type, locator)
            # 等待元素可见（visible 状态）
            await element.wait_for(state="visible", timeout=timeout)
            # 返回成功结果
            return {
                "success": True,  # 执行成功
                "message": f"元素已可见: {locator}",  # 成功消息
            }
        except Exception as e:
            # 捕获异常，返回失败结果
            return {
                "success": False,  # 执行失败
                "message": f"等待元素超时: {locator}",  # 失败消息
                "error": str(e),  # 错误详情
            }

    # 定义执行验证文本的异步方法
    async def execute_verify_text(self, text: str) -> dict:
        """
        执行验证文本操作

        Args:
            text: 要验证的文本

        Returns:
            执行结果字典
        """
        try:
            # 等待页面包含指定文本的元素出现
            await self.page.wait_for_selector(f"text={text}", timeout=DEFAULT_STEP_TIMEOUT)
            # 返回成功结果
            return {
                "success": True,  # 执行成功
                "message": f"成功验证文本存在: {text}",  # 成功消息
            }
        except Exception as e:
            # 捕获异常，返回失败结果
            return {
                "success": False,  # 执行失败
                "message": f"验证文本失败: {text}",  # 失败消息
                "error": str(e),  # 错误详情
            }

    # 定义执行验证元素存在的异步方法
    async def execute_verify_element(self, locator_type: str, locator: str) -> dict:
        """
        执行验证元素存在操作

        Args:
            locator_type: 定位类型
            locator: 定位符

        Returns:
            执行结果字典
        """
        try:
            # 获取元素定位器
            element = await self._get_locator(locator_type, locator)
            # 使用 count() 方法检查元素是否存在
            count = await element.count()
            # 如果元素数量大于 0，说明元素存在
            if count > 0:
                return {
                    "success": True,  # 执行成功
                    "message": f"元素存在: {locator}",  # 成功消息
                }
            else:
                # 元素不存在
                return {
                    "success": False,  # 执行失败
                    "message": f"元素不存在: {locator}",  # 失败消息
                }
        except Exception as e:
            # 捕获异常，返回失败结果
            return {
                "success": False,  # 执行失败
                "message": f"验证元素失败: {locator}",  # 失败消息
                "error": str(e),  # 错误详情
            }

    # ========== 截图功能 ==========

    # 定义截取页面截图的异步方法
    async def take_screenshot(self, filename: str | None = None) -> str:
        """
        截取当前页面截图

        Args:
            filename: 截图文件名（不含路径）

        Returns:
            截图文件完整路径
        """
        # 检查页面是否已初始化
        if not self.page:
            raise RuntimeError("页面未初始化")

        # 如果未指定文件名，生成带时间戳的文件名
        if filename is None:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"

        # 构建截图文件的完整路径
        filepath = SCREENSHOTS_DIR / filename
        # 截取页面截图并保存到指定路径
        await self.page.screenshot(path=str(filepath))
        # 返回截图文件的完整路径
        return str(filepath)

    # 定义失败时截图的异步方法
    async def take_screenshot_on_error(self, error_info: dict) -> str:
        """
        失败时截图

        Args:
            error_info: 错误信息（当前未使用，保留用于扩展）

        Returns:
            截图文件路径
        """
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"error_{timestamp}.png"
        # 调用通用截图方法
        return await self.take_screenshot(filename)

    # ========== 执行控制器 ==========

    # 定义执行单个测试步骤的异步方法
    async def execute_step(self, step: dict) -> dict:
        """
        执行单个测试步骤

        Args:
            step: 步骤数据
                {
                    "action_type": "navigate/click/input/clear/wait/verify_text/verify_element",
                    "element_locator": "元素定位符",
                    "locator_type": "id/xpath/css/name/class",
                    "action_params": {"key": "value"}  # JSON参数
                }

        Returns:
            执行结果
                {
                    "success": True/False,
                    "message": "执行消息",
                    "error": "错误信息（如果失败）"
                }
        """
        # 从步骤数据中提取各字段
        action_type = step.get("action_type")  # 操作类型
        element_locator = step.get("element_locator")  # 元素定位符
        locator_type = step.get("locator_type", "css")  # 定位类型，默认 css
        action_params = step.get("action_params", {})  # 操作参数

        # 如果参数是 JSON 字符串，解析为字典
        if isinstance(action_params, str):
            action_params = json.loads(action_params) if action_params else {}

        # 初始化结果字典
        result = {"success": False, "message": ""}

        try:
            # 根据操作类型执行对应的操作
            if action_type == "navigate":
                # 页面跳转操作
                url = action_params.get("url")  # 从参数中获取 URL
                if not url:
                    # 如果没有提供 URL，抛出异常
                    raise ValueError("navigate操作需要url参数")
                result = await self.execute_navigate(url)  # 执行跳转

            elif action_type == "click":
                # 点击操作
                if not element_locator:
                    # 如果没有提供定位符，抛出异常
                    raise ValueError("click操作需要element_locator参数")
                result = await self.execute_click(locator_type, element_locator)  # 执行点击

            elif action_type == "input":
                # 输入文本操作
                if not element_locator:
                    # 如果没有提供定位符，抛出异常
                    raise ValueError("input操作需要element_locator参数")
                text = action_params.get("text", "")  # 从参数中获取输入文本
                result = await self.execute_input(locator_type, element_locator, text)  # 执行输入

            elif action_type == "clear":
                # 清除内容操作
                if not element_locator:
                    # 如果没有提供定位符，抛出异常
                    raise ValueError("clear操作需要element_locator参数")
                result = await self.execute_clear(locator_type, element_locator)  # 执行清除

            elif action_type == "wait":
                # 等待元素操作
                if not element_locator:
                    # 如果没有提供定位符，抛出异常
                    raise ValueError("wait操作需要element_locator参数")
                timeout = action_params.get("timeout", DEFAULT_STEP_TIMEOUT)  # 从参数中获取超时时间
                result = await self.execute_wait(locator_type, element_locator, timeout)  # 执行等待

            elif action_type == "verify_text":
                # 验证文本操作
                text = action_params.get("text")  # 从参数中获取要验证的文本
                if not text:
                    # 如果没有提供文本，抛出异常
                    raise ValueError("verify_text操作需要text参数")
                result = await self.execute_verify_text(text)  # 执行验证

            elif action_type == "verify_element":
                # 验证元素存在操作
                if not element_locator:
                    # 如果没有提供定位符，抛出异常
                    raise ValueError("verify_element操作需要element_locator参数")
                result = await self.execute_verify_element(locator_type, element_locator)  # 执行验证

            else:
                # 不支持的操作类型
                result = {
                    "success": False,  # 执行失败
                    "message": f"不支持的操作类型: {action_type}",  # 失败消息
                }

        except Exception as e:
            # 捕获执行过程中的异常
            result = {
                "success": False,  # 执行失败
                "message": f"执行步骤时发生异常: {action_type}",  # 失败消息
                "error": str(e),  # 错误详情
            }

        # 返回执行结果
        return result

    # 定义执行完整测试用例的异步方法
    async def execute_case(self, case_data: dict) -> dict:
        """
        执行完整的测试用例

        Args:
            case_data: 用例数据
                {
                    "id": 用例ID,
                    "name": "用例名称",
                    "steps": [步骤列表]
                }

        Returns:
            执行结果
                {
                    "success": True/False,
                    "total_steps": 步骤总数,
                    "success_steps": 成功步骤数,
                    "failed_steps": 失败步骤数,
                    "step_results": [每步结果],
                    "error": "错误信息（如果失败）"
                }
        """
        # 获取用例的步骤列表
        steps = case_data.get("steps", [])
        # 统计总步骤数
        total_steps = len(steps)
        # 初始化成功步骤计数器
        success_steps = 0
        # 初始化失败步骤计数器
        failed_steps = 0
        # 初始化步骤结果列表
        step_results = []

        # 遍历执行每个步骤
        for idx, step in enumerate(steps):
            # 获取步骤顺序（如果未指定则使用索引+1）
            step_order = step.get("step_order", idx + 1)
            # 执行步骤并获取结果
            step_result = await self.execute_step(step)
            # 将步骤顺序添加到结果中
            step_result["step_order"] = step_order
            # 将操作类型添加到结果中
            step_result["action_type"] = step.get("action_type")
            # 将步骤结果添加到结果列表
            step_results.append(step_result)

            # 判断步骤是否成功
            if step_result.get("success"):
                # 成功，增加成功计数
                success_steps += 1
            else:
                # 失败，增加失败计数
                failed_steps += 1
                # 失败时截图
                try:
                    # 调用失败截图方法
                    screenshot_path = await self.take_screenshot_on_error(step_result)
                    # 将截图路径添加到结果中
                    step_result["screenshot"] = screenshot_path
                except Exception as e:
                    # 截图失败，记录错误
                    step_result["screenshot_error"] = str(e)

        # 判断整体是否成功（没有失败的步骤即为成功）
        overall_success = failed_steps == 0

        # 返回执行结果汇总
        return {
            "success": overall_success,  # 整体成功状态
            "total_steps": total_steps,  # 总步骤数
            "success_steps": success_steps,  # 成功步骤数
            "failed_steps": failed_steps,  # 失败步骤数
            "step_results": step_results,  # 每步的详细结果
        }


# ========== 测试代码 ==========

# 定义测试主函数
async def main():
    """
    测试执行引擎

    演示如何使用 PlaywrightEngine 执行测试用例
    """
    # 创建执行引擎实例，使用 Chromium 浏览器，显示浏览器窗口
    engine = PlaywrightEngine(browser_type="chromium", headless=False)

    try:
        # 启动浏览器
        await engine.start_browser()
        print("Browser started successfully")  # 打印成功消息

        # 测试用例示例 - 使用 Playwright 官方演示网站
        test_case = {
            "id": 1,  # 用例 ID
            "name": "Test Case",  # 用例名称
            "steps": [  # 测试步骤列表
                {
                    "step_order": 1,  # 步骤顺序
                    "action_type": "navigate",  # 操作类型：跳转
                    "action_params": {"url": "https://playwright.dev"}  # 参数：目标 URL
                },
                {
                    "step_order": 2,  # 步骤顺序
                    "action_type": "verify_text",  # 操作类型：验证文本
                    "action_params": {"text": "Playwright"}  # 参数：要验证的文本
                },
            ]
        }

        # 执行测试用例
        result = await engine.execute_case(test_case)
        # 打印执行结果
        print(f"\nExecution Result:")
        print(f"Success: {result['success']}")  # 整体成功状态
        print(f"Total Steps: {result['total_steps']}")  # 总步骤数
        print(f"Success Steps: {result['success_steps']}")  # 成功步骤数
        print(f"Failed Steps: {result['failed_steps']}")  # 失败步骤数

        # 打印每步的详细结果
        for step_result in result.get('step_results', []):
            # 根据成功状态设置显示标记
            status = "[OK]" if step_result.get('success') else "[FAIL]"
            # 获取操作类型
            action = step_result.get('action_type')
            # 获取消息
            msg = step_result.get('message')
            # 打印步骤结果
            print(f"{status} Step {step_result.get('step_order')}: {action} - {msg}")
            # 如果步骤失败且有截图，打印截图路径
            if not step_result.get('success') and 'screenshot' in step_result:
                print(f"  Screenshot: {step_result['screenshot']}")

        # 等待查看结果
        print("\nWaiting 5 seconds to see the result...")
        await asyncio.sleep(5)  # 暂停 5 秒

    finally:
        # 无论成功或失败，都关闭浏览器
        await engine.close_browser()
        print("Browser closed")  # 打印关闭消息


# 判断是否以主程序方式运行
if __name__ == "__main__":
    # 运行测试主函数
    asyncio.run(main())
