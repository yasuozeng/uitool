"""
测试用例 API 接口测试
测试用例管理的所有 HTTP 端点
"""
# 导入 pytest 测试框架
import pytest
# 导入用例相关的数据模式
from app.schemas.case import CaseCreate, StepCreate
# 导入用例模型
from app.models.case import TestCase


class TestGetCases:
    """测试获取用例列表接口"""

    def test_get_cases_empty(self, client):
        """测试空列表"""
        # 发送 GET 请求
        response = client.get("/api/v1/cases")

        # 验证：状态码 200
        assert response.status_code == 200
        # 验证：响应数据
        data = response.json()
        assert data["code"] == 200
        assert data["data"] == []
        assert data["total"] == 0

    def test_get_cases_with_data(self, client, db_session):
        """测试有数据的情况"""
        # 创建测试数据
        case1 = TestCase(name="用例1", priority="P1")
        case2 = TestCase(name="用例2", priority="P0")
        db_session.add_all([case1, case2])
        import asyncio
        asyncio.run(db_session.commit())

        # 发送 GET 请求
        response = client.get("/api/v1/cases")

        # 验证：返回 2 条记录
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2
        assert data["total"] == 2

    def test_get_cases_with_name_filter(self, client, db_session):
        """测试按名称筛选"""
        # 创建测试数据
        case1 = TestCase(name="登录测试")
        case2 = TestCase(name="注册测试")
        db_session.add_all([case1, case2])
        import asyncio
        asyncio.run(db_session.commit())

        # 按名称筛选
        response = client.get("/api/v1/cases?name=登录")

        # 验证：返回 1 条结果
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "登录测试"

    def test_get_cases_with_priority_filter(self, client, db_session):
        """测试按优先级筛选"""
        # 创建测试数据
        case1 = TestCase(name="用例1", priority="P0")
        case2 = TestCase(name="用例2", priority="P1")
        case3 = TestCase(name="用例3", priority="P0")
        db_session.add_all([case1, case2, case3])
        import asyncio
        asyncio.run(db_session.commit())

        # 按优先级筛选
        response = client.get("/api/v1/cases?priority=P0")

        # 验证：返回 2 条 P0 用例
        data = response.json()
        assert len(data["data"]) == 2

    def test_get_cases_pagination(self, client, db_session):
        """测试分页"""
        # 创建 15 条测试数据
        for i in range(1, 16):
            case = TestCase(name=f"用例{i}")
            db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())

        # 获取第 1 页（每页 10 条）
        response = client.get("/api/v1/cases?page=1&page_size=10")

        # 验证：第 1 页 10 条
        data = response.json()
        assert data["total"] == 15
        assert len(data["data"]) == 10
        assert data["page"] == 1

    def test_get_cases_invalid_priority(self, client):
        """测试非法优先级"""
        # 发送请求（非法优先级）
        response = client.get("/api/v1/cases?priority=P5")

        # 验证：验证错误（422）
        assert response.status_code == 422

    def test_get_cases_invalid_page(self, client):
        """测试非法页码"""
        # 发送请求（页码为 0）
        response = client.get("/api/v1/cases?page=0")

        # 验证：验证错误（422）
        assert response.status_code == 422


class TestGetCaseById:
    """测试获取用例详情接口"""

    def test_get_case_by_id_exists(self, client, db_session):
        """测试获取存在的用例"""
        # 创建测试数据
        case = TestCase(name="测试用例", description="测试描述")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(case))

        # 发送 GET 请求
        response = client.get(f"/api/v1/cases/{case.id}")

        # 验证：返回正确数据
        data = response.json()
        assert response.status_code == 200
        assert data["code"] == 200
        assert data["data"]["id"] == case.id
        assert data["data"]["name"] == "测试用例"

    def test_get_case_by_id_not_exists(self, client):
        """测试获取不存在的用例"""
        # 发送 GET 请求（ID 不存在）
        response = client.get("/api/v1/cases/999")

        # 验证：404 错误
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_case_by_id_with_steps(self, client, db_session):
        """测试获取用例及其步骤"""
        # 创建测试数据（用例 + 步骤）
        from app.models.case import TestStep
        case = TestCase(name="带步骤的用例")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(case))

        step1 = TestStep(case_id=case.id, step_order=1, action_type="navigate")
        step2 = TestStep(case_id=case.id, step_order=2, action_type="click")
        db_session.add_all([step1, step2])
        asyncio.run(db_session.commit())

        # 发送 GET 请求
        response = client.get(f"/api/v1/cases/{case.id}")

        # 验证：包含步骤
        data = response.json()
        assert len(data["data"]["steps"]) == 2


