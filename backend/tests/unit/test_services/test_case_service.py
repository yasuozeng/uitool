"""
测试用例服务测试
测试 CaseService 的所有业务逻辑方法
"""
# 导入 pytest 测试框架和异步标记
import pytest
# 从 sqlalchemy 导入查询相关函数
from sqlalchemy import select

# 导入用例服务
from app.services.case_service import case_service
# 导入数据模式
from app.schemas.case import CaseCreate, CaseUpdate, StepCreate
# 导入模型
from app.models.case import TestCase, TestStep


class TestCaseServiceGetCases:
    """测试获取用例列表方法"""

    @pytest.mark.asyncio
    async def test_get_cases_empty(self, db_session):
        """测试空列表"""
        # 调用服务方法获取空列表
        cases, total = await case_service.get_cases(db_session)

        # 验证：列表为空
        assert cases == []
        # 验证：总数为 0
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_cases_with_data(self, db_session):
        """测试有数据的情况"""
        # 创建测试数据：插入 3 个用例
        for i in range(1, 4):
            case = TestCase(
                name=f"测试用例{i}",
                description=f"描述{i}",
                priority="P1",
                tags=f"tag{i}"
            )
            db_session.add(case)
        await db_session.commit()

        # 调用服务方法获取列表
        cases, total = await case_service.get_cases(db_session)

        # 验证：返回 3 个用例
        assert len(cases) == 3
        # 验证：总数为 3
        assert total == 3
        # 验证：第一个用例名称正确
        assert cases[0].name == "测试用例1"

    @pytest.mark.asyncio
    async def test_get_cases_with_name_filter(self, db_session):
        """测试按名称筛选"""
        # 创建测试数据
        case1 = TestCase(name="登录测试", description="测试登录")
        case2 = TestCase(name="注册测试", description="测试注册")
        case3 = TestCase(name="退出测试", description="测试退出")
        db_session.add_all([case1, case2, case3])
        await db_session.commit()

        # 按名称筛选（包含"测试"）
        cases, total = await case_service.get_cases(db_session, name="测试")

        # 验证：返回 3 个结果
        assert len(cases) == 3
        assert total == 3

        # 按名称筛选（包含"登录"）
        cases, total = await case_service.get_cases(db_session, name="登录")

        # 验证：返回 1 个结果
        assert len(cases) == 1
        assert cases[0].name == "登录测试"

    @pytest.mark.asyncio
    async def test_get_cases_with_priority_filter(self, db_session):
        """测试按优先级筛选"""
        # 创建测试数据（不同优先级）
        case1 = TestCase(name="用例1", priority="P0")
        case2 = TestCase(name="用例2", priority="P1")
        case3 = TestCase(name="用例3", priority="P0")
        db_session.add_all([case1, case2, case3])
        await db_session.commit()

        # 按优先级筛选
        cases, total = await case_service.get_cases(db_session, priority="P0")

        # 验证：返回 2 个 P0 用例
        assert len(cases) == 2
        assert total == 2
        # 验证：所有结果优先级为 P0
        for case in cases:
            assert case.priority == "P0"

    @pytest.mark.asyncio
    async def test_get_cases_with_tags_filter(self, db_session):
        """测试按标签筛选"""
        # 创建测试数据
        case1 = TestCase(name="用例1", tags="smoke,regression")
        case2 = TestCase(name="用例2", tags="api")
        case3 = TestCase(name="用例3", tags="smoke,api")
        db_session.add_all([case1, case2, case3])
        await db_session.commit()

        # 按标签筛选
        cases, total = await case_service.get_cases(db_session, tags="smoke")

        # 验证：返回 2 个包含 smoke 标签的用例
        assert len(cases) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_get_cases_pagination(self, db_session):
        """测试分页"""
        # 创建 25 条测试数据
        for i in range(1, 26):
            case = TestCase(name=f"用例{i}")
            db_session.add(case)
        await db_session.commit()

        # 获取第 1 页（每页 10 条）
        cases, total = await case_service.get_cases(db_session, page=1, page_size=10)

        # 验证：总数 25，第 1 页 10 条
        assert total == 25
        assert len(cases) == 10

        # 获取第 2 页
        cases, total = await case_service.get_cases(db_session, page=2, page_size=10)

        # 验证：第 2 页 10 条
        assert len(cases) == 10

        # 获取第 3 页
        cases, total = await case_service.get_cases(db_session, page=3, page_size=10)

        # 验证：第 3 页 5 条
        assert len(cases) == 5

    @pytest.mark.asyncio
    async def test_get_cases_ordering(self, db_session):
        """测试排序（按创建时间倒序）"""
        # 创建测试数据（不同时间）
        case1 = TestCase(name="用例1")
        db_session.add(case1)
        await db_session.commit()

        case2 = TestCase(name="用例2")
        db_session.add(case2)
        await db_session.commit()

        # 获取列表
        cases, total = await case_service.get_cases(db_session)

        # 验证：用例2 在前面（后创建的在前）
        assert cases[0].name == "用例2"
        assert cases[1].name == "用例1"


