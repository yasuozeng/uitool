/**
 * 执行状态管理测试
 * 测试 useExecutionStore 的所有方法和计算属性
 */
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useExecutionStore } from './execution'
import type { Execution, ExecutionLog } from './execution'

// Mock WebSocket 类
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.OPEN
  url = ''
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null

  constructor(url: string) {
    this.url = url
  }

  send(data: string) {
    // Mock send method
  }

  close() {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close'))
    }
  }
}

// 全局 WebSocket mock
global.WebSocket = MockWebSocket as any

describe('useExecutionStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const store = useExecutionStore()

      // 验证初始状态
      expect(store.executions).toEqual([])
      expect(store.currentExecution).toBeNull()
      expect(store.logs).toEqual([])
      expect(store.wsStatus).toBe('disconnected')
      expect(store.wsConnection).toBeNull()
      expect(store.loading).toBe(false)
    })

    it('计算属性应该返回初始值', () => {
      const store = useExecutionStore()

      expect(store.progress).toBe(0)
      expect(store.passRate).toBe(0)
      expect(store.isCompleted).toBe(false)
    })
  })

  describe('setExecutions 方法', () => {
    it('应该设置执行列表', () => {
      const store = useExecutionStore()
      const mockExecutions: Execution[] = [
        {
          id: 1,
          status: 'completed',
          browser: 'chromium',
          headless: true,
          window_size: '1920x1080',
          total_cases: 2,
          passed_cases: 2,
          failed_cases: 0,
          started_at: '2025-12-27T10:00:00',
          completed_at: '2025-12-27T10:05:00',
          duration: 300000
        },
        {
          id: 2,
          status: 'running',
          browser: 'firefox',
          headless: false,
          window_size: '1920x1080',
          total_cases: 5,
          passed_cases: 3,
          failed_cases: 1,
          started_at: '2025-12-27T11:00:00'
        }
      ]

      store.setExecutions(mockExecutions)

      expect(store.executions).toHaveLength(2)
      expect(store.executions[0].browser).toBe('chromium')
      expect(store.executions[1].status).toBe('running')
    })
  })

  describe('setCurrentExecution 方法', () => {
    it('应该设置当前执行', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'running',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 5,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00'
      }

      store.setCurrentExecution(mockExecution)

      expect(store.currentExecution).toEqual(mockExecution)
      expect(store.currentExecution?.id).toBe(1)
    })

    it('应该可以清除当前执行', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'running',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 5,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00'
      }

      store.setCurrentExecution(mockExecution)
      expect(store.currentExecution).not.toBeNull()

      store.setCurrentExecution(null)
      expect(store.currentExecution).toBeNull()
    })
  })

  describe('addExecution 方法', () => {
    it('应该在列表开头添加新执行', () => {
      const store = useExecutionStore()
      const existingExecution: Execution = {
        id: 1,
        status: 'completed',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 2,
        passed_cases: 2,
        failed_cases: 0,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:05:00',
        duration: 300000
      }

      store.setExecutions([existingExecution])

      const newExecution: Execution = {
        id: 2,
        status: 'running',
        browser: 'firefox',
        headless: false,
        window_size: '1920x1080',
        total_cases: 5,
        passed_cases: 3,
        failed_cases: 1,
        started_at: '2025-12-27T11:00:00'
      }

      store.addExecution(newExecution)

      expect(store.executions).toHaveLength(2)
      expect(store.executions[0].id).toBe(2)
      expect(store.executions[1].id).toBe(1)
    })
  })

  describe('updateExecution 方法', () => {
    it('应该更新列表中的执行', () => {
      const store = useExecutionStore()
      const originalExecution: Execution = {
        id: 1,
        status: 'running',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 5,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00'
      }

      store.setExecutions([originalExecution])

      const updatedExecution: Execution = {
        id: 1,
        status: 'completed',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 8,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:10:00',
        duration: 600000
      }

      store.updateExecution(updatedExecution)

      expect(store.executions).toHaveLength(1)
      expect(store.executions[0].status).toBe('completed')
      expect(store.executions[0].passed_cases).toBe(8)
    })

    it('如果更新的是当前执行，应该同时更新当前执行', () => {
      const store = useExecutionStore()
      const originalExecution: Execution = {
        id: 1,
        status: 'running',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 5,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00'
      }

      store.setCurrentExecution(originalExecution)

      const updatedExecution: Execution = {
        id: 1,
        status: 'completed',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 10,
        failed_cases: 0,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:10:00',
        duration: 600000
      }

      store.updateExecution(updatedExecution)

      expect(store.currentExecution?.status).toBe('completed')
      expect(store.currentExecution?.passed_cases).toBe(10)
    })

    it('更新不存在的执行不应该改变列表', () => {
      const store = useExecutionStore()
      const existingExecution: Execution = {
        id: 1,
        status: 'running',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 5,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00'
      }

      store.setExecutions([existingExecution])

      const nonExistentExecution: Execution = {
        id: 999,
        status: 'completed',
        browser: 'firefox',
        headless: false,
        window_size: '1920x1080',
        total_cases: 5,
        passed_cases: 5,
        failed_cases: 0,
        started_at: '2025-12-27T11:00:00',
        completed_at: '2025-12-27T11:05:00',
        duration: 300000
      }

      store.updateExecution(nonExistentExecution)

      expect(store.executions).toHaveLength(1)
      expect(store.executions[0].id).toBe(1)
    })
  })

  describe('addLog 方法', () => {
    it('应该添加日志到列表', () => {
      const store = useExecutionStore()
      const log1: ExecutionLog = {
        id: '1',
        timestamp: '2025-12-27T10:00:00',
        level: 'info',
        message: '开始执行'
      }

      store.addLog(log1)

      expect(store.logs).toHaveLength(1)
      expect(store.logs[0]).toEqual(log1)

      const log2: ExecutionLog = {
        id: '2',
        timestamp: '2025-12-27T10:00:01',
        level: 'success',
        message: '步骤执行成功'
      }

      store.addLog(log2)

      expect(store.logs).toHaveLength(2)
      expect(store.logs[1].level).toBe('success')
    })
  })

  describe('clearLogs 方法', () => {
    it('应该清空日志列表', () => {
      const store = useExecutionStore()

      // 添加多条日志
      for (let i = 1; i <= 5; i++) {
        store.addLog({
          id: String(i),
          timestamp: '2025-12-27T10:00:00',
          level: 'info',
          message: `日志${i}`
        })
      }

      expect(store.logs).toHaveLength(5)

      store.clearLogs()

      expect(store.logs).toEqual([])
    })
  })

  describe('setWsStatus 方法', () => {
    it('应该设置 WebSocket 状态', () => {
      const store = useExecutionStore()

      expect(store.wsStatus).toBe('disconnected')

      store.setWsStatus('connecting')
      expect(store.wsStatus).toBe('connecting')

      store.setWsStatus('connected')
      expect(store.wsStatus).toBe('connected')

      store.setWsStatus('error')
      expect(store.wsStatus).toBe('error')
    })
  })

  describe('setWsConnection 方法', () => {
    it('应该设置 WebSocket 连接', () => {
      const store = useExecutionStore()
      const mockWs = new MockWebSocket('ws://localhost:8000/ws')

      store.setWsConnection(mockWs)

      // 使用 toStrictEqual 因为 ref 可能创建了新引用
      expect(store.wsConnection).toStrictEqual(mockWs)
      expect(store.wsConnection).not.toBeNull()
    })

    it('应该可以清除 WebSocket 连接', () => {
      const store = useExecutionStore()
      const mockWs = new MockWebSocket('ws://localhost:8000/ws')

      store.setWsConnection(mockWs)
      expect(store.wsConnection).not.toBeNull()

      store.setWsConnection(null)
      expect(store.wsConnection).toBeNull()
    })
  })

  describe('closeWsConnection 方法', () => {
    it('应该关闭 WebSocket 连接', () => {
      const store = useExecutionStore()
      const mockWs = new MockWebSocket('ws://localhost:8000/ws')

      store.setWsConnection(mockWs)
      store.setWsStatus('connected')

      expect(store.wsConnection).not.toBeNull()
      expect(store.wsStatus).toBe('connected')

      store.closeWsConnection()

      expect(store.wsConnection).toBeNull()
      expect(store.wsStatus).toBe('disconnected')
    })

    it('没有连接时调用不应该报错', () => {
      const store = useExecutionStore()

      expect(() => store.closeWsConnection()).not.toThrow()
      expect(store.wsConnection).toBeNull()
      expect(store.wsStatus).toBe('disconnected')
    })
  })

  describe('setLoading 方法', () => {
    it('应该设置加载状态', () => {
      const store = useExecutionStore()

      expect(store.loading).toBe(false)

      store.setLoading(true)
      expect(store.loading).toBe(true)

      store.setLoading(false)
      expect(store.loading).toBe(false)
    })
  })

  describe('progress 计算属性', () => {
    it('应该正确计算执行进度', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'running',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 3,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00'
      }

      store.setCurrentExecution(mockExecution)

      expect(store.progress).toBe(50) // (3 + 2) / 10 * 100
    })

    it('全部完成应该返回 100', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'completed',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 8,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:10:00',
        duration: 600000
      }

      store.setCurrentExecution(mockExecution)

      expect(store.progress).toBe(100)
    })

    it('没有当前执行应该返回 0', () => {
      const store = useExecutionStore()

      expect(store.progress).toBe(0)
    })

    it('总用例数为 0 应该返回 0', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'pending',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 0,
        passed_cases: 0,
        failed_cases: 0,
        started_at: '2025-12-27T10:00:00'
      }

      store.setCurrentExecution(mockExecution)

      expect(store.progress).toBe(0)
    })
  })

  describe('passRate 计算属性', () => {
    it('应该正确计算通过率', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'running',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 8,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00'
      }

      store.setCurrentExecution(mockExecution)

      expect(store.passRate).toBe(80) // 8 / 10 * 100
    })

    it('全部通过应该返回 100', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'completed',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 5,
        passed_cases: 5,
        failed_cases: 0,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:05:00',
        duration: 300000
      }

      store.setCurrentExecution(mockExecution)

      expect(store.passRate).toBe(100)
    })

    it('全部失败应该返回 0', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'failed',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 0,
        failed_cases: 10,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:10:00',
        duration: 600000
      }

      store.setCurrentExecution(mockExecution)

      expect(store.passRate).toBe(0)
    })

    it('没有当前执行应该返回 0', () => {
      const store = useExecutionStore()

      expect(store.passRate).toBe(0)
    })
  })

  describe('isCompleted 计算属性', () => {
    it('completed 状态应该返回 true', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'completed',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 5,
        passed_cases: 5,
        failed_cases: 0,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:05:00',
        duration: 300000
      }

      store.setCurrentExecution(mockExecution)

      expect(store.isCompleted).toBe(true)
    })

    it('failed 状态应该返回 true', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'failed',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 5,
        failed_cases: 5,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:05:00',
        duration: 300000
      }

      store.setCurrentExecution(mockExecution)

      expect(store.isCompleted).toBe(true)
    })

    it('cancelled 状态应该返回 true', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'cancelled',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 3,
        failed_cases: 0,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:02:00',
        duration: 120000
      }

      store.setCurrentExecution(mockExecution)

      expect(store.isCompleted).toBe(true)
    })

    it('running 状态应该返回 false', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'running',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 5,
        failed_cases: 2,
        started_at: '2025-12-27T10:00:00'
      }

      store.setCurrentExecution(mockExecution)

      expect(store.isCompleted).toBe(false)
    })

    it('pending 状态应该返回 false', () => {
      const store = useExecutionStore()
      const mockExecution: Execution = {
        id: 1,
        status: 'pending',
        browser: 'chromium',
        headless: true,
        window_size: '1920x1080',
        total_cases: 10,
        passed_cases: 0,
        failed_cases: 0,
        started_at: '2025-12-27T10:00:00'
      }

      store.setCurrentExecution(mockExecution)

      expect(store.isCompleted).toBe(false)
    })

    it('没有当前执行应该返回 false', () => {
      const store = useExecutionStore()

      expect(store.isCompleted).toBe(false)
    })
  })
})