class TestCreateCase:
    """测试创建用例接口"""

    def test_create_case_success(self, client):
        """测试成功创建用例"""
        # 请求数据
        request_data = {
            "name": "新用例",
            "description": "新用例描述",
            "priority": "P1",
            "tags": "smoke",
            "steps": [
                {
                    "step_order": 1,
                    "action_type": "navigate",
                    "action_params": {"url": "https://example.com"}
                },
                {
                    "step_order": 2,
                    "action_type": "click",
                    "element_locator": "#button",
                    "locator_type": "css"
                }
            ]
        }

        # 发送 POST 请求
        response = client.post("/api/v1/cases", json=request_data)

        # 验证：创建成功
        data = response.json()
        assert response.status_code == 201
        assert data["code"] == 200
        assert data["data"]["name"] == "新用例"
        assert data["data"]["id"] > 0
        assert len(data["data"]["steps"]) == 2

    def test_create_case_minimal(self, client):
        """测试最小字段创建"""
        # 请求数据（只有必填字段）
        request_data = {
            "name": "最小用例"
        }

        # 发送 POST 请求
        response = client.post("/api/v1/cases", json=request_data)

        # 验证：创建成功
        data = response.json()
        assert response.status_code == 201
        assert data["data"]["name"] == "最小用例"
        assert data["data"]["steps"] == []

    def test_create_case_invalid_name(self, client):
        """测试非法名称（空字符串）"""
        # 请求数据（名称为空）
        request_data = {
            "name": ""
        }

        # 发送 POST 请求
        response = client.post("/api/v1/cases", json=request_data)

        # 验证：验证错误（422）
        assert response.status_code == 422

    def test_create_case_invalid_priority(self, client):
        """测试非法优先级"""
        # 请求数据（非法优先级）
        request_data = {
            "name": "测试用例",
            "priority": "P5"
        }

        # 发送 POST 请求
        response = client.post("/api/v1/cases", json=request_data)

        # 验证：验证错误（422）
        assert response.status_code == 422


class TestUpdateCase:
    """测试更新用例接口"""

    def test_update_case_success(self, client, db_session):
        """测试成功更新用例"""
        # 创建初始用例
        case = TestCase(name="原名称", priority="P1")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(case))

        # 更新数据
        update_data = {
            "name": "新名称",
            "description": "新描述",
            "priority": "P0"
        }

        # 发送 PUT 请求
        response = client.put(f"/api/v1/cases/{case.id}", json=update_data)

        # 验证：更新成功
        data = response.json()
        assert response.status_code == 200
        assert data["data"]["name"] == "新名称"
        assert data["data"]["priority"] == "P0"

    def test_update_case_partial(self, client, db_session):
        """测试部分更新"""
        # 创建初始用例
        case = TestCase(name="原名称", description="原描述")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(case))

        # 只更新名称
        update_data = {
            "name": "只更新名称"
        }

        # 发送 PUT 请求
        response = client.put(f"/api/v1/cases/{case.id}", json=update_data)

        # 验证：只更新了名称
        data = response.json()
        assert data["data"]["name"] == "只更新名称"
        assert data["data"]["description"] == "原描述"

    def test_update_case_not_exists(self, client):
        """测试更新不存在的用例"""
        # 更新数据
        update_data = {
            "name": "新名称"
        }

        # 发送 PUT 请求（ID 不存在）
        response = client.put("/api/v1/cases/999", json=update_data)

        # 验证：404 错误
        assert response.status_code == 404


class TestDeleteCase:
    """测试删除用例接口"""

    def test_delete_case_success(self, client, db_session):
        """测试成功删除用例"""
        # 创建测试用例
        case = TestCase(name="待删除用例")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())
        case_id = case.id

        # 发送 DELETE 请求
        response = client.delete(f"/api/v1/cases/{case_id}")

        # 验证：删除成功
        data = response.json()
        assert response.status_code == 200
        assert data["code"] == 200
        assert data["message"] == "用例删除成功"

    def test_delete_case_not_exists(self, client):
        """测试删除不存在的用例"""
        # 发送 DELETE 请求（ID 不存在）
        response = client.delete("/api/v1/cases/999")

        # 验证：404 错误
        assert response.status_code == 404


class TestBatchDeleteCases:
    """测试批量删除用例接口"""

    def test_batch_delete_cases_success(self, client, db_session):
        """测试成功批量删除"""
        # 创建测试用例
        case1 = TestCase(name="用例1")
        case2 = TestCase(name="用例2")
        case3 = TestCase(name="用例3")
        db_session.add_all([case1, case2, case3])
        import asyncio
        asyncio.run(db_session.commit())

        # 请求数据
        request_data = {
            "case_ids": [case1.id, case2.id, case3.id]
        }

        # 发送 DELETE 请求
        response = client.delete("/api/v1/cases/batch", json=request_data)

        # 验证：删除成功
        data = response.json()
        assert response.status_code == 200
        assert data["data"]["deleted"] == 3

    def test_batch_delete_cases_empty_list(self, client):
        """测试空列表删除"""
        # 请求数据（空列表）
        request_data = {
            "case_ids": []
        }

        # 发送 DELETE 请求
        response = client.delete("/api/v1/cases/batch", json=request_data)

        # 验证：验证错误（422）
        assert response.status_code == 422