class TestCaseServiceGetCaseById:
    """测试根据 ID 获取用例方法"""

    @pytest.mark.asyncio
    async def test_get_case_by_id_exists(self, db_session):
        """测试获取存在的用例"""
        # 创建测试数据
        case = TestCase(name="测试用例", description="测试描述")
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)

        # 调用服务方法
        result = await case_service.get_case_by_id(db_session, case.id)

        # 验证：返回的用例数据正确
        assert result is not None
        assert result.id == case.id
        assert result.name == "测试用例"
        assert result.description == "测试描述"

    @pytest.mark.asyncio
    async def test_get_case_by_id_not_exists(self, db_session):
        """测试获取不存在的用例"""
        # 调用服务方法（ID 不存在）
        result = await case_service.get_case_by_id(db_session, 999)

        # 验证：返回 None
        assert result is None

    @pytest.mark.asyncio
    async def test_get_case_by_id_with_steps(self, db_session):
        """测试获取用例及其步骤"""
        # 创建测试数据（用例 + 步骤）
        case = TestCase(name="带步骤的用例")
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)

        # 添加步骤
        step1 = TestStep(case_id=case.id, step_order=1, action_type="navigate")
        step2 = TestStep(case_id=case.id, step_order=2, action_type="click")
        db_session.add_all([step1, step2])
        await db_session.commit()

        # 调用服务方法
        result = await case_service.get_case_by_id(db_session, case.id)

        # 验证：用例包含步骤
        assert result is not None
        assert len(result.steps) == 2
        assert result.steps[0].action_type == "navigate"
        assert result.steps[1].action_type == "click"


class TestCaseServiceCreateCase:
    """测试创建用例方法"""

    @pytest.mark.asyncio
    async def test_create_case_success(self, db_session):
        """测试成功创建用例"""
        # 创建用例数据
        case_data = CaseCreate(
            name="新用例",
            description="新用例描述",
            priority="P1",
            tags="smoke",
            steps=[
                StepCreate(step_order=1, action_type="navigate"),
                StepCreate(step_order=2, action_type="click")
            ]
        )

        # 调用服务方法
        result = await case_service.create_case(db_session, case_data)

        # 验证：用例创建成功
        assert result is not None
        assert result.id > 0
        assert result.name == "新用例"
        assert result.priority == "P1"

        # 验证：步骤已创建
        assert len(result.steps) == 2
        assert result.steps[0].action_type == "navigate"

    @pytest.mark.asyncio
    async def test_create_case_with_empty_steps(self, db_session):
        """测试创建空步骤用例"""
        # 创建用例数据（空步骤）
        case_data = CaseCreate(
            name="空步骤用例",
            steps=[]
        )

        # 调用服务方法
        result = await case_service.create_case(db_session, case_data)

        # 验证：用例创建成功，无步骤
        assert result is not None
        assert len(result.steps) == 0

    @pytest.mark.asyncio
    async def test_create_case_persisted(self, db_session):
        """测试用例持久化到数据库"""
        # 创建用例数据
        case_data = CaseCreate(
            name="持久化测试",
            steps=[StepCreate(step_order=1, action_type="navigate")]
        )

        # 调用服务方法
        result = await case_service.create_case(db_session, case_data)

        # 直接查询数据库验证
        query = select(TestCase).where(TestCase.id == result.id)
        db_result = await db_session.execute(query)
        db_case = db_result.scalar_one_or_none()

        # 验证：数据库中存在该用例
        assert db_case is not None
        assert db_case.name == "持久化测试"


