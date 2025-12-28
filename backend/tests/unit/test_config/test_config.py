"""
配置模块单元测试
"""
# 导入 pytest 测试框架，用于编写测试用例和断言
import pytest
# 导入 Path 路径处理类，用于路径验证
from pathlib import Path
# 从 app.config 模块导入所有需要测试的常量和函数
from app.config import (
    BASE_DIR,  # 项目根目录路径
    DATABASE_URL,  # 数据库连接 URL
    DEFAULT_BROWSER_TYPE,  # 默认浏览器类型
    DEFAULT_HEADLESS,  # 默认无头模式开关
    DEFAULT_WINDOW_SIZE,  # 默认窗口大小
    WINDOW_SIZES,  # 窗口大小配置字典
    SCREENSHOTS_DIR,  # 截图保存目录
    REPORTS_DIR,  # 报告保存目录
    DATA_DIR,  # 数据存储目录
    WS_HEARTBEAT_INTERVAL,  # WebSocket 心跳间隔
    DEFAULT_STEP_TIMEOUT,  # 默认步骤超时时间
    DEFAULT_NAVIGATION_TIMEOUT,  # 默认导航超时时间
    LOG_LEVEL,  # 日志级别
    LOG_FORMAT,  # 日志格式
    API_PREFIX,  # API 路由前缀
    CORS_ORIGINS,  # CORS 允许的源列表
    ACTION_TYPES,  # 支持的操作类型列表
    LOCATOR_TYPES,  # 支持的定位类型列表
    EXECUTION_STATUS,  # 执行状态列表
    CASE_STATUS,  # 用例状态列表
    PRIORITIES,  # 优先级列表
    get_window_size,  # 获取窗口大小的函数
    ensure_dirs,  # 确保目录存在的函数
)


class TestConfigConstants:
    """测试配置常量"""

    def test_base_dir_exists(self):
        """测试 BASE_DIR 存在"""
        # 验证 BASE_DIR 是 Path 对象
        assert isinstance(BASE_DIR, Path)
        # 验证 BASE_DIR 所指向的目录实际存在
        assert BASE_DIR.exists()

    def test_database_url(self):
        """测试数据库 URL"""
        # 验证数据库 URL 包含 "sqlite" 关键字
        assert "sqlite" in DATABASE_URL
        # 验证数据库 URL 包含数据库名 "uitool.db"
        assert "uitool.db" in DATABASE_URL

    def test_default_browser_type(self):
        """测试默认浏览器类型"""
        # 验证默认浏览器类型是 "chromium"
        assert DEFAULT_BROWSER_TYPE == "chromium"

    def test_default_headless(self):
        """测试默认无头模式"""
        # 验证默认无头模式开关为 True（不显示浏览器界面）
        assert DEFAULT_HEADLESS is True

    def test_default_window_size(self):
        """测试默认窗口大小"""
        # 验证默认窗口大小字符串为 "1920x1080"
        assert DEFAULT_WINDOW_SIZE == "1920x1080"

    def test_window_sizes_dict(self):
        """测试窗口大小映射"""
        # 验证 WINDOW_SIZES 是一个字典类型
        assert isinstance(WINDOW_SIZES, dict)
        # 验证包含 "1920x1080" 这个键
        assert "1920x1080" in WINDOW_SIZES
        # 验证对应的值是正确的宽高配置
        assert WINDOW_SIZES["1920x1080"] == {"width": 1920, "height": 1080}

    def test_screenshots_dir(self):
        """测试截图目录"""
        # 验证 SCREENSHOTS_DIR 是 Path 对象
        assert isinstance(SCREENSHOTS_DIR, Path)
        # 验证目录名称是 "screenshots"
        assert SCREENSHOTS_DIR.name == "screenshots"

    def test_reports_dir(self):
        """测试报告目录"""
        # 验证 REPORTS_DIR 是 Path 对象
        assert isinstance(REPORTS_DIR, Path)
        # 验证目录名称是 "reports"
        assert REPORTS_DIR.name == "reports"

    def test_data_dir(self):
        """测试数据目录"""
        # 验证 DATA_DIR 是 Path 对象
        assert isinstance(DATA_DIR, Path)
        # 验证目录名称是 "data"
        assert DATA_DIR.name == "data"

    def test_ws_heartbeat_interval(self):
        """测试 WebSocket 心跳间隔"""
        # 验证 WebSocket 心跳间隔为 30 秒
        assert WS_HEARTBEAT_INTERVAL == 30

    def test_default_step_timeout(self):
        """测试默认步骤超时"""
        # 验证默认步骤超时时间为 30000 毫秒（30 秒）
        assert DEFAULT_STEP_TIMEOUT == 30000

    def test_default_navigation_timeout(self):
        """测试默认导航超时"""
        # 验证默认导航超时时间为 30000 毫秒（30 秒）
        assert DEFAULT_NAVIGATION_TIMEOUT == 30000

    def test_log_level(self):
        """测试日志级别"""
        # 验证日志级别为 "INFO"
        assert LOG_LEVEL == "INFO"

    def test_log_format(self):
        """测试日志格式"""
        # 验证日志格式包含时间戳占位符
        assert "%(asctime)s" in LOG_FORMAT
        # 验证日志格式包含日志级别占位符
        assert "%(levelname)s" in LOG_FORMAT

    def test_api_prefix(self):
        """测试 API 前缀"""
        # 验证 API 路由前缀为 "/api/v1"
        assert API_PREFIX == "/api/v1"

    def test_cors_origins(self):
        """测试 CORS 源"""
        # 验证 CORS_ORIGINS 是一个列表
        assert isinstance(CORS_ORIGINS, list)
        # 验证包含本地开发服务器地址
        assert "http://localhost:5173" in CORS_ORIGINS


