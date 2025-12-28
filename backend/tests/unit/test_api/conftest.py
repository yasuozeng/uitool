"""
API 测试模块的 pytest 配置
导入 API 测试所需的 fixtures
"""
# 导入 API 测试相关的 fixtures
from tests.fixtures.api_fixtures import (
    client,  # FastAPI 测试客户端
    mock_playwright_engine,  # Mock Playwright 引擎
    sample_execution_data,  # 执行记录样本数据
    sample_single_execution_data,  # 单个执行样本数据
    sample_case_data,  # 用例样本数据
    sample_case_update_data,  # 用例更新样本数据
    sample_batch_delete_data,  # 批量删除样本数据
    # 报告测试 fixtures
    temp_reports_dir,  # 临时报告目录
    sample_report_file,  # 示例报告文件
    sample_report_files,  # 多个示例报告文件
    sample_report_with_screenshots,  # 包含截图的报告文件
    mock_report_service,  # Mock 报告服务
    # 基础接口测试 fixtures
    sample_screenshot_file,  # 示例截图文件
    health_check_response_time_threshold,  # 健康检查响应时间阈值
)

# 导入数据库 fixtures（所有 API 测试都需要）
from tests.fixtures.db_fixtures import db_session
