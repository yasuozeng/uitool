"""
通用响应模式
定义 API 响应的通用数据结构
"""
# 从 typing 模块导入类型注解工具
from typing import Optional, Any, Generic, TypeVar
# 从 pydantic 导入基础模型和字段定义
from pydantic import BaseModel, Field


# 定义泛型类型变量 T，用于表示任意数据类型
T = TypeVar("T")


# 定义统一的 API 响应格式类，继承 BaseModel 并支持泛型
class ApiResponse(BaseModel, Generic[T]):
    """
    统一 API 响应格式

    所有 API 接口都使用此格式返回数据
    """
    # 状态码字段：默认 200，表示成功
    code: int = Field(200, description="状态码")
    # 响应消息字段：默认 "success"，描述操作结果
    message: str = Field("success", description="响应消息")
    # 响应数据字段：可选的泛型类型，默认为 None
    data: Optional[T] = Field(None, description="响应数据")

    # 内部配置类
    class Config:
        # 定义 JSON Schema 示例，用于 API 文档展示
        json_schema_extra = {
            "example": {  # 示例数据
                "code": 200,  # 成功状态码
                "message": "success",  # 成功消息
                "data": {}  # 空数据对象
            }
        }


# 定义分页响应格式类，继承 BaseModel 并支持泛型
class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应格式

    用于返回列表数据的分页信息
    """
    # 状态码字段：默认 200
    code: int = 200
    # 响应消息字段：默认 "success"
    message: str = "success"
    # 数据列表字段：泛型类型的列表，默认为空列表
    data: list[T] = Field(default_factory=list)
    # 总记录数字段：默认 0
    total: int = 0
    # 当前页码字段：默认第 1 页
    page: int = 1
    # 每页大小字段：默认每页 20 条
    page_size: int = 20
    # 总页数字段：默认 0 页
    pages: int = 0

    # 内部配置类
    class Config:
        # 定义 JSON Schema 示例
        json_schema_extra = {
            "example": {  # 示例数据
                "code": 200,  # 成功状态码
                "message": "success",  # 成功消息
                "data": [],  # 空数据列表
                "total": 100,  # 总共 100 条记录
                "page": 1,  # 第 1 页
                "page_size": 20,  # 每页 20 条
                "pages": 5  # 总共 5 页
            }
        }


# 定义错误响应格式类
class ErrorResponse(BaseModel):
    """
    错误响应格式

    用于返回错误信息给客户端
    """
    # 错误状态码字段：必填，范围 400-599
    code: int = Field(..., ge=400, le=599, description="错误状态码")
    # 错误消息字段：必填，简短描述错误
    message: str = Field(..., description="错误消息")
    # 详细错误信息字段：可选，提供更多错误细节
    error: Optional[str] = Field(None, description="详细错误信息")
    # 请求路径字段：可选，记录发生错误的请求路径
    path: Optional[str] = Field(None, description="请求路径")

    # 内部配置类
    class Config:
        # 定义 JSON Schema 示例
        json_schema_extra = {
            "example": {  # 示例数据
                "code": 404,  # 资源未找到状态码
                "message": "Resource not found",  # 错误消息
                "error": "Case with id 999 not found",  # 详细错误
                "path": "/api/v1/cases/999"  # 请求路径
            }
        }