class TestConfigEnums:
    """测试枚举配置"""

    def test_action_types(self):
        """测试操作类型枚举"""
        # 验证 ACTION_TYPES 是一个列表
        assert isinstance(ACTION_TYPES, list)
        # 验证包含 "navigate" 操作类型（页面跳转）
        assert "navigate" in ACTION_TYPES
        # 验证包含 "click" 操作类型（点击元素）
        assert "click" in ACTION_TYPES
        # 验证包含 "input" 操作类型（输入文本）
        assert "input" in ACTION_TYPES
        # 验证包含 "clear" 操作类型（清空输入）
        assert "clear" in ACTION_TYPES
        # 验证包含 "wait" 操作类型（等待元素）
        assert "wait" in ACTION_TYPES
        # 验证包含 "verify_text" 操作类型（验证文本）
        assert "verify_text" in ACTION_TYPES
        # 验证包含 "verify_element" 操作类型（验证元素）
        assert "verify_element" in ACTION_TYPES

    def test_locator_types(self):
        """测试定位类型枚举"""
        # 验证 LOCATOR_TYPES 是一个列表
        assert isinstance(LOCATOR_TYPES, list)
        # 验证包含 "id" 定位类型（通过 ID 定位）
        assert "id" in LOCATOR_TYPES
        # 验证包含 "xpath" 定位类型（通过 XPath 定位）
        assert "xpath" in LOCATOR_TYPES
        # 验证包含 "css" 定位类型（通过 CSS 选择器定位）
        assert "css" in LOCATOR_TYPES
        # 验证包含 "name" 定位类型（通过 name 属性定位）
        assert "name" in LOCATOR_TYPES
        # 验证包含 "class" 定位类型（通过 class 属性定位）
        assert "class" in LOCATOR_TYPES

    def test_execution_status(self):
        """测试执行状态枚举"""
        # 验证 EXECUTION_STATUS 是一个列表
        assert isinstance(EXECUTION_STATUS, list)
        # 验证包含 "pending" 状态（等待执行）
        assert "pending" in EXECUTION_STATUS
        # 验证包含 "running" 状态（执行中）
        assert "running" in EXECUTION_STATUS
        # 验证包含 "completed" 状态（执行完成）
        assert "completed" in EXECUTION_STATUS
        # 验证包含 "failed" 状态（执行失败）
        assert "failed" in EXECUTION_STATUS

    def test_case_status(self):
        """测试用例状态枚举"""
        # 验证 CASE_STATUS 是一个列表
        assert isinstance(CASE_STATUS, list)
        # 验证包含 "success" 状态（执行成功）
        assert "success" in CASE_STATUS
        # 验证包含 "failed" 状态（执行失败）
        assert "failed" in CASE_STATUS
        # 验证包含 "skipped" 状态（跳过执行）
        assert "skipped" in CASE_STATUS

    def test_priorities(self):
        """测试优先级枚举"""
        # 验证 PRIORITIES 是一个列表
        assert isinstance(PRIORITIES, list)
        # 验证包含 "P0" 优先级（最高）
        assert "P0" in PRIORITIES
        # 验证包含 "P1" 优先级（高）
        assert "P1" in PRIORITIES
        # 验证包含 "P2" 优先级（中）
        assert "P2" in PRIORITIES
        # 验证包含 "P3" 优先级（低）
        assert "P3" in PRIORITIES


