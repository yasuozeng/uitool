"""
uiTool1.0 FastAPI 主应用
"""
# 导入 sys 模块用于检测操作系统平台
import sys
# 导入 asyncio 异步编程模块
import asyncio
# 从 fastapi 框架导入 FastAPI 应用类
from fastapi import FastAPI
# 从 fastapi.middleware.cors 导入 CORS 中间件，用于处理跨域请求
from fastapi.middleware.cors import CORSMiddleware
# 从 fastapi.staticfiles 导入 StaticFiles 用于提供静态文件服务
from fastapi.staticfiles import StaticFiles
# 从 contextlib 导入 asynccontextmanager 装饰器，用于定义异步上下文管理器
from contextlib import asynccontextmanager

# 从本地配置模块导入 API 前缀、CORS 允许的来源列表和截图目录
from app.config import API_PREFIX, CORS_ORIGINS, SCREENSHOTS_DIR
# 从本地 API 路由模块导入用例、执行和报告相关的路由
from app.api import cases, executions, reports
# 从本地数据库模块导入数据库引擎和初始化函数
from app.models.database import engine, init_db

# ========== Windows 平台 Playwright 兼容性修复 ==========
# 检测当前操作系统是否为 Windows
if sys.platform == 'win32':
    # 导入 Windows 专用的事件循环策略
    from asyncio import WindowsProactorEventLoopPolicy
    # 设置 Windows Proactor 事件循环策略
    # 这是 Playwright 在 Windows 上正常工作的必要条件
    # ProactorEventLoop 支持真正的子进程操作，而默认的 SelectorEventLoop 不支持
    asyncio.set_event_loop_policy(WindowsProactorEventLoopPolicy())


# 使用 asynccontextmanager 装饰器定义应用生命周期管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理函数

    在应用启动时执行初始化操作，在应用关闭时执行清理操作
    """
    # 应用启动时：初始化数据库（创建表结构）
    await init_db()
    # 暂停执行，将控制权交给应用，应用在此期间运行
    yield
    # 应用关闭时：释放数据库连接池资源
    await engine.dispose()


# 创建 FastAPI 应用实例
app = FastAPI(
    title="uiTool1.0 API",  # API 标题，显示在文档页面
    description="轻量级 Web UI 自动化测试平台",  # API 描述信息
    version="1.0.0",  # API 版本号
    lifespan=lifespan  # 绑定生命周期管理器
)

# 配置 CORS（跨域资源共享）中间件，允许前端跨域访问 API
app.add_middleware(
    CORSMiddleware,  # CORS 中间件类
    allow_origins=CORS_ORIGINS,  # 允许的跨域来源列表（配置在 config.py）
    allow_credentials=True,  # 允许携带凭证（如 Cookie）
    allow_methods=["*"],  # 允许所有 HTTP 方法（GET、POST、PUT、DELETE 等）
    allow_headers=["*"],  # 允许所有请求头
)

# 注册用例管理相关的 API 路由
app.include_router(cases.router, prefix=API_PREFIX)  # 用例路由，路径前缀为 /api/v1
# 注册执行相关的 API 路由
app.include_router(executions.router, prefix=API_PREFIX)  # 执行路由，路径前缀为 /api/v1
# 注册报告相关的 API 路由
app.include_router(reports.router, prefix=API_PREFIX)  # 报告路由，路径前缀为 /api/v1

# 挂载静态文件服务，用于提供截图文件访问
app.mount("/api/screenshots", StaticFiles(directory=str(SCREENSHOTS_DIR)), name="screenshots")


# 定义根路径 GET 请求处理器，返回 API 基本信息
@app.get("/")
async def root():
    """
    根路径端点

    返回 API 的基本信息和文档链接
    """
    # 返回 JSON 格式的 API 信息
    return {
        "message": "uiTool1.0 API",  # API 欢迎消息
        "version": "1.0.0",  # API 版本
        "docs": "/docs",  # Swagger UI 文档地址
        "redoc": "/redoc"  # ReDoc 文档地址
    }


# 定义健康检查 GET 请求处理器
@app.get("/health")
async def health_check():
    """
    健康检查端点

    用于监控服务是否正常运行
    """
    # 返回健康状态
    return {"status": "healthy"}  # 状态为健康


# 判断是否以主程序方式运行（而非被导入）
if __name__ == "__main__":
    # 导入 uvicorn ASGI 服务器
    import uvicorn
    # 启动 uvicorn 开发服务器
    uvicorn.run(
        app,  # FastAPI 应用实例
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,  # 监听端口 8000
        reload=True  # 开启自动重载（代码修改后自动重启）
    )
