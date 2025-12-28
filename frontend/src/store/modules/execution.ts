/**
 * 执行状态管理
 * 管理执行任务列表、当前执行、实时日志等
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 执行状态枚举
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

// 日志类型
export type LogLevel = 'info' | 'success' | 'error' | 'warning'

// 执行日志接口
export interface ExecutionLog {
  id: string
  timestamp: string
  level: LogLevel
  message: string
  case_id?: number
  case_name?: string
  step_order?: number
  screenshot_path?: string
}

// 执行详情接口
export interface ExecutionDetail {
  id: number
  execution_id: number
  case_id: number
  case_name: string
  status: ExecutionStatus
  error_message?: string
  screenshot_path?: string
  step_count: number
  passed_steps: number
  failed_steps: number
  started_at?: string
  completed_at?: string
}

// 执行任务接口
export interface Execution {
  id: number
  status: ExecutionStatus
  browser: string
  headless: boolean
  window_size: string
  total_cases: number
  passed_cases: number
  failed_cases: number
  started_at: string
  completed_at?: string
  duration?: number
  details?: ExecutionDetail[]
}

// WebSocket 连接状态
type WSStatus = 'disconnected' | 'connecting' | 'connected' | 'error'

export const useExecutionStore = defineStore('execution', () => {
  // ========== 状态 ==========
  // 执行列表
  const executions = ref<Execution[]>([])
  // 当前执行
  const currentExecution = ref<Execution | null>(null)
  // 实时日志列表
  const logs = ref<ExecutionLog[]>([])
  // WebSocket 连接状态
  const wsStatus = ref<WSStatus>('disconnected')
  // WebSocket 实例
  const wsConnection = ref<WebSocket | null>(null)
  // 加载状态
  const loading = ref(false)

  // ========== 计算属性 ==========
  // 当前执行的进度百分比
  const progress = computed(() => {
    if (!currentExecution.value) return 0
    const { total_cases, passed_cases, failed_cases } = currentExecution.value
    if (total_cases === 0) return 0
    return Math.round(((passed_cases + failed_cases) / total_cases) * 100)
  })

  // 通过率
  const passRate = computed(() => {
    if (!currentExecution.value) return 0
    const { total_cases, passed_cases } = currentExecution.value
    if (total_cases === 0) return 0
    return Math.round((passed_cases / total_cases) * 100)
  })

  // 当前执行是否已完成
  const isCompleted = computed(() => {
    if (!currentExecution.value) return false
    return ['completed', 'failed', 'cancelled'].includes(currentExecution.value.status)
  })

  // ========== 操作方法 ==========
  // 设置执行列表
  const setExecutions = (data: Execution[]) => {
    executions.value = data
  }

  // 设置当前执行
  const setCurrentExecution = (data: Execution | null) => {
    currentExecution.value = data
  }

  // 添加执行到列表
  const addExecution = (data: Execution) => {
    executions.value.unshift(data)
  }

  // 更新列表中的执行
  const updateExecution = (data: Execution) => {
    const index = executions.value.findIndex(e => e.id === data.id)
    if (index !== -1) {
      executions.value[index] = data
    }
    // 如果是当前执行，也更新当前执行
    if (currentExecution.value?.id === data.id) {
      currentExecution.value = data
    }
  }

  // 添加日志
  const addLog = (log: ExecutionLog) => {
    logs.value.push(log)
  }

  // 清空日志
  const clearLogs = () => {
    logs.value = []
  }

  // 设置 WebSocket 状态
  const setWsStatus = (status: WSStatus) => {
    wsStatus.value = status
  }

  // 设置 WebSocket 连接
  const setWsConnection = (ws: WebSocket | null) => {
    wsConnection.value = ws
  }

  // 关闭 WebSocket 连接
  const closeWsConnection = () => {
    if (wsConnection.value) {
      wsConnection.value.close()
      wsConnection.value = null
    }
    wsStatus.value = 'disconnected'
  }

  // 设置加载状态
  const setLoading = (state: boolean) => {
    loading.value = state
  }

  return {
    // 状态
    executions,
    currentExecution,
    logs,
    wsStatus,
    wsConnection,
    loading,
    // 计算属性
    progress,
    passRate,
    isCompleted,
    // 方法
    setExecutions,
    setCurrentExecution,
    addExecution,
    updateExecution,
    addLog,
    clearLogs,
    setWsStatus,
    setWsConnection,
    closeWsConnection,
    setLoading
  }
})
