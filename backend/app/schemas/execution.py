"""
测试执行相关的 Pydantic 数据模式
定义测试执行任务和执行结果的数据验证结构
"""
# 从 datetime 模块导入 datetime 类，用于时间戳字段
from datetime import datetime
# 从 typing 模块导入类型注解工具
from typing import Optional, List
# 从 pydantic 导入基础模型、字段定义和计算字段装饰器
from pydantic import BaseModel, Field, computed_field


# ========== 执行请求 ==========

# 定义创建执行任务的请求模式类
class ExecutionCreate(BaseModel):
    """
    创建执行任务模式

    用于启动测试执行任务的请求数据验证
    """
    # 执行类型字段：必填，single 单个用例或 batch 批量用例
    execution_type: str = Field(..., pattern="^(single|batch)$", description="执行类型")
    # 浏览器类型字段：默认 chrome，可选 chrome/firefox/edge
    browser_type: str = Field("chrome", pattern="^(chrome|firefox|edge)$", description="浏览器类型")
    # 无头模式字段：默认 True，True 不显示浏览器，False 显示浏览器
    headless: bool = Field(True, description="无头模式")
    # 窗口大小字段：可选，如 1920x1080
    window_size: Optional[str] = Field(None, description="窗口大小")
    # 用例 ID 列表字段：可选，批量模式下指定要执行的用例
    case_ids: Optional[List[int]] = Field(None, description="用例ID列表（batch模式）")

    # 内部配置类
    class Config:
        # 定义 JSON Schema 示例，用于 API 文档展示
        json_schema_extra = {
            "example": {  # 示例数据
                "execution_type": "batch",  # 批量执行模式
                "browser_type": "chrome",  # 使用 Chrome 浏览器
                "headless": True,  # 无头模式
                "window_size": "1920x1080",  # 窗口大小
                "case_ids": [1, 2, 3]  # 要执行的用例 ID 列表
            }
        }


# ========== 执行响应 ==========

# 定义执行任务响应的模式类
class ExecutionResponse(BaseModel):
    """
    执行任务响应模式

    用于返回执行任务数据到客户端
    """
    # 执行任务 ID 字段：数据库自动生成
    id: int
    # 执行类型字段：single 或 batch
    execution_type: str
    # 浏览器类型字段：chrome/firefox/edge
    browser_type: str
    # 无头模式字段：True/False
    headless: bool
    # 窗口大小字段：如 1920x1080
    window_size: Optional[str]
    # 开始时间字段：执行开始的时间戳
    start_time: datetime
    # 结束时间字段：执行结束的时间戳（执行中为空）
    end_time: Optional[datetime] = None
    # 总用例数字段：本次执行包含的用例总数
    total_count: int
    # 成功用例数字段：执行成功的用例数量
    success_count: int
    # 失败用例数字段：执行失败的用例数量
    fail_count: int
    # 跳过用例数字段：跳过执行的用例数量
    skip_count: int = 0
    # 执行状态字段：pending/running/completed/failed
    status: str
    # 通过率字段：成功率百分比（0-100）
    pass_rate: float
    # 执行时长字段：单位毫秒（执行中为空）
    duration: Optional[int]
    # 创建时间字段：记录创建时间
    created_at: datetime

    # 前端期望的字段别名（序列化时使用）
    @computed_field  # type: ignore[misc]
    @property
    def browser(self) -> str:
        """浏览器类型别名"""
        return self.browser_type

    @computed_field  # type: ignore[misc]
    @property
    def started_at(self) -> datetime:
        """开始时间别名"""
        return self.start_time

    @computed_field  # type: ignore[misc]
    @property
    def completed_at(self) -> Optional[datetime]:
        """结束时间别名"""
        return self.end_time

    @computed_field  # type: ignore[misc]
    @property
    def total_cases(self) -> int:
        """总用例数别名"""
        return self.total_count

    @computed_field  # type: ignore[misc]
    @property
    def passed_cases(self) -> int:
        """成功用例数别名"""
        return self.success_count

    @computed_field  # type: ignore[misc]
    @property
    def failed_cases(self) -> int:
        """失败用例数别名"""
        return self.fail_count

    # 内部配置类
    class Config:
        # 允许从 ORM 对象（数据库模型）创建 Pydantic 模型
        from_attributes = True
        # 启用按名称填充，允许使用别名进行序列化
        populate_by_name = True


