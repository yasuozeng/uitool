"""
测试报告服务测试
测试 ReportService 的报告生成功能
"""
# 导入 pytest 测试框架和异步标记
import pytest
# 导入操作系统相关模块，用于文件操作
import os
# 导入 Path 路径处理类
from pathlib import Path
# 从 datetime 导入 datetime 类
from datetime import datetime

# 导入报告服务
from app.services.report_service import report_service
# 导入数据模式
from app.models.execution import Execution, ExecutionDetail
# 导入配置
from app.config import REPORTS_DIR


class TestReportServiceGetExecutionData:
    """测试获取执行数据方法（通过公共方法间接测试）"""

    @pytest.mark.asyncio
    async def test_get_execution_data_success(self, db_session):
        """测试成功获取执行数据"""
        # 创建测试执行记录
        execution = Execution(
            execution_type="single",
            browser_type="chromium",
            headless=True,
            window_size="1920x1080",
            status="completed",
            total_count=2,
            success_count=1,
            fail_count=1,
            start_time=datetime(2025, 12, 27, 10, 0, 0),
            end_time=datetime(2025, 12, 27, 10, 1, 0),
            created_at=datetime(2025, 12, 27, 10, 0, 0)
        )
        db_session.add(execution)
        await db_session.commit()
        await db_session.refresh(execution)

        # 创建执行详情
        detail1 = ExecutionDetail(
            execution_id=execution.id,
            case_id=1,
            case_name="测试用例1",
            status="success",
            start_time=datetime(2025, 12, 27, 10, 0, 0),
            end_time=datetime(2025, 12, 27, 10, 0, 30),
            duration=30000,
            created_at=datetime(2025, 12, 27, 10, 0, 0)
        )
        detail2 = ExecutionDetail(
            execution_id=execution.id,
            case_id=2,
            case_name="测试用例2",
            status="failed",
            error_message="元素未找到",
            start_time=datetime(2025, 12, 27, 10, 0, 30),
            end_time=datetime(2025, 12, 27, 10, 1, 0),
            duration=30000,
            created_at=datetime(2025, 12, 27, 10, 0, 30)
        )
        db_session.add_all([detail1, detail2])
        await db_session.commit()

        # 调用服务方法
        result = await report_service._get_execution_data(db_session, execution.id)

        # 验证：返回执行数据和详情列表
        assert result is not None
        execution_result, details = result
        assert execution_result.id == execution.id
        assert len(details) == 2

    @pytest.mark.asyncio
    async def test_get_execution_data_not_exists(self, db_session):
        """测试获取不存在的执行数据"""
        # 调用服务方法（ID 不存在）
        result = await report_service._get_execution_data(db_session, 999)

        # 验证：返回 None
        assert result is None

    @pytest.mark.asyncio
    async def test_get_execution_data_with_no_details(self, db_session):
        """测试获取没有详情的执行数据"""
        # 创建测试执行记录（无详情）
        execution = Execution(
            execution_type="single",
            browser_type="chromium",
            window_size="1920x1080",
            status="pending",
            created_at=datetime(2025, 12, 27, 10, 0, 0)
        )
        db_session.add(execution)
        await db_session.commit()
        await db_session.refresh(execution)

        # 调用服务方法
        result = await report_service._get_execution_data(db_session, execution.id)

        # 验证：返回执行数据，详情列表为空
        assert result is not None
        execution_result, details = result
        assert execution_result.id == execution.id
        assert len(details) == 0


