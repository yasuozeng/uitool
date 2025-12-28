"""
测试执行记录模型单元测试
"""
# 导入 pytest 测试框架
import pytest
# 导入 datetime 和 timedelta，用于时间相关的测试和计算
from datetime import datetime, timedelta
# 从 app.models.execution 导入需要测试的模型类
from app.models.execution import Execution, ExecutionDetail


class TestExecution:
    """Execution 模型测试"""

    def test_create_execution_minimal(self):
        """测试创建最小执行记录"""
        # 创建只包含必要字段的执行记录对象
        execution = Execution(
            execution_type="single",  # 执行类型：单个用例
            browser_type="chrome"  # 浏览器类型：Chrome
        )

        # 验证：未保存前 ID 为 None
        assert execution.id is None
        # 验证：执行类型正确
        assert execution.execution_type == "single"
        # 验证：浏览器类型正确
        assert execution.browser_type == "chrome"
        # 注意：这些默认值是数据库层面的，Python 创建时为 None
        # 验证：窗口大小为 None 或指定值
        assert execution.window_size is None
        # 验证：总用例数为 None 或 0
        assert execution.total_count is None or execution.total_count == 0
        # 验证：成功数为 None 或 0
        assert execution.success_count is None or execution.success_count == 0
        # 验证：失败数为 None 或 0
        assert execution.fail_count is None or execution.fail_count == 0
        # 验证：跳过数为 None 或 0
        assert execution.skip_count is None or execution.skip_count == 0
        # 验证：状态为 None 或 "pending"
        assert execution.status is None or execution.status == "pending"

    def test_create_execution_full(self):
        """测试创建完整执行记录"""
        # 获取当前时间
        now = datetime.now()
        # 创建包含所有字段的执行记录对象
        execution = Execution(
            execution_type="batch",  # 执行类型：批量
            browser_type="firefox",  # 浏览器类型：Firefox
            headless=True,  # 无头模式：开启
            window_size="1920x1080",  # 窗口大小
            total_count=10,  # 总用例数
            success_count=8,  # 成功数
            fail_count=1,  # 失败数
            skip_count=1,  # 跳过数
            status="completed"  # 状态：已完成
        )

        # 验证：执行类型为批量
        assert execution.execution_type == "batch"
        # 验证：浏览器为 Firefox
        assert execution.browser_type == "firefox"
        # 验证：无头模式开启
        assert execution.headless is True
        # 验证：窗口大小正确
        assert execution.window_size == "1920x1080"
        # 验证：总用例数为 10
        assert execution.total_count == 10
        # 验证：成功数为 8
        assert execution.success_count == 8
        # 验证：失败数为 1
        assert execution.fail_count == 1
        # 验证：跳过数为 1
        assert execution.skip_count == 1
        # 验证：状态为已完成
        assert execution.status == "completed"

    def test_pass_rate_property_zero_total(self):
        """测试通过率计算 - 总数为0"""
        # 创建总数为 0 的执行记录
        execution = Execution(
            execution_type="single",  # 执行类型
            browser_type="chrome",  # 浏览器类型
            total_count=0,  # 总用例数为 0
            success_count=0  # 成功数为 0
        )

        # 验证：通过率为 0.0
        assert execution.pass_rate == 0.0

    def test_pass_rate_property_all_success(self):
        """测试通过率计算 - 全部成功"""
        # 创建全部成功的执行记录
        execution = Execution(
            execution_type="batch",  # 执行类型
            browser_type="chrome",  # 浏览器类型
            total_count=10,  # 总用例数
            success_count=10,  # 全部成功
            fail_count=0  # 无失败
        )

        # 验证：通过率为 100.0%
        assert execution.pass_rate == 100.0

    def test_pass_rate_property_partial_success(self):
        """测试通过率计算 - 部分成功"""
        # 创建部分成功的执行记录
        execution = Execution(
            execution_type="batch",  # 执行类型
            browser_type="chrome",  # 浏览器类型
            total_count=10,  # 总用例数
            success_count=7,  # 成功 7 个
            fail_count=3  # 失败 3 个
        )

        # 验证：通过率为 70.0%
        assert execution.pass_rate == 70.0

    def test_pass_rate_property_fractional(self):
        """测试通过率计算 - 小数"""
        # 创建会产生小数通过率的执行记录
        execution = Execution(
            execution_type="batch",  # 执行类型
            browser_type="chrome",  # 浏览器类型
            total_count=3,  # 总用例数
            success_count=2,  # 成功 2 个
            fail_count=1  # 失败 1 个
        )

        # 验证：通过率约为 66.67%（四舍五入）
        assert execution.pass_rate == 66.67

    def test_duration_property_no_end_time(self):
        """测试执行时长计算 - 无结束时间"""
        # 创建没有结束时间的执行记录
        execution = Execution(
            execution_type="single",  # 执行类型
            browser_type="chrome"  # 浏览器类型
        )

        # 验证：没有结束时间时，duration 为 None
        assert execution.duration is None

    def test_duration_property_with_end_time(self):
        """测试执行时长计算 - 有结束时间"""
        # 获取开始时间
        start = datetime.now()
        # 结束时间为开始后 5 秒
        end = start + timedelta(seconds=5)

        # 创建有开始和结束时间的执行记录
        execution = Execution(
            execution_type="single",  # 执行类型
            browser_type="chrome",  # 浏览器类型
            start_time=start,  # 开始时间
            end_time=end  # 结束时间
        )

        # 5秒 = 5000毫秒
        assert execution.duration == 5000

    def test_duration_property_precise(self):
        """测试执行时长计算 - 精确时长"""
        # 获取开始时间
        start = datetime.now()
        # 结束时间为开始后 1234 毫秒
        end = start + timedelta(milliseconds=1234)

        # 创建执行记录
        execution = Execution(
            execution_type="single",  # 执行类型
            browser_type="chrome",  # 浏览器类型
            start_time=start,  # 开始时间
            end_time=end  # 结束时间
        )

        # 验证：执行时长为 1234 毫秒
        assert execution.duration == 1234

    def test_to_dict(self):
        """测试 to_dict 方法"""
        # 获取开始时间
        start = datetime.now()
        # 结束时间为开始后 10 秒
        end = start + timedelta(seconds=10)

        # 创建完整的执行记录
        execution = Execution(
            id=1,  # 执行 ID
            execution_type="single",  # 执行类型
            browser_type="chrome",  # 浏览器类型
            headless=False,  # 有头模式
            window_size="1920x1080",  # 窗口大小
            total_count=5,  # 总用例数
            success_count=4,  # 成功数
            fail_count=1,  # 失败数
            skip_count=0,  # 跳过数
            status="completed",  # 状态
            start_time=start,  # 开始时间
            end_time=end  # 结束时间
        )

        # 调用 to_dict 方法转换
        result = execution.to_dict()

        # 验证：字典包含所有字段
        assert result["id"] == 1
        assert result["execution_type"] == "single"
        assert result["browser_type"] == "chrome"
        assert result["headless"] is False
        assert result["window_size"] == "1920x1080"
        assert result["total_count"] == 5
        assert result["success_count"] == 4
        assert result["fail_count"] == 1
        assert result["skip_count"] == 0
        assert result["status"] == "completed"
        # 验证：通过率计算正确 (4/5 * 100 = 80.0)
        assert result["pass_rate"] == 80.0
        # 验证：执行时长正确 (10秒 = 10000毫秒)
        assert result["duration"] == 10000
        # 验证：包含时间字段
        assert "start_time" in result
        assert "end_time" in result

    @pytest.mark.parametrize("status", ["pending", "running", "completed", "failed"])  # 参数化测试
    def test_valid_statuses(self, status):
        """测试有效状态值"""
        # 使用参数化的状态创建执行记录
        execution = Execution(
            execution_type="single",  # 执行类型
            browser_type=browser_type,  # 参数化的浏览器类型
            status=status  # 参数化的状态
        )
        # 验证：状态正确赋值
        assert execution.status == status

    @pytest.mark.parametrize("browser_type", ["chrome", "firefox", "edge"])  # 参数化测试
    def test_valid_browser_types(self, browser_type):
        """测试有效浏览器类型"""
        # 使用参数化的浏览器类型创建执行记录
        execution = Execution(
            execution_type="single",  # 执行类型
            browser_type=browser_type  # 参数化的浏览器类型
        )
        # 验证：浏览器类型正确赋值
        assert execution.browser_type == browser_type