class TestCaseServiceUpdateCase:
    """测试更新用例方法"""

    @pytest.mark.asyncio
    async def test_update_case_success(self, db_session):
        """测试成功更新用例"""
        # 创建初始用例
        case = TestCase(name="原名称", priority="P1")
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)

        # 更新数据
        update_data = CaseUpdate(
            name="新名称",
            priority="P0",
            description="新描述"
        )

        # 调用服务方法
        result = await case_service.update_case(db_session, case.id, update_data)

        # 验证：更新成功
        assert result is not None
        assert result.name == "新名称"
        assert result.priority == "P0"
        assert result.description == "新描述"

    @pytest.mark.asyncio
    async def test_update_case_partial(self, db_session):
        """测试部分更新"""
        # 创建初始用例
        case = TestCase(name="原名称", description="原描述", priority="P1")
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)

        # 只更新名称
        update_data = CaseUpdate(name="只更新名称")

        # 调用服务方法
        result = await case_service.update_case(db_session, case.id, update_data)

        # 验证：只更新了名称，其他字段保持不变
        assert result.name == "只更新名称"
        assert result.description == "原描述"
        assert result.priority == "P1"

    @pytest.mark.asyncio
    async def test_update_case_not_exists(self, db_session):
        """测试更新不存在的用例"""
        # 更新数据
        update_data = CaseUpdate(name="新名称")

        # 调用服务方法（ID 不存在）
        result = await case_service.update_case(db_session, 999, update_data)

        # 验证：返回 None
        assert result is None

    @pytest.mark.asyncio
    async def test_update_case_no_changes(self, db_session):
        """测试不更新任何字段"""
        # 创建初始用例
        case = TestCase(name="用例名")
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)

        # 空更新数据
        update_data = CaseUpdate()

        # 调用服务方法
        result = await case_service.update_case(db_session, case.id, update_data)

        # 验证：数据保持不变
        assert result.name == "用例名"


class TestCaseServiceDeleteCase:
    """测试删除用例方法"""

    @pytest.mark.asyncio
    async def test_delete_case_success(self, db_session):
        """测试成功删除用例"""
        # 创建测试用例
        case = TestCase(name="待删除用例")
        db_session.add(case)
        await db_session.commit()
        case_id = case.id

        # 调用服务方法
        success = await case_service.delete_case(db_session, case_id)

        # 验证：删除成功
        assert success is True

        # 验证：数据库中不存在
        query = select(TestCase).where(TestCase.id == case_id)
        result = await db_session.execute(query)
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_delete_case_not_exists(self, db_session):
        """测试删除不存在的用例"""
        # 调用服务方法（ID 不存在）
        success = await case_service.delete_case(db_session, 999)

        # 验证：返回 False
        assert success is False

    @pytest.mark.asyncio
    async def test_delete_case_with_steps(self, db_session):
        """测试删除带步骤的用例（级联删除）"""
        # 创建测试用例和步骤
        case = TestCase(name="带步骤的用例")
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)

        step1 = TestStep(case_id=case.id, step_order=1, action_type="navigate")
        step2 = TestStep(case_id=case.id, step_order=2, action_type="click")
        db_session.add_all([step1, step2])
        await db_session.commit()

        case_id = case.id
        step_count_before = len(case.steps)

        # 验证：删除前有 2 个步骤
        assert step_count_before == 2

        # 调用服务方法
        success = await case_service.delete_case(db_session, case_id)

        # 验证：删除成功
        assert success is True

        # 验证：步骤也被级联删除
        query = select(TestStep).where(TestStep.case_id == case_id)
        result = await db_session.execute(query)
        steps = result.scalars().all()
        assert len(steps) == 0