class TestReportServicePrepareReportData:
    """测试准备报告数据方法"""

    def test_prepare_report_data_success(self):
        """测试成功准备报告数据"""
        # 创建测试执行记录
        execution = Execution(
            id=1,
            execution_type="single",
            status="completed",
            browser_type="chromium",
            headless=True,
            window_size="1920x1080",
            total_count=2,
            success_count=1,
            fail_count=1,
            start_time=datetime(2025, 12, 27, 10, 0, 0),
            end_time=datetime(2025, 12, 27, 10, 5, 0),
            created_at=datetime(2025, 12, 27, 10, 0, 0)
        )

        # 创建测试详情列表
        details = [
            ExecutionDetail(
                case_id=1,
                case_name="测试用例1",
                status="success",
                start_time=datetime(2025, 12, 27, 10, 0, 0),
                end_time=datetime(2025, 12, 27, 10, 2, 0),
                duration=120000,
                created_at=datetime(2025, 12, 27, 10, 0, 0)
            ),
            ExecutionDetail(
                case_id=2,
                case_name="测试用例2",
                status="failed",
                error_message="元素超时",
                screenshot_path="/api/screenshots/error_1.png",
                start_time=datetime(2025, 12, 27, 10, 2, 0),
                end_time=datetime(2025, 12, 27, 10, 5, 0),
                duration=180000,
                created_at=datetime(2025, 12, 27, 10, 2, 0)
            )
        ]

        # 调用服务方法
        result = report_service._prepare_report_data((execution, details))

        # 验证：执行摘要正确
        assert result.execution.execution_id == 1
        assert result.execution.status == "completed"
        assert result.execution.browser == "chromium"
        assert result.execution.headless is True
        assert result.execution.total_cases == 2
        assert result.execution.passed_cases == 1
        assert result.execution.failed_cases == 1
        assert result.execution.pass_rate == 50.0
        assert result.execution.started_at == "2025-12-27T10:00:00"
        assert result.execution.completed_at == "2025-12-27T10:05:00"
        assert result.execution.duration == 300000

        # 验证：用例摘要列表正确
        assert len(result.cases) == 2
        assert result.cases[0].case_name == "测试用例1"
        assert result.cases[0].status == "success"
        assert result.cases[0].step_count == 1
        assert result.cases[0].passed_steps == 1
        assert result.cases[0].failed_steps == 0

        assert result.cases[1].case_name == "测试用例2"
        assert result.cases[1].status == "failed"
        assert result.cases[1].error_message == "元素超时"
        assert result.cases[1].screenshot_path == "/api/screenshots/error_1.png"

    def test_prepare_report_data_all_success(self):
        """测试全部成功的报告数据"""
        # 创建测试执行记录（全部成功）
        execution = Execution(
            id=1,
            execution_type="batch",
            status="completed",
            browser_type="firefox",
            headless=False,
            window_size="1920x1080",
            total_count=3,
            success_count=3,
            fail_count=0,
            start_time=datetime(2025, 12, 27, 10, 0, 0),
            created_at=datetime(2025, 12, 27, 10, 0, 0)
        )

        # 创建测试详情列表
        details = [
            ExecutionDetail(
                case_id=i,
                case_name=f"用例{i}",
                status="success",
                start_time=datetime(2025, 12, 27, 10, 0, 0),
                end_time=datetime(2025, 12, 27, 10, 1, 0),
                duration=60000,
                created_at=datetime(2025, 12, 27, 10, 0, 0)
            )
            for i in range(1, 4)
        ]

        # 调用服务方法
        result = report_service._prepare_report_data((execution, details))

        # 验证：全部通过
        assert result.execution.pass_rate == 100.0
        assert all(case.status == "success" for case in result.cases)
        assert all(case.passed_steps == 1 for case in result.cases)

    def test_prepare_report_data_all_failed(self):
        """测试全部失败的报告数据"""
        # 创建测试执行记录（全部失败）
        execution = Execution(
            id=1,
            execution_type="batch",
            status="completed",
            browser_type="webkit",
            headless=True,
            window_size="1920x1080",
            total_count=2,
            success_count=0,
            fail_count=2,
            start_time=datetime(2025, 12, 27, 10, 0, 0),
            created_at=datetime(2025, 12, 27, 10, 0, 0)
        )

        # 创建测试详情列表
        details = [
            ExecutionDetail(
                case_id=1,
                case_name="失败用例1",
                status="failed",
                error_message="错误1",
                start_time=datetime(2025, 12, 27, 10, 0, 0),
                end_time=datetime(2025, 12, 27, 10, 1, 0),
                duration=60000,
                created_at=datetime(2025, 12, 27, 10, 0, 0)
            ),
            ExecutionDetail(
                case_id=2,
                case_name="失败用例2",
                status="failed",
                error_message="错误2",
                start_time=datetime(2025, 12, 27, 10, 1, 0),
                end_time=datetime(2025, 12, 27, 10, 2, 0),
                duration=60000,
                created_at=datetime(2025, 12, 27, 10, 1, 0)
            )
        ]

        # 调用服务方法
        result = report_service._prepare_report_data((execution, details))

        # 验证：全部失败
        assert result.execution.pass_rate == 0.0
        assert all(case.status == "failed" for case in result.cases)
        assert all(case.failed_steps == 1 for case in result.cases)


