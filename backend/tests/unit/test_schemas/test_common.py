"""
通用响应模式测试
测试 ApiResponse、PaginatedResponse 和 ErrorResponse
"""
# 导入 pytest 测试框架
import pytest
# 导入通用响应模式
from app.schemas.common import ApiResponse, PaginatedResponse, ErrorResponse


class TestApiResponse:
    """测试 ApiResponse 通用响应模式"""

    def test_api_response_default_values(self):
        """测试默认值"""
        # 创建响应对象（使用默认值）
        response = ApiResponse()

        # 验证：状态码默认为 200
        assert response.code == 200
        # 验证：消息默认为 "success"
        assert response.message == "success"
        # 验证：数据默认为 None
        assert response.data is None

    def test_api_response_with_data(self):
        """测试带数据的响应"""
        # 定义测试数据
        test_data = {"name": "测试用例", "id": 1}
        # 创建响应对象（传入数据）
        response = ApiResponse(data=test_data)

        # 验证：状态码为默认值 200
        assert response.code == 200
        # 验证：数据与输入一致
        assert response.data == test_data
        # 验证：data["name"] 为 "测试用例"
        assert response.data["name"] == "测试用例"

    def test_api_response_custom_message(self):
        """测试自定义消息"""
        # 创建响应对象（自定义消息）
        response = ApiResponse(message="创建成功")

        # 验证：消息与输入一致
        assert response.message == "创建成功"

    def test_api_response_custom_code(self):
        """测试自定义状态码"""
        # 创建响应对象（自定义状态码）
        response = ApiResponse(code=201)

        # 验证：状态码与输入一致
        assert response.code == 201

    def test_api_response_all_fields(self):
        """测试所有字段"""
        # 定义完整数据
        test_data = {"items": [1, 2, 3]}
        # 创建响应对象（传入所有字段）
        response = ApiResponse(code=200, message="操作成功", data=test_data)

        # 验证：所有字段与输入一致
        assert response.code == 200
        assert response.message == "操作成功"
        assert response.data == test_data

    def test_api_response_serialization(self):
        """测试 JSON 序列化"""
        # 定义测试数据
        test_data = {"id": 1, "name": "测试"}
        # 创建响应对象
        response = ApiResponse(data=test_data, message="成功")

        # 转换为字典
        result = response.model_dump()

        # 验证：序列化后的字典包含所有字段
        assert result["code"] == 200
        assert result["message"] == "成功"
        assert result["data"] == test_data

    def test_api_response_with_none_data(self):
        """测试 data 为 None"""
        # 创建响应对象（data 显式传入 None）
        response = ApiResponse(data=None)

        # 验证：data 为 None
        assert response.data is None

    def test_api_response_with_complex_data(self):
        """测试复杂数据结构"""
        # 定义复杂数据（嵌套字典和列表）
        test_data = {
            "user": {"id": 1, "name": "张三"},
            "items": [1, 2, 3, 4],
            "meta": {"total": 100, "page": 1}
        }
        # 创建响应对象
        response = ApiResponse(data=test_data)

        # 验证：复杂数据正确存储
        assert response.data["user"]["name"] == "张三"
        assert response.data["items"][0] == 1
        assert response.data["meta"]["total"] == 100


