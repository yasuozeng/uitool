"""
数据库初始化脚本
"""
import sys
import asyncio

# Windows 平台事件循环策略设置
if sys.platform == 'win32':
    from asyncio import WindowsProactorEventLoopPolicy
    asyncio.set_event_loop_policy(WindowsProactorEventLoopPolicy())

# 导入数据库初始化函数
from app.models.database import init_db
# 导入所有模型，确保 SQLAlchemy 能识别它们并创建对应的表
# 必须在调用 init_db() 之前导入，否则不会创建任何表
from app.models.case import TestCase, TestStep  # 导入测试用例和测试步骤模型
from app.models.execution import Execution, ExecutionDetail  # 导入执行记录和执行详情模型
from app.models.ai_config import AIConfig  # 导入 AI 配置模型

# 运行初始化
async def main():
    # 调用初始化函数，创建所有数据库表
    # 此时所有模型已导入，Base.metadata 能识别所有需要创建的表
    await init_db()
    print("数据库初始化成功！")

if __name__ == "__main__":
    asyncio.run(main())
