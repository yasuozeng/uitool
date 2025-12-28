/**
 * 执行 API 接口封装
 * 提供所有执行相关的 HTTP 请求方法
 */
import request from './index'
import type { Execution, ExecutionDetail } from '@/store/modules/execution'

// ========== 类型定义 ==========

// 创建执行请求
export interface CreateExecutionRequest {
  execution_type: 'single' | 'batch'  // 执行类型：single 单个用例或 batch 批量用例
  case_ids: number[]
  browser?: 'chrome' | 'firefox' | 'edge'
  headless?: boolean
  window_size?: string
}

// 统一响应格式
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// ========== API 方法 ==========

/**
 * 创建执行任务
 */
export const createExecution = (data: CreateExecutionRequest) => {
  return request.post<any, ApiResponse<Execution>>('/executions', data)
}

/**
 * 获取执行状态
 */
export const getExecution = (id: number) => {
  return request.get<any, ApiResponse<Execution>>(`/executions/${id}`)
}

/**
 * 获取执行详情（包含所有用例的执行结果）
 */
export const getExecutionDetails = (id: number) => {
  return request.get<any, ApiResponse<ExecutionDetail[]>>(`/executions/${id}/details`)
}

/**
 * 获取执行历史列表
 */
export const getExecutionList = (params: { page?: number; page_size?: number } = {}) => {
  return request.get<any, any>('/executions', { params })
}

/**
 * 启动执行任务
 * @param id 执行 ID
 */
export const startExecution = (id: number) => {
  return request.post<any, ApiResponse<Execution>>(`/executions/${id}/start`)
}

/**
 * 停止执行
 */
export const stopExecution = (id: number) => {
  return request.post<any, ApiResponse<null>>(`/executions/${id}/stop`)
}

/**
 * 生成HTML测试报告
 * @param id 执行 ID
 */
export const generateHtmlReport = (id: number) => {
  return request.get<any, ApiResponse<string>>(`/executions/${id}/report`)
}

/**
 * 导出类型定义（供其他模块使用）
 */
export type { Execution, ExecutionDetail } from '@/store/modules/execution'

// ========== 辅助函数 ==========

/**
 * 获取浏览器选项
 */
export const getBrowserOptions = () => {
  return [
    { value: 'chrome', label: 'Chrome', icon: 'chrome' },
    { value: 'firefox', label: 'Firefox', icon: 'firefox' },
    { value: 'edge', label: 'Edge', icon: 'edge' }
  ]
}

/**
 * 获取窗口大小选项
 */
export const getWindowSizeOptions = () => {
  return [
    { value: '1920x1080', label: '1920x1080 (Desktop)' },
    { value: '1366x768', label: '1366x768 (Laptop)' },
    { value: '1280x720', label: '1280x720 (HD)' },
    { value: '768x1024', label: '768x1024 (Tablet Portrait)' },
    { value: '1024x768', label: '1024x768 (Tablet Landscape)' },
    { value: '375x667', label: '375x667 (Mobile Portrait)' },
    { value: '667x375', label: '667x375 (Mobile Landscape)' }
  ]
}
