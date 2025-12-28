# uiTool1.0 API 接口层单元测试计划

## 文档信息

- **项目名称**: uiTool1.0 - UI自动化测试平台
- **文档类型**: API 接口层单元测试计划
- **版本**: v1.0
- **创建日期**: 2025-12-27
- **涉及阶段**: 第二阶段 - API 接口层

---

## 一、测试目标

为第二阶段 API 接口层编写完整的单元测试，包括 Schemas、Services 和 API Routes，确保接口质量和功能正确性。

### 测试范围

| 层级 | 文件 | 测试内容 |
|-----|------|---------|
| **Schemas** | `schemas/common.py` | 通用响应模式验证 |
| | `schemas/case.py` | 用例和步骤数据验证 |
| | `schemas/execution.py` | 执行数据验证 |
| **Services** | `services/case_service.py` | 用例 CRUD 业务逻辑 |
| | `services/execution_service.py` | 执行任务业务逻辑 |
| **API Routes** | `api/cases.py` | 用例管理接口 |
| | `api/executions.py` | 执行管理接口 |
| **Main App** | `main.py` | FastAPI 应用配置 |

---

## 二、测试框架

| 框架/工具 | 版本要求 | 用途 |
|---------|---------|------|
| pytest | 7.4+ | 测试框架 |
| pytest-asyncio | 0.21+ | 异步测试 |
| FastAPI | 0.104+ | TestClient |
| pytest-mock | 3.12+ | Mock 功能 |
| pytest-cov | 4.1+ | 覆盖率报告 |

---

## 三、测试文件结构

```
backend/tests/
├── unit/
│   ├── test_schemas/              # Schema 测试
│   │   ├── __init__.py
│   │   ├── test_common.py         # 通用响应模式
│   │   ├── test_case_schemas.py   # 用例模式
│   │   └── test_execution_schemas.py  # 执行模式
│   ├── test_services/             # Service 测试
│   │   ├── __init__.py
│   │   ├── test_case_service.py   # 用例服务
│   │   └── test_execution_service.py  # 执行服务
│   └── test_api/                  # API 测试
│       ├── __init__.py
│       ├── test_cases_api.py      # 用例接口
│       └── test_executions_api.py # 执行接口
├── integration/                   # 集成测试
│   ├── __init__.py
│   └── test_api_integration.py
└── fixtures/
    ├── api_fixtures.py           # API fixtures
    └── db_fixtures.py            # 数据库 fixtures
```

---

## 四、测试用例规划

### 4.1 Schemas 测试（30-40 个）

#### test_common.py - 通用响应模式

```python
# ApiResponse 测试
- test_api_response_default_values
- test_api_response_with_success_code
- test_api_response_with_custom_code
- test_api_response_with_data

# PaginatedResponse 测试
- test_paginated_response_default_values
- test_paginated_response_calculates_pages

# ErrorResponse 测试
- test_error_response_required_fields
- test_error_response_all_fields
```

#### test_case_schemas.py - 用例模式测试

```python
# StepBase 相关测试
- test_step_base_valid_data
- test_step_base_invalid_order_zero
- test_step_base_invalid_order_negative

# CaseBase 相关测试
- test_case_base_valid_data
- test_case_base_name_too_short
- test_case_base_name_too_long
- test_case_base_invalid_priority

# CaseCreate 测试
- test_case_create_with_steps
- test_case_create_without_steps

# CaseResponse 测试
- test_case_response_from_model
- test_case_response_serialization
```

#### test_execution_schemas.py - 执行模式测试

```python
# ExecutionCreate 测试
- test_execution_create_single_type
- test_execution_create_batch_type
- test_execution_create_invalid_type
- test_execution_create_invalid_browser

# ExecutionResponse 测试
- test_execution_response_from_model
- test_execution_response_pass_rate_calculation
```

### 4.2 Services 测试（40-50 个）

#### test_case_service.py - 用例服务测试

```python
# 查询测试
- test_get_cases_empty_database
- test_get_cases_returns_list
- test_get_cases_with_name_filter
- test_get_cases_with_priority_filter
- test_get_cases_with_tags_filter
- test_get_cases_pagination_first_page
- test_get_cases_pagination_second_page
- test_get_cases_pagination_page_size

# 单条查询测试
- test_get_case_by_id_found
- test_get_case_by_id_not_found
- test_get_case_by_id_includes_steps

# 创建测试
- test_create_case_basic
- test_create_case_with_single_step
- test_create_case_with_multiple_steps
- test_create_case_sets_priority_default

# 更新测试
- test_update_case_name_only
- test_update_case_all_fields
- test_update_case_not_found

# 删除测试
- test_delete_case_success
- test_delete_case_not_found
- test_delete_case_with_steps

# 批量删除测试
- test_batch_delete_cases_empty_list
- test_batch_delete_cases_multiple
- test_batch_delete_cases_partial_not_found

# 步骤保存测试
- test_save_steps_replace_existing
- test_save_steps_case_not_found
- test_save_steps_empty_list
```

#### test_execution_service.py - 执行服务测试

```python
# 查询测试
- test_get_executions_empty_database
- test_get_executions_with_status_filter
- test_get_executions_with_browser_filter

# 创建测试
- test_create_execution_single_with_case_ids
- test_create_execution_batch_with_case_ids
- test_create_execution_batch_without_case_ids_uses_all
- test_create_execution_sets_defaults

# 启动执行测试（使用 mock 引擎）
- test_start_execution_success
- test_start_execution_not_found
- test_start_execution_updates_status

# 停止执行测试
- test_stop_execution_success
- test_stop_execution_not_found
- test_stop_execution_closes_browser
```

