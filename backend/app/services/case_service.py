"""
测试用例业务逻辑服务
提供测试用例和测试步骤的增删改查操作
"""
# 从 typing 模块导入类型注解工具
from typing import List, Optional
# 从 sqlalchemy.ext.asyncio 导入异步会话
from sqlalchemy.ext.asyncio import AsyncSession
# 从 sqlalchemy 导入查询相关函数
from sqlalchemy import select, func, delete
# 从 sqlalchemy.orm 导入预加载选项
from sqlalchemy.orm import selectinload
# 从本地模型模块导入用例和步骤模型
from app.models.case import TestCase, TestStep
# 从本地 schemas 模块导入用例相关的数据验证模式
from app.schemas.case import CaseCreate, CaseUpdate, StepCreate


# 定义测试用例服务类
class CaseService:
    """
    测试用例服务

    封装测试用例的所有业务逻辑操作
    """

    # 定义获取用例列表的异步方法
    async def get_cases(
        self,
        db: AsyncSession,  # 数据库会话
        name: Optional[str] = None,  # 按名称筛选（模糊搜索）
        priority: Optional[str] = None,  # 按优先级筛选
        tags: Optional[str] = None,  # 按标签筛选（模糊搜索）
        page: int = 1,  # 页码，默认第 1 页
        page_size: int = 20  # 每页数量，默认 20 条
    ) -> tuple[List[TestCase], int]:
        """
        获取用例列表（分页）

        支持按名称、优先级、标签筛选，支持分页

        Returns:
            (用例列表, 总数) 元组
        """
        # 构建基础查询：查询 TestCase 表，预加载 steps 关系
        query = select(TestCase).options(selectinload(TestCase.steps))

        # 添加筛选条件
        if name:
            # 如果提供了名称参数，添加模糊搜索条件
            query = query.where(TestCase.name.contains(name))
        if priority:
            # 如果提供了优先级参数，添加精确匹配条件
            query = query.where(TestCase.priority == priority)
        if tags:
            # 如果提供了标签参数，添加模糊搜索条件
            query = query.where(TestCase.tags.contains(tags))

        # 构建统计总数的查询（使用子查询）
        count_query = select(func.count()).select_from(query.subquery())
        # 执行统计查询
        total_result = await db.execute(count_query)
        # 获取总数，如果没有结果则返回 0
        total = total_result.scalar() or 0

        # 添加排序：按创建时间倒序排列（最新的在前）
        query = query.order_by(TestCase.created_at.desc())
        # 添加分页：计算偏移量并限制返回数量
        query = query.offset((page - 1) * page_size).limit(page_size)

        # 执行分页查询
        result = await db.execute(query)
        # 获取所有结果（scalars 返回单个列，all 获取全部）
        cases = result.scalars().all()

        # 返回用例列表和总数
        return list(cases), total

    # 定义根据 ID 获取用例详情的异步方法
    async def get_case_by_id(self, db: AsyncSession, case_id: int) -> Optional[TestCase]:
        """
        根据 ID 获取用例详情

        包括用例的所有测试步骤

        Args:
            db: 数据库会话
            case_id: 用例 ID

        Returns:
            用例对象（包含步骤）或 None
        """
        # 构建查询：查询指定 ID 的用例
        # selectinload 用于预加载关联的 steps 数据，避免 N+1 查询问题
        query = select(TestCase).options(selectinload(TestCase.steps)).where(TestCase.id == case_id)
        # 执行查询
        result = await db.execute(query)
        # 返回单个结果或 None
        return result.scalar_one_or_none()

    # 定义创建测试用例的异步方法
    async def create_case(self, db: AsyncSession, case_data: CaseCreate) -> TestCase:
        """
        创建测试用例

        创建用例及其关联的所有测试步骤

        Args:
            db: 数据库会话
            case_data: 用例创建数据

        Returns:
            创建的用例对象（包含步骤）
        """
        # 创建用例主记录
        db_case = TestCase(
            name=case_data.name,  # 用例名称
            description=case_data.description,  # 用例描述
            priority=case_data.priority,  # 优先级
            tags=case_data.tags  # 标签
        )

        # 将用例添加到会话（尚未提交到数据库）
        db.add(db_case)
        # 刷新会话以获取数据库生成的 ID
        await db.flush()  # 获取 ID

        # 创建关联的测试步骤
        for step_data in case_data.steps:
            # 创建步骤对象
            db_step = TestStep(
                case_id=db_case.id,  # 关联到刚创建的用例
                step_order=step_data.step_order,  # 步骤顺序
                action_type=step_data.action_type,  # 操作类型
                element_locator=step_data.element_locator,  # 元素定位符
                locator_type=step_data.locator_type,  # 定位类型
                # 操作参数 - 如果是 dict 需要转换为 JSON 字符串
                expected_result=step_data.expected_result,  # 期望结果
                description=step_data.description  # 步骤描述
            )
            # 使用 set_params 方法将 dict 转换为 JSON 字符串
            if step_data.action_params:
                if isinstance(step_data.action_params, dict):
                    # 如果是 dict，使用 set_params 方法转换为 JSON 字符串
                    db_step.set_params(step_data.action_params)
                else:
                    # 如果已经是字符串，直接赋值
                    db_step.action_params = step_data.action_params
            # 将步骤添加到会话
            db.add(db_step)

        # 提交事务到数据库
        await db.commit()
        # 刷新用例对象以获取数据库中的最新状态
        await db.refresh(db_case)

        # 重新加载包含步骤的完整用例数据
        return await self.get_case_by_id(db, db_case.id)

    # 定义更新测试用例的异步方法
    async def update_case(
        self,
        db: AsyncSession,  # 数据库会话
        case_id: int,  # 用例 ID
        case_data: CaseUpdate  # 更新数据
    ) -> Optional[TestCase]:
        """
        更新测试用例

        更新用例的基本信息（不包含步骤）

        Args:
            db: 数据库会话
            case_id: 用例 ID
            case_data: 更新数据

        Returns:
            更新后的用例对象或 None
        """
        # 获取要更新的用例
        db_case = await self.get_case_by_id(db, case_id)
        # 如果用例不存在，返回 None
        if not db_case:
            return None

        # 更新字段（只更新提供的字段）
        if case_data.name is not None:
            # 如果提供了新名称，更新名称
            db_case.name = case_data.name
        if case_data.description is not None:
            # 如果提供了新描述，更新描述
            db_case.description = case_data.description
        if case_data.priority is not None:
            # 如果提供了新优先级，更新优先级
            db_case.priority = case_data.priority
        if case_data.tags is not None:
            # 如果提供了新标签，更新标签
            db_case.tags = case_data.tags

        # 提交更改到数据库
        await db.commit()
        # 刷新用例对象以获取最新状态
        await db.refresh(db_case)

        # 重新加载完整的用例数据
        return await self.get_case_by_id(db, db_case.id)

    # 定义删除测试用例的异步方法
    async def delete_case(self, db: AsyncSession, case_id: int) -> bool:
        """
        删除测试用例

        删除用例及其所有关联步骤（级联删除）

        Args:
            db: 数据库会话
            case_id: 用例 ID

        Returns:
            是否删除成功
        """
        # 获取要删除的用例
        db_case = await self.get_case_by_id(db, case_id)
        # 如果用例不存在，返回 False
        if not db_case:
            return False

        # 删除用例（步骤会通过级联自动删除）
        await db.delete(db_case)
        # 提交更改到数据库
        await db.commit()

        # 返回删除成功
        return True

    # 定义批量删除测试用例的异步方法
    async def batch_delete_cases(self, db: AsyncSession, case_ids: List[int]) -> int:
        """
        批量删除测试用例

        Args:
            db: 数据库会话
            case_ids: 用例 ID 列表

        Returns:
            删除的数量
        """
        # 构建批量删除语句
        # 步骤会通过数据库级联自动删除
        stmt = delete(TestCase).where(TestCase.id.in_(case_ids))
        # 执行删除操作
        result = await db.execute(stmt)
        # 提交更改到数据库
        await db.commit()

        # 返回删除的行数
        return result.rowcount

    # 定义批量保存测试步骤的异步方法
    async def save_steps(
        self,
        db: AsyncSession,  # 数据库会话
        case_id: int,  # 用例 ID
        steps_data: List[StepCreate]  # 步骤数据列表
    ) -> Optional[TestCase]:
        """
        批量保存测试步骤

        删除用例的所有现有步骤，然后创建新步骤

        Args:
            db: 数据库会话
            case_id: 用例 ID
            steps_data: 步骤数据列表

        Returns:
            更新后的用例对象或 None
        """
        # 获取要更新的用例
        db_case = await self.get_case_by_id(db, case_id)
        # 如果用例不存在，返回 None
        if not db_case:
            return None

        # 删除现有步骤
        for existing_step in db_case.steps:
            # 逐个删除每个步骤
            await db.delete(existing_step)

        # 创建新步骤
        for step_data in steps_data:
            # 创建步骤对象
            db_step = TestStep(
                case_id=db_case.id,  # 关联到用例
                step_order=step_data.step_order,  # 步骤顺序
                action_type=step_data.action_type,  # 操作类型
                element_locator=step_data.element_locator,  # 元素定位符
                locator_type=step_data.locator_type,  # 定位类型
                # action_params 需要 JSON 字符串，使用 set_params 方法转换
                expected_result=step_data.expected_result,  # 期望结果
                description=step_data.description  # 步骤描述
            )
            # 使用 set_params 方法将 dict 转换为 JSON 字符串
            if step_data.action_params:
                db_step.set_params(step_data.action_params)
            # 将步骤添加到会话
            db.add(db_step)

        # 提交更改到数据库
        await db.commit()
        # 刷新用例对象以获取最新状态
        await db.refresh(db_case)

        # 重新加载完整的用例数据
        return await self.get_case_by_id(db, db_case.id)


# 创建全局服务实例，供其他模块导入使用
case_service = CaseService()
