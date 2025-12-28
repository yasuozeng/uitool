/**
 * 执行 API 接口测试
 * 测试所有执行相关的 HTTP 请求方法和 WebSocket 工具函数
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  createExecution,
  getExecution,
  getExecutionDetails,
  getExecutionList,
  cancelExecution,
  createWebSocket,
  getBrowserOptions,
  getWindowSizeOptions
} from './execution'
import type { CreateExecutionRequest, WSMessage } from './execution'

// Mock request 模块 - 使用工厂函数避免变量提升问题
vi.mock('./index', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

// 导入 mock 后的 request
import request from './index'
const mockRequest = request as any

describe('执行 API 接口', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('createExecution 方法', () => {
    it('应该调用 POST /executions 接口', () => {
      mockRequest.post.mockResolvedValue({})

      const data: CreateExecutionRequest = {
        case_ids: [1, 2, 3]
      }

      createExecution(data)

      expect(mockRequest.post).toHaveBeenCalledTimes(1)
      expect(mockRequest.post).toHaveBeenCalledWith('/executions', data)
    })

    it('应该支持指定浏览器类型', () => {
      mockRequest.post.mockResolvedValue({})

      const data: CreateExecutionRequest = {
        case_ids: [1],
        browser: 'firefox'
      }

      createExecution(data)

      expect(mockRequest.post).toHaveBeenCalledWith('/executions', data)
    })

    it('应该支持完整的执行配置', () => {
      mockRequest.post.mockResolvedValue({})

      const data: CreateExecutionRequest = {
        case_ids: [1, 2, 3, 4, 5],
        browser: 'chrome',
        headless: true,
        window_size: '1920x1080'
      }

      createExecution(data)

      expect(mockRequest.post).toHaveBeenCalledWith('/executions', data)
    })

    it('应该支持空用例列表（虽然不推荐）', () => {
      mockRequest.post.mockResolvedValue({})

      const data: CreateExecutionRequest = {
        case_ids: []
      }

      createExecution(data)

      expect(mockRequest.post).toHaveBeenCalledWith('/executions', data)
    })
  })

  describe('getExecution 方法', () => {
    it('应该调用 GET /executions/:id 接口', () => {
      mockRequest.get.mockResolvedValue({})

      getExecution(1)

      expect(mockRequest.get).toHaveBeenCalledTimes(1)
      expect(mockRequest.get).toHaveBeenCalledWith('/executions/1')
    })

    it('应该支持不同的执行 ID', () => {
      mockRequest.get.mockResolvedValue({})

      getExecution(999)

      expect(mockRequest.get).toHaveBeenCalledWith('/executions/999')
    })
  })

  describe('getExecutionDetails 方法', () => {
    it('应该调用 GET /executions/:id/details 接口', () => {
      mockRequest.get.mockResolvedValue({})

      getExecutionDetails(1)

      expect(mockRequest.get).toHaveBeenCalledTimes(1)
      expect(mockRequest.get).toHaveBeenCalledWith('/executions/1/details')
    })

    it('应该支持获取任何执行 ID 的详情', () => {
      mockRequest.get.mockResolvedValue({})

      getExecutionDetails(42)

      expect(mockRequest.get).toHaveBeenCalledWith('/executions/42/details')
    })
  })

  describe('getExecutionList 方法', () => {
    it('应该调用 GET /executions 接口（无参数）', () => {
      mockRequest.get.mockResolvedValue({})

      getExecutionList()

      expect(mockRequest.get).toHaveBeenCalledTimes(1)
      expect(mockRequest.get).toHaveBeenCalledWith('/executions', { params: {} })
    })

    it('应该传递分页参数', () => {
      mockRequest.get.mockResolvedValue({})

      const params = { page: 1, page_size: 20 }

      getExecutionList(params)

      expect(mockRequest.get).toHaveBeenCalledWith('/executions', { params })
    })

    it('应该支持只传 page 参数', () => {
      mockRequest.get.mockResolvedValue({})

      getExecutionList({ page: 2 })

      expect(mockRequest.get).toHaveBeenCalledWith('/executions', {
        params: { page: 2 }
      })
    })
  })

  describe('cancelExecution 方法', () => {
    it('应该调用 POST /executions/:id/cancel 接口', () => {
      mockRequest.post.mockResolvedValue({})

      cancelExecution(1)

      expect(mockRequest.post).toHaveBeenCalledTimes(1)
      expect(mockRequest.post).toHaveBeenCalledWith('/executions/1/cancel')
    })

    it('应该支持取消不同的执行任务', () => {
      mockRequest.post.mockResolvedValue({})

      cancelExecution(5)

      expect(mockRequest.post).toHaveBeenCalledWith('/executions/5/cancel')
    })
  })

  describe('createWebSocket 方法', () => {
    // Mock WebSocket
    class MockWebSocket {
      url = ''
      onopen: ((event: Event) => void) | null = null
      onmessage: ((event: MessageEvent) => void) | null = null
      onerror: ((event: Event) => void) | null = null
      onclose: ((event: CloseEvent) => void) | null = null

      constructor(url: string) {
        this.url = url
      }

      // 模拟发送消息
      send(data: string) {
        // Mock implementation
      }

      // 模拟关闭连接
      close() {
        if (this.onclose) {
          this.onclose(new CloseEvent('close'))
        }
      }
    }

    // 全局 WebSocket mock
    global.WebSocket = MockWebSocket as any

    // 保存原始 location
    const originalLocation = global.location

    beforeEach(() => {
      // Mock location
      Object.defineProperty(global, 'location', {
        value: {
          protocol: 'http:',
          host: 'localhost:5173'
        },
        writable: true,
        configurable: true
      })
    })

    afterEach(() => {
      // 恢复原始 location
      Object.defineProperty(global, 'location', {
        value: originalLocation,
        writable: true,
        configurable: true
      })
    })

    it('应该创建 WebSocket 连接', () => {
      const onMessage = vi.fn()

      const ws = createWebSocket(1, onMessage)

      expect(ws).toBeInstanceOf(MockWebSocket)
      expect(ws.url).toBe('ws://localhost:5173/api/v1/ws/executions/1')
    })

    it('应该在 HTTPS 环境使用 WSS 协议', () => {
      const onMessage = vi.fn()

      // 模拟 HTTPS 环境
      Object.defineProperty(global, 'location', {
        value: {
          protocol: 'https:',
          host: 'example.com'
        },
        writable: true,
        configurable: true
      })

      const ws = createWebSocket(5, onMessage)

      expect(ws.url).toBe('wss://example.com/api/v1/ws/executions/5')
    })

    it('应该设置 onopen 回调', () => {
      const onMessage = vi.fn()

      const ws = createWebSocket(1, onMessage)

      expect(ws.onopen).toBeTypeOf('function')
    })

    it('应该设置 onmessage 回调并解析 JSON', () => {
      const onMessage = vi.fn()

      const ws = createWebSocket(1, onMessage)

      // 触发 onmessage
      const mockMessage: WSMessage = {
        type: 'step_success',
        timestamp: '2025-12-27T10:00:00',
        case_id: 1,
        case_name: '测试用例',
        step_order: 1,
        message: '步骤执行成功',
        level: 'success'
      }

      if (ws.onmessage) {
        ws.onmessage(new MessageEvent('message', {
          data: JSON.stringify(mockMessage)
        }))
      }

      expect(onMessage).toHaveBeenCalledWith(mockMessage)
    })

    it('应该处理 JSON 解析错误', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const onMessage = vi.fn()

      const ws = createWebSocket(1, onMessage)

      // 触发无效的 JSON
      if (ws.onmessage) {
        ws.onmessage(new MessageEvent('message', {
          data: 'invalid json'
        }))
      }

      expect(consoleSpy).toHaveBeenCalled()
      expect(onMessage).not.toHaveBeenCalled()

      consoleSpy.mockRestore()
    })

    it('应该设置 onerror 回调', () => {
      const onMessage = vi.fn()

      const ws = createWebSocket(1, onMessage)

      expect(ws.onerror).toBeTypeOf('function')
    })

    it('应该设置 onclose 回调', () => {
      const onMessage = vi.fn()

      const ws = createWebSocket(1, onMessage)

      expect(ws.onclose).toBeTypeOf('function')
    })

    it('应该返回 WebSocket 实例', () => {
      const onMessage = vi.fn()

      const ws = createWebSocket(1, onMessage)

      expect(ws).toBeDefined()
      expect(typeof ws.send).toBe('function')
      expect(typeof ws.close).toBe('function')
    })
  })

  describe('getBrowserOptions 方法', () => {
    it('应该返回浏览器选项列表', () => {
      const options = getBrowserOptions()

      expect(Array.isArray(options)).toBe(true)
      expect(options.length).toBe(3)
    })

    it('应该包含 Chrome、Firefox、Edge', () => {
      const options = getBrowserOptions()

      const values = options.map(o => o.value)
      expect(values).toContain('chrome')
      expect(values).toContain('firefox')
      expect(values).toContain('edge')
    })

    it('每个选项应该有正确的结构', () => {
      const options = getBrowserOptions()

      options.forEach(option => {
        expect(option).toHaveProperty('value')
        expect(option).toHaveProperty('label')
        expect(option).toHaveProperty('icon')
      })
    })

    it('Chrome 应该有正确的 icon', () => {
      const options = getBrowserOptions()
      const chrome = options.find(o => o.value === 'chrome')

      expect(chrome).toBeDefined()
      expect(chrome?.icon).toBe('chrome')
      expect(chrome?.label).toBe('Chrome')
    })
  })

  describe('getWindowSizeOptions 方法', () => {
    it('应该返回窗口大小选项列表', () => {
      const options = getWindowSizeOptions()

      expect(Array.isArray(options)).toBe(true)
      expect(options.length).toBeGreaterThan(0)
    })

    it('应该包含常用的分辨率', () => {
      const options = getWindowSizeOptions()

      const values = options.map(o => o.value)
      expect(values).toContain('1920x1080')
      expect(values).toContain('1366x768')
      expect(values).toContain('1280x720')
    })

    it('应该包含移动设备分辨率', () => {
      const options = getWindowSizeOptions()

      const values = options.map(o => o.value)
      expect(values).toContain('375x667') // Mobile Portrait
      expect(values).toContain('667x375') // Mobile Landscape
    })

    it('每个选项应该有描述性的标签', () => {
      const options = getWindowSizeOptions()

      options.forEach(option => {
        expect(option).toHaveProperty('value')
        expect(option).toHaveProperty('label')
        expect(option.label.length).toBeGreaterThan(0)
      })
    })

    it('Desktop 分辨率应该有正确标记', () => {
      const options = getWindowSizeOptions()
      const desktop = options.find(o => o.value === '1920x1080')

      expect(desktop).toBeDefined()
      expect(desktop?.label).toContain('Desktop')
    })

    it('Mobile 分辨率应该有正确标记', () => {
      const options = getWindowSizeOptions()
      const mobile = options.find(o => o.value === '375x667')

      expect(mobile).toBeDefined()
      expect(mobile?.label).toContain('Mobile')
      expect(mobile?.label).toContain('Portrait')
    })
  })
})