### 4.3 API Routes 测试（30-40 个）

#### test_cases_api.py - 用例接口测试

```python
# GET /api/v1/cases
- test_get_cases_success_empty
- test_get_cases_success_with_data
- test_get_cases_with_name_param
- test_get_cases_with_priority_param
- test_get_cases_pagination_page_1
- test_get_cases_pagination_page_2
- test_get_cases_invalid_page_negative
- test_get_cases_invalid_page_size

# GET /api/v1/cases/{id}
- test_get_case_by_id_success
- test_get_case_by_id_not_found_404
- test_get_case_by_id_includes_steps

# POST /api/v1/cases
- test_create_case_success_201
- test_create_case_invalid_priority_422
- test_create_case_name_too_short_422

# PUT /api/v1/cases/{id}
- test_update_case_success_200
- test_update_case_not_found_404
- test_update_case_invalid_priority_422

# DELETE /api/v1/cases/{id}
- test_delete_case_success_200
- test_delete_case_not_found_404

# DELETE /api/v1/cases/batch
- test_batch_delete_cases_success
- test_batch_delete_cases_empty_list

# PUT /api/v1/cases/{id}/steps
- test_save_steps_success_200
- test_save_steps_case_not_found_404
- test_save_steps_empty_list
```

#### test_executions_api.py - 执行接口测试

```python
# GET /api/v1/executions
- test_get_executions_success_empty
- test_get_executions_success_with_data
- test_get_executions_with_status_filter
- test_get_executions_with_browser_filter

# POST /api/v1/executions
- test_create_execution_success_201
- test_create_execution_invalid_type_422
- test_create_execution_invalid_browser_422
- test_create_execution_batch_without_case_ids

# GET /api/v1/executions/{id}
- test_get_execution_by_id_success
- test_get_execution_by_id_not_found_404

# GET /api/v1/executions/{id}/details
- test_get_execution_details_success
- test_get_execution_details_not_found_404
- test_get_execution_details_includes_step_logs

# POST /api/v1/executions/{id}/start
- test_start_execution_success_200
- test_start_execution_not_found_404
- test_start_execution_already_running

# POST /api/v1/executions/{id}/stop
- test_stop_execution_success_200
- test_stop_execution_not_found_404

# WebSocket /api/v1/ws/executions/{id}
- test_websocket_connect_and_accept
- test_websocket_receive_heartbeat
- test_websocket_disconnect
```

---

## 五、关键 Fixtures

### api_fixtures.py

```python
"""
API 测试 Fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.main import app
from app.models.case import TestCase, TestStep
from app.models.execution import Execution


@pytest.fixture
def client():
    """FastAPI 测试客户端"""
    return TestClient(app)


@pytest.fixture
async def db_session():
    """内存数据库会话（每个测试独立）"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(DeclarativeBase.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def sample_case(db_session: AsyncSession):
    """示例测试用例"""
    case = TestCase(
        name="示例测试用例",
        description="这是一个示例用例",
        priority="P1",
        tags="smoke, login"
    )
    db_session.add(case)
    await db_session.commit()
    await db_session.refresh(case)
    return case


@pytest.fixture
async def sample_case_with_steps(db_session: AsyncSession):
    """带步骤的示例用例"""
    case = TestCase(name="登录测试", priority="P0")
    db_session.add(case)
    await db_session.flush()

    step1 = TestStep(
        case_id=case.id,
        step_order=1,
        action_type="navigate",
        action_params={"url": "https://example.com"}
    )
    step2 = TestStep(
        case_id=case.id,
        step_order=2,
        action_type="input",
        element_locator="#username",
        locator_type="css",
        action_params={"text": "testuser"}
    )
    db_session.add_all([step1, step2])
    await db_session.commit()
    await db_session.refresh(case)
    return case
```

---

## 六、运行测试

### 运行所有测试
```bash
cd backend
pytest tests/ -v --tb=short
```

### 运行特定模块
```bash
# 只测试 Schemas
pytest tests/unit/test_schemas/ -v

# 只测试 Services
pytest tests/unit/test_services/ -v

# 只测试 API Routes
pytest tests/unit/test_api/ -v

# 带覆盖率报告
pytest tests/ --cov=app.schemas --cov=app.services --cov=app.api --cov-report=html
```

### 只运行 API 测试
```bash
pytest tests/unit/test_api/ tests/integration/ -v -m "not slow"
```

---

## 七、验收标准

| 验收项 | 标准 |
|-------|------|
| 测试用例通过率 | 100% |
| Schemas 覆盖率 | >= 90% |
| Services 覆盖率 | >= 85% |
| API Routes 覆盖率 | >= 85% |
| API 端点覆盖 | 100% |
| 测试执行时间 | < 60 秒 |
| 数据依赖 | 使用内存数据库，无外部依赖 |

---

## 八、预期测试数量

| 模块 | 预计测试数 |
|-----|----------|
| Schemas | 30-40 |
| Services | 40-50 |
| API Routes | 30-40 |
| Integration | 10-15 |
| **总计** | **110-145** |

---

## 九、预估工作量

| 任务 | 预估时间 |
|-----|---------|
| Schemas 测试 | 1-2 小时 |
| Services 测试 | 2-3 小时 |
| API Routes 测试 | 2-3 小时 |
| Fixtures 准备 | 0.5 小时 |
| Integration 测试 | 1-2 小时 |
| **总计** | **6-10 小时** |

---

## 十、后续优化建议

1. **性能测试** - 添加接口响应时间测试
2. **并发测试** - 验证数据库连接池和并发安全
3. **安全测试** - 验证输入校验和 SQL 注入防护
4. **API 文档验证** - 确保 Swagger 文档完整准确