class TestReportServiceRenderHtml:
    """测试渲染 HTML 方法"""

    @pytest.mark.asyncio
    async def test_render_html_success(self):
        """测试成功渲染 HTML"""
        # 创建报告数据（使用简单的模拟数据）
        from app.schemas.report import ReportData, ExecutionSummary, CaseResultSummary

        report_data = ReportData(
            execution=ExecutionSummary(
                execution_id=1,
                status="completed",
                browser="chromium",
                headless=True,
                total_cases=1,
                passed_cases=1,
                failed_cases=0,
                pass_rate=100.0,
                started_at="2025-12-27T10:00:00",
                completed_at="2025-12-27T10:01:00",
                duration=60000
            ),
            cases=[
                CaseResultSummary(
                    case_id=1,
                    case_name="测试用例",
                    status="success",
                    step_count=1,
                    passed_steps=1,
                    failed_steps=0
                )
            ]
        )

        # 调用服务方法
        html_content = await report_service._render_html(report_data)

        # 验证：HTML 内容包含关键信息
        assert html_content is not None
        assert len(html_content) > 0
        assert "测试用例" in html_content
        assert "100.0%" in html_content or "100%" in html_content
        assert "Chromium" in html_content  # 模板使用 title 过滤器

    @pytest.mark.asyncio
    async def test_render_html_with_failed_cases(self):
        """测试渲染包含失败用例的 HTML"""
        from app.schemas.report import ReportData, ExecutionSummary, CaseResultSummary

        report_data = ReportData(
            execution=ExecutionSummary(
                execution_id=1,
                status="completed",
                browser="chromium",
                headless=True,
                total_cases=2,
                passed_cases=1,
                failed_cases=1,
                pass_rate=50.0,
                started_at="2025-12-27T10:00:00",
                completed_at="2025-12-27T10:02:00",
                duration=120000
            ),
            cases=[
                CaseResultSummary(
                    case_id=1,
                    case_name="成功用例",
                    status="success",
                    step_count=1,
                    passed_steps=1,
                    failed_steps=0
                ),
                CaseResultSummary(
                    case_id=2,
                    case_name="失败用例",
                    status="failed",
                    step_count=1,
                    passed_steps=0,
                    failed_steps=1,
                    error_message="元素未找到"
                )
            ]
        )

        # 调用服务方法
        html_content = await report_service._render_html(report_data)

        # 验证：HTML 包含失败信息
        assert "失败用例" in html_content
        assert "元素未找到" in html_content


class TestReportServiceSaveReport:
    """测试保存报告方法"""

    @pytest.mark.asyncio
    async def test_save_report_success(self, tmp_path):
        """测试成功保存报告"""
        # 临时修改 REPORTS_DIR 以使用 tmp_path
        import app.config
        original_dir = app.config.REPORTS_DIR
        app.config.REPORTS_DIR = tmp_path

        try:
            # HTML 内容
            html_content = "<html><body>测试报告</body></html>"

            # 调用服务方法
            report_path = await report_service._save_report(1, html_content)

            # 验证：文件已创建
            assert report_path is not None
            assert Path(report_path).exists()

            # 验证：文件内容正确
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert content == html_content

            # 验证：文件名格式正确
            filename = Path(report_path).name
            assert filename.startswith("report_1_")
            assert filename.endswith(".html")

        finally:
            # 恢复原始配置
            app.config.REPORTS_DIR = original_dir

    @pytest.mark.asyncio
    async def test_save_report_creates_directory(self, tmp_path):
        """测试保存报告时自动创建目录"""
        import app.config
        original_dir = app.config.REPORTS_DIR
        # 使用一个不存在的子目录
        app.config.REPORTS_DIR = tmp_path / "nonexistent" / "reports"

        try:
            html_content = "<html><body>测试</body></html>"

            # 调用服务方法
            report_path = await report_service._save_report(1, html_content)

            # 验证：目录已创建，文件已保存
            assert Path(report_path).exists()
            assert Path(report_path).parent.exists()

        finally:
            app.config.REPORTS_DIR = original_dir

    @pytest.mark.asyncio
    async def test_save_report_unicode_content(self, tmp_path):
        """测试保存包含 Unicode 字符的报告"""
        import app.config
        original_dir = app.config.REPORTS_DIR
        app.config.REPORTS_DIR = tmp_path

        try:
            # 包含中文和特殊字符的 HTML
            html_content = "<html><body>测试报告 🎉 <特殊> &符号</body></html>"

            # 调用服务方法
            report_path = await report_service._save_report(1, html_content)

            # 验证：Unicode 字符正确保存
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert content == html_content
                assert "🎉" in content
                assert "<特殊>" in content

        finally:
            app.config.REPORTS_DIR = original_dir