class TestPaginatedResponse:
    """测试 PaginatedResponse 分页响应模式"""

    def test_paginated_response_default_values(self):
        """测试默认值"""
        # 创建分页响应对象（使用默认值）
        response = PaginatedResponse()

        # 验证：所有默认值正确
        assert response.code == 200
        assert response.message == "success"
        assert response.data == []
        assert response.total == 0
        assert response.page == 1
        assert response.page_size == 20
        assert response.pages == 0

    def test_paginated_response_with_data(self):
        """测试带数据的分页响应"""
        # 定义测试数据列表
        test_data = [
            {"id": 1, "name": "用例1"},
            {"id": 2, "name": "用例2"},
            {"id": 3, "name": "用例3"}
        ]
        # 创建分页响应对象
        response = PaginatedResponse(
            data=test_data,
            total=3,
            page=1,
            page_size=10
        )

        # 验证：数据长度为 3
        assert len(response.data) == 3
        # 验证：总数为 3
        assert response.total == 3
        # 验证：当前页为 1
        assert response.page == 1
        # 验证：每页大小为 10
        assert response.page_size == 10
        # 验证：总页数为 1（3 条记录，每页 10 条，共 1 页）
        assert response.pages == 1

    def test_paginated_response_pages_calculation(self):
        """测试总页数计算"""
        # 创建分页响应对象（100 条记录，每页 20 条）
        response = PaginatedResponse(
            data=[],
            total=100,
            page=1,
            page_size=20
        )

        # 验证：总页数为 5（100 / 20 = 5）
        assert response.pages == 5

    def test_paginated_response_partial_page(self):
        """测试不满一页的情况"""
        # 创建分页响应对象（25 条记录，每页 10 条）
        response = PaginatedResponse(
            data=[],
            total=25,
            page=1,
            page_size=10
        )

        # 验证：总页数为 3（25 / 10 = 2.5，向上取整为 3）
        assert response.pages == 3

    def test_paginated_response_empty(self):
        """测试空数据"""
        # 创建空的分页响应对象
        response = PaginatedResponse(
            data=[],
            total=0,
            page=1,
            page_size=20
        )

        # 验证：数据列表为空
        assert response.data == []
        # 验证：总数为 0
        assert response.total == 0
        # 验证：总页数为 0
        assert response.pages == 0

    def test_paginated_response_second_page(self):
        """测试第二页"""
        # 定义第二页的数据
        test_data = [{"id": 21}, {"id": 22}]
        # 创建分页响应对象（第 2 页）
        response = PaginatedResponse(
            data=test_data,
            total=50,
            page=2,
            page_size=20
        )

        # 验证：当前页为 2
        assert response.page == 2
        # 验证：总页数为 3（50 / 20 = 2.5，向上取整为 3）
        assert response.pages == 3
        # 验证：数据长度为 2
        assert len(response.data) == 2

    def test_paginated_response_serialization(self):
        """测试 JSON 序列化"""
        # 定义测试数据
        test_data = [{"id": 1}]
        # 创建分页响应对象
        response = PaginatedResponse(
            data=test_data,
            total=100,
            page=5,
            page_size=20
        )

        # 转换为字典
        result = response.model_dump()

        # 验证：序列化后的字典包含所有分页信息
        assert result["code"] == 200
        assert result["message"] == "success"
        assert result["data"] == test_data
        assert result["total"] == 100
        assert result["page"] == 5
        assert result["page_size"] == 20
        assert result["pages"] == 5


class TestErrorResponse:
    """测试 ErrorResponse 错误响应模式"""

    def test_error_response_required_fields(self):
        """测试必填字段"""
        # 创建错误响应对象（必填字段 code 和 message）
        response = ErrorResponse(code=404, message="资源未找到")

        # 验证：必填字段正确设置
        assert response.code == 404
        assert response.message == "资源未找到"

    def test_error_response_with_error_detail(self):
        """测试带详细错误信息"""
        # 创建错误响应对象（包含详细错误）
        response = ErrorResponse(
            code=400,
            message="请求参数错误",
            error="name 字段不能为空"
        )

        # 验证：详细错误信息正确设置
        assert response.error == "name 字段不能为空"

    def test_error_response_with_path(self):
        """测试带请求路径"""
        # 创建错误响应对象（包含路径）
        response = ErrorResponse(
            code=404,
            message="用例不存在",
            path="/api/v1/cases/999"
        )

        # 验证：路径正确设置
        assert response.path == "/api/v1/cases/999"

    def test_error_response_all_fields(self):
        """测试所有字段"""
        # 创建完整的错误响应对象
        response = ErrorResponse(
            code=404,
            message="Case not found",
            error="Case with id 999 does not exist",
            path="/api/v1/cases/999"
        )

        # 验证：所有字段正确设置
        assert response.code == 404
        assert response.message == "Case not found"
        assert response.error == "Case with id 999 does not exist"
        assert response.path == "/api/v1/cases/999"

    def test_error_response_code_range(self):
        """测试状态码范围验证"""
        # 测试各种合法状态码
        for code in [400, 404, 500, 503]:
            # 创建错误响应对象
            response = ErrorResponse(code=code, message="Error")
            # 验证：状态码正确
            assert response.code == code

    def test_error_response_serialization(self):
        """测试 JSON 序列化"""
        # 创建错误响应对象
        response = ErrorResponse(
            code=422,
            message="Validation error",
            error="Invalid priority value",
            path="/api/v1/cases"
        )

        # 转换为字典
        result = response.model_dump()

        # 验证：序列化后的字典包含所有字段
        assert result["code"] == 422
        assert result["message"] == "Validation error"
        assert result["error"] == "Invalid priority value"
        assert result["path"] == "/api/v1/cases"

    def test_error_response_optional_fields(self):
        """测试可选字段默认为 None"""
        # 创建错误响应对象（只有必填字段）
        response = ErrorResponse(code=500, message="Server error")

        # 验证：可选字段为 None
        assert response.error is None
        assert response.path is None