class TestCaseServiceBatchDeleteCases:
    """测试批量删除用例方法"""

    @pytest.mark.asyncio
    async def test_batch_delete_cases_success(self, db_session):
        """测试成功批量删除"""
        # 创建测试用例
        case1 = TestCase(name="用例1")
        case2 = TestCase(name="用例2")
        case3 = TestCase(name="用例3")
        db_session.add_all([case1, case2, case3])
        await db_session.commit()

        case_ids = [case1.id, case2.id, case3.id]

        # 调用服务方法
        count = await case_service.batch_delete_cases(db_session, case_ids)

        # 验证：删除数量为 3
        assert count == 3

        # 验证：数据库中不存在
        query = select(TestCase).where(TestCase.id.in_(case_ids))
        result = await db_session.execute(query)
        assert len(result.scalars().all()) == 0

    @pytest.mark.asyncio
    async def test_batch_delete_cases_partial(self, db_session):
        """测试部分删除（部分 ID 不存在）"""
        # 创建测试用例
        case1 = TestCase(name="用例1")
        case2 = TestCase(name="用例2")
        db_session.add_all([case1, case2])
        await db_session.commit()

        # 包含不存在的 ID
        case_ids = [case1.id, 999, case2.id]

        # 调用服务方法
        count = await case_service.batch_delete_cases(db_session, case_ids)

        # 验证：只删除了存在的 2 个
        assert count == 2

    @pytest.mark.asyncio
    async def test_batch_delete_cases_empty(self, db_session):
        """测试空列表删除"""
        # 调用服务方法（空列表）
        count = await case_service.batch_delete_cases(db_session, [])

        # 验证：删除数量为 0
        assert count == 0

    @pytest.mark.asyncio
    async def test_batch_delete_cases_all_not_exist(self, db_session):
        """测试所有 ID 都不存在"""
        # 调用服务方法（所有 ID 都不存在）
        count = await case_service.batch_delete_cases(db_session, [999, 888, 777])

        # 验证：删除数量为 0
        assert count == 0


class TestCaseServiceSaveSteps:
    """测试保存步骤方法"""

    @pytest.mark.asyncio
    async def test_save_steps_success(self, db_session):
        """测试成功保存步骤"""
        # 创建测试用例
        case = TestCase(name="测试用例")
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)

        # 新步骤数据
        steps_data = [
            StepCreate(step_order=1, action_type="navigate"),
            StepCreate(step_order=2, action_type="click"),
            StepCreate(step_order=3, action_type="input")
        ]

        # 调用服务方法
        result = await case_service.save_steps(db_session, case.id, steps_data)

        # 验证：步骤保存成功
        assert result is not None
        assert len(result.steps) == 3
        assert result.steps[0].action_type == "navigate"
        assert result.steps[1].action_type == "click"
        assert result.steps[2].action_type == "input"

    @pytest.mark.asyncio
    async def test_save_steps_replace_existing(self, db_session):
        """测试替换现有步骤"""
        # 创建测试用例和步骤
        case = TestCase(name="测试用例")
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)

        # 添加初始步骤
        step1 = TestStep(case_id=case.id, step_order=1, action_type="old_action")
        db_session.add(step1)
        await db_session.commit()

        # 新步骤数据（替换旧的）
        steps_data = [
            StepCreate(step_order=1, action_type="new_action"),
            StepCreate(step_order=2, action_type="another_action")
        ]

        # 调用服务方法
        result = await case_service.save_steps(db_session, case.id, steps_data)

        # 验证：旧步骤被替换
        assert len(result.steps) == 2
        assert result.steps[0].action_type == "new_action"

    @pytest.mark.asyncio
    async def test_save_steps_case_not_exists(self, db_session):
        """测试用例不存在"""
        # 步骤数据
        steps_data = [StepCreate(step_order=1, action_type="navigate")]

        # 调用服务方法（用例 ID 不存在）
        result = await case_service.save_steps(db_session, 999, steps_data)

        # 验证：返回 None
        assert result is None

    @pytest.mark.asyncio
    async def test_save_steps_empty_list(self, db_session):
        """测试保存空步骤列表（清空步骤）"""
        # 创建测试用例和步骤
        case = TestCase(name="测试用例")
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)

        # 添加初始步骤
        step1 = TestStep(case_id=case.id, step_order=1, action_type="navigate")
        db_session.add(step1)
        await db_session.commit()

        # 保存空步骤列表
        steps_data = []

        # 调用服务方法
        result = await case_service.save_steps(db_session, case.id, steps_data)

        # 验证：步骤被清空
        assert result is not None
        assert len(result.steps) == 0
