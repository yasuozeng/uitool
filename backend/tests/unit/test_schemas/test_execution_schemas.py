"""
测试执行相关模式测试
测试执行任务和执行结果的数据验证模式
"""
# 导入 pytest 测试框架
import pytest
# 从 datetime 导入 datetime 类
from datetime import datetime
# 导入执行相关的所有模式
from app.schemas.execution import (
    ExecutionCreate, ExecutionResponse, ExecutionListResponse,
    ExecutionDetailResponse, ExecutionLogMessage, ExecutionQueryParams
)
# 从 pydantic 导入验证错误异常
from pydantic import ValidationError


class TestExecutionCreate:
    """测试 ExecutionCreate 创建执行任务模式"""

    def test_execution_create_batch(self):
        """测试批量执行类型"""
        # 创建执行对象（批量模式）
        execution = ExecutionCreate(
            execution_type="batch",
            browser_type="chrome",
            headless=True,
            window_size="1920x1080",
            case_ids=[1, 2, 3]
        )

        # 验证：所有字段正确
        assert execution.execution_type == "batch"
        assert execution.browser_type == "chrome"
        assert execution.headless is True
        assert execution.window_size == "1920x1080"
        assert execution.case_ids == [1, 2, 3]

    def test_execution_create_single(self):
        """测试单个执行类型"""
        # 创建执行对象（单个模式）
        execution = ExecutionCreate(
            execution_type="single",
            browser_type="firefox",
            headless=False
        )

        # 验证：所有字段正确
        assert execution.execution_type == "single"
        assert execution.browser_type == "firefox"
        assert execution.headless is False

    def test_execution_create_defaults(self):
        """测试默认值"""
        # 创建执行对象（只传必填字段）
        execution = ExecutionCreate(execution_type="batch")

        # 验证：默认值正确
        assert execution.execution_type == "batch"
        assert execution.browser_type == "chrome"  # 默认值
        assert execution.headless is True  # 默认值
        assert execution.window_size is None
        assert execution.case_ids is None

    def test_execution_type_validation(self):
        """测试执行类型验证（只允许 single/batch）"""
        # 测试非法执行类型
        with pytest.raises(ValidationError) as exc_info:
            ExecutionCreate(execution_type="invalid")
        # 验证：错误信息包含 pattern 约束
        assert "execution_type" in str(exc_info.value).lower()

    def test_browser_type_validation(self):
        """测试浏览器类型验证（只允许 chrome/firefox/edge）"""
        # 测试非法浏览器类型
        with pytest.raises(ValidationError) as exc_info:
            ExecutionCreate(
                execution_type="batch",
                browser_type="safari"
            )
        # 验证：错误信息包含 pattern 约束
        assert "browser_type" in str(exc_info.value).lower()

    def test_browser_type_all_valid(self):
        """测试所有合法浏览器类型"""
        # 测试所有合法浏览器类型
        for browser in ["chrome", "firefox", "edge"]:
            execution = ExecutionCreate(
                execution_type="batch",
                browser_type=browser
            )
            assert execution.browser_type == browser

    def test_headless_type(self):
        """测试无头模式类型（布尔值）"""
        # 测试 True
        execution1 = ExecutionCreate(
            execution_type="batch",
            headless=True
        )
        assert execution1.headless is True

        # 测试 False
        execution2 = ExecutionCreate(
            execution_type="batch",
            headless=False
        )
        assert execution2.headless is False

    def test_case_ids_optional(self):
        """测试用例 ID 列表可选"""
        # 创建执行对象（不传 case_ids）
        execution = ExecutionCreate(
            execution_type="batch",
            case_ids=None
        )

        # 验证：case_ids 可以为 None
        assert execution.case_ids is None

    def test_case_ids_empty_list(self):
        """测试空用例 ID 列表"""
        # 创建执行对象（case_ids 为空列表）
        execution = ExecutionCreate(
            execution_type="batch",
            case_ids=[]
        )

        # 验证：case_ids 可以为空列表
        assert execution.case_ids == []

    def test_window_size_optional(self):
        """测试窗口大小可选"""
        # 创建执行对象（不传 window_size）
        execution = ExecutionCreate(execution_type="batch")

        # 验证：window_size 可以为 None
        assert execution.window_size is None


