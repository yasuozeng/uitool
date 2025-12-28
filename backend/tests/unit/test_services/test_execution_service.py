"""
测试执行服务测试
测试 ExecutionService 的所有业务逻辑方法
"""
# 导入 pytest 测试框架和异步标记
import pytest
# 从 unittest.mock 导入 AsyncMock
from unittest.mock import AsyncMock, patch
# 从 sqlalchemy 导入查询相关函数
from sqlalchemy import select

# 导入执行服务
from app.services.execution_service import execution_service
# 导入数据模式
from app.schemas.execution import ExecutionCreate
# 导入模型
from app.models.execution import Execution, ExecutionDetail
from app.models.case import TestCase


class TestExecutionServiceGetExecutions:
    """测试获取执行列表方法"""

    @pytest.mark.asyncio
    async def test_get_executions_empty(self, db_session):
        """测试空列表"""
        # 调用服务方法获取空列表
        executions, total = await execution_service.get_executions(db_session)

        # 验证：列表为空
        assert executions == []
        # 验证：总数为 0
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_executions_with_data(self, db_session):
        """测试有数据的情况"""
        # 创建测试数据：插入 3 条执行记录
        for i in range(1, 4):
            execution = Execution(
                execution_type="batch",
                browser_type="chrome",
                headless=True,
                total_count=10,
                status="completed"
            )
            db_session.add(execution)
        await db_session.commit()

        # 调用服务方法获取列表
        executions, total = await execution_service.get_executions(db_session)

        # 验证：返回 3 条记录
        assert len(executions) == 3
        # 验证：总数为 3
        assert total == 3

    @pytest.mark.asyncio
    async def test_get_executions_with_status_filter(self, db_session):
        """测试按状态筛选"""
        # 创建测试数据（不同状态）
        exec1 = Execution(execution_type="batch", browser_type="chrome", status="pending")
        exec2 = Execution(execution_type="batch", browser_type="chrome", status="running")
        exec3 = Execution(execution_type="batch", browser_type="chrome", status="pending")
        db_session.add_all([exec1, exec2, exec3])
        await db_session.commit()

        # 按状态筛选
        executions, total = await execution_service.get_executions(db_session, status="pending")

        # 验证：返回 2 条 pending 状态的记录
        assert len(executions) == 2
        assert total == 2
        for e in executions:
            assert e.status == "pending"

    @pytest.mark.asyncio
    async def test_get_executions_with_browser_filter(self, db_session):
        """测试按浏览器类型筛选"""
        # 创建测试数据（不同浏览器）
        exec1 = Execution(execution_type="batch", browser_type="chrome", status="pending")
        exec2 = Execution(execution_type="batch", browser_type="firefox", status="pending")
        exec3 = Execution(execution_type="batch", browser_type="chrome", status="pending")
        db_session.add_all([exec1, exec2, exec3])
        await db_session.commit()

        # 按浏览器类型筛选
        executions, total = await execution_service.get_executions(db_session, browser_type="chrome")

        # 验证：返回 2 条 chrome 类型的记录
        assert len(executions) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_get_executions_pagination(self, db_session):
        """测试分页"""
        # 创建 25 条测试数据
        for i in range(25):
            execution = Execution(
                execution_type="batch",
                browser_type="chrome",
                status="pending"
            )
            db_session.add(execution)
        await db_session.commit()

        # 获取第 1 页（每页 10 条）
        executions, total = await execution_service.get_executions(db_session, page=1, page_size=10)

        # 验证：总数 25，第 1 页 10 条
        assert total == 25
        assert len(executions) == 10


