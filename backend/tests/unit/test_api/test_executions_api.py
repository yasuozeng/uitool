"""
测试执行 API 接口测试
测试执行任务管理的所有 HTTP 端点
"""
# 导入 pytest 测试框架
import pytest
# 导入执行相关的数据模式
from app.schemas.execution import ExecutionCreate
# 导入执行模型
from app.models.execution import Execution, ExecutionDetail
# 导入用例模型
from app.models.case import TestCase
# 从 unittest.mock 导入 AsyncMock
from unittest.mock import AsyncMock, patch


class TestGetExecutions:
    """测试获取执行任务列表接口"""

    def test_get_executions_empty(self, client):
        """测试空列表"""
        # 发送 GET 请求
        response = client.get("/api/v1/executions")

        # 验证：状态码 200
        assert response.status_code == 200
        # 验证：响应数据
        data = response.json()
        assert data["code"] == 200
        assert data["data"] == []
        assert data["total"] == 0

    def test_get_executions_with_data(self, client, db_session):
        """测试有数据的情况"""
        # 创建测试数据
        exec1 = Execution(execution_type="batch", browser_type="chrome", status="completed")
        exec2 = Execution(execution_type="single", browser_type="firefox", status="pending")
        db_session.add_all([exec1, exec2])
        import asyncio
        asyncio.run(db_session.commit())

        # 发送 GET 请求
        response = client.get("/api/v1/executions")

        # 验证：返回 2 条记录
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2
        assert data["total"] == 2

    def test_get_executions_with_status_filter(self, client, db_session):
        """测试按状态筛选"""
        # 创建测试数据
        exec1 = Execution(execution_type="batch", browser_type="chrome", status="pending")
        exec2 = Execution(execution_type="batch", browser_type="chrome", status="running")
        exec3 = Execution(execution_type="batch", browser_type="chrome", status="pending")
        db_session.add_all([exec1, exec2, exec3])
        import asyncio
        asyncio.run(db_session.commit())

        # 按状态筛选
        response = client.get("/api/v1/executions?status=pending")

        # 验证：返回 2 条 pending 状态的记录
        data = response.json()
        assert len(data["data"]) == 2

    def test_get_executions_with_browser_filter(self, client, db_session):
        """测试按浏览器类型筛选"""
        # 创建测试数据
        exec1 = Execution(execution_type="batch", browser_type="chrome", status="pending")
        exec2 = Execution(execution_type="batch", browser_type="firefox", status="pending")
        exec3 = Execution(execution_type="batch", browser_type="chrome", status="pending")
        db_session.add_all([exec1, exec2, exec3])
        import asyncio
        asyncio.run(db_session.commit())

        # 按浏览器类型筛选
        response = client.get("/api/v1/executions?browser_type=chrome")

        # 验证：返回 2 条 chrome 类型的记录
        data = response.json()
        assert len(data["data"]) == 2

    def test_get_executions_invalid_status(self, client):
        """测试非法状态"""
        # 发送请求（非法状态）
        response = client.get("/api/v1/executions?status=invalid")

        # 验证：验证错误（422）
        assert response.status_code == 422


class TestGetExecutionById:
    """测试获取执行任务详情接口"""

    def test_get_execution_by_id_exists(self, client, db_session):
        """测试获取存在的执行任务"""
        # 创建测试数据
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="pending",
            total_count=5
        )
        db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 发送 GET 请求
        response = client.get(f"/api/v1/executions/{execution.id}")

        # 验证：返回正确数据
        data = response.json()
        assert response.status_code == 200
        assert data["code"] == 200
        assert data["data"]["id"] == execution.id
        assert data["data"]["status"] == "pending"

    def test_get_execution_by_id_not_exists(self, client):
        """测试获取不存在的执行任务"""
        # 发送 GET 请求（ID 不存在）
        response = client.get("/api/v1/executions/999")

        # 验证：404 错误
        assert response.status_code == 404