class TestExecutionResponse:
    """测试 ExecutionResponse 执行任务响应模式"""

    def test_execution_response(self):
        """测试执行任务响应"""
        # 创建当前时间
        now = datetime.now()
        # 创建响应对象
        response = ExecutionResponse(
            id=1,
            execution_type="batch",
            browser_type="chrome",
            headless=True,
            window_size="1920x1080",
            start_time=now,
            end_time=now,
            total_count=10,
            success_count=8,
            fail_count=2,
            skip_count=0,
            status="completed",
            pass_rate=80.0,
            duration=5000,
            created_at=now
        )

        # 验证：所有字段正确
        assert response.id == 1
        assert response.execution_type == "batch"
        assert response.total_count == 10
        assert response.success_count == 8
        assert response.fail_count == 2
        assert response.pass_rate == 80.0
        assert response.duration == 5000

    def test_execution_response_running(self):
        """测试运行中的执行响应（无结束时间）"""
        # 创建当前时间
        now = datetime.now()
        # 创建响应对象（运行中）
        response = ExecutionResponse(
            id=1,
            execution_type="single",
            browser_type="chrome",
            headless=True,
            window_size=None,
            start_time=now,
            end_time=None,  # 运行中，无结束时间
            total_count=1,
            success_count=0,
            fail_count=0,
            skip_count=0,
            status="running",
            pass_rate=0.0,
            duration=None,  # 运行中，无执行时长
            created_at=now
        )

        # 验证：运行中状态特征
        assert response.status == "running"
        assert response.end_time is None
        assert response.duration is None


class TestExecutionListResponse:
    """测试 ExecutionListResponse 执行任务列表响应模式"""

    def test_execution_list_response(self):
        """测试执行任务列表响应"""
        # 创建当前时间
        now = datetime.now()
        # 创建列表响应对象
        response = ExecutionListResponse(
            id=1,
            execution_type="batch",
            browser_type="chrome",
            status="completed",
            total_count=10,
            success_count=9,
            fail_count=1,
            pass_rate=90.0,
            start_time=now,
            created_at=now
        )

        # 验证：所有字段正确
        assert response.id == 1
        assert response.status == "completed"
        assert response.pass_rate == 90.0


class TestExecutionDetailResponse:
    """测试 ExecutionDetailResponse 执行详情响应模式"""

    def test_execution_detail_response_success(self):
        """测试成功的执行详情"""
        # 创建当前时间
        now = datetime.now()
        # 创建详情响应对象
        detail = ExecutionDetailResponse(
            id=1,
            execution_id=1,
            case_id=1,
            case_name="登录测试",
            status="success",
            error_message=None,
            error_stack=None,
            screenshot_path=None,
            step_logs=[
                {"step_order": 1, "action": "navigate", "status": "success"},
                {"step_order": 2, "action": "click", "status": "success"}
            ],
            start_time=now,
            end_time=now,
            duration=1500,
            created_at=now
        )

        # 验证：所有字段正确
        assert detail.id == 1
        assert detail.case_name == "登录测试"
        assert detail.status == "success"
        assert detail.error_message is None
        assert len(detail.step_logs) == 2
        assert detail.duration == 1500

    def test_execution_detail_response_failed(self):
        """测试失败的执行详情"""
        # 创建当前时间
        now = datetime.now()
        # 创建详情响应对象（失败）
        detail = ExecutionDetailResponse(
            id=1,
            execution_id=1,
            case_id=1,
            case_name="登录测试",
            status="failed",
            error_message="元素未找到",
            error_stack="ElementNotFoundError: ...",
            screenshot_path="/screenshots/error_001.png",
            step_logs=[],
            start_time=now,
            end_time=now,
            duration=500,
            created_at=now
        )

        # 验证：失败状态特征
        assert detail.status == "failed"
        assert detail.error_message == "元素未找到"
        assert detail.screenshot_path == "/screenshots/error_001.png"

    def test_execution_detail_optional_fields(self):
        """测试可选字段"""
        # 创建当前时间
        now = datetime.now()
        # 创建详情响应对象（最小字段）
        detail = ExecutionDetailResponse(
            id=1,
            execution_id=1,
            case_id=1,
            case_name="测试",
            status="skipped",
            error_message=None,
            error_stack=None,
            screenshot_path=None,
            step_logs=None,
            start_time=now,
            end_time=None,
            duration=None,
            created_at=now
        )

        # 验证：可选字段为 None
        assert detail.status == "skipped"
        assert detail.error_message is None
        assert detail.step_logs is None
        assert detail.duration is None


