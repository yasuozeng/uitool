"""
测试用例和步骤模型单元测试
"""
# 导入 pytest 测试框架，用于编写测试用例和参数化测试
import pytest
# 导入 datetime 模块，用于时间相关的验证
from datetime import datetime
# 从 app.models.case 导入需要测试的模型类
from app.models.case import TestCase, TestStep


class TestCaseModel:
    """TestCase 模型测试"""

    def test_create_test_case_minimal(self):
        """测试创建最小测试用例"""
        # 创建只包含名称字段的测试用例对象
        case = TestCase(name="测试用例1")

        # 验证：未保存到数据库前 ID 应为 None
        assert case.id is None
        # 验证：用例名称正确赋值
        assert case.name == "测试用例1"
        # 验证：描述字段默认为 None
        assert case.description is None
        # 注意：priority 的默认值是数据库层面的，Python 创建时为 None
        # 验证：标签字段默认为 None
        assert case.tags is None
        # 验证：步骤关系默认为空列表
        assert case.steps == []

    def test_create_test_case_full(self):
        """测试创建完整测试用例"""
        # 创建包含所有可选字段的测试用例对象
        case = TestCase(
            name="完整测试用例",  # 用例名称
            description="这是一个完整的测试用例",  # 用例描述
            priority="P0",  # 优先级 P0（最高）
            tags="登录, smoke, critical"  # 标签，逗号分隔
        )

        # 验证：用例名称正确赋值
        assert case.name == "完整测试用例"
        # 验证：用例描述正确赋值
        assert case.description == "这是一个完整的测试用例"
        # 验证：优先级正确赋值为 P0
        assert case.priority == "P0"
        # 验证：标签正确赋值
        assert case.tags == "登录, smoke, critical"

    def test_to_dict(self):
        """测试 to_dict 方法"""
        # 创建一个包含 ID 的测试用例对象
        case = TestCase(
            id=1,  # 模拟已保存的 ID
            name="字典转换测试",  # 用例名称
            description="测试转换为字典",  # 用例描述
            priority="P2",  # 优先级
            tags="tag1, tag2"  # 标签
        )

        # 调用 to_dict 方法转换为字典
        result = case.to_dict()

        # 验证：字典包含正确的 ID
        assert result["id"] == 1
        # 验证：字典包含正确的名称
        assert result["name"] == "字典转换测试"
        # 验证：字典包含正确的描述
        assert result["description"] == "测试转换为字典"
        # 验证：字典包含正确的优先级
        assert result["priority"] == "P2"
        # 验证：字典包含正确的标签
        assert result["tags"] == "tag1, tag2"
        # 验证：字典包含 created_at 键
        assert "created_at" in result
        # 验证：字典包含 updated_at 键
        assert "updated_at" in result

    def test_to_dict_with_none_timestamps(self):
        """测试 to_dict 方法处理 None 时间戳"""
        # 创建时间戳为 None 的测试用例对象
        case = TestCase(
            id=1,  # 用例 ID
            name="测试用例",  # 用例名称
            created_at=None,  # 创建时间为 None
            updated_at=None  # 更新时间为 None
        )

        # 调用 to_dict 方法转换为字典
        result = case.to_dict()

        # 验证：created_at 在字典中为 None
        assert result["created_at"] is None
        # 验证：updated_at 在字典中为 None
        assert result["updated_at"] is None

    @pytest.mark.parametrize("priority", ["P0", "P1", "P2", "P3"])  # 参数化测试：测试 4 个优先级
    def test_valid_priorities(self, priority):
        """测试有效优先级值"""
        # 使用参数化的优先级创建测试用例
        case = TestCase(name="优先级测试", priority=priority)
        # 验证：优先级正确赋值
        assert case.priority == priority


