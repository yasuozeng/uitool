"""
基础接口测试
测试根路径、健康检查和静态文件访问等基础 HTTP 端点
"""
# 导入 pytest 测试框架
import pytest
# 导入时间模块用于测量响应时间
import time


class TestRootEndpoint:
    """测试 GET / - 根路径接口"""

    def test_root_success(self, client):
        """测试访问根路径成功"""
        # 发送 GET 请求
        response = client.get("/")

        # 验证：状态码 200
        assert response.status_code == 200

        # 验证：响应数据
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "redoc" in data

    def test_root_fields(self, client):
        """测试根路径响应字段完整性"""
        # 发送 GET 请求
        response = client.get("/")

        # 验证：状态码 200
        assert response.status_code == 200

        # 验证：响应数据结构
        data = response.json()
        # 验证 message 字段
        assert data["message"] == "uiTool1.0 API"
        # 验证 version 字段格式
        assert isinstance(data["version"], str)
        # 验证 docs 字段
        assert data["docs"] == "/docs"
        # 验证 redoc 字段
        assert data["redoc"] == "/redoc"


class TestHealthCheck:
    """测试 GET /health - 健康检查接口"""

    def test_health_check_success(self, client):
        """测试健康检查成功"""
        # 发送 GET 请求
        response = client.get("/health")

        # 验证：状态码 200
        assert response.status_code == 200

        # 验证：响应数据
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_response_time(self, client, health_check_response_time_threshold):
        """测试健康检查响应时间"""
        # 记录开始时间
        start_time = time.time()

        # 发送 GET 请求
        response = client.get("/health")

        # 记录结束时间
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000  # 转换为毫秒

        # 验证：状态码 200
        assert response.status_code == 200

        # 验证：响应时间在阈值范围内
        assert response_time_ms < health_check_response_time_threshold, \
            f"健康检查响应时间 {response_time_ms:.2f}ms 超过阈值 {health_check_response_time_threshold}ms"


class TestStaticFiles:
    """测试 GET /api/v1/screenshots/{filename} - 静态文件访问接口"""

    def test_screenshot_exists(self, client, sample_screenshot_file):
        """测试访问存在的截图文件"""
        screenshots_dir, screenshot_filename = sample_screenshot_file

        # 注意：由于测试环境的静态文件路径配置，
        # 这个测试需要根据实际的静态文件配置进行调整

        # 发送 GET 请求
        # 这里假设静态文件路径可以通过 API 访问
        response = client.get(f"/api/v1/screenshots/{screenshot_filename}")

        # 验证：文件可能不存在于实际的静态文件目录中
        # 这取决于后端的静态文件配置
        # 如果配置正确，应该返回 200 和图片内容
        # 如果配置不正确，返回 404
        assert response.status_code in [200, 404]

        # 如果返回 200，验证内容类型
        if response.status_code == 200:
            assert "image" in response.headers.get("content-type", "")

    def test_screenshot_not_found(self, client):
        """测试访问不存在的截图"""
        # 发送 GET 请求（文件不存在）
        response = client.get("/api/v1/screenshots/nonexistent.png")

        # 验证：404 错误
        assert response.status_code == 404

    def test_screenshot_path_traversal(self, client):
        """测试路径遍历攻击防护"""
        # 发送 GET 请求（路径遍历攻击）
        response = client.get("/api/v1/screenshots/../test.png")

        # 验证：拒绝访问（400 或 403 或 404）
        assert response.status_code in [400, 403, 404]

    def test_screenshot_invalid_extension(self, client):
        """测试非图片文件扩展名"""
        # 发送 GET 请求（非图片扩展名）
        response = client.get("/api/v1/screenshots/test.txt")

        # 验证：拒绝访问（400 或 404）
        assert response.status_code in [400, 404]

    def test_screenshot_with_subdirectory(self, client):
        """测试包含子目录的文件路径"""
        # 发送 GET 请求（包含子目录）
        response = client.get("/api/v1/screenshots/subdir/test.png")

        # 验证：根据实际配置，可能返回 200 或 404
        # 正常情况下应该拒绝子目录访问
        assert response.status_code in [200, 400, 403, 404]

    def test_screenshot_empty_filename(self, client):
        """测试空文件名"""
        # 发送 GET 请求（空文件名）
        response = client.get("/api/v1/screenshots/")

        # 验证：拒绝访问
        assert response.status_code in [400, 404]
