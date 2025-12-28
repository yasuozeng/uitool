/**
 * 用例 API 接口测试
 * 测试所有用例相关的 HTTP 请求方法
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getCases,
  getCaseDetail,
  createCase,
  updateCase,
  deleteCase,
  batchDeleteCases,
  saveSteps,
  getActionTypes,
  getLocatorTypes,
  getPriorities
} from './case'
import type {
  CreateCaseRequest,
  UpdateCaseRequest,
  CreateStepRequest
} from './case'

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

describe('用例 API 接口', () => {
  beforeEach(() => {
    // 清除所有 mock 调用记录
    vi.clearAllMocks()
  })

  describe('getCases 方法', () => {
    it('应该调用 GET /cases 接口（无参数）', () => {
      mockRequest.get.mockResolvedValue({})

      getCases()

      expect(mockRequest.get).toHaveBeenCalledTimes(1)
      expect(mockRequest.get).toHaveBeenCalledWith('/cases', { params: {} })
    })

    it('应该传递查询参数', () => {
      mockRequest.get.mockResolvedValue({})

      const params = {
        name: '登录测试',
        priority: 'P0',
        tags: 'smoke',
        page: 1,
        page_size: 20
      }

      getCases(params)

      expect(mockRequest.get).toHaveBeenCalledWith('/cases', { params })
    })

    it('应该支持部分参数', () => {
      mockRequest.get.mockResolvedValue({})

      getCases({ name: '测试' })

      expect(mockRequest.get).toHaveBeenCalledWith('/cases', {
        params: { name: '测试' }
      })
    })
  })

  describe('getCaseDetail 方法', () => {
    it('应该调用 GET /cases/:id 接口', () => {
      mockRequest.get.mockResolvedValue({})

      getCaseDetail(1)

      expect(mockRequest.get).toHaveBeenCalledTimes(1)
      expect(mockRequest.get).toHaveBeenCalledWith('/cases/1')
    })

    it('应该支持不同的用例 ID', () => {
      mockRequest.get.mockResolvedValue({})

      getCaseDetail(999)

      expect(mockRequest.get).toHaveBeenCalledWith('/cases/999')
    })
  })

  describe('createCase 方法', () => {
    it('应该调用 POST /cases 接口', () => {
      mockRequest.post.mockResolvedValue({})

      const data: CreateCaseRequest = {
        name: '新用例',
        description: '测试描述',
        priority: 'P0',
        tags: 'smoke'
      }

      createCase(data)

      expect(mockRequest.post).toHaveBeenCalledTimes(1)
      expect(mockRequest.post).toHaveBeenCalledWith('/cases', data)
    })

    it('应该支持创建带步骤的用例', () => {
      mockRequest.post.mockResolvedValue({})

      const steps: CreateStepRequest[] = [
        {
          step_order: 1,
          action_type: 'navigate',
          element_locator: '',
          locator_type: '',
          action_params: '{"url": "https://example.com"}'
        },
        {
          step_order: 2,
          action_type: 'click',
          element_locator: '#submit',
          locator_type: 'css'
        }
      ]

      const data: CreateCaseRequest = {
        name: '带步骤的用例',
        steps
      }

      createCase(data)

      expect(mockRequest.post).toHaveBeenCalledWith('/cases', data)
    })

    it('应该支持最小化创建（只用例名）', () => {
      mockRequest.post.mockResolvedValue({})

      const data: CreateCaseRequest = {
        name: '最小用例'
      }

      createCase(data)

      expect(mockRequest.post).toHaveBeenCalledWith('/cases', data)
    })
  })

  describe('updateCase 方法', () => {
    it('应该调用 PUT /cases/:id 接口', () => {
      mockRequest.put.mockResolvedValue({})

      const data: UpdateCaseRequest = {
        name: '更新后的用例名'
      }

      updateCase(1, data)

      expect(mockRequest.put).toHaveBeenCalledTimes(1)
      expect(mockRequest.put).toHaveBeenCalledWith('/cases/1', data)
    })

    it('应该支持部分更新', () => {
      mockRequest.put.mockResolvedValue({})

      const data: UpdateCaseRequest = {
        priority: 'P1',
        tags: 'regression'
      }

      updateCase(5, data)

      expect(mockRequest.put).toHaveBeenCalledWith('/cases/5', data)
    })

    it('应该支持全量更新', () => {
      mockRequest.put.mockResolvedValue({})

      const data: UpdateCaseRequest = {
        name: '全量更新',
        description: '更新描述',
        priority: 'P0',
        tags: 'smoke,api'
      }

      updateCase(10, data)

      expect(mockRequest.put).toHaveBeenCalledWith('/cases/10', data)
    })
  })

  describe('deleteCase 方法', () => {
    it('应该调用 DELETE /cases/:id 接口', () => {
      mockRequest.delete.mockResolvedValue({})

      deleteCase(1)

      expect(mockRequest.delete).toHaveBeenCalledTimes(1)
      expect(mockRequest.delete).toHaveBeenCalledWith('/cases/1')
    })

    it('应该支持不同的用例 ID', () => {
      mockRequest.delete.mockResolvedValue({})

      deleteCase(999)

      expect(mockRequest.delete).toHaveBeenCalledWith('/cases/999')
    })
  })

  describe('batchDeleteCases 方法', () => {
    it('应该调用 DELETE /cases/batch 接口', () => {
      mockRequest.delete.mockResolvedValue({})

      const caseIds = [1, 2, 3, 4, 5]

      batchDeleteCases(caseIds)

      expect(mockRequest.delete).toHaveBeenCalledTimes(1)
      expect(mockRequest.delete).toHaveBeenCalledWith('/cases/batch', {
        data: { case_ids: caseIds }
      })
    })

    it('应该支持单个用例删除', () => {
      mockRequest.delete.mockResolvedValue({})

      batchDeleteCases([1])

      expect(mockRequest.delete).toHaveBeenCalledWith('/cases/batch', {
        data: { case_ids: [1] }
      })
    })

    it('应该支持空列表（虽然不推荐）', () => {
      mockRequest.delete.mockResolvedValue({})

      batchDeleteCases([])

      expect(mockRequest.delete).toHaveBeenCalledWith('/cases/batch', {
        data: { case_ids: [] }
      })
    })
  })

  describe('saveSteps 方法', () => {
    it('应该调用 PUT /cases/:id/steps 接口', () => {
      mockRequest.put.mockResolvedValue({})

      const steps: CreateStepRequest[] = [
        {
          step_order: 1,
          action_type: 'navigate',
          element_locator: '',
          locator_type: '',
          action_params: '{"url": "https://example.com"}'
        }
      ]

      saveSteps(1, steps)

      expect(mockRequest.put).toHaveBeenCalledTimes(1)
      expect(mockRequest.put).toHaveBeenCalledWith('/cases/1/steps', { steps })
    })

    it('应该支持保存多个步骤', () => {
      mockRequest.put.mockResolvedValue({})

      const steps: CreateStepRequest[] = [
        { step_order: 1, action_type: 'navigate', element_locator: '', locator_type: '' },
        { step_order: 2, action_type: 'click', element_locator: '#btn', locator_type: 'css' },
        { step_order: 3, action_type: 'input', element_locator: '#input', locator_type: 'css' }
      ]

      saveSteps(5, steps)

      expect(mockRequest.put).toHaveBeenCalledWith('/cases/5/steps', { steps })
    })

    it('应该支持清空步骤', () => {
      mockRequest.put.mockResolvedValue({})

      saveSteps(1, [])

      expect(mockRequest.put).toHaveBeenCalledWith('/cases/1/steps', { steps: [] })
    })
  })

  describe('getActionTypes 方法', () => {
    it('应该返回操作类型列表', () => {
      const actionTypes = getActionTypes()

      expect(Array.isArray(actionTypes)).toBe(true)
      expect(actionTypes.length).toBeGreaterThan(0)
    })

    it('应该包含所有必需的操作类型', () => {
      const actionTypes = getActionTypes()

      const typeValues = actionTypes.map(t => t.value)
      expect(typeValues).toContain('navigate')
      expect(typeValues).toContain('click')
      expect(typeValues).toContain('input')
      expect(typeValues).toContain('clear')
      expect(typeValues).toContain('wait')
      expect(typeValues).toContain('verify_text')
      expect(typeValues).toContain('verify_element')
    })

    it('每个操作类型应该有正确的结构', () => {
      const actionTypes = getActionTypes()

      actionTypes.forEach(type => {
        expect(type).toHaveProperty('value')
        expect(type).toHaveProperty('label')
        expect(type).toHaveProperty('params')
        expect(Array.isArray(type.params)).toBe(true)
      })
    })

    it('navigate 应该有必需的 url 参数', () => {
      const actionTypes = getActionTypes()
      const navigateType = actionTypes.find(t => t.value === 'navigate')

      expect(navigateType).toBeDefined()
      expect(navigateType?.params).toHaveLength(1)
      expect(navigateType?.params[0].key).toBe('url')
      expect(navigateType?.params[0].required).toBe(true)
    })

    it('click 应该没有参数', () => {
      const actionTypes = getActionTypes()
      const clickType = actionTypes.find(t => t.value === 'click')

      expect(clickType).toBeDefined()
      expect(clickType?.params).toHaveLength(0)
    })
  })

  describe('getLocatorTypes 方法', () => {
    it('应该返回定位类型列表', () => {
      const locatorTypes = getLocatorTypes()

      expect(Array.isArray(locatorTypes)).toBe(true)
      expect(locatorTypes.length).toBeGreaterThan(0)
    })

    it('应该包含所有常用的定位类型', () => {
      const locatorTypes = getLocatorTypes()

      const typeValues = locatorTypes.map(t => t.value)
      expect(typeValues).toContain('id')
      expect(typeValues).toContain('xpath')
      expect(typeValues).toContain('css')
      expect(typeValues).toContain('name')
      expect(typeValues).toContain('class')
    })

    it('每个定位类型应该有正确的结构', () => {
      const locatorTypes = getLocatorTypes()

      locatorTypes.forEach(type => {
        expect(type).toHaveProperty('value')
        expect(type).toHaveProperty('label')
        expect(type).toHaveProperty('placeholder')
      })
    })

    it('id 类型应该有正确的占位符', () => {
      const locatorTypes = getLocatorTypes()
      const idType = locatorTypes.find(t => t.value === 'id')

      expect(idType).toBeDefined()
      expect(idType?.placeholder).toBe('#username')
    })

    it('xpath 类型应该有正确的占位符', () => {
      const locatorTypes = getLocatorTypes()
      const xpathType = locatorTypes.find(t => t.value === 'xpath')

      expect(xpathType).toBeDefined()
      expect(xpathType?.placeholder).toContain('//')
    })
  })

  describe('getPriorities 方法', () => {
    it('应该返回优先级列表', () => {
      const priorities = getPriorities()

      expect(Array.isArray(priorities)).toBe(true)
      expect(priorities).toHaveLength(4)
    })

    it('应该包含所有 P0-P3 优先级', () => {
      const priorities = getPriorities()

      const values = priorities.map(p => p.value)
      expect(values).toEqual(['P0', 'P1', 'P2', 'P3'])
    })

    it('P0 应该是 danger 类型', () => {
      const priorities = getPriorities()
      const p0 = priorities.find(p => p.value === 'P0')

      expect(p0).toBeDefined()
      expect(p0?.type).toBe('danger')
      expect(p0?.label).toContain('核心功能')
    })

    it('P3 应该没有类型标签', () => {
      const priorities = getPriorities()
      const p3 = priorities.find(p => p.value === 'P3')

      expect(p3).toBeDefined()
      expect(p3?.type).toBe('')
      expect(p3?.label).toContain('边缘功能')
    })
  })
})
