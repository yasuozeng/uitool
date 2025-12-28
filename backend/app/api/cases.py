"""
测试用例 API 路由
定义测试用例管理相关的 HTTP 接口端点
"""
# 从 typing 模块导入类型注解工具
from typing import List
# 从 fastapi 导入路由器、依赖注入、异常等核心组件
from fastapi import APIRouter, Depends, HTTPException, Query
# 从 sqlalchemy.ext.asyncio 导入异步会话
from sqlalchemy.ext.asyncio import AsyncSession

# 从本地数据库模块导入数据库会话依赖
from app.models.database import get_db
# 从本地 schemas 模块导入用例相关的数据验证和响应格式
from app.schemas.case import (
    CaseCreate,  # 创建用例的数据模式
    CaseUpdate,  # 更新用例的数据模式
    CaseResponse,  # 用例详情响应模式
    CaseListResponse,  # 用例列表响应模式
    StepCreate,  # 创建步骤的数据模式
    StepResponse,  # 步骤响应模式
    BatchStepCreate,  # 批量创建步骤的数据模式
    BatchDeleteRequest  # 批量删除请求的数据模式
)
# 从本地 schemas 模块导入通用响应格式
from app.schemas.common import ApiResponse, PaginatedResponse
# 从本地服务模块导入用例服务
from app.services.case_service import case_service

# 创建 API 路由器，设置 URL 前缀和标签
router = APIRouter(prefix="/cases", tags=["用例管理"])


# 定义获取测试用例列表的 GET 请求处理器
@router.get("", response_model=PaginatedResponse[CaseListResponse])
async def get_cases(
    name: str = Query(None, description="按名称搜索"),  # 名称搜索参数
    priority: str = Query(None, pattern="^(P0|P1|P2|P3)$", description="按优先级筛选"),  # 优先级筛选参数
    tags: str = Query(None, description="按标签筛选"),  # 标签筛选参数
    page: int = Query(1, ge=1, description="页码"),  # 页码参数，最小值 1
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),  # 每页数量参数，范围 1-100
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    获取测试用例列表（分页）

    - **name**: 按名称模糊搜索
    - **priority**: 按优先级筛选 (P0/P1/P2/P3)
    - **tags**: 按标签搜索
    - **page**: 页码，从 1 开始
    - **page_size**: 每页数量，最大 100
    """
    try:
        # 调用服务层获取用例列表和总数
        cases, total = await case_service.get_cases(
            db, name=name, priority=priority, tags=tags,
            page=page, page_size=page_size
        )

        # 计算总页数（向上取整）
        pages = (total + page_size - 1) // page_size

        # 转换为响应格式
        case_list = []
        for case in cases:
            # 使用 model_validate 从 ORM 对象创建响应对象
            case_response = CaseListResponse.model_validate(case)
            # 设置步骤数量
            case_response.step_count = len(case.steps)
            case_list.append(case_response)

        # 返回分页响应 - 直接构造字典
        return {
            "code": 200,
            "message": "success",
            "data": case_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages
        }
    except Exception as e:
        # 捕获并打印错误信息
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in get_cases: {e}")
        print(f"TRACEBACK:\n{error_details}")
        raise


# 定义获取测试用例详情的 GET 请求处理器
@router.get("/{case_id}", response_model=ApiResponse[CaseResponse])
async def get_case(
    case_id: int,  # 用例 ID 路径参数
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    获取测试用例详情

    - **case_id**: 用例 ID
    """
    # 调用服务层获取用例详情
    case = await case_service.get_case_by_id(db, case_id)
    # 如果用例不存在，抛出 404 异常
    if not case:
        raise HTTPException(status_code=404, detail=f"用例 {case_id} 不存在")

    # 转换步骤数据
    steps = []
    for step in case.steps:
        # 将步骤模型转换为响应对象
        steps.append(StepResponse(
            id=step.id,  # 步骤 ID
            case_id=step.case_id,  # 所属用例 ID
            step_order=step.step_order,  # 步骤顺序
            action_type=step.action_type,  # 操作类型
            element_locator=step.element_locator,  # 元素定位符
            locator_type=step.locator_type,  # 定位类型
            action_params=step.params_dict,  # 操作参数（解析后的字典）
            expected_result=step.expected_result,  # 期望结果
            description=step.description,  # 步骤描述
            created_at=step.created_at,  # 创建时间
            updated_at=step.updated_at  # 更新时间
        ))

    # 构建响应数据
    response_data = CaseResponse(
        id=case.id,  # 用例 ID
        name=case.name,  # 用例名称
        description=case.description,  # 用例描述
        priority=case.priority,  # 优先级
        tags=case.tags,  # 标签
        steps=steps,  # 步骤列表
        created_at=case.created_at,  # 创建时间
        updated_at=case.updated_at  # 更新时间
    )

    # 返回统一响应格式
    return ApiResponse(data=response_data)