class TestExecutionDetail:
    """ExecutionDetail 模型测试"""

    def test_create_execution_detail_minimal(self):
        """测试创建最小执行详情"""
        # 创建只包含必要字段的执行详情对象
        detail = ExecutionDetail(
            execution_id=1,  # 所属执行 ID
            case_id=5,  # 用例 ID
            case_name="测试用例1"  # 用例名称
        )

        # 验证：未保存前 ID 为 None
        assert detail.id is None
        # 验证：执行 ID 正确
        assert detail.execution_id == 1
        # 验证：用例 ID 正确
        assert detail.case_id == 5
        # 验证：用例名称正确
        assert detail.case_name == "测试用例1"
        # 注意：status 的默认值是数据库层面的，Python 创建时为 None
        # 验证：错误信息默认为 None
        assert detail.error_message is None
        # 验证：错误堆栈默认为 None
        assert detail.error_stack is None
        # 验证：截图路径默认为 None
        assert detail.screenshot_path is None
        # 验证：步骤日志默认为 None
        assert detail.step_logs is None
        # 验证：结束时间默认为 None
        assert detail.end_time is None
        # 验证：执行时长默认为 None
        assert detail.duration is None

    def test_create_execution_detail_full(self):
        """测试创建完整执行详情"""
        # 获取当前时间
        now = datetime.now()
        # 创建包含所有字段的执行详情对象
        detail = ExecutionDetail(
            execution_id=1,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="测试用例1",  # 用例名称
            status="failed",  # 状态：失败
            error_message="元素未找到",  # 错误信息
            error_stack="Traceback...",  # 错误堆栈
            screenshot_path="/screenshots/error1.png",  # 截图路径
            duration=5000  # 执行时长（毫秒）
        )

        # 验证所有字段正确赋值
        assert detail.execution_id == 1
        assert detail.case_id == 5
        assert detail.case_name == "测试用例1"
        assert detail.status == "failed"
        assert detail.error_message == "元素未找到"
        assert detail.error_stack == "Traceback..."
        assert detail.screenshot_path == "/screenshots/error1.png"
        assert detail.duration == 5000

    def test_logs_list_property_valid_json(self):
        """测试 logs_list 属性 - 有效 JSON"""
        # 创建执行详情对象
        detail = ExecutionDetail(
            execution_id=1,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="测试用例1"  # 用例名称
        )

        # 设置测试日志列表
        test_logs = [
            {"step": 1, "action": "navigate", "status": "success"},  # 步骤 1 成功
            {"step": 2, "action": "click", "status": "failed", "error": "Element not found"}  # 步骤 2 失败
        ]
        # 将日志列表转换为 JSON 存储
        detail.set_logs(test_logs)

        # 获取解析后的日志列表
        result = detail.logs_list
        # 验证：日志被正确解析
        assert len(result) == 2
        # 验证：第一条日志正确
        assert result[0]["action"] == "navigate"
        assert result[0]["status"] == "success"
        # 验证：第二条日志正确
        assert result[1]["status"] == "failed"

    def test_logs_list_property_invalid_json(self):
        """测试 logs_list 属性 - 无效 JSON"""
        # 创建执行详情对象
        detail = ExecutionDetail(
            execution_id=1,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="测试用例1",  # 用例名称
            step_logs="invalid json"  # 无效的 JSON 字符串
        )

        # 获取解析后的日志列表
        result = detail.logs_list
        # 验证：无效 JSON 返回空列表
        assert result == []

    def test_logs_list_property_none(self):
        """测试 logs_list 属性 - None"""
        # 创建执行详情对象
        detail = ExecutionDetail(
            execution_id=1,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="测试用例1"  # 用例名称
        )

        # 获取解析后的日志列表（未设置）
        result = detail.logs_list
        # 验证：None 返回空列表
        assert result == []

    def test_set_logs(self):
        """测试 set_logs 方法"""
        # 创建执行详情对象
        detail = ExecutionDetail(
            execution_id=1,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="测试用例1"  # 用例名称
        )

        # 准备测试日志
        logs = [
            {"step": 1, "action": "navigate", "message": "成功"},  # 步骤 1
            {"step": 2, "action": "click", "message": "成功"}  # 步骤 2
        ]
        # 设置日志（转换为 JSON 存储）
        detail.set_logs(logs)

        # 验证：日志被正确序列化为 JSON
        import json
        assert json.loads(detail.step_logs) == logs

    def test_set_logs_none(self):
        """测试 set_logs 方法 - None"""
        # 创建带日志的执行详情
        detail = ExecutionDetail(
            execution_id=1,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="测试用例1",  # 用例名称
            step_logs='{"old": "logs"}'  # 初始日志
        )

        # 设置日志为 None（清空日志）
        detail.set_logs(None)
        # 验证：日志被设置为 None
        assert detail.step_logs is None

    def test_set_logs_empty(self):
        """测试 set_logs 方法 - 空列表"""
        # 创建执行详情对象
        detail = ExecutionDetail(
            execution_id=1,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="测试用例1"  # 用例名称
        )

        # 设置空日志列表
        detail.set_logs([])
        # 验证：空列表被转换为 None
        assert detail.step_logs is None

    def test_to_dict(self):
        """测试 to_dict 方法"""
        # 创建完整的执行详情对象
        detail = ExecutionDetail(
            id=1,  # 详情 ID
            execution_id=10,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="登录测试",  # 用例名称
            status="success",  # 状态：成功
            error_message=None,  # 无错误信息
            error_stack=None,  # 无错误堆栈
            screenshot_path=None,  # 无截图
            duration=3000  # 执行时长 3 秒
        )

        # 调用 to_dict 方法转换
        result = detail.to_dict()

        # 验证：字典包含所有字段
        assert result["id"] == 1
        assert result["execution_id"] == 10
        assert result["case_id"] == 5
        assert result["case_name"] == "登录测试"
        assert result["status"] == "success"
        assert result["error_message"] is None
        assert result["error_stack"] is None
        assert result["screenshot_path"] is None
        # 验证：日志列表默认为空列表
        assert result["step_logs"] == []
        # 验证：执行时长正确
        assert result["duration"] == 3000
        # 验证：包含时间字段
        assert "start_time" in result
        assert "end_time" in result

    def test_to_dict_with_logs(self):
        """测试 to_dict 方法 - 带日志"""
        # 创建执行详情对象
        detail = ExecutionDetail(
            id=1,  # 详情 ID
            execution_id=10,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="测试"  # 用例名称
        )

        # 设置测试日志
        logs = [{"step": 1, "action": "navigate"}]
        detail.set_logs(logs)

        # 调用 to_dict 方法转换
        result = detail.to_dict()
        # 验证：字典包含解析后的日志列表
        assert result["step_logs"] == logs

    @pytest.mark.parametrize("status", ["success", "failed", "skipped"])  # 参数化测试
    def test_valid_statuses(self, status):
        """测试有效状态值"""
        # 使用参数化的状态创建执行详情
        detail = ExecutionDetail(
            execution_id=1,  # 执行 ID
            case_id=5,  # 用例 ID
            case_name="测试",  # 用例名称
            status=status  # 参数化的状态
        )
        # 验证：状态正确赋值
        assert detail.status == status
