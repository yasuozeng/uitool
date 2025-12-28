/**
 * 用例状态管理
 * 管理测试用例列表、当前编辑用例、筛选条件等
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 用例接口定义
export interface TestStep {
  id?: number
  case_id?: number
  step_order: number
  action_type: string
  element_locator: string
  locator_type: string
  // action_params 支持 JSON 字符串或对象类型（后端 SQLAlchemy 返回对象）
  action_params?: string | Record<string, any>
  expected_result?: string
  description?: string
  created_at?: string
  updated_at?: string
}

export interface TestCase {
  id: number
  name: string
  description: string
  priority: string
  tags: string
  step_count: number
  created_at: string
  updated_at: string
  steps?: TestStep[]
}

// 用例筛选条件接口
export interface CaseFilters {
  name?: string
  priority?: string
  tags?: string
}

// 分页信息接口
export interface Pagination {
  page: number
  page_size: number
  total: number
  pages: number
}

export const useCaseStore = defineStore('case', () => {
  // ========== 状态 ==========
  // 用例列表
  const cases = ref<TestCase[]>([])
  // 当前编辑的用例
  const currentCase = ref<TestCase | null>(null)
  // 筛选条件
  const filters = ref<CaseFilters>({})
  // 分页信息
  const pagination = ref<Pagination>({
    page: 1,
    page_size: 20,
    total: 0,
    pages: 0
  })
  // 加载状态
  const loading = ref(false)

  // ========== 计算属性 ==========
  // 按优先级分组的用例数量
  const priorityStats = computed(() => {
    const stats = { P0: 0, P1: 0, P2: 0, P3: 0 }
    cases.value.forEach(c => {
      if (c.priority in stats) {
        stats[c.priority as keyof typeof stats]++
      }
    })
    return stats
  })

  // ========== 操作方法 ==========
  // 设置用例列表
  const setCases = (data: TestCase[]) => {
    cases.value = data
  }

  // 设置当前用例
  const setCurrentCase = (data: TestCase | null) => {
    currentCase.value = data
  }

  // 更新筛选条件
  const setFilters = (newFilters: Partial<CaseFilters>) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  // 重置筛选条件
  const resetFilters = () => {
    filters.value = {}
    pagination.value.page = 1
  }

  // 设置分页信息
  const setPagination = (data: Partial<Pagination>) => {
    pagination.value = { ...pagination.value, ...data }
  }

  // 设置加载状态
  const setLoading = (state: boolean) => {
    loading.value = state
  }

  // 添加新用例到列表
  const addCase = (data: TestCase) => {
    cases.value.unshift(data)
    pagination.value.total++
  }

  // 更新列表中的用例
  const updateCaseInList = (data: TestCase) => {
    const index = cases.value.findIndex(c => c.id === data.id)
    if (index !== -1) {
      cases.value[index] = data
    }
  }

  // 从列表中移除用例
  const removeCase = (id: number) => {
    const index = cases.value.findIndex(c => c.id === id)
    if (index !== -1) {
      cases.value.splice(index, 1)
      pagination.value.total--
    }
  }

  // 批量移除用例
  const batchRemoveCases = (ids: number[]) => {
    cases.value = cases.value.filter(c => !ids.includes(c.id))
    pagination.value.total -= ids.length
  }

  return {
    // 状态
    cases,
    currentCase,
    filters,
    pagination,
    loading,
    // 计算属性
    priorityStats,
    // 方法
    setCases,
    setCurrentCase,
    setFilters,
    resetFilters,
    setPagination,
    setLoading,
    addCase,
    updateCaseInList,
    removeCase,
    batchRemoveCases
  }
})
