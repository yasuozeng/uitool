"""
uiTool1.0 后端服务启动脚本
在 Windows 上正确启动 Playwright 兼容的 FastAPI 服务
"""
# 导入 sys 模块用于检测操作系统平台
import sys
# 导入 asyncio 异步编程模块
import asyncio

# ========== Windows 平台 Playwright 兼容性修复 ==========
# 必须在导入 uvicorn 或 FastAPI 之前设置事件循环策略
# 检测当前操作系统是否为 Windows
if sys.platform == 'win32':
    # 导入 Windows 专用的事件循环策略
    from asyncio import WindowsProactorEventLoopPolicy
    # 设置 Windows Proactor 事件循环策略
    # 这是 Playwright 在 Windows 上正常工作的必要条件
    # ProactorEventLoop 支持真正的子进程操作，而默认的 SelectorEventLoop 不支持
    # 注意：必须在任何异步操作（包括导入 uvicorn）之前设置
    asyncio.set_event_loop_policy(WindowsProactorEventLoopPolicy())
    print("[INFO] Windows ProactorEventLoopPolicy 已设置")

# 导入 uvicorn ASGI 服务器
import uvicorn

# 启动 uvicorn 开发服务器
if __name__ == "__main__":
    print("[INFO] 正在启动 uiTool1.0 后端服务...")
    # 启动服务器
    uvicorn.run(
        "app.main:app",  # 应用模块路径
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,  # 监听端口 8000
        reload=True,  # 开启自动重载（代码修改后自动重启）
        # 注意：reload 模式下，主进程和子进程都需要正确的策略设置
        # 因此 app.main.py 中也保留了策略设置代码
    )
