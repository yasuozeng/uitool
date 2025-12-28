"""
uiTool1.0 配置文件
"""
# 从 pathlib 导入 Path 类，用于处理文件路径
from pathlib import Path
# 从 typing 导入 Literal 类型，用于定义字面量类型约束
from typing import Literal

# 获取项目根目录：当前文件（app/config.py）的上级的上级（backend 目录）
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库配置
# 构建 SQLite 数据库连接 URL，使用 aiosqlite 异步驱动
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/data/uitool.db"

# 浏览器配置
# 定义浏览器类型字面量类型，只允许三种浏览器
BrowserType = Literal["chromium", "firefox", "webkit"]

# 默认浏览器类型设置为 Chromium
DEFAULT_BROWSER_TYPE: BrowserType = "chromium"
# 默认使用无头模式（不显示浏览器界面）
DEFAULT_HEADLESS = True
# 默认窗口大小为 1920x1080
DEFAULT_WINDOW_SIZE = "1920x1080"

# 浏览器窗口大小映射表：字符串配置到实际像素值
WINDOW_SIZES = {
    "1920x1080": {"width": 1920, "height": 1080},  # 标准 1080p
    "1366x768": {"width": 1366, "height": 768},    # 笔记本常用
    "2560x1440": {"width": 2560, "height": 1440},  # 2K 分辨率
    "1280x720": {"width": 1280, "height": 720},    # 720p 分辨率
}

# 存储路径配置
# 截图保存目录：backend/screenshots/
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
# 测试报告保存目录：backend/reports/
REPORTS_DIR = BASE_DIR / "reports"
# 数据存储目录：backend/data/
DATA_DIR = BASE_DIR / "data"

# WebSocket 配置
# WebSocket 心跳间隔：30 秒
WS_HEARTBEAT_INTERVAL = 30  # 心跳间隔（秒）

# 执行配置
# 单个测试步骤的默认超时时间：30000 毫秒（30 秒）
DEFAULT_STEP_TIMEOUT = 300000  # 默认步骤超时（毫秒）
# 页面导航的默认超时时间：30000 毫秒（30 秒）
DEFAULT_NAVIGATION_TIMEOUT = 300000  # 默认导航超时（毫秒）

# 日志配置
# 日志级别设置为 INFO
LOG_LEVEL = "INFO"
# 日志格式：包含时间、模块名、日志级别、消息
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# API 配置
# API 路由前缀
API_PREFIX = "/api/v1"
# CORS 允许的跨域来源列表（前端开发服务器）
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite 开发服务器默认端口
    "http://localhost:5174",  # 备用端口
    "http://localhost:5175",  # 备用端口
    "http://localhost:3000",  # 常用的开发服务器端口
    "http://127.0.0.1:5173",  # localhost 的 IP 形式
    "http://127.0.0.1:5174",  # localhost 的 IP 形式
    "http://127.0.0.1:5175",  # localhost 的 IP 形式
    "http://127.0.0.1:3000",  # localhost 的 IP 形式
]

# 操作类型枚举：支持的测试操作类型列表
ACTION_TYPES = [
    "navigate",   # 页面跳转操作
    "click",      # 点击元素操作
    "input",      # 输入文本操作
    "clear",      # 清除内容操作
    "wait",       # 等待元素操作
    "verify_text",  # 验证文本存在操作
    "verify_element",  # 验证元素存在操作
]

# 定位类型枚举：支持的元素定位方式列表
LOCATOR_TYPES = [
    "id",        # 通过 ID 属性定位元素
    "xpath",     # 通过 XPath 表达式定位元素
    "css",       # 通过 CSS 选择器定位元素
    "name",      # 通过 name 属性定位元素
    "class",     # 通过 class 属性定位元素
]

# 执行状态枚举：测试执行的状态列表
EXECUTION_STATUS = [
    "pending",   # 等待执行
    "running",   # 执行中
    "completed", # 执行完成
    "failed",    # 执行失败
]

# 用例执行状态枚举：单个用例的执行结果状态
CASE_STATUS = [
    "success",   # 执行成功
    "failed",    # 执行失败
    "skipped",   # 跳过执行
]

# 优先级枚举：测试用例的优先级列表
PRIORITIES = ["P0", "P1", "P2", "P3"]  # P0 最高，P3 最低


def get_window_size(size_str: str) -> dict:
    """
    获取窗口大小配置

    Args:
        size_str: 窗口大小字符串（如 "1920x1080"）

    Returns:
        包含 width 和 height 的字典
    """
    # 从映射表中获取窗口大小，如果不存在则返回默认值 1920x1080
    return WINDOW_SIZES.get(size_str, WINDOW_SIZES["1920x1080"])


# 确保目录存在
def ensure_dirs():
    """
    确保必要的目录存在

    在应用启动时创建截图、报告和数据目录
    """
    # 创建截图目录（如果不存在），parents=True 自动创建父目录
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    # 创建报告目录
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    # 创建数据目录
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# 模块导入时自动执行：确保必要目录已创建
ensure_dirs()