class TestExecutionLogMessage:
    """测试 ExecutionLogMessage 执行日志消息模式"""

    def test_log_message_step_start(self):
        """测试步骤开始消息"""
        # 创建当前时间
        now = datetime.now()
        # 创建日志消息对象
        log = ExecutionLogMessage(
            type="step_start",
            execution_id=1,
            case_id=1,
            step_order=1,
            message="开始执行步骤 1",
            timestamp=now
        )

        # 验证：所有字段正确
        assert log.type == "step_start"
        assert log.execution_id == 1
        assert log.case_id == 1
        assert log.step_order == 1
        assert log.message == "开始执行步骤 1"

    def test_log_message_step_success(self):
        """测试步骤成功消息"""
        # 创建当前时间
        now = datetime.now()
        # 创建日志消息对象
        log = ExecutionLogMessage(
            type="step_success",
            execution_id=1,
            case_id=1,
            step_order=2,
            message="步骤执行成功",
            timestamp=now,
            data={"element": "#button", "action": "click"}
        )

        # 验证：类型和数据正确
        assert log.type == "step_success"
        assert log.data["element"] == "#button"

    def test_log_message_step_failed(self):
        """测试步骤失败消息"""
        # 创建当前时间
        now = datetime.now()
        # 创建日志消息对象
        log = ExecutionLogMessage(
            type="step_failed",
            execution_id=1,
            case_id=1,
            step_order=3,
            message="步骤执行失败",
            timestamp=now,
            data={"error": "TimeoutError", "timeout": 5000}
        )

        # 验证：类型和错误数据正确
        assert log.type == "step_failed"
        assert log.data["error"] == "TimeoutError"

    def test_log_message_log(self):
        """测试普通日志消息"""
        # 创建当前时间
        now = datetime.now()
        # 创建日志消息对象
        log = ExecutionLogMessage(
            type="log",
            execution_id=1,
            message="浏览器已启动",
            timestamp=now
        )

        # 验证：普通日志不需要 case_id 和 step_order
        assert log.type == "log"
        assert log.case_id is None
        assert log.step_order is None

    def test_log_message_error(self):
        """测试错误消息"""
        # 创建当前时间
        now = datetime.now()
        # 创建日志消息对象
        log = ExecutionLogMessage(
            type="error",
            execution_id=1,
            case_id=1,
            message="执行出错",
            timestamp=now,
            data={"stack": "Traceback..."}
        )

        # 验证：错误类型和数据
        assert log.type == "error"
        assert log.data["stack"] == "Traceback..."

    def test_log_type_validation(self):
        """测试日志类型验证"""
        # 测试非法日志类型
        with pytest.raises(ValidationError) as exc_info:
            ExecutionLogMessage(
                type="invalid_type",
                execution_id=1,
                message="test",
                timestamp=datetime.now()
            )
        # 验证：错误信息包含 pattern 约束
        assert "type" in str(exc_info.value).lower()

    def test_log_type_all_valid(self):
        """测试所有合法日志类型"""
        # 测试所有合法日志类型
        for log_type in ["step_start", "step_success", "step_failed", "log", "error"]:
            log = ExecutionLogMessage(
                type=log_type,
                execution_id=1,
                message="test",
                timestamp=datetime.now()
            )
            assert log.type == log_type

    def test_log_data_optional(self):
        """测试附加数据可选"""
        # 创建当前时间
        now = datetime.now()
        # 创建日志消息对象（不传 data）
        log = ExecutionLogMessage(
            type="log",
            execution_id=1,
            message="测试消息",
            timestamp=now
        )

        # 验证：data 默认为 None
        assert log.data is None


class TestExecutionQueryParams:
    """测试 ExecutionQueryParams 执行查询参数模式"""

    def test_query_params_default(self):
        """测试默认值"""
        # 创建查询参数对象（使用默认值）
        params = ExecutionQueryParams()

        # 验证：所有默认值正确
        assert params.status is None
        assert params.browser_type is None
        assert params.page == 1
        assert params.page_size == 20

    def test_query_params_with_filters(self):
        """测试带筛选条件"""
        # 创建查询参数对象（带筛选条件）
        params = ExecutionQueryParams(
            status="running",
            browser_type="chrome",
            page=2,
            page_size=50
        )

        # 验证：所有筛选条件正确
        assert params.status == "running"
        assert params.browser_type == "chrome"
        assert params.page == 2
        assert params.page_size == 50

    def test_query_params_status_validation(self):
        """测试状态筛选验证"""
        # 测试非法状态
        with pytest.raises(ValidationError):
            ExecutionQueryParams(status="invalid_status")

    def test_query_params_status_all_valid(self):
        """测试所有合法状态"""
        # 测试所有合法状态值
        for status in ["pending", "running", "completed", "failed"]:
            params = ExecutionQueryParams(status=status)
            assert params.status == status

    def test_query_params_browser_validation(self):
        """测试浏览器筛选验证"""
        # 测试非法浏览器类型
        with pytest.raises(ValidationError):
            ExecutionQueryParams(browser_type="safari")

    def test_query_params_page_validation(self):
        """测试页码验证"""
        # 测试非法页码（0）
        with pytest.raises(ValidationError):
            ExecutionQueryParams(page=0)

    def test_query_params_page_size_validation(self):
        """测试每页数量验证"""
        # 测试非法值（101，超过上限）
        with pytest.raises(ValidationError):
            ExecutionQueryParams(page_size=101)

    def test_query_params_page_size_boundary(self):
        """测试每页数量边界值"""
        # 测试边界值（100，合法）
        params = ExecutionQueryParams(page_size=100)
        assert params.page_size == 100

        # 测试边界值（1，合法）
        params = ExecutionQueryParams(page_size=1)
        assert params.page_size == 1