class TestStepModel:
    """TestStep 模型测试"""

    def test_create_test_step_minimal(self):
        """测试创建最小测试步骤"""
        # 创建只包含必要字段的测试步骤对象
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type="navigate"  # 操作类型
        )

        # 验证：未保存前 ID 为 None
        assert step.id is None
        # 验证：用例 ID 正确
        assert step.case_id == 1
        # 验证：步骤顺序正确
        assert step.step_order == 1
        # 验证：操作类型正确
        assert step.action_type == "navigate"
        # 验证：元素定位符默认为 None
        assert step.element_locator is None
        # 验证：定位类型默认为 None
        assert step.locator_type is None
        # 验证：操作参数默认为 None
        assert step.action_params is None
        # 验证：期望结果默认为 None
        assert step.expected_result is None
        # 验证：步骤描述默认为 None
        assert step.description is None

    def test_create_test_step_full(self):
        """测试创建完整测试步骤"""
        # 创建包含所有字段的测试步骤对象
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type="input",  # 操作类型：输入文本
            element_locator="#username",  # 元素定位符
            locator_type="css",  # 定位类型：CSS 选择器
            action_params='{"text": "testuser"}',  # 操作参数 JSON 字符串
            expected_result="输入成功",  # 期望结果
            description="输入用户名"  # 步骤描述
        )

        # 验证：用例 ID 正确
        assert step.case_id == 1
        # 验证：步骤顺序正确
        assert step.step_order == 1
        # 验证：操作类型正确
        assert step.action_type == "input"
        # 验证：元素定位符正确
        assert step.element_locator == "#username"
        # 验证：定位类型正确
        assert step.locator_type == "css"
        # 验证：操作参数正确
        assert step.action_params == '{"text": "testuser"}'
        # 验证：期望结果正确
        assert step.expected_result == "输入成功"
        # 验证：步骤描述正确
        assert step.description == "输入用户名"

    def test_params_dict_property_valid_json(self):
        """测试 params_dict 属性 - 有效 JSON"""
        # 创建包含有效 JSON 参数的测试步骤
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type="input",  # 操作类型
            action_params='{"url": "https://example.com", "timeout": 5000}'  # JSON 参数
        )

        # 获取解析后的参数字典
        result = step.params_dict
        # 验证：JSON 被正确解析为字典
        assert result == {"url": "https://example.com", "timeout": 5000}

    def test_params_dict_property_invalid_json(self):
        """测试 params_dict 属性 - 无效 JSON"""
        # 创建包含无效 JSON 的测试步骤
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type="click",  # 操作类型
            action_params="invalid json"  # 无效的 JSON 字符串
        )

        # 获取解析后的参数字典
        result = step.params_dict
        # 验证：无效 JSON 返回空字典
        assert result == {}

    def test_params_dict_property_none(self):
        """测试 params_dict 属性 - None"""
        # 创建参数为 None 的测试步骤
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type="click"  # 操作类型（无参数）
        )

        # 获取解析后的参数字典
        result = step.params_dict
        # 验证：None 返回空字典
        assert result == {}

    def test_set_params(self):
        """测试 set_params 方法"""
        # 创建测试步骤对象
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type="navigate"  # 操作类型
        )

        # 设置参数字典（会被转换为 JSON 字符串）
        step.set_params({"url": "https://example.com", "wait": 2000})
        # 验证：参数被正确序列化为 JSON 字符串
        assert step.action_params == '{"url": "https://example.com", "wait": 2000}'

    def test_set_params_none(self):
        """测试 set_params 方法 - None"""
        # 创建带参数的测试步骤
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type="click",  # 操作类型
            action_params='{"text": "old"}'  # 初始参数
        )

        # 设置参数为 None（清空参数）
        step.set_params(None)
        # 验证：参数被设置为 None
        assert step.action_params is None

    def test_set_params_empty_dict(self):
        """测试 set_params 方法 - 空字典"""
        # 创建测试步骤对象
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type="click"  # 操作类型
        )

        # 设置空字典参数
        step.set_params({})
        # 验证：空字典被转换为 None
        assert step.action_params is None

    def test_to_dict(self):
        """测试 to_dict 方法"""
        # 创建完整的测试步骤对象
        step = TestStep(
            id=1,  # 步骤 ID
            case_id=5,  # 所属用例 ID
            step_order=2,  # 步骤顺序号
            action_type="input",  # 操作类型
            element_locator="#password",  # 元素定位符
            locator_type="css",  # 定位类型
            action_params='{"text": "secret"}',  # 操作参数
            expected_result="输入成功",  # 期望结果
            description="输入密码"  # 步骤描述
        )

        # 调用 to_dict 方法转换为字典
        result = step.to_dict()

        # 验证：字典包含正确的 ID
        assert result["id"] == 1
        # 验证：字典包含正确的用例 ID
        assert result["case_id"] == 5
        # 验证：字典包含正确的步骤顺序
        assert result["step_order"] == 2
        # 验证：字典包含正确的操作类型
        assert result["action_type"] == "input"
        # 验证：字典包含正确的元素定位符
        assert result["element_locator"] == "#password"
        # 验证：字典包含正确的定位类型
        assert result["locator_type"] == "css"
        # 验证：字典包含解析后的参数字典
        assert result["action_params"] == {"text": "secret"}
        # 验证：字典包含正确的期望结果
        assert result["expected_result"] == "输入成功"
        # 验证：字典包含正确的步骤描述
        assert result["description"] == "输入密码"
        # 验证：字典包含 created_at 键
        assert "created_at" in result
        # 验证：字典包含 updated_at 键
        assert "updated_at" in result

    @pytest.mark.parametrize("action_type", [  # 参数化测试：测试各种操作类型
        "navigate",  # 页面跳转
        "click",  # 点击元素
        "input",  # 输入文本
        "clear",  # 清空输入
        "wait",  # 等待元素
        "verify_text",  # 验证文本
        "verify_element"  # 验证元素
    ])
    def test_valid_action_types(self, action_type):
        """测试有效操作类型"""
        # 使用参数化的操作类型创建测试步骤
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type=action_type  # 参数化的操作类型
        )
        # 验证：操作类型正确赋值
        assert step.action_type == action_type

    @pytest.mark.parametrize("locator_type", ["id", "xpath", "css", "name", "class"])  # 参数化测试
    def test_valid_locator_types(self, locator_type):
        """测试有效定位类型"""
        # 使用参数化的定位类型创建测试步骤
        step = TestStep(
            case_id=1,  # 所属用例 ID
            step_order=1,  # 步骤顺序号
            action_type="click",  # 操作类型
            locator_type=locator_type  # 参数化的定位类型
        )
        # 验证：定位类型正确赋值
        assert step.locator_type == locator_type
