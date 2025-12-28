"""
简单的 API 测试脚本
用于诊断后端问题
"""
import asyncio
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def main():
    """主测试函数"""
    print("开始测试...")
    try:
        # 导入主应用
        from app.main import app
        print("✓ 主应用导入成功")

        # 导入数据库
        from app.models.database import engine, init_db
        print("✓ 数据库模块导入成功")

        # 初始化数据库
        await init_db()
        print("✓ 数据库初始化成功")

        # 导入服务
        from app.services.case_service import case_service
        print("✓ 用例服务导入成功")

        # 创建测试会话
        from app.models.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            # 测试获取用例列表
            cases, total = await case_service.get_cases(db, page=1, page_size=20)
            print(f"✓ 获取用例列表成功: {len(cases)} 条记录, 总数 {total}")

        print("\n所有测试通过! ✓")

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # 关闭数据库
        from app.models.database import engine
        await engine.dispose()

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