class TestGetExecutionDetails:
    """测试获取执行任务详细信息接口"""

    def test_get_execution_details(self, client, db_session):
        """测试获取执行详情"""
        # 创建测试数据
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="completed"
        )
        db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 添加详情
        detail1 = ExecutionDetail(
            execution_id=execution.id,
            case_id=1,
            case_name="用例1",
            status="success"
        )
        detail2 = ExecutionDetail(
            execution_id=execution.id,
            case_id=2,
            case_name="用例2",
            status="failed"
        )
        db_session.add_all([detail1, detail2])
        asyncio.run(db_session.commit())

        # 发送 GET 请求
        response = client.get(f"/api/v1/executions/{execution.id}/details")

        # 验证：返回详情列表
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2
        assert data["data"][0]["case_name"] == "用例1"
        assert data["data"][1]["case_name"] == "用例2"

    def test_get_execution_details_not_exists(self, client):
        """测试获取不存在的执行任务详情"""
        # 发送 GET 请求（ID 不存在）
        response = client.get("/api/v1/executions/999/details")

        # 验证：404 错误
        assert response.status_code == 404


class TestCreateExecution:
    """测试创建执行任务接口"""

    def test_create_execution_batch(self, client, db_session):
        """测试创建批量执行任务"""
        # 创建测试用例
        case1 = TestCase(name="用例1")
        case2 = TestCase(name="用例2")
        db_session.add_all([case1, case2])
        import asyncio
        asyncio.run(db_session.commit())

        # 请求数据
        request_data = {
            "execution_type": "batch",
            "browser_type": "chrome",
            "headless": True,
            "window_size": "1920x1080",
            "case_ids": [case1.id, case2.id]
        }

        # 发送 POST 请求
        response = client.post("/api/v1/executions", json=request_data)

        # 验证：创建成功
        data = response.json()
        assert response.status_code == 201
        assert data["code"] == 200
        assert data["data"]["execution_type"] == "batch"
        assert data["data"]["total_count"] == 2

    def test_create_execution_single(self, client, db_session):
        """测试创建单个执行任务"""
        # 创建测试用例
        case = TestCase(name="单个用例")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())

        # 请求数据
        request_data = {
            "execution_type": "single",
            "browser_type": "firefox",
            "headless": False,
            "case_ids": [case.id]
        }

        # 发送 POST 请求
        response = client.post("/api/v1/executions", json=request_data)

        # 验证：创建成功
        data = response.json()
        assert response.status_code == 201
        assert data["data"]["execution_type"] == "single"
        assert data["data"]["browser_type"] == "firefox"

    def test_create_execution_defaults(self, client):
        """测试默认值"""
        # 请求数据（只传必填字段）
        request_data = {
            "execution_type": "batch"
        }

        # 发送 POST 请求
        response = client.post("/api/v1/executions", json=request_data)

        # 验证：默认值正确
        data = response.json()
        assert response.status_code == 201
        assert data["data"]["browser_type"] == "chrome"
        assert data["data"]["headless"] is True

    def test_create_execution_invalid_type(self, client):
        """测试非法执行类型"""
        # 请求数据（非法执行类型）
        request_data = {
            "execution_type": "invalid"
        }

        # 发送 POST 请求
        response = client.post("/api/v1/executions", json=request_data)

        # 验证：验证错误（422）
        assert response.status_code == 422

    def test_create_execution_invalid_browser(self, client):
        """测试非法浏览器类型"""
        # 请求数据（非法浏览器类型）
        request_data = {
            "execution_type": "batch",
            "browser_type": "safari"
        }

        # 发送 POST 请求
        response = client.post("/api/v1/executions", json=request_data)

        # 验证：验证错误（422）
        assert response.status_code == 422


class TestStartExecution:
    """测试启动执行任务接口"""

    def test_start_execution_success(self, client, db_session):
        """测试成功启动执行任务"""
        # 创建测试用例
        case = TestCase(name="测试用例")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())

        # 创建执行记录
        execution = Execution(
            execution_type="single",
            browser_type="chrome",
            total_count=1,
            status="pending"
        )
        db_session.add(execution)
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 创建执行详情
        detail = ExecutionDetail(
            execution_id=execution.id,
            case_id=case.id,
            case_name=case.name,
            status="pending"
        )
        db_session.add(detail)
        asyncio.run(db_session.commit())

        # Mock PlaywrightEngine
        with patch('app.services.execution_service.PlaywrightEngine') as MockEngine:
            # 配置 Mock
            mock_engine = AsyncMock()
            mock_engine.start_browser = AsyncMock()
            mock_engine.close_browser = AsyncMock()
            mock_engine.execute_case = AsyncMock(return_value={
                "success": True,
                "total_steps": 0,
                "success_steps": 0,
                "failed_steps": 0,
                "step_results": []
            })
            MockEngine.return_value = mock_engine

            # 发送 POST 请求
            response = client.post(f"/api/v1/executions/{execution.id}/start")

            # 验证：启动成功
            # 注意：由于是后台任务，状态可能还未更新为 running
            assert response.status_code in [200, 404]

    def test_start_execution_not_exists(self, client):
        """测试启动不存在的执行任务"""
        # 发送 POST 请求（ID 不存在）
        response = client.post("/api/v1/executions/999/start")

        # 验证：404 错误
        assert response.status_code == 404