# 定义创建测试用例的 POST 请求处理器
@router.post("", response_model=ApiResponse[CaseResponse], status_code=201)
async def create_case(
    case_data: CaseCreate,  # 请求数据体验证
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    创建测试用例

    - **name**: 用例名称（必填）
    - **description**: 用例描述
    - **priority**: 优先级 (P0/P1/P2/P3)
    - **tags**: 标签
    - **steps**: 测试步骤列表
    """
    # 调用服务层创建用例
    case = await case_service.create_case(db, case_data)

    # 转换步骤数据
    steps = []
    for step in case.steps:
        # 将步骤模型转换为响应对象
        steps.append(StepResponse(
            id=step.id,  # 步骤 ID
            case_id=step.case_id,  # 所属用例 ID
            step_order=step.step_order,  # 步骤顺序
            action_type=step.action_type,  # 操作类型
            element_locator=step.element_locator,  # 元素定位符
            locator_type=step.locator_type,  # 定位类型
            action_params=step.params_dict,  # 操作参数
            expected_result=step.expected_result,  # 期望结果
            description=step.description,  # 步骤描述
            created_at=step.created_at,  # 创建时间
            updated_at=step.updated_at  # 更新时间
        ))

    # 构建响应数据
    response_data = CaseResponse(
        id=case.id,  # 用例 ID
        name=case.name,  # 用例名称
        description=case.description,  # 用例描述
        priority=case.priority,  # 优先级
        tags=case.tags,  # 标签
        steps=steps,  # 步骤列表
        created_at=case.created_at,  # 创建时间
        updated_at=case.updated_at  # 更新时间
    )

    # 返回成功响应（状态码 201）
    return ApiResponse(data=response_data, message="用例创建成功")


# 定义更新测试用例的 PUT 请求处理器
@router.put("/{case_id}", response_model=ApiResponse[CaseResponse])
async def update_case(
    case_id: int,  # 用例 ID 路径参数
    case_data: CaseUpdate,  # 请求数据体验证
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    更新测试用例

    - **case_id**: 用例 ID
    - **name**: 新的用例名称
    - **description**: 新的描述
    - **priority**: 新的优先级
    - **tags**: 新的标签
    """
    # 调用服务层更新用例
    case = await case_service.update_case(db, case_id, case_data)
    # 如果用例不存在，抛出 404 异常
    if not case:
        raise HTTPException(status_code=404, detail=f"用例 {case_id} 不存在")

    # 转换步骤数据
    steps = []
    for step in case.steps:
        # 将步骤模型转换为响应对象
        steps.append(StepResponse(
            id=step.id,  # 步骤 ID
            case_id=step.case_id,  # 所属用例 ID
            step_order=step.step_order,  # 步骤顺序
            action_type=step.action_type,  # 操作类型
            element_locator=step.element_locator,  # 元素定位符
            locator_type=step.locator_type,  # 定位类型
            action_params=step.params_dict,  # 操作参数
            expected_result=step.expected_result,  # 期望结果
            description=step.description,  # 步骤描述
            created_at=step.created_at,  # 创建时间
            updated_at=step.updated_at  # 更新时间
        ))

    # 构建响应数据
    response_data = CaseResponse(
        id=case.id,  # 用例 ID
        name=case.name,  # 用例名称
        description=case.description,  # 用例描述
        priority=case.priority,  # 优先级
        tags=case.tags,  # 标签
        steps=steps,  # 步骤列表
        created_at=case.created_at,  # 创建时间
        updated_at=case.updated_at  # 更新时间
    )

    # 返回成功响应
    return ApiResponse(data=response_data, message="用例更新成功")


# 定义删除测试用例的 DELETE 请求处理器
@router.delete("/{case_id}", response_model=ApiResponse[None])
async def delete_case(
    case_id: int,  # 用例 ID 路径参数
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    删除测试用例

    - **case_id**: 用例 ID
    """
    # 调用服务层删除用例
    success = await case_service.delete_case(db, case_id)
    # 如果用例不存在，抛出 404 异常
    if not success:
        raise HTTPException(status_code=404, detail=f"用例 {case_id} 不存在")

    # 返回成功响应
    return ApiResponse(message="用例删除成功")


# 定义批量删除测试用例的 DELETE 请求处理器
@router.delete("/batch", response_model=ApiResponse[dict])
async def batch_delete_cases(
    request: BatchDeleteRequest,  # 批量删除请求数据体验证
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    批量删除测试用例

    - **case_ids**: 用例 ID 列表
    """
    # 调用服务层批量删除用例
    count = await case_service.batch_delete_cases(db, request.case_ids)

    # 返回成功响应，包含删除数量
    return ApiResponse(data={"deleted": count}, message=f"成功删除 {count} 个用例")


# 定义批量保存测试步骤的 PUT 请求处理器
@router.put("/{case_id}/steps", response_model=ApiResponse[CaseResponse])
async def save_steps(
    case_id: int,  # 用例 ID 路径参数
    steps_data: BatchStepCreate,  # 批量步骤请求数据体验证
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    批量保存测试步骤

    - **case_id**: 用例 ID
    - **steps**: 步骤数据列表
    """
    # 调用服务层保存步骤
    case = await case_service.save_steps(db, case_id, steps_data.steps)
    # 如果用例不存在，抛出 404 异常
    if not case:
        raise HTTPException(status_code=404, detail=f"用例 {case_id} 不存在")

    # 转换步骤数据
    steps = []
    for step in case.steps:
        # 将步骤模型转换为响应对象
        steps.append(StepResponse(
            id=step.id,  # 步骤 ID
            case_id=step.case_id,  # 所属用例 ID
            step_order=step.step_order,  # 步骤顺序
            action_type=step.action_type,  # 操作类型
            element_locator=step.element_locator,  # 元素定位符
            locator_type=step.locator_type,  # 定位类型
            action_params=step.params_dict,  # 操作参数
            expected_result=step.expected_result,  # 期望结果
            description=step.description,  # 步骤描述
            created_at=step.created_at,  # 创建时间
            updated_at=step.updated_at  # 更新时间
        ))

    # 构建响应数据
    response_data = CaseResponse(
        id=case.id,  # 用例 ID
        name=case.name,  # 用例名称
        description=case.description,  # 用例描述
        priority=case.priority,  # 优先级
        tags=case.tags,  # 标签
        steps=steps,  # 步骤列表
        created_at=case.created_at,  # 创建时间
        updated_at=case.updated_at  # 更新时间
    )

    # 返回成功响应
    return ApiResponse(data=response_data, message="步骤保存成功")