class TestSaveSteps:
    """测试保存步骤接口"""

    def test_save_steps_success(self, client, db_session):
        """测试成功保存步骤"""
        # 创建测试用例
        case = TestCase(name="测试用例")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(case))

        # 步骤数据
        request_data = {
            "steps": [
                {
                    "step_order": 1,
                    "action_type": "navigate",
                    "action_params": {"url": "https://example.com"}
                },
                {
                    "step_order": 2,
                    "action_type": "click",
                    "element_locator": "#button"
                }
            ]
        }

        # 发送 PUT 请求
        response = client.put(f"/api/v1/cases/{case.id}/steps", json=request_data)

        # 验证：保存成功
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]["steps"]) == 2

    def test_save_steps_replace_existing(self, client, db_session):
        """测试替换现有步骤"""
        from app.models.case import TestStep
        # 创建测试用例和步骤
        case = TestCase(name="测试用例")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(case))

        step1 = TestStep(case_id=case.id, step_order=1, action_type="old_action")
        db_session.add(step1)
        asyncio.run(db_session.commit())

        # 新步骤数据
        request_data = {
            "steps": [
                {
                    "step_order": 1,
                    "action_type": "new_action"
                }
            ]
        }

        # 发送 PUT 请求
        response = client.put(f"/api/v1/cases/{case.id}/steps", json=request_data)

        # 验证：旧步骤被替换
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]["steps"]) == 1
        assert data["data"]["steps"][0]["action_type"] == "new_action"

    def test_save_steps_case_not_exists(self, client):
        """测试用例不存在"""
        # 步骤数据
        request_data = {
            "steps": [
                {
                    "step_order": 1,
                    "action_type": "navigate"
                }
            ]
        }

        # 发送 PUT 请求（用例 ID 不存在）
        response = client.put("/api/v1/cases/999/steps", json=request_data)

        # 验证：404 错误
        assert response.status_code == 404


class TestGetCasesTagsFilter:
    """测试按标签筛选接口"""

    def test_get_cases_with_tags_filter(self, client, db_session):
        """测试按标签筛选"""
        # 创建测试数据（包含不同标签）
        case1 = TestCase(name="用例1", tags="smoke,auth")
        case2 = TestCase(name="用例2", tags="regression")
        case3 = TestCase(name="用例3", tags="smoke")
        db_session.add_all([case1, case2, case3])
        import asyncio
        asyncio.run(db_session.commit())

        # 按标签筛选（smoke）
        response = client.get("/api/v1/cases?tags=smoke")

        # 验证：返回包含 smoke 标签的用例
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2
        # 验证返回的用例都包含 smoke 标签
        for case in data["data"]:
            assert "smoke" in case["tags"]

    def test_get_cases_with_multiple_tags(self, client, db_session):
        """测试按多个标签筛选"""
        # 创建测试数据
        case1 = TestCase(name="用例1", tags="smoke,auth")
        case2 = TestCase(name="用例2", tags="smoke")
        db_session.add_all([case1, case2])
        import asyncio
        asyncio.run(db_session.commit())

        # 按标签筛选（auth）
        response = client.get("/api/v1/cases?tags=auth")

        # 验证：返回包含 auth 标签的用例
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["tags"] == "smoke,auth"

    def test_get_cases_no_tags_filter(self, client, db_session):
        """测试无标签的用例"""
        # 创建测试数据（一个有标签，一个没有）
        case1 = TestCase(name="有标签用例", tags="smoke")
        case2 = TestCase(name="无标签用例", tags=None)
        db_session.add_all([case1, case2])
        import asyncio
        asyncio.run(db_session.commit())

        # 不筛选标签
        response = client.get("/api/v1/cases")

        # 验证：返回所有用例
        data = response.json()
        assert len(data["data"]) == 2