class TestExecutionServiceGetExecutionById:
    """测试根据 ID 获取执行记录方法"""

    @pytest.mark.asyncio
    async def test_get_execution_by_id_exists(self, db_session):
        """测试获取存在的执行记录"""
        # 创建测试数据
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="pending"
        )
        db_session.add(execution)
        await db_session.commit()
        await db_session.refresh(execution)

        # 调用服务方法
        result = await execution_service.get_execution_by_id(db_session, execution.id)

        # 验证：返回的执行记录正确
        assert result is not None
        assert result.id == execution.id
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_get_execution_by_id_not_exists(self, db_session):
        """测试获取不存在的执行记录"""
        # 调用服务方法（ID 不存在）
        result = await execution_service.get_execution_by_id(db_session, 999)

        # 验证：返回 None
        assert result is None

    @pytest.mark.asyncio
    async def test_get_execution_by_id_with_details(self, db_session):
        """测试获取执行记录及其详情"""
        # 创建测试数据（执行记录 + 详情）
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="completed"
        )
        db_session.add(execution)
        await db_session.commit()
        await db_session.refresh(execution)

        # 添加详情
        detail1 = ExecutionDetail(
            execution_id=execution.id,
            case_id=1,
            case_name="用例1",
            status="success"
        )
        detail2 = ExecutionDetail(
            execution_id=execution.id,
            case_id=2,
            case_name="用例2",
            status="failed"
        )
        db_session.add_all([detail1, detail2])
        await db_session.commit()

        # 调用服务方法
        result = await execution_service.get_execution_by_id(db_session, execution.id)

        # 验证：执行记录包含详情
        assert result is not None
        assert len(result.details) == 2


class TestExecutionServiceCreateExecution:
    """测试创建执行任务方法"""

    @pytest.mark.asyncio
    async def test_create_execution_batch_with_cases(self, db_session):
        """测试创建批量执行任务（指定用例）"""
        # 创建测试用例
        case1 = TestCase(name="用例1")
        case2 = TestCase(name="用例2")
        case3 = TestCase(name="用例3")
        db_session.add_all([case1, case2, case3])
        await db_session.commit()

        # 创建执行数据
        execution_data = ExecutionCreate(
            execution_type="batch",
            browser_type="chrome",
            headless=True,
            case_ids=[case1.id, case2.id, case3.id]
        )

        # 调用服务方法
        result = await execution_service.create_execution(db_session, execution_data)

        # 验证：执行任务创建成功
        assert result is not None
        assert result.id > 0
        assert result.execution_type == "batch"
        assert result.total_count == 3
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_create_execution_batch_all_cases(self, db_session):
        """测试创建批量执行任务（所有用例）"""
        # 创建测试用例
        for i in range(1, 6):
            case = TestCase(name=f"用例{i}")
            db_session.add(case)
        await db_session.commit()

        # 创建执行数据（不指定用例，获取所有）
        execution_data = ExecutionCreate(
            execution_type="batch",
            browser_type="firefox",
            case_ids=None
        )

        # 调用服务方法
        result = await execution_service.create_execution(db_session, execution_data)

        # 验证：获取所有用例
        assert result.total_count == 5

    @pytest.mark.asyncio
    async def test_create_execution_single(self, db_session):
        """测试创建单个执行任务"""
        # 创建测试用例
        case = TestCase(name="单个用例")
        db_session.add(case)
        await db_session.commit()

        # 创建执行数据
        execution_data = ExecutionCreate(
            execution_type="single",
            browser_type="chrome",
            case_ids=[case.id]
        )

        # 调用服务方法
        result = await execution_service.create_execution(db_session, execution_data)

        # 验证：单个执行创建成功
        assert result.execution_type == "single"
        assert result.total_count == 1

    @pytest.mark.asyncio
    async def test_create_execution_default_values(self, db_session):
        """测试默认值"""
        # 创建执行数据（只传必填字段）
        execution_data = ExecutionCreate(
            execution_type="batch"
        )

        # 调用服务方法
        result = await execution_service.create_execution(db_session, execution_data)

        # 验证：默认值正确
        assert result.browser_type == "chrome"
        assert result.headless is True
        assert result.status == "pending"