class TestGetWindowSize:
    """测试 get_window_size 函数"""

    def test_get_window_size_valid(self):
        """测试获取有效的窗口大小"""
        # 调用 get_window_size 函数获取窗口大小
        result = get_window_size("1920x1080")
        # 验证返回正确的宽高配置
        assert result == {"width": 1920, "height": 1080}

    def test_get_window_size_1366x768(self):
        """测试获取 1366x768 窗口大小"""
        # 获取 1366x768 分辨率
        result = get_window_size("1366x768")
        # 验证返回正确的宽高配置
        assert result == {"width": 1366, "height": 768}

    def test_get_window_size_2560x1440(self):
        """测试获取 2560x1440 窗口大小"""
        # 获取 2560x1440 分辨率（2K）
        result = get_window_size("2560x1440")
        # 验证返回正确的宽高配置
        assert result == {"width": 2560, "height": 1440}

    def test_get_window_size_1280x720(self):
        """测试获取 1280x720 窗口大小"""
        # 获取 1280x720 分辨率（720p）
        result = get_window_size("1280x720")
        # 验证返回正确的宽高配置
        assert result == {"width": 1280, "height": 720}

    def test_get_window_size_invalid(self):
        """测试获取无效的窗口大小（返回默认值）"""
        # 传入无效的窗口大小字符串
        result = get_window_size("invalid")
        # 验证返回默认的窗口大小 1920x1080
        assert result == {"width": 1920, "height": 1080}

    def test_get_window_size_empty(self):
        """测试获取空字符串窗口大小（返回默认值）"""
        # 传入空字符串
        result = get_window_size("")
        # 验证返回默认的窗口大小 1920x1080
        assert result == {"width": 1920, "height": 1080}


class TestEnsureDirs:
    """测试 ensure_dirs 函数"""

    def test_ensure_dirs_creates_screenshots(self):
        """测试 ensure_dirs 创建截图目录"""
        # ensure_dirs 在模块导入时已调用，直接验证目录存在
        assert SCREENSHOTS_DIR.exists()
        # 验证它确实是一个目录
        assert SCREENSHOTS_DIR.is_dir()

    def test_ensure_dirs_creates_reports(self):
        """测试 ensure_dirs 创建报告目录"""
        # 验证报告目录存在
        assert REPORTS_DIR.exists()
        # 验证它确实是一个目录
        assert REPORTS_DIR.is_dir()

    def test_ensure_dirs_creates_data(self):
        """测试 ensure_dirs 创建数据目录"""
        # 验证数据目录存在
        assert DATA_DIR.exists()
        # 验证它确实是一个目录
        assert DATA_DIR.is_dir()

    def test_ensure_dirs_idempotent(self):
        """测试 ensure_dirs 多次调用不会报错"""
        # 多次调用不应该报错（幂等性测试）
        ensure_dirs()  # 第一次调用
        ensure_dirs()  # 第二次调用
        ensure_dirs()  # 第三次调用

        # 验证目录仍然存在
        assert SCREENSHOTS_DIR.exists()
        # 验证报告目录仍然存在
        assert REPORTS_DIR.exists()
        # 验证数据目录仍然存在
        assert DATA_DIR.exists()
