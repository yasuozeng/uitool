"""
HTML 报告生成服务
使用 Jinja2 模板生成美观的 HTML 测试报告
"""
from typing import Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.execution import Execution, ExecutionDetail
from app.config import REPORTS_DIR
from app.schemas.report import ReportData, ExecutionSummary, CaseResultSummary


# 定义报告服务类
class ReportService:
    """
    报告生成服务

    负责收集执行数据并渲染为 HTML 报告
    """

    # 生成报告的异步方法
    async def generate_report(
        self,
        db: AsyncSession,
        execution_id: int,
        include_screenshots: bool = True,
        include_logs: bool = True
    ) -> dict:
        """
        生成 HTML 报告

        Args:
            db: 数据库会话
            execution_id: 执行 ID
            include_screenshots: 是否包含截图
            include_logs: 是否包含日志

        Returns:
            包含报告路径和下载 URL 的字典
        """
        # 1. 获取执行数据
        execution_data = await self._get_execution_data(db, execution_id)
        if not execution_data:
            return None

        # 2. 准备模板数据
        report_data = self._prepare_report_data(execution_data)

        # 3. 渲染 HTML
        html_content = await self._render_html(report_data)

        # 4. 保存报告文件
        report_path = await self._save_report(execution_id, html_content)

        # 5. 返回报告信息
        return {
            "report_id": f"report_{execution_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "html_path": report_path,
            "download_url": f"/api/v1/reports/download/{Path(report_path).name}"
        }

    # 获取执行数据的私有方法
    async def _get_execution_data(
        self,
        db: AsyncSession,
        execution_id: int
    ) -> Optional[tuple[Execution, list[ExecutionDetail]]]:
        """
        从数据库获取执行数据

        Args:
            db: 数据库会话
            execution_id: 执行 ID

        Returns:
            (执行记录, 详情列表) 元组或 None
        """
        # 构建查询：获取执行记录和关联的详情
        query = select(Execution).options(
            selectinload(Execution.details)
        ).where(Execution.id == execution_id)

        # 执行查询
        result = await db.execute(query)
        execution = result.scalar_one_or_none()

        if not execution:
            return None

        return execution, execution.details

    # 准备报告数据的私有方法
    def _prepare_report_data(
        self,
        data: tuple[Execution, list[ExecutionDetail]]
    ) -> ReportData:
        """
        准备报告模板数据

        Args:
            data: (执行记录, 详情列表) 元组

        Returns:
            报告数据对象
        """
        execution, details = data

        # 构建执行摘要
        execution_summary = ExecutionSummary(
            execution_id=execution.id,
            status=execution.status,
            browser=execution.browser_type,
            headless=execution.headless,
            total_cases=execution.total_count,
            passed_cases=execution.success_count,
            failed_cases=execution.fail_count,
            pass_rate=execution.pass_rate,
            started_at=execution.start_time.isoformat() if execution.start_time else "",
            completed_at=execution.end_time.isoformat() if execution.end_time else None,
            duration=execution.duration
        )

        # 构建用例结果列表
        case_summaries = []
        for detail in details:
            # 计算步骤统计（从日志中解析）
            step_count = 0
            passed_steps = 0
            failed_steps = 0
            if detail.status == "success":
                passed_steps = 1
                step_count = 1
            elif detail.status == "failed":
                failed_steps = 1
                step_count = 1

            case_summaries.append(CaseResultSummary(
                case_id=detail.case_id,
                case_name=detail.case_name,
                status=detail.status,
                step_count=step_count,
                passed_steps=passed_steps,
                failed_steps=failed_steps,
                error_message=detail.error_message,
                screenshot_path=detail.screenshot_path
            ))

        return ReportData(
            execution=execution_summary,
            cases=case_summaries
        )

    # 渲染 HTML 的私有方法
    async def _render_html(self, report_data: ReportData) -> str:
        """
        使用 Jinja2 渲染 HTML

        Args:
            report_data: 报告数据

        Returns:
            渲染后的 HTML 内容
        """
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        # 创建 Jinja2 环境
        template_dir = Path(__file__).parent.parent.parent / "templates"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # 加载模板
        template = env.get_template('report.html')

        # 渲染模板
        return template.render(
            report=report_data,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    # 保存报告的私有方法
    async def _save_report(self, execution_id: int, html_content: str) -> str:
        """
        保存 HTML 报告到文件

        Args:
            execution_id: 执行 ID
            html_content: HTML 内容

        Returns:
            报告文件路径
        """
        # 确保报告目录存在
        reports_dir = REPORTS_DIR
        reports_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{execution_id}_{timestamp}.html"
        file_path = reports_dir / filename

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(file_path)


# 创建全局服务实例，供其他模块导入使用
report_service = ReportService()