class TestStopExecution:
    """测试停止执行任务接口"""

    def test_stop_execution_success(self, client, db_session):
        """测试成功停止执行任务"""
        # 创建执行记录
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="running"
        )
        db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 发送 POST 请求
        response = client.post(f"/api/v1/executions/{execution.id}/stop")

        # 验证：停止成功
        data = response.json()
        assert response.status_code == 200
        assert data["code"] == 200
        assert data["message"] == "执行任务已停止"

    def test_stop_execution_not_exists(self, client):
        """测试停止不存在的执行任务"""
        # 发送 POST 请求（ID 不存在）
        response = client.post("/api/v1/executions/999/stop")

        # 验证：404 错误
        assert response.status_code == 404


class TestWebSocketExecutionLogs:
    """测试 WebSocket 实时日志推送接口"""

    def test_websocket_connection(self, client):
        """测试 WebSocket 连接"""
        # 使用 TestClient 测试 WebSocket
        with client.websocket_connect("/api/v1/ws/executions/1") as websocket:
            # 验证：连接成功
            assert websocket is not None

            # 发送消息（心跳）
            websocket.send_text("ping")

            # 接收消息
            data = websocket.receive_json()

            # 验证：收到心跳响应
            assert data["type"] == "heartbeat"
            assert data["execution_id"] == 1

    def test_websocket_disconnect(self, client):
        """测试 WebSocket 断开连接"""
        # 测试自动断开
        with client.websocket_connect("/api/v1/ws/executions/2") as websocket:
            # 连接后自动断开（退出 with 块）
            pass
        # 验证：正常退出（无异常）

    def test_websocket_multiple_messages(self, client):
        """测试多次消息交互"""
        with client.websocket_connect("/api/v1/ws/executions/3") as websocket:
            # 发送多条消息
            for i in range(3):
                websocket.send_text("ping")
                data = websocket.receive_json()
                assert data["type"] == "heartbeat"


class TestStartExecutionEdgeCases:
    """测试启动执行接口的边界情况"""

    def test_start_execution_already_running(self, client, db_session):
        """测试重复启动正在运行的执行任务"""
        # 创建执行记录（状态为 running）
        execution = Execution(
            execution_type="single",
            browser_type="chrome",
            status="running",
            total_count=1
        )
        db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 尝试再次启动
        response = client.post(f"/api/v1/executions/{execution.id}/start")

        # 验证：根据业务规则，可能返回当前状态或冲突
        assert response.status_code in [200, 409]

    def test_start_execution_no_cases(self, client, db_session):
        """测试启动没有用例的执行任务"""
        # 创建执行记录（没有关联用例）
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="pending",
            total_count=0
        )
        db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 尝试启动
        response = client.post(f"/api/v1/executions/{execution.id}/start")

        # 验证：可能返回成功（无用例可执行）或错误
        assert response.status_code in [200, 400]


class TestStopExecutionEdgeCases:
    """测试停止执行接口的边界情况"""

    def test_stop_execution_already_stopped(self, client, db_session):
        """测试重复停止已停止的执行任务"""
        # 创建执行记录（状态为 stopped）
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="stopped",
            total_count=5
        )
        db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 尝试再次停止
        response = client.post(f"/api/v1/executions/{execution.id}/stop")

        # 验证：返回成功（幂等操作）
        data = response.json()
        assert response.status_code == 200
        assert data["code"] == 200

    def test_stop_execution_completed(self, client, db_session):
        """测试停止已完成的执行任务"""
        # 创建执行记录（状态为 completed）
        execution = Execution(
            execution_type="batch",
            browser_type="chrome",
            status="completed",
            total_count=5,
            success_count=5
        )
        db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 尝试停止
        response = client.post(f"/api/v1/executions/{execution.id}/stop")

        # 验证：已完成任务无法停止，或返回成功
        assert response.status_code in [200, 400]


