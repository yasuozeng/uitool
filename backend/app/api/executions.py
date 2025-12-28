"""
测试执行 API 路由
定义测试执行任务管理相关的 HTTP 接口端点
"""
# 从 typing 模块导入类型注解工具
from typing import List
# 从 fastapi 导入路由器、依赖注入、异常、Query 等核心组件
from fastapi import APIRouter, Depends, HTTPException, Query
# 从 sqlalchemy.ext.asyncio 导入异步会话
from sqlalchemy.ext.asyncio import AsyncSession

# 从本地数据库模块导入数据库会话依赖
from app.models.database import get_db
# 从本地 schemas 模块导入执行相关的数据验证和响应格式
from app.schemas.execution import (
    ExecutionCreate,  # 创建执行任务的数据模式
    ExecutionResponse,  # 执行任务响应模式
    ExecutionListResponse,  # 执行任务列表响应模式
    ExecutionDetailResponse  # 执行详情响应模式
)
# 从本地 schemas 模块导入通用响应格式
from app.schemas.common import ApiResponse, PaginatedResponse
# 从本地服务模块导入执行服务
from app.services.execution_service import execution_service

# 创建 API 路由器，设置 URL 前缀和标签
router = APIRouter(prefix="/executions", tags=["执行管理"])


# 定义获取执行任务列表的 GET 请求处理器
@router.get("", response_model=PaginatedResponse[ExecutionListResponse])
async def get_executions(
    status: str = Query(None, pattern="^(pending|running|completed|failed)$", description="按状态筛选"),  # 状态筛选参数
    browser_type: str = Query(None, pattern="^(chrome|firefox|edge)$", description="按浏览器筛选"),  # 浏览器筛选参数
    page: int = Query(1, ge=1, description="页码"),  # 页码参数，最小值 1
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),  # 每页数量参数，范围 1-100
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    获取执行任务列表（分页）

    - **status**: 按状态筛选
    - **browser_type**: 按浏览器类型筛选
    - **page**: 页码，从 1 开始
    - **page_size**: 每页数量，最大 100
    """
    # 调用服务层获取执行列表和总数
    executions, total = await execution_service.get_executions(
        db, status=status, browser_type=browser_type,
        page=page, page_size=page_size
    )

    # 计算总页数（向上取整）
    pages = (total + page_size - 1) // page_size

    # 转换为响应格式
    execution_list = []
    for execution in executions:
        # 将数据库模型转换为响应对象
        execution_list.append(ExecutionListResponse(
            id=execution.id,  # 执行任务 ID
            execution_type=execution.execution_type,  # 执行类型
            browser_type=execution.browser_type,  # 浏览器类型
            status=execution.status,  # 执行状态
            total_count=execution.total_count,  # 总用例数
            success_count=execution.success_count,  # 成功数
            fail_count=execution.fail_count,  # 失败数
            pass_rate=execution.pass_rate,  # 通过率
            start_time=execution.start_time,  # 开始时间
            created_at=execution.created_at  # 创建时间
        ))

    # 返回分页响应
    return PaginatedResponse(
        data=execution_list,  # 执行列表数据
        total=total,  # 总记录数
        page=page,  # 当前页码
        page_size=page_size,  # 每页数量
        pages=pages  # 总页数
    )


# 定义创建执行任务的 POST 请求处理器
@router.post("", response_model=ApiResponse[ExecutionResponse], status_code=201)
async def create_execution(
    execution_data: ExecutionCreate,  # 请求数据体验证
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    创建执行任务

    - **execution_type**: 执行类型 (single/batch)
    - **browser_type**: 浏览器类型 (chrome/firefox/edge)
    - **headless**: 无头模式
    - **window_size**: 窗口大小
    - **case_ids**: 用例 ID 列表
    """
    # 调用服务层创建执行任务
    execution = await execution_service.create_execution(db, execution_data)

    # 构建响应数据
    response_data = ExecutionResponse(
        id=execution.id,  # 执行任务 ID
        execution_type=execution.execution_type,  # 执行类型
        browser_type=execution.browser_type,  # 浏览器类型
        headless=execution.headless,  # 无头模式
        window_size=execution.window_size,  # 窗口大小
        start_time=execution.start_time,  # 开始时间
        end_time=execution.end_time,  # 结束时间
        total_count=execution.total_count,  # 总用例数
        success_count=execution.success_count,  # 成功数
        fail_count=execution.fail_count,  # 失败数
        skip_count=execution.skip_count,  # 跳过数
        status=execution.status,  # 执行状态
        pass_rate=execution.pass_rate,  # 通过率
        duration=execution.duration,  # 执行时长
        created_at=execution.created_at  # 创建时间
    )

    # 返回成功响应（状态码 201）
    return ApiResponse(data=response_data, message="执行任务创建成功")


