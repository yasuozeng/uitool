"""
测试用例相关的 Pydantic 数据模式
定义测试用例和测试步骤的数据验证结构
"""
# 从 datetime 模块导入 datetime 类，用于时间戳字段
from datetime import datetime
# 从 typing 模块导入类型注解工具
from typing import Optional, List
# 从 pydantic 导入基础模型、字段定义和字段验证器
from pydantic import BaseModel, Field, field_validator


# ========== 步骤相关 ==========

# 定义测试步骤的基础模式类
class StepBase(BaseModel):
    """
    步骤基础模式

    定义测试步骤的通用字段结构
    """
    # 步骤顺序字段：必填，最小值为 1
    step_order: int = Field(..., ge=1, description="步骤顺序")
    # 操作类型字段：必填，如 navigate/click/input 等
    action_type: str = Field(..., description="操作类型")
    # 元素定位符字段：可选，如 #button 或 //input[@id='xxx']
    element_locator: Optional[str] = Field(None, description="元素定位符")
    # 定位类型字段：默认 "css"，可选 id/xpath/css/name/class
    locator_type: str = Field("css", description="定位类型")
    # 操作参数字段：可选，如输入文本、URL 地址等
    action_params: Optional[dict] = Field(None, description="操作参数")
    # 期望结果字段：可选，用于验证步骤执行结果
    expected_result: Optional[str] = Field(None, description="期望结果")
    # 步骤描述字段：可选，用于说明步骤目的
    description: Optional[str] = Field(None, description="步骤描述")


# 定义创建步骤的模式类，继承基础模式
class StepCreate(StepBase):
    """
    创建步骤模式

    用于创建新测试步骤时的请求数据验证
    """
    pass  # 继承 StepBase 的所有字段


# 定义更新步骤的模式类，继承基础模式
class StepUpdate(StepBase):
    """
    更新步骤模式

    用于更新现有测试步骤时的请求数据验证
    """
    pass  # 继承 StepBase 的所有字段


# 定义步骤响应的模式类，继承基础模式
class StepResponse(StepBase):
    """
    步骤响应模式

    用于返回测试步骤数据到客户端
    """
    # 步骤 ID 字段：数据库自动生成
    id: int
    # 所属用例 ID 字段：关联到 test_cases 表
    case_id: int
    # 创建时间字段：记录步骤创建时间
    created_at: datetime
    # 更新时间字段：记录步骤最后修改时间
    updated_at: datetime

    # 内部配置类
    class Config:
        # 允许从 ORM 对象（数据库模型）创建 Pydantic 模型
        from_attributes = True


# ========== 用例相关 ==========

# 定义测试用例的基础模式类
class CaseBase(BaseModel):
    """
    用例基础模式

    定义测试用例的通用字段结构
    """
    # 用例名称字段：必填，长度 1-200 字符
    name: str = Field(..., min_length=1, max_length=200, description="用例名称")
    # 用例描述字段：可选，用于说明用例目的
    description: Optional[str] = Field(None, description="用例描述")
    # 优先级字段：默认 P1，只允许 P0/P1/P2/P3
    priority: str = Field("P1", pattern="^(P0|P1|P2|P3)$", description="优先级")
    # 标签字段：可选，最长 500 字符，逗号分隔
    tags: Optional[str] = Field(None, max_length=500, description="标签")


# 定义创建用例的模式类，继承基础模式
class CaseCreate(CaseBase):
    """
    创建用例模式

    用于创建新测试用例时的请求数据验证
    """
    # 测试步骤列表字段：必填，至少包含一个步骤
    steps: List[StepCreate] = Field(default_factory=list, description="测试步骤")


# 定义更新用例的模式类，继承基础模式
class CaseUpdate(CaseBase):
    """
    更新用例模式

    用于更新现有测试用例时的请求数据验证
    所有字段都变为可选，支持部分更新
    """
    # 用例名字段：可选，更新时可以不修改名称
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    # 优先级字段：可选，更新时可以不修改优先级
    priority: Optional[str] = Field(None, pattern="^(P0|P1|P2|P3)$")


# 定义用例响应的模式类，继承基础模式
class CaseResponse(CaseBase):
    """
    用例响应模式

    用于返回测试用例数据到客户端
    """
    # 用例 ID 字段：数据库自动生成
    id: int
    # 测试步骤列表字段：包含该用例的所有步骤
    steps: List[StepResponse] = Field(default_factory=list)
    # 创建时间字段：记录用例创建时间
    created_at: datetime
    # 更新时间字段：记录用例最后修改时间
    updated_at: datetime

    # 内部配置类
    class Config:
        # 允许从 ORM 对象（数据库模型）创建 Pydantic 模型
        from_attributes = True


# 定义用例列表响应的模式类
class CaseListResponse(BaseModel):
    """
    用例列表响应模式

    用于用例列表页面，不包含详细步骤信息
    """
    # 用例 ID 字段
    id: int
    # 用例名称字段
    name: str
    # 用例描述字段
    description: Optional[str]
    # 优先级字段
    priority: str
    # 标签字段
    tags: Optional[str]
    # 步骤数量字段：默认 0，表示该用例包含多少步骤
    step_count: int = 0
    # 创建时间字段
    created_at: datetime
    # 更新时间字段
    updated_at: datetime

    # 内部配置类
    class Config:
        # 允许从 ORM 对象（数据库模型）创建 Pydantic 模型
        from_attributes = True


# ========== 批量操作 ==========

# 定义批量创建步骤的模式类
class BatchStepCreate(BaseModel):
    """
    批量创建步骤模式

    用于一次性创建多个测试步骤
    """
    # 步骤列表字段：必填，至少包含一个步骤
    steps: List[StepCreate] = Field(..., min_length=1, description="步骤列表")


# 定义批量删除请求的模式类
class BatchDeleteRequest(BaseModel):
    """
    批量删除请求模式

    用于一次性删除多个测试用例
    """
    # 用例 ID 列表字段：必填，至少包含一个用例 ID
    case_ids: List[int] = Field(..., min_length=1, description="用例ID列表")


# ========== 查询参数 ==========

# 定义用例查询参数的模式类
class CaseQueryParams(BaseModel):
    """
    用例查询参数

    用于用例列表的筛选和分页
    """
    # 名称搜索字段：可选，用于模糊搜索用例名称
    name: Optional[str] = Field(None, description="按名称搜索")
    # 优先级筛选字段：可选，只允许 P0/P1/P2/P3
    priority: Optional[str] = Field(None, pattern="^(P0|P1|P2|P3)$", description="按优先级筛选")
    # 标签筛选字段：可选，用于按标签过滤用例
    tags: Optional[str] = Field(None, description="按标签筛选")
    # 页码字段：默认第 1 页，最小值为 1
    page: int = Field(1, ge=1, description="页码")
    # 每页数量字段：默认 20 条，范围 1-100
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
