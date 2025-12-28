"""
测试用例和步骤数据模型
定义测试用例表（test_cases）和测试步骤表（test_steps）的 ORM 模型
"""
# 从 datetime 模块导入 datetime 类，用于时间戳字段
from datetime import datetime
# 从 sqlalchemy 导入列类型
from sqlalchemy import String, Integer, Text, ForeignKey, JSON
# 从 sqlalchemy.orm 导入映射装饰器和关系定义
from sqlalchemy.orm import Mapped, mapped_column, relationship
# 从本地数据库模块导入 Base 基类
from app.models.database import Base


# 定义测试用表模型类
class TestCase(Base):
    """
    测试用例表模型

    对应数据库表 test_cases，存储测试用例的基本信息
    """
    # 指定数据库表名
    __tablename__ = "test_cases"

    # ID 字段：主键，整数类型，自动递增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 用例名字段：字符串类型，最大长度 200，不允许为空
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # 描述字段：文本类型，允许为空（使用 str | None 表示可选）
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 优先级字段：字符串类型，最大长度 10，默认 P1，不允许为空
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="P1")
    # 标签字段：字符串类型，最大长度 500，允许为空，用于逗号分隔的标签
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 创建时间字段：datetime 类型，不允许为空，默认当前时间
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    # 更新时间字段：datetime 类型，不允许为空，默认当前时间，更新时自动刷新
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now, onupdate=datetime.now)

    # 定义与 TestStep 的一对多关系：一个用例包含多个步骤
    # cascade="all, delete-orphan" 表示删除用例时级联删除所有关联步骤
    steps = relationship("TestStep", back_populates="test_case", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """
        转换为字典

        将模型对象转换为字典格式，便于 JSON 序列化

        Returns:
            dict: 包含用例数据的字典
        """
        # 返回字典格式的用例数据
        return {
            "id": self.id,  # 用例 ID
            "name": self.name,  # 用例名称
            "description": self.description,  # 用例描述
            "priority": self.priority,  # 优先级
            "tags": self.tags,  # 标签
            # 将 datetime 对象转换为 ISO 格式字符串
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# 定义测试步骤表模型类
class TestStep(Base):
    """
    测试步骤表模型

    对应数据库表 test_steps，存储测试用例的执行步骤
    """
    # 指定数据库表名
    __tablename__ = "test_steps"

    # ID 字段：主键，整数类型，自动递增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 用例 ID 字段：外键，关联到 test_cases 表
    # ondelete="CASCADE" 表示删除用例时自动删除关联步骤
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    # 步骤顺序字段：整数类型，表示步骤的执行顺序，不允许为空
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    # 操作类型字段：字符串类型，最大长度 50，如 navigate/click/input 等
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 元素定位符字段：字符串类型，最大长度 500，如 #button 或 //input
    element_locator: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 定位类型字段：字符串类型，最大长度 20，如 css/xpath/id 等
    locator_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # 操作参数字段：文本类型，存储 JSON 字符串格式的参数
    action_params: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON字符串
    # 期望结果字段：文本类型，用于验证步骤执行结果
    expected_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 步骤描述字段：字符串类型，最大长度 500，用于说明步骤目的
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 创建时间字段：datetime 类型，不允许为空，默认当前时间
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    # 更新时间字段：datetime 类型，不允许为空，默认当前时间，更新时自动刷新
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now, onupdate=datetime.now)

    # 定义与 TestCase 的多对一关系：一个步骤属于一个用例
    test_case = relationship("TestCase", back_populates="steps")

    @property
    def params_dict(self) -> dict:
        """
        获取解析后的参数字典

        将存储的 JSON 字符串解析为字典

        Returns:
            dict: 解析后的参数字典，解析失败返回空字典
        """
        # 导入 json 模块用于解析 JSON 字符串
        import json
        # 如果 action_params 不为空
        if self.action_params:
            try:
                # 尝试解析 JSON 字符串为字典
                return json.loads(self.action_params)
            except json.JSONDecodeError:
                # 解析失败时返回空字典
                return {}
        # action_params 为空时返回空字典
        return {}

    def set_params(self, params: dict):
        """
        设置参数

        将字典转换为 JSON 字符串并存储

        Args:
            params: 参数字典
        """
        # 导入 json 模块用于序列化
        import json
        # 将字典转换为 JSON 字符串存储，如果 params 为空则存储 None
        self.action_params = json.dumps(params) if params else None

    def to_dict(self) -> dict:
        """
        转换为字典

        将模型对象转换为字典格式，便于 JSON 序列化

        Returns:
            dict: 包含步骤数据的字典，参数自动解析为字典
        """
        # 返回字典格式的步骤数据
        return {
            "id": self.id,  # 步骤 ID
            "case_id": self.case_id,  # 所属用例 ID
            "step_order": self.step_order,  # 步骤顺序
            "action_type": self.action_type,  # 操作类型
            "element_locator": self.element_locator,  # 元素定位符
            "locator_type": self.locator_type,  # 定位类型
            # 使用 params_dict 属性自动解析 JSON 字符串
            "action_params": self.params_dict,
            "expected_result": self.expected_result,  # 期望结果
            "description": self.description,  # 步骤描述
            # 将 datetime 对象转换为 ISO 格式字符串
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
