"""
测试执行记录数据模型
定义测试执行表（executions）和执行详情表（execution_details）的 ORM 模型
"""
# 从 datetime 模块导入 datetime 类，用于时间戳字段
from datetime import datetime
# 从 sqlalchemy 导入列类型
from sqlalchemy import String, Integer, Text, ForeignKey, Boolean, BigInteger
# 从 sqlalchemy.orm 导入映射装饰器和关系定义
from sqlalchemy.orm import Mapped, mapped_column, relationship
# 从本地数据库模块导入 Base 基类
from app.models.database import Base


# 定义测试执行记录表模型类
class Execution(Base):
    """
    测试执行记录表模型

    对应数据库表 executions，存储测试执行任务的汇总信息
    """
    # 指定数据库表名
    __tablename__ = "executions"

    # ID 字段：主键，整数类型，自动递增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 执行类型字段：字符串类型，single 单个用例或 batch 批量用例
    execution_type: Mapped[str] = mapped_column(String(20), nullable=False)  # single/batch
    # 浏览器类型字段：字符串类型，chrome/firefox/edge
    browser_type: Mapped[str] = mapped_column(String(20), nullable=False)  # chrome/firefox/edge
    # 无头模式字段：布尔类型，默认 False（显示浏览器），True 为无头模式
    headless: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # 窗口大小字段：字符串类型，如 1920x1080
    window_size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # 开始时间字段：datetime 类型，执行开始的时间
    start_time: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    # 结束时间字段：datetime 类型，执行结束的时间（执行中为空）
    end_time: Mapped[datetime | None] = mapped_column(nullable=True)
    # 总用例数字段：整数类型，本次执行的用例总数
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 用例ID列表字段：文本类型，存储 JSON 字符串格式的用例 ID 列表
    case_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 成功用例数字段：整数类型，执行成功的用例数量
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 失败用例数字段：整数类型，执行失败的用例数量
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 跳过用例数字段：整数类型，跳过执行的用例数量
    skip_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 执行状态字段：字符串类型，pending/running/completed/failed
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending/running/completed/failed
    # 创建时间字段：datetime 类型，记录创建时间
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)

    # 定义与 ExecutionDetail 的一对多关系：一个执行包含多个执行详情
    # cascade="all, delete-orphan" 表示删除执行记录时级联删除所有关联详情
    details = relationship("ExecutionDetail", back_populates="execution", cascade="all, delete-orphan")

    @property
    def case_ids_list(self) -> list:
        """
        获取解析后的用例 ID 列表

        将存储的 JSON 字符串解析为用例 ID 列表

        Returns:
            list: 用例 ID 列表，解析失败返回空列表
        """
        # 导入 json 模块用于解析 JSON 字符串
        import json
        # 如果 case_ids_json 不为空
        if self.case_ids_json:
            try:
                # 尝试解析 JSON 字符串为列表
                return json.loads(self.case_ids_json)
            except json.JSONDecodeError:
                # 解析失败时返回空列表
                return []
        # case_ids_json 为空时返回空列表
        return []

    def set_case_ids(self, case_ids: list):
        """
        设置用例 ID 列表

        将用例 ID 列表转换为 JSON 字符串并存储

        Args:
            case_ids: 用例 ID 列表
        """
        # 导入 json 模块用于序列化
        import json
        # 将列表转换为 JSON 字符串存储，如果 case_ids 为空则存储 None
        self.case_ids_json = json.dumps(case_ids) if case_ids else None

    @property
    def pass_rate(self) -> float:
        """
        计算通过率

        根据成功数和总数计算通过率百分比

        Returns:
            float: 通过率（0-100），保留两位小数
        """
        # 如果总用例数为 0，返回 0.0 避免除零错误
        if self.total_count == 0:
            return 0.0
        # 计算通过率：(成功数 / 总数) * 100，保留两位小数
        return round(self.success_count * 100.0 / self.total_count, 2)

    @property
    def duration(self) -> int | None:
        """
        计算执行时长

        根据开始时间和结束时间计算执行时长（毫秒）

        Returns:
            int | None: 执行时长（毫秒），如果未结束则返回 None
        """
        # 如果开始时间和结束时间都存在
        if self.end_time and self.start_time:
            # 计算时间差
            delta = self.end_time - self.start_time
            # 转换为毫秒并返回
            return int(delta.total_seconds() * 1000)
        # 如果未结束，返回 None
        return None

    def to_dict(self) -> dict:
        """
        转换为字典

        将模型对象转换为字典格式，便于 JSON 序列化

        Returns:
            dict: 包含执行记录数据的字典
        """
        # 返回字典格式的执行记录数据
        return {
            "id": self.id,  # 执行记录 ID
            "execution_type": self.execution_type,  # 执行类型
            "browser_type": self.browser_type,  # 浏览器类型
            "headless": self.headless,  # 无头模式
            "window_size": self.window_size,  # 窗口大小
            # 将 datetime 对象转换为 ISO 格式字符串
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_count": self.total_count,  # 总用例数
            "success_count": self.success_count,  # 成功数
            "fail_count": self.fail_count,  # 失败数
            "skip_count": self.skip_count,  # 跳过数
            "status": self.status,  # 执行状态
            "pass_rate": self.pass_rate,  # 通过率（计算属性）
            "duration": self.duration,  # 执行时长（计算属性）
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# 定义测试执行详情表模型类
class ExecutionDetail(Base):
    """
    测试执行详情表模型

    对应数据库表 execution_details，存储每个用例的执行结果详情
    """
    # 指定数据库表名
    __tablename__ = "execution_details"

    # ID 字段：主键，整数类型，自动递增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 执行记录 ID 字段：外键，关联到 executions 表
    # ondelete="CASCADE" 表示删除执行记录时自动删除关联详情
    execution_id: Mapped[int] = mapped_column(Integer, ForeignKey("executions.id", ondelete="CASCADE"), nullable=False)
    # 用例 ID 字段：外键，关联到 test_cases 表
    # ondelete="CASCADE" 表示删除用例时自动删除关联的执行详情
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    # 用例名称字段：字符串类型，最大长度 200，冗余存储便于查询
    case_name: Mapped[str] = mapped_column(String(200), nullable=False)
    # 执行状态字段：字符串类型，success/failed/skipped
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success/failed/skipped
    # 错误消息字段：文本类型，失败时的错误描述
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 错误堆栈字段：文本类型，失败时的详细堆栈信息
    error_stack: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 截图路径字段：字符串类型，最大长度 500，失败时的截图文件路径
    screenshot_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 步骤日志字段：文本类型，存储 JSON 字符串格式的日志列表
    step_logs: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON字符串
    # 开始时间字段：datetime 类型，用例开始执行的时间
    start_time: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    # 结束时间字段：datetime 类型，用例执行结束的时间（执行中为空）
    end_time: Mapped[datetime | None] = mapped_column(nullable=True)
    # 执行时长字段：大整数类型，单位毫秒
    duration: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # 毫秒
    # 创建时间字段：datetime 类型，记录创建时间
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)

    # 定义与 Execution 的多对一关系：一个详情属于一个执行记录
    execution = relationship("Execution", back_populates="details")

    @property
    def logs_list(self) -> list:
        """
        获取解析后的日志列表

        将存储的 JSON 字符串解析为日志列表

        Returns:
            list: 解析后的日志列表，解析失败返回空列表
        """
        # 导入 json 模块用于解析 JSON 字符串
        import json
        # 如果 step_logs 不为空
        if self.step_logs:
            try:
                # 尝试解析 JSON 字符串为列表
                return json.loads(self.step_logs)
            except json.JSONDecodeError:
                # 解析失败时返回空列表
                return []
        # step_logs 为空时返回空列表
        return []

    def set_logs(self, logs: list):
        """
        设置日志

        将日志列表转换为 JSON 字符串并存储

        Args:
            logs: 日志列表
        """
        # 导入 json 模块用于序列化
        import json
        # 将列表转换为 JSON 字符串存储，如果 logs 为空则存储 None
        self.step_logs = json.dumps(logs) if logs else None

    def to_dict(self) -> dict:
        """
        转换为字典

        将模型对象转换为字典格式，便于 JSON 序列化

        Returns:
            dict: 包含执行详情数据的字典，日志自动解析为列表
        """
        # 返回字典格式的执行详情数据
        return {
            "id": self.id,  # 详情 ID
            "execution_id": self.execution_id,  # 所属执行记录 ID
            "case_id": self.case_id,  # 用例 ID
            "case_name": self.case_name,  # 用例名称
            "status": self.status,  # 执行状态
            "error_message": self.error_message,  # 错误消息
            "error_stack": self.error_stack,  # 错误堆栈
            "screenshot_path": self.screenshot_path,  # 截图路径
            # 使用 logs_list 属性自动解析 JSON 字符串
            "step_logs": self.logs_list,
            # 将 datetime 对象转换为 ISO 格式字符串
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,  # 执行时长
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