# 定义执行任务列表响应的模式类
class ExecutionListResponse(BaseModel):
    """
    执行任务列表响应模式

    用于执行列表页面，包含简要信息
    """
    # 执行任务 ID 字段
    id: int
    # 执行类型字段
    execution_type: str
    # 浏览器类型字段
    browser_type: str
    # 执行状态字段
    status: str
    # 总用例数字段
    total_count: int
    # 成功用例数字段
    success_count: int
    # 失败用例数字段
    fail_count: int
    # 通过率字段
    pass_rate: float
    # 开始时间字段
    start_time: datetime
    # 创建时间字段
    created_at: datetime

    # 前端期望的字段别名（序列化时使用）
    @computed_field  # type: ignore[misc]
    @property
    def browser(self) -> str:
        """浏览器类型别名"""
        return self.browser_type

    @computed_field  # type: ignore[misc]
    @property
    def started_at(self) -> datetime:
        """开始时间别名"""
        return self.start_time

    @computed_field  # type: ignore[misc]
    @property
    def total_cases(self) -> int:
        """总用例数别名"""
        return self.total_count

    @computed_field  # type: ignore[misc]
    @property
    def passed_cases(self) -> int:
        """成功用例数别名"""
        return self.success_count

    @computed_field  # type: ignore[misc]
    @property
    def failed_cases(self) -> int:
        """失败用例数别名"""
        return self.fail_count

    # 内部配置类
    class Config:
        # 允许从 ORM 对象（数据库模型）创建 Pydantic 模型
        from_attributes = True
        # 启用按名称填充，允许使用别名进行序列化
        populate_by_name = True


# ========== 执行详情响应 ==========

# 定义执行详情响应的模式类
class ExecutionDetailResponse(BaseModel):
    """
    执行详情响应模式

    用于返回单个用例的执行结果详情
    """
    # 详情 ID 字段：数据库自动生成
    id: int
    # 所属执行任务 ID 字段：关联到 executions 表
    execution_id: int
    # 用例 ID 字段：被执行的用例 ID
    case_id: int
    # 用例名称字段：用例的名称
    case_name: str
    # 执行状态字段：success/failed/skipped
    status: str
    # 错误消息字段：可选，失败时的错误描述
    error_message: Optional[str]
    # 错误堆栈字段：可选，失败时的详细堆栈信息
    error_stack: Optional[str]
    # 截图路径字段：可选，失败时的截图文件路径
    screenshot_path: Optional[str]
    # 步骤日志字段：可选，每个步骤的执行日志
    step_logs: Optional[list]
    # 开始时间字段：用例开始执行的时间
    start_time: datetime
    # 结束时间字段：用例执行结束的时间（执行中为空）
    end_time: Optional[datetime]
    # 执行时长字段：单位毫秒（执行中为空）
    duration: Optional[int]
    # 创建时间字段：记录创建时间
    created_at: datetime

    # 内部配置类
    class Config:
        # 允许从 ORM 对象（数据库模型）创建 Pydantic 模型
        from_attributes = True
        # 启用按名称填充，允许使用别名进行序列化
        populate_by_name = True


# ========== 执行日志 ==========

# 定义执行日志消息的模式类
class ExecutionLogMessage(BaseModel):
    """
    执行日志消息模式

    用于 WebSocket 推送实时执行日志
    """
    # 消息类型字段：必填，支持五种消息类型
    type: str = Field(..., pattern="^(step_start|step_success|step_failed|log|error)$")
    # 执行任务 ID 字段：关联到执行的任务
    execution_id: int
    # 用例 ID 字段：可选，关联到具体用例
    case_id: Optional[int]
    # 步骤序号字段：可选，关联到具体步骤
    step_order: Optional[int]
    # 消息内容字段：日志文本内容
    message: str
    # 时间戳字段：消息产生的时间
    timestamp: datetime
    # 附加数据字段：可选，携带额外的结构化数据
    data: Optional[dict] = None


# ========== 查询参数 ==========

# 定义执行查询参数的模式类
class ExecutionQueryParams(BaseModel):
    """
    执行查询参数

    用于执行列表的筛选和分页
    """
    # 状态筛选字段：可选，只允许 pending/running/completed/failed
    status: Optional[str] = Field(None, pattern="^(pending|running|completed|failed)$")
    # 浏览器类型筛选字段：可选，只允许 chrome/firefox/edge
    browser_type: Optional[str] = Field(None, pattern="^(chrome|firefox|edge)$")
    # 页码字段：默认第 1 页，最小值为 1
    page: int = Field(1, ge=1)
    # 每页数量字段：默认 20 条，范围 1-100
    page_size: int = Field(20, ge=1, le=100)