# 定义获取执行任务详情的 GET 请求处理器
@router.get("/{execution_id}", response_model=ApiResponse[ExecutionResponse])
async def get_execution(
    execution_id: int,  # 执行任务 ID 路径参数
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    获取执行任务详情

    - **execution_id**: 执行 ID
    """
    # 调用服务层获取执行任务详情
    execution = await execution_service.get_execution_by_id(db, execution_id)
    # 如果执行任务不存在，抛出 404 异常
    if not execution:
        raise HTTPException(status_code=404, detail=f"执行任务 {execution_id} 不存在")

    # 构建响应数据
    response_data = ExecutionResponse(
        id=execution.id,  # 执行任务 ID
        execution_type=execution.execution_type,  # 执行类型
        browser_type=execution.browser_type,  # 浏览器类型
        headless=execution.headless,  # 无头模式
        window_size=execution.window_size,  # 窗口大小
        start_time=execution.start_time,  # 开始时间
        end_time=execution.end_time,  # 结束时间
        total_count=execution.total_count,  # 总用例数
        success_count=execution.success_count,  # 成功数
        fail_count=execution.fail_count,  # 失败数
        skip_count=execution.skip_count,  # 跳过数
        status=execution.status,  # 执行状态
        pass_rate=execution.pass_rate,  # 通过率
        duration=execution.duration,  # 执行时长
        created_at=execution.created_at  # 创建时间
    )

    # 返回统一响应格式
    return ApiResponse(data=response_data)


# 定义获取执行任务详细信息的 GET 请求处理器
@router.get("/{execution_id}/details", response_model=ApiResponse[List[ExecutionDetailResponse]])
async def get_execution_details(
    execution_id: int,  # 执行任务 ID 路径参数
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    获取执行任务的详细信息

    包含每个用例的执行结果详情

    - **execution_id**: 执行 ID
    """
    # 调用服务层获取执行任务（包含详情）
    execution = await execution_service.get_execution_by_id(db, execution_id)
    # 如果执行任务不存在，抛出 404 异常
    if not execution:
        raise HTTPException(status_code=404, detail=f"执行任务 {execution_id} 不存在")

    # 转换详情数据
    details_list = []
    for detail in execution.details:
        # 将详情模型转换为响应对象
        details_list.append(ExecutionDetailResponse(
            id=detail.id,  # 详情 ID
            execution_id=detail.execution_id,  # 所属执行任务 ID
            case_id=detail.case_id,  # 用例 ID
            case_name=detail.case_name,  # 用例名称
            status=detail.status,  # 执行状态
            error_message=detail.error_message,  # 错误消息
            error_stack=detail.error_stack,  # 错误堆栈
            screenshot_path=detail.screenshot_path,  # 截图路径
            step_logs=detail.logs_list,  # 步骤日志列表
            start_time=detail.start_time,  # 开始时间
            end_time=detail.end_time,  # 结束时间
            duration=detail.duration,  # 执行时长
            created_at=detail.created_at  # 创建时间
        ))

    # 返回详情列表
    return ApiResponse(data=details_list)


# 定义启动执行任务的 POST 请求处理器
@router.post("/{execution_id}/start", response_model=ApiResponse[ExecutionResponse])
async def start_execution(
    execution_id: int,  # 执行任务 ID 路径参数
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    启动执行任务

    - **execution_id**: 执行 ID
    """
    # 调用服务层启动执行任务
    execution = await execution_service.start_execution(db, execution_id)
    # 如果执行任务不存在，抛出 404 异常
    if not execution:
        raise HTTPException(status_code=404, detail=f"执行任务 {execution_id} 不存在")

    # 构建响应数据
    response_data = ExecutionResponse(
        id=execution.id,  # 执行任务 ID
        execution_type=execution.execution_type,  # 执行类型
        browser_type=execution.browser_type,  # 浏览器类型
        headless=execution.headless,  # 无头模式
        window_size=execution.window_size,  # 窗口大小
        start_time=execution.start_time,  # 开始时间
        end_time=execution.end_time,  # 结束时间
        total_count=execution.total_count,  # 总用例数
        success_count=execution.success_count,  # 成功数
        fail_count=execution.fail_count,  # 失败数
        skip_count=execution.skip_count,  # 跳过数
        status=execution.status,  # 执行状态
        pass_rate=execution.pass_rate,  # 通过率
        duration=execution.duration,  # 执行时长
        created_at=execution.created_at  # 创建时间
    )

    # 返回成功响应
    return ApiResponse(data=response_data, message="执行任务已启动")


# 定义停止执行任务的 POST 请求处理器
@router.post("/{execution_id}/stop", response_model=ApiResponse[ExecutionResponse])
async def stop_execution(
    execution_id: int,  # 执行任务 ID 路径参数
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    停止执行任务

    - **execution_id**: 执行 ID
    """
    # 调用服务层停止执行任务
    success = await execution_service.stop_execution(db, execution_id)
    # 如果执行任务不存在，抛出 404 异常
    if not success:
        raise HTTPException(status_code=404, detail=f"执行任务 {execution_id} 不存在")

    # 重新获取执行任务状态
    execution = await execution_service.get_execution_by_id(db, execution_id)

    # 构建响应数据
    response_data = ExecutionResponse(
        id=execution.id,  # 执行任务 ID
        execution_type=execution.execution_type,  # 执行类型
        browser_type=execution.browser_type,  # 浏览器类型
        headless=execution.headless,  # 无头模式
        window_size=execution.window_size,  # 窗口大小
        start_time=execution.start_time,  # 开始时间
        end_time=execution.end_time,  # 结束时间
        total_count=execution.total_count,  # 总用例数
        success_count=execution.success_count,  # 成功数
        fail_count=execution.fail_count,  # 失败数
        skip_count=execution.skip_count,  # 跳过数
        status=execution.status,  # 执行状态
        pass_rate=execution.pass_rate,  # 通过率
        duration=execution.duration,  # 执行时长
        created_at=execution.created_at  # 创建时间
    )

    # 返回成功响应
    return ApiResponse(data=response_data, message="执行任务已停止")