class TestExecutionServiceStartExecution:
    """测试启动执行任务方法"""

    @pytest.mark.asyncio
    async def test_start_execution_success(self, db_session):
        """测试成功启动执行任务"""
        # 创建测试用例
        case = TestCase(name="测试用例")
        db_session.add(case)
        await db_session.commit()

        # 创建执行记录
        execution = Execution(
            execution_type="single",
            browser_type="chrome",
            headless=True,
            total_count=1,
            status="pending"
        )
        db_session.add(execution)
        await db_session.commit()
        await db_session.refresh(execution)

        # 创建执行详情
        detail = ExecutionDetail(
            execution_id=execution.id,
            case_id=case.id,
            case_name=case.name,
            status="pending"
        )
        db_session.add(detail)
        await db_session.commit()

        # Mock PlaywrightEngine
        with patch('app.services.execution_service.PlaywrightEngine') as MockEngine:
            # 配置 Mock
            mock_engine = AsyncMock()
            mock_engine.start_browser = AsyncMock()
            mock_engine.close_browser = AsyncMock()
            mock_engine.execute_case = AsyncMock(return_value={
                "success": True,
                "total_steps": 0,
                "success_steps": 0,
                "failed_steps": 0,
                "step_results": []
            })
            MockEngine.return_value = mock_engine

            # 调用服务方法
            result = await execution_service.start_execution(db_session, execution.id)

            # 验证：执行状态更新为运行中
            assert result is not None
            assert result.status == "running"

    @pytest.mark.asyncio
    async def test_start_execution_not_exists(self, db_session):
        """测试启动不存在的执行任务"""
        # 调用服务方法（ID 不存在）
        result = await execution_service.start_execution(db_session, 999)

        # 验证：返回 None
        assert result is None


class TestExecutionServiceStopExecution:
    """测试停止执行任务方法"""

    @pytest.mark.asyncio
    async def test_stop_execution_success(self, db_session):
        """测试成功停止执行任务"""
        # 创建执行记录
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="running"
        )
        db_session.add(execution)
        await db_session.commit()
        await db_session.refresh(execution)

        # Mock 引擎（模拟正在运行）
        mock_engine = AsyncMock()
        execution_service._running_executions[execution.id] = mock_engine

        # 调用服务方法
        success = await execution_service.stop_execution(db_session, execution.id)

        # 验证：停止成功
        assert success is True

        # 验证：状态更新为失败
        await db_session.refresh(execution)
        assert execution.status == "failed"

    @pytest.mark.asyncio
    async def test_stop_execution_not_exists(self, db_session):
        """测试停止不存在的执行任务"""
        # 调用服务方法（ID 不存在）
        success = await execution_service.stop_execution(db_session, 999)

        # 验证：返回 False
        assert success is False

    @pytest.mark.asyncio
    async def test_stop_execution_no_engine(self, db_session):
        """测试停止没有引擎的执行任务"""
        # 创建执行记录
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="running"
        )
        db_session.add(execution)
        await db_session.commit()
        await db_session.refresh(execution)

        # 调用服务方法（没有运行中的引擎）
        success = await execution_service.stop_execution(db_session, execution.id)

        # 验证：仍然成功（状态已更新）
        assert success is True


class TestExecutionServiceGetRunningEngine:
    """测试获取正在运行的引擎方法"""

    def test_get_running_engine_exists(self):
        """测试获取存在的引擎"""
        # 创建 Mock 引擎
        mock_engine = AsyncMock()
        execution_id = 1

        # 设置运行中的引擎
        execution_service._running_executions[execution_id] = mock_engine

        # 调用服务方法
        result = execution_service.get_running_engine(execution_id)

        # 验证：返回引擎
        assert result is not None
        assert result == mock_engine

    def test_get_running_engine_not_exists(self):
        """测试获取不存在的引擎"""
        # 调用服务方法（ID 不在运行列表中）
        result = execution_service.get_running_engine(999)

        # 验证：返回 None
        assert result is None

    def test_get_running_engine_empty_dict(self):
        """测试运行字典为空"""
        # 清空运行字典
        execution_service._running_executions.clear()

        # 调用服务方法
        result = execution_service.get_running_engine(1)

        # 验证：返回 None
        assert result is None
