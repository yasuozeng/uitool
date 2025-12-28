"""
测试用例相关模式测试
测试用例和步骤的数据验证模式
"""
# 导入 pytest 测试框架
import pytest
# 从 datetime 导入 datetime 类
from datetime import datetime
# 导入用例相关的所有模式
from app.schemas.case import (
    StepBase, StepCreate, StepUpdate, StepResponse,
    CaseBase, CaseCreate, CaseUpdate, CaseResponse, CaseListResponse,
    BatchStepCreate, BatchDeleteRequest, CaseQueryParams
)
# 从 pydantic 导入验证错误异常
from pydantic import ValidationError


class TestStepBase:
    """测试 StepBase 步骤基础模式"""

    def test_step_base_valid(self):
        """测试有效的步骤数据"""
        # 创建步骤对象
        step = StepBase(
            step_order=1,
            action_type="navigate",
            element_locator="#button",
            locator_type="css",
            action_params={"url": "https://example.com"},
            expected_result="页面加载成功",
            description="打开首页"
        )

        # 验证：所有字段正确设置
        assert step.step_order == 1
        assert step.action_type == "navigate"
        assert step.element_locator == "#button"
        assert step.locator_type == "css"
        assert step.action_params == {"url": "https://example.com"}
        assert step.expected_result == "页面加载成功"
        assert step.description == "打开首页"

    def test_step_base_minimal(self):
        """测试最小字段（只有必填字段）"""
        # 创建步骤对象（只有 step_order 和 action_type）
        step = StepBase(step_order=1, action_type="click")

        # 验证：必填字段正确，可选字段使用默认值
        assert step.step_order == 1
        assert step.action_type == "click"
        assert step.locator_type == "css"  # 默认值
        assert step.element_locator is None
        assert step.action_params is None

    def test_step_order_validation(self):
        """测试步骤顺序验证（最小值为 1）"""
        # 测试非法值（step_order = 0）
        with pytest.raises(ValidationError) as exc_info:
            StepBase(step_order=0, action_type="click")
        # 验证：错误信息包含最小值约束
        assert "step_order" in str(exc_info.value).lower()

    def test_step_order_negative(self):
        """测试步骤顺序为负数"""
        # 测试非法值（step_order = -1）
        with pytest.raises(ValidationError):
            StepBase(step_order=-1, action_type="click")


class TestStepCreate:
    """测试 StepCreate 创建步骤模式"""

    def test_step_create_valid(self):
        """测试有效的创建步骤数据"""
        # 创建步骤对象
        step = StepCreate(
            step_order=1,
            action_type="input",
            element_locator="#username",
            locator_type="id",
            action_params={"text": "testuser"}
        )

        # 验证：所有字段正确
        assert step.step_order == 1
        assert step.action_type == "input"
        assert step.action_params["text"] == "testuser"


class TestStepUpdate:
    """测试 StepUpdate 更新步骤模式"""

    def test_step_update_valid(self):
        """测试有效的更新步骤数据"""
        # 创建步骤对象
        step = StepUpdate(
            step_order=2,
            action_type="click",
            element_locator=".submit-btn"
        )

        # 验证：所有字段正确
        assert step.step_order == 2
        assert step.action_type == "click"


class TestCaseBase:
    """测试 CaseBase 用例基础模式"""

    def test_case_base_valid(self):
        """测试有效的用例数据"""
        # 创建用例对象
        case = CaseBase(
            name="登录测试",
            description="测试用户登录功能",
            priority="P0",
            tags="auth,smoke"
        )

        # 验证：所有字段正确
        assert case.name == "登录测试"
        assert case.description == "测试用户登录功能"
        assert case.priority == "P0"
        assert case.tags == "auth,smoke"

    def test_case_base_defaults(self):
        """测试默认值"""
        # 创建用例对象（只有必填字段）
        case = CaseBase(name="测试用例")

        # 验证：必填字段正确，可选字段使用默认值
        assert case.name == "测试用例"
        assert case.description is None
        assert case.priority == "P1"  # 默认值
        assert case.tags is None

    def test_case_name_min_length(self):
        """测试用例名称最小长度（1）"""
        # 测试空名称（非法）
        with pytest.raises(ValidationError) as exc_info:
            CaseBase(name="")
        # 验证：错误信息包含最小长度约束
        assert "name" in str(exc_info.value).lower()

    def test_case_name_max_length(self):
        """测试用例名称最大长度（200）"""
        # 测试超长名称（201 个字符）
        with pytest.raises(ValidationError):
            CaseBase(name="a" * 201)

    def test_case_name_boundary(self):
        """测试用例名称边界值（200 个字符）"""
        # 测试边界值（200 个字符，合法）
        case = CaseBase(name="a" * 200)
        assert case.name == "a" * 200

    def test_case_priority_validation(self):
        """测试优先级验证（只允许 P0/P1/P2/P3）"""
        # 测试非法优先级
        with pytest.raises(ValidationError):
            CaseBase(name="测试", priority="P4")

    def test_case_priority_all_valid(self):
        """测试所有合法优先级"""
        # 测试所有合法优先级值
        for priority in ["P0", "P1", "P2", "P3"]:
            case = CaseBase(name="测试", priority=priority)
            assert case.priority == priority

    def test_case_tags_max_length(self):
        """测试标签最大长度（500）"""
        # 测试超长标签（501 个字符）
        with pytest.raises(ValidationError):
            CaseBase(name="测试", tags="a" * 501)


