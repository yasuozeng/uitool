/**
 * 用例 API 接口封装
 * 提供所有用例相关的 HTTP 请求方法
 */
import request from './index'
import type {
  TestCase,
  TestStep,
  CaseFilters,
  Pagination
} from '@/store/modules/case'

// ========== 类型定义 ==========

// 创建用例请求
export interface CreateCaseRequest {
  name: string
  description?: string
  priority?: string
  tags?: string
  steps?: CreateStepRequest[]
}

// 创建步骤请求
export interface CreateStepRequest {
  step_order: number
  action_type: string
  element_locator: string
  locator_type: string
  action_params?: string
  expected_result?: string
  description?: string
}

// 更新用例请求
export interface UpdateCaseRequest {
  name?: string
  description?: string
  priority?: string
  tags?: string
}

// 批量删除请求
export interface BatchDeleteRequest {
  case_ids: number[]
}

// 分页请求参数
export interface GetCasesParams {
  name?: string
  priority?: string
  tags?: string
  page?: number
  page_size?: number
}

// 分页响应
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// 统一响应格式
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// ========== API 方法 ==========

/**
 * 获取用例列表（分页）
 */
export const getCases = (params: GetCasesParams = {}) => {
  return request.get<any, PaginatedResponse<TestCase>>('/cases', { params })
}

/**
 * 获取用例详情
 */
export const getCaseDetail = (id: number) => {
  return request.get<any, ApiResponse<TestCase>>(`/cases/${id}`)
}

/**
 * 创建测试用例
 */
export const createCase = (data: CreateCaseRequest) => {
  return request.post<any, ApiResponse<TestCase>>('/cases', data)
}

/**
 * 更新测试用例
 */
export const updateCase = (id: number, data: UpdateCaseRequest) => {
  return request.put<any, ApiResponse<TestCase>>(`/cases/${id}`, data)
}

/**
 * 删除测试用例
 */
export const deleteCase = (id: number) => {
  return request.delete<any, ApiResponse<null>>(`/cases/${id}`)
}

/**
 * 批量删除测试用例
 */
export const batchDeleteCases = (caseIds: number[]) => {
  return request.delete<any, ApiResponse<{ deleted: number }>>('/cases/batch', {
    data: { case_ids: caseIds }
  })
}

/**
 * 保存用例步骤
 */
export const saveSteps = (caseId: number, steps: CreateStepRequest[]) => {
  return request.put<any, ApiResponse<TestCase>>(`/cases/${caseId}/steps`, {
    steps
  })
}

/**
 * 获取操作类型列表（前端常量，无需后端接口）
 */
export const getActionTypes = () => {
  return [
    { value: 'navigate', label: '页面跳转', params: [{ key: 'url', label: 'URL', required: true }] },
    { value: 'click', label: '点击元素', params: [] },
    { value: 'input', label: '输入文本', params: [{ key: 'text', label: '输入内容', required: true }] },
    { value: 'clear', label: '清空输入', params: [] },
    { value: 'wait', label: '等待元素', params: [{ key: 'timeout', label: '超时时间(ms)', required: false, default: 5000 }] },
    { value: 'verify_text', label: '验证文本', params: [{ key: 'text', label: '期望文本', required: true }] },
    { value: 'verify_element', label: '验证元素', params: [] },
    { value: 'select', label: '下拉选择', params: [{ key: 'value', label: '选项值', required: true }] },
    { value: 'hover', label: '鼠标悬停', params: [] },
    { value: 'scroll', label: '滚动到元素', params: [] },
    { value: 'screenshot', label: '截图', params: [] }
  ]
}

/**
 * 获取定位类型列表（前端常量，无需后端接口）
 */
export const getLocatorTypes = () => {
  return [
    { value: 'id', label: 'ID', placeholder: '#username' },
    { value: 'xpath', label: 'XPath', placeholder: '//input[@id="username"]' },
    { value: 'css', label: 'CSS Selector', placeholder: 'input#username' },
    { value: 'name', label: 'Name', placeholder: '[name="username"]' },
    { value: 'class', label: 'Class', placeholder: '.form-control' },
    { value: 'text', label: '文本', placeholder: '文本内容' },
    { value: 'data-testid', label: 'Data Test ID', placeholder: '[data-testid="submit"]' }
  ]
}

/**
 * 获取优先级列表（前端常量，无需后端接口）
 */
export const getPriorities = () => {
  return [
    { value: 'P0', label: 'P0 - 核心功能', type: 'danger' },
    { value: 'P1', label: 'P1 - 重要功能', type: 'warning' },
    { value: 'P2', label: 'P2 - 一般功能', type: 'info' },
    { value: 'P3', label: 'P3 - 边缘功能', type: '' }
  ]
}