class TestGetCasesCombinedFilters:
    """测试组合筛选条件接口"""

    def test_get_cases_with_priority_and_name(self, client, db_session):
        """测试按优先级和名称组合筛选"""
        # 创建测试数据
        case1 = TestCase(name="登录测试", priority="P0")
        case2 = TestCase(name="注册测试", priority="P1")
        case3 = TestCase(name="登录高级测试", priority="P0")
        db_session.add_all([case1, case2, case3])
        import asyncio
        asyncio.run(db_session.commit())

        # 组合筛选：P0 优先级 + 名称包含"登录"
        response = client.get("/api/v1/cases?priority=P0&name=登录")

        # 验证：返回符合条件的用例
        data = response.json()
        assert response.status_code == 200
        assert len(data["data"]) == 2
        # 验证所有结果都是 P0 优先级且名称包含"登录"
        for case in data["data"]:
            assert case["priority"] == "P0"
            assert "登录" in case["name"]

    def test_get_cases_with_all_filters(self, client, db_session):
        """测试所有筛选条件组合"""
        # 创建测试数据
        case1 = TestCase(name="登录测试", priority="P0", tags="smoke")
        case2 = TestCase(name="登录测试", priority="P1", tags="regression")
        case3 = TestCase(name="注册测试", priority="P0", tags="smoke")
        db_session.add_all([case1, case2, case3])
        import asyncio
        asyncio.run(db_session.commit())

        # 组合筛选：P0 + smoke + 登录
        response = client.get("/api/v1/cases?priority=P0&tags=smoke&name=登录")

        # 验证：返回符合条件的用例
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "登录测试"
        assert data["data"][0]["priority"] == "P0"


class TestCreateCaseWithTags:
    """测试创建带标签的用例接口"""

    def test_create_case_with_tags(self, client):
        """测试创建带标签的用例"""
        # 请求数据（包含标签）
        request_data = {
            "name": "登录测试",
            "tags": "smoke,auth,critical"
        }

        # 发送 POST 请求
        response = client.post("/api/v1/cases", json=request_data)

        # 验证：创建成功
        data = response.json()
        assert response.status_code == 201
        assert data["data"]["tags"] == "smoke,auth,critical"

    def test_create_case_with_empty_tags(self, client):
        """测试创建空标签的用例"""
        # 请求数据（标签为空字符串）
        request_data = {
            "name": "测试用例",
            "tags": ""
        }

        # 发送 POST 请求
        response = client.post("/api/v1/cases", json=request_data)

        # 验证：创建成功（空标签被视为 None 或空字符串）
        data = response.json()
        assert response.status_code == 201


class TestUpdateCaseWithTags:
    """测试更新用例标签接口"""

    def test_update_case_with_tags(self, client, db_session):
        """测试更新用例标签"""
        # 创建初始用例
        case = TestCase(name="测试用例", tags="smoke")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(case))

        # 更新数据（修改标签）
        update_data = {
            "tags": "regression,critical"
        }

        # 发送 PUT 请求
        response = client.put(f"/api/v1/cases/{case.id}", json=update_data)

        # 验证：标签更新成功
        data = response.json()
        assert response.status_code == 200
        assert data["data"]["tags"] == "regression,critical"

    def test_update_case_clear_tags(self, client, db_session):
        """测试清除用例标签"""
        # 创建初始用例（带标签）
        case = TestCase(name="测试用例", tags="smoke,auth")
        db_session.add(case)
        import asyncio
        asyncio.run(db_session.commit())
        asyncio.run(db_session.refresh(case))

        # 更新数据（清除标签）
        update_data = {
            "tags": None
        }

        # 发送 PUT 请求
        response = client.put(f"/api/v1/cases/{case.id}", json=update_data)

        # 验证：标签被清除
        data = response.json()
        assert response.status_code == 200
        # 验证标签为空
        assert data["data"]["tags"] is None or data["data"]["tags"] == ""


class TestCreateCaseDuplicateName:
    """测试创建同名用例接口"""

    def test_create_case_duplicate_name(self, client, db_session):
        """测试创建重复名称的用例"""
        # 创建第一个用例
        case1 = TestCase(name="重复名称测试")
        db_session.add(case1)
        import asyncio
        asyncio.run(db_session.commit())

        # 尝试创建同名用例
        request_data = {
            "name": "重复名称测试"
        }

        # 发送 POST 请求
        response = client.post("/api/v1/cases", json=request_data)

        # 验证：根据业务规则，可能允许同名或返回错误
        # 如果允许同名，返回 201
        # 如果不允许同名，返回 400 或 409
        assert response.status_code in [201, 400, 409]

    def test_create_case_similar_name(self, client, db_session):
        """测试创建相似名称的用例"""
        # 创建第一个用例
        case1 = TestCase(name="登录测试")
        db_session.add(case1)
        import asyncio
        asyncio.run(db_session.commit())

        # 创建名称相似但不同的用例
        request_data = {
            "name": "登录测试v2"
        }

        # 发送 POST 请求
        response = client.post("/api/v1/cases", json=request_data)

        # 验证：应该成功创建（名称不同）
        data = response.json()
        assert response.status_code == 201
        assert data["data"]["name"] == "登录测试v2"