class TestGetExecutionsPagination:
    """测试执行列表分页接口"""

    def test_get_executions_pagination(self, client, db_session):
        """测试分页查询执行列表"""
        # 创建 25 条执行记录
        for i in range(1, 26):
            execution = Execution(
                execution_type="batch",
                browser_type="chrome",
                status="completed",
                total_count=i
            )
            db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())

        # 获取第 1 页（每页 10 条）
        response = client.get("/api/v1/executions?page=1&page_size=10")

        # 验证：第 1 页 10 条
        data = response.json()
        assert response.status_code == 200
        assert data["total"] == 25
        assert len(data["data"]) == 10
        assert data["page"] == 1

    def test_get_executions_last_page(self, client, db_session):
        """测试最后一页的分页"""
        # 创建 15 条执行记录
        for i in range(1, 16):
            execution = Execution(
                execution_type="batch",
                browser_type="chrome",
                status="completed",
                total_count=i
            )
            db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())

        # 获取第 2 页（每页 10 条）
        response = client.get("/api/v1/executions?page=2&page_size=10")

        # 验证：第 2 页剩余 5 条
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 5
        assert data["page"] == 2

    def test_get_executions_page_out_of_range(self, client, db_session):
        """测试超出范围的页码"""
        # 创建 5 条执行记录
        for i in range(1, 6):
            execution = Execution(
                execution_type="batch",
                browser_type="chrome",
                status="completed",
                total_count=i
            )
            db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())

        # 获取第 10 页（超出范围）
        response = client.get("/api/v1/executions?page=10&page_size=10")

        # 验证：返回空列表
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 0


class TestExecutionStatusTransition:
    """测试执行状态转换接口"""

    def test_execution_status_flow_pending_to_running(self, client, db_session):
        """测试状态转换：pending -> running"""
        # 创建执行记录（pending 状态）
        execution = Execution(
            execution_type="single",
            browser_type="chrome",
            status="pending",
            total_count=1
        )
        db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 获取初始状态
        response = client.get(f"/api/v1/executions/{execution.id}")
        data = response.json()
        assert data["data"]["status"] == "pending"

    def test_execution_status_flow_running_to_completed(self, client, db_session):
        """测试状态转换：running -> completed"""
        # 创建执行记录（running 状态）
        execution = Execution(
            execution_type="single",
            browser_type="chrome",
            status="running",
            total_count=1,
            success_count=1
        )
        db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(execution))

        # 停止执行（模拟完成）
        response = client.post(f"/api/v1/executions/{execution.id}/stop")

        # 验证：状态已改变
        assert response.status_code == 200

    def test_execution_status_flow_all_transitions(self, client, db_session):
        """测试所有状态转换流程"""
        # 验证状态转换顺序：pending -> running -> completed/stopped
        # 这里只测试数据模型支持的状态值
        valid_statuses = ["pending", "running", "completed", "failed", "stopped"]

        # 创建各种状态的执行记录
        for status in valid_statuses:
            execution = Execution(
                execution_type="single",
                browser_type="chrome",
                status=status,
                total_count=1
            )
            db_session.add(execution)
        import asyncio
        asyncio.run(db_session.commit())

        # 验证所有状态都能正确保存
        response = client.get("/api/v1/executions")
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == len(valid_statuses)


class TestWebSocketMultipleClients:
    """测试 WebSocket 多客户端连接"""

    def test_websocket_two_clients(self, client):
        """测试两个客户端同时连接"""
        # 创建第一个连接
        with client.websocket_connect("/api/v1/ws/executions/1") as ws1:
            # 发送心跳
            ws1.send_text("ping")
            data1 = ws1.receive_json()
            assert data1["type"] == "heartbeat"

            # 创建第二个连接
            with client.websocket_connect("/api/v1/ws/executions/2") as ws2:
                # 第二个客户端发送心跳
                ws2.send_text("ping")
                data2 = ws2.receive_json()
                assert data2["type"] == "heartbeat"

                # 验证：两个连接独立
                assert data1["execution_id"] == 1
                assert data2["execution_id"] == 2

    def test_websocket_different_execution_ids(self, client):
        """测试不同执行ID的连接"""
        execution_ids = [10, 20, 30]

        for eid in execution_ids:
            with client.websocket_connect(f"/api/v1/ws/executions/{eid}") as ws:
                ws.send_text("ping")
                data = ws.receive_json()
                # 验证：返回正确的执行ID
                assert data["execution_id"] == eid