class TestCaseCreate:
    """测试 CaseCreate 创建用例模式"""

    def test_case_create_valid(self):
        """测试有效的创建用例数据"""
        # 创建用例对象（包含步骤）
        case = CaseCreate(
            name="登录测试",
            priority="P1",
            steps=[
                StepCreate(step_order=1, action_type="navigate"),
                StepCreate(step_order=2, action_type="input")
            ]
        )

        # 验证：用例和步骤正确
        assert case.name == "登录测试"
        assert len(case.steps) == 2
        assert case.steps[0].action_type == "navigate"

    def test_case_create_empty_steps(self):
        """测试空步骤列表（合法）"""
        # 创建用例对象（步骤列表为空）
        case = CaseCreate(name="测试", steps=[])

        # 验证：步骤列表为空
        assert case.steps == []

    def test_case_create_default_steps(self):
        """测试默认步骤列表（空列表）"""
        # 创建用例对象（不传 steps，使用默认值）
        case = CaseCreate(name="测试")

        # 验证：步骤列表为空列表（默认值）
        assert case.steps == []


class TestCaseUpdate:
    """测试 CaseUpdate 更新用例模式"""

    def test_case_update_partial(self):
        """测试部分更新（只更新部分字段）"""
        # 创建更新对象（只更新名称）
        update = CaseUpdate(name="新名称")

        # 验证：只提供了名称，其他字段为 None
        assert update.name == "新名称"
        assert update.description is None
        assert update.priority is None
        assert update.tags is None

    def test_case_update_all_fields(self):
        """测试更新所有字段"""
        # 创建更新对象（更新所有字段）
        update = CaseUpdate(
            name="更新名称",
            description="更新描述",
            priority="P0",
            tags="updated"
        )

        # 验证：所有字段正确
        assert update.name == "更新名称"
        assert update.priority == "P0"

    def test_case_update_priority_validation(self):
        """测试更新优先级验证"""
        # 测试非法优先级
        with pytest.raises(ValidationError):
            CaseUpdate(priority="P5")


class TestCaseListResponse:
    """测试 CaseListResponse 用例列表响应模式"""

    def test_case_list_response(self):
        """测试用例列表响应"""
        # 创建响应对象
        response = CaseListResponse(
            id=1,
            name="登录测试",
            description="测试登录",
            priority="P1",
            tags="smoke",
            step_count=3,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 验证：所有字段正确
        assert response.id == 1
        assert response.name == "登录测试"
        assert response.step_count == 3


class BatchStepCreate:
    """测试 BatchStepCreate 批量创建步骤模式"""

    def test_batch_step_create_valid(self):
        """测试有效的批量创建步骤数据"""
        # 创建批量步骤对象
        batch = BatchStepCreate(steps=[
            StepCreate(step_order=1, action_type="navigate"),
            StepCreate(step_order=2, action_type="click"),
            StepCreate(step_order=3, action_type="input")
        ])

        # 验证：步骤列表长度为 3
        assert len(batch.steps) == 3

    def test_batch_step_create_min_length(self):
        """测试最小长度（至少 1 个步骤）"""
        # 测试空步骤列表（非法）
        with pytest.raises(ValidationError) as exc_info:
            BatchStepCreate(steps=[])
        # 验证：错误信息包含最小长度约束
        assert "steps" in str(exc_info.value).lower()


class BatchDeleteRequest:
    """测试 BatchDeleteRequest 批量删除请求模式"""

    def test_batch_delete_valid(self):
        """测试有效的批量删除请求"""
        # 创建批量删除请求对象
        request = BatchDeleteRequest(case_ids=[1, 2, 3, 4, 5])

        # 验证：用例 ID 列表正确
        assert request.case_ids == [1, 2, 3, 4, 5]

    def test_batch_delete_single(self):
        """测试单个删除"""
        # 创建批量删除请求对象（只有一个 ID）
        request = BatchDeleteRequest(case_ids=[1])

        # 验证：列表包含一个 ID
        assert len(request.case_ids) == 1

    def test_batch_delete_empty(self):
        """测试空 ID 列表（非法）"""
        # 测试空列表（非法）
        with pytest.raises(ValidationError):
            BatchDeleteRequest(case_ids=[])


class TestCaseQueryParams:
    """测试 CaseQueryParams 用例查询参数模式"""

    def test_query_params_default(self):
        """测试默认值"""
        # 创建查询参数对象（使用默认值）
        params = CaseQueryParams()

        # 验证：所有默认值正确
        assert params.name is None
        assert params.priority is None
        assert params.tags is None
        assert params.page == 1
        assert params.page_size == 20

    def test_query_params_with_filters(self):
        """测试带筛选条件"""
        # 创建查询参数对象（带筛选条件）
        params = CaseQueryParams(
            name="登录",
            priority="P0",
            tags="smoke",
            page=2,
            page_size=50
        )

        # 验证：所有筛选条件正确
        assert params.name == "登录"
        assert params.priority == "P0"
        assert params.tags == "smoke"
        assert params.page == 2
        assert params.page_size == 50

    def test_query_params_page_validation(self):
        """测试页码验证（最小值为 1）"""
        # 测试非法页码（0）
        with pytest.raises(ValidationError):
            CaseQueryParams(page=0)

    def test_query_params_page_size_validation(self):
        """测试每页数量验证（范围 1-100）"""
        # 测试非法值（101，超过上限）
        with pytest.raises(ValidationError):
            CaseQueryParams(page_size=101)

    def test_query_params_page_size_min(self):
        """测试每页数量最小值"""
        # 测试非法值（0）
        with pytest.raises(ValidationError):
            CaseQueryParams(page_size=0)

    def test_query_params_priority_validation(self):
        """测试优先级筛选验证"""
        # 测试非法优先级
        with pytest.raises(ValidationError):
            CaseQueryParams(priority="P5")
