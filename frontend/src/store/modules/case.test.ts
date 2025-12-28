/**
 * 用例状态管理测试
 * 测试 useCaseStore 的所有方法和计算属性
 */
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach } from 'vitest'
import { useCaseStore } from './case'
import type { TestCase, CaseFilters } from './case'

describe('useCaseStore', () => {
  // 在每个测试前创建新的 Pinia 实例
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const store = useCaseStore()

      // 验证初始状态
      expect(store.cases).toEqual([])
      expect(store.currentCase).toBeNull()
      expect(store.filters).toEqual({})
      expect(store.pagination).toEqual({
        page: 1,
        page_size: 20,
        total: 0,
        pages: 0
      })
      expect(store.loading).toBe(false)
    })

    it('priorityStats 计算属性应该返回初始值', () => {
      const store = useCaseStore()

      expect(store.priorityStats).toEqual({ P0: 0, P1: 0, P2: 0, P3: 0 })
    })
  })

  describe('setCases 方法', () => {
    it('应该设置用例列表', () => {
      const store = useCaseStore()
      const mockCases: TestCase[] = [
        {
          id: 1,
          name: '测试用例1',
          description: '描述1',
          priority: 'P0',
          tags: 'smoke',
          step_count: 3,
          created_at: '2025-12-27',
          updated_at: '2025-12-27'
        },
        {
          id: 2,
          name: '测试用例2',
          description: '描述2',
          priority: 'P1',
          tags: 'regression',
          step_count: 5,
          created_at: '2025-12-27',
          updated_at: '2025-12-27'
        }
      ]

      store.setCases(mockCases)

      expect(store.cases).toHaveLength(2)
      expect(store.cases[0].name).toBe('测试用例1')
      expect(store.cases[1].priority).toBe('P1')
    })
  })

  describe('setCurrentCase 方法', () => {
    it('应该设置当前用例', () => {
      const store = useCaseStore()
      const mockCase: TestCase = {
        id: 1,
        name: '当前用例',
        description: '测试',
        priority: 'P0',
        tags: 'smoke',
        step_count: 1,
        created_at: '2025-12-27',
        updated_at: '2025-12-27'
      }

      store.setCurrentCase(mockCase)

      expect(store.currentCase).toEqual(mockCase)
      expect(store.currentCase?.name).toBe('当前用例')
    })

    it('应该可以清除当前用例', () => {
      const store = useCaseStore()
      const mockCase: TestCase = {
        id: 1,
        name: '测试',
        description: '测试',
        priority: 'P0',
        tags: 'smoke',
        step_count: 1,
        created_at: '2025-12-27',
        updated_at: '2025-12-27'
      }

      store.setCurrentCase(mockCase)
      expect(store.currentCase).not.toBeNull()

      store.setCurrentCase(null)
      expect(store.currentCase).toBeNull()
    })
  })

  describe('setFilters 方法', () => {
    it('应该更新筛选条件', () => {
      const store = useCaseStore()

      store.setFilters({ name: '登录测试' })
      expect(store.filters).toEqual({ name: '登录测试' })

      store.setFilters({ priority: 'P0' })
      expect(store.filters).toEqual({ name: '登录测试', priority: 'P0' })

      store.setFilters({ name: '注册测试' })
      expect(store.filters).toEqual({ name: '注册测试', priority: 'P0' })
    })

    it('应该合并多个筛选条件', () => {
      const store = useCaseStore()

      store.setFilters({ name: '测试', priority: 'P1', tags: 'smoke' })

      expect(store.filters).toEqual({
        name: '测试',
        priority: 'P1',
        tags: 'smoke'
      })
    })
  })

  describe('resetFilters 方法', () => {
    it('应该重置筛选条件', () => {
      const store = useCaseStore()

      // 设置筛选条件
      store.setFilters({ name: '测试', priority: 'P0' })
      store.setPagination({ page: 5 })

      expect(store.filters).toEqual({ name: '测试', priority: 'P0' })
      expect(store.pagination.page).toBe(5)

      // 重置
      store.resetFilters()

      expect(store.filters).toEqual({})
      expect(store.pagination.page).toBe(1)
    })
  })

  describe('setPagination 方法', () => {
    it('应该更新分页信息', () => {
      const store = useCaseStore()

      store.setPagination({ page: 2 })
      expect(store.pagination.page).toBe(2)
      expect(store.pagination.page_size).toBe(20) // 保持默认值

      store.setPagination({ total: 100 })
      expect(store.pagination.total).toBe(100)
      expect(store.pagination.page).toBe(2) // 保持之前设置的值
    })

    it('应该合并多个分页参数', () => {
      const store = useCaseStore()

      store.setPagination({ page: 3, page_size: 50, total: 150, pages: 3 })

      expect(store.pagination).toEqual({
        page: 3,
        page_size: 50,
        total: 150,
        pages: 3
      })
    })
  })

  describe('setLoading 方法', () => {
    it('应该设置加载状态', () => {
      const store = useCaseStore()

      expect(store.loading).toBe(false)

      store.setLoading(true)
      expect(store.loading).toBe(true)

      store.setLoading(false)
      expect(store.loading).toBe(false)
    })
  })

  describe('addCase 方法', () => {
    it('应该在列表开头添加新用例', () => {
      const store = useCaseStore()
      const existingCase: TestCase = {
        id: 1,
        name: '已存在用例',
        description: '描述',
        priority: 'P1',
        tags: 'smoke',
        step_count: 2,
        created_at: '2025-12-27',
        updated_at: '2025-12-27'
      }

      store.setCases([existingCase])

      const newCase: TestCase = {
        id: 2,
        name: '新用例',
        description: '描述',
        priority: 'P0',
        tags: 'regression',
        step_count: 3,
        created_at: '2025-12-27',
        updated_at: '2025-12-27'
      }

      store.addCase(newCase)

      // 验证新用例在列表开头
      expect(store.cases).toHaveLength(2)
      expect(store.cases[0].id).toBe(2)
      expect(store.cases[1].id).toBe(1)

      // 验证总数增加
      expect(store.pagination.total).toBe(1)
    })
  })

  describe('updateCaseInList 方法', () => {
    it('应该更新列表中的用例', () => {
      const store = useCaseStore()
      const originalCase: TestCase = {
        id: 1,
        name: '原始名称',
        description: '原始描述',
        priority: 'P1',
        tags: 'smoke',
        step_count: 2,
        created_at: '2025-12-27',
        updated_at: '2025-12-27'
      }

      store.setCases([originalCase])

      const updatedCase: TestCase = {
        id: 1,
        name: '更新名称',
        description: '更新描述',
        priority: 'P0',
        tags: 'regression',
        step_count: 3,
        created_at: '2025-12-27',
        updated_at: '2025-12-28'
      }

      store.updateCaseInList(updatedCase)

      expect(store.cases).toHaveLength(1)
      expect(store.cases[0].name).toBe('更新名称')
      expect(store.cases[0].priority).toBe('P0')
    })

    it('不存在的用例不应该改变列表', () => {
      const store = useCaseStore()
      const existingCase: TestCase = {
        id: 1,
        name: '存在用例',
        description: '描述',
        priority: 'P1',
        tags: 'smoke',
        step_count: 2,
        created_at: '2025-12-27',
        updated_at: '2025-12-27'
      }

      store.setCases([existingCase])

      const nonExistentCase: TestCase = {
        id: 999,
        name: '不存在用例',
        description: '描述',
        priority: 'P0',
        tags: 'regression',
        step_count: 1,
        created_at: '2025-12-27',
        updated_at: '2025-12-27'
      }

      store.updateCaseInList(nonExistentCase)

      expect(store.cases).toHaveLength(1)
      expect(store.cases[0].id).toBe(1)
    })
  })

  describe('removeCase 方法', () => {
    it('应该从列表中移除用例', () => {
      const store = useCaseStore()
      const cases: TestCase[] = [
        {
          id: 1,
          name: '用例1',
          description: '描述',
          priority: 'P0',
          tags: 'smoke',
          step_count: 1,
          created_at: '2025-12-27',
          updated_at: '2025-12-27'
        },
        {
          id: 2,
          name: '用例2',
          description: '描述',
          priority: 'P1',
          tags: 'regression',
          step_count: 2,
          created_at: '2025-12-27',
          updated_at: '2025-12-27'
        },
        {
          id: 3,
          name: '用例3',
          description: '描述',
          priority: 'P2',
          tags: 'api',
          step_count: 1,
          created_at: '2025-12-27',
          updated_at: '2025-12-27'
        }
      ]

      store.setCases(cases)
      store.setPagination({ total: 3 })

      store.removeCase(2)

      expect(store.cases).toHaveLength(2)
      expect(store.cases[0].id).toBe(1)
      expect(store.cases[1].id).toBe(3)
      expect(store.pagination.total).toBe(2)
    })

    it('移除不存在的用例不应该改变列表', () => {
      const store = useCaseStore()
      const testCase: TestCase = {
        id: 1,
        name: '测试用例',
        description: '描述',
        priority: 'P0',
        tags: 'smoke',
        step_count: 1,
        created_at: '2025-12-27',
        updated_at: '2025-12-27'
      }

      store.setCases([testCase])
      store.setPagination({ total: 1 })

      store.removeCase(999)

      expect(store.cases).toHaveLength(1)
      expect(store.pagination.total).toBe(1)
    })
  })

  describe('batchRemoveCases 方法', () => {
    it('应该批量移除多个用例', () => {
      const store = useCaseStore()
      const cases: TestCase[] = [
        { id: 1, name: '用例1', description: '描述', priority: 'P0', tags: 'smoke', step_count: 1, created_at: '2025-12-27', updated_at: '2025-12-27' },
        { id: 2, name: '用例2', description: '描述', priority: 'P1', tags: 'regression', step_count: 2, created_at: '2025-12-27', updated_at: '2025-12-27' },
        { id: 3, name: '用例3', description: '描述', priority: 'P2', tags: 'api', step_count: 1, created_at: '2025-12-27', updated_at: '2025-12-27' },
        { id: 4, name: '用例4', description: '描述', priority: 'P0', tags: 'smoke', step_count: 3, created_at: '2025-12-27', updated_at: '2025-12-27' }
      ]

      store.setCases(cases)
      store.setPagination({ total: 4 })

      store.batchRemoveCases([1, 3])

      expect(store.cases).toHaveLength(2)
      expect(store.cases[0].id).toBe(2)
      expect(store.cases[1].id).toBe(4)
      expect(store.pagination.total).toBe(2)
    })

    it('空 ID 列表不应该改变任何东西', () => {
      const store = useCaseStore()
      const testCase: TestCase = {
        id: 1,
        name: '测试用例',
        description: '描述',
        priority: 'P0',
        tags: 'smoke',
        step_count: 1,
        created_at: '2025-12-27',
        updated_at: '2025-12-27'
      }

      store.setCases([testCase])
      store.setPagination({ total: 1 })

      store.batchRemoveCases([])

      expect(store.cases).toHaveLength(1)
      expect(store.pagination.total).toBe(1)
    })
  })

  describe('priorityStats 计算属性', () => {
    it('应该正确计算各优先级的用例数量', () => {
      const store = useCaseStore()
      const cases: TestCase[] = [
        { id: 1, name: '用例1', description: '描述', priority: 'P0', tags: 'smoke', step_count: 1, created_at: '2025-12-27', updated_at: '2025-12-27' },
        { id: 2, name: '用例2', description: '描述', priority: 'P0', tags: 'regression', step_count: 2, created_at: '2025-12-27', updated_at: '2025-12-27' },
        { id: 3, name: '用例3', description: '描述', priority: 'P1', tags: 'api', step_count: 1, created_at: '2025-12-27', updated_at: '2025-12-27' },
        { id: 4, name: '用例4', description: '描述', priority: 'P1', tags: 'smoke', step_count: 3, created_at: '2025-12-27', updated_at: '2025-12-27' },
        { id: 5, name: '用例5', description: '描述', priority: 'P1', tags: 'regression', step_count: 2, created_at: '2025-12-27', updated_at: '2025-12-27' },
        { id: 6, name: '用例6', description: '描述', priority: 'P2', tags: 'api', step_count: 1, created_at: '2025-12-27', updated_at: '2025-12-27' }
      ]

      store.setCases(cases)

      expect(store.priorityStats).toEqual({ P0: 2, P1: 3, P2: 1, P3: 0 })
    })

    it('空列表应该返回全零统计', () => {
      const store = useCaseStore()

      expect(store.priorityStats).toEqual({ P0: 0, P1: 0, P2: 0, P3: 0 })
    })

    it('应该忽略无效的优先级值', () => {
      const store = useCaseStore()
      const cases: TestCase[] = [
        { id: 1, name: '用例1', description: '描述', priority: 'P0', tags: 'smoke', step_count: 1, created_at: '2025-12-27', updated_at: '2025-12-27' },
        { id: 2, name: '用例2', description: '描述', priority: 'INVALID' as any, tags: 'regression', step_count: 1, created_at: '2025-12-27', updated_at: '2025-12-27' }
      ]

      store.setCases(cases)

      // 只统计有效的 P0 用例
      expect(store.priorityStats.P0).toBe(1)
    })
  })
})