class TestReportServiceGenerateReport:
    """测试生成报告完整流程"""

    @pytest.mark.asyncio
    async def test_generate_report_success(self, db_session, tmp_path):
        """测试完整生成报告流程"""
        import app.config
        original_dir = app.config.REPORTS_DIR
        app.config.REPORTS_DIR = tmp_path

        try:
            # 创建测试执行记录
            execution = Execution(
                execution_type="single",
                browser_type="chromium",
                headless=True,
                window_size="1920x1080",
                status="completed",
                total_count=1,
                success_count=1,
                fail_count=0,
                start_time=datetime(2025, 12, 27, 10, 0, 0),
                end_time=datetime(2025, 12, 27, 10, 1, 0),
                created_at=datetime(2025, 12, 27, 10, 0, 0)
            )
            db_session.add(execution)
            await db_session.commit()
            await db_session.refresh(execution)

            # 创建执行详情
            detail = ExecutionDetail(
                execution_id=execution.id,
                case_id=1,
                case_name="测试用例",
                status="success",
                start_time=datetime(2025, 12, 27, 10, 0, 0),
                end_time=datetime(2025, 12, 27, 10, 1, 0),
                duration=60000,
                created_at=datetime(2025, 12, 27, 10, 0, 0)
            )
            db_session.add(detail)
            await db_session.commit()

            # 调用服务方法
            result = await report_service.generate_report(db_session, execution.id)

            # 验证：返回报告信息
            assert result is not None
            assert "report_id" in result
            assert "html_path" in result
            assert "download_url" in result

            # 验证：报告文件已创建
            assert Path(result["html_path"]).exists()

            # 验证：文件内容是有效的 HTML
            with open(result["html_path"], 'r', encoding='utf-8') as f:
                content = f.read()
                assert "<html" in content.lower()
                assert "测试用例" in content

        finally:
            app.config.REPORTS_DIR = original_dir

    @pytest.mark.asyncio
    async def test_generate_report_not_exists(self, db_session):
        """测试生成不存在的执行报告"""
        # 调用服务方法（执行 ID 不存在）
        result = await report_service.generate_report(db_session, 999)

        # 验证：返回 None
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_report_with_failed_cases(self, db_session, tmp_path):
        """测试生成包含失败用例的报告"""
        import app.config
        original_dir = app.config.REPORTS_DIR
        app.config.REPORTS_DIR = tmp_path

        try:
            # 创建测试执行记录（包含失败）
            execution = Execution(
                execution_type="batch",
                browser_type="firefox",
                headless=False,
                window_size="1920x1080",
                status="completed",
                total_count=2,
                success_count=1,
                fail_count=1,
                start_time=datetime(2025, 12, 27, 10, 0, 0),
                created_at=datetime(2025, 12, 27, 10, 0, 0)
            )
            db_session.add(execution)
            await db_session.commit()
            await db_session.refresh(execution)

            # 创建执行详情（包含失败）
            detail1 = ExecutionDetail(
                execution_id=execution.id,
                case_id=1,
                case_name="成功用例",
                status="success",
                start_time=datetime(2025, 12, 27, 10, 0, 0),
                end_time=datetime(2025, 12, 27, 10, 0, 30),
                duration=30000,
                created_at=datetime(2025, 12, 27, 10, 0, 0)
            )
            detail2 = ExecutionDetail(
                execution_id=execution.id,
                case_id=2,
                case_name="失败用例",
                status="failed",
                error_message="超时错误",
                screenshot_path="/api/screenshots/error.png",
                start_time=datetime(2025, 12, 27, 10, 0, 30),
                end_time=datetime(2025, 12, 27, 10, 1, 0),
                duration=30000,
                created_at=datetime(2025, 12, 27, 10, 0, 30)
            )
            db_session.add_all([detail1, detail2])
            await db_session.commit()

            # 调用服务方法
            result = await report_service.generate_report(db_session, execution.id)

            # 验证：报告生成成功
            assert result is not None
            assert Path(result["html_path"]).exists()

            # 验证：HTML 包含失败信息
            with open(result["html_path"], 'r', encoding='utf-8') as f:
                content = f.read()
                assert "失败用例" in content
                assert "超时错误" in content

        finally:
            app.config.REPORTS_DIR = original_dir
