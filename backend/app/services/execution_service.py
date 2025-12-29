"""
测试执行业务逻辑服务
提供测试执行任务的创建、启动、停止和查询功能
"""
# 导入 asyncio 异步编程模块
import asyncio
# 从 typing 模块导入类型注解工具
from typing import List, Optional
# 从 datetime 模块导入 datetime 类，用于时间戳
from datetime import datetime
# 从 sqlalchemy.ext.asyncio 导入异步会话
from sqlalchemy.ext.asyncio import AsyncSession
# 从 sqlalchemy 导入查询相关函数
from sqlalchemy import select, func
# 从 sqlalchemy.orm 导入预加载选项
from sqlalchemy.orm import selectinload
# 从本地模型模块导入执行相关模型
from app.models.execution import Execution, ExecutionDetail
# 从本地模型模块导入用例模型
from app.models.case import TestCase
# 从本地 schemas 模块导入执行相关的数据验证模式
from app.schemas.execution import ExecutionCreate
# 从本地引擎模块导入 Playwright 执行引擎
from app.engines.playwright_engine import PlaywrightEngine
# 从本地配置模块导入窗口大小获取函数
from app.config import get_window_size


# 定义测试执行服务类
class ExecutionService:
    """
    测试执行服务

    封装测试执行任务的创建、启动、停止和查询逻辑
    """

    def __init__(self):
        # 初始化正在执行的任务字典，格式：{execution_id: engine}
        self._running_executions = {}  # 存储正在执行的任务 {execution_id: engine}

    # 定义获取执行列表的异步方法
    async def get_executions(
        self,
        db: AsyncSession,  # 数据库会话
        status: Optional[str] = None,  # 按状态筛选
        browser_type: Optional[str] = None,  # 按浏览器类型筛选
        page: int = 1,  # 页码，默认第 1 页
        page_size: int = 20  # 每页数量，默认 20 条
    ) -> tuple[List[Execution], int]:
        """
        获取执行列表（分页）

        支持按状态和浏览器类型筛选，支持分页

        Returns:
            (执行列表, 总数) 元组
        """
        # 构建基础查询：查询 Execution 表
        query = select(Execution)

        # 添加筛选条件
        if status:
            # 如果提供了状态参数，添加精确匹配条件
            query = query.where(Execution.status == status)
        if browser_type:
            # 如果提供了浏览器类型参数，添加精确匹配条件
            query = query.where(Execution.browser_type == browser_type)

        # 构建统计总数的查询（使用子查询）
        count_query = select(func.count()).select_from(query.subquery())
        # 执行统计查询
        total_result = await db.execute(count_query)
        # 获取总数，如果没有结果则返回 0
        total = total_result.scalar() or 0

        # 添加排序：按创建时间倒序排列（最新的在前）
        query = query.order_by(Execution.created_at.desc())
        # 添加分页：计算偏移量并限制返回数量
        query = query.offset((page - 1) * page_size).limit(page_size)

        # 执行分页查询
        result = await db.execute(query)
        # 获取所有结果
        executions = result.scalars().all()

        # 返回执行列表和总数
        return list(executions), total

    # 定义根据 ID 获取执行记录的异步方法
    async def get_execution_by_id(
        self,
        db: AsyncSession,  # 数据库会话
        execution_id: int  # 执行 ID
    ) -> Optional[Execution]:
        """
        根据 ID 获取执行记录

        包括执行的所有详情记录

        Returns:
            执行对象（包含详情）或 None
        """
        # 构建查询：查询指定 ID 的执行记录
        # selectinload 用于预加载关联的 details 数据，避免 N+1 查询问题
        query = select(Execution).options(
            selectinload(Execution.details)
        ).where(Execution.id == execution_id)

        # 执行查询
        result = await db.execute(query)
        # 返回单个结果或 None
        return result.scalar_one_or_none()

    # 定义创建执行任务的异步方法
    async def create_execution(
        self,
        db: AsyncSession,  # 数据库会话
        execution_data: ExecutionCreate  # 执行创建数据
    ) -> Execution:
        """
        创建执行任务

        根据执行类型确定要执行的用例列表，创建执行记录

        Args:
            db: 数据库会话
            execution_data: 执行创建数据

        Returns:
            创建的执行对象
        """
        # 获取要执行的用例
        if execution_data.execution_type == "single":
            # 单个用例执行模式
            case_ids = execution_data.case_ids or []  # 获取用例 ID 列表
            if not case_ids:
                # 如果没有指定用例，取第一个用例
                case_query = select(TestCase).limit(1)
                case_result = await db.execute(case_query)
                case = case_result.scalar_one_or_none()
                if case:
                    # 如果找到了用例，使用其 ID
                    case_ids = [case.id]
        else:
            # 批量执行模式
            case_ids = execution_data.case_ids or []  # 获取用例 ID 列表
            if not case_ids:
                # 如果没有指定，获取所有用例
                case_query = select(TestCase)
                case_result = await db.execute(case_query)
                # 提取所有用例的 ID
                case_ids = [c.id for c in case_result.scalars().all()]

        # 创建执行记录对象
        db_execution = Execution(
            execution_type=execution_data.execution_type,  # 执行类型
            browser_type=execution_data.browser_type,  # 浏览器类型
            headless=execution_data.headless,  # 无头模式
            window_size=execution_data.window_size,  # 窗口大小
            total_count=len(case_ids),  # 总用例数
            status="pending"  # 初始状态为等待
        )
        # 保存用例 ID 列表到执行记录（转换为 JSON 字符串存储）
        db_execution.set_case_ids(case_ids)

        # 将执行记录添加到会话
        db.add(db_execution)
        # 提交事务到数据库
        await db.commit()
        # 刷新执行记录以获取数据库生成的 ID
        await db.refresh(db_execution)

        # 返回创建的执行记录
        return db_execution

    # 定义启动执行任务的异步方法
    async def start_execution(
        self,
        db: AsyncSession,  # 数据库会话
        execution_id: int  # 执行 ID
    ) -> Optional[Execution]:
        """
        启动执行任务

        获取要执行的用例，创建 Playwright 引擎，使用 asyncio 任务异步执行测试

        Args:
            db: 数据库会话
            execution_id: 执行 ID

        Returns:
            执行对象或 None
        """
        # 获取执行记录
        execution = await self.get_execution_by_id(db, execution_id)
        # 如果执行记录不存在，返回 None
        if not execution:
            return None

        # 获取要执行的用例
        # 从执行记录中获取存储的用例 ID 列表
        case_ids = execution.case_ids_list
        if not case_ids:
            # 如果没有用例 ID 列表，返回错误
            execution.status = "failed"  # 标记为失败
            execution.end_time = datetime.now()  # 记录结束时间
            await db.commit()
            return None

        # 根据用例 ID 列表查询用例，并预加载步骤（避免任务中的懒加载问题）
        # selectinload 用于预加载关联的 steps 数据，避免 DetachedInstanceError
        case_query = select(TestCase).options(
            selectinload(TestCase.steps)
        ).where(TestCase.id.in_(case_ids))

        # 执行查询获取用例列表
        case_result = await db.execute(case_query)
        cases = case_result.scalars().all()

        # 解析窗口大小配置
        window_size = get_window_size(execution.window_size or "1920x1080")
        # 映射浏览器类型：API 使用 chrome/firefox/edge，引擎使用 chromium/firefox/webkit
        browser_type_mapping = {
            "chrome": "chromium",
            "firefox": "firefox",
            "edge": "webkit"
        }
        engine_browser_type = browser_type_mapping.get(execution.browser_type, execution.browser_type)
        # 创建 Playwright 引擎实例
        engine = PlaywrightEngine(
            browser_type=engine_browser_type,  # 映射后的浏览器类型
            headless=execution.headless,  # 无头模式
            window_size=execution.window_size  # 窗口大小
        )

        # 保存引擎引用到正在执行的任务字典
        self._running_executions[execution_id] = engine

        # 更新执行状态为运行中
        execution.status = "running"
        # 记录开始时间
        execution.start_time = datetime.now()
        # 提交更改到数据库
        await db.commit()

        # 添加调试日志：使用 print 确保能看到
        print(f"[DEBUG] start_execution: execution_id={execution.id}, cases_count={len(cases)}")
        # 添加调试日志：写入文件测试文件写入是否工作
        from pathlib import Path
        log_file = Path(__file__).parent.parent / "debug.log"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[DEBUG] start_execution: 准备创建后台任务, execution_id={execution.id}, cases_count={len(cases)}\n")
                f.flush()
        except Exception as e:
            print(f"[ERROR] 无法写入日志文件: {e}")

        # 使用 asyncio.create_task 异步执行测试
        # 添加任务包装器，用于捕获后台任务中的异常
        async def task_wrapper():
            # 记录任务开始
            import sys
            from pathlib import Path
            # 使用绝对路径写入日志文件
            log_file = Path(__file__).parent.parent / "debug.log"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[DEBUG] task_wrapper 开始: execution_id={execution.id}\n")
                f.flush()  # 立即刷新缓冲区

            try:
                await self._run_execution(execution.id, cases, engine)
            except Exception as e:
                # 捕获任务级别的异常
                import traceback
                from pathlib import Path
                # 将错误信息写入文件，确保能被看到
                log_file = Path(__file__).parent.parent / "debug.log"
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[ERROR] 后台任务异常: execution_id={execution.id}\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write(f"Traceback:\n{traceback.format_exc()}\n")
                    f.flush()  # 立即刷新缓冲区

        # 创建并启动后台任务
        # 添加日志：准备创建任务
        print(f"[DEBUG] start_execution: 准备创建后台任务, execution_id={execution.id}, cases_count={len(cases)}")

        task = asyncio.create_task(task_wrapper())
        # 保存任务引用，防止被垃圾回收
        # 在 async 中，asyncio.create_task() 创建的任务需要保持引用，否则可能被垃圾回收
        self._running_executions[execution_id] = engine  # 引擎已经在上面保存了，这里只需确保任务运行
        # 任务引用保存到服务实例中，防止被垃圾回收
        if not hasattr(self, '_tasks'):
            self._tasks = {}  # 任务字典：{execution_id: task}
        self._tasks[execution_id] = task

        # 添加日志：任务已创建
        print(f"[DEBUG] start_execution: 后台任务已创建, task_id={id(task)}, execution_id={execution.id}")

        # 返回执行记录
        return execution

    # 定义执行测试用例的私有异步方法（后台任务）
    async def _run_execution(
        self,
        execution_id: int,  # 执行 ID
        cases: List[TestCase],  # 用例列表
        engine: PlaywrightEngine  # Playwright 引擎
    ):
        """
        执行测试用例（后台任务）

        遍历执行每个测试用例，记录执行结果

        Args:
            execution_id: 执行 ID
            cases: 用例列表
            engine: Playwright 引擎
        """
        # 添加调试日志：记录方法入口，写入文件确保能看到
        import sys
        from pathlib import Path
        # 使用绝对路径写入日志文件
        log_file = Path(__file__).parent.parent / "debug.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[DEBUG] _run_execution 被调用: execution_id={execution_id}, cases_count={len(cases)}\n")
            f.flush()  # 立即刷新缓冲区
        sys.stderr.write(f"[DEBUG] _run_execution 被调用: execution_id={execution_id}, cases_count={len(cases)}\n")
        sys.stderr.flush()

        # 创建新的数据库会话，避免使用请求会话（可能已关闭）
        from app.models.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            try:
                # 重新获取执行记录（在新会话中）
                result = await db.execute(select(Execution).where(Execution.id == execution_id))
                execution = result.scalar_one_or_none()
                if not execution:
                    return  # 执行记录不存在，退出

                # 启动浏览器
                await engine.start_browser()

                # 初始化计数器
                success_count = 0  # 成功用例数
                fail_count = 0  # 失败用例数

                # 遍历执行每个用例
                for case in cases:
                    # 创建执行详情记录
                    detail = ExecutionDetail(
                        execution_id=execution.id,  # 关联执行记录
                        case_id=case.id,  # 用例 ID
                        case_name=case.name,  # 用例名称
                        status="running",  # 初始状态为运行中
                        start_time=datetime.now()  # 开始时间
                    )
                    # 将详情添加到会话
                    db.add(detail)
                    # 提交到数据库
                    await db.commit()

                    # 构建用例数据，包含步骤信息
                    case_data = {
                        "id": case.id,  # 用例 ID
                        "name": case.name,  # 用例名称
                        "steps": [  # 步骤列表
                            {
                                "step_order": s.step_order,  # 步骤顺序
                                "action_type": s.action_type,  # 操作类型
                                "element_locator": s.element_locator,  # 元素定位符
                                "locator_type": s.locator_type,  # 定位类型
                                "action_params": s.params_dict,  # 操作参数（解析后的字典）
                            }
                            for s in case.steps  # 遍历用例的所有步骤
                        ]
                    }

                    # 使用引擎执行用例
                    result = await engine.execute_case(case_data)

                    # 更新执行详情
                    detail.end_time = datetime.now()  # 结束时间
                    # 保存步骤日志（使用 set_logs 方法自动转换为 JSON）
                    detail.set_logs(result.get("step_results", []))

                    # 判断执行结果
                    if result["success"]:
                        # 用例执行成功
                        detail.status = "success"
                        success_count += 1  # 增加成功计数
                    else:
                        # 用例执行失败
                        detail.status = "failed"
                        fail_count += 1  # 增加失败计数
                        # 失败时截图
                        try:
                            # 调用失败截图方法
                            screenshot_path = await engine.take_screenshot_on_error(result)
                            # 保存截图路径
                            detail.screenshot_path = screenshot_path
                        except Exception:
                            # 截图失败时忽略，继续执行
                            pass

                    # 提交详情更新到数据库
                    await db.commit()

                # 更新执行记录的汇总信息
                execution.success_count = success_count  # 成功用例数
                execution.fail_count = fail_count  # 失败用例数
                # 根据失败数确定最终状态
                execution.status = "completed" if fail_count == 0 else "failed"
                # 记录结束时间
                execution.end_time = datetime.now()
                # 提交执行记录更新到数据库
                await db.commit()

            except Exception as e:
                # 捕获执行过程中的异常
                import traceback
                import sys
                from pathlib import Path
                # 打印完整的异常堆栈信息到 stderr，确保能看到错误
                traceback.print_exc()
                sys.stderr.write(f"[ERROR] 执行失败: execution_id={execution_id}, error={str(e)}\n")
                sys.stderr.flush()
                # 同时写入日志文件
                log_file = Path(__file__).parent.parent / "debug.log"
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[ERROR] 执行失败: execution_id={execution_id}, error={str(e)}\n")
                    f.write(f"Traceback:\n{traceback.format_exc()}\n")
                    f.flush()
                # 重新获取执行记录并更新状态
                result = await db.execute(select(Execution).where(Execution.id == execution_id))
                execution = result.scalar_one_or_none()
                if execution:
                    execution.status = "failed"  # 标记为失败
                    execution.end_time = datetime.now()  # 记录结束时间
                    await db.commit()

            finally:
                # 无论成功或失败，都执行清理操作
                # 关闭浏览器
                try:
                    await engine.close_browser()
                except Exception:
                    # 关闭浏览器失败时忽略
                    pass

                # 清除引擎引用和任务引用
                self._running_executions.pop(execution_id, None)
                self._tasks.pop(execution_id, None)

    # 定义停止执行任务的异步方法
    async def stop_execution(self, db: AsyncSession, execution_id: int) -> bool:
        """
        停止执行任务

        关闭浏览器，更新执行状态为失败

        Args:
            db: 数据库会话
            execution_id: 执行 ID

        Returns:
            是否停止成功
        """
        # 获取执行记录
        execution = await self.get_execution_by_id(db, execution_id)
        # 如果执行记录不存在，返回 False
        if not execution:
            return False

        # 关闭浏览器以停止执行
        engine = self._running_executions.get(execution_id)
        if engine:
            # 如果引擎存在，尝试关闭浏览器
            try:
                await engine.close_browser()
            except Exception:
                # 关闭失败时忽略
                pass

        # 更新执行状态
        execution.status = "failed"  # 标记为失败
        execution.end_time = datetime.now()  # 记录结束时间

        # 清除引擎引用
        self._running_executions.pop(execution_id, None)
        # 提交更改到数据库
        await db.commit()

        # 返回停止成功
        return True

    # 定义获取正在运行的引擎的方法
    def get_running_engine(self, execution_id: int) -> Optional[PlaywrightEngine]:
        """
        获取正在运行的引擎

        Args:
            execution_id: 执行 ID

        Returns:
            Playwright 引擎或 None
        """
        # 从正在执行的任务字典中获取引擎
        return self._running_executions.get(execution_id)


# 创建全局服务实例，供其他模块导入使用
execution_service = ExecutionService()
