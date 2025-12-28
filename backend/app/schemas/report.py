"""
报告相关的 Pydantic 模式定义
定义报告生成和导出相关的数据验证和响应格式
"""
from typing import Optional
from pydantic import BaseModel


# ========== 报告生成请求 ==========

class ReportGenerateRequest(BaseModel):
    """生成报告请求"""
    execution_id: int
    include_screenshots: bool = True
    include_logs: bool = True


# ========== 报告响应 ==========

class CaseResultSummary(BaseModel):
    """用例结果摘要"""
    case_id: int
    case_name: str
    status: str  # completed, failed
    step_count: int
    passed_steps: int
    failed_steps: int
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None


class ExecutionSummary(BaseModel):
    """执行摘要"""
    execution_id: int
    status: str
    browser: str
    headless: bool
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float  # 通过率百分比
    started_at: str
    completed_at: Optional[str] = None
    duration: Optional[int] = None  # 秒


class ReportData(BaseModel):
    """报告数据"""
    execution: ExecutionSummary
    cases: list[CaseResultSummary]


class ReportResponse(BaseModel):
    """报告响应"""
    report_id: str
    html_path: str
    download_url: str
