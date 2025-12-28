"""
测试报告 API 路由
定义报告生成和下载相关的 HTTP 接口端点
"""
# 从 typing 模块导入类型注解工具
from typing import Dict
# 从 fastapi 导入路由器、依赖注入、异常等核心组件
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

# 从本地数据库模块导入数据库会话依赖
from app.models.database import get_db
# 从本地 schemas 模块导入报告相关的数据验证和响应格式
from app.schemas.report import ReportGenerateRequest
# 从本地 schemas 模块导入通用响应格式
from app.schemas.common import ApiResponse
# 从本地服务模块导入报告服务
from app.services.report_service import report_service
# 从本地配置模块导入报告目录
from app.config import REPORTS_DIR
from pathlib import Path

# 创建 API 路由器，设置 URL 前缀和标签
router = APIRouter(prefix="/reports", tags=["报告管理"])


# 定义生成报告的 POST 请求处理器
@router.post("/generate", response_model=ApiResponse[Dict])
async def generate_report(
    request_data: ReportGenerateRequest,  # 请求数据体验证
    db: AsyncSession = Depends(get_db)  # 注入数据库会话依赖
):
    """
    生成 HTML 测试报告

    - **execution_id**: 执行 ID
    - **include_screenshots**: 是否包含截图（默认 true）
    - **include_logs**: 是否包含日志（默认 true）
    """
    # 调用服务层生成报告
    result = await report_service.generate_report(
        db,
        request_data.execution_id,
        request_data.include_screenshots,
        request_data.include_logs
    )

    # 如果执行不存在，抛出 404 异常
    if not result:
        raise HTTPException(status_code=404, detail=f"执行 {request_data.execution_id} 不存在")

    # 返回成功响应
    return ApiResponse(data=result, message="报告生成成功")


# 定义下载报告的 GET 请求处理器
@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    下载 HTML 报告文件

    - **filename**: 报告文件名
    """
    # 构建文件路径
    file_path = REPORTS_DIR / filename

    # 检查文件是否存在
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="报告文件不存在")

    # 返回文件响应
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/html"
    )


# 定义获取报告列表的 GET 请求处理器
@router.get("", response_model=ApiResponse[list])
async def get_reports():
    """
    获取所有报告文件列表

    返回已生成的报告文件名列表
    """
    # 获取报告目录下的所有 HTML 文件
    reports = []
    if REPORTS_DIR.exists():
        for file_path in REPORTS_DIR.glob("*.html"):
            reports.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "created_time": file_path.stat().st_ctime
            })

    # 按创建时间倒序排列
    reports.sort(key=lambda x: x["created_time"], reverse=True)

    return ApiResponse(data=reports, message="获取报告列表成功")
